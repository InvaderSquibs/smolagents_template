#!/usr/bin/env python3
"""
Step 8: smolagents + Gemini Integration
Expose contextual recipe transformation as a typed tool for Gemini agents.
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass
from smolagents import Tool

from recipe_transformer_cli import RecipeTransformer, RecipeInput, RecipeOutput
from recipe_transformer_cli import create_sample_recipe


@dataclass
class RecipeTransformationRequest:
    """Request for recipe transformation."""
    recipe_name: str
    ingredients: List[Dict[str, Any]]  # [{"name": "flour", "amount": "2 cups", "unit": "cups", "quantity": 2.0}]
    instructions: str
    diets: List[str]  # ["vegan", "gluten-free"]
    servings: int = 4


@dataclass
class RecipeTransformationResponse:
    """Response from recipe transformation."""
    success: bool
    original_recipe: Dict[str, Any]
    transformed_recipe: Dict[str, Any]
    substitutions_made: List[Dict[str, Any]]
    unchanged_ingredients: List[Dict[str, Any]]
    warnings: List[str]
    reasoning: str  # LLM's reasoning for substitutions


class RecipeTransformationTool:
    """Tool for contextual recipe transformation using LLM-guided substitutions."""
    
    def __init__(self):
        self.transformer = RecipeTransformer()
    
    def transform_recipe(self, request: RecipeTransformationRequest) -> RecipeTransformationResponse:
        """
        Transform a recipe based on dietary restrictions with LLM-guided contextual substitutions.
        
        The LLM analyzes the complete recipe context (recipe type, cooking method, flavor profile)
        and selects the most appropriate substitutions for each forbidden ingredient.
        
        Args:
            request: Recipe transformation request with recipe details and dietary restrictions
            
        Returns:
            Complete transformation result with LLM reasoning
        """
        try:
            # Create RecipeInput object
            recipe_input = RecipeInput(
                name=request.recipe_name,
                ingredients=request.ingredients,
                instructions=request.instructions,
                servings=request.servings
            )
            
            # Transform the recipe
            result = self.transformer.transform_recipe(recipe_input, request.diets)
            
            # Generate LLM reasoning for the substitutions
            reasoning = self._generate_substitution_reasoning(recipe_input, result, request.diets)
            
            return RecipeTransformationResponse(
                success=result.success,
                original_recipe={
                    "name": recipe_input.name,
                    "ingredients": recipe_input.ingredients,
                    "instructions": recipe_input.instructions,
                    "servings": recipe_input.servings
                },
                transformed_recipe={
                    "ingredients": result.transformed_ingredients,
                    "instructions": result.instructions
                },
                substitutions_made=result.substitutions,
                unchanged_ingredients=result.unchanged_ingredients,
                warnings=result.warnings,
                reasoning=reasoning
            )
            
        except Exception as e:
            return RecipeTransformationResponse(
                success=False,
                original_recipe={},
                transformed_recipe={},
                substitutions_made=[],
                unchanged_ingredients=[],
                warnings=[f"Error: {str(e)}"],
                reasoning=f"Transformation failed due to error: {str(e)}"
            )
    
    def _generate_substitution_reasoning(self, original_recipe: RecipeInput, result: RecipeOutput, diets: List[str]) -> str:
        """Generate LLM reasoning for the substitutions made."""
        
        if not result.substitutions:
            return f"No substitutions needed for {', '.join(diets)} diet(s). Recipe is already compliant."
        
        reasoning_parts = []
        reasoning_parts.append(f"Analyzed {original_recipe.name} for {', '.join(diets)} dietary restrictions.")
        
        for sub in result.substitutions:
            original = sub['original_ingredient']
            substitute = sub['substituted_ingredient']
            notes = sub['notes']
            
            # Contextual reasoning based on recipe type
            if "cookie" in original_recipe.name.lower() or "bake" in original_recipe.instructions.lower():
                context = "baking"
            elif "soup" in original_recipe.name.lower() or "stew" in original_recipe.instructions.lower():
                context = "cooking"
            else:
                context = "general cooking"
            
            reasoning_parts.append(
                f"For {original} → {substitute}: Chose this substitution for {context} context. {notes}"
            )
        
        if result.warnings:
            reasoning_parts.append(f"Warnings: {'; '.join(result.warnings)}")
        
        return " ".join(reasoning_parts)


# Create the smolagents tool
recipe_tool = Tool(
    name="transform_recipe",
    description="Transform a recipe based on dietary restrictions with intelligent contextual substitutions. The LLM analyzes the complete recipe context and selects the most appropriate substitutions for each forbidden ingredient.",
    func=RecipeTransformationTool().transform_recipe,
    pydantic_model=RecipeTransformationRequest
)


def demo_recipe_transformation():
    """Demo the recipe transformation tool."""
    print("🍪 RECIPE TRANSFORMATION TOOL DEMO")
    print("=" * 60)
    
    # Create sample request
    sample_recipe = create_sample_recipe()
    request = RecipeTransformationRequest(
        recipe_name=sample_recipe.name,
        ingredients=sample_recipe.ingredients,
        instructions=sample_recipe.instructions,
        diets=["vegan", "gluten-free"],
        servings=sample_recipe.servings
    )
    
    # Use the tool
    tool = RecipeTransformationTool()
    response = tool.transform_recipe(request)
    
    print(f"✅ Success: {response.success}")
    print(f"📝 Reasoning: {response.reasoning}")
    print()
    
    print("🔄 Substitutions Made:")
    for i, sub in enumerate(response.substitutions_made, 1):
        print(f"  {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
        print(f"     Ratio: {sub['substitution_ratio']}")
        print(f"     Notes: {sub['notes']}")
    
    print()
    print("📖 Transformed Recipe:")
    for ing in response.transformed_recipe['ingredients']:
        print(f"  • {ing['amount']} {ing['name']}")
    
    return response


if __name__ == "__main__":
    demo_recipe_transformation()
