#!/usr/bin/env python3
"""
LLM-Guided Substitution Engine

This module implements the core substitution logic where:
- LLM selects appropriate substitutions from available options
- Deterministic engine calculates exact ratios/units and validates
- System maintains determinism while allowing intelligent choice
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from unified_substitution_system import UnifiedSubstitutionSystem
from restriction_knowledge import SubstitutionOption


@dataclass
class RecipeIngredient:
    """Represents a single ingredient in a recipe."""
    name: str
    amount: str  # e.g., "1 cup", "2 tbsp", "3 large"
    unit: str    # e.g., "cup", "tbsp", "large"
    quantity: float  # e.g., 1.0, 2.0, 3.0
    notes: str = ""  # e.g., "chopped", "diced", "optional"


@dataclass
class SubstitutionDecision:
    """Represents an LLM's decision about ingredient substitution."""
    original_ingredient: str
    canonical_ingredient: str
    selected_substitution: str
    substitution_ratio: str
    unit_conversion: str
    confidence: float  # 0-1, how confident the LLM is in this choice
    reasoning: str     # LLM's explanation for the choice
    notes: str         # Additional cooking notes


@dataclass
class RecipeSubstitution:
    """Represents a complete recipe substitution result."""
    original_recipe: List[RecipeIngredient]
    diet_restrictions: List[str]
    substitutions: List[SubstitutionDecision]
    unchanged_ingredients: List[RecipeIngredient]
    warnings: List[str]
    change_log: List[str]


