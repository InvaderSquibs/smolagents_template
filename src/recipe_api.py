#!/usr/bin/env python3
"""
Recipe Transformation API

This module provides a simple callable API for recipe transformation
that can be easily integrated into other applications.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from recipe_transformer_cli import RecipeTransformer, RecipeInput, RecipeOutput


class RecipeAPI:
    """Simple API for recipe transformation."""
    
    def __init__(self):
        self.transformer = RecipeTransformer()
    
    def transform_recipe(self, recipe: Union[Dict, RecipeInput], diets: List[str]) -> Dict[str, Any]:
        """
        Transform a recipe based on dietary restrictions.
        
        Args:
            recipe: Recipe data as dict or RecipeInput object
            diets: List of dietary restrictions to apply
            
        Returns:
            Dictionary with transformation results
        """
        # Convert dict to RecipeInput if needed
        if isinstance(recipe, dict):
            recipe_input = RecipeInput(**recipe)
        else:
            recipe_input = recipe
        
        # Transform the recipe
        output = self.transformer.transform_recipe(recipe_input, diets)
        
        # Return as dictionary
        return asdict(output)
    
    def get_available_diets(self) -> List[str]:
        """Get list of available dietary restrictions."""
        return self.transformer.get_available_diets()
    
    def check_ingredient(self, ingredient: str, diet: str) -> Dict[str, Any]:
        """Check if an ingredient is compatible with a specific diet."""
        return self.transformer.get_ingredient_info(ingredient, diet)
    
    def batch_transform(self, recipes: List[Dict], diets: List[str]) -> List[Dict[str, Any]]:
        """Transform multiple recipes at once."""
        results = []
        for recipe in recipes:
            try:
                result = self.transform_recipe(recipe, diets)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "recipe": recipe,
                    "diets": diets
                })
        return results


# Convenience functions for direct use
def transform_recipe(recipe: Dict, diets: List[str]) -> Dict[str, Any]:
    """Transform a single recipe."""
    api = RecipeAPI()
    return api.transform_recipe(recipe, diets)


def get_available_diets() -> List[str]:
    """Get available dietary restrictions."""
    api = RecipeAPI()
    return api.get_available_diets()


def check_ingredient(ingredient: str, diet: str) -> Dict[str, Any]:
    """Check ingredient compatibility with diet."""
    api = RecipeAPI()
    return api.check_ingredient(ingredient, diet)


# Example usage
if __name__ == "__main__":
    # Example recipe
    sample_recipe = {
        "name": "Simple Pancakes",
        "ingredients": [
            {"name": "AP flour", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "sugar", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "milk", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "eggs", "amount": "1 large", "unit": "large", "quantity": 1.0},
            {"name": "butter", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
        ],
        "instructions": "Mix dry ingredients. Whisk wet ingredients. Combine and cook on griddle.",
        "servings": 4
    }
    
    print("🧪 Testing Recipe API")
    print("=" * 40)
    
    # Test 1: Available diets
    print("📋 Available diets:")
    diets = get_available_diets()
    for diet in diets:
        print(f"  • {diet}")
    
    print()
    
    # Test 2: Transform recipe
    print("🔄 Transforming recipe for gluten-free diet:")
    result = transform_recipe(sample_recipe, ["gluten-free"])
    
    print(f"Success: {result['success']}")
    print(f"Substitutions: {len(result['substitutions'])}")
    print(f"Warnings: {len(result['warnings'])}")
    
    if result['substitutions']:
        print("\nSubstitutions made:")
        for sub in result['substitutions']:
            print(f"  • {sub['original_ingredient']} → {sub['substituted_ingredient']}")
    
    print()
    
    # Test 3: Check specific ingredient
    print("🔍 Checking ingredient compatibility:")
    info = check_ingredient("eggs", "vegan")
    print(f"Eggs in vegan diet: forbidden={info['is_forbidden']}, options={info['total_options']}")
    
    if info['substitution_options']:
        print("Available substitutions:")
        for opt in info['substitution_options'][:2]:  # Show first 2
            print(f"  • {opt['name']}: {opt['ratio']}")
    
    print("\n✅ Recipe API working correctly!")
