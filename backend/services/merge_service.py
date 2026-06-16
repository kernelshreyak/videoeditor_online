from pathlib import Path
from typing import List

from moviepy.editor import concatenate_videoclips

from backend.config import CLIPS_DIR
from backend.utils.file_utils import ensure_clips_dir

def merge_videos(videoclip_filenames: List[str]) -> str:
    """Merge multiple video files."""
    # Get the full paths for the videos
    video_paths = [CLIPS_DIR / filename for filename in videoclip_filenames]
    
    # Check if all files exist
    for path in video_paths:
        if not path.exists():
            raise FileNotFoundError(f"Video file not found: {path}")
    
    # Create output filename
    output_path = CLIPS_DIR / "merged_output.mp4"

    # Merge the videos
    with concatenate_videoclips([VideoFileClip(str(path)) for path in video_paths]) as final_clip:
        final_clip.write_videofile(
            str(output_path), 
            codec="libx264", 
            audio_codec="aac"
        )
    
    return str(output_path.relative_to(CLIPS_DIR))