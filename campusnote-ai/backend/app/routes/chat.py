from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.chat import Chat, Message
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ChatOut, ChatSummaryOut, SourceOut
from app.auth.dependencies import get_current_user
from app.services.chat_service import answer_question
from app.utils.logger import get_logger

router = APIRouter(prefix="/api", tags=["chat"])
logger = get_logger("campusnote.chat_route")


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Find or create the chat thread
    if payload.chat_id:
        chat_obj = db.query(Chat).filter(Chat.id == payload.chat_id, Chat.user_id == current_user.id).first()
        if not chat_obj:
            raise HTTPException(status_code=404, detail="Chat not found.")
    else:
        title = payload.question.strip()[:60]
        chat_obj = Chat(
            user_id=current_user.id,
            title=title,
            subject_id=payload.subject_id,
            unit_id=payload.unit_id,
        )
        db.add(chat_obj)
        db.flush()

    # Save the user's message
    user_msg = Message(chat_id=chat_obj.id, role="user", content=payload.question)
    db.add(user_msg)

    # Run the RAG pipeline
    try:
        result = answer_question(
            question=payload.question,
            subject_id=payload.subject_id,
            unit_id=payload.unit_id,
            topic=payload.topic,
            marks=payload.marks,
        )
    except Exception as e:
        logger.error(f"Chat pipeline error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong while generating the answer. Please try again.")

    assistant_msg = Message(
        chat_id=chat_obj.id,
        role="assistant",
        content=result["answer"],
        question_type=result["question_type"],
        marks=result["marks"],
        grounded=result["grounded"],
        sources=result["sources"],
    )
    db.add(assistant_msg)

    from datetime import datetime
    chat_obj.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assistant_msg)

    return ChatResponse(
        chat_id=chat_obj.id,
        message_id=assistant_msg.id,
        answer=result["answer"],
        question_type=result["question_type"],
        marks=result["marks"],
        sources=[SourceOut(**s) for s in result["sources"]],
        grounded=result["grounded"],
    )


@router.get("/chats", response_model=List[ChatSummaryOut])
def list_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Chat).filter(Chat.user_id == current_user.id).order_by(Chat.updated_at.desc()).all()


@router.get("/chats/{chat_id}", response_model=ChatOut)
def get_chat(chat_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat_obj = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found.")
    return chat_obj


@router.delete("/chats/{chat_id}", status_code=204)
def delete_chat(chat_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat_obj = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found.")
    db.delete(chat_obj)
    db.commit()
    return None


@router.put("/chats/{chat_id}/rename", response_model=ChatSummaryOut)
def rename_chat(chat_id: str, title: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat_obj = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat_obj:
        raise HTTPException(status_code=404, detail="Chat not found.")
    chat_obj.title = title
    db.commit()
    db.refresh(chat_obj)
    return chat_obj
