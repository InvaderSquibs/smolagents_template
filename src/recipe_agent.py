#!/usr/bin/env python3
"""
Recipe Transformation Agent using smolagents + Gemini

This is the main LLM agent that makes intelligent contextual decisions about
recipe substitutions based on dietary restrictions.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from smolagents import CodeAgent, Tool
from smolagents import OpenAIServerModel

# Load environment variables from .env file in root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from llm_substitution_engine import LLMSubstitutionEngine, RecipeIngredient
from restriction_knowledge import RestrictionKnowledgeBase
from ingredient_canonicalizer import IngredientCanonicalizer


@dataclass
class RecipeContext:
    """Context information for recipe transformation."""
    recipe_name: str
    recipe_type: str  # e.g., "cake", "pasta", "salad"
    cooking_method: str  # e.g., "baking", "stovetop", "raw"
    flavor_profile: str  # e.g., "sweet", "savory", "spicy"
    serving_size: int
    dietary_restrictions: List[str]
    original_ingredients: List[Dict[str, Any]]


@dataclass
class SubstitutionDecision:
    """LLM's decision about ingredient substitution."""
    original_ingredient: str
    selected_substitution: str
    reasoning: str
    confidence: float
    contextual_notes: str


class RecipeAnalysisTool(Tool):
    """Tool for analyzing recipe context and ingredients."""
    
    name: str = "analyze_recipe"
    description: str = (
        "Analyze a recipe to understand its context, cooking method, and flavor profile. "
        "This helps the agent make better substitution decisions."
    )
    inputs: dict = {
        "recipe_data": {
            "type": "object",
            "description": "Recipe data including name, ingredients, and instructions"
        }
    }
    output_type: dict = "object"
    
    def __init__(self):
        super().__init__()
    
    def forward(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze recipe context."""
        try:
            # Extract recipe information
            name = recipe_data.get("name", "Unknown Recipe")
            ingredients = recipe_data.get("ingredients", [])
            instructions = recipe_data.get("instructions", "")
            
            # Determine recipe type based on name and ingredients
            recipe_type = self._determine_recipe_type(name, ingredients)
            
            # Determine cooking method from instructions
            cooking_method = self._determine_cooking_method(instructions)
            
            # Determine flavor profile
            flavor_profile = self._determine_flavor_profile(ingredients, name)
            
            return {
                "recipe_name": name,
                "recipe_type": recipe_type,
                "cooking_method": cooking_method,
                "flavor_profile": flavor_profile,
                "serving_size": recipe_data.get("servings", 4),
                "ingredient_count": len(ingredients),
                "analysis_confidence": 0.9
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze recipe: {str(e)}"}
    
    def _determine_recipe_type(self, name: str, ingredients: List[Dict]) -> str:
        """Determine recipe type based on name and ingredients."""
        name_lower = name.lower()
        ingredient_names = [ing.get("name", "").lower() for ing in ingredients]
        
        # Check for baking indicators
        baking_indicators = ["flour", "baking powder", "baking soda", "oven", "bake"]
        if any(indicator in name_lower for indicator in ["cake", "cookie", "bread", "muffin", "pie"]) or \
           any(any(indicator in ing_name for indicator in baking_indicators) for ing_name in ingredient_names):
            return "baking"
        
        # Check for stovetop indicators
        stovetop_indicators = ["pasta", "rice", "soup", "stir", "fry", "sauté"]
        if any(indicator in name_lower for indicator in stovetop_indicators):
            return "stovetop"
        
        # Check for raw/no-cook indicators
        raw_indicators = ["salad", "smoothie", "juice", "raw"]
        if any(indicator in name_lower for indicator in raw_indicators):
            return "raw"
        
        return "mixed"
    
    def _determine_cooking_method(self, instructions: str) -> str:
        """Determine cooking method from instructions."""
        instructions_lower = instructions.lower()
        
        if "bake" in instructions_lower or "oven" in instructions_lower:
            return "baking"
        elif "fry" in instructions_lower or "sauté" in instructions_lower or "stir" in instructions_lower:
            return "stovetop"
        elif "boil" in instructions_lower or "simmer" in instructions_lower:
            return "boiling"
        elif "grill" in instructions_lower:
            return "grilling"
        else:
            return "mixed"
    
    def _determine_flavor_profile(self, ingredients: List[Dict], name: str) -> str:
        """Determine flavor profile from ingredients and name."""
        name_lower = name.lower()
        ingredient_names = [ing.get("name", "").lower() for ing in ingredients]
        all_text = " ".join(ingredient_names + [name_lower])
        
        # Check for sweet indicators
        sweet_indicators = ["sugar", "honey", "chocolate", "vanilla", "sweet", "cake", "cookie", "dessert"]
        if any(indicator in all_text for indicator in sweet_indicators):
            return "sweet"
        
        # Check for savory indicators
        savory_indicators = ["salt", "garlic", "onion", "herbs", "spices", "meat", "cheese"]
        if any(indicator in all_text for indicator in savory_indicators):
            return "savory"
        
        # Check for spicy indicators
        spicy_indicators = ["pepper", "chili", "hot", "spicy", "cayenne"]
        if any(indicator in all_text for indicator in spicy_indicators):
            return "spicy"
        
        return "neutral"


class IngredientSubstitutionTool(Tool):
    """Tool for getting substitution options for ingredients."""
    
    name: str = "get_substitution_options"
    description: str = (
        "Get available substitution options for a specific ingredient based on dietary restrictions. "
        "Returns detailed information about each option including ratios, notes, and confidence scores."
    )
    inputs: dict = {
        "ingredient": {
            "type": "string",
            "description": "The ingredient name to find substitutions for"
        },
        "diet_type": {
            "type": "string", 
            "description": "The dietary restriction type (e.g., 'vegan', 'gluten-free')"
        }
    }
    output_type: dict = "object"
    
    def __init__(self):
        super().__init__()
        self.llm_engine = LLMSubstitutionEngine()
    
    def forward(self, ingredient: str, diet_type: str) -> Dict[str, Any]:
        """Get substitution options for an ingredient."""
        try:
            return self.llm_engine.get_substitution_options_for_llm(ingredient, diet_type)
        except Exception as e:
            return {"error": f"Failed to get substitution options: {str(e)}"}


class SubstitutionDecisionTool(Tool):
    """Tool for making final substitution decisions."""
    
    name: str = "make_substitution_decision"
    description: str = (
        "Make an intelligent substitution decision based on recipe context, available options, "
        "and dietary requirements. This is where the LLM's reasoning comes into play."
    )
    inputs: dict = {
        "ingredient": {
            "type": "string",
            "description": "The original ingredient name"
        },
        "diet_type": {
            "type": "string",
            "description": "The dietary restriction type"
        },
        "substitution_options": {
            "type": "array",
            "description": "List of available substitution options with details"
        },
        "recipe_context": {
            "type": "object",
            "description": "Context about the recipe (type, cooking method, flavor profile)"
        }
    }
    output_type: dict = "object"
    
    def __init__(self):
        super().__init__()
        self.llm_engine = LLMSubstitutionEngine()
    
    def forward(self, ingredient: str, diet_type: str, substitution_options: Any, 
                 recipe_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make intelligent substitution decision."""
        try:
            # Handle both array and object formats for substitution_options
            if isinstance(substitution_options, dict):
                # If it's a dict, extract the options array
                options_list = substitution_options.get("substitution_options", [])
            elif isinstance(substitution_options, list):
                # If it's already a list, use it directly
                options_list = substitution_options
            else:
                options_list = []
            
            if not options_list:
                return {
                    "selected_substitution": None,
                    "reasoning": f"No substitution options available for {ingredient}",
                    "confidence": 0.0,
                    "contextual_notes": "Cannot substitute this ingredient"
                }
            
            # Simple decision logic (this will be replaced by LLM reasoning)
            best_option = None
            best_score = 0
            
            for option in options_list:
                score = option.get("confidence", 0.5)
                
                # Boost score based on recipe context
                if recipe_context.get("recipe_type") == "baking" and "flour" in option.get("name", "").lower():
                    score += 0.2
                elif recipe_context.get("cooking_method") == "baking" and "oil" in option.get("name", "").lower():
                    score += 0.1
                
                if score > best_score:
                    best_score = score
                    best_option = option
            
            if best_option:
                return {
                    "selected_substitution": best_option["name"],
                    "reasoning": f"Selected {best_option['name']} based on recipe context and confidence score",
                    "confidence": best_score,
                    "contextual_notes": best_option.get("notes", ""),
                    "substitution_ratio": best_option.get("ratio", "1:1")
                }
            else:
                return {
                    "selected_substitution": options_list[0]["name"],
                    "reasoning": "Selected first available option as fallback",
                    "confidence": 0.5,
                    "contextual_notes": "Fallback selection"
                }
                
        except Exception as e:
            return {"error": f"Failed to make substitution decision: {str(e)}"}


class RecipeTransformationAgent:
    """Main LLM agent for recipe transformation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent with Gemini API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Initialize the LLM model (Gemini via OpenAI-compatible API)
        self.model = OpenAIServerModel(
            model_id="gemini-1.5-flash",
            api_key=self.api_key,
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Initialize tools
        self.recipe_analysis_tool = RecipeAnalysisTool()
        self.substitution_options_tool = IngredientSubstitutionTool()
        self.decision_tool = SubstitutionDecisionTool()
        
        # Create the agent with tools
        self.agent = CodeAgent(
            model=self.model,
            tools=[
                self.recipe_analysis_tool,
                self.substitution_options_tool, 
                self.decision_tool
            ],
            additional_authorized_imports=['json']
        )
        
        # Initialize substitution engine
        self.llm_engine = LLMSubstitutionEngine()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the recipe transformation agent."""
        return """You are an expert recipe transformation agent specializing in adapting recipes for dietary restrictions.

Your role is to:
1. Analyze recipe context (type, cooking method, flavor profile)
2. Identify ingredients that need substitution based on dietary restrictions
3. Make intelligent, contextual substitution decisions
4. Provide clear reasoning for your choices

Key principles:
- Consider the recipe's cooking method when choosing substitutions
- Maintain flavor profiles and texture where possible
- Prioritize substitutions that work well with the cooking technique
- Provide clear reasoning for your decisions
- Consider the overall balance of the recipe

When making substitution decisions, consider:
- Recipe type (baking vs stovetop vs raw)
- Cooking temperature and method
- Flavor profile (sweet, savory, spicy, etc.)
- Texture requirements
- Binding properties for baking
- Fat content for cooking methods

Always explain your reasoning clearly and consider the practical cooking implications of your choices."""

    def transform_recipe(self, recipe_data: Dict[str, Any], dietary_restrictions: List[str]) -> Dict[str, Any]:
        """Transform a recipe using LLM-guided decisions."""
        try:
            # Let the LLM agent do all the work and return a cookbook format
            transformation_prompt = f"""
            I need to transform a recipe for dietary restrictions. Here's what I need you to do:
            
            1. First, analyze this recipe using the analyze_recipe tool
            2. Then, for each ingredient that needs substitution for {', '.join(dietary_restrictions)}:
               - Use get_substitution_options to find alternatives
               - Use make_substitution_decision to choose the best one
            3. Finally, create a complete transformed recipe in cookbook format
            
            Recipe: {json.dumps(recipe_data, indent=2)}
            Dietary Restrictions: {', '.join(dietary_restrictions)}
            
            IMPORTANT: When creating the final recipe, make sure to:
            - Replace the ingredient names in the ingredients list with the actual substitution names
            - For example, if you substitute "eggs" with "flax eggs", the ingredients list should show "flax eggs", not "eggs"
            - Keep the same amounts and units, just change the ingredient names
            - When accessing substitution decisions, use the 'selected_substitution' field, not the entire decision object
            - For example: if substitution_decision = {{'selected_substitution': 'flax egg', 'reasoning': '...'}}, use substitution_decision['selected_substitution'] which is 'flax egg'
            
            Please work through this step by step and return the final transformed recipe in a cookbook format with:
            - Recipe title with dietary restriction noted
            - Complete ingredients list with substitutions applied (ingredient names changed to substitutions)
            - Original cooking instructions
            - Notes about substitutions made
            
            Format it like a proper cookbook recipe that someone could actually use to cook with.
            """
            
            # Run the agent and get the final result
            agent_response = self.agent.run(transformation_prompt)
            
            # The agent now returns a cookbook format directly
            # Let's create a simple result that just contains the cookbook text
            result = {
                "success": True,
                "original_recipe": recipe_data,
                "dietary_restrictions": dietary_restrictions,
                "recipe_context": {
                    "recipe_type": "baking",
                    "cooking_method": "baking",
                    "flavor_profile": "sweet"
                },
                "substitutions": [],  # We'll extract these from the cookbook text
                "unchanged_ingredients": [],
                "total_substitutions": 0,
                "agent_reasoning": "LLM agent created a complete cookbook-style recipe",
                "cookbook_recipe": agent_response  # The full cookbook text
            }
            
            # Try to extract substitutions from the cookbook text for summary
            try:
                import re
                substitutions_list = []
                
                # Look for substitution patterns in the cookbook text
                substitution_patterns = [
                    r'(\w+)\s*→\s*(\w+)',  # "eggs → flax egg"
                    r'(\w+)\s*replaced with\s*(\w+)',  # "eggs replaced with flax egg"
                    r'(\w+)\s*substituted with\s*(\w+)',  # "eggs substituted with flax egg"
                ]
                
                for pattern in substitution_patterns:
                    matches = re.findall(pattern, agent_response, re.IGNORECASE)
                    for match in matches:
                        substitutions_list.append({
                            "original_ingredient": match[0],
                            "substituted_ingredient": match[1],
                            "reasoning": "Substitution made for dietary compliance",
                            "confidence": 1.0,
                            "contextual_notes": "See cookbook recipe for details"
                        })
                
                result["substitutions"] = substitutions_list
                result["total_substitutions"] = len(substitutions_list)
                
            except Exception as e:
                pass  # Keep the basic result even if extraction fails
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Agent transformation failed: {str(e)}",
                "original_recipe": recipe_data,
                "dietary_restrictions": dietary_restrictions
            }
    


def demo_recipe_agent():
    """Demo the recipe transformation agent."""
    print("🤖 RECIPE TRANSFORMATION AGENT DEMO")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY=your_api_key_here")
        return
    
    try:
        # Initialize agent
        agent = RecipeTransformationAgent(api_key)
        
        # Sample recipe
        sample_recipe = {
            "name": "Chocolate Layer Cake",
            "ingredients": [
                {"name": "all-purpose flour", "amount": "2 1/4 cups", "unit": "cups", "quantity": 2.25},
                {"name": "eggs", "amount": "2 large", "unit": "large", "quantity": 2},
                {"name": "milk", "amount": "1 cup", "unit": "cup", "quantity": 1},
                {"name": "butter", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5}
            ],
            "instructions": "Preheat oven to 350°F. Mix dry ingredients. Add wet ingredients. Bake for 30-35 minutes.",
            "servings": 12
        }
        
        # Transform recipe
        result = agent.transform_recipe(sample_recipe, ["vegan", "gluten-free"])
        
        print(f"✅ Success: {result['success']}")
        print(f"🔄 Substitutions Made: {result['total_substitutions']}")
        
        for i, sub in enumerate(result.get("substitutions", []), 1):
            print(f"  {i}. {sub['original_ingredient']} → {sub['substituted_ingredient']}")
            print(f"     Reasoning: {sub['reasoning']}")
            print(f"     Confidence: {sub['confidence']:.2f}")
        
        print(f"\n🤖 Agent Reasoning: {result.get('agent_reasoning', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    demo_recipe_agent()
