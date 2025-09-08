#!/usr/bin/env python3
"""
Recipe Transformation Agent CLI

This CLI uses the LLM agent (Gemini) to make intelligent contextual decisions
about recipe substitutions based on dietary restrictions.
"""

import os
import json
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv
from recipe_agent import RecipeTransformationAgent
from dataclasses import dataclass

# Load environment variables from .env file in root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


@dataclass
class RecipeInput:
    """Simple recipe data structure for CLI input."""
    name: str
    ingredients: List[Dict[str, Any]]
    instructions: str
    servings: int


def parse_plain_text_recipe(file_path: str) -> RecipeInput:
    """Parse a plain text recipe file into structured data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        lines = content.split('\n')
        
        # Extract recipe name (first non-empty line)
        name = ""
        for line in lines:
            if line.strip() and not line.strip().startswith('Ingredients:') and not line.strip().startswith('Instructions:'):
                name = line.strip()
                break
        
        # Find ingredients section
        ingredients = []
        in_ingredients = False
        in_instructions = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith('ingredients:'):
                in_ingredients = True
                in_instructions = False
                continue
            elif line.lower().startswith('instructions:'):
                in_ingredients = False
                in_instructions = True
                continue
            elif line.lower().startswith('serves') or line.lower().startswith('servings'):
                # Extract serving count
                try:
                    servings = int(''.join(filter(str.isdigit, line)))
                except:
                    servings = 4
                continue
            
            if in_ingredients:
                # Skip section headers and empty lines
                if not line or line.startswith('For ') or line.startswith('Instructions:'):
                    continue
                
                # Parse ingredient line
                # Better parsing - handle complex amounts like "2 1/4 cups"
                # Split by first occurrence of common units
                line_lower = line.lower()
                unit_positions = []
                for unit in ['cups', 'cup', 'tablespoons', 'tablespoon', 'tbsp', 'teaspoons', 'teaspoon', 'tsp', 'ounces', 'ounce', 'oz', 'pounds', 'pound', 'lb', 'large', 'small', 'medium']:
                    pos = line_lower.find(unit)
                    if pos != -1:
                        unit_positions.append((pos, unit))
                
                if unit_positions:
                    # Find the earliest unit
                    unit_positions.sort()
                    unit_pos, unit = unit_positions[0]
                    
                    # Split at the unit position
                    amount_part = line[:unit_pos].strip()
                    ingredient_part = line[unit_pos + len(unit):].strip()
                    
                    # Clean up ingredient name
                    ingredient_name = ingredient_part.strip(',').strip()
                    # Remove leading 's' if it's just a stray character
                    if ingredient_name.startswith('s ') and len(ingredient_name) > 2:
                        ingredient_name = ingredient_name[2:]
                    
                    # Parse amount
                    amount = amount_part
                else:
                    # Fallback to simple parsing
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        amount = parts[0]
                        ingredient_name = parts[1]
                    else:
                        continue
                
                # Try to extract quantity and unit
                quantity = 1
                unit = ""
                
                # Handle fractions and mixed numbers
                if '/' in amount:
                    try:
                        if ' ' in amount:
                            # Mixed number like "2 1/4"
                            whole, frac = amount.split(' ', 1)
                            whole_num = int(whole)
                            num, den = frac.split('/')
                            quantity = whole_num + (int(num) / int(den))
                        else:
                            # Simple fraction like "1/2"
                            num, den = amount.split('/')
                            quantity = int(num) / int(den)
                    except:
                        quantity = 1
                else:
                    try:
                        quantity = float(amount)
                    except:
                        quantity = 1
                
                # Extract unit from the line if we found one
                if unit_positions:
                    unit = unit_positions[0][1]  # Use the first unit we found
                else:
                    # Fallback: look for units in the amount
                    for unit_word in ['cups', 'cup', 'tablespoons', 'tablespoon', 'tbsp', 'teaspoons', 'teaspoon', 'tsp', 'ounces', 'ounce', 'oz', 'pounds', 'pound', 'lb']:
                        if unit_word in amount.lower():
                            unit = unit_word
                            break
                
                ingredients.append({
                    "name": ingredient_name,
                    "amount": amount,
                    "quantity": quantity,
                    "unit": unit
                })
        
        # Extract instructions
        instructions_lines = []
        in_instructions = False
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('instructions:'):
                in_instructions = True
                continue
            elif line.lower().startswith('serves') or line.lower().startswith('servings'):
                break
            elif in_instructions and line:
                instructions_lines.append(line)
        
        instructions = '\n'.join(instructions_lines)
        
        return RecipeInput(
            name=name,
            ingredients=ingredients,
            instructions=instructions,
            servings=servings if 'servings' in locals() else 4
        )
        
    except Exception as e:
        raise ValueError(f"Failed to parse recipe file {file_path}: {str(e)}")


def create_sample_recipe() -> RecipeInput:
    """Create a sample recipe for testing."""
    return RecipeInput(
        name="Chocolate Layer Cake",
        ingredients=[
            {"name": "all-purpose flour", "amount": "2 1/4 cups", "quantity": 2.25, "unit": "cups"},
            {"name": "granulated sugar", "amount": "2 cups", "quantity": 2, "unit": "cups"},
            {"name": "unsweetened cocoa powder", "amount": "3/4 cup", "quantity": 0.75, "unit": "cup"},
            {"name": "baking powder", "amount": "1 1/2 tsp", "quantity": 1.5, "unit": "tsp"},
            {"name": "baking soda", "amount": "1 1/2 tsp", "quantity": 1.5, "unit": "tsp"},
            {"name": "salt", "amount": "1 tsp", "quantity": 1, "unit": "tsp"},
            {"name": "eggs", "amount": "2 large", "quantity": 2, "unit": "large"},
            {"name": "milk", "amount": "1 cup", "quantity": 1, "unit": "cup"},
            {"name": "vegetable oil", "amount": "1/2 cup", "quantity": 0.5, "unit": "cup"},
            {"name": "vanilla extract", "amount": "2 tsp", "quantity": 2, "unit": "tsp"},
            {"name": "boiling water", "amount": "1 cup", "quantity": 1, "unit": "cup"},
            {"name": "butter", "amount": "1/2 cup", "quantity": 0.5, "unit": "cup"}
        ],
        instructions="Preheat oven to 350°F (175°C). Grease and flour two 9-inch round cake pans. In a large bowl, mix flour, sugar, cocoa, baking powder, baking soda, and salt. Add eggs, milk, oil, and vanilla. Beat for 2 minutes. Stir in boiling water (batter will be thin). Pour into prepared pans. Bake for 30-35 minutes until toothpick comes out clean. Cool in pans for 10 minutes, then remove to wire racks.",
        servings=12
    )


def format_recipe_dict_as_cookbook(recipe_dict: Dict[str, Any], dietary_restrictions: List[str]) -> str:
    """Format a recipe dictionary as a cookbook-style recipe."""
    output = []
    
    # Title
    title = recipe_dict.get('title', recipe_dict.get('name', 'Recipe'))
    output.append("=" * 60)
    output.append(f"🍰 {title}")
    output.append("=" * 60)
    
    # Servings
    servings = recipe_dict.get('servings', 'Unknown')
    output.append(f"👥 Serves: {servings}")
    output.append("")
    
    # Ingredients
    output.append("📋 INGREDIENTS:")
    output.append("-" * 20)
    
    ingredients = recipe_dict.get('ingredients', [])
    for ing in ingredients:
        name = ing.get('name', '')
        amount = ing.get('amount', '')
        unit = ing.get('unit', '')
        notes = ing.get('notes', '')
        
        if amount and unit:
            output.append(f"• {amount} {unit} {name}")
        else:
            output.append(f"• {name}")
        
        if notes:
            output.append(f"  💡 {notes}")
    
    output.append("")
    
    # Instructions
    output.append("👨‍🍳 INSTRUCTIONS:")
    output.append("-" * 20)
    
    instructions = recipe_dict.get('instructions', '')
    if instructions:
        # Split by newlines and clean up numbering
        instruction_lines = instructions.split('\n')
        for line in instruction_lines:
            if line.strip():
                # Fix double numbering if present
                if line.strip()[0].isdigit():
                    parts = line.split('.', 2)
                    if len(parts) >= 3 and parts[1].strip() and parts[1].strip()[0].isdigit():
                        line = parts[0] + '. ' + parts[2].strip()
                output.append(line.strip())
    
    output.append("")
    
    # Substitution notes
    substitution_notes = recipe_dict.get('substitution_notes', '')
    if substitution_notes:
        output.append("🔄 SUBSTITUTION NOTES:")
        output.append("-" * 20)
        output.append(substitution_notes)
        output.append("")
    
    return "\n".join(output)


def format_cookbook_recipe(result: Dict[str, Any]) -> str:
    """Format the transformed recipe in cookbook style."""
    if not result["success"]:
        return f"❌ Transformation failed: {result.get('error', 'Unknown error')}"
    
    # Check if we have a cookbook recipe from the agent
    if "cookbook_recipe" in result:
        # The agent returned a cookbook format directly
        cookbook_data = result["cookbook_recipe"]
        
        # If it's a string, clean it up
        if isinstance(cookbook_data, str):
            # Clean up the cookbook text - fix double numbering in instructions
            lines = cookbook_data.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Fix double numbering like "1. 1. Preheat oven" -> "1. Preheat oven"
                if line.strip() and line.strip()[0].isdigit():
                    # Check if it has double numbering
                    parts = line.split('.', 2)
                    if len(parts) >= 3 and parts[1].strip() and parts[1].strip()[0].isdigit():
                        # Remove the duplicate number
                        line = parts[0] + '. ' + parts[2].strip()
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        # If it's a dictionary, format it as a cookbook
        elif isinstance(cookbook_data, dict):
            return format_recipe_dict_as_cookbook(cookbook_data, result.get('dietary_restrictions', []))
        
        else:
            return str(cookbook_data)
    
    # Fallback to old format if no cookbook recipe
    original = result["original_recipe"]
    substitutions = result.get("substitutions", [])
    unchanged = result.get("unchanged_ingredients", [])
    
    # Create substitution mapping
    sub_map = {sub['original_ingredient']: sub for sub in substitutions}
    
    # Build the cookbook format
    output = []
    output.append("=" * 60)
    output.append(f"🍰 {original['name']} ({', '.join(result['dietary_restrictions']).title()})")
    output.append("=" * 60)
    output.append(f"👥 Serves: {original.get('servings', 'Unknown')}")
    output.append("")
    
    # Ingredients section
    output.append("📋 INGREDIENTS:")
    output.append("-" * 20)
    
    # Process all ingredients (substituted and unchanged)
    all_ingredients = []
    
    # Add unchanged ingredients
    for ing in unchanged:
        all_ingredients.append({
            'amount': ing.get('amount', ''),
            'name': ing.get('name', ''),
            'unit': ing.get('unit', ''),
            'substituted': False
        })
    
    # Add substituted ingredients
    for sub in substitutions:
        original_ing = None
        # Find the original ingredient data
        for ing in original.get('ingredients', []):
            if ing.get('name') == sub['original_ingredient']:
                original_ing = ing
                break
        
        if original_ing:
            all_ingredients.append({
                'amount': original_ing.get('amount', ''),
                'name': sub['substituted_ingredient'],
                'unit': original_ing.get('unit', ''),
                'substituted': True,
                'original': sub['original_ingredient'],
                'notes': sub.get('contextual_notes', '')
            })
    
    # Sort ingredients to maintain original order
    original_ingredients = original.get('ingredients', [])
    sorted_ingredients = []
    for orig_ing in original_ingredients:
        orig_name = orig_ing.get('name', '')
        # Find matching ingredient in our list
        for ing in all_ingredients:
            if (ing.get('original', ing.get('name', '')) == orig_name and 
                ing not in sorted_ingredients):
                sorted_ingredients.append(ing)
                break
    
    # Print ingredients
    for ing in sorted_ingredients:
        if ing['substituted']:
            output.append(f"• {ing['amount']} {ing['name']} (substituted for {ing['original']})")
            if ing.get('notes'):
                output.append(f"  💡 {ing['notes']}")
        else:
            output.append(f"• {ing['amount']} {ing['name']}")
    
    output.append("")
    
    # Instructions section
    output.append("👨‍🍳 INSTRUCTIONS:")
    output.append("-" * 20)
    instructions = original.get('instructions', '').split('\n')
    for i, instruction in enumerate(instructions, 1):
        if instruction.strip():
            output.append(f"{i}. {instruction.strip()}")
    
    output.append("")
    
    # Substitutions notes
    if substitutions:
        output.append("🔄 SUBSTITUTION NOTES:")
        output.append("-" * 20)
        for sub in substitutions:
            output.append(f"• {sub['original_ingredient']} → {sub['substituted_ingredient']}")
            output.append(f"  🤖 {sub['reasoning']}")
            if sub.get('contextual_notes'):
                output.append(f"  💡 {sub['contextual_notes']}")
            output.append("")
    
    return "\n".join(output)


def print_agent_results(result: Dict[str, Any]):
    """Print the results from the LLM agent transformation."""
    if not result["success"]:
        print(f"❌ Transformation failed: {result.get('error', 'Unknown error')}")
        return
    
    # Print the cookbook format
    cookbook_recipe = format_cookbook_recipe(result)
    print(cookbook_recipe)
    
    # Also print a summary
    print("\n" + "=" * 60)
    print("📊 TRANSFORMATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully transformed recipe for: {', '.join(result['dietary_restrictions'])}")
    print(f"🔄 Total substitutions made: {result.get('total_substitutions', 0)}")
    print(f"🧠 Agent reasoning: {result.get('agent_reasoning', 'LLM made contextual decisions')}")


def save_agent_output(result: Dict[str, Any], output_file: str):
    """Save the agent's output to a file."""
    try:
        # Save both cookbook format and JSON
        cookbook_recipe = format_cookbook_recipe(result)
        
        # Save cookbook format
        cookbook_file = output_file.replace('.json', '.txt')
        with open(cookbook_file, 'w') as f:
            f.write(cookbook_recipe)
        print(f"📖 Cookbook recipe saved to: {cookbook_file}")
        
        # Also save JSON for reference
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 JSON data saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Recipe Transformation Agent using LLM (Gemini) for intelligent substitutions"
    )
    
    parser.add_argument(
        "--recipe", 
        type=str, 
        help="Path to recipe file (.txt or .json)"
    )
    
    parser.add_argument(
        "--diets", 
        type=str, 
        help="Comma-separated list of dietary restrictions (e.g., 'vegan,gluten-free')"
    )
    
    parser.add_argument(
        "--sample", 
        action="store_true", 
        help="Use sample recipe for testing"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file path (default: auto-generated)"
    )
    
    parser.add_argument(
        "--api-key", 
        type=str, 
        help="Gemini API key (or set GEMINI_API_KEY environment variable)"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Gemini API key required!")
        print("Set GEMINI_API_KEY environment variable or use --api-key")
        print("Get your API key from: https://aistudio.google.com/")
        return 1
    
    # Load recipe
    if args.sample:
        recipe_input = create_sample_recipe()
        recipe_data = {
            "name": recipe_input.name,
            "ingredients": recipe_input.ingredients,
            "instructions": recipe_input.instructions,
            "servings": recipe_input.servings
        }
        print("📝 Using sample recipe for testing")
    elif args.recipe:
        if args.recipe.endswith('.txt'):
            recipe_input = parse_plain_text_recipe(args.recipe)
            recipe_data = {
                "name": recipe_input.name,
                "ingredients": recipe_input.ingredients,
                "instructions": recipe_input.instructions,
                "servings": recipe_input.servings
            }
        elif args.recipe.endswith('.json'):
            with open(args.recipe, 'r') as f:
                recipe_data = json.load(f)
        else:
            print("❌ Recipe file must be .txt or .json")
            return 1
    else:
        print("❌ Please provide --recipe or --sample")
        return 1
    
    # Parse dietary restrictions
    if not args.diets:
        print("❌ Please specify --diets (e.g., 'vegan,gluten-free')")
        return 1
    
    dietary_restrictions = [diet.strip() for diet in args.diets.split(',')]
    
    print(f"🤖 Initializing LLM Agent with Gemini...")
    print(f"📝 Recipe: {recipe_data['name']}")
    print(f"📋 Dietary Restrictions: {', '.join(dietary_restrictions)}")
    print()
    
    try:
        # Initialize and run the agent
        agent = RecipeTransformationAgent(api_key)
        result = agent.transform_recipe(recipe_data, dietary_restrictions)
        
        # Print results
        print_agent_results(result)
        
        # Save output
        if args.output:
            save_agent_output(result, args.output)
        else:
            # Auto-generate output filename
            recipe_name = recipe_data['name'].lower().replace(' ', '_')
            diets_str = '_'.join(dietary_restrictions)
            output_file = f"{recipe_name}_agent_transformed_{diets_str}.json"
            save_agent_output(result, output_file)
        
        return 0 if result["success"] else 1
        
    except Exception as e:
        print(f"❌ Agent transformation failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
