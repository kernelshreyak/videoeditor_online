from pathlib import Path
from typing import Set

# Configuration
CLIPS_DIR = Path("clips")
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS: Set[str] = {".mp4", ".avi", ".mov", ".mkv", ".webm"}