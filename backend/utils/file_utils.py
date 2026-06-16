from pathlib import Path
from typing import List

from backend.config import CLIPS_DIR

def ensure_clips_dir():
    """Ensure the clips directory exists."""
    CLIPS_DIR.mkdir(exist_ok=True)

def save_file(videofile, target_path: Path):
    """Save uploaded file to target path."""
    videofile.save(target_path)