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


def print_agent_results(result: Dict[str, Any]):
    """Print the results from the LLM agent transformation."""
    if not result["success"]:
        print(f"❌ Transformation failed: {result.get('error', 'Unknown error')}")
        return
    
    print(f"🤖 LLM Agent Recipe Transformation Results")
    print("=" * 60)
    
    # Recipe info
    original = result["original_recipe"]
    print(f"📝 Recipe: {original['name']}")
    print(f"📋 Dietary Restrictions: {', '.join(result['dietary_restrictions'])}")
    print(f"👥 Servings: {original.get('servings', 'Unknown')}")
    
    # Recipe context (if available)
    context = result.get("recipe_context", {})
    if context:
        print(f"\n🔍 Recipe Analysis:")
        print(f"   Type: {context.get('recipe_type', 'Unknown')}")
        print(f"   Cooking Method: {context.get('cooking_method', 'Unknown')}")
        print(f"   Flavor Profile: {context.get('flavor_profile', 'Unknown')}")
    
    # Substitutions
    substitutions = result.get("substitutions", [])
    if substitutions:
        print(f"\n🔄 LLM-Guided Substitutions ({len(substitutions)}):")
        for i, sub in enumerate(substitutions, 1):
            print(f"   {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
            print(f"      🤖 Reasoning: {sub['reasoning']}")
            print(f"      📊 Confidence: {sub['confidence']:.2f}")
            if sub.get('contextual_notes'):
                print(f"      💡 Notes: {sub['contextual_notes']}")
            print()
    else:
        print(f"\n✅ No substitutions needed - recipe is already compliant!")
    
    # Unchanged ingredients
    unchanged = result.get("unchanged_ingredients", [])
    if unchanged:
        print(f"✅ Unchanged Ingredients ({len(unchanged)}):")
        for ing in unchanged:
            print(f"   • {ing.get('amount', '')} {ing.get('name', '')}")
    
    # Agent reasoning
    agent_reasoning = result.get("agent_reasoning", "")
    if agent_reasoning:
        print(f"\n🤖 Agent Summary: {agent_reasoning}")


def save_agent_output(result: Dict[str, Any], output_file: str):
    """Save the agent's output to a file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Agent results saved to: {output_file}")
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
