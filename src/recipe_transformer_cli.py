#!/usr/bin/env python3
"""
Recipe Transformer CLI

This module provides a simple command-line interface and callable API for
transforming recipes based on dietary restrictions.
"""

import json
import argparse
import sys
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from unit_aware_substitution import UnitAwareSubstitutionEngine, UnitAwareRecipeResult
from llm_substitution_engine import RecipeIngredient


@dataclass
class RecipeInput:
    """Input format for recipe transformation."""
    name: str
    ingredients: List[Dict[str, Any]]  # [{"name": "flour", "amount": "2 cups", "unit": "cups", "quantity": 2.0}]
    instructions: Optional[str] = None
    servings: Optional[int] = None


@dataclass
class RecipeOutput:
    """Output format for transformed recipe."""
    original_name: str
    transformed_name: str
    diet_restrictions: List[str]
    original_ingredients: List[Dict[str, Any]]
    transformed_ingredients: List[Dict[str, Any]]
    substitutions: List[Dict[str, Any]]
    unchanged_ingredients: List[Dict[str, Any]]
    warnings: List[str]
    change_log: List[str]
    success: bool
    instructions: Optional[str] = None
    servings: Optional[int] = None


class RecipeTransformer:
    """Main interface for recipe transformation."""
    
    def __init__(self):
        self.engine = UnitAwareSubstitutionEngine()
    
    def transform_recipe(self, recipe_input: RecipeInput, diet_restrictions: List[str]) -> RecipeOutput:
        """Transform a recipe based on dietary restrictions."""
        # Convert input to RecipeIngredient objects
        recipe_ingredients = []
        for ing_data in recipe_input.ingredients:
            ingredient = RecipeIngredient(
                name=ing_data["name"],
                amount=ing_data.get("amount", ""),
                unit=ing_data.get("unit", ""),
                quantity=ing_data.get("quantity", 1.0),
                notes=ing_data.get("notes", "")
            )
            recipe_ingredients.append(ingredient)
        
        # Process the recipe
        result = self.engine.process_recipe_with_units(recipe_ingredients, diet_restrictions)
        
        # Convert substitutions to dictionaries
        substitutions = []
        for sub in result.substitutions:
            substitutions.append({
                "original_ingredient": sub.original_ingredient,
                "original_amount": sub.original_amount,
                "substituted_ingredient": sub.substituted_ingredient,
                "substituted_amount": sub.substituted_amount,
                "conversion_applied": sub.conversion_applied,
                "substitution_ratio": sub.substitution_ratio,
                "notes": sub.notes,
                "confidence": sub.confidence
            })
        
        # Convert unchanged ingredients to dictionaries
        unchanged = []
        for ing in result.unchanged_ingredients:
            unchanged.append({
                "name": ing.name,
                "amount": ing.amount,
                "unit": ing.unit,
                "quantity": ing.quantity,
                "notes": ing.notes
            })
        
        # Convert transformed ingredients to dictionaries
        transformed_ingredients = []
        
        # Add unchanged ingredients
        for ing in result.unchanged_ingredients:
            transformed_ingredients.append({
                "name": ing.name,
                "amount": ing.amount,
                "unit": ing.unit,
                "quantity": ing.quantity,
                "notes": ing.notes
            })
        
        # Add substituted ingredients (these replace the original ingredients)
        for sub in result.substitutions:
            transformed_ingredients.append({
                "name": sub.substituted_ingredient,
                "amount": sub.substituted_amount,
                "unit": sub.substituted_unit,
                "quantity": sub.substituted_quantity,
                "notes": f"Substituted for {sub.original_ingredient}"
            })
        
        # Create transformed recipe name
        transformed_name = f"{recipe_input.name} ({', '.join(diet_restrictions)})"
        
        return RecipeOutput(
            original_name=recipe_input.name,
            transformed_name=transformed_name,
            diet_restrictions=diet_restrictions,
            original_ingredients=recipe_input.ingredients,
            transformed_ingredients=transformed_ingredients,
            substitutions=substitutions,
            unchanged_ingredients=unchanged,
            warnings=result.warnings,
            change_log=result.change_log,
            success=result.success,
            instructions=recipe_input.instructions,
            servings=recipe_input.servings
        )
    
    def get_available_diets(self) -> List[str]:
        """Get list of available dietary restrictions."""
        return self.engine.unified_system.get_all_diets()
    
    def get_ingredient_info(self, ingredient: str, diet: str) -> Dict[str, Any]:
        """Get information about an ingredient for a specific diet."""
        options = self.engine.unified_system.get_substitution_options(ingredient, diet)
        is_forbidden = self.engine.unified_system.is_forbidden(ingredient, diet)
        
        return {
            "ingredient": ingredient,
            "diet": diet,
            "is_forbidden": is_forbidden,
            "substitution_options": [
                {
                    "name": opt.name,
                    "ratio": opt.ratio,
                    "unit_conversion": opt.unit_conversion,
                    "notes": opt.notes,
                    "confidence": opt.confidence
                } for opt in options
            ],
            "total_options": len(options)
        }


