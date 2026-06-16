from pathlib import Path
from typing import List

from moviepy.editor import VideoFileClip, concatenate_videoclips

from backend.config import CLIPS_DIR

def trim_video(videofile: str, start_time: int, end_time: int) -> str:
    """Trim a video file."""
    input_path = CLIPS_DIR / videofile
    if not input_path.exists():
        raise FileNotFoundError(f"Video file not found: {input_path}")

    # Create output filename
    input_stem = input_path.stem
    output_path = CLIPS_DIR / f"{input_stem}_trimmed.mp4"

    # Trim the video
    with VideoFileClip(str(input_path)) as video:
        trimmed_video = video.subclip(start_time, end_time)
        trimmed_video.write_videofile(
            str(output_path), 
            codec="libx264", 
            audio_codec="aac"
        )
    
    return str(output_path.relative_to(CLIPS_DIR))

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