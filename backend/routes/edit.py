from flask import Blueprint, request
from typing import Any, Dict

from backend.services.trim_service import trim_video
from backend.services.merge_service import merge_videos

bp = Blueprint("edit", __name__)

@bp.route("/edit_video/<actiontype>", methods=["POST"])
def edit_video(actiontype: str):
    payload: Dict[str, Any] = request.get_json(silent=True) or {}
    videofile = payload.get("videofile")
    if not videofile:
        return {"status": "error", "message": "Missing 'videofile' in payload"}, 400

    if actiontype != "trim":
        return {
            "status": "error",
            "message": f"Unsupported action type '{actiontype}'",
        }, 400

    try:
        start_time = int(payload.get("trim_start", 0))
        end_time = int(payload.get("trim_end", 0))
        edited_videopath = trim_video(videofile, start_time, end_time)
        return {
            "status": "success",
            "message": "video edit success",
            "edited_videopath": edited_videopath,
        }
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}, 400
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": f"video edit failure: {exc}",
        }, 500