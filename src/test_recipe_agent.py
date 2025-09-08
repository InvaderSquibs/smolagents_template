#!/usr/bin/env python3
"""
Test script for recipe agent without LLM API calls
"""

import os
import json
from recipe_agent_cli import parse_plain_text_recipe, print_agent_results
from llm_substitution_engine import LLMSubstitutionEngine

def mock_recipe_transformation(recipe_data, dietary_restrictions):
    """Mock the LLM agent transformation for testing."""
    
    # Initialize substitution engine
    engine = LLMSubstitutionEngine()
    
    # Analyze recipe context (mock)
    recipe_context = {
        "recipe_type": "baking",
        "cooking_method": "baking", 
        "flavor_profile": "sweet"
    }
    
    # Process ingredients
    substitutions = []
    unchanged_ingredients = []
    
    for ingredient_data in recipe_data.get("ingredients", []):
        ingredient_name = ingredient_data.get("name", "")
        
        # Check if ingredient needs substitution
        needs_substitution = False
        for diet in dietary_restrictions:
            if engine.knowledge_base.is_forbidden(ingredient_name, diet):
                needs_substitution = True
                break
        
        if needs_substitution:
            # Get substitution options
            options = engine.get_substitution_options_for_llm(ingredient_name, dietary_restrictions[0])
            substitution_options = options.get("substitution_options", [])
            
            if substitution_options:
                # Mock decision: pick the first option
                best_option = substitution_options[0]
                substitutions.append({
                    "original_ingredient": ingredient_name,
                    "substituted_ingredient": best_option["name"],
                    "reasoning": f"Selected {best_option['name']} as the best vegan substitute",
                    "confidence": best_option.get("confidence", 0.9),
                    "contextual_notes": best_option.get("notes", "")
                })
            else:
                unchanged_ingredients.append(ingredient_data)
        else:
            unchanged_ingredients.append(ingredient_data)
    
    return {
        "success": True,
        "original_recipe": recipe_data,
        "dietary_restrictions": dietary_restrictions,
        "recipe_context": recipe_context,
        "substitutions": substitutions,
        "unchanged_ingredients": unchanged_ingredients,
        "total_substitutions": len(substitutions),
        "agent_reasoning": "Mock agent made substitution decisions based on knowledge base"
    }

def main():
    """Test the recipe transformation without LLM."""
    print("🧪 Testing Recipe Agent (Mock Mode)")
    print("=" * 50)
    
    # Load recipe
    recipe = parse_plain_text_recipe('../demos/demo_cake.txt')
    recipe_data = {
        "name": recipe.name,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "servings": recipe.servings
    }
    
    dietary_restrictions = ["vegan"]
    
    print(f"📝 Recipe: {recipe_data['name']}")
    print(f"📋 Dietary Restrictions: {', '.join(dietary_restrictions)}")
    print()
    
    # Transform recipe
    result = mock_recipe_transformation(recipe_data, dietary_restrictions)
    
    # Print results
    print_agent_results(result)
    
    # Save output
    output_file = "chocolate_layer_cake_mock_transformed_vegan.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"💾 Mock results saved to: {output_file}")

if __name__ == "__main__":
    main()
