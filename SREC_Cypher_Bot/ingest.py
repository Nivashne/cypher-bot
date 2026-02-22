"""Ingest local SREC documents into Chroma vector store."""

from pathlib import Path
from typing import List

import chromadb
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"
COLLECTION_NAME = "srec_docs"


def load_documents() -> List[dict]:
    documents = []
    for file_path in sorted(DATA_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()
        documents.append(
            {
                "id": file_path.stem,
                "text": text,
                "metadata": {"source": file_path.name},
            }
        )
    return documents


def ingest() -> None:
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(EMBEDDINGS_DIR))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    docs = load_documents()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        [doc["text"] for doc in docs], normalize_embeddings=True
    ).tolist()

    existing_ids = set(collection.get(include=[]).get("ids", []))
    new_docs = [doc for doc in docs if doc["id"] not in existing_ids]

    if new_docs:
        new_embeddings = [embeddings[docs.index(doc)] for doc in new_docs]
        collection.add(
            ids=[doc["id"] for doc in new_docs],
            documents=[doc["text"] for doc in new_docs],
            metadatas=[doc["metadata"] for doc in new_docs],
            embeddings=new_embeddings,
        )

    print(f"Ingestion complete. Collection '{COLLECTION_NAME}' has {collection.count()} documents.")


if __name__ == "__main__":
    ingest()
