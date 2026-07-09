from flask import Blueprint, request, send_file
from pathlib import Path

from backend.config import CLIPS_DIR

bp = Blueprint("health", __name__)

@bp.route("/")
def health():
    return {"status": "success", "message": "Video editor backend"}

@bp.route("/clips/<path:filename>")
def render_clip(filename: str):
    file_path = CLIPS_DIR / filename
    if not file_path.exists():
        return {"status": "error", "message": "File not found"}, 404
    return send_file(file_path)