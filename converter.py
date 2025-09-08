#!/usr/bin/env python3
"""
Simple CLI for recipe transformation demo.
Usage: python3 converter.py --recipe="recipe_name" --restrictions="['vegan', 'gluten-free']"
"""

import sys
import argparse
import json
import os
import re
from typing import List, Dict, Any

# Add src to path
sys.path.append('src')

from recipe_transformer_cli import RecipeTransformer, RecipeInput
from testing.test_recipes import get_test_recipes

def get_recipe_by_name(name: str):
    """Get a test recipe by name."""
    recipes = get_test_recipes()
    for recipe in recipes:
        if recipe.name.lower() == name.lower():
            return recipe
    return None

def parse_restrictions(restrictions_str: str) -> List[str]:
    """Parse restrictions string like "['vegan', 'gluten-free']" into list."""
    try:
        # Remove quotes and brackets, split by comma
        clean_str = restrictions_str.strip("[]'\"")
        restrictions = [r.strip().strip("'\"") for r in clean_str.split(',')]
        return restrictions
    except:
        return [restrictions_str]

def parse_ingredient_line(line: str) -> Dict[str, str]:
    """Parse a single ingredient line into amount, unit, and name."""
    line = line.strip()
    if not line:
        return None
    
    # Common patterns for ingredients
    patterns = [
        # "2 1/4 cups flour" or "1/2 cup butter"
        r'^(\d+(?:\s+\d+/\d+)?)\s+(\w+)\s+(.+)$',
        # "2 large eggs" or "1 tsp salt"
        r'^(\d+(?:\s+\d+/\d+)?)\s+(\w+)\s+(.+)$',
        # "1 cup butter, softened" or "2 cups chocolate chips"
        r'^(\d+(?:\s+\d+/\d+)?)\s+(\w+)\s+(.+)$',
        # Just ingredient name without amount/unit
        r'^(.+)$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            if len(match.groups()) == 3:
                amount, unit, name = match.groups()
                return {
                    "amount": line.strip(),  # Keep the full original string
                    "unit": unit.strip(),
                    "name": name.strip()
                }
            elif len(match.groups()) == 1:
                # Just ingredient name
                return {
                    "amount": "1",
                    "unit": "item",
                    "name": match.group(1).strip()
                }
    
    # Fallback: treat whole line as ingredient name
    return {
        "amount": "1",
        "unit": "item", 
        "name": line
    }

def parse_recipe_text(recipe_text: str) -> RecipeInput:
    """Parse natural recipe text into structured RecipeInput."""
    lines = [line.strip() for line in recipe_text.strip().split('\n') if line.strip()]
    
    if not lines:
        raise ValueError("Empty recipe text")
    
    # First line is usually the recipe name
    name = lines[0]
    
    # Find ingredients section (look for common keywords)
    ingredients_start = -1
    instructions_start = -1
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ['ingredients:', 'ingredient:', 'for the']):
            ingredients_start = i + 1
        elif any(keyword in line_lower for keyword in ['instructions:', 'directions:', 'method:', 'steps:']):
            instructions_start = i
            break
    
    # If no clear sections found, assume first few lines are ingredients
    if ingredients_start == -1:
        ingredients_start = 1
    if instructions_start == -1:
        # Look for numbered steps or common instruction patterns
        for i in range(ingredients_start, len(lines)):
            line = lines[i]
            if (re.match(r'^\d+\.', line) or 
                any(word in line.lower() for word in ['preheat', 'mix', 'stir', 'bake', 'cook', 'add', 'combine'])):
                instructions_start = i
                break
        
        if instructions_start == -1:
            instructions_start = len(lines)
    
    # Parse ingredients
    ingredients = []
    for i in range(ingredients_start, instructions_start):
        if i < len(lines):
            ingredient = parse_ingredient_line(lines[i])
            if ingredient:
                ingredients.append(ingredient)
    
    # Parse instructions
    instructions = []
    for i in range(instructions_start, len(lines)):
        if i < len(lines):
            instruction = lines[i].strip()
            if instruction:
                # Remove leading numbers if present
                instruction = re.sub(r'^\d+\.\s*', '', instruction)
                instructions.append(instruction)
    
    # Try to extract servings from text
    servings = 4  # default
    for line in lines:
        if 'serves' in line.lower() or 'servings' in line.lower():
            numbers = re.findall(r'\d+', line)
            if numbers:
                servings = int(numbers[0])
                break
    
    return RecipeInput(
        name=name,
        ingredients=ingredients,
        instructions=instructions,
        servings=servings
    )

