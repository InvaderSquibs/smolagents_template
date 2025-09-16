#!/usr/bin/env python3
"""
RAG Calculator Agent Demo - Simple command-line interface
Usage: python3 src/rag_calculator_demo.py "your question here"
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # If no arguments provided, show usage
    if len(sys.argv) < 2:
        print("🧮 Calculator Agent")
        print("=" * 40)
        print("Usage: python3 src/calculator_demo.py \"your question here\"")
        print("\nExamples:")
        print('  python3 src/calculator_demo.py "What is 15 * 23 + 42?"')
        print('  python3 src/calculator_demo.py "What is the area of a circle with radius 5?"')
        print('  python3 src/calculator_demo.py "Convert 25 Celsius to Fahrenheit"')
        print('  python3 src/calculator_demo.py "What is the volume of a cylinder 3 inches tall and 2 inches wide?"')
        print("\nFor demo mode: python3 src/calculator_demo.py --mode demo")
        print("For interactive mode: python3 src/calculator_demo.py --mode interactive")
        print("\n💡 RAG Features:")
        print("  - Set RAG_ENABLED=true in .env to enable formula retrieval")
        print("  - Run 'python3 scripts/build_vector_store.py' to build knowledge base")
        sys.exit(1)
    
    # Import and run the main agent
    import sys
    import subprocess
    
    # Build the command to run the main app with the query
    cmd = [sys.executable, str(project_root / "app" / "main.py")] + sys.argv[1:]
    subprocess.run(cmd)
