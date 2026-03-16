from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CLIPS_DIR = BASE_DIR / "clips"

# Upload limits
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB in bytes

# Allowed video file extensions
ALLOWED_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
    ".flv",
    ".wmv",
    ".m4v",
    ".mpg",
    ".mpeg",
}