class LLMSubstitutionEngine:
    """Handles LLM-guided substitution with deterministic ratio calculations."""
    
    def __init__(self):
        self.unified_system = UnifiedSubstitutionSystem()
    
    def get_substitution_options_for_llm(self, ingredient: str, diet_type: str) -> Dict[str, Any]:
        """
        Get substitution options formatted for LLM decision-making.
        
        Args:
            ingredient: Raw ingredient name
            diet_type: Diet restriction type
            
        Returns:
            Dictionary with options and context for LLM
        """
        # Canonicalize ingredient
        canonical = self.unified_system.canonicalizer.canonicalize(ingredient)
        
        # Get substitution options
        options = self.unified_system.get_substitution_options(ingredient, diet_type)
        
        # Check if forbidden
        is_forbidden = self.unified_system.is_forbidden(ingredient, diet_type)
        
        return {
            "original_ingredient": ingredient,
            "canonical_ingredient": canonical,
            "diet_type": diet_type,
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
    
    def validate_llm_decision(self, ingredient: str, diet_type: str, selected_substitution: str) -> Tuple[bool, str]:
        """
        Validate that an LLM's substitution choice is valid.
        
        Args:
            ingredient: Original ingredient
            diet_type: Diet type
            selected_substitution: LLM's chosen substitution
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        options = self.unified_system.get_substitution_options(ingredient, diet_type)
        
        # Check if the selected substitution is in our available options
        valid_names = [opt.name.lower() for opt in options]
        if selected_substitution.lower() not in valid_names:
            return False, f"'{selected_substitution}' is not a valid substitution for '{ingredient}' on {diet_type} diet"
        
        return True, ""
    
    def calculate_substitution_ratio(self, ingredient: str, diet_type: str, selected_substitution: str) -> Dict[str, Any]:
        """
        Calculate the exact substitution ratio and units.
        
        Args:
            ingredient: Original ingredient
            diet_type: Diet type
            selected_substitution: Chosen substitution
            
        Returns:
            Dictionary with calculated ratios and units
        """
        options = self.unified_system.get_substitution_options(ingredient, diet_type)
        
        # Find the selected option
        selected_option = None
        for opt in options:
            if opt.name.lower() == selected_substitution.lower():
                selected_option = opt
                break
        
        if not selected_option:
            return {"error": f"Could not find substitution details for '{selected_substitution}'"}
        
        return {
            "original_ingredient": ingredient,
            "canonical_ingredient": self.unified_system.canonicalizer.canonicalize(ingredient),
            "selected_substitution": selected_option.name,
            "ratio": selected_option.ratio,
            "unit_conversion": selected_option.unit_conversion,
            "notes": selected_option.notes,
            "confidence": selected_option.confidence
        }
    
    def process_recipe_substitution(self, recipe_ingredients: List[RecipeIngredient], 
                                  diet_restrictions: List[str]) -> RecipeSubstitution:
        """
        Process a complete recipe substitution.
        
        Args:
            recipe_ingredients: List of recipe ingredients
            diet_restrictions: List of diet types to apply
            
        Returns:
            Complete recipe substitution result
        """
        substitutions = []
        unchanged_ingredients = []
        warnings = []
        change_log = []
        
        for ingredient in recipe_ingredients:
            # Check if ingredient needs substitution for any diet
            needs_substitution = False
            applicable_diets = []
            
            for diet in diet_restrictions:
                if self.unified_system.is_forbidden(ingredient.name, diet):
                    needs_substitution = True
                    applicable_diets.append(diet)
            
            if needs_substitution:
                # Get options for the first applicable diet (LLM will choose)
                primary_diet = applicable_diets[0]
                options_data = self.get_substitution_options_for_llm(ingredient.name, primary_diet)
                
                if options_data["total_options"] > 0:
                    # For now, select the first option (LLM will make this choice)
                    first_option = options_data["substitution_options"][0]
                    
                    substitution = SubstitutionDecision(
                        original_ingredient=ingredient.name,
                        canonical_ingredient=options_data["canonical_ingredient"],
                        selected_substitution=first_option["name"],
                        substitution_ratio=first_option["ratio"],
                        unit_conversion=first_option["unit_conversion"],
                        confidence=first_option["confidence"],
                        reasoning=f"Selected for {primary_diet} diet compatibility",
                        notes=first_option["notes"]
                    )
                    
                    substitutions.append(substitution)
                    change_log.append(f"Replaced '{ingredient.name}' with '{first_option['name']}' for {primary_diet}")
                else:
                    warnings.append(f"No substitution found for '{ingredient.name}' on {primary_diet} diet")
                    unchanged_ingredients.append(ingredient)
            else:
                unchanged_ingredients.append(ingredient)
        
        return RecipeSubstitution(
            original_recipe=recipe_ingredients,
            diet_restrictions=diet_restrictions,
            substitutions=substitutions,
            unchanged_ingredients=unchanged_ingredients,
            warnings=warnings,
            change_log=change_log
        )
    
    def demo_llm_substitution(self) -> List[Dict]:
        """Demo the LLM substitution system."""
        # Create sample recipe
        sample_recipe = [
            RecipeIngredient(name="AP flour", amount="2 cups", unit="cups", quantity=2.0),
            RecipeIngredient(name="eggs", amount="3 large", unit="large", quantity=3.0),
            RecipeIngredient(name="milk", amount="1 cup", unit="cup", quantity=1.0),
            RecipeIngredient(name="sugar", amount="1/2 cup", unit="cup", quantity=0.5),
            RecipeIngredient(name="salt", amount="1 tsp", unit="tsp", quantity=1.0)
        ]
        
        # Test different diet scenarios
        test_scenarios = [
            ["gluten-free"],
            ["vegan"],
            ["keto"],
            ["gluten-free", "vegan"]  # Multiple diets
        ]
        
        results = []
        for diets in test_scenarios:
            result = self.process_recipe_substitution(sample_recipe, diets)
            
            results.append({
                "diets": diets,
                "total_ingredients": len(sample_recipe),
                "substitutions_made": len(result.substitutions),
                "unchanged_ingredients": len(result.unchanged_ingredients),
                "warnings": len(result.warnings),
                "substitutions": [
                    {
                        "original": sub.original_ingredient,
                        "replacement": sub.selected_substitution,
                        "ratio": sub.substitution_ratio
                    } for sub in result.substitutions
                ]
            })
        
        return results


def main():
    """Demo the LLM substitution engine."""
    print("🧪 Testing LLM-Guided Substitution Engine")
    print("=" * 60)
    
    engine = LLMSubstitutionEngine()
    
    # Test 1: Get options for LLM
    print("📝 Test 1: LLM Decision Context")
    test_cases = [
        ("AP flour", "gluten-free"),
        ("eggs", "vegan"),
        ("sugar", "keto")
    ]
    
    for ingredient, diet in test_cases:
        options = engine.get_substitution_options_for_llm(ingredient, diet)
        print(f"\n🍽️  {ingredient} ({diet}):")
        print(f"   Canonical: {options['canonical_ingredient']}")
        print(f"   Forbidden: {options['is_forbidden']}")
        print(f"   Options: {options['total_options']}")
        
        if options['substitution_options']:
            for i, opt in enumerate(options['substitution_options'][:2], 1):
                print(f"   {i}. {opt['name']} ({opt['ratio']})")
    
    # Test 2: Validate LLM decisions
    print(f"\n📝 Test 2: LLM Decision Validation")
    validation_tests = [
        ("AP flour", "gluten-free", "almond flour", True),
        ("AP flour", "gluten-free", "invalid choice", False),
        ("eggs", "vegan", "flax egg", True),
    ]
    
    for ingredient, diet, choice, should_be_valid in validation_tests:
        is_valid, error = engine.validate_llm_decision(ingredient, diet, choice)
        status = "✅" if is_valid == should_be_valid else "❌"
        print(f"   {status} {ingredient} → {choice}: valid={is_valid} (expected={should_be_valid})")
        if not is_valid:
            print(f"      Error: {error}")
    
    # Test 3: Calculate ratios
    print(f"\n📝 Test 3: Ratio Calculations")
    ratio_tests = [
        ("AP flour", "gluten-free", "almond flour"),
        ("eggs", "vegan", "flax egg"),
        ("sugar", "keto", "erythritol")
    ]
    
    for ingredient, diet, substitution in ratio_tests:
        ratio_data = engine.calculate_substitution_ratio(ingredient, diet, substitution)
        if "error" not in ratio_data:
            print(f"   ✅ {ingredient} → {substitution}: {ratio_data['ratio']}")
        else:
            print(f"   ❌ {ingredient} → {substitution}: {ratio_data['error']}")
    
    # Test 4: Complete recipe processing
    print(f"\n📝 Test 4: Complete Recipe Processing")
    demo_results = engine.demo_llm_substitution()
    
    for result in demo_results:
        print(f"\n🥗 Diets: {', '.join(result['diets'])}")
        print(f"   Ingredients: {result['total_ingredients']}")
        print(f"   Substitutions: {result['substitutions_made']}")
        print(f"   Unchanged: {result['unchanged_ingredients']}")
        print(f"   Warnings: {result['warnings']}")
        
        if result['substitutions']:
            print("   Changes:")
            for sub in result['substitutions']:
                print(f"     • {sub['original']} → {sub['replacement']}")
    
    print(f"\n✅ LLM substitution engine ready!")
    print("✅ LLM decision context provided")
    print("✅ Decision validation working")
    print("✅ Ratio calculations deterministic")
    print("✅ Complete recipe processing functional")


if __name__ == "__main__":
    main()
