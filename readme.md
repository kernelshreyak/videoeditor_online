# Video Editor Online

Flask + MoviePy backend and Vue 3 frontend for simple web-based editing (upload, trim, merge). The backend writes generated clips to `clips/` (created at runtime); avoid committing media.

## Requirements
- Python 3.8+ and Node 16+
- FFmpeg available on PATH (MoviePy uses it under the hood)

## Quickstart
1) Install Python deps:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2) Run backend (Flask on :5000):
```bash
./start-server
# or on Windows: start-server-windows.bat
```
3) Run frontend (Vite dev server on :5173):
```bash
cd frontend
npm install
npm run dev
```
4) Open the dev URL from Vite, upload a small clip, trim it, and merge multiple clips to verify the flow.

## Project Structure
- `index.py`: app entrypoint using `backend/` factory
- `backend/`: Flask app (`__init__.py`), video helpers (`video_utils.py`), paths config (`config.py`)
- `frontend/`: Vue 3 + Vite app (`src/` components, `public/` static)
- `css/`: shared/vendor styles (e.g., Font Awesome)
- `clips/`: runtime uploads/renders (auto-created; not tracked)

## Development Tips
- Frontend scripts: `npm run dev`, `npm run build`, `npm run preview`, `npm run lint`, `npm run format`.
- Adjust backend behavior in `backend/video_utils.py`; ensure new outputs stay under `clips/`.
- Keep responses JSON-friendly and handle missing/invalid inputs; the frontend expects relative clip paths like `clips/<file>`.
