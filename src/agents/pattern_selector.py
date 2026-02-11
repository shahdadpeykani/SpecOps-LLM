"""
PatternSelector Agent.
Selects design patterns based on SRS and RAG knowledge (Vector DB).
"""
import json
import chromadb
# Add src to path if needed, usually handled by runtime
import sys
import os

from src.backend.llm_client import LLMClient

class PatternSelector:
    def __init__(self, db_path=None):
        if db_path is None:
            # Resolve to project_root/data/chroma_db
            self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/chroma_db'))
        else:
            self.db_path = db_path
        self.llm_client = LLMClient()
        try:
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_collection(name="design_patterns")
            print("PatternSelector: Connected to ChromaDB.")
        except Exception as e:
            print(f"PatternSelector Warning: Connection failed: {e}")
            self.collection = None

    def select_patterns(self, srs: dict) -> dict:
        """
        Selects patterns for the given SRS dictionary using Vector DB.
        Returns format: {"success": bool, "selected_patterns": list[str], "justification": str}
        """
        if not self.collection:
             return {"success": False, "error": "ChromaDB (Vector DB) is not connected. Cannot retrieve patterns."}

        # 1. Construct Query from SRS
        project_name = srs.get('project_name', 'Unnamed Project')
        description = srs.get('description', '')
        tech_stack = srs.get('tech_stack', [])
        
        query_text = f"Project: {project_name}. Description: {description}. Tech Stack: {tech_stack}"
        print(f"Selecting patterns for: {project_name}")

        # 2. Retrieve Context from ChromaDB
        retrieved_contexts = []
        try:
            # Get embedding for the query using LLMClient
            query_embedding = self.llm_client.get_embedding(query_text)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=3 # Get top 3 relevant chunks
            )
            
            if results['documents'] and results['metadatas']:
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i]
                    source = meta.get('source', 'Unknown')
                    retrieved_contexts.append(f"- Source: {source}\n  Content: {doc[:500]}...")
        except Exception as e:
            return {"success": False, "error": f"Vector DB Retrieval Error: {str(e)}"}
        
        if not retrieved_contexts:
             # Strict mode: If nothing found, warn or return empty? 
             # User implies strict connection, but maybe empty result is valid "no patterns".
             # However, "if chromadb is not found" refers to the connection usually.
             pass 

        context_str = "\n".join(retrieved_contexts) if retrieved_contexts else "No relevant patterns found in knowledge base."

        # 3. Ask LLM to Formulate Selection from Retrieved Context
        prompt = f"""
        You are a Senior Software Architect. We have retrieved the following relevant Design Pattern documentation from our Vector Knowledge Base based on the Project SRS.

        PROJECT SRS:
        {json.dumps(srs, indent=2)}

        RETRIEVED KNOWLEDGE (CONTEXT):
        {context_str}

        INSTRUCTIONS:
        1. Analyze the SRS and the RETRIEVED KNOWLEDGE.
        2. Formulate the final list of design patterns to be applied.
        3. The retrieved knowledge contains the most relevant patterns (e.g., specific PDF chunks). USE THEM.
        4. Provide formatted JSON output.

        OUTPUT FORMAT:
        {{
            "selected_patterns": ["Pattern Name 1", "Pattern Name 2"],
            "justification": "Detailed explanation of why..."
        }}
        """

        try:
            response_text = self.llm_client.generate_content(prompt)
            
            # Robust JSON extraction
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
            
            selection_result = json.loads(json_str)
            return {
                "success": True, 
                "selected_patterns": selection_result.get("selected_patterns", []),
                "justification": selection_result.get("justification", ""),
                "retrieved_patterns_count": len(retrieved_contexts)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
