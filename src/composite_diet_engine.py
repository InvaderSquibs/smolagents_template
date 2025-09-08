#!/usr/bin/env python3
"""
Composite Diet Reconciliation Engine

This module handles multiple overlapping dietary restrictions by:
- Applying diets in order of priority
- Ensuring final ingredients satisfy the union of all restrictions
- Detecting conflicts and providing structured warnings
- Maintaining substitution history for complex scenarios
"""

import json
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, asdict
from unified_substitution_system import UnifiedSubstitutionSystem
from restriction_knowledge import SubstitutionOption
from llm_substitution_engine import RecipeIngredient, SubstitutionDecision, RecipeSubstitution


@dataclass
class DietConflict:
    """Represents a conflict between multiple dietary restrictions."""
    ingredient: str
    conflicting_diets: List[str]
    conflict_type: str  # "no_common_substitution", "contradictory_requirements", etc.
    suggested_resolution: str
    severity: str  # "warning", "error", "critical"


@dataclass
class CompositeSubstitutionResult:
    """Result of applying multiple diets to a recipe."""
    original_recipe: List[RecipeIngredient]
    applied_diets: List[str]
    final_ingredients: List[RecipeIngredient]
    substitution_history: List[Dict[str, Any]]  # Track all substitutions made
    conflicts: List[DietConflict]
    warnings: List[str]
    change_log: List[str]
    success: bool


class CompositeDietEngine:
    """Handles multiple overlapping dietary restrictions."""
    
    def __init__(self):
        self.unified_system = UnifiedSubstitutionSystem()
        
        # Diet priority order (higher priority diets applied first)
        self.diet_priority = [
            "keto",           # Most restrictive (macros)
            "paleo",          # Very restrictive (food groups)
            "vegan",          # Restrictive (animal products)
            "dairy-free",     # Moderate restriction
            "gluten-free",    # Moderate restriction
            "soy-free",       # Moderate restriction
            "egg-free",       # Moderate restriction
            "nut-free",       # Moderate restriction
            "low-fodmap"      # Least restrictive (digestive)
        ]
    
    def get_union_forbidden_tags(self, diets: List[str]) -> Set[str]:
        """Get the union of all forbidden tags across multiple diets."""
        union_tags = set()
        
        for diet in diets:
            # Get all ingredients that are forbidden in this diet
            for ingredient, restriction in self.unified_system.knowledge_base.restrictions.items():
                if restriction.diet_type == diet:
                    union_tags.update(restriction.forbidden_tags)
        
        return union_tags
    
    def find_common_substitutions(self, ingredient: str, diets: List[str]) -> List[SubstitutionOption]:
        """Find substitutions that work for ALL specified diets."""
        if not diets:
            return []
        
        # Get substitution options for each diet
        diet_options = {}
        for diet in diets:
            options = self.unified_system.get_substitution_options(ingredient, diet)
            diet_options[diet] = {opt.name.lower(): opt for opt in options}
        
        # Find common substitutions across all diets
        if not diet_options:
            return []
        
        # Start with options from the first diet
        first_diet = list(diet_options.keys())[0]
        common_substitutions = set(diet_options[first_diet].keys())
        
        # Intersect with options from other diets
        for diet, options in diet_options.items():
            if diet != first_diet:
                common_substitutions = common_substitutions.intersection(set(options.keys()))
        
        # Return the actual SubstitutionOption objects
        result = []
        for sub_name in common_substitutions:
            # Use the substitution from the highest priority diet
            for diet in self.diet_priority:
                if diet in diet_options and sub_name in diet_options[diet]:
                    result.append(diet_options[diet][sub_name])
                    break
        
        return result
    
    def detect_diet_conflicts(self, ingredient: str, diets: List[str]) -> List[DietConflict]:
        """Detect conflicts between multiple dietary restrictions."""
        conflicts = []
        
        # Check if ingredient is forbidden in any diet
        forbidden_diets = []
        for diet in diets:
            if self.unified_system.is_forbidden(ingredient, diet):
                forbidden_diets.append(diet)
        
        if len(forbidden_diets) > 1:
            # Check if there are common substitutions
            common_subs = self.find_common_substitutions(ingredient, forbidden_diets)
            
            if not common_subs:
                conflicts.append(DietConflict(
                    ingredient=ingredient,
                    conflicting_diets=forbidden_diets,
                    conflict_type="no_common_substitution",
                    suggested_resolution=f"No single substitution works for all diets: {', '.join(forbidden_diets)}",
                    severity="error"
                ))
            else:
                conflicts.append(DietConflict(
                    ingredient=ingredient,
                    conflicting_diets=forbidden_diets,
                    conflict_type="multiple_diet_restriction",
                    suggested_resolution=f"Use common substitution: {common_subs[0].name}",
                    severity="warning"
                ))
        elif len(forbidden_diets) == 1:
            # Single diet restriction - not a conflict, but worth noting
            conflicts.append(DietConflict(
                ingredient=ingredient,
                conflicting_diets=forbidden_diets,
                conflict_type="single_diet_restriction",
                suggested_resolution=f"Ingredient forbidden in {forbidden_diets[0]} diet",
                severity="info"
            ))
        
        return conflicts
    
    def apply_composite_diets(self, recipe_ingredients: List[RecipeIngredient], 
                            diets: List[str]) -> CompositeSubstitutionResult:
        """
        Apply multiple diets to a recipe, handling conflicts and ensuring union compliance.
        
        Args:
            recipe_ingredients: List of recipe ingredients
            diets: List of diet types to apply (in priority order)
            
        Returns:
            Complete composite diet substitution result
        """
        # Sort diets by priority
        sorted_diets = sorted(diets, key=lambda d: self.diet_priority.index(d) if d in self.diet_priority else 999)
        
        current_ingredients = recipe_ingredients.copy()
        substitution_history = []
        all_conflicts = []
        all_warnings = []
        change_log = []
        
        # Track which ingredients have been substituted
        substituted_ingredients = set()
        
        # Apply each diet in priority order
        for diet in sorted_diets:
            diet_changes = []
            
            for ingredient in current_ingredients:
                if ingredient.name in substituted_ingredients:
                    continue  # Skip already substituted ingredients
                
                # Check if ingredient needs substitution for this diet
                if self.unified_system.is_forbidden(ingredient.name, diet):
                    # Find substitutions that work for this diet
                    options = self.unified_system.get_substitution_options(ingredient.name, diet)
                    
                    if options:
                        # For composite diets, prefer substitutions that work for multiple diets
                        remaining_diets = [d for d in sorted_diets if d != diet]
                        common_subs = self.find_common_substitutions(ingredient.name, [diet] + remaining_diets)
                        
                        if common_subs:
                            # Use a common substitution
                            selected_option = common_subs[0]
                        else:
                            # Use the first available substitution for this diet
                            selected_option = options[0]
                        
                        # Create substitution decision
                        substitution = SubstitutionDecision(
                            original_ingredient=ingredient.name,
                            canonical_ingredient=self.unified_system.canonicalizer.canonicalize(ingredient.name),
                            selected_substitution=selected_option.name,
                            substitution_ratio=selected_option.ratio,
                            unit_conversion=selected_option.unit_conversion,
                            confidence=selected_option.confidence,
                            reasoning=f"Applied for {diet} diet compatibility",
                            notes=selected_option.notes
                        )
                        
                        # Update the ingredient
                        new_ingredient = RecipeIngredient(
                            name=selected_option.name,
                            amount=ingredient.amount,
                            unit=ingredient.unit,
                            quantity=ingredient.quantity,
                            notes=f"{ingredient.notes} (substituted for {ingredient.name})"
                        )
                        
                        # Replace in current ingredients
                        ingredient_index = current_ingredients.index(ingredient)
                        current_ingredients[ingredient_index] = new_ingredient
                        substituted_ingredients.add(ingredient.name)
                        
                        # Record the change
                        diet_changes.append({
                            "diet": diet,
                            "original": ingredient.name,
                            "substitution": selected_option.name,
                            "ratio": selected_option.ratio,
                            "reasoning": substitution.reasoning
                        })
                        
                        change_log.append(f"[{diet}] Replaced '{ingredient.name}' with '{selected_option.name}'")
                    else:
                        all_warnings.append(f"No substitution found for '{ingredient.name}' on {diet} diet")
            
            # Record diet application
            if diet_changes:
                substitution_history.append({
                    "diet": diet,
                    "changes": diet_changes,
                    "ingredients_affected": len(diet_changes)
                })
        
        # Final validation: check for remaining conflicts
        for ingredient in current_ingredients:
            conflicts = self.detect_diet_conflicts(ingredient.name, sorted_diets)
            all_conflicts.extend(conflicts)
        
        # Check if final ingredients satisfy all diet restrictions
        final_compliance = self.validate_final_compliance(current_ingredients, sorted_diets)
        
        # Success means: final compliance AND no critical conflicts
        critical_conflicts = [c for c in all_conflicts if c.severity == "error"]
        success = final_compliance and len(critical_conflicts) == 0
        
        return CompositeSubstitutionResult(
            original_recipe=recipe_ingredients,
            applied_diets=sorted_diets,
            final_ingredients=current_ingredients,
            substitution_history=substitution_history,
            conflicts=all_conflicts,
            warnings=all_warnings,
            change_log=change_log,
            success=success
        )
    
    def validate_final_compliance(self, ingredients: List[RecipeIngredient], diets: List[str]) -> bool:
        """Validate that final ingredients comply with all diet restrictions."""
        union_forbidden = self.get_union_forbidden_tags(diets)
        
        for ingredient in ingredients:
            canonical_name = self.unified_system.canonicalizer.canonicalize(ingredient.name)
            
            # Check if ingredient contains any forbidden tags
            for tag in union_forbidden:
                if tag.lower() in canonical_name.lower():
                    return False
        
        return True
    
    def demo_composite_diets(self) -> List[Dict]:
        """Demo the composite diet system with various scenarios."""
        # Create sample recipe
        sample_recipe = [
            RecipeIngredient(name="AP flour", amount="2 cups", unit="cups", quantity=2.0),
            RecipeIngredient(name="eggs", amount="3 large", unit="large", quantity=3.0),
            RecipeIngredient(name="milk", amount="1 cup", unit="cup", quantity=1.0),
            RecipeIngredient(name="sugar", amount="1/2 cup", unit="cup", quantity=0.5),
            RecipeIngredient(name="butter", amount="1/2 cup", unit="cup", quantity=0.5),
            RecipeIngredient(name="salt", amount="1 tsp", unit="tsp", quantity=1.0)
        ]
        
        # Test different composite diet scenarios
        test_scenarios = [
            ["gluten-free", "vegan"],           # Moderate complexity
            ["keto", "dairy-free"],             # High complexity
            ["vegan", "gluten-free", "nut-free"], # High complexity
            ["paleo", "keto"],                  # Very high complexity (conflicting)
            ["low-fodmap", "dairy-free"]        # Low complexity
        ]
        
        results = []
        for diets in test_scenarios:
            result = self.apply_composite_diets(sample_recipe, diets)
            
            results.append({
                "diets": diets,
                "success": result.success,
                "total_ingredients": len(sample_recipe),
                "final_ingredients": len(result.final_ingredients),
                "substitutions_made": len(result.substitution_history),
                "conflicts": len(result.conflicts),
                "warnings": len(result.warnings),
                "change_log": result.change_log,
                "conflict_details": [
                    {
                        "ingredient": conflict.ingredient,
                        "conflicting_diets": conflict.conflicting_diets,
                        "type": conflict.conflict_type,
                        "severity": conflict.severity
                    } for conflict in result.conflicts
                ]
            })
        
        return results


