# SmolAgents Calculator Template

A simple template demonstrating how to use smolagents with a calculator tool and Gemini API.

## 🎯 What This Template Does

This template provides a basic calculator agent that can:
- Perform mathematical calculations using Python expressions
- Use Gemini API for natural language processing
- Monitor LLM calls with Phoenix telemetry (optional)
- Be easily extended with additional tools

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
python3 src/code_agent_gemini_demo.py
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
   python3 src/code_agent_gemini_demo.py
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


