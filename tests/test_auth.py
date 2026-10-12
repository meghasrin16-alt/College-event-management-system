"""
Unit tests for authentication, password hashing, and user registration.
"""

from tests.conftest import login_user


def test_login_seeded_admin(client):
    res = login_user(client, "admin@college.edu", "AdminPassword123!")
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["role"] == "admin"
    assert data["user"]["email"] == "admin@college.edu"


def test_login_seeded_student(client):
    res = login_user(client, "student@college.edu", "StudentPassword123!")
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["role"] == "student"
    assert data["user"]["roll_number"] == "CS2026-042"


def test_login_invalid_password(client):
    res = login_user(client, "admin@college.edu", "WrongPassword!")
    assert res.status_code == 401
    assert "Invalid email or password" in res.get_json()["error"]


def test_login_nonexistent_user(client):
    res = login_user(client, "nobody@college.edu", "Password123")
    assert res.status_code == 401


def test_student_registration_success(client):
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Sarah Connor",
            "email": "sarah.connor@college.edu",
            "password": "SecurePassword123",
            "roll_number": "ME2026-999",
            "department": "Mechanical Engineering",
            "semester": "4th Semester",
        },
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["user"]["email"] == "sarah.connor@college.edu"
    assert data["user"]["role"] == "student"

    # Verify session is established
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["user"]["email"] == "sarah.connor@college.edu"


def test_registration_validation_errors(client):
    # Short name
    res = client.post(
        "/api/auth/register",
        json={"name": "A", "email": "a@college.edu", "password": "123456", "roll_number": "R1"},
    )
    assert res.status_code == 400

    # Invalid email
    res = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "not-an-email", "password": "123456", "roll_number": "R1"},
    )
    assert res.status_code == 400

    # Short password
    res = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@college.edu", "password": "123", "roll_number": "R1"},
    )
    assert res.status_code == 400

    # Missing roll number for student
    res = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@college.edu", "password": "123456", "roll_number": ""},
    )
    assert res.status_code == 400


def test_registration_duplicate_email(client):
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Duplicate Student",
            "email": "student@college.edu",  # Seeded email
            "password": "Password123",
            "roll_number": "NEW-999",
        },
    )
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]


def test_registration_duplicate_roll_number(client):
    res = client.post(
        "/api/auth/register",
        json={
            "name": "Another Student",
            "email": "unique@college.edu",
            "password": "Password123",
            "roll_number": "CS2026-042",  # Seeded roll number
        },
    )
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]


def test_logout(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    res = client.post("/api/auth/logout")
    assert res.status_code == 200

    me_res = client.get("/api/auth/me")
    assert me_res.get_json()["user"] is None
