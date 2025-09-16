#!/usr/bin/env python3
"""
Main RAG-enhanced calculator agent.
Combines retrieval-augmented generation with mathematical calculation capabilities.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from smolagents import CodeAgent, OpenAIServerModel

from app.tools.retriever_tool import RetrieverTool
from app.tools.calculator_tool import CalculatorTool

# Phoenix telemetry imports (from original demo)
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
        phoenix_project = os.getenv("PHOENIX_PROJECT_NAME", "rag-calculator-agent")
        
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

def build_agent():
    """Build the calculator agent with optional RAG."""
    print("🔧 Building Calculator Agent...")
    
    # Use the modular RAG utilities
    try:
        from app.rag_utils import get_rag_tools, get_calculator_only_tools, check_rag_requirements, get_agent_instructions
        
        if check_rag_requirements():
            tools, embedder = get_rag_tools()
            if not tools:  # RAG failed, fallback to calculator only
                tools = get_calculator_only_tools()
        else:
            print("🔄 Falling back to calculator-only mode")
            tools = get_calculator_only_tools()
            
        instructions = get_agent_instructions()
        
    except ImportError:
        # Fallback if RAG utils not available
        print("🔄 RAG utilities not available, using calculator-only mode")
        from app.tools.calculator_tool import CalculatorTool
        calculator = CalculatorTool()
        tools = [calculator]
        instructions = "You are a helpful mathematical assistant. Use the calculator tool to perform calculations."

    # Create LLM for the agent
    model_id = os.getenv("MODEL_ID", os.getenv("MODEL_NAME", "qwen/qwen3-4b-2507"))
    api_key = os.getenv("OPENAI_API_KEY", os.getenv("GEMINI_API_KEY"))
    api_base = os.getenv("GPT_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/openai/")
    
    print(f"🤖 Using model: {model_id}")
    print(f"🌐 Using endpoint: {api_base}")
    
    model = OpenAIServerModel(
        model_id=model_id,
        api_base=api_base,
        api_key=api_key,
    )

    # Create agent
    agent = CodeAgent(
        tools=tools,
        model=model,
        max_steps=8 if len(tools) > 1 else 3,  # More steps if RAG enabled
        verbosity_level=2,
        name="CalculatorAgent",
        instructions=instructions
    )
    
    print("✅ Calculator Agent built successfully!")
    return agent

def demo():
    """Run demo queries to showcase the Calculator functionality."""
    # Initialize Phoenix telemetry if enabled
    phoenix_enabled = initialize_phoenix()
    
    # Build the agent
    agent = build_agent()
    
    # Get project name for Phoenix
    phoenix_project = os.getenv("PHOENIX_PROJECT_NAME", "calculator-agent")
    
    print("\n" + "="*60)
    print("🧮 Calculator Agent Demo")
    print("="*60)
    
    # Example queries
    demo_queries = [
        "What is 15 * 23 + 42?",
        "What's the area of a circle with radius 7?",
        "If I have a right triangle with legs 3 and 4, what's the hypotenuse?",
        "Convert 25 degrees Celsius to Fahrenheit",
        "What's the kinetic energy of a 2kg object moving at 5 m/s?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*20} Query {i} {'='*20}")
        print(f"USER: {query}")
        print("-" * 50)
        
        # Use Phoenix project context if enabled
        if phoenix_enabled and PHOENIX_AVAILABLE:
            with using_project(phoenix_project):
                answer = agent.run(query)
        else:
            answer = agent.run(query)
        
        print(f"AGENT: {answer}")
        print("-" * 50)

def interactive_mode():
    """Run the agent in interactive mode."""
    # Initialize Phoenix telemetry if enabled
    phoenix_enabled = initialize_phoenix()
    
    # Build the agent
    agent = build_agent()
    
    # Get project name for Phoenix
    phoenix_project = os.getenv("PHOENIX_PROJECT_NAME", "rag-calculator-agent")
    
    print("\n" + "="*60)
    print("🧮 RAG Calculator Agent - Interactive Mode")
    print("="*60)
    print("Ask me mathematical questions! I'll retrieve relevant formulas and calculate answers.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
                
            print("-" * 50)
            
            # Use Phoenix project context if enabled
            if phoenix_enabled and PHOENIX_AVAILABLE:
                with using_project(phoenix_project):
                    answer = agent.run(query)
            else:
                answer = agent.run(query)
            
            print(f"Agent: {answer}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="RAG Calculator Agent")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo",
                       help="Run mode: demo (predefined queries) or interactive (user input)")
    parser.add_argument("query", nargs="?", help="Single query to process (overrides mode)")
    
    args = parser.parse_args()
    
    # If a query is provided as argument, process it directly
    if args.query:
        # Initialize Phoenix telemetry if enabled
        phoenix_enabled = initialize_phoenix()
        
        # Build the agent
        agent = build_agent()
        
        # Get project name for Phoenix
        phoenix_project = os.getenv("PHOENIX_PROJECT_NAME", "rag-calculator-agent")
        
        print(f"\n🔍 Query: {args.query}")
        print("-" * 60)
        
        # Use Phoenix project context if enabled
        if phoenix_enabled and PHOENIX_AVAILABLE:
            with using_project(phoenix_project):
                answer = agent.run(args.query)
        else:
            answer = agent.run(args.query)
        
        print(f"\n💡 Answer: {answer}")
        print("-" * 60)
    elif args.mode == "demo":
        demo()
    else:
        interactive_mode()