def load_recipe_from_file(file_path: str) -> RecipeInput:
    """Load a recipe from a JSON file or parse from text file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Recipe file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    # Try to parse as JSON first
    try:
        recipe_data = json.loads(content)
        return RecipeInput(
            name=recipe_data.get('name', 'Unknown Recipe'),
            ingredients=recipe_data.get('ingredients', []),
            instructions=recipe_data.get('instructions', []),
            servings=recipe_data.get('servings', 4)
        )
    except json.JSONDecodeError:
        # Not JSON, try to parse as natural text
        try:
            return parse_recipe_text(content)
        except Exception as e:
            raise ValueError(f"Could not parse recipe file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Transform recipes based on dietary restrictions")
    parser.add_argument("--recipe-file", "-f", help="Path to recipe JSON file")
    parser.add_argument("--recipe", "-r", help="Recipe name from test recipes (e.g., 'Chocolate Chip Cookies')")
    parser.add_argument("--restrictions", "-d", required=True, help="Dietary restrictions (e.g., \"['vegan', 'gluten-free']\")")
    parser.add_argument("--list-recipes", action="store_true", help="List available test recipes")
    
    args = parser.parse_args()
    
    if args.list_recipes:
        print("📋 Available Test Recipes:")
        recipes = get_test_recipes()
        for recipe in recipes:
            print(f"  • {recipe.name} ({recipe.category}, {recipe.complexity})")
        return
    
    # Check if recipe source is provided
    if not args.recipe_file and not args.recipe:
        print("❌ Error: Either --recipe-file or --recipe is required")
        print("Use --list-recipes to see available test recipes")
        return
    
    # Parse restrictions
    restrictions = parse_restrictions(args.restrictions)
    
    # Get recipe
    if args.recipe_file:
        try:
            recipe_input = load_recipe_from_file(args.recipe_file)
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in recipe file: {e}")
            return
    else:
        # Get from test recipes
        recipe = get_recipe_by_name(args.recipe)
        if not recipe:
            print(f"❌ Recipe '{args.recipe}' not found. Use --list-recipes to see available recipes.")
            return
        
        recipe_input = RecipeInput(
            name=recipe.name,
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            servings=recipe.servings
        )
    
    # Transform recipe
    transformer = RecipeTransformer()
    
    print(f"🍪 Transforming: {recipe_input.name}")
    print(f"🥗 Restrictions: {', '.join(restrictions)}")
    print("=" * 50)
    
    # Transform
    result = transformer.transform_recipe(recipe_input, restrictions)
    
    print(f"✅ Success: {result.success}")
    print()
    
    if result.substitutions:
        print("🔄 Substitutions Made:")
        for i, sub in enumerate(result.substitutions, 1):
            print(f"  {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
            print(f"     Ratio: {sub['substitution_ratio']}")
            print(f"     Notes: {sub['notes']}")
        print()
    
    print("📖 Transformed Recipe:")
    for ing in result.transformed_ingredients:
        print(f"  • {ing['amount']} {ing['name']}")
    
    if result.warnings:
        print()
        print("⚠️  Warnings:")
        for warning in result.warnings:
            print(f"  • {warning}")

if __name__ == "__main__":
    main()
