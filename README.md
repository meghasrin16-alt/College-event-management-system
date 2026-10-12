# College Event Management System 🎓

An Open Source Software (OSS) college event management web application built with **Python Flask**, **SQLite**, and modern **vanilla HTML, CSS, and JavaScript**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Framework: Flask](https://img.shields.io/badge/Backend-Flask-black.svg)](https://flask.palletsprojects.com/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite-blue.svg)](https://www.sqlite.org/)
[![Tests: 26 Passing](https://img.shields.io/badge/Tests-26%20Passed-success.svg)](tests/)

---

## ✨ Features

1. **Student Registration & Login**:
   - Secure student registration with Roll Number, Department, Semester, Email, and hashed passwords.
   - Session-based authentication with current user tracking.
2. **Admin Dashboard**:
   - High-level metrics: Total Events, Active Events, Registered Students, Total Signups.
   - Interactive charts for Category Distributions and Popular Events.
3. **Event Management (CRUD)**:
   - Create, edit, view, and delete college events with validation.
   - Capacity controls, dates, times, venues, and registration deadlines.
4. **Standardized Event Categories**:
   - **Technical** 💻
   - **Cultural** 🎭
   - **Sports** 🏆
   - **Workshops** 🛠️
5. **Student Event Registration**:
   - Instant one-click event registration.
   - Real-time remaining seat counter and progress bar.
   - Dedicated "My Events" modal where students can view and cancel registrations.
6. **Duplicate Registration Prevention**:
   - Enforced at both the database schema level (`UNIQUE(event_id, student_id)`) and application logic layer.
7. **Registered Attendees Roster**:
   - Admins can view all students registered for any event, with name, roll number, department, and contact email.
   - Built-in attendance print / export view.
8. **Instant Search & Multi-Filters**:
   - Real-time search across event titles, descriptions, and venues.
   - Filter by category pills, timeline status (*Upcoming*, *Past*, *All*), and sort order (*Earliest*, *Latest*, *Most Popular*).
9. **Visual Analytics & Charts**:
   - Doughnut chart displaying registrations by event category.
   - Bar chart showcasing the top 5 most popular campus events.
10. **Responsive Design & Dark Mode**:
    - Clean academic UI with CSS variables, accessible contrast, and glassmorphism.
    - Persistent dark mode toggle stored in `localStorage`.
    - Fully responsive layout for mobile, tablet, and desktop viewports.

---

## 🔒 Security Measures

- **Password Hashing**: Industry-standard PBKDF2/SHA-256 via Werkzeug (`generate_password_hash`, `check_password_hash`).
- **Role-Based Access Control**: `@admin_required` decorators ensure students cannot access administrative endpoints or delete events.
- **Strict Parameterized SQL Queries**: 100% of SQLite database operations utilize parameterized queries (`?` placeholders) to eliminate SQL injection vulnerabilities.
- **Input Validation**: Server-side and client-side validation for emails, positive seat capacities, and whitelisted categories.

---

## 🏗️ Repository Architecture

```text
College-event-management-system/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md           # Bug report template
│   │   ├── feature_request.md      # Feature request template
│   │   └── good_first_issue.md     # Beginner-friendly issue proposal
│   └── workflows/
│       └── tests.yml               # Automated GitHub Actions test runner
├── backend/
│   ├── __init__.py
│   ├── app.py                      # Flask factory & static asset server
│   ├── auth.py                     # Authentication & role middleware
│   ├── database.py                 # SQLite schema, connection, & seed data
│   ├── events.py                   # Event CRUD, search, & category filters
│   ├── registrations.py            # Event signups, duplicate check, & attendees
│   ├── stats.py                    # Analytics aggregations & chart metrics
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── index.html                  # Student Portal & event discovery UI
│   ├── admin.html                  # Admin Dashboard & management portal
│   ├── css/
│   │   └── style.css               # Modern responsive styling & dark mode
│   └── js/
│       ├── api.js                  # Centralized fetch API client
│       ├── auth.js                 # Authentication state & modals
│       ├── app.js                  # Event discovery & student logic
│       └── admin.js                # Admin dashboard, charts, & event table
├── tests/
│   ├── conftest.py                 # Pytest fixtures & isolated test DB
│   ├── test_auth.py                # Auth, registration, & hashing tests
│   ├── test_events.py              # Event CRUD & category filter tests
│   ├── test_registrations.py       # Signup & duplicate prevention tests
│   └── test_stats.py               # Statistics & analytics tests
├── run.py                          # Easy launcher script for Windows/Linux
├── CONTRIBUTING.md                 # Open source contributor guide & Good First Issues
├── LICENSE                         # MIT License
├── README.md                       # Documentation
└── .gitignore                      # Git ignore file (includes *.db)
```

---

## 💻 Quickstart on Windows

### 1. Prerequisites
- Python 3.9 or higher (Python 3.11 / 3.12 recommended)
- Verify installation in PowerShell:
  ```powershell
  python --version
  ```

### 2. Clone the Repository
```powershell
git clone https://github.com/meghasrin16-alt/College-event-management-system.git
cd College-event-management-system
```

### 3. Create a Virtual Environment (Optional but recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r backend/requirements.txt
```

### 5. Launch the Server
```powershell
python run.py
```

### 6. Open in Browser
- **Student Discovery Portal**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Management Portal**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 🔑 Pre-seeded Demo Credentials

The database is automatically pre-seeded with realistic demo events and sample users on initial startup:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Administrator** | `admin@college.edu` | `AdminPassword123!` | Full Admin Dashboard, Event CRUD, Student Rosters |
| **Student** | `student@college.edu` | `StudentPassword123!` | Browse, Register, View & Cancel Registrations |
| **Student (Priya)** | `priya.sharma@college.edu` | `StudentPassword123!` | Sample student account |

---

## 🧪 Running Automated Tests

Run the full pytest automated test suite with verbose output:

```powershell
pytest tests -v
```

Or using the Python module syntax:

```powershell
python -m pytest tests -v
```

All 26 automated unit and integration tests run against an isolated SQLite test database.

---

## 📡 REST API Reference

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Public | Register a new student account |
| `POST` | `/api/auth/login` | Public | Authenticate user & start session |
| `POST` | `/api/auth/logout` | Logged In | Terminate user session |
| `GET` | `/api/auth/me` | Public | Check current authenticated session |
| `GET` | `/api/events` | Public | List events with `search`, `category`, `status`, `sort` |
| `GET` | `/api/events/<id>` | Public | Get single event details |
| `POST` | `/api/events` | Admin Only | Create a new campus event |
| `PUT` | `/api/events/<id>` | Admin Only | Update existing event |
| `DELETE`| `/api/events/<id>` | Admin Only | Delete event and its registrations |
| `POST` | `/api/events/<id>/register` | Student | Register student for event (prevents duplicates) |
| `POST` | `/api/events/<id>/unregister` | Student | Cancel event registration (frees spot) |
| `GET` | `/api/my-registrations` | Student | List logged-in student's registrations |
| `GET` | `/api/events/<id>/registrations` | Admin Only | List students registered for an event |
| `GET` | `/api/stats/summary` | Public | Retrieve metrics and category charts data |

---

## 🤝 Contributing

We welcome contributions from students and open source enthusiasts! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines, coding conventions, and a list of **Good First Issues**.

---

## 📄 License

This project is open source and available under the terms of the [MIT License](LICENSE).
