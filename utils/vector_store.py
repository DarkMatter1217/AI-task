# utils/vector_store.py

import streamlit as st
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
from pathlib import Path
from typing import List, Tuple, Dict

class CodeVectorStore:
    def __init__(self):
        # Load or initialize embedding model
        self.model = SentenceTransformer('microsoft/codebert-base')
        self.index = None  # FAISS index will be created when patterns are added
        self.database: List[Dict] = []

    def add_code_patterns(self, patterns: List[Dict]):
        """
        Build a FAISS inner-product index from a list of code patterns.
        Each pattern is a dict with keys: 'description', 'code', plus metadata.
        """
        # Prepare texts and update in-memory database
        texts = [p["description"] + " " + p["code"] for p in patterns]
        self.database.extend(patterns)

        # Generate float32 embeddings
        embeddings = np.array(self.model.encode(texts), dtype='float32')

        # Create a flat inner-product index of appropriate dimension
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)

        # Add embeddings to the index; at runtime this takes a single argument
        # but Pyright/typing may expect two args. Use a type ignore to suppress errors.
        self.index.add(embeddings)  # type: ignore[arg-type]

    def find_similar_patterns(self, code: str, k: int = 3) -> List[Tuple[Dict, float]]:
        """
        Encode the query 'code' snippet and search the FAISS index for the top-k similar patterns.
        Returns a list of tuples (pattern_dict, similarity_score).
        """
        if self.index is None:
            return []

        # Encode the query vector
        query_emb = np.array(self.model.encode([code]), dtype='float32')

        # Perform search: at runtime, search(query_emb, k) returns (distances, indices)
        # but static type checkers may expect a different signature. Suppress type errors.
        distances, indices = self.index.search(query_emb, k)  # type: ignore[arg-type]

        # Build the result list
        results: List[Tuple[Dict, float]] = []
        for row_idx, row_ids in enumerate(indices):
            for j, idx in enumerate(row_ids):
                if idx < len(self.database):
                    results.append((self.database[idx], float(distances[row_idx][j])))
        return results

@st.cache_resource
def get_vector_store() -> CodeVectorStore:
    """
    Initialize and cache the CodeVectorStore, loading predefined patterns from disk.
    """
    store = CodeVectorStore()
    try:
        patterns_path = Path("data/patterns/algorithm_patterns.json")
        patterns = json.loads(patterns_path.read_text())
        store.add_code_patterns(patterns)
    except Exception:
        # If loading fails, proceed with an empty store
        pass
    return store
