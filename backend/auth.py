"""
Authentication module for College Event Management System.
Handles registration, login, logout, password hashing, and role-based access control.
"""

import re
from functools import wraps
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required. Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required. Please log in."}), 401
        if session.get("role") != "admin":
            return (
                jsonify(
                    {"error": "Access denied. Administrator privileges required."}
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function


def get_current_user_dict():
    """Returns the current user session data or None."""
    if not session.get("user_id"):
        return None
    return {
        "id": session.get("user_id"),
        "name": session.get("name"),
        "email": session.get("email"),
        "role": session.get("role"),
        "roll_number": session.get("roll_number"),
        "department": session.get("department"),
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    roll_number = (data.get("roll_number") or "").strip().upper()
    department = (data.get("department") or "").strip()
    semester = (data.get("semester") or "").strip()
    requested_role = (data.get("role") or "student").strip().lower()
    admin_secret = data.get("admin_secret") or ""

    # Validation
    if not name or len(name) < 2:
        return jsonify({"error": "Full name must be at least 2 characters long."}), 400
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"error": "Please provide a valid email address."}), 400
    if not password or len(password) < 6:
        return (
            jsonify({"error": "Password must be at least 6 characters long."}),
            400,
        )

    # Role validation: students must provide roll_number
    # Admin can only be created if correct admin setup key is supplied
    role = "student"
    if requested_role == "admin":
        if admin_secret == "COLLEGE_ADMIN_2026":
            role = "admin"
        else:
            return (
                jsonify(
                    {"error": "Invalid administrator secret key for admin sign up."}
                ),
                403,
            )

    if role == "student" and not roll_number:
        return (
            jsonify({"error": "Roll Number is required for student registration."}),
            400,
        )

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check duplicate email
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return (
                jsonify({"error": "An account with this email address already exists."}),
                409,
            )

        # Check duplicate roll_number for students
        if roll_number:
            cursor.execute(
                "SELECT id FROM users WHERE roll_number = ?", (roll_number,)
            )
            if cursor.fetchone():
                return (
                    jsonify(
                        {
                            "error": "An account with this Roll Number already exists."
                        }
                    ),
                    409,
                )

        password_hash = generate_password_hash(password)
        cursor.execute(
            """
            INSERT INTO users (name, email, roll_number, department, semester, password_hash, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                roll_number if roll_number else None,
                department,
                semester,
                password_hash,
                role,
            ),
        )
        conn.commit()
        user_id = cursor.lastrowid

        # Automatically log in the user
        session["user_id"] = user_id
        session["name"] = name
        session["email"] = email
        session["role"] = role
        session["roll_number"] = roll_number
        session["department"] = department

        return (
            jsonify(
                {
                    "message": "Registration successful!",
                    "user": {
                        "id": user_id,
                        "name": name,
                        "email": email,
                        "role": role,
                        "roll_number": roll_number,
                        "department": department,
                        "semester": semester,
                    },
                }
            ),
            201,
        )

    finally:
        conn.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Please provide both email and password."}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, name, email, roll_number, department, semester, password_hash, role
            FROM users WHERE email = ?
            """,
            (email,),
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid email or password."}), 401

        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]
        session["roll_number"] = user["roll_number"]
        session["department"] = user["department"]

        return jsonify(
            {
                "message": "Login successful!",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                    "roll_number": user["roll_number"],
                    "department": user["department"],
                    "semester": user["semester"],
                },
            }
        )
    finally:
        conn.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Successfully logged out."})


@auth_bp.route("/me", methods=["GET"])
def me():
    current_user = get_current_user_dict()
    return jsonify({"user": current_user})
