"""
Unit tests for events CRUD, category filtering, search, and admin permissions.
"""

from tests.conftest import login_user


def test_list_events(client):
    res = client.get("/api/events")
    assert res.status_code == 200
    data = res.get_json()
    assert "events" in data
    assert data["count"] > 0
    # Verify calculated fields
    first = data["events"][0]
    assert "spots_left" in first
    assert "registered_count" in first


def test_filter_events_by_category(client):
    res = client.get("/api/events?category=Sports")
    assert res.status_code == 200
    data = res.get_json()
    for ev in data["events"]:
        assert ev["category"] == "Sports"


def test_search_events(client):
    res = client.get("/api/events?search=Hackathon")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] >= 1
    assert "HackSphere" in data["events"][0]["title"]


def test_create_event_unauthorized_student(client):
    login_user(client, "student@college.edu", "StudentPassword123!")
    res = client.post(
        "/api/events",
        json={
            "title": "Unauthorized Event",
            "description": "Student trying to create event",
            "category": "Technical",
            "event_date": "2026-12-01",
            "event_time": "10:00",
            "venue": "Hall A",
            "capacity": 50,
        },
    )
    assert res.status_code == 403


def test_create_event_unauthenticated(client):
    res = client.post(
        "/api/events",
        json={
            "title": "Anon Event",
            "description": "Anon desc",
            "category": "Technical",
            "event_date": "2026-12-01",
            "event_time": "10:00",
            "venue": "Hall A",
            "capacity": 50,
        },
    )
    assert res.status_code == 401


def test_create_event_admin_success(client):
    login_user(client, "admin@college.edu", "AdminPassword123!")
    res = client.post(
        "/api/events",
        json={
            "title": "AI Robotics Challenge 2026",
            "description": "Comprehensive autonomous robotics competition.",
            "category": "Technical",
            "event_date": "2026-12-28",
            "event_time": "09:30",
            "venue": "Innovation Lab 2",
            "capacity": 40,
            "registration_deadline": "2026-12-25",
            "organizer_contact": "robotics@college.edu",
        },
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["event"]["title"] == "AI Robotics Challenge 2026"
    assert data["event"]["capacity"] == 40


def test_create_event_invalid_category(client):
    login_user(client, "admin@college.edu", "AdminPassword123!")
    res = client.post(
        "/api/events",
        json={
            "title": "Bad Category Event",
            "description": "Test invalid category",
            "category": "Gaming",  # Not in Technical, Cultural, Sports, Workshops
            "event_date": "2026-12-28",
            "event_time": "09:30",
            "venue": "Room 101",
            "capacity": 30,
        },
    )
    assert res.status_code == 400
    assert "Invalid category" in res.get_json()["error"]


def test_update_event_admin(client):
    login_user(client, "admin@college.edu", "AdminPassword123!")
    # Update event with ID 1
    res = client.put(
        "/api/events/1",
        json={
            "title": "Updated Flagship Hackathon",
            "description": "Updated description with extra prizes.",
            "category": "Technical",
            "event_date": "2026-11-16",
            "event_time": "10:00",
            "venue": "Main Auditorium & New Wing",
            "capacity": 150,
            "registration_deadline": "2026-11-12",
            "organizer_contact": "admin@college.edu",
        },
    )
    assert res.status_code == 200

    # Verify update persisted
    get_res = client.get("/api/events/1")
    assert get_res.status_code == 200
    assert get_res.get_json()["event"]["title"] == "Updated Flagship Hackathon"
    assert get_res.get_json()["event"]["capacity"] == 150


def test_delete_event_admin(client):
    login_user(client, "admin@college.edu", "AdminPassword123!")
    # Create an event to delete
    create_res = client.post(
        "/api/events",
        json={
            "title": "Temporary Event To Delete",
            "description": "Will be deleted immediately.",
            "category": "Cultural",
            "event_date": "2026-12-30",
            "event_time": "12:00",
            "venue": "Stage B",
            "capacity": 20,
        },
    )
    new_id = create_res.get_json()["event"]["id"]

    del_res = client.delete(f"/api/events/{new_id}")
    assert del_res.status_code == 200

    # Verify event is gone
    get_res = client.get(f"/api/events/{new_id}")
    assert get_res.status_code == 404
