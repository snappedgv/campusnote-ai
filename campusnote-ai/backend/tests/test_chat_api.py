def test_chat_requires_auth(client):
    resp = client.post("/api/chat", json={"question": "What is normalization?"})
    assert resp.status_code == 401


def test_chat_with_no_matching_notes_returns_honest_message(client, student_token):
    """With no documents ingested, the RAG pipeline must NOT hallucinate an
    answer -- it should report that no relevant notes were found."""
    resp = client.post(
        "/api/chat",
        json={"question": "Explain the CAP theorem in distributed databases."},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["grounded"] is False
    assert data["sources"] == []
    assert "not" in data["answer"].lower()  # "couldn't find enough information..."


def test_chat_empty_question_rejected(client, student_token):
    resp = client.post(
        "/api/chat",
        json={"question": "   "},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 400


def test_admin_only_document_upload_rejected_for_student(client, student_token):
    resp = client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", b"some notes content", "text/plain")},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert resp.status_code == 403
