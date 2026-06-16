from pathlib import Path
from flask import Flask
from flask_cors import CORS

from backend.routes import health, upload, edit, merge
from backend.config import CLIPS_DIR

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIST / "assets"),
        template_folder=str(FRONTEND_DIST),
    )
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"
    
    # Register blueprints
    app.register_blueprint(health.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(edit.bp)
    app.register_blueprint(merge.bp)
    
    return app