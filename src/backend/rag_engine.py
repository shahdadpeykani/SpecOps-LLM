"""
RAG Engine.
Handles retrieval of design patterns using embeddings.
"""
import json
import os
import numpy as np
from src.backend.llm_client import LLMClient

class RAGEngine:
    def __init__(self):
        self.llm_client = LLMClient()
        self.kb_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../data/knowledge_base/patterns.json')
        )
        self.cache_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../data/cache/embeddings.json')
        )
        self.patterns = []
        self.embeddings = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """
        Loads patterns and generates/caches valid embeddings.
        """
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
            
            # Try to load cached embeddings
            if os.path.exists(self.cache_path):
                print("Loading cached embeddings...")
                try:
                    with open(self.cache_path, 'r', encoding='utf-8') as f:
                        self.embeddings = json.load(f)
                    print("Cached embeddings loaded.")
                    return
                except Exception as e:
                    print(f"Cache load failed: {e}. Regenerating embeddings...")
            
            # Generate and cache embeddings
            print("Generating embeddings for Knowledge Base...")
            for p in self.patterns:
                text = f"{p['name']}: {p['description']} {p['use_case']}"
                emb = self.llm_client.get_embedding(text)
                if emb:
                    self.embeddings.append(emb)
                else:
                    self.embeddings.append([0.0]*768) # Fallback placeholder
            
            # Save to cache
            try:
                os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
                with open(self.cache_path, 'w', encoding='utf-8') as f:
                    json.dump(self.embeddings, f)
                print("Embeddings cached for future use.")
            except Exception as e:
                print(f"Failed to cache embeddings: {e}")

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """
        Retrieves top_k patterns matching the query.
        """
        query_emb = self.llm_client.get_embedding(query)
        if not query_emb:
            return []

        # Cosine Similarity
        query_vec = np.array(query_emb)
        scores = []
        for i, emb in enumerate(self.embeddings):
            doc_vec = np.array(emb)
            if np.linalg.norm(doc_vec) == 0:
                scores.append( -1.0 )
                continue
            
            score = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            scores.append(score)

        # Get indices of top k
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "pattern": self.patterns[idx],
                "score": float(scores[idx])
            })
            
        return results
