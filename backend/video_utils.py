from pathlib import Path
import time
from typing import Iterable, List

from moviepy.editor import VideoFileClip, concatenate_videoclips

from .config import BASE_DIR, CLIPS_DIR


def ensure_clips_dir() -> None:
    """Create the clips directory if it does not already exist."""
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_clip_path(videofile: str) -> Path:
    """Convert relative clip paths (e.g., clips/foo.mp4) into absolute paths."""
    path = Path(videofile)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return path


def _relative_clip_path(path: Path) -> str:
    """Return a clip path relative to the project root, matching frontend expectations."""
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def trim_video(videofile: str, start_time: int, end_time: int) -> str:
    if start_time < 0 or end_time <= start_time:
        raise ValueError("Invalid trim window: end_time must be greater than start_time.")

    ensure_clips_dir()
    source_path = _resolve_clip_path(videofile)
    if not source_path.exists():
        raise FileNotFoundError(f"Source video not found: {videofile}")

    clip = VideoFileClip(str(source_path))
    output_name = f"edited_{int(time.time())}_{source_path.name}"
    output_path = CLIPS_DIR / output_name

    trimmed_clip = clip.subclip(start_time, end_time)
    trimmed_clip.write_videofile(str(output_path))

    # Release resources
    trimmed_clip.close()
    clip.close()
    return _relative_clip_path(output_path)


def merge_videos(videoclip_filenames: Iterable[str]) -> str:
    ensure_clips_dir()
    clips: List[VideoFileClip] = []

    try:
        for filename in videoclip_filenames:
            path = _resolve_clip_path(filename)
            if not path.exists():
                raise FileNotFoundError(f"Video not found: {filename}")
            clips.append(VideoFileClip(str(path)))

        final_clip = concatenate_videoclips(clips, method="compose")
        final_path = CLIPS_DIR / f"finalrender_{int(time.time())}.mp4"
        final_clip.write_videofile(str(final_path))
        final_clip.close()
        return _relative_clip_path(final_path)
    finally:
        for clip in clips:
            clip.close()
