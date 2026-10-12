"""
College Event Management System - Main Flask Application
Serves RESTful APIs and the frontend web client.
"""

import os
from flask import Flask, send_from_directory, jsonify
from backend.database import init_db
from backend.auth import auth_bp
from backend.events import events_bp
from backend.registrations import registrations_bp
from backend.stats import stats_bp

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


def create_app(test_config=None):
    """
    Application factory for the College Event Management System.
    """
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path="",
    )

    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "college-events-secret-key-2026"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config:
        app.config.update(test_config)

    # Initialize Database unless in memory or already set
    if not app.config.get("TESTING"):
        init_db(seed=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(registrations_bp)
    app.register_blueprint(stats_bp)

    # Serve Frontend Client Routes
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/admin")
    @app.route("/admin.html")
    def admin():
        return send_from_directory(FRONTEND_DIR, "admin.html")

    @app.route("/<path:path>")
    def static_files(path):
        full_path = os.path.join(FRONTEND_DIR, path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    # Global Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error occurred"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 College Event Management System running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
