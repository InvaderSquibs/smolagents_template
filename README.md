# SmolAgents Calculator Template

A simple template demonstrating how to use smolagents with a calculator tool and Gemini API, with optional RAG (Retrieval-Augmented Generation) capabilities.

## 🎯 What This Template Does

This template provides a calculator agent that can:
- Perform mathematical calculations using Python expressions
- Use Gemini API for natural language processing
- **NEW**: Optional RAG functionality for educational mathematical assistance
- Monitor LLM calls with Phoenix telemetry (optional)
- Be easily extended with additional tools

## 🧠 RAG Features (Optional)

When RAG is enabled, the agent can:
- Retrieve relevant mathematical formulas and concepts from a knowledge base
- Provide educational context along with calculations
- Answer questions like "What's the area of a circle with radius 5?" with both the formula and the result
- Support 20+ mathematical domains: geometry, physics, conversions, finance, algebra, trigonometry, and statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))
- Virtual environment (recommended)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd smolagents_template

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

Run the calculator agent demo:

```bash
# Run the calculator agent
python3 src/calculator_demo.py

# Run with a custom query
python3 src/calculator_demo.py "What is 15 * 23 + 42?"

# Run with mathematical questions (RAG enabled automatically if configured)
python3 src/calculator_demo.py "What's the volume of a cylinder 3 inches tall and 2 inches wide?"
```

## 🧠 Setting Up RAG (Optional)

To enable RAG functionality for educational mathematical assistance:

### 1. Install RAG Dependencies
```bash
pip install sentence-transformers chromadb python-dotenv
```

### 2. Build the Knowledge Base
```bash
# Create the vector store from mathematical formulas
python3 scripts/build_vector_store.py
```

This will:
- Load 20 mathematical formulas from `data/knowledge.json`
- Create embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- Store them in a ChromaDB vector database at `./chroma_db`

### 3. Enable RAG in Environment
```bash
# Edit your .env file
RAG_ENABLED=true
```

### 4. Run with RAG
```bash
# The calculator demo automatically uses RAG when enabled
python3 src/calculator_demo.py "What's the area of a circle with radius 7?"
python3 src/calculator_demo.py "Convert 25 Celsius to Fahrenheit"
```

### RAG Configuration Options
```bash
# In your .env file
RAG_ENABLED=true                    # Enable/disable RAG
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Embedding model
CHROMA_DIR=./chroma_db             # Vector database location
```

## 🔍 Phoenix Telemetry & Monitoring

This template includes built-in support for [Phoenix](https://github.com/Arize-ai/phoenix) telemetry to monitor and analyze LLM calls, performance, and debugging.

### Setup Phoenix Monitoring

1. **Install Phoenix** (already included in requirements.txt):
   ```bash
   pip install phoenix
   ```

2. **Enable Phoenix in your environment**:
   ```bash
   # Edit your .env file
   PHOENIX_ENABLED=true
   PHOENIX_ENDPOINT=http://localhost:6006
   PHOENIX_PROJECT_NAME=calculator-agent
   ```

3. **Start Phoenix server** (in a separate terminal):
   ```bash
   phoenix serve
   ```

4. **Run your calculator agent** - it will automatically be tracked:
   ```bash
   python3 src/calculator_demo.py
   ```

5. **View telemetry data** at http://localhost:6006

### What Phoenix Tracks

- **LLM Calls**: All Gemini API requests and responses
- **Tool Usage**: Calculator tool executions
- **Performance Metrics**: Response times, token usage, costs
- **Error Tracking**: Failed requests and debugging information
- **Trace Visualization**: Complete request flows and agent reasoning

### Phoenix Dashboard Features

- **Traces**: See complete request flows from start to finish
- **Spans**: Individual LLM calls and tool executions
- **Metrics**: Performance, cost, and usage analytics
- **Debugging**: Detailed logs and error tracking
- **Filtering**: Search and filter by calculation type, etc.

### Disable Phoenix

To disable telemetry, set in your `.env` file:
```bash
PHOENIX_ENABLED=false
```

## ⚙️ Environment Variables Configuration

The template supports several environment variables for customization:

### Core Configuration
- `GEMINI_API_KEY` - Your Gemini API key (required)
- `MODEL_NAME` - LLM model to use (default: "gemini-2.5-flash")

### Phoenix Telemetry
- `PHOENIX_ENABLED` - Enable Phoenix monitoring (default: false)
- `PHOENIX_ENDPOINT` - Phoenix server endpoint (default: http://localhost:6006)
- `PHOENIX_PROJECT_NAME` - Project name for traces (default: calculator-agent)

### Output Configuration
- `OUTPUT_DIR` - Directory for output files (default: current directory)
- `VERBOSE_LOGGING` - Enable verbose logging (default: false)

### Example .env Configuration
```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional customizations
MODEL_NAME=gemini-2.5-flash
PHOENIX_ENABLED=true
PHOENIX_PROJECT_NAME=my-calculator-agent
VERBOSE_LOGGING=true
```

## 📝 Assignment Setup

Before starting your assignment, make sure to:

1. **Fill in the assignment document**:
   ```bash
   # Create and edit assignment.md with your specific requirements
   nano assignment.md
   ```

2. **Update environment variables** in `.env` based on your assignment needs

3. **Test the system** with the provided calculator demo

## 🛠️ Extending the Template

This template can be easily extended:

### Adding New Tools
```python
class NewTool(Tool):
    name: str = "new_tool"
    description: str = "Description of what this tool does"
    inputs: dict = {
        "input_param": {
            "type": "string",
            "description": "Description of the input parameter"
        }
    }
    output_type: dict = "string"
    
    def forward(self, input_param: str) -> str:
        # Your tool logic here
        return "result"
```

### Adding to Agent
```python
new_tool = NewTool()
tools = [calculator_tool, new_tool]  # Add your new tool
```

## 🔑 API Configuration

The system requires a Gemini API key for LLM-powered calculations:

1. Get your API key from [Google AI Studio](https://aistudio.google.com/)
2. Set it in your environment:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```
3. Or add it to your `.env` file

**Note**: The free tier has a 50 requests/day limit. For production use, consider upgrading to a paid plan.

## 🤝 Contributing

This template is designed to be extensible. You can:
- Add new tools in the Calculator class or create new tool classes
- Enhance the agent's capabilities
- Add new environment variables for configuration
- Improve error handling and logging

## 📝 License

See LICENSE file for details.


