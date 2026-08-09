"""
Chat Service
============
Orchestrates the full RAG chat flow (Section 7):
question -> retrieve -> build grounded prompt -> LLM -> answer + sources

Also implements the "no relevant notes" honest-failure behavior from
Section 24, and never fabricates source citations (Section 23).
"""
from typing import Optional
from app.rag.retriever import retrieve
from app.rag.question_type import detect_question_type
from app.rag.prompt_builder import build_prompt
from app.rag.llm_client import generate_answer
from app.utils.logger import get_logger

logger = get_logger("campusnote.chat")

NO_NOTES_MESSAGE = (
    "I couldn't find enough information about this question in the uploaded "
    "college notes. Try selecting the correct subject/unit or upload the "
    "relevant material."
)


def answer_question(
    question: str,
    subject_id: Optional[str] = None,
    unit_id: Optional[str] = None,
    topic: Optional[str] = None,
    marks: Optional[int] = None,
) -> dict:
    """
    Returns:
    {
      "answer": str,
      "question_type": str,
      "marks": int|None,
      "sources": [{"document","document_id","page","unit","relevance","excerpt"}],
      "grounded": bool
    }
    """
    question_type = detect_question_type(question)

    retrieved = retrieve(
        question=question,
        subject_id=subject_id or None,
        unit_id=unit_id or None,
        topic=topic or None,
    )

    if not retrieved:
        return {
            "answer": NO_NOTES_MESSAGE,
            "question_type": question_type,
            "marks": marks,
            "sources": [],
            "grounded": False,
        }

    prompt = build_prompt(
        question=question,
        retrieved_chunks=retrieved,
        question_type=question_type,
        marks=marks,
    )

    try:
        answer_text = generate_answer(prompt["system"], prompt["user"])
    except RuntimeError as e:
        # LLM failure (Section 24) -- fail cleanly, never a raw stack trace.
        logger.error(f"LLM generation failed: {e}")
        return {
            "answer": f"Sorry, I ran into a problem generating the answer: {e}",
            "question_type": question_type,
            "marks": marks,
            "sources": [],
            "grounded": False,
        }

    # If the model itself reports the notes are insufficient, mark ungrounded
    grounded = "not available in the uploaded college notes" not in answer_text.lower()

    sources = [
        {
            "document": c["document"],
            "document_id": c.get("document_id"),
            "page": c.get("page"),
            "unit": c.get("unit"),
            "relevance": c["relevance"],
            "excerpt": c["text"][:400],
        }
        for c in retrieved
    ] if grounded else []

    return {
        "answer": answer_text,
        "question_type": question_type,
        "marks": marks,
        "sources": sources,
        "grounded": grounded,
    }
