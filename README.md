# Recipe Transformation System

An intelligent recipe transformation system that automatically adapts recipes to meet specific dietary restrictions while maintaining flavor and cooking properties.

## 🎯 What This System Does

This system takes any recipe and intelligently transforms it to meet dietary requirements like:
- **Vegan** - Replaces animal products with plant-based alternatives
- **Gluten-Free** - Substitutes wheat flour with gluten-free options
- **Keto** - Replaces high-carb ingredients with low-carb alternatives
- **Nut-Free** - Avoids all tree nuts and peanuts
- **Dairy-Free** - Eliminates milk, cheese, and other dairy products
- **And more...**

The system uses advanced ingredient canonicalization, unit conversion, and contextual substitution to ensure the transformed recipes are not only compliant but also maintain proper cooking ratios and flavors.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
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
```

### Basic Usage

Transform a recipe with dietary restrictions:

```bash
# Transform a recipe to be vegan
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan

# Transform with multiple restrictions
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan gluten-free

# Use a sample recipe
python3 src/recipe_transformer_cli.py --sample --diets keto
```

## 📁 Project Structure

```
├── src/                          # Core system modules
│   ├── recipe_transformer_cli.py # Main CLI interface
│   ├── ingredient_canonicalizer.py # Ingredient name normalization
│   ├── restriction_knowledge.py  # Dietary restriction database
│   ├── unit_aware_substitution.py # Smart substitution engine
│   ├── unit_converter.py         # Unit conversion system
│   ├── unified_substitution_system.py # Unified substitution logic
│   ├── composite_diet_engine.py  # Multi-diet conflict resolution
│   └── llm_substitution_engine.py # LLM-based substitution decisions
├── demos/                        # Demo recipes and outputs
│   ├── demo_cake.txt            # Chocolate layer cake
│   ├── demo_pancakes.txt        # Fluffy buttermilk pancakes
│   ├── demo_pasta.txt           # Classic pasta recipe
│   └── ...                      # More demo recipes
├── testing/                      # Test suites
└── requirements.txt              # Python dependencies
```

## 🧪 Test Commands

Here are some test commands to try the system:

### Single Diet Transformations
```bash
# Vegan chocolate cake
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan

# Gluten-free pancakes
python3 src/recipe_transformer_cli.py --recipe demos/demo_pancakes.txt --diets gluten-free

# Keto-friendly cake
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets keto
```

### Multi-Diet Transformations
```bash
# Vegan + Gluten-free cake
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan gluten-free

# Vegan + Keto + Nut-free (complex scenario)
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan keto nut-free
```

### Ingredient Analysis
```bash
# Check if an ingredient is forbidden in a diet
python3 src/recipe_transformer_cli.py --check-ingredient "all-purpose flour" --diet-for-ingredient "gluten-free"

# List all available diets
python3 src/recipe_transformer_cli.py --list-diets
```

## 🔧 How It Works

### 1. Recipe Parsing
- Accepts both plain text (.txt) and JSON recipe formats
- Automatically parses ingredients, amounts, units, and instructions
- Handles complex measurements like "2 1/4 cups" and fractions

### 2. Ingredient Canonicalization
- Normalizes ingredient names (e.g., "AP flour" → "flour")
- Handles aliases and variations
- Ensures consistent lookup across the knowledge base

### 3. Dietary Restriction Analysis
- Checks each ingredient against the specified dietary restrictions
- Identifies forbidden ingredients that need substitution
- Maintains a comprehensive database of dietary rules

### 4. Intelligent Substitution
- Selects contextually appropriate substitutions
- Maintains proper cooking ratios and unit conversions
- Provides helpful cooking notes for each substitution

### 5. Output Generation
- Creates clean, cookable recipe text files
- Documents all substitutions made
- Includes cooking tips and warnings

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
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan
```

You get a clean, cookable recipe like:

```
Chocolate Layer Cake (vegan)

Dietary Restrictions: vegan

Serves 12

Substitutions Made:
  1. eggs → flax egg
     Note: Mix and let sit 5 minutes. Good for binding.
  2. milk → oat milk
     Note: Creamy texture, neutral flavor. Good for coffee and baking.
  3. butter, softened → coconut oil
     Note: Solid at room temperature. Good for baking.

Ingredients:
• 2 1/4 cups all-purpose flour
• 2 cups granulated sugar
• 3/4 cup unsweetened cocoa powder
• 1 1/2 tsp baking powder
• 1 1/2 tsp baking soda
• 1 tsp salt
• 1/2 cup vegetable oil
• 2 tsp vanilla extract
• 1 cup boiling water
• 2/3 cup unsweetened cocoa powder
• 3 cups powdered sugar
• 1 tsp vanilla extract
• 2 large flax egg
• 1 cup oat milk
• 1/2 cup coconut oil
• 1/3 cup oat milk

Instructions:
1. Preheat oven to 350°F (175°C).
2. Grease and flour two 9-inch round cake pans.
[... full cooking instructions ...]
```

## 🧪 Testing

Run the test suite:
```bash
cd testing
python3 comprehensive_test_runner.py
```

## 🤝 Contributing

This system is designed to be extensible. You can:
- Add new dietary restrictions in `src/restriction_knowledge.py`
- Improve ingredient canonicalization in `src/ingredient_canonicalizer.py`
- Enhance substitution logic in `src/unit_aware_substitution.py`

## 📝 License

See LICENSE file for details.

## 🎯 Quick Test String

Try this command to see the system in action:

```bash
python3 src/recipe_transformer_cli.py --recipe demos/demo_cake.txt --diets vegan gluten-free
```

This will transform a chocolate cake to be both vegan and gluten-free, showing you how the system handles multiple overlapping dietary restrictions!