"""
Pytest configuration and shared test fixtures for College Event Management System.
"""

import os
import tempfile
import pytest
from backend.app import create_app
from backend.database import init_db


@pytest.fixture
def app():
    """
    Creates an isolated temporary test database and yields a configured Flask app.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    os.environ["COLLEGE_EVENTS_DB"] = db_path

    # Initialize schema and seed data
    init_db(db_path=db_path, seed=True)

    flask_app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-12345",
        }
    )

    yield flask_app

    # Teardown
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


@pytest.fixture
def client(app):
    """
    Yields Flask test client with session cookies preserved.
    """
    return app.test_client()


def login_user(client, email, password):
    """Helper to authenticate a user in the test client session."""
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
