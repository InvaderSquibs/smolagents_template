# Recipe Transformation Agent

An intelligent recipe transformation system that uses LLM-powered agents (Gemini) to automatically adapt recipes to meet specific dietary restrictions while maintaining flavor and cooking properties.

## 🎯 What This System Does

This system takes any recipe and intelligently transforms it to meet dietary requirements like:
- **Vegan** - Replaces animal products with plant-based alternatives
- **Gluten-Free** - Substitutes wheat flour with gluten-free options
- **Keto** - Replaces high-carb ingredients with low-carb alternatives
- **Nut-Free** - Avoids all tree nuts and peanuts
- **Dairy-Free** - Eliminates milk, cheese, and other dairy products
- **And more...**

The system uses **LLM-guided contextual decision making** to select the most appropriate substitutions based on recipe type, cooking method, and flavor profile.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd ut-cs6300-assignment-01

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.template .env
# Edit .env and add your GEMINI_API_KEY
```

### Basic Usage

Transform a recipe with dietary restrictions:

```bash
# Transform a recipe to be vegan (requires Gemini API key)
python3 src/recipe_agent_cli.py --recipe demos/demo_cake.txt --diets vegan

# Transform with multiple restrictions
python3 src/recipe_agent_cli.py --recipe demos/demo_cake.txt --diets vegan gluten-free

# Use a sample recipe
python3 src/recipe_agent_cli.py --sample --diets keto

# Test without API calls (mock mode)
python3 src/test_recipe_agent.py
```

## 📁 Project Structure

```
├── src/                          # Core system modules
│   ├── recipe_agent_cli.py       # Main CLI interface
│   ├── recipe_agent.py           # LLM-powered transformation agent
│   ├── llm_substitution_engine.py # Core substitution logic
│   ├── restriction_knowledge.py  # Dietary restriction database
│   ├── ingredient_canonicalizer.py # Ingredient name normalization
│   ├── recipe_agent_tool.py      # Tool wrapper for smolagents
│   └── test_recipe_agent.py      # Testing utility (mock mode)
├── demos/                        # Demo recipes and outputs
│   ├── demo_cake.txt            # Chocolate layer cake
│   ├── demo_pancakes.txt        # Fluffy buttermilk pancakes
│   ├── demo_pasta.txt           # Classic pasta recipe
│   └── ...                      # More demo recipes
├── testing/                      # Test suites
├── env.template                  # Environment variables template
└── requirements.txt              # Python dependencies
```

## 🛠️ System Architecture

### Core Components

1. **Recipe Agent CLI** (`recipe_agent_cli.py`)
   - Parses plain text recipes with complex measurements
   - Handles command-line interface
   - Manages recipe input/output formatting

2. **LLM Transformation Agent** (`recipe_agent.py`)
   - Uses Gemini API for intelligent decision making
   - Contains 3 specialized tools:
     - `RecipeAnalysisTool` - Analyzes recipe context (type, cooking method, flavor)
     - `IngredientSubstitutionTool` - Gets substitution options
     - `SubstitutionDecisionTool` - Makes contextual substitution decisions

3. **Substitution Engine** (`llm_substitution_engine.py`)
   - Manages LLM-guided substitutions
   - Processes recipe ingredients
   - Provides structured substitution options

4. **Knowledge Base** (`restriction_knowledge.py`)
   - Comprehensive dietary restriction database
   - Manages substitution options with ratios and cooking notes
   - Handles multi-diet conflict resolution

5. **Ingredient Canonicalizer** (`ingredient_canonicalizer.py`)
   - Normalizes ingredient names (e.g., "AP flour" → "all-purpose flour")
   - Handles aliases and variations
   - Ensures consistent lookups across the system

6. **Agent Tool Wrapper** (`recipe_agent_tool.py`)
   - Exposes recipe transformation as a typed tool
   - For integration with other AI agents using smolagents

7. **Testing Utility** (`test_recipe_agent.py`)
   - Mock mode for testing without API calls
   - Validates core functionality
   - Useful for development and debugging

## 🧪 Test Commands

### With LLM Agent (requires API key)
```bash
# Vegan chocolate cake
python3 src/recipe_agent_cli.py --recipe demos/demo_cake.txt --diets vegan

# Gluten-free pancakes
python3 src/recipe_agent_cli.py --recipe demos/demo_pancakes.txt --diets gluten-free

