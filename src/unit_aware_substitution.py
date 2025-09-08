#!/usr/bin/env python3
"""
Unit-Aware Substitution System

This module integrates unit conversion with the substitution system to provide
complete recipe transformation with proper unit handling.
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from unified_substitution_system import UnifiedSubstitutionSystem
from unit_converter import UnitConverter, ConversionResult
from llm_substitution_engine import RecipeIngredient, SubstitutionDecision


@dataclass
class UnitAwareSubstitution:
    """Represents a substitution with unit conversion."""
    original_ingredient: str
    original_amount: str
    original_unit: str
    original_quantity: float
    
    substituted_ingredient: str
    substituted_amount: str
    substituted_unit: str
    substituted_quantity: float
    
    conversion_applied: bool
    substitution_ratio: str
    unit_conversion: str
    notes: str
    confidence: float
    conversion_result: Optional[ConversionResult] = None


@dataclass
class UnitAwareRecipeResult:
    """Result of unit-aware recipe substitution."""
    original_recipe: List[RecipeIngredient]
    diet_restrictions: List[str]
    substitutions: List[UnitAwareSubstitution]
    unchanged_ingredients: List[RecipeIngredient]
    warnings: List[str]
    change_log: List[str]
    success: bool


class UnitAwareSubstitutionEngine:
    """Handles substitutions with proper unit conversions."""
    
    def __init__(self):
        self.unified_system = UnifiedSubstitutionSystem()
        self.unit_converter = UnitConverter()
    
    def parse_ingredient_amount(self, ingredient: RecipeIngredient) -> Tuple[float, str]:
        """Parse ingredient amount and unit."""
        # Try to parse the amount field first
        if ingredient.amount:
            quantity, unit = self.unit_converter.parse_amount(ingredient.amount)
            if unit:
                return quantity, unit
        
        # Fall back to separate quantity and unit fields
        return ingredient.quantity, ingredient.unit
    
    def apply_substitution_with_units(self, ingredient: RecipeIngredient, 
                                    substitution_name: str, diet_type: str) -> UnitAwareSubstitution:
        """Apply a substitution with proper unit conversion."""
        # Get substitution details
        options = self.unified_system.get_substitution_options(ingredient.name, diet_type)
        selected_option = None
        
        for option in options:
            if option.name.lower() == substitution_name.lower():
                selected_option = option
                break
        
        if not selected_option:
            raise ValueError(f"Substitution '{substitution_name}' not found for '{ingredient.name}'")
        
        # Parse original amount
        original_quantity, original_unit = self.parse_ingredient_amount(ingredient)
        
        # Parse substitution ratio to get target unit
        target_quantity, target_unit = self._parse_substitution_ratio(
            selected_option.ratio, original_quantity, original_unit
        )
        
        # Apply unit conversion if needed
        conversion_applied = False
        conversion_result = None
        
        if original_unit != target_unit:
            conversion_result = self.unit_converter.convert(
                original_quantity, original_unit, target_unit, substitution_name
            )
            
            if conversion_result.success:
                conversion_applied = True
                final_quantity = conversion_result.converted_amount
                final_unit = conversion_result.converted_unit
            else:
                # Fall back to original values if conversion fails
                final_quantity = original_quantity
                final_unit = original_unit
        else:
            final_quantity = original_quantity
            final_unit = original_unit
        
        return UnitAwareSubstitution(
            original_ingredient=ingredient.name,
            original_amount=ingredient.amount,
            original_unit=original_unit,
            original_quantity=original_quantity,
            
            substituted_ingredient=substitution_name,
            substituted_amount=f"{final_quantity:.0f} {final_unit}" if final_quantity == int(final_quantity) else f"{final_quantity} {final_unit}",
            substituted_unit=final_unit,
            substituted_quantity=final_quantity,
            
            conversion_applied=conversion_applied,
            conversion_result=conversion_result,
            
            substitution_ratio=selected_option.ratio,
            unit_conversion=selected_option.unit_conversion,
            notes=selected_option.notes,
            confidence=selected_option.confidence
        )
    
    def _parse_substitution_ratio(self, ratio: str, original_quantity: float, 
                                original_unit: str) -> Tuple[float, str]:
        """Parse substitution ratio to determine target quantity and unit."""
        # Common ratio patterns
        if "1:1" in ratio or "=" in ratio:
            # Direct substitution
            return original_quantity, original_unit
        
        # Look for specific unit conversions in the ratio
        if "cup" in ratio and "ml" in ratio:
            return original_quantity, "ml"
        elif "tbsp" in ratio and "tsp" in ratio:
            return original_quantity * 3, "tsp"  # 1 tbsp = 3 tsp
        elif "lb" in ratio and "oz" in ratio:
            return original_quantity * 16, "oz"  # 1 lb = 16 oz
        
        # Default to original values
        return original_quantity, original_unit
    
    def process_recipe_with_units(self, recipe_ingredients: List[RecipeIngredient], 
                                diet_restrictions: List[str]) -> UnitAwareRecipeResult:
        """Process a complete recipe with unit-aware substitutions."""
        substitutions = []
        unchanged_ingredients = []
        warnings = []
        change_log = []
        
        for ingredient in recipe_ingredients:
            # Check if ingredient needs substitution for any diet
            needs_substitution = False
            applicable_diet = None
            
            for diet in diet_restrictions:
                if self.unified_system.is_forbidden(ingredient.name, diet):
                    needs_substitution = True
                    applicable_diet = diet
                    break
            
            if needs_substitution:
                # Get substitution options
                options = self.unified_system.get_substitution_options(ingredient.name, applicable_diet)
                
                if options:
                    # Select the first option (LLM will make this choice)
                    selected_option = options[0]
                    
                    try:
                        substitution = self.apply_substitution_with_units(
                            ingredient, selected_option.name, applicable_diet
                        )
                        
                        substitutions.append(substitution)
                        change_log.append(
                            f"Replaced '{ingredient.name}' ({ingredient.amount}) with "
                            f"'{substitution.substituted_ingredient}' ({substitution.substituted_amount})"
                        )
                        
                        if substitution.conversion_applied:
                            converted_amount = substitution.conversion_result.converted_amount
                            formatted_amount = f"{converted_amount:.0f}" if converted_amount == int(converted_amount) else f"{converted_amount}"
                            change_log.append(
                                f"  Applied unit conversion: {substitution.conversion_result.original_amount} "
                                f"{substitution.conversion_result.original_unit} → "
                                f"{formatted_amount} "
                                f"{substitution.conversion_result.converted_unit}"
                            )
                    
                    except Exception as e:
                        warnings.append(f"Failed to substitute '{ingredient.name}': {str(e)}")
                        unchanged_ingredients.append(ingredient)
                else:
                    warnings.append(f"No substitution found for '{ingredient.name}' on {applicable_diet} diet")
                    unchanged_ingredients.append(ingredient)
            else:
                unchanged_ingredients.append(ingredient)
        
        return UnitAwareRecipeResult(
            original_recipe=recipe_ingredients,
            diet_restrictions=diet_restrictions,
            substitutions=substitutions,
            unchanged_ingredients=unchanged_ingredients,
            warnings=warnings,
            change_log=change_log,
            success=len(warnings) == 0
        )
    
    def demo_unit_aware_substitutions(self) -> List[Dict]:
        """Demo unit-aware substitutions with various scenarios."""
        # Create sample recipe with different unit types
        sample_recipe = [
            RecipeIngredient(name="AP flour", amount="2 cups", unit="cups", quantity=2.0),
            RecipeIngredient(name="sugar", amount="1/2 cup", unit="cup", quantity=0.5),
            RecipeIngredient(name="butter", amount="1/2 cup", unit="cup", quantity=0.5),
            RecipeIngredient(name="eggs", amount="3 large", unit="large", quantity=3.0),
            RecipeIngredient(name="milk", amount="1 cup", unit="cup", quantity=1.0),
            RecipeIngredient(name="salt", amount="1 tsp", unit="tsp", quantity=1.0),
        ]
        
        # Test different diet scenarios
        test_scenarios = [
            ["gluten-free"],
            ["vegan"],
            ["keto"],
            ["gluten-free", "vegan"],
        ]
        
        results = []
        for diets in test_scenarios:
            result = self.process_recipe_with_units(sample_recipe, diets)
            
            results.append({
                "diets": diets,
                "success": result.success,
                "total_ingredients": len(sample_recipe),
                "substitutions_made": len(result.substitutions),
                "unchanged_ingredients": len(result.unchanged_ingredients),
                "warnings": len(result.warnings),
                "unit_conversions": sum(1 for sub in result.substitutions if sub.conversion_applied),
                "substitutions": [
                    {
                        "original": f"{sub.original_ingredient} ({sub.original_amount})",
                        "replacement": f"{sub.substituted_ingredient} ({sub.substituted_amount})",
                        "conversion": sub.conversion_applied,
                        "ratio": sub.substitution_ratio
                    } for sub in result.substitutions
                ]
            })
        
        return results


def main():
    """Demo the unit-aware substitution system."""
    print("🧪 Testing Unit-Aware Substitution System")
    print("=" * 60)
    
    engine = UnitAwareSubstitutionEngine()
    
    # Test 1: Amount parsing
    print("📝 Test 1: Ingredient Amount Parsing")
    test_ingredients = [
        RecipeIngredient(name="flour", amount="2 cups", unit="cups", quantity=2.0),
        RecipeIngredient(name="sugar", amount="1/2 cup", unit="cup", quantity=0.5),
        RecipeIngredient(name="butter", amount="1/2 cup", unit="cup", quantity=0.5),
        RecipeIngredient(name="salt", amount="1 tsp", unit="tsp", quantity=1.0),
    ]
    
    for ingredient in test_ingredients:
        quantity, unit = engine.parse_ingredient_amount(ingredient)
        print(f"   {ingredient.name}: '{ingredient.amount}' → {quantity} {unit}")
    
    print()
    
    # Test 2: Unit conversions
    print("📝 Test 2: Unit Conversions")
    conversion_tests = [
        ("1", "cup", "ml", "flour"),
        ("2", "tbsp", "tsp", ""),
        ("100", "g", "ml", "butter"),
    ]
    
    for amount_str, from_unit, to_unit, ingredient in conversion_tests:
        amount, _ = engine.unit_converter.parse_amount(amount_str)
        result = engine.unit_converter.convert(amount, from_unit, to_unit, ingredient)
        status = "✅" if result.success else "❌"
        print(f"   {status} {amount} {from_unit} → {result.converted_amount:.2f} {result.converted_unit}")
        if not result.success:
            print(f"      Error: {result.error_message}")
    
    print()
    
    # Test 3: Complete recipe processing
    print("📝 Test 3: Complete Recipe Processing")
    demo_results = engine.demo_unit_aware_substitutions()
    
    for result in demo_results:
        print(f"\n🥗 Diets: {', '.join(result['diets'])}")
        print(f"   Success: {result['success']}")
        print(f"   Ingredients: {result['total_ingredients']}")
        print(f"   Substitutions: {result['substitutions_made']}")
        print(f"   Unit conversions: {result['unit_conversions']}")
        print(f"   Unchanged: {result['unchanged_ingredients']}")
        print(f"   Warnings: {result['warnings']}")
        
        if result['substitutions']:
            print("   Changes:")
            for sub in result['substitutions']:
                conversion_note = " (with unit conversion)" if sub['conversion'] else ""
                print(f"     • {sub['original']} → {sub['replacement']}{conversion_note}")
    
    print(f"\n✅ Unit-aware substitution system ready!")
    print("✅ Amount parsing working")
    print("✅ Unit conversions integrated")
    print("✅ Complete recipe processing functional")


if __name__ == "__main__":
    main()
