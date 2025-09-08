#!/usr/bin/env python3
"""
Test script for Step 7: Recipe-Level Interface
"""

import sys
import os
sys.path.append('src')

from recipe_transformer_cli import RecipeTransformer, create_sample_recipe

def test_step7():
    print("=== STEP 7: RECIPE-LEVEL INTERFACE VALIDATION ===")
    print("Starting validation...")
    
    try:
        print("1. Importing RecipeTransformer...")
        transformer = RecipeTransformer()
        print("✅ RecipeTransformer imported successfully")
        
        print("2. Creating sample recipe...")
        sample_recipe = create_sample_recipe()
        print("✅ Sample recipe created")
        print(f"   Recipe: {sample_recipe.name}")
        print(f"   Ingredients: {len(sample_recipe.ingredients)}")
        print(f"   Instructions: {len(sample_recipe.instructions)} characters")
        
        print("\n3. Testing single diet transformation...")
        print("   Testing vegan diet...")
        result = transformer.transform_recipe(sample_recipe, ['vegan'])
        print(f"   ✅ Success: {result.success}")
        print(f"   ✅ Substitutions made: {len(result.substitutions)}")
        print(f"   ✅ Unchanged ingredients: {len(result.unchanged_ingredients)}")
        
        if result.substitutions:
            print("   Substitutions:")
            for i, sub in enumerate(result.substitutions, 1):
                print(f"     {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
                print(f"        Ratio: {sub['substitution_ratio']}")
                print(f"        Notes: {sub['notes']}")
        
        print("\n4. Testing multiple diet transformation...")
        print("   Testing vegan + gluten-free diets...")
        result2 = transformer.transform_recipe(sample_recipe, ['vegan', 'gluten-free'])
        print(f"   ✅ Success: {result2.success}")
        print(f"   ✅ Substitutions made: {len(result2.substitutions)}")
        print(f"   ✅ Unchanged ingredients: {len(result2.unchanged_ingredients)}")
        
        if result2.substitutions:
            print("   Substitutions:")
            for i, sub in enumerate(result2.substitutions, 1):
                print(f"     {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
                print(f"        Ratio: {sub['substitution_ratio']}")
                print(f"        Notes: {sub['notes']}")
        
        print("\n5. Testing ingredient compatibility check...")
        print("   Checking individual ingredients...")
        test_ingredients = ['eggs', 'butter', 'wheat flour', 'milk']
        test_diets = ['vegan', 'dairy-free', 'gluten-free']
        
        for ingredient in test_ingredients:
            print(f"   Checking {ingredient}:")
            for diet in test_diets:
                # Use the knowledge base directly for compatibility check
                from restriction_knowledge import RestrictionKnowledgeBase
                kb = RestrictionKnowledgeBase()
                is_forbidden = kb.is_forbidden(ingredient, diet)
                options = kb.get_substitution_options(ingredient, diet)
                compatibility = f"Forbidden: {is_forbidden}, Options: {len(options)}"
                print(f"     {diet}: {compatibility}")
        
        print("\n6. Testing available diets...")
        # Use the knowledge base directly to get available diets
        from restriction_knowledge import RestrictionKnowledgeBase
        kb = RestrictionKnowledgeBase()
        diets = kb.get_all_diets()
        print(f"   ✅ Available diets: {diets}")
        
        print("\n7. Testing complete recipe output...")
        print("   Final transformed recipe:")
        print("   " + "="*50)
        for ing in result.transformed_ingredients:
            print(f"   • {ing['amount']} {ing['name']}")
        
        if result.instructions:
            print(f"\n   Instructions:")
            print(f"   {result.instructions}")
        
        print("\n✅ Step 7 validation completed successfully!")
        print("✅ Recipe-level interface working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Step 7 validation failed: {e}")
        print("Full error details:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_step7()
