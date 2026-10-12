"""
Statistics and analytics module for College Event Management System.
Aggregates event metrics, category distributions, and attendee numbers.
"""

from datetime import date
from flask import Blueprint, jsonify
from backend.database import get_db

stats_bp = Blueprint("stats", __name__, url_prefix="/api/stats")

VALID_CATEGORIES = ["Technical", "Cultural", "Sports", "Workshops"]


@stats_bp.route("/summary", methods=["GET"])
def get_stats_summary():
    """
    Returns high-level statistics, category breakdown, and popular events
    for dashboard cards and visual charts.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        today_str = date.today().isoformat()

        # 1. Total events
        cursor.execute("SELECT COUNT(*) AS total FROM events")
        total_events = cursor.fetchone()["total"]

        # 2. Upcoming vs Past events
        cursor.execute("SELECT COUNT(*) AS total FROM events WHERE event_date >= ?", (today_str,))
        upcoming_events = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM events WHERE event_date < ?", (today_str,))
        past_events = cursor.fetchone()["total"]

        # 3. Total registered students in platform
        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role = 'student'")
        total_students = cursor.fetchone()["total"]

        # 4. Total event registrations
        cursor.execute("SELECT COUNT(*) AS total FROM registrations WHERE status = 'confirmed'")
        total_registrations = cursor.fetchone()["total"]

        # 5. Category breakdown
        category_stats = []
        for cat in VALID_CATEGORIES:
            cursor.execute(
                """
                SELECT 
                    COUNT(DISTINCT e.id) AS event_count,
                    COUNT(r.id) AS registration_count
                FROM events e
                LEFT JOIN registrations r ON e.id = r.event_id AND r.status = 'confirmed'
                WHERE e.category = ?
                """,
                (cat,),
            )
            row = cursor.fetchone()
            category_stats.append(
                {
                    "category": cat,
                    "event_count": row["event_count"],
                    "registration_count": row["registration_count"],
                }
            )

        # 6. Top 5 Most Popular Events
        cursor.execute(
            """
            SELECT 
                e.id,
                e.title,
                e.category,
                e.capacity,
                e.event_date,
                COUNT(r.id) AS registration_count
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id AND r.status = 'confirmed'
            GROUP BY e.id
            ORDER BY registration_count DESC, e.title ASC
            LIMIT 5
            """
        )
        popular_events = [dict(row) for row in cursor.fetchall()]
        for p in popular_events:
            cap = p.get("capacity", 1) or 1
            p["fill_percentage"] = round((p["registration_count"] / cap) * 100, 1)

        # 7. Recent 5 registrations
        cursor.execute(
            """
            SELECT 
                r.id,
                r.registered_at,
                u.name AS student_name,
                u.roll_number,
                e.title AS event_title,
                e.category
            FROM registrations r
            JOIN users u ON r.student_id = u.id
            JOIN events e ON r.event_id = e.id
            WHERE r.status = 'confirmed'
            ORDER BY r.registered_at DESC
            LIMIT 5
            """
        )
        recent_registrations = [dict(row) for row in cursor.fetchall()]

        return jsonify(
            {
                "metrics": {
                    "total_events": total_events,
                    "upcoming_events": upcoming_events,
                    "past_events": past_events,
                    "total_students": total_students,
                    "total_registrations": total_registrations,
                },
                "category_breakdown": category_stats,
                "popular_events": popular_events,
                "recent_registrations": recent_registrations,
            }
        )
    finally:
        conn.close()
