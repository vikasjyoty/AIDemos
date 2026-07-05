from __future__ import annotations

import chromadb
from pathlib import Path
from typing import Dict, List

from sentence_transformers import SentenceTransformer


def ingest_chunks_to_chroma(
    chunk_documents: List[Dict[str, object]],
    persist_directory: str | Path,
    collection_name: str = "rag_docs",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> None:
    """
    Convert chunk text to embeddings and store in local persistent ChromaDB.

    Why local PersistentClient:
    - Best for learning and offline experimentation.

    Other options:
    - Chroma HTTP client for a remote DB service
    - Other vector DBs like FAISS, Qdrant, Pinecone, Weaviate
    """
    if not chunk_documents:
        print("[INFO] No chunks to ingest.")
        return

    print(f"[INFO] Ingesting {len(chunk_documents)} chunk(s) into ChromaDB collection '{collection_name}'...")

    # Same embedding model used in chunking flow to keep behavior predictable.
    embedder = SentenceTransformer(model_name)
    print(f"[OK] Loaded embedding model for ingest: {model_name}")

    texts = [str(item["text"]) for item in chunk_documents]
    ids = [str(item["id"]) for item in chunk_documents]
    metadatas = [dict(item.get("metadata", {})) for item in chunk_documents]

    embeddings = embedder.encode(texts, convert_to_numpy=True).tolist()
    print(f"[OK] Generated embeddings: {len(embeddings)}")

    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    collection = _get_collection(persist_path, collection_name)

    # upsert updates existing ids and inserts new ones.
    # Alternative: collection.add(...) if you only want inserts.
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print("[OK] Chroma upsert complete.")


def _get_collection(persist_path: Path, collection_name: str):
    """Small helper used by both insert and retrieval."""
    persist_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_path))
    return client.get_or_create_collection(name=collection_name)


def retrieve_relevant_chunks(
    query_text: str,
    persist_directory: str | Path,
    collection_name: str = "rag_docs",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    top_k: int = 4,
) -> List[Dict[str, object]]:
    """
    Search the Chroma collection and return top matching chunks.

    Why explicit query embeddings:
    - Keeps ingestion and retrieval embedding model consistent.

    Other option:
    - collection.query(query_texts=[...]) with a server-side embedding function.
    """
    if not query_text.strip():
        print("[INFO] Empty query text. Nothing to retrieve.")
        return []

    print(f"[INFO] Retrieving top {top_k} chunk(s) from collection '{collection_name}'...")

    embedder = SentenceTransformer(model_name)
    query_embedding = embedder.encode(query_text, convert_to_numpy=True).tolist()

    persist_path = Path(persist_directory)
    collection = _get_collection(persist_path, collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches: List[Dict[str, object]] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        matches.append(
            {
                "text": document,
                "metadata": metadata or {},
                "distance": distance,
            }
        )

    print(f"[OK] Retrieved matches: {len(matches)}")
    return matches