def parse_plain_text_recipe(file_path: str) -> RecipeInput:
    """Parse a plain text recipe file and convert it to RecipeInput format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    lines = content.split('\n')
    
    # Find recipe name (first non-empty line that's not a section header)
    recipe_name = ""
    for line in lines:
        line_stripped = line.strip()
        if (line_stripped and 
            not line_stripped.lower().startswith(('ingredients:', 'instructions:', 'serves', 'directions:')) and
            not line_stripped.startswith('{') and  # Skip JSON artifacts
            len(line_stripped) > 1):  # Skip single characters
            recipe_name = line_stripped
            break
    
    # Find ingredients section
    ingredients = []
    in_ingredients = False
    instructions_lines = []
    servings = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for ingredients section
        if line.lower().startswith('ingredients:'):
            in_ingredients = True
            continue
        elif line.lower().startswith(('instructions:', 'directions:')):
            in_ingredients = False
            continue
        elif line.lower().startswith('serves'):
            # Extract serving count
            match = re.search(r'serves?\s+(\d+)', line.lower())
            if match:
                servings = int(match.group(1))
            continue
        
        if in_ingredients:
            # Parse ingredient line
            if line and not line.lower().startswith('for '):  # Skip section headers like "For Frosting:"
                ingredient_data = parse_ingredient_line(line)
                if ingredient_data:
                    ingredients.append(ingredient_data)
            elif line.lower().startswith('for '):
                # Handle section headers like "For Frosting:" - treat as a new ingredients section
                continue
        else:
            # Collect instructions
            if line and not line.lower().startswith(('ingredients:', 'serves')):
                instructions_lines.append(line)
    
    # Join instructions
    instructions = '\n'.join(instructions_lines) if instructions_lines else None
    
    return RecipeInput(
        name=recipe_name,
        ingredients=ingredients,
        instructions=instructions,
        servings=servings
    )


def parse_ingredient_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single ingredient line into structured data."""
    # Remove any leading dashes or bullets
    line = re.sub(r'^[-•]\s*', '', line).strip()
    
    # Pattern to match: amount + unit + ingredient name
    # Examples: "2 1/4 cups all-purpose flour", "1/2 cup butter, softened", "2 large eggs"
    
    # First try: amount + unit + rest (most common case)
    pattern1 = r'^(\d+(?:\s+\d+/\d+)?)\s+(cups?|tbsp|tsp|oz|lb|large|small|medium)\s+(.+)$'
    match1 = re.match(pattern1, line, re.IGNORECASE)
    
    if match1:
        amount_str = match1.group(1).strip()
        unit = match1.group(2).strip()
        ingredient_name = match1.group(3).strip()
        
        quantity = parse_quantity(amount_str)
        
        return {
            "name": ingredient_name,
            "amount": f"{amount_str} {unit}",
            "unit": unit,
            "quantity": quantity
        }
    
    # Second try: amount + unit + rest (broader unit matching)
    pattern2 = r'^(\d+(?:\s+\d+/\d+)?)\s+([a-zA-Z]+)\s+(.+)$'
    match2 = re.match(pattern2, line)
    
    if match2:
        amount_str = match2.group(1).strip()
        unit = match2.group(2).strip()
        ingredient_name = match2.group(3).strip()
        
        quantity = parse_quantity(amount_str)
        
        return {
            "name": ingredient_name,
            "amount": f"{amount_str} {unit}",
            "unit": unit,
            "quantity": quantity
        }
    
    # Fallback: treat the whole line as ingredient name
    return {
        "name": line,
        "amount": line,
        "unit": "",
        "quantity": 1.0
    }


