import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List

from moviepy.editor import VideoFileClip, concatenate_videoclips

from .config import BASE_DIR, CLIPS_DIR


def ensure_clips_dir() -> None:
    """Create the clips directory if it does not already exist."""
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_old_clips(max_age_hours: int = 24) -> int:
    """
    Delete video clips older than the specified age.

    Args:
        max_age_hours: Maximum age in hours before clips are deleted (default: 24)

    Returns:
        Number of files deleted
    """
    if not CLIPS_DIR.exists():
        return 0

    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    deleted_count = 0

    for file_path in CLIPS_DIR.glob("*"):
        if not file_path.is_file():
            continue

        # Get file modification time
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

        if file_mtime < cutoff_time:
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception:  # noqa: BLE001
                # Continue cleanup even if one file fails
                pass

    return deleted_count


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
        raise ValueError(
            "Invalid trim window: end_time must be greater than start_time."
        )

    ensure_clips_dir()
    source_path = _resolve_clip_path(videofile)
    if not source_path.exists():
        raise FileNotFoundError(f"Source video not found: {videofile}")

    clip = None
    trimmed_clip = None
    try:
        clip = VideoFileClip(str(source_path))

        # Validate trim times against video duration
        if end_time > clip.duration:
            raise ValueError(
                f"end_time ({end_time}s) exceeds video duration ({clip.duration:.2f}s)"
            )

        output_name = f"edited_{int(time.time())}_{source_path.name}"
        output_path = CLIPS_DIR / output_name

        trimmed_clip = clip.subclip(start_time, end_time)
        trimmed_clip.write_videofile(str(output_path))

        return _relative_clip_path(output_path)
    finally:
        # Ensure resources are released even on exception
        if trimmed_clip is not None:
            trimmed_clip.close()
        if clip is not None:
            clip.close()


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
