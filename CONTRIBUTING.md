# Contributing to College Event Management System 🎓

Thank you for your interest in contributing to the **College Event Management System**! This is an Open Source Software (OSS) mini project built with Flask, SQLite, and vanilla HTML/CSS/JavaScript, designed to be friendly to first-time contributors and students.

---

## 🌟 Good First Issues for Beginners

Looking for a place to start? Here are curated beginner-friendly contribution ideas:

| Issue Idea | Area | Description |
|---|---|---|
| **#1 Export to CSV** | Backend / Admin | Add an endpoint and frontend button to export the registered students list to a `.csv` file. |
| **#2 QR Code Attendance** | Frontend / Backend | Generate a unique QR code for each confirmed student registration for event check-in. |
| **#3 Calendar View** | Frontend | Add a monthly/weekly calendar toggle on the main event discovery page using CSS Grid. |
| **#4 Email Notifications** | Backend | Send a confirmation email upon registration using Flask-Mail or SMTP. |
| **#5 Event Feedback & Ratings** | Full Stack | Allow registered students to submit star ratings and comments after an event ends. |
| **#6 Multi-Tag Filtering** | Frontend / Backend | Support multiple category tags simultaneously or tags like "Free Food", "Certificates Provided". |

---

## 🛠️ Local Development Setup (Windows / macOS / Linux)

### 1. Prerequisites
- Python 3.9+ (Python 3.11 or 3.12 recommended)
- Git

### 2. Fork & Clone
```powershell
# Clone your fork
git clone https://github.com/<your-username>/College-event-management-system.git
cd College-event-management-system
```

### 3. Create a Virtual Environment (Recommended)
On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 5. Run the Application
From the repository root directory:
```bash
python run.py
```
Open your browser at:
- **Student Discovery Portal**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Dashboard**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

---

## 🧪 Running Automated Tests

Always ensure existing tests pass before opening a Pull Request:

```bash
# Run tests with pytest
pytest tests -v

# Or run using Python directly
python -m pytest tests -v
```

All new features should include corresponding test coverage under the `tests/` directory.

---

## 🔒 Security & Coding Standards

1. **Parameterized SQL Queries ONLY**:
   - Never use string interpolation (`f"SELECT ... WHERE id = {id}"`).
   - Always use `cursor.execute("SELECT ... WHERE id = ?", (id,))`.
2. **Password Security**:
   - Never store plain text passwords. Always use `generate_password_hash` and `check_password_hash`.
3. **Role Enforcement**:
   - Protect all administrative endpoints with `@admin_required`.
4. **Input Validation**:
   - Validate emails, string lengths, capacities, and whitelisted categories (`Technical`, `Cultural`, `Sports`, `Workshops`).
5. **No Broken Existing Files**:
   - Preserve existing git history and license headers.

---

## 🚀 Pull Request Guidelines

1. Create a descriptive branch:
   ```bash
   git checkout -b feature/export-attendance-csv
   ```
2. Commit with meaningful commit messages:
   ```bash
   git commit -m "feat(admin): add CSV export button for event attendees"
   ```
3. Push to your fork:
   ```bash
   git push origin feature/export-attendance-csv
   ```
4. Open a Pull Request against the `main` branch. Describe your changes clearly and link any associated issues.

Thank you for building open source software with us! 🎉