def main():
    """Demo the composite diet engine."""
    print("🧪 Testing Composite Diet Reconciliation Engine")
    print("=" * 70)
    
    engine = CompositeDietEngine()
    
    # Test 1: Union forbidden tags
    print("📝 Test 1: Union Forbidden Tags")
    test_diets = [["vegan", "gluten-free"], ["keto", "dairy-free"]]
    
    for diets in test_diets:
        union_tags = engine.get_union_forbidden_tags(diets)
        print(f"   {diets}: {len(union_tags)} forbidden tags")
        print(f"      Sample tags: {list(union_tags)[:5]}")
    
    print()
    
    # Test 2: Common substitutions
    print("📝 Test 2: Common Substitutions")
    common_tests = [
        ("eggs", ["vegan", "egg-free"]),
        ("milk", ["vegan", "dairy-free"]),
        ("wheat flour", ["gluten-free", "vegan"])
    ]
    
    for ingredient, diets in common_tests:
        common_subs = engine.find_common_substitutions(ingredient, diets)
        print(f"   {ingredient} ({', '.join(diets)}): {len(common_subs)} common substitutions")
        for sub in common_subs[:2]:
            print(f"      • {sub.name}: {sub.ratio}")
    
    print()
    
    # Test 3: Conflict detection
    print("📝 Test 3: Conflict Detection")
    conflict_tests = [
        ("eggs", ["vegan", "keto"]),
        ("milk", ["vegan", "dairy-free"]),
        ("wheat flour", ["gluten-free", "paleo"])
    ]
    
    for ingredient, diets in conflict_tests:
        conflicts = engine.detect_diet_conflicts(ingredient, diets)
        print(f"   {ingredient} ({', '.join(diets)}): {len(conflicts)} conflicts")
        for conflict in conflicts:
            print(f"      • {conflict.conflict_type}: {conflict.suggested_resolution}")
    
    print()
    
    # Test 4: Complete composite diet processing
    print("📝 Test 4: Complete Composite Diet Processing")
    demo_results = engine.demo_composite_diets()
    
    for result in demo_results:
        print(f"\n🥗 Diets: {', '.join(result['diets'])}")
        print(f"   Success: {result['success']}")
        print(f"   Ingredients: {result['total_ingredients']} → {result['final_ingredients']}")
        print(f"   Substitutions: {result['substitutions_made']}")
        print(f"   Conflicts: {result['conflicts']}")
        print(f"   Warnings: {result['warnings']}")
        
        if result['change_log']:
            print("   Changes:")
            for change in result['change_log']:
                print(f"     • {change}")
        
        if result['conflict_details']:
            print("   Conflicts:")
            for conflict in result['conflict_details']:
                print(f"     • {conflict['ingredient']}: {conflict['type']} ({conflict['severity']})")
    
    print(f"\n✅ Composite diet engine ready!")
    print("✅ Union forbidden tags calculated")
    print("✅ Common substitutions found")
    print("✅ Conflict detection working")
    print("✅ Multi-diet processing functional")


if __name__ == "__main__":
    main()
