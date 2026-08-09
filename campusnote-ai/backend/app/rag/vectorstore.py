"""
Vector Store (ChromaDB)
=======================
Thin wrapper around a persistent ChromaDB collection. Uses Chroma's
built-in local embedding function (ONNX MiniLM) by default so the
project runs out of the box with zero embedding API keys. This is
configurable via EMBEDDING_PROVIDER in .env, and can be swapped for a
different provider in `embeddings.py` without touching call sites.

Optional FAISS support: the same add/query interface could be backed by
a FAISS index instead of Chroma. Left as a TODO extension point -- see
`FAISS_TODO` note below -- since Chroma already gives persistence +
metadata filtering out of the box, which FAISS does not natively.
"""
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
from app.config import settings

_client = None
_collection = None


def get_embedding_function():
    """
    Returns the embedding function used for both indexing and querying.
    EMBEDDING_PROVIDER=local -> Chroma's bundled ONNX MiniLM model (no API key).
    Other providers are TODO extension points (see embeddings.py).
    """
    if settings.EMBEDDING_PROVIDER == "local":
        return embedding_functions.DefaultEmbeddingFunction()
    # TODO: plug in a hosted embedding provider here if EMBEDDING_PROVIDER != "local"
    return embedding_functions.DefaultEmbeddingFunction()


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(settings.resolved_chroma_path()))
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name="campusnote_chunks",
            embedding_function=get_embedding_function(),
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunk_ids: List[str], texts: List[str], metadatas: List[Dict]):
    """Adds chunks to the vector store. Embeddings are generated automatically."""
    if not chunk_ids:
        return
    collection = get_collection()
    collection.add(ids=chunk_ids, documents=texts, metadatas=metadatas)


def delete_document_chunks(document_id: str):
    """Removes every chunk belonging to a document (used on delete/re-index)."""
    collection = get_collection()
    collection.delete(where={"document_id": document_id})


def query(
    query_text: str,
    top_k: int = None,
    subject_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    topic: Optional[str] = None,
) -> Dict:
    """
    Runs a similarity search with optional metadata filters
    (subject / unit / topic), as required by Section 7.
    """
    top_k = top_k or settings.TOP_K
    collection = get_collection()

    where_clauses = []
    if subject_id:
        where_clauses.append({"subject_id": subject_id})
    if unit_id:
        where_clauses.append({"unit_id": unit_id})
    if topic:
        where_clauses.append({"topic": topic})

    where = None
    if len(where_clauses) == 1:
        where = where_clauses[0]
    elif len(where_clauses) > 1:
        where = {"$and": where_clauses}

    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
        where=where,
    )
    return results


# FAISS_TODO: to add optional FAISS backing, implement a second class with the
# same add_chunks/delete_document_chunks/query signatures backed by
# faiss.IndexFlatIP + a parallel metadata store, and select between the two
# implementations based on a VECTOR_BACKEND env var.
