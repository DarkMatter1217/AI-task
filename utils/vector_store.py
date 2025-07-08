import streamlit as st
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
from pathlib import Path
from typing import List, Tuple, Dict

class CodeVectorStore:
    def __init__(self):
        self.model = SentenceTransformer('microsoft/codebert-base')
        self.index = None
        self.database: List[Dict] = []

    def add_code_patterns(self, patterns: List[Dict]):
        texts = [p["description"] + " " + p["code"] for p in patterns]
        self.database.extend(patterns)
        embeddings = np.array(self.model.encode(texts), dtype='float32')
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)  # type: ignore[arg-type]

    def find_similar_patterns(self, code: str, k: int = 3) -> List[Tuple[Dict, float]]:
        if self.index is None:
            return []
        query_emb = np.array(self.model.encode([code]), dtype='float32')
        distances, indices = self.index.search(query_emb, k)  # type: ignore[arg-type]
        results: List[Tuple[Dict, float]] = []
        for row_idx, row_ids in enumerate(indices):
            for j, idx in enumerate(row_ids):
                if idx < len(self.database):
                    results.append((self.database[idx], float(distances[row_idx][j])))
        return results

@st.cache_resource
def get_vector_store() -> CodeVectorStore:
    store = CodeVectorStore()
    try:
        patterns_path = Path("data/patterns/algorithm_patterns.json")
        patterns = json.loads(patterns_path.read_text())
        store.add_code_patterns(patterns)
    except Exception:
        pass
    return store
