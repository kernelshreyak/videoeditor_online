from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .config import CLIPS_DIR
from .video_utils import ensure_clips_dir, merge_videos, trim_video

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIST / "assets"),
        template_folder=str(FRONTEND_DIST),
    )
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    @app.route("/")
    def health() -> Dict[str, str]:
        return {"status": "success", "message": "Video editor backend"}

    @app.route("/clips/<path:filename>")
    def render_clip(filename: str):
        file_path = CLIPS_DIR / filename
        if not file_path.exists():
            return {"status": "error", "message": "File not found"}, 404
        return send_file(file_path)

    @app.route("/upload_video", methods=["POST"])
    def upload_video():
        videofile = request.files.get("videofile")
        if videofile is None or videofile.filename == "":
            return {"status": "error", "message": "No video file provided"}, 400

        ensure_clips_dir()
        safe_name = secure_filename(videofile.filename)
        target_path = CLIPS_DIR / safe_name
        videofile.save(target_path)

        return f"{CLIPS_DIR.name}/{safe_name}"

    @app.route("/edit_video/<actiontype>", methods=["POST"])
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

    @app.route("/merged_render", methods=["POST"])
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

    return app
