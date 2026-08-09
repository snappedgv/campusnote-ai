import os
import sys
import tempfile
import pytest
from pathlib import Path

# Point the app at a throwaway sqlite DB + chroma/upload dirs before importing it
TEST_DIR = tempfile.mkdtemp(prefix="campusnote_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DIR}/test.db"
os.environ["CHROMA_PATH"] = f"{TEST_DIR}/chroma"
os.environ["UPLOAD_DIR"] = f"{TEST_DIR}/uploads"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["LLM_API_KEY"] = "test-key-not-real"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.database import init_db  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _init_test_db():
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def student_token(client):
    resp = client.post("/api/auth/register", json={
        "name": "Test Student",
        "email": "student_test@example.com",
        "password": "password123",
    })
    if resp.status_code == 400:
        resp = client.post("/api/auth/login", json={
            "email": "student_test@example.com",
            "password": "password123",
        })
    return resp.json()["access_token"]
