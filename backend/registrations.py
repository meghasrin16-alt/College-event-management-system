"""
Registrations module for College Event Management System.
Handles student event signups, duplicate prevention, capacity enforcement,
and registered attendee listings.
"""

import sqlite3
from datetime import date
from flask import Blueprint, jsonify, session
from backend.database import get_db
from backend.auth import login_required, admin_required

registrations_bp = Blueprint("registrations", __name__, url_prefix="/api")


@registrations_bp.route("/events/<int:event_id>/register", methods=["POST"])
@login_required
def register_for_event(event_id):
    """
    Register the logged-in student for a specific event.
    Guarantees no duplicate registrations and enforces event capacity.
    """
    student_id = session.get("user_id")
    role = session.get("role")

    if role != "student":
        return (
            jsonify({"error": "Only student accounts can register for college events."}),
            403,
        )

    conn = get_db()
    cursor = conn.cursor()
    try:
        # Check event existence and capacity
        cursor.execute(
            """
            SELECT id, title, capacity, registration_deadline, event_date 
            FROM events WHERE id = ?
            """,
            (event_id,),
        )
        event = cursor.fetchone()
        if not event:
            return jsonify({"error": "Event not found."}), 404

        # Check deadline if defined
        today_str = date.today().isoformat()
        if event["registration_deadline"] and event["registration_deadline"] < today_str:
            return (
                jsonify(
                    {
                        "error": f"Registration closed on {event['registration_deadline']}."
                    }
                ),
                400,
            )

        # Check if already registered (prevent duplicates)
        cursor.execute(
            """
            SELECT id, status FROM registrations 
            WHERE event_id = ? AND student_id = ?
            """,
            (event_id, student_id),
        )
        existing_reg = cursor.fetchone()

        if existing_reg:
            if existing_reg["status"] == "confirmed":
                return (
                    jsonify(
                        {
                            "error": "You are already registered for this event.",
                            "registration_id": existing_reg["id"],
                        }
                    ),
                    409,
                )
            else:
                # If was cancelled earlier, re-activate
                # First check capacity
                cursor.execute(
                    """
                    SELECT COUNT(*) AS total 
                    FROM registrations 
                    WHERE event_id = ? AND status = 'confirmed'
                    """,
                    (event_id,),
                )
                current_count = cursor.fetchone()["total"]
                if current_count >= event["capacity"]:
                    return (
                        jsonify(
                            {
                                "error": "Sorry, registration is currently full for this event."
                            }
                        ),
                        400,
                    )

                cursor.execute(
                    """
                    UPDATE registrations 
                    SET status = 'confirmed', registered_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                    """,
                    (existing_reg["id"],),
                )
                conn.commit()
                return (
                    jsonify(
                        {
                            "message": f"Successfully re-registered for '{event['title']}'!",
                            "registration_id": existing_reg["id"],
                        }
                    ),
                    200,
                )

        # Check current confirmed count against capacity
        cursor.execute(
            """
            SELECT COUNT(*) AS total 
            FROM registrations 
            WHERE event_id = ? AND status = 'confirmed'
            """,
            (event_id,),
        )
        current_count = cursor.fetchone()["total"]
        if current_count >= event["capacity"]:
            return (
                jsonify(
                    {"error": "Sorry, this event has reached its maximum capacity."}
                ),
                400,
            )

        # Insert new registration
        try:
            cursor.execute(
                """
                INSERT INTO registrations (event_id, student_id, status)
                VALUES (?, ?, 'confirmed')
                """,
                (event_id, student_id),
            )
            conn.commit()
            reg_id = cursor.lastrowid

            return (
                jsonify(
                    {
                        "message": f"Registration successful for '{event['title']}'!",
                        "registration_id": reg_id,
                        "event_id": event_id,
                    }
                ),
                201,
            )
        except sqlite3.IntegrityError:
            return (
                jsonify({"error": "You are already registered for this event."}),
                409,
            )

    finally:
        conn.close()


@registrations_bp.route("/events/<int:event_id>/unregister", methods=["POST"])
@login_required
def unregister_from_event(event_id):
    """
    Allow a student to cancel their registration, freeing up the spot.
    """
    student_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id FROM registrations 
            WHERE event_id = ? AND student_id = ? AND status = 'confirmed'
            """,
            (event_id, student_id),
        )
        reg = cursor.fetchone()
        if not reg:
            return (
                jsonify({"error": "No active registration found for this event."}),
                404,
            )

        cursor.execute(
            "DELETE FROM registrations WHERE id = ?",
            (reg["id"],),
        )
        conn.commit()

        return jsonify({"message": "Registration cancelled successfully."})
    finally:
        conn.close()


@registrations_bp.route("/my-registrations", methods=["GET"])
@login_required
def get_my_registrations():
    """
    List all events the logged-in student has registered for.
    """
    student_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 
                r.id AS registration_id,
                r.registered_at,
                r.status,
                e.id AS event_id,
                e.title,
                e.description,
                e.category,
                e.event_date,
                e.event_time,
                e.venue,
                e.capacity,
                e.organizer_contact,
                e.banner_url
            FROM registrations r
            JOIN events e ON r.event_id = e.id
            WHERE r.student_id = ? AND r.status = 'confirmed'
            ORDER BY e.event_date ASC, e.event_time ASC
            """,
            (student_id,),
        )
        rows = cursor.fetchall()
        registrations = [dict(r) for r in rows]
        return jsonify({"registrations": registrations, "count": len(registrations)})
    finally:
        conn.close()


@registrations_bp.route("/events/<int:event_id>/registrations", methods=["GET"])
@admin_required
def get_event_registered_students(event_id):
    """
    List all students registered for an event (Admin only).
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, capacity FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            return jsonify({"error": "Event not found."}), 404

        cursor.execute(
            """
            SELECT 
                r.id AS registration_id,
                r.registered_at,
                r.status,
                u.id AS student_id,
                u.name,
                u.email,
                u.roll_number,
                u.department,
                u.semester
            FROM registrations r
            JOIN users u ON r.student_id = u.id
            WHERE r.event_id = ? AND r.status = 'confirmed'
            ORDER BY r.registered_at ASC
            """,
            (event_id,),
        )
        rows = cursor.fetchall()
        students = [dict(r) for r in rows]

        return jsonify(
            {
                "event_id": event["id"],
                "event_title": event["title"],
                "capacity": event["capacity"],
                "total_registered": len(students),
                "spots_remaining": max(0, event["capacity"] - len(students)),
                "students": students,
            }
        )
    finally:
        conn.close()
