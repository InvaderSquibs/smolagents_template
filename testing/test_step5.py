#!/usr/bin/env python3
"""
Test script for Step 5: Composite Diet Reconciliation
"""

import sys
import os
sys.path.append('src')

from composite_diet_engine import CompositeDietEngine
from recipe_transformer_cli import create_sample_recipe
from llm_substitution_engine import RecipeIngredient

def test_step5():
    print("=== STEP 5: COMPOSITE DIET RECONCILIATION VALIDATION ===")
    print("Starting validation...")
    
    try:
        print("1. Importing CompositeDietEngine...")
        engine = CompositeDietEngine()
        print("✅ CompositeDietEngine imported successfully")
        
        print("2. Creating sample recipe...")
        sample_recipe = create_sample_recipe()
        print("✅ Sample recipe created")
        print(f"   Recipe has {len(sample_recipe.ingredients)} ingredients:")
        for ing in sample_recipe.ingredients:
            print(f"     • {ing['name']} ({ing['amount']})")
        
        print("3. Converting ingredients to RecipeIngredient objects...")
        recipe_ingredients = []
        for ing_dict in sample_recipe.ingredients:
            recipe_ingredient = RecipeIngredient(
                name=ing_dict['name'],
                amount=ing_dict['amount'],
                unit=ing_dict['unit'],
                quantity=ing_dict['quantity']
            )
            recipe_ingredients.append(recipe_ingredient)
        print(f"✅ Converted {len(recipe_ingredients)} ingredients to RecipeIngredient objects")
        
        print("4. Testing composite diet processing...")
        print("   Applying diets: ['vegan', 'gluten-free']")
        result = engine.apply_composite_diets(recipe_ingredients, ['vegan', 'gluten-free'])
        print("✅ Composite diet processing completed")
        
        print("5. Analyzing results...")
        print(f"   Success: {result.success}")
        print(f"   Applied diets: {result.applied_diets}")
        print(f"   Final ingredients: {len(result.final_ingredients)}")
        print(f"   Conflicts: {len(result.conflicts)}")
        print(f"   Warnings: {len(result.warnings)}")
        print(f"   Substitution history: {len(result.substitution_history)}")
        
        if result.substitution_history:
            print("   Substitution History:")
            for i, sub in enumerate(result.substitution_history, 1):
                print(f"     {i}. {sub}")
        
        if result.conflicts:
            print("   Conflicts:")
            for i, conflict in enumerate(result.conflicts, 1):
                print(f"     {i}. {conflict.conflict_type}: {conflict.suggested_resolution}")
                print(f"        Ingredient: {conflict.ingredient}")
                print(f"        Conflicting diets: {conflict.conflicting_diets}")
                print(f"        Severity: {conflict.severity}")
        
        if result.warnings:
            print("   Warnings:")
            for i, warning in enumerate(result.warnings, 1):
                print(f"     {i}. {warning}")
        
        print("   Final Ingredients:")
        for i, ing in enumerate(result.final_ingredients, 1):
            print(f"     {i}. {ing.amount} {ing.name}")
        
        print("\n✅ Step 5 validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Step 5 validation failed: {e}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_step5()
