def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "supersecret",
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "student"

    resp2 = client.post("/api/auth/login", json={
        "email": "alice@example.com",
        "password": "supersecret",
    })
    assert resp2.status_code == 200
    assert "access_token" in resp2.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "password": "correctpass",
    })
    resp = client.post("/api/auth/login", json={
        "email": "bob@example.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, student_token):
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "student"


def test_student_cannot_access_admin_stats(client, student_token):
    resp = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {student_token}"})
    assert resp.status_code == 403
