from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.subject import Subject, Unit
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectOut
from app.auth.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Subject).all()


@router.post("", response_model=SubjectOut, status_code=201)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    subject = Subject(
        name=payload.name,
        code=payload.code,
        department=payload.department,
        semester=payload.semester,
    )
    db.add(subject)
    db.flush()  # get subject.id before commit

    if payload.units:
        for i, unit_name in enumerate(payload.units):
            db.add(Unit(subject_id=subject.id, name=unit_name, order_index=i))

    db.commit()
    db.refresh(subject)
    return subject


@router.put("/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: str, payload: SubjectUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=204)
def delete_subject(subject_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found.")
    db.delete(subject)
    db.commit()
    return None


@router.post("/{subject_id}/units", response_model=SubjectOut, status_code=201)
def add_unit(subject_id: str, name: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found.")
    order_index = len(subject.units)
    db.add(Unit(subject_id=subject_id, name=name, order_index=order_index))
    db.commit()
    db.refresh(subject)
    return subject
