from pathlib import Path
from typing import List

from backend.config import CLIPS_DIR

def ensure_clips_dir():
    """Ensure the clips directory exists."""
    CLIPS_DIR.mkdir(exist_ok=True)