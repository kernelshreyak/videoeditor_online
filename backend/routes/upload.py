from flask import Blueprint, request
from pathlib import Path
from werkzeug.utils import secure_filename

from backend.config import ALLOWED_EXTENSIONS, CLIPS_DIR, MAX_UPLOAD_SIZE
from backend.services.video_service import ensure_clips_dir
from backend.utils.file_utils import save_file

bp = Blueprint("upload", __name__)

@bp.route("/upload_video", methods=["POST"])
def upload_video():
    videofile = request.files.get("videofile")
    if videofile is None or videofile.filename == "":
        return {"status": "error", "message": "No video file provided"}, 400

    # Validate file extension
    filename = videofile.filename or ""
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return {
            "status": "error",
            "message": f"Invalid file type. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        }, 400

    # Validate MIME type
    if videofile.content_type and not videofile.content_type.startswith("video/"):
        return {
            "status": "error",
            "message": f"Invalid MIME type. Expected video/*, got {videofile.content_type}",
        }, 400

    # Validate file size
    videofile.seek(0, 2)  # Seek to end
    file_size = videofile.tell()
    videofile.seek(0)  # Reset to beginning

    if file_size > MAX_UPLOAD_SIZE:
        max_mb = MAX_UPLOAD_SIZE / (1024 * 1024)
        return {
            "status": "error",
            "message": f"File too large. Maximum size: {max_mb:.0f}MB",
        }, 400

    ensure_clips_dir()
    safe_name = secure_filename(filename)
    target_path = CLIPS_DIR / safe_name
    save_file(videofile, target_path)

    return f"{CLIPS_DIR.name}/{safe_name}"