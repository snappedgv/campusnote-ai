from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.bookmark import Bookmark
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkOut
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


@router.post("", response_model=BookmarkOut, status_code=201)
def create_bookmark(payload: BookmarkCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookmark = Bookmark(
        user_id=current_user.id,
        message_id=payload.message_id,
        question=payload.question,
        answer=payload.answer,
        subject_name=payload.subject_name,
        unit_name=payload.unit_name,
        sources=payload.sources,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.get("", response_model=List[BookmarkOut])
def list_bookmarks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Bookmark).filter(Bookmark.user_id == current_user.id).order_by(Bookmark.created_at.desc()).all()


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found.")
    db.delete(bookmark)
    db.commit()
    return None
