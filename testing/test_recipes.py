#!/usr/bin/env python3
"""
Step 9: Comprehensive Test Recipes
10 diverse recipes for robust error rate testing across multiple diet combinations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TestRecipe:
    """Test recipe data structure."""
    name: str
    ingredients: List[Dict[str, Any]]
    instructions: str
    servings: int
    category: str  # "baking", "cooking", "dessert", "savory"
    complexity: str  # "simple", "medium", "complex"

# 10 Diverse Test Recipes
TEST_RECIPES = [
    TestRecipe(
        name="Chocolate Chip Cookies",
        ingredients=[
            {"name": "AP flour", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "sugar", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "brown sugar", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "butter", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "eggs", "amount": "2 large", "unit": "large", "quantity": 2.0},
            {"name": "vanilla extract", "amount": "2 tsp", "unit": "tsp", "quantity": 2.0},
            {"name": "baking soda", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "salt", "amount": "1/2 tsp", "unit": "tsp", "quantity": 0.5},
            {"name": "chocolate chips", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
        ],
        instructions="Mix dry ingredients. Cream butter and sugars. Add eggs and vanilla. Combine wet and dry ingredients. Fold in chocolate chips. Bake at 375°F for 9-11 minutes.",
        servings=24,
        category="baking",
        complexity="simple"
    ),
    
    TestRecipe(
        name="Beef Stir Fry",
        ingredients=[
            {"name": "beef sirloin", "amount": "1 lb", "unit": "lb", "quantity": 1.0},
            {"name": "soy sauce", "amount": "3 tbsp", "unit": "tbsp", "quantity": 3.0},
            {"name": "garlic", "amount": "3 cloves", "unit": "cloves", "quantity": 3.0},
            {"name": "ginger", "amount": "1 tbsp", "unit": "tbsp", "quantity": 1.0},
            {"name": "onion", "amount": "1 medium", "unit": "medium", "quantity": 1.0},
            {"name": "bell peppers", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "broccoli", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "vegetable oil", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "rice", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
        ],
        instructions="Marinate beef in soy sauce, garlic, and ginger. Heat oil in wok. Stir-fry beef until browned. Add vegetables and cook until tender. Serve over rice.",
        servings=4,
        category="cooking",
        complexity="medium"
    ),
    
    TestRecipe(
        name="Caesar Salad",
        ingredients=[
            {"name": "romaine lettuce", "amount": "1 head", "unit": "head", "quantity": 1.0},
            {"name": "parmesan cheese", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "croutons", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "anchovies", "amount": "6 fillets", "unit": "fillets", "quantity": 6.0},
            {"name": "garlic", "amount": "2 cloves", "unit": "cloves", "quantity": 2.0},
            {"name": "lemon juice", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "olive oil", "amount": "1/4 cup", "unit": "cup", "quantity": 0.25},
            {"name": "egg yolk", "amount": "1 large", "unit": "large", "quantity": 1.0},
            {"name": "worcestershire sauce", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
        ],
        instructions="Wash and chop lettuce. Make dressing with anchovies, garlic, lemon juice, olive oil, egg yolk, and Worcestershire sauce. Toss lettuce with dressing, cheese, and croutons.",
        servings=4,
        category="cooking",
        complexity="medium"
    ),
    
    TestRecipe(
        name="Banana Bread",
        ingredients=[
            {"name": "ripe bananas", "amount": "3 medium", "unit": "medium", "quantity": 3.0},
            {"name": "AP flour", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "sugar", "amount": "3/4 cup", "unit": "cup", "quantity": 0.75},
            {"name": "butter", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "eggs", "amount": "2 large", "unit": "large", "quantity": 2.0},
            {"name": "baking soda", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "salt", "amount": "1/2 tsp", "unit": "tsp", "quantity": 0.5},
            {"name": "vanilla extract", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "walnuts", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
        ],
        instructions="Mash bananas. Cream butter and sugar. Add eggs and vanilla. Mix in dry ingredients. Fold in bananas and walnuts. Bake at 350°F for 60-65 minutes.",
        servings=8,
        category="baking",
        complexity="simple"
    ),
    
    TestRecipe(
        name="Chicken Curry",
        ingredients=[
            {"name": "chicken thighs", "amount": "2 lbs", "unit": "lbs", "quantity": 2.0},
            {"name": "coconut milk", "amount": "1 can", "unit": "can", "quantity": 1.0},
            {"name": "curry powder", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "onion", "amount": "1 large", "unit": "large", "quantity": 1.0},
            {"name": "garlic", "amount": "4 cloves", "unit": "cloves", "quantity": 4.0},
            {"name": "ginger", "amount": "1 tbsp", "unit": "tbsp", "quantity": 1.0},
            {"name": "tomatoes", "amount": "2 medium", "unit": "medium", "quantity": 2.0},
            {"name": "vegetable oil", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "basmati rice", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
        ],
        instructions="Heat oil and sauté onions, garlic, and ginger. Add curry powder and cook until fragrant. Add chicken and brown. Add tomatoes and coconut milk. Simmer 30 minutes. Serve over rice.",
        servings=6,
        category="cooking",
        complexity="medium"
    ),
    
    TestRecipe(
        name="Pancakes",
        ingredients=[
            {"name": "AP flour", "amount": "1 1/2 cups", "unit": "cups", "quantity": 1.5},
            {"name": "sugar", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "baking powder", "amount": "2 tsp", "unit": "tsp", "quantity": 2.0},
            {"name": "salt", "amount": "1/2 tsp", "unit": "tsp", "quantity": 0.5},
            {"name": "milk", "amount": "1 1/4 cups", "unit": "cups", "quantity": 1.25},
            {"name": "eggs", "amount": "1 large", "unit": "large", "quantity": 1.0},
            {"name": "butter", "amount": "3 tbsp", "unit": "tbsp", "quantity": 3.0},
            {"name": "vanilla extract", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
        ],
        instructions="Mix dry ingredients. Whisk wet ingredients. Combine wet and dry ingredients. Cook on griddle until bubbles form. Flip and cook until golden.",
        servings=4,
        category="baking",
        complexity="simple"
    ),
    
    TestRecipe(
        name="Quinoa Buddha Bowl",
        ingredients=[
            {"name": "quinoa", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "chickpeas", "amount": "1 can", "unit": "can", "quantity": 1.0},
            {"name": "sweet potato", "amount": "2 medium", "unit": "medium", "quantity": 2.0},
            {"name": "kale", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "avocado", "amount": "1 large", "unit": "large", "quantity": 1.0},
            {"name": "tahini", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "lemon juice", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
            {"name": "olive oil", "amount": "1 tbsp", "unit": "tbsp", "quantity": 1.0},
            {"name": "pumpkin seeds", "amount": "1/4 cup", "unit": "cup", "quantity": 0.25},
        ],
        instructions="Cook quinoa. Roast sweet potatoes. Massage kale with lemon. Make tahini dressing. Combine all ingredients in bowls. Top with avocado and seeds.",
        servings=4,
        category="cooking",
        complexity="medium"
    ),
    
    TestRecipe(
        name="Chocolate Cake",
        ingredients=[
            {"name": "AP flour", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "sugar", "amount": "2 cups", "unit": "cups", "quantity": 2.0},
            {"name": "cocoa powder", "amount": "3/4 cup", "unit": "cup", "quantity": 0.75},
            {"name": "baking powder", "amount": "2 tsp", "unit": "tsp", "quantity": 2.0},
            {"name": "baking soda", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "salt", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "eggs", "amount": "2 large", "unit": "large", "quantity": 2.0},
            {"name": "milk", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "vegetable oil", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "vanilla extract", "amount": "2 tsp", "unit": "tsp", "quantity": 2.0},
        ],
        instructions="Mix dry ingredients. Whisk wet ingredients. Combine wet and dry ingredients. Pour into greased pans. Bake at 350°F for 30-35 minutes. Cool and frost.",
        servings=12,
        category="baking",
        complexity="medium"
    ),
    
    TestRecipe(
        name="Pasta Carbonara",
        ingredients=[
            {"name": "spaghetti", "amount": "1 lb", "unit": "lb", "quantity": 1.0},
            {"name": "pancetta", "amount": "6 oz", "unit": "oz", "quantity": 6.0},
            {"name": "eggs", "amount": "4 large", "unit": "large", "quantity": 4.0},
            {"name": "parmesan cheese", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "garlic", "amount": "2 cloves", "unit": "cloves", "quantity": 2.0},
            {"name": "black pepper", "amount": "1 tsp", "unit": "tsp", "quantity": 1.0},
            {"name": "olive oil", "amount": "2 tbsp", "unit": "tbsp", "quantity": 2.0},
        ],
        instructions="Cook pasta. Fry pancetta until crispy. Whisk eggs with cheese and pepper. Toss hot pasta with pancetta. Remove from heat and add egg mixture. Toss quickly to create creamy sauce.",
        servings=4,
        category="cooking",
        complexity="medium"
    ),
    
    TestRecipe(
        name="Smoothie Bowl",
        ingredients=[
            {"name": "frozen bananas", "amount": "2 medium", "unit": "medium", "quantity": 2.0},
            {"name": "frozen berries", "amount": "1 cup", "unit": "cup", "quantity": 1.0},
            {"name": "almond milk", "amount": "1/2 cup", "unit": "cup", "quantity": 0.5},
            {"name": "honey", "amount": "1 tbsp", "unit": "tbsp", "quantity": 1.0},
            {"name": "vanilla extract", "amount": "1/2 tsp", "unit": "tsp", "quantity": 0.5},
            {"name": "granola", "amount": "1/4 cup", "unit": "cup", "quantity": 0.25},
            {"name": "chia seeds", "amount": "1 tbsp", "unit": "tbsp", "quantity": 1.0},
            {"name": "coconut flakes", "amount": "1 tbsp", "unit": "tbsp", "quantity": 1.0},
        ],
        instructions="Blend frozen bananas, berries, almond milk, honey, and vanilla until smooth. Pour into bowl. Top with granola, chia seeds, and coconut flakes.",
        servings=1,
        category="dessert",
        complexity="simple"
    ),
]

# Test Diet Combinations
SIMPLE_DIETS = [
    ["vegan"],
    ["gluten-free"],
    ["dairy-free"],
    ["keto"],
    ["paleo"]
]

COMPLEX_DIETS = [
    ["vegan", "gluten-free"],
    ["dairy-free", "nut-free"],
    ["keto", "dairy-free"],
    ["paleo", "soy-free"],
    ["vegan", "gluten-free", "nut-free"],
    ["dairy-free", "gluten-free", "soy-free"]
]

ALL_DIET_COMBINATIONS = SIMPLE_DIETS + COMPLEX_DIETS

def get_test_recipes():
    """Get all test recipes."""
    return TEST_RECIPES

def get_diet_combinations():
    """Get all diet combinations for testing."""
    return ALL_DIET_COMBINATIONS

def get_simple_diets():
    """Get simple single-diet combinations."""
    return SIMPLE_DIETS

def get_complex_diets():
    """Get complex multi-diet combinations."""
    return COMPLEX_DIETS
