"""
Unit tests for student event registrations, duplicate prevention, and attendee lists.
"""

from tests.conftest import login_user


def test_student_register_event_success(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    # Event 3 is badminton, student@college.edu was not registered in seed
    res = client.post("/api/events/3/register")
    assert res.status_code == 201
    data = res.get_json()
    assert "Registration successful" in data["message"]


def test_duplicate_registration_prevention(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    # Student is already registered for Event 1 in demo seed
    res = client.post("/api/events/1/register")
    assert res.status_code == 409
    data = res.get_json()
    assert "already registered" in data["error"]


def test_capacity_limit_enforcement(client):
    # Admin creates an event with capacity = 1
    login_user(client, "admin@college.edu", "AdminPassword123!")
    create_res = client.post(
        "/api/events",
        json={
            "title": "Exclusive VIP Masterclass",
            "description": "Only 1 lucky attendee allowed.",
            "category": "Workshops",
            "event_date": "2026-12-29",
            "event_time": "14:00",
            "venue": "Boardroom",
            "capacity": 1,
        },
    )
    event_id = create_res.get_json()["event"]["id"]

    # Student 1 logs in and takes the only spot
    client.post("/api/auth/logout")
    login_user(client, "student@college.edu", "StudentPassword123!")
    reg1_res = client.post(f"/api/events/{event_id}/register")
    assert reg1_res.status_code == 201

    # Student 2 tries to register
    client.post("/api/auth/logout")
    login_user(client, "priya.sharma@college.edu", "StudentPassword123!")
    reg2_res = client.post(f"/api/events/{event_id}/register")
    assert reg2_res.status_code == 400
    assert "maximum capacity" in reg2_res.get_json()["error"]


def test_unregister_and_reregister(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    # Register for event 2
    reg_res = client.post("/api/events/2/register")
    assert reg_res.status_code == 201

    # Unregister
    unreg_res = client.post("/api/events/2/unregister")
    assert unreg_res.status_code == 200
    assert "Registration cancelled successfully" in unreg_res.get_json()["message"]

    # Re-register
    rereg_res = client.post("/api/events/2/register")
    assert rereg_res.status_code in (200, 201)
    assert "successful" in rereg_res.get_json()["message"].lower()


def test_my_registrations(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    res = client.get("/api/my-registrations")
    assert res.status_code == 200
    data = res.get_json()
    assert "registrations" in data
    assert data["count"] >= 1


def test_admin_view_event_attendees(client):
    login_user(client, "admin@college.edu", "AdminPassword123!")
    res = client.get("/api/events/1/registrations")
    assert res.status_code == 200
    data = res.get_json()
    assert "students" in data
    assert data["total_registered"] >= 1
    assert any(s["email"] == "student@college.edu" for s in data["students"])


def test_student_cannot_view_event_attendees(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    res = client.get("/api/events/1/registrations")
    assert res.status_code == 403
