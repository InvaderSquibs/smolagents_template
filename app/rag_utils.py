#!/usr/bin/env python3
"""
RAG utilities for optional retrieval-augmented generation.
Provides modular RAG functionality that can be enabled/disabled via environment variables.
"""

import os
from typing import List, Optional, Tuple
from smolagents import Tool

def is_rag_enabled() -> bool:
    """Check if RAG functionality is enabled via environment variable."""
    return os.getenv("RAG_ENABLED", "false").lower() == "true"

def get_rag_tools() -> Tuple[List[Tool], Optional[object]]:
    """
    Get RAG tools if enabled, otherwise return empty list.
    
    Returns:
        Tuple of (tools_list, embedder_instance)
        - tools_list: List of tools (retriever + calculator if RAG enabled, empty if disabled)
        - embedder_instance: Embedder instance if RAG enabled, None if disabled
    """
    if not is_rag_enabled():
        return [], None
    
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb
        from chromadb.config import Settings
        from app.tools.retriever_tool import RetrieverTool
        from app.tools.calculator_tool import CalculatorTool
        
        # Load Chroma collection
        chroma_dir = os.getenv("CHROMA_DIR", "./chroma_db")
        client = chromadb.PersistentClient(path=chroma_dir)
        collection = client.get_collection("knowledge_base")
        
        # Load embedder
        embedder_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        embedder = SentenceTransformer(embedder_name)
        
        # Create tools
        retriever = RetrieverTool(collection=collection, embedder=embedder)
        calculator = CalculatorTool()
        
        print("✅ RAG enabled - using retriever + calculator tools")
        return [retriever, calculator], embedder
        
    except Exception as e:
        print(f"⚠️  RAG initialization failed: {e}")
        print("💡 Falling back to calculator-only mode")
        return [], None

def get_calculator_only_tools() -> List[Tool]:
    """Get calculator-only tools (fallback when RAG is disabled or fails)."""
    try:
        from app.tools.calculator_tool import CalculatorTool
        calculator = CalculatorTool()
        print("✅ Calculator-only mode - using safe calculator tool")
        return [calculator]
    except ImportError:
        # Fallback to original unsafe calculator if new one not available
        from src.code_agent_gemini_demo import Calculator
        calculator = Calculator()
        print("⚠️  Using original calculator (less safe)")
        return [calculator]

def get_agent_instructions() -> str:
    """Get appropriate instructions based on RAG status."""
    if is_rag_enabled():
        return (
            "You are a helpful mathematical assistant with access to a knowledge base and calculator. "
            "IMPORTANT: You MUST follow this exact workflow for EVERY mathematical question:\n\n"
            "1. FIRST: ALWAYS use the 'retriever' tool to search for relevant formulas, concepts, or context "
            "   when the user asks about mathematical topics, formulas, or calculations.\n"
            "2. THEN: Use the 'calculator' tool to perform any necessary numerical calculations.\n"
            "3. FINALLY: Provide a comprehensive answer that combines the retrieved knowledge with "
            "   the calculated results.\n\n"
            "NEVER skip the retriever step. Even if you know the formula, always retrieve it first "
            "to provide educational context and ensure accuracy. The retriever tool helps you give "
            "complete explanations with proper formulas."
        )
    else:
        return (
            "You are a helpful mathematical assistant with access to a calculator tool. "
            "Use the calculator tool to perform mathematical calculations and provide clear, "
            "step-by-step explanations of your work."
        )

def check_rag_requirements() -> bool:
    """Check if RAG requirements are met (vector store exists, etc.)."""
    if not is_rag_enabled():
        return True  # RAG not enabled, so requirements are "met"
    
    chroma_dir = os.getenv("CHROMA_DIR", "./chroma_db")
    if not os.path.exists(chroma_dir):
        print(f"❌ RAG enabled but Chroma database not found at {chroma_dir}")
        print("💡 Run 'python3 scripts/build_vector_store.py' to create the knowledge base")
        return False
    
    try:
        import chromadb
        client = chromadb.PersistentClient(path=chroma_dir)
        collections = client.list_collections()
        if not any(c.name == "knowledge_base" for c in collections):
            print("❌ RAG enabled but 'knowledge_base' collection not found")
            print("💡 Run 'python3 scripts/build_vector_store.py' to create the knowledge base")
            return False
        return True
    except Exception as e:
        print(f"❌ RAG enabled but Chroma database error: {e}")
        return False
