from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.document import Document, ProcessingStatus
from app.models.user import User, UserRole
from app.models.chat import Chat, Message
from app.models.subject import Subject
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """Basic usage statistics (Section 19) + a lightweight RAG evaluation
    summary (Section 32) computed from stored chat data."""
    total_documents = db.query(func.count(Document.id)).scalar()
    completed_documents = db.query(func.count(Document.id)).filter(
        Document.processing_status == ProcessingStatus.COMPLETED
    ).scalar()
    failed_documents = db.query(func.count(Document.id)).filter(
        Document.processing_status == ProcessingStatus.FAILED
    ).scalar()
    total_students = db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar()
    total_subjects = db.query(func.count(Subject.id)).scalar()
    total_chats = db.query(func.count(Chat.id)).scalar()

    total_assistant_messages = db.query(func.count(Message.id)).filter(Message.role == "assistant").scalar()
    grounded_messages = db.query(func.count(Message.id)).filter(
        Message.role == "assistant", Message.grounded == True  # noqa: E712
    ).scalar()
    ungrounded_messages = total_assistant_messages - grounded_messages if total_assistant_messages else 0

    grounded_rate = (grounded_messages / total_assistant_messages) if total_assistant_messages else None

    return {
        "documents": {
            "total": total_documents,
            "completed": completed_documents,
            "failed": failed_documents,
        },
        "students": total_students,
        "subjects": total_subjects,
        "chats": total_chats,
        "rag_evaluation": {
            "total_questions_answered": total_assistant_messages,
            "grounded_answers": grounded_messages,
            "questions_with_no_matching_notes": ungrounded_messages,
            "grounded_answer_rate": round(grounded_rate, 3) if grounded_rate is not None else None,
            "note": "This is a lightweight, self-reported metric based on stored chat "
                    "data, not a validated accuracy benchmark. Do not treat it as a "
                    "claim of 100% correctness.",
        },
    }
