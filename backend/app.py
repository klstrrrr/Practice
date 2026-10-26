import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.database import close_db, init_db
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp


def create_app(test_config=None):
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        static_folder=str(project_root / "frontend"),
        static_url_path="/frontend",
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("TASKFLOW_SECRET_KEY", "development-only-change-me"),
        DATABASE=str(project_root / "database" / "taskflow.db"),
    )

    if test_config is not None:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    with app.app_context():
        init_db()

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Method not allowed"}), 405

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
