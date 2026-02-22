"""Vector retrieval module using Chroma + SentenceTransformers."""

from pathlib import Path
from typing import Dict, List

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
COLLECTION_NAME = "srec_docs"


class SRECRetriever:
    """Retriever that queries a persisted Chroma collection."""

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=str(EMBEDDINGS_DIR))
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Return top-k relevant docs with metadata and scores."""
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0].tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        output: List[Dict] = []
        for text, metadata, distance in zip(documents, metadatas, distances):
            output.append(
                {
                    "text": text,
                    "metadata": metadata or {},
                    "distance": distance,
                }
            )
        return output