# Multi-diet transformation
python3 src/recipe_agent_cli.py --recipe demos/demo_cake.txt --diets vegan gluten-free
```

### Without API calls (mock mode)
```bash
# Test core functionality
python3 src/test_recipe_agent.py
```

## 🔧 How It Works

### 1. Recipe Parsing
- Accepts plain text (.txt) recipe formats
- Automatically parses ingredients, amounts, units, and instructions
- Handles complex measurements like "2 1/4 cups" and fractions
- Supports section headers like "For Frosting:"

### 2. Ingredient Canonicalization
- Normalizes ingredient names (e.g., "AP flour" → "all-purpose flour")
- Handles aliases and variations
- Ensures consistent lookup across the knowledge base

### 3. Recipe Context Analysis
- LLM analyzes recipe type (baking, stovetop, raw)
- Determines cooking method and flavor profile
- Provides context for intelligent substitution decisions

### 4. Dietary Restriction Analysis
- Checks each ingredient against specified dietary restrictions
- Identifies forbidden ingredients that need substitution
- Maintains comprehensive database of dietary rules

### 5. LLM-Guided Substitution
- LLM selects contextually appropriate substitutions
- Considers recipe type, cooking method, and flavor profile
- Maintains proper cooking ratios and provides cooking notes
- Provides confidence scores and reasoning for decisions

### 6. Output Generation
- Creates detailed transformation reports
- Documents all substitutions with reasoning
- Includes cooking tips and confidence scores
- Saves results in JSON format

## 📊 Supported Dietary Restrictions

| Diet | Description | Key Substitutions |
|------|-------------|-------------------|
| **Vegan** | No animal products | Eggs → flax eggs, milk → plant milk, butter → coconut oil |
| **Gluten-Free** | No wheat/gluten | Flour → almond/coconut/GF blend |
| **Keto** | Low-carb, high-fat | Sugar → erythritol, flour → almond flour |
| **Nut-Free** | No tree nuts/peanuts | Almond flour → sunflower seed flour |
| **Dairy-Free** | No milk products | Milk → oat milk, butter → coconut oil |
| **Paleo** | Ancient diet | Grains → nuts/seeds, sugar → honey |
| **Soy-Free** | No soy products | Soy sauce → coconut aminos |
| **Egg-Free** | No eggs | Eggs → flax eggs, applesauce |

## 🎯 Example Output

When you run:
```bash
python3 src/recipe_agent_cli.py --recipe demos/demo_cake.txt --diets vegan
```

You get detailed transformation results:

```
🤖 LLM Agent Recipe Transformation Results
============================================================
📝 Recipe: Chocolate Layer Cake
📋 Dietary Restrictions: vegan
👥 Servings: 12

🔍 Recipe Analysis:
   Type: baking
   Cooking Method: baking
   Flavor Profile: sweet

🔄 LLM-Guided Substitutions (3):
   1. eggs → flax egg
      🤖 Reasoning: Selected flax egg based on recipe context and confidence score
      📊 Confidence: 1.00
      💡 Notes: Mix and let sit 5 minutes. Good for binding.

   2. milk → oat milk
      🤖 Reasoning: Selected oat milk based on recipe context and confidence score
      📊 Confidence: 1.00
      💡 Notes: Creamy texture, neutral flavor. Good for coffee and baking.

   3. butter, softened → coconut oil
      🤖 Reasoning: Selected coconut oil based on recipe context and confidence score
      📊 Confidence: 1.00
      💡 Notes: Solid at room temperature. Good for baking.

✅ Unchanged Ingredients (13):
   • 2 1/4 all-purpose flour
   • 2 granulated sugar
   • 3/4 unsweetened cocoa powder
   [... and more]

🤖 Agent Summary: LLM agent made contextual substitution decisions based on recipe analysis
💾 Agent results saved to: chocolate_layer_cake_agent_transformed_vegan.json
```

## 🧪 Testing

### Run Mock Tests (no API required)
```bash
python3 src/test_recipe_agent.py
```

### Run Full Test Suite
```bash
cd testing
python3 comprehensive_test_runner.py
```

## 🔑 API Configuration

The system requires a Gemini API key for LLM-powered transformations:

1. Get your API key from [Google AI Studio](https://aistudio.google.com/)
2. Set it in your environment:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
3. Or add it to your `.env` file

**Note**: The free tier has a 50 requests/day limit. For production use, consider upgrading to a paid plan.

## 🤝 Contributing

This system is designed to be extensible. You can:
- Add new dietary restrictions in `src/restriction_knowledge.py`
- Improve ingredient canonicalization in `src/ingredient_canonicalizer.py`
- Enhance LLM prompts in `src/recipe_agent.py`
- Add new recipe formats in `src/recipe_agent_cli.py`

## 📝 License

See LICENSE file for details.

## 🎯 Quick Test

Try this command to see the system in action:

```bash
# Test with mock mode (no API required)
python3 src/test_recipe_agent.py

# Or with real LLM (requires API key)
python3 src/recipe_agent_cli.py --recipe demos/demo_cake.txt --diets vegan
```

This will transform a chocolate cake to be vegan, showing you how the LLM agent makes intelligent contextual substitution decisions!