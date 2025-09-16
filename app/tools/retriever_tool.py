#!/usr/bin/env python3
"""
Retriever tool for SmolAgents that queries the Chroma vector store.
Retrieves relevant knowledge chunks based on user queries.
"""

from smolagents import Tool

class RetrieverTool(Tool):
    name = "retriever"
    description = (
        "Retrieve the most relevant knowledge chunks for a user query "
        "from the local Chroma vector store. Use this BEFORE answering if the "
        "query might require factual knowledge, formulas, or mathematical concepts."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Natural-language query to search the knowledge base."
        },
        "top_k": {
            "type": "integer",
            "description": "Number of results to return (default 4).",
            "optional": True,
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self, collection, embedder):
        super().__init__()
        self.collection = collection      # Chroma collection
        self.embedder = embedder          # SentenceTransformer instance

    def forward(self, query: str, top_k: int = 4) -> str:
        """
        Retrieve relevant knowledge chunks for the given query.
        
        Args:
            query: Natural language query to search for
            top_k: Number of results to return
            
        Returns:
            Formatted string with retrieved knowledge chunks
        """
        try:
            # Embed the query using the SAME embedder used for the index
            qvec = self.embedder.encode([query], convert_to_numpy=True)
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=qvec, 
                n_results=top_k
            )
            
            # Format results as a readable string
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            
            if not docs:
                return "[RAG] No relevant knowledge found for this query."
            
            lines = ["[RAG] Retrieved knowledge:"]
            for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), start=1):
                title = (meta or {}).get("title", "")
                prefix = f"{i}. {title}: " if title else f"{i}. "
                # Include relevance score (lower distance = more relevant)
                relevance = f" (relevance: {1-dist:.2f})" if dist is not None else ""
                lines.append(prefix + doc + relevance)
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"[RAG] Error retrieving knowledge: {str(e)}"
