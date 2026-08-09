"""
Central application configuration.
All values are loaded from environment variables / .env file.
Never hardcode secrets here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./data/campusnote.db"

    # LLM
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_MAX_TOKENS: int = 1500

    # Embeddings
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # JWT
    JWT_SECRET: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Vector store
    CHROMA_PATH: str = "../data/chroma"

    # File storage
    UPLOAD_DIR: str = "../data/uploads"
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20 MB

    # RAG tuning
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    TOP_K: int = 5

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # Optional LMS integration
    LMS_API_BASE_URL: str = ""
    LMS_API_TOKEN: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def resolved_upload_dir(self) -> Path:
        p = Path(self.UPLOAD_DIR)
        if not p.is_absolute():
            p = (BASE_DIR / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def resolved_chroma_path(self) -> Path:
        p = Path(self.CHROMA_PATH)
        if not p.is_absolute():
            p = (BASE_DIR / p).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