def parse_quantity(amount_str: str) -> float:
    """Parse quantity string to float, handling fractions and mixed numbers."""
    # Handle mixed numbers like "2 1/4"
    mixed_match = re.match(r'(\d+)\s+(\d+/\d+)', amount_str)
    if mixed_match:
        whole = int(mixed_match.group(1))
        fraction = mixed_match.group(2)
        return whole + parse_fraction(fraction)
    
    # Handle simple fractions
    if '/' in amount_str:
        return parse_fraction(amount_str)
    
    # Handle whole numbers
    try:
        return float(amount_str)
    except ValueError:
        return 1.0


def parse_fraction(fraction_str: str) -> float:
    """Parse a fraction string to float."""
    fraction_map = {
        "1/8": 0.125,
        "1/4": 0.25,
        "1/3": 0.333,
        "3/8": 0.375,
        "1/2": 0.5,
        "5/8": 0.625,
        "2/3": 0.667,
        "3/4": 0.75,
        "7/8": 0.875,
    }
    
    if fraction_str in fraction_map:
        return fraction_map[fraction_str]
    
    # Try to parse other fractions
    try:
        parts = fraction_str.split('/')
        if len(parts) == 2:
            return float(parts[0]) / float(parts[1])
    except (ValueError, ZeroDivisionError):
        pass
    
    return 1.0


