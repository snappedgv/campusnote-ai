"""
SQLAlchemy engine/session configuration.
Uses SQLite for development. Swap DATABASE_URL for PostgreSQL/MySQL
in production -- no other code changes required because all queries
go through the ORM.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
from app.config import settings, BASE_DIR

db_url = settings.DATABASE_URL
connect_args = {}

if db_url.startswith("sqlite"):
    # Ensure the sqlite file path resolves relative to backend/ and the folder exists
    connect_args = {"check_same_thread": False}
    if db_url.startswith("sqlite:///./"):
        rel_path = db_url.replace("sqlite:///./", "")
        abs_path = (BASE_DIR / rel_path).resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite:///{abs_path}"

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called on app startup."""
    from app.models import user, subject, document, chat, bookmark  # noqa: F401
    Base.metadata.create_all(bind=engine)
