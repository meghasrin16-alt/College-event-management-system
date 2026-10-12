"""
Database module for College Event Management System.
Handles SQLite connection, schema initialization, and demo data seeding.
All queries strictly use parameterized statements (?) for security.
"""

import os
import sqlite3
from werkzeug.security import generate_password_hash

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "college_events.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    roll_number TEXT UNIQUE,
    department TEXT,
    semester TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'admin')) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('Technical', 'Cultural', 'Sports', 'Workshops')),
    event_date TEXT NOT NULL,
    event_time TEXT NOT NULL,
    venue TEXT NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 50 CHECK(capacity > 0),
    registration_deadline TEXT,
    organizer_contact TEXT,
    banner_url TEXT DEFAULT '',
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'confirmed' CHECK(status IN ('confirmed', 'cancelled')),
    FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE (event_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_registrations_event ON registrations(event_id);
CREATE INDEX IF NOT EXISTS idx_registrations_student ON registrations(student_id);
"""


def get_db(db_path=None):
    """
    Establish and return a SQLite database connection with row factory.
    """
    path = db_path or os.environ.get("COLLEGE_EVENTS_DB", DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path=None, seed=True):
    """
    Initialize SQLite schema and optionally seed demo data.
    """
    conn = get_db(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        if seed:
            seed_demo_data(conn)
    finally:
        conn.close()


def seed_demo_data(conn):
    """
    Seeds initial admin, students, and events if database is newly initialized.
    """
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@college.edu",))
    if cursor.fetchone():
        return  # Already seeded

    # Seed Admin User
    admin_pw_hash = generate_password_hash("AdminPassword123!")
    cursor.execute(
        """
        INSERT INTO users (name, email, roll_number, department, semester, password_hash, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Event Coordinator Admin",
            "admin@college.edu",
            "FACULTY-001",
            "Dean of Student Affairs",
            "Staff",
            admin_pw_hash,
            "admin",
        ),
    )
    admin_id = cursor.lastrowid

    # Seed Sample Students
    student_pw_hash = generate_password_hash("StudentPassword123!")
    students = [
        (
            "Alex Rivera",
            "student@college.edu",
            "CS2026-042",
            "Computer Science",
            "6th Semester",
            student_pw_hash,
            "student",
        ),
        (
            "Priya Sharma",
            "priya.sharma@college.edu",
            "EC2026-088",
            "Electronics & Comm.",
            "4th Semester",
            student_pw_hash,
            "student",
        ),
        (
            "Rohit Verma",
            "rohit.verma@college.edu",
            "ME2026-015",
            "Mechanical Eng.",
            "6th Semester",
            student_pw_hash,
            "student",
        ),
        (
            "Ananya Patel",
            "ananya.patel@college.edu",
            "IT2026-102",
            "Information Tech.",
            "4th Semester",
            student_pw_hash,
            "student",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO users (name, email, roll_number, department, semester, password_hash, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        students,
    )

    # Seed Events across all categories
    events = [
        (
            "HackSphere 2026: 24-Hour Hackathon",
            "Annual flagship 24-hour hackathon bringing together creative minds to build innovative solutions for AI, Healthcare, and Sustainability.",
            "Technical",
            "2026-11-15",
            "09:00",
            "Main Auditorium & CS Labs",
            120,
            "2026-11-10",
            "techclub@college.edu | +91 98765 43210",
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "Tarang: Annual Cultural Carnival",
            "A dazzling celebration of music, street play, classical dance, and fashion showcase celebrating heritage and contemporary talent.",
            "Cultural",
            "2026-11-20",
            "16:00",
            "Open Air Amphitheatre",
            300,
            "2026-11-18",
            "cultural@college.edu | +91 98765 43211",
            "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "Inter-College Badminton Championship",
            "Men's & Women's singles and doubles knockout tournament featuring the top collegiate shuttlers in the state.",
            "Sports",
            "2026-11-25",
            "08:30",
            "Indoor Sports Complex Court 1-3",
            64,
            "2026-11-22",
            "sports@college.edu | +91 98765 43212",
            "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "Hands-on Generative AI & LLM Workshop",
            "Deep-dive technical workshop on Prompt Engineering, LangChain, and fine-tuning open source language models on edge devices.",
            "Workshops",
            "2026-12-02",
            "10:00",
            "Seminar Hall B",
            80,
            "2026-11-30",
            "ai.club@college.edu | +91 98765 43213",
            "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "RoboWars: Arena Combat & Line Follower",
            "Design and pilot custom autonomous line-following bots and remote-controlled combat robots in an obstacle arena.",
            "Technical",
            "2026-12-08",
            "11:00",
            "Mechanical Engineering Quad",
            50,
            "2026-12-05",
            "robotics@college.edu | +91 98765 43214",
            "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "Symphony: Battle of the College Bands",
            "Electrifying rock, indie, and fusion bands battle it out for the coveted trophy and cash prizes.",
            "Cultural",
            "2026-12-12",
            "17:30",
            "Central Grounds Stage",
            250,
            "2026-12-09",
            "music.society@college.edu | +91 98765 43215",
            "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "College Premier Cricket League 2026",
            "Departmental cricket tournament formatted in T10 style. Register your team players and represent your branch.",
            "Sports",
            "2026-12-18",
            "07:30",
            "Main Sports Ground",
            100,
            "2026-12-14",
            "cricket@college.edu | +91 98765 43216",
            "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
        (
            "Full Stack Web Development with Modern Python",
            "Build, containerize, and deploy full stack web applications with Flask, SQLite, and cloud deployment pipelines.",
            "Workshops",
            "2026-12-22",
            "13:30",
            "Computer Center Lab 4",
            60,
            "2026-12-20",
            "webdev@college.edu | +91 98765 43217",
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&auto=format&fit=crop&q=80",
            admin_id,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO events (
            title, description, category, event_date, event_time, venue,
            capacity, registration_deadline, organizer_contact, banner_url, created_by
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        events,
    )

    # Seed Sample Registrations for Alex, Priya, Rohit, Ananya
    # Fetch student ids
    cursor.execute("SELECT id, email FROM users WHERE role = 'student'")
    student_map = {row["email"]: row["id"] for row in cursor.fetchall()}

    # Fetch event ids
    cursor.execute("SELECT id, title FROM events")
    event_list = cursor.fetchall()
    if event_list and student_map:
        e1_id = event_list[0]["id"]
        e2_id = event_list[1]["id"]
        e3_id = event_list[2]["id"]
        e4_id = event_list[3]["id"]

        alex_id = student_map.get("student@college.edu")
        priya_id = student_map.get("priya.sharma@college.edu")
        rohit_id = student_map.get("rohit.verma@college.edu")
        ananya_id = student_map.get("ananya.patel@college.edu")

        sample_regs = [
            (e1_id, alex_id),
            (e4_id, alex_id),
            (e1_id, priya_id),
            (e2_id, priya_id),
            (e3_id, rohit_id),
            (e2_id, ananya_id),
            (e4_id, ananya_id),
        ]
        for ev_id, st_id in sample_regs:
            if ev_id and st_id:
                try:
                    cursor.execute(
                        "INSERT INTO registrations (event_id, student_id) VALUES (?, ?)",
                        (ev_id, st_id),
                    )
                except sqlite3.IntegrityError:
                    pass

    conn.commit()
