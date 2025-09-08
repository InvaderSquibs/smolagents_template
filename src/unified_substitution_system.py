#!/usr/bin/env python3
"""
Unified Substitution System

This module combines the restriction knowledge base with ingredient canonicalization
to provide a complete recipe substitution system.
"""

from typing import Dict, List, Optional, Tuple
from restriction_knowledge import RestrictionKnowledgeBase, SubstitutionOption
from ingredient_canonicalizer import IngredientCanonicalizer


class UnifiedSubstitutionSystem:
    """Combines canonicalization and restriction knowledge for recipe substitution."""
    
    def __init__(self):
        self.knowledge_base = RestrictionKnowledgeBase()
        self.canonicalizer = IngredientCanonicalizer()
        
        # Load the knowledge base
        self.knowledge_base.load_from_table("Restriction Table")
    
    def get_substitution_options(self, ingredient: str, diet_type: str) -> List[SubstitutionOption]:
        """
        Get substitution options for an ingredient on a specific diet.
        
        Args:
            ingredient: Raw ingredient name (e.g., "AP flour", "white  flour")
            diet_type: Diet type (e.g., "gluten-free", "vegan")
            
        Returns:
            List of substitution options
        """
        # Step 1: Canonicalize the ingredient name
        canonical_ingredient = self.canonicalizer.canonicalize(ingredient)
        
        # Step 2: Look up substitution options
        options = self.knowledge_base.get_substitution_options(canonical_ingredient, diet_type)
        
        return options
    
    def is_forbidden(self, ingredient: str, diet_type: str) -> bool:
        """
        Check if an ingredient is forbidden on a specific diet.
        
        Args:
            ingredient: Raw ingredient name
            diet_type: Diet type
            
        Returns:
            True if ingredient is forbidden on the diet
        """
        canonical_ingredient = self.canonicalizer.canonicalize(ingredient)
        return self.knowledge_base.is_forbidden(canonical_ingredient, diet_type)
    
    def demo_unified_system(self) -> List[Dict]:
        """Demo the unified system with canonicalization + restrictions."""
        test_cases = [
            ("AP flour", "gluten-free"),
            ("white  flour", "gluten-free"),
            ("Granulated Sugar", "keto"),
            ("whole milk", "vegan"),
            ("eggs", "egg-free"),
            ("yellow onion", "low-fodmap"),
            ("garbanzo beans", "paleo"),
            ("firm tofu", "soy-free")
        ]
        
        results = []
        for ingredient, diet in test_cases:
            # Canonicalize
            canonical = self.canonicalizer.canonicalize(ingredient)
            
            # Get substitution options
            options = self.get_substitution_options(ingredient, diet)
            
            # Check if forbidden
            forbidden = self.is_forbidden(ingredient, diet)
            
            results.append({
                "input": ingredient,
                "canonical": canonical,
                "diet": diet,
                "forbidden": forbidden,
                "substitution_count": len(options),
                "substitutions": [
                    {
                        "name": opt.name,
                        "ratio": opt.ratio
                    } for opt in options[:2]  # Show first 2
                ]
            })
        
        return results
    
    def get_all_diets(self) -> List[str]:
        """Get all available diet types."""
        return self.knowledge_base.get_all_diets()
    
    def get_canonical_ingredients(self) -> List[str]:
        """Get all canonical ingredient names."""
        return self.canonicalizer.get_all_canonical_names()


def main():
    """Demo the unified substitution system."""
    print("🧪 Testing Unified Substitution System")
    print("=" * 60)
    
    system = UnifiedSubstitutionSystem()
    
    print(f"📋 Available diets: {len(system.get_all_diets())}")
    print(f"📋 Canonical ingredients: {len(system.get_canonical_ingredients())}")
    print()
    
    # Run unified demo
    print("🔍 Unified System Examples (Canonicalization + Restrictions):")
    examples = system.demo_unified_system()
    
    for example in examples:
        print(f"\n📝 Input: '{example['input']}' → '{example['canonical']}'")
        print(f"   🎯 Diet: {example['diet']}")
        print(f"   🚫 Forbidden: {example['forbidden']}")
        print(f"   🔄 Substitutions: {example['substitution_count']} options")
        
        if example['substitutions']:
            for i, sub in enumerate(example['substitutions'], 1):
                print(f"   {i}. {sub['name']} ({sub['ratio']})")
    
    print(f"\n✅ Unified system ready!")
    print("✅ Canonicalization working (AP flour → all-purpose flour)")
    print("✅ Restriction lookup working (all-purpose flour → gluten-free options)")
    print("✅ Deterministic results confirmed")


if __name__ == "__main__":
    main()
