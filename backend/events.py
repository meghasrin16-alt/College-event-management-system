"""
Events management module for College Event Management System.
Handles Event CRUD operations, search & filtering, and category validation.
"""

from datetime import date
from flask import Blueprint, request, jsonify, session
from backend.database import get_db
from backend.auth import admin_required

events_bp = Blueprint("events", __name__, url_prefix="/api/events")

VALID_CATEGORIES = ("Technical", "Cultural", "Sports", "Workshops")


def serialize_event(row, current_user_id=None, registered_ids=None):
    """
    Converts a sqlite Row into a clean dictionary with calculated fields.
    """
    event_dict = dict(row)
    registered_count = event_dict.get("registered_count", 0)
    capacity = event_dict.get("capacity", 50)
    spots_left = max(0, capacity - registered_count)
    event_dict["registered_count"] = registered_count
    event_dict["spots_left"] = spots_left
    event_dict["is_full"] = spots_left <= 0

    if registered_ids is not None:
        event_dict["is_registered"] = event_dict["id"] in registered_ids
    else:
        event_dict["is_registered"] = bool(event_dict.get("is_registered", False))

    return event_dict


@events_bp.route("", methods=["GET"])
def list_events():
    """
    List events with optional search, category filter, and status filter.
    """
    search_query = (request.args.get("search") or "").strip()
    category = (request.args.get("category") or "").strip()
    status = (request.args.get("status") or "all").strip().lower()
    sort_by = (request.args.get("sort") or "date_asc").strip().lower()

    current_user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()
    try:
        query = """
            SELECT 
                e.*,
                COALESCE(r.reg_count, 0) AS registered_count
            FROM events e
            LEFT JOIN (
                SELECT event_id, COUNT(*) AS reg_count 
                FROM registrations 
                WHERE status = 'confirmed' 
                GROUP BY event_id
            ) r ON e.id = r.event_id
            WHERE 1=1
        """
        params = []

        if category and category in VALID_CATEGORIES:
            query += " AND e.category = ?"
            params.append(category)

        if search_query:
            query += " AND (e.title LIKE ? OR e.description LIKE ? OR e.venue LIKE ?)"
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard])

        today_str = date.today().isoformat()
        if status == "upcoming":
            query += " AND e.event_date >= ?"
            params.append(today_str)
        elif status == "past":
            query += " AND e.event_date < ?"
            params.append(today_str)

        if sort_by == "date_desc":
            query += " ORDER BY e.event_date DESC, e.event_time DESC"
        elif sort_by == "popularity":
            query += " ORDER BY registered_count DESC, e.event_date ASC"
        else:  # default date_asc
            query += " ORDER BY e.event_date ASC, e.event_time ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # If user is logged in, find all events they are registered for
        registered_ids = set()
        if current_user_id:
            cursor.execute(
                "SELECT event_id FROM registrations WHERE student_id = ? AND status = 'confirmed'",
                (current_user_id,),
            )
            registered_ids = {r["event_id"] for r in cursor.fetchall()}

        events = [
            serialize_event(r, current_user_id=current_user_id, registered_ids=registered_ids)
            for r in rows
        ]
        return jsonify({"events": events, "count": len(events)})
    finally:
        conn.close()


