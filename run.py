"""
College Event Management System Launcher
Run this script to start the server:
    python run.py
"""

import sys
import os

# Add project root to Python module search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print("\n=======================================================")
    print("  🎓 College Event Management System (OSS)")
    print("=======================================================")
    print(f"  • Student Portal : http://127.0.0.1:{port}/")
    print(f"  • Admin Dashboard: http://127.0.0.1:{port}/admin")
    print("  • Default Admin  : admin@college.edu / AdminPassword123!")
    print("  • Sample Student : student@college.edu / StudentPassword123!")
    print("=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=True)
