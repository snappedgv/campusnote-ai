from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.rag.retriever import retrieve

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
def semantic_search(
    q: str = Query(..., min_length=1),
    subject_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    topic: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Semantic search over the uploaded notes (Section 18) -- reuses the
    same retriever as chat, just without an LLM generation step."""
    results = retrieve(question=q, subject_id=subject_id, unit_id=unit_id, topic=topic, top_k=10)
    return {"query": q, "results": results}