@events_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    """
    Get detailed information for a single event.
    """
    current_user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT 
                e.*,
                COALESCE(r.reg_count, 0) AS registered_count
            FROM events e
            LEFT JOIN (
                SELECT event_id, COUNT(*) AS reg_count 
                FROM registrations 
                WHERE status = 'confirmed' 
                GROUP BY event_id
            ) r ON e.id = r.event_id
            WHERE e.id = ?
            """,
            (event_id,),
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Event not found."}), 404

        is_registered = False
        if current_user_id:
            cursor.execute(
                "SELECT id FROM registrations WHERE event_id = ? AND student_id = ? AND status = 'confirmed'",
                (event_id, current_user_id),
            )
            is_registered = cursor.fetchone() is not None

        event_data = dict(row)
        event_data["is_registered"] = is_registered
        event_dict = serialize_event(event_data)
        return jsonify({"event": event_dict})
    finally:
        conn.close()


@events_bp.route("", methods=["POST"])
@admin_required
def create_event():
    """
    Create a new event (Admin only).
    """
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    category = (data.get("category") or "").strip()
    event_date = (data.get("event_date") or "").strip()
    event_time = (data.get("event_time") or "").strip()
    venue = (data.get("venue") or "").strip()
    capacity = data.get("capacity")
    registration_deadline = (data.get("registration_deadline") or "").strip() or None
    organizer_contact = (data.get("organizer_contact") or "").strip()
    banner_url = (data.get("banner_url") or "").strip()

    # Validation
    if not title:
        return jsonify({"error": "Event title is required."}), 400
    if not description:
        return jsonify({"error": "Event description is required."}), 400
    if category not in VALID_CATEGORIES:
        return (
            jsonify(
                {
                    "error": f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}."
                }
            ),
            400,
        )
    if not event_date:
        return jsonify({"error": "Event date is required (YYYY-MM-DD)."}), 400
    if not event_time:
        return jsonify({"error": "Event time is required (HH:MM)."}), 400
    if not venue:
        return jsonify({"error": "Event venue is required."}), 400

    try:
        capacity = int(capacity)
        if capacity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return (
            jsonify({"error": "Capacity must be a positive integer greater than zero."}),
            400,
        )

    user_id = session.get("user_id")

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO events (
                title, description, category, event_date, event_time, venue,
                capacity, registration_deadline, organizer_contact, banner_url, created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                category,
                event_date,
                event_time,
                venue,
                capacity,
                registration_deadline,
                organizer_contact,
                banner_url,
                user_id,
            ),
        )
        conn.commit()
        new_event_id = cursor.lastrowid

        return (
            jsonify(
                {
                    "message": "Event created successfully!",
                    "event": {
                        "id": new_event_id,
                        "title": title,
                        "category": category,
                        "event_date": event_date,
                        "event_time": event_time,
                        "venue": venue,
                        "capacity": capacity,
                    },
                }
            ),
            201,
        )
    finally:
        conn.close()


@events_bp.route("/<int:event_id>", methods=["PUT"])
@admin_required
def update_event(event_id):
    """
    Update an existing event (Admin only).
    """
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    category = (data.get("category") or "").strip()
    event_date = (data.get("event_date") or "").strip()
    event_time = (data.get("event_time") or "").strip()
    venue = (data.get("venue") or "").strip()
    capacity = data.get("capacity")
    registration_deadline = (data.get("registration_deadline") or "").strip() or None
    organizer_contact = (data.get("organizer_contact") or "").strip()
    banner_url = (data.get("banner_url") or "").strip()

    if not title or not description or not venue or not event_date or not event_time:
        return jsonify({"error": "Title, description, venue, date, and time are required."}), 400

    if category not in VALID_CATEGORIES:
        return (
            jsonify(
                {
                    "error": f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}."
                }
            ),
            400,
        )

    try:
        capacity = int(capacity)
        if capacity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return (
            jsonify({"error": "Capacity must be a positive integer greater than zero."}),
            400,
        )

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM events WHERE id = ?", (event_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Event not found."}), 404

        cursor.execute(
            """
            UPDATE events
            SET title = ?, description = ?, category = ?, event_date = ?,
                event_time = ?, venue = ?, capacity = ?, registration_deadline = ?,
                organizer_contact = ?, banner_url = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                category,
                event_date,
                event_time,
                venue,
                capacity,
                registration_deadline,
                organizer_contact,
                banner_url,
                event_id,
            ),
        )
        conn.commit()
        return jsonify({"message": "Event updated successfully!"})
    finally:
        conn.close()


@events_bp.route("/<int:event_id>", methods=["DELETE"])
@admin_required
def delete_event(event_id):
    """
    Delete an event (Admin only). Associated registrations cascade delete.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if not event:
            return jsonify({"error": "Event not found."}), 404

        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        return jsonify(
            {"message": f"Event '{event['title']}' deleted successfully."}
        )
    finally:
        conn.close()