def create_sample_recipe() -> RecipeInput:
    """Create a sample recipe for testing."""
    return RecipeInput(
        name="Chocolate Chip Cookies",
        ingredients=[
            {"name": "AP flour", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "sugar", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "brown sugar", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "butter", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "eggs", "amount": "2 large", "unit": "large", "quantity": 2.0},
            {"name": "vanilla extract", "amount": "2 tsp", "unit": "tsp", "quantity": 2.0},
            {"name": "baking soda", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "salt", "amount": "1/2 tsp", "unit": "tsp", "quantity": 0.5},
            {"name": "chocolate chips", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
        ],
        instructions="Mix dry ingredients. Cream butter and sugars. Add eggs and vanilla. Combine wet and dry ingredients. Fold in chocolate chips. Bake at 375°F for 9-11 minutes.",
        servings=24
    )


def print_recipe_output(output: RecipeOutput, verbose: bool = False):
    """Print recipe transformation results in a readable format."""
    print(f"\n🍪 {output.transformed_name}")
    print("=" * 60)
    
    if output.success:
        print("✅ Recipe transformation successful!")
    else:
        print("⚠️  Recipe transformation completed with warnings")
    
    print(f"\n📋 Diet Restrictions: {', '.join(output.diet_restrictions)}")
    print(f"👥 Servings: {output.servings}")
    
    if output.substitutions:
        print(f"\n🔄 Substitutions Made ({len(output.substitutions)}):")
        for i, sub in enumerate(output.substitutions, 1):
            print(f"  {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
            print(f"     Ratio: {sub['substitution_ratio']}")
            print(f"     Notes: {sub['notes']}")
            if sub['conversion_applied']:
                print(f"     (Unit conversion applied)")
    
    if output.unchanged_ingredients:
        print(f"\n✅ Unchanged Ingredients ({len(output.unchanged_ingredients)}):")
        for ing in output.unchanged_ingredients:
            print(f"   • {ing['name']} ({ing['amount']})")
    
    if output.warnings:
        print(f"\n⚠️  Warnings ({len(output.warnings)}):")
        for warning in output.warnings:
            print(f"   • {warning}")
    
    if verbose and output.change_log:
        print(f"\n📝 Change Log:")
        for change in output.change_log:
            print(f"   • {change}")
    
    print(f"\n📖 Transformed Recipe:")
    print("-" * 40)
    for ing in output.transformed_ingredients:
        # Format the amount properly, avoiding 'item' placeholders
        amount_display = ing['amount']
        name = ing['name']
        
        if amount_display and not amount_display.startswith('1 item'):
            # Clean up the amount display to show proper format
            if amount_display.endswith(f" {name}"):
                # Remove duplicate ingredient name
                clean_amount = amount_display.replace(f" {name}", "")
                print(f"• {clean_amount} {name}")
            else:
                print(f"• {amount_display} {name}")
        else:
            # Fallback for when unit parsing fails
            quantity = ing.get('quantity', 1.0)
            unit = ing.get('unit', '')
            if unit and unit != 'item':
                # Format decimal quantities nicely
                if quantity == int(quantity):
                    print(f"• {int(quantity)} {unit} {name}")
                else:
                    print(f"• {quantity} {unit} {name}")
            else:
                print(f"• {quantity} {name}")
    
    if output.instructions:
        print(f"\n👨‍🍳 Instructions:")
        print(output.instructions)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Transform recipes based on dietary restrictions")
    parser.add_argument("--recipe", "-r", help="Path to recipe JSON file")
    parser.add_argument("--diets", "-d", nargs="+", help="Dietary restrictions to apply")
    parser.add_argument("--sample", "-s", action="store_true", help="Use sample recipe")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list-diets", action="store_true", help="List available diets")
    parser.add_argument("--check-ingredient", help="Check ingredient for specific diet")
    parser.add_argument("--diet-for-ingredient", help="Diet to check ingredient against")
    
    args = parser.parse_args()
    
    transformer = RecipeTransformer()
    
    # List available diets
    if args.list_diets:
        diets = transformer.get_available_diets()
        print("Available dietary restrictions:")
        for diet in diets:
            print(f"  • {diet}")
        return
    
    # Check specific ingredient
    if args.check_ingredient and args.diet_for_ingredient:
        info = transformer.get_ingredient_info(args.check_ingredient, args.diet_for_ingredient)
        print(f"\n🔍 Ingredient Analysis: {info['ingredient']} ({info['diet']})")
        print("=" * 50)
        print(f"Forbidden: {info['is_forbidden']}")
        print(f"Substitution options: {info['total_options']}")
        
        if info['substitution_options']:
            print("\nAvailable substitutions:")
            for opt in info['substitution_options']:
                print(f"  • {opt['name']}: {opt['ratio']}")
                print(f"    Notes: {opt['notes']}")
        return
    
    # Load recipe
    if args.sample:
        recipe_input = create_sample_recipe()
    elif args.recipe:
        try:
            # Check file extension to determine parsing method
            if args.recipe.lower().endswith('.json'):
                # Load JSON recipe
                with open(args.recipe, 'r') as f:
                    recipe_data = json.load(f)
                recipe_input = RecipeInput(**recipe_data)
            else:
                # Parse plain text recipe
                recipe_input = parse_plain_text_recipe(args.recipe)
                print(f"📝 Parsed plain text recipe: {recipe_input.name}")
        except Exception as e:
            print(f"Error loading recipe: {e}")
            return
    else:
        print("Error: Please provide a recipe file (--recipe) or use sample recipe (--sample)")
        return
    
    # Get diet restrictions
    if not args.diets:
        print("Error: Please specify dietary restrictions (--diets)")
        print("Available diets:", ", ".join(transformer.get_available_diets()))
        return
    
    # Transform recipe
    try:
        output = transformer.transform_recipe(recipe_input, args.diets)
        print_recipe_output(output, args.verbose)
        
        # Save output if requested
        if args.recipe:
            # Create output filename based on input
            if args.recipe.lower().endswith('.json'):
                output_file = args.recipe.replace('.json', '_transformed.json')
            else:
                # For .txt files, create a .json output file
                base_name = args.recipe.rsplit('.', 1)[0] if '.' in args.recipe else args.recipe
                output_file = f"{base_name}_transformed.json"
            
            with open(output_file, 'w') as f:
                json.dump(asdict(output), f, indent=2)
            print(f"\n💾 Transformed recipe saved to: {output_file}")
    
    except Exception as e:
        print(f"Error transforming recipe: {e}")
        return


if __name__ == "__main__":
    main()
