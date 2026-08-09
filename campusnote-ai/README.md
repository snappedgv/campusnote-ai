# CampusNote AI

**College Notes Grounded AI Study Assistant**
*"Your College Notes. Your Syllabus. Your Exam Assistant."*

CampusNote AI is a Retrieval-Augmented Generation (RAG) study assistant for
college students. Unlike a general-purpose chatbot, every answer is grounded
in the actual PDF/DOCX/PPTX/TXT notes uploaded by your college — with source
document + page-number citations — so answers match your faculty's
terminology and syllabus instead of generic internet knowledge.

> If the uploaded notes don't contain the answer, CampusNote AI says so
> instead of inventing one. See [Strict Grounding](#strict-grounding).

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Prerequisites](#prerequisites)
6. [Installation (Windows / VS Code)](#installation-windows--vs-code)
7. [Environment Configuration](#environment-configuration)
8. [Running the App](#running-the-app)
9. [Creating an Admin Account & Demo Data](#creating-an-admin-account--demo-data)
10. [Uploading Documents](#uploading-documents)
11. [Testing the Chatbot](#testing-the-chatbot)
12. [API Documentation](#api-documentation)
13. [Strict Grounding](#strict-grounding)
14. [Running Tests](#running-tests)
15. [Troubleshooting](#troubleshooting)
16. [Security Notes](#security-notes)
17. [Future Improvements / TODOs](#future-improvements--todos)

---

## Features

- **RAG, not a generic chatbot** — every answer is retrieved from ChromaDB
  embeddings of your uploaded notes, never invented.
- **Document ingestion pipeline** — PDF / DOCX / PPTX / TXT → text
  extraction → cleaning → page-aware chunking → embeddings → ChromaDB.
- **Subject / Semester / Unit / Topic metadata filtering** on every query.
- **Exam-oriented answers** formatted for 2 / 5 / 10 / 13 / 15 marks.
- **Question-type detection**: definition, explain, difference (table),
  algorithm, programming, numerical, diagram-based, compare, short note.
- **Source citations** with document name + page number on every grounded
  answer, plus a **"Why this answer?"** panel showing the retrieved
  passages and relevance scores.
- **JWT auth** with Student and Admin roles.
- **Admin dashboard**: upload notes, manage subjects/units, view ingestion
  status, re-index, delete, basic usage stats.
- **Chat history, bookmarks, semantic search.**
- **SHA-256 duplicate detection** on upload.
- **Never fabricates sources** — if nothing relevant is retrieved, the API
  returns the honest "not available in the uploaded college notes" message.

---

## Architecture

```
Frontend (React + Vite)
        |
        | REST API (JWT)
        v
FastAPI Backend
        |
        +-- Auth (JWT, roles)
        +-- Document API (upload, list, delete, reindex)
        +-- Subject/Unit API
        +-- Chat API  ---> RAG Pipeline
        +-- Bookmarks API                |
        +-- Admin API                    +-- Parser (PDF/DOCX/PPTX/TXT)
                                          +-- Cleaner
                                          +-- Chunker (page-aware, overlap)
                                          +-- Embeddings (local, sentence-transformers)
                                          +-- ChromaDB (vector store)
                                          +-- Retriever (metadata-filtered similarity search)
                                          +-- Question-type detector
                                          +-- Prompt builder (grounding + marks format)
                                          +-- LLM client (Anthropic Claude via env)
        |
        v
SQLite (SQLAlchemy ORM; swappable for PostgreSQL/MySQL)
```

Ingestion pipeline (Section 6 of the spec):

```
Upload -> Validate -> SHA-256 hash -> Duplicate check -> Extract text
       -> Clean -> Preserve page numbers -> Chunk (size/overlap via .env)
       -> Attach metadata -> Generate embeddings -> Store in ChromaDB
       -> Save DocumentChunk + Document records -> status = completed
```

RAG query pipeline (Section 7):

```
Question -> Query embedding -> Metadata filter (subject/unit/topic)
         -> Vector similarity search (top K) -> Drop low-relevance chunks
         -> Build grounded system+user prompt -> LLM -> Answer + citations
```

---

## Technology Stack

**Frontend:** React 18, Vite, JavaScript, Tailwind CSS, React Router,
react-markdown, axios.

**Backend:** Python 3.11+, FastAPI, Pydantic, Uvicorn, SQLAlchemy, python-jose
(JWT), passlib/bcrypt.

**RAG / AI:** ChromaDB (vector store), sentence-transformers (local
embeddings, no API key required), Anthropic Claude API (LLM, via
`LLM_API_KEY`), PyMuPDF, python-docx, python-pptx.

**Database:** SQLite for development (`DATABASE_URL` is swappable for
PostgreSQL/MySQL with no code changes since access goes through the
SQLAlchemy ORM).

---

## Project Structure

```
campusnote-ai/
├── frontend/
│   ├── src/
│   │   ├── components/       # ProtectedRoute, ChatMessage, Selector, ...
│   │   ├── pages/             # Login, Register, Dashboard, Chat, History, ...
│   │   │   └── admin/          # AdminDashboard, AdminDocuments, AdminSubjects
│   │   ├── layouts/           # AppLayout (sidebar + topbar)
│   │   ├── services/          # api.js + one service per resource
│   │   ├── context/            # AuthContext, ThemeContext (dark/light)
│   │   ├── App.jsx / main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app + router registration
│   │   ├── config.py           # env-driven settings
│   │   ├── database.py         # SQLAlchemy engine/session
│   │   ├── seed.py             # creates admin + demo subjects
│   │   ├── models/             # User, Subject, Unit, Document, Chat, Bookmark ...
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── routes/             # auth, subjects, documents, chat, bookmarks, admin, search
│   │   ├── services/           # ingestion_service.py, chat_service.py
│   │   ├── rag/                # parser, cleaner, chunker, embeddings, vectorstore,
│   │   │                       # retriever, question_type, prompt_builder, llm_client, ocr(TODO)
│   │   ├── auth/                # security.py (hash/JWT), dependencies.py (guards)
│   │   └── utils/               # logger.py, files.py
│   ├── tests/                   # pytest suite
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   ├── uploads/                 # raw uploaded files
│   ├── processed/                # extracted text cache
│   └── chroma/                   # persistent vector DB
│
├── README.md
└── .gitignore
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **VS Code** (recommended) with the Python and ES7+ React extensions
- An **Anthropic API key** (or another LLM provider key) for answer
  generation — the app runs the retrieval/embedding pipeline locally and
  only calls the LLM at the final answer-generation step.

---

## Installation (Windows / VS Code)

Open the project folder in VS Code (`File > Open Folder... > campusnote-ai`),
then open a terminal (`` Ctrl+` ``) for each of the steps below.

### 1. Backend setup (PowerShell)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Now open `backend\.env` and fill in `LLM_API_KEY` and `JWT_SECRET` (see
[Environment Configuration](#environment-configuration)).

### 2. Frontend setup (PowerShell, separate terminal)

```powershell
cd frontend
npm install
```

> On macOS/Linux, replace `venv\Scripts\activate` with `source venv/bin/activate`
> and `copy .env.example .env` with `cp .env.example .env`.

---

## Environment Configuration

All secrets live in `backend/.env` (never commit this file — it's in
`.gitignore`). Copy `backend/.env.example` and fill in real values:

```
DATABASE_URL=sqlite:///./data/campusnote.db
LLM_API_KEY=your_anthropic_api_key_here
LLM_MODEL=claude-sonnet-4-6
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=all-MiniLM-L6-v2
JWT_SECRET=change_this_to_a_long_random_secret_string
CHROMA_PATH=../data/chroma
UPLOAD_DIR=../data/uploads
MAX_FILE_SIZE=26214400
FRONTEND_URL=http://localhost:5173
```

- `EMBEDDING_PROVIDER=local` uses `sentence-transformers` on-device, so no
  embedding API key is required.
- Swap `DATABASE_URL` for a PostgreSQL/MySQL connection string later —
  everything goes through SQLAlchemy so no other code changes are needed.

---

## Running the App

**Terminal 1 — backend** (from `backend/`, venv activated):

```powershell
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

**Terminal 2 — frontend** (from `frontend/`):

```powershell
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## Creating an Admin Account & Demo Data

Run the seed script once (from `backend/`, venv activated) to create an
admin account and sample demo subjects (DBMS, DAA, OS, Computer Networks):

```powershell
python -m app.seed
```

Default admin login (change the password immediately in production):

```
Email:    admin@campusnote.ai
Password: Admin@123
```

Students can self-register from `/register` in the frontend.

---

## Uploading Documents

1. Log in as the admin account.
2. Go to **Admin → Documents**.
3. Select a subject, unit, topic, and upload a PDF/DOCX/PPTX/TXT file.
4. The ingestion pipeline runs (validate → hash → extract → chunk → embed →
   store in ChromaDB) and the document's status updates from
   `pending → processing → completed` (or `failed`, with the error shown).
5. Duplicate files (same SHA-256 hash) are rejected with
   *"This document already exists."*

---

## Testing the Chatbot

1. Log in as a student.
2. Go to **Chat**, pick the subject/unit/exam/marks selectors.
3. Ask a question, e.g. *"Explain 2NF with example."*
4. The answer streams back with a **Sources** panel (document + page) and a
   **Why this answer?** button showing the retrieved passages and
   relevance scores.
5. Ask something outside the uploaded notes to see the honest
   "not available in the uploaded college notes" response — this proves the
   system is grounded and not hallucinating.

---

## API Documentation

Full interactive docs (Swagger UI) are auto-generated by FastAPI at
`http://localhost:8000/docs` once the backend is running. Key endpoints:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Student registration |
| POST | `/api/auth/login` | Login (student or admin) |
| GET | `/api/auth/me` | Current user |
| GET/POST/PUT/DELETE | `/api/subjects` | Subject & unit management |
| POST | `/api/documents/upload` | Admin: upload + ingest a document |
| GET/DELETE | `/api/documents` / `/api/documents/{id}` | List / remove documents |
| POST | `/api/documents/{id}/reindex` | Re-run the ingestion pipeline |
| POST | `/api/chat` | Ask a grounded question, get answer + sources |
| GET/DELETE | `/api/chats` / `/api/chats/{id}` | Chat history |
| POST/GET/DELETE | `/api/bookmarks` | Bookmark answers |
| GET | `/api/admin/stats` | Basic usage statistics |
| GET | `/api/search` | Semantic search across notes |

Example `/api/chat` response:

```json
{
  "answer": "...",
  "question_type": "explain",
  "marks": 5,
  "sources": [
    {
      "document": "DBMS_Unit3.pdf",
      "page": 12,
      "unit": "Unit 3",
      "relevance": 0.91,
      "excerpt": "..."
    }
  ],
  "grounded": true
}
```

---

## Strict Grounding

The system prompt sent to the LLM (see `app/rag/prompt_builder.py`)
instructs the model to answer **only** from the retrieved chunks, preserve
source terminology, and say *"This information is not available in the
uploaded college notes"* when the retrieval doesn't support an answer. The
API also independently drops low-relevance chunks (`MIN_RELEVANCE` in
`app/rag/retriever.py`) and only returns source citations when the answer
was actually grounded — citations are never fabricated.

---

## Running Tests

```powershell
cd backend
venv\Scripts\activate
pip install -r requirements.txt   # if not already installed
pytest -q
```

Covers: authentication, file/type validation, duplicate detection,
chunking, RAG retrieval, the "no matching notes" honest-failure path,
the chat API contract, and route authorization.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on backend start | Activate the venv, re-run `pip install -r requirements.txt`. |
| ChromaDB errors on first run | Make sure `data/chroma/` exists and is writable — it's created automatically by `app/config.py`. |
| "This document already exists" for a new file | The SHA-256 hash matches an existing document; delete the old one first if you intended to replace it, or use **Re-index**. |
| LLM errors ("LLM generation failed") | Check `LLM_API_KEY` in `backend/.env` and your network connection. |
| Empty/garbled answers from scanned PDFs | Scanned PDFs have no extractable text; OCR is a planned TODO (see below) — for now, use text-based PDFs or DOCX/PPTX/TXT. |
| CORS errors in the browser console | Confirm `FRONTEND_URL` in `.env` matches the URL Vite is actually running on. |
| 401 on every request | The JWT expired or `JWT_SECRET` changed after the token was issued — log in again. |

---

## Security Notes

- Passwords are hashed with bcrypt; JWTs are signed with `JWT_SECRET`.
- Admin-only endpoints are protected by role-based dependencies
  (`app/auth/dependencies.py`) — students can never reach document upload,
  deletion, or subject-management routes.
- File uploads are validated by extension and size (`MAX_FILE_SIZE`) and
  saved under sanitized, hash-derived filenames.
- No API keys, database credentials, or JWT secrets are ever sent to the
  frontend or logged (`app/utils/logger.py` never logs secrets).
- SQL injection is mitigated by exclusive use of the SQLAlchemy ORM.

---

## Future Improvements / TODOs

These are explicitly deferred per the project brief rather than silently
stubbed:

- [ ] **OCR for scanned PDFs** — `app/rag/ocr.py` is a stub; wire in
      Tesseract/EasyOCR when the extracted text length is below a
      threshold.
- [ ] **LMS / campus-portal integration** — `DocumentSource` abstraction
      exists with `ManualUploadSource` implemented; `LMSApiSource` /
      `CampusStackApiSource` are TODO and must only be built against an
      authorized, documented API — never by bypassing login/CAPTCHA.
- [ ] **Cross-encoder reranking** of retrieved chunks before prompting.
- [ ] **RAG evaluation dashboard** (retrieval accuracy, grounded-answer
      rate, average response time) — data model supports it; UI is TODO.
- [ ] **PostgreSQL/MySQL** in production (swap `DATABASE_URL`; the ORM
      layer already supports it).

---

Built to keep exam prep grounded in *your* college's actual notes — not
generic internet answers.
