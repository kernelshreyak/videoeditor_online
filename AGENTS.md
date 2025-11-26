# Repository Guidelines

## Project Structure & Modules
- Backend entrypoint is `index.py` (Flask) and app code lives in `backend/` (`__init__.py` factory, `video_utils.py`, `config.py`). Uploads/outputs are written to `clips/` (created at runtime; keep large media files out of Git).
- Frontend is a Vue 3 + Vite app under `frontend/` (`src/` for views/components, `public/` for static assets). Build artifacts land in `frontend/dist/`.
- Shared styles or vendor assets sit in `css/` (e.g., `fontawesome.min.css`). Server scripts are `start-server` (Unix) and `start-server-windows.bat`.

## Build, Test, and Development
- Backend: `pip install -r requirements.txt`, then `./start-server` (or `.bat` on Windows) to run Flask on `:5000`. Set `FLASK_APP=index.py` if running manually.
- Frontend: `cd frontend && npm install` once, then `npm run dev` for hot reload, `npm run build` for production, `npm run preview` to sanity-check the built bundle.
- Lint/format frontend: `npm run lint` (ESLint + Vue rules) and `npm run format` (Prettier on `src/`).
- No automated backend tests are present yet; prefer small, targeted additions (pytest) when touching backend logic.

## Coding Style & Naming
- Python: aim for PEP 8 (4-space indents, snake_case functions/vars); keep response payloads and config keys lower_snake. Align new utility names with `video_utils.py` patterns.
- Vue/JS: use PascalCase for component files, camelCase for methods/props, and single quotes as seen. Keep templates lean; prefer composition over long methods where possible.
- Format JS/Vue via Prettier; fix lint warnings instead of suppressing unless justified.

## Testing Guidelines
- Frontend interactions are currently verified manually: upload, trim, merge, and render flows against the running Flask API. When adding features, document manual test steps in PRs and add automated coverage if feasible.
- Use small sample clips in `clips/` during local testing; avoid committing media.

## Commit & Pull Request Practices
- Commit messages follow the existing short, imperative style (`improve layout`, `update scripts`). Group related changes; avoid mixed frontend/backend refactors in a single commit when possible.
- Pull requests should include: concise summary, linked issue (if any), affected areas (backend, frontend, assets), manual test notes or screenshots for UI changes, and any API contract updates. Mention breaking changes or new config/env needs explicitly.

## Security & Configuration Tips
- Keep `backend/config.py` minimal and non-secret; externalize secrets via environment variables if introduced. Validate user uploads server-side when expanding upload logic, and clean up temp files in `clips/` for long runs.
