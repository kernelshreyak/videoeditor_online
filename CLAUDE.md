# Claude Code Guidelines

## Project Overview
Web-based video editor with Flask + MoviePy backend and Vue 3 + Vite frontend. Supports uploading, trimming, and merging video clips. Generated outputs are stored in `clips/` (runtime-created, not tracked in git).

## Architecture

### Backend (Python/Flask)
- `index.py` - Application entrypoint, runs Flask on :5000
- `backend/__init__.py` - Flask app factory with API routes
- `backend/video_utils.py` - Video processing logic (trim, merge) using MoviePy
- `backend/config.py` - Path configuration (BASE_DIR, CLIPS_DIR)

### Frontend (Vue 3/Vite)
- `frontend/src/App.vue` - Main component with upload, trim, merge UI
- `frontend/src/components/TimelineEditor.vue` - Stub component (not yet implemented)
- `frontend/src/components/CustomLoader.vue` - Loading spinner

### API Endpoints
- `GET /` - Health check
- `GET /clips/<filename>` - Serve clip files
- `POST /upload_video` - Upload video (multipart form)
- `POST /edit_video/trim` - Trim video (JSON: videofile, trim_start, trim_end)
- `POST /merged_render` - Merge clips (JSON: videoscount, video0, video1, ...)

## Development Commands

### Backend
```bash
source venv/bin/activate
pip install -r requirements.txt
./start-server  # or python index.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Dev server on :5173
npm run build    # Production build
npm run lint     # ESLint
npm run format   # Prettier
```

## Key Files to Modify
- Video processing logic: `backend/video_utils.py`
- API routes: `backend/__init__.py`
- Main UI: `frontend/src/App.vue`
- Config: `backend/config.py`

## Conventions
- Python: PEP 8, snake_case, type hints
- Vue/JS: PascalCase components, camelCase methods, single quotes
- API responses: `{status: "success"|"error", message: "...", ...data}`
- Clip paths in responses: relative to project root (e.g., `clips/file.mp4`)

## Testing
- No automated tests yet - manual testing against running servers
- Use small test clips; don't commit media files

## Common Tasks
- Adding new video effect: Add function in `video_utils.py`, route in `__init__.py`, UI controls in `App.vue`
- Changing output format: Modify `write_videofile()` calls in `video_utils.py`
