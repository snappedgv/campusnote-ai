from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app.database import get_db
from app.models.document import Document, ProcessingStatus
from app.models.user import User
from app.schemas.document import DocumentOut
from app.auth.dependencies import require_admin, get_current_user
from app.utils.files import is_allowed_file, secure_filename, sha256_of_file, get_extension
from app.config import settings
from app.services.ingestion_service import process_document, reindex_document, delete_document
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/documents", tags=["documents"])
logger = get_logger("campusnote.documents")


@router.get("", response_model=List[DocumentOut])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject_id: Optional[str] = Form(None),
    unit_id: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    semester: Optional[str] = Form(None),
    academic_year: Optional[str] = Form(None),
    faculty: Optional[str] = Form(None),
    source: Optional[str] = Form("Manual Upload"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    # --- VALIDATE FILE ---
    if not file.filename or not is_allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, PPTX, TXT.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File exceeds max size of {settings.MAX_FILE_SIZE // (1024*1024)} MB.")

    # --- SAVE TO DISK ---
    upload_dir = settings.resolved_upload_dir()
    safe_name = secure_filename(file.filename)
    stored_path = upload_dir / safe_name
    stored_path.write_bytes(contents)

    # --- CALCULATE SHA-256 + CHECK DUPLICATE ---
    file_hash = sha256_of_file(stored_path)
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        stored_path.unlink(missing_ok=True)  # don't keep the duplicate copy on disk
        raise HTTPException(status_code=409, detail="This document already exists.")

    document = Document(
        filename=file.filename,
        stored_path=str(stored_path),
        file_type=get_extension(file.filename),
        subject_id=subject_id or None,
        unit_id=unit_id or None,
        topic=topic,
        department=department,
        semester=semester,
        academic_year=academic_year,
        faculty=faculty,
        source=source,
        file_hash=file_hash,
        processing_status=ProcessingStatus.PENDING,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(f"Document uploaded: {document.filename} ({document.id}) by {admin.email}")

    # Ingestion runs as a background task so the upload request returns immediately.
    background_tasks.add_task(process_document_in_new_session, document.id)

    return document


def process_document_in_new_session(document_id: str):
    """BackgroundTasks share no request-scoped DB session, so open a fresh one."""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        process_document(db, document_id)
    finally:
        db.close()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document_route(document_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    delete_document(db, doc)
    logger.info(f"Document deleted: {document_id} by {admin.email}")
    return None


@router.post("/{document_id}/reindex", response_model=DocumentOut)
def reindex_document_route(document_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    background_tasks.add_task(reindex_document_in_new_session, document_id)
    return doc


def reindex_document_in_new_session(document_id: str):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        reindex_document(db, document_id)
    finally:
        db.close()
