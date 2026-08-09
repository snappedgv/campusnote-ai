"""
Retriever
=========
Runs the similarity search (with optional subject/unit/topic metadata
filters) and formats the results into the shape used by the prompt
builder and the API's source-citation response.
"""
from typing import List, Dict, Optional
from app.rag import vectorstore
from app.config import settings

# A retrieved chunk below this similarity is treated as noise and dropped,
# so "no relevant notes" is reported honestly instead of citing a weak match.
MIN_RELEVANCE = 0.15


def _cosine_distance_to_relevance(distance: float) -> float:
    """Chroma returns a distance (lower = more similar) for cosine space.
    Convert to a 0-1 relevance score for the UI."""
    relevance = 1 - distance
    return max(0.0, min(1.0, relevance))


def retrieve(
    question: str,
    subject_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    topic: Optional[str] = None,
    top_k: int = None,
) -> List[Dict]:
    """Returns a list of retrieved chunks:
    [{"document": filename, "document_id": ..., "page": int, "unit": str,
      "text": str, "relevance": float}]
    Sorted by relevance descending. Chunks below MIN_RELEVANCE are dropped.
    """
    top_k = top_k or settings.TOP_K
    raw = vectorstore.query(
        query_text=question,
        top_k=top_k,
        subject_id=subject_id,
        unit_id=unit_id,
        topic=topic,
    )

    results = []
    ids = raw.get("ids", [[]])[0]
    docs = raw.get("documents", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    for i in range(len(ids)):
        relevance = _cosine_distance_to_relevance(distances[i]) if distances else 0.5
        if relevance < MIN_RELEVANCE:
            continue
        meta = metadatas[i] or {}
        results.append({
            "chunk_id": ids[i],
            "text": docs[i],
            "document": meta.get("filename", "Unknown Document"),
            "document_id": meta.get("document_id"),
            "page": meta.get("page"),
            "unit": meta.get("unit_name"),
            "subject_id": meta.get("subject_id"),
            "relevance": round(relevance, 3),
        })

    results.sort(key=lambda r: r["relevance"], reverse=True)
    return results
