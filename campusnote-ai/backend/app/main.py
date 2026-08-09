"""
CampusNote AI - Backend Entrypoint
====================================
College Notes Grounded AI Study Assistant.
Run with:  uvicorn app.main:app --reload
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.utils.logger import setup_logging, get_logger

from app.routes import auth, subjects, documents, chat, bookmarks, admin, search

setup_logging()
logger = get_logger("campusnote.main")

app = FastAPI(
    title="CampusNote AI",
    description="College Notes Grounded AI Study Assistant - RAG API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


@app.on_event("startup")
def on_startup():
    logger.info("Starting CampusNote AI backend...")
    init_db()
    logger.info("Database initialized.")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "CampusNote AI"}


app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(bookmarks.router)
app.include_router(admin.router)
app.include_router(search.router)
