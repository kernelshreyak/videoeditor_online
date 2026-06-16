from flask import Blueprint, request
from typing import Any, Dict, List

from backend.services.merge_service import merge_videos

bp = Blueprint("merge", __name__)

@bp.route("/merged_render", methods=["POST"])
def merged_render():
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    try:
        videoscount = int(payload.get("videoscount", 0))
    except (TypeError, ValueError):
        return {"status": "error", "message": "videoscount must be an integer"}, 400

    if videoscount <= 0:
        return {
            "status": "error",
            "message": "merged render error. Invalid videos count",
        }, 400

    videoclip_filenames: List[str] = []
    for i in range(videoscount):
        clip_path = payload.get(f"video{i}")
        if not clip_path:
            return {
                "status": "error",
                "message": f"Missing video{i} path in payload",
            }, 400
        videoclip_filenames.append(clip_path)

    try:
        finalrender_videopath = merge_videos(videoclip_filenames)
        return {
            "status": "success",
            "message": "merged render success",
            "finalrender_videopath": finalrender_videopath,
        }
    except FileNotFoundError as exc:
        return {"status": "error", "message": str(exc)}, 404
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"video merge failure: {exc}",
        }, 500