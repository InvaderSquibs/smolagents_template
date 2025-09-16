#!/usr/bin/env python3

import os
from smolagents import CodeAgent, Tool
from smolagents import OpenAIServerModel

# Phoenix telemetry imports
try:
    import phoenix as px
    from phoenix.trace import using_project
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.openai import OpenAIInstrumentor
    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False


# Define a simple calculator tool
class Calculator(Tool):
    name: str = "calculator"
    description: str = (
        "Computes the results of a mathematical expression."
        "The expression must be made in Python syntax."
    )
    inputs: dict = {
        "expression": {
            "type": "string",
            "description": "The Python expression to evaluate."
        }
    }
    output_type: dict = "string"

    def forward(self, expression: str) -> str:
        """
        Evaluates the mathematical python expression and returns the result.

        Args:
            expression: The python mathematical expression.

        Returns:
            The numerical result of evaluating the expression.
        """
        return str(eval(expression))


def initialize_phoenix():
    """Initialize Phoenix telemetry if enabled."""
    if not PHOENIX_AVAILABLE:
        return False
        
    phoenix_enabled = os.getenv("PHOENIX_ENABLED", "false").lower() == "true"
    if not phoenix_enabled:
        return False
        
    try:
        # Get Phoenix configuration from environment
        phoenix_endpoint = os.getenv("PHOENIX_ENDPOINT", "http://localhost:6006")
        phoenix_project = os.getenv("PHOENIX_PROJECT_NAME", "calculator-agent")
        
        # Set up OpenTelemetry tracing with project name in attributes
        from opentelemetry.sdk.resources import Resource
        resource = Resource.create({
            "service.name": phoenix_project,
            "service.version": "1.0.0",
            "phoenix.project.name": phoenix_project
        })
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer = trace.get_tracer(__name__)
        
        # Create OTLP exporter for Phoenix
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{phoenix_endpoint}/v1/traces",
            headers={}
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument OpenAI
        OpenAIInstrumentor().instrument()
        
        print(f"🔍 Phoenix telemetry enabled - sending traces to {phoenix_endpoint}")
        print(f"📊 Project name: {phoenix_project}")
        return True
        
    except Exception as e:
        print(f"⚠️  Phoenix telemetry initialization failed: {e}")
        return False


def main():
    """Main function to run the calculator agent."""
    # Load environment variables
    import dotenv
    dotenv.load_dotenv()
    
    # Initialize Phoenix telemetry if enabled
    phoenix_enabled = initialize_phoenix()
    
    # Initialize calculator tool
    calculator_tool = Calculator()
    tools = [calculator_tool]
    additional_authorized_imports = []
    
    # Get model configuration from environment
    model_id = os.getenv("MODEL_ID", os.getenv("MODEL_NAME", "qwen/qwen3-4b-2507"))
    api_key = os.getenv("OPENAI_API_KEY", os.getenv("GEMINI_API_KEY"))
    api_base = os.getenv("GPT_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/openai/")
    
    print(f"🔧 Using model: {model_id}")
    print(f"🔧 Using endpoint: {api_base}")
    
    # Initialize model
    model = OpenAIServerModel(
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
    )
    
    # Initialize agent
    agent = CodeAgent(
        tools=tools,
        model=model,
        additional_authorized_imports=additional_authorized_imports,
        max_steps=3
    )
    
    # Run calculation with Phoenix project context
    print("🧮 Calculator Agent Demo")
    print("=" * 30)
    
    # Get project name for Phoenix
    phoenix_project = os.getenv("PHOENIX_PROJECT_NAME", "calculator-agent")
    
    # Use Phoenix project context
    if phoenix_enabled and PHOENIX_AVAILABLE:
        with using_project(phoenix_project):
            answer = agent.run("What is 23 times 17 minus 42?")
    else:
        answer = agent.run("What is 23 times 17 minus 42?")
    
    print(f"Agent returned answer: {answer}")


if __name__ == "__main__":
    main()
