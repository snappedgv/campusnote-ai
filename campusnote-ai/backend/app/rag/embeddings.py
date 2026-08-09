"""
Embedding Generator
====================
In this implementation, embedding generation is delegated to ChromaDB's
embedding function (configured in vectorstore.py) so indexing and query-time
embedding always use the identical model -- a common source of RAG bugs when
these are handled separately.

This module exists as the explicit "Embedding Generator" pipeline stage
called out in the architecture, and as the extension point for swapping in
a hosted embedding API later (set EMBEDDING_PROVIDER in .env and implement
the branch in vectorstore.get_embedding_function()).
"""
from app.rag.vectorstore import get_embedding_function


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Directly embed a list of texts using the configured embedding function.
    Not used in the main ingestion path (Chroma embeds internally on .add()),
    but exposed for tooling/tests/evaluation that need raw vectors."""
    ef = get_embedding_function()
    return ef(texts)
