# Story 3.5: Deploy Frontend and Backend to Render

Status: review

## Story

As Clint,
I want the frontend and backend deployed to Render,
So that the project runs on its chosen hosted platform with a repeatable production setup.

## Acceptance Criteria

1. **Given** the repository is connected to Render, **When** deployment configuration is applied, **Then** the frontend is served from a Render static site **And** the backend runs as a Render web service with required environment variables configured.

2. **Given** the hosted services are deployed, **When** I open the production app, **Then** the frontend can call the backend successfully over HTTPS **And** health checks and basic rollback/redeploy steps are documented.

## Tasks / Subtasks

- [x] Create `render.yaml` Blueprint at repository root (AC: 1)
  - [x] Define backend as a `web` service with Python runtime, `rootDir: backend`, build command, and start command
  - [x] Configure `healthCheckPath: /v1/health` on the backend service
  - [x] Set non-secret env vars directly in `render.yaml` (`APP_ENV`, `APP_VERSION`, `OCR_PROVIDER`); mark secrets `sync: false`
  - [x] Define frontend as a `web` service with `runtime: static`, `rootDir: frontend`, build command, and `staticPublishPath: dist`
  - [x] Add SPA rewrite rule on frontend (`/* → /index.html`)
  - [x] Mark `VITE_API_BASE_URL` and `VITE_SENTRY_DSN` as `sync: false` (must be set in Render dashboard)

- [x] Update `backend/.env.example` — document `CORS_ALLOW_ORIGINS` (AC: 1, 2)
  - [x] Add `CORS_ALLOW_ORIGINS=` with a comment explaining it must be set to the Render frontend URL in production

- [x] Create `docs/deployment.md` — Render deployment and operational runbook (AC: 2)
  - [x] Document the one-time Render setup steps (connect repo, set dashboard env vars)
  - [x] List all environment variables required in the Render dashboard per service
  - [x] Document how to verify the deployment (health check URL, smoke test)
  - [x] Document how to redeploy (git push to main auto-deploys)
  - [x] Document how to roll back (Render dashboard → service → "Deploys" tab → "Redeploy" on a prior successful deploy)

- [x] Verify all backend tests pass (`cd backend && uv run python -m pytest`) — no regressions
- [x] Verify all frontend tests pass (`cd frontend && npm test`) — no regressions

## Dev Notes

### Story Foundation

- **Epic goal**: Epic 3 closes with Story 3-5 shipping the deployment configuration that puts the fully-instrumented app (Sentry from 3-4, health/metrics from 3-3) onto the chosen hosted platform.
- **FRs covered**: Operational requirement for hosted production access (from sprint-change-proposal-2026-03-26, which added this story).
- **Architecture decision**: Render Blueprint (`render.yaml`) at repo root is the explicit architecture direction — see `_bmad-output/planning-artifacts/architecture.md#Infrastructure-Deployment`.
- **No new Python or JS logic** — this story is infrastructure configuration only.

### Current State — What Exists

**No Dockerfile** for either service. Render's native Python and static runtimes do not require a Dockerfile.

**No `render.yaml`** — this is the primary deliverable.

**`backend/app/main.py`** — CORS origins are already env-var driven via `CORS_ALLOW_ORIGINS`:
```python
def _get_cors_origins() -> list[str]:
    configured = os.getenv("CORS_ALLOW_ORIGINS")
    if configured:
        parsed = [origin.strip() for origin in configured.split(",") if origin.strip()]
        if parsed:
            return parsed
    return ["http://localhost:5173", "http://127.0.0.1:5173"]
```
Set `CORS_ALLOW_ORIGINS=https://<frontend>.onrender.com` in the backend Render dashboard. No code change needed.

**`frontend/src/lib/api-client.js`** — API base URL is already env-var driven:
```js
const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
```
Empty string = relative URL (works with Vite dev proxy, breaks in production where frontend and backend are separate Render services). Set `VITE_API_BASE_URL=https://<backend>.onrender.com` in the frontend Render dashboard. No code change needed.

**`backend/app/api/v1/health.py`** — returns `{"status": "healthy"}` at `GET /v1/health`. Already implemented in story 3-3. Used as Render's health check path.

**`backend/app/adapters/google_cloud_vision_ocr_provider.py`** — reads `GOOGLE_APPLICATION_CREDENTIALS_JSON` as a JSON string directly from the environment. Render environment variables can hold a multi-line JSON value — paste the full service account JSON as a single-line string. The adapter already handles quotes/whitespace normalization.

**Test baseline**: 108 backend tests, 38 frontend tests (both must remain green).

**Package manager**: `uv` — build command must install it first since Render's Python image has `pip` but not `uv`.

### New File: `render.yaml`

```yaml
services:
  - type: web
    name: ocr-pinyin-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install uv && uv sync --no-dev --frozen
    startCommand: uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /v1/health
    envVars:
      - key: APP_ENV
        value: production
      - key: APP_VERSION
        value: 0.1.0
      - key: OCR_PROVIDER
        value: google_vision
      - key: SENTRY_DSN
        sync: false
      - key: SENTRY_TRACES_SAMPLE_RATE
        value: "0.2"
      - key: GOOGLE_APPLICATION_CREDENTIALS_JSON
        sync: false
      - key: CORS_ALLOW_ORIGINS
        sync: false

  - type: web
    name: ocr-pinyin-frontend
    runtime: static
    rootDir: frontend
    buildCommand: npm install && npm run build
    staticPublishPath: dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_APP_ENV
        value: production
      - key: VITE_APP_VERSION
        value: 0.1.0
      - key: VITE_API_BASE_URL
        sync: false
      - key: VITE_SENTRY_DSN
        sync: false
      - key: VITE_SENTRY_TRACES_SAMPLE_RATE
        value: "0.2"
```

Key notes:
- `sync: false` — Render Dashboard property meaning "this value is NOT in source control; operator must set it manually in the Render dashboard". This is how secrets are handled in Render Blueprints.
- `SENTRY_TRACES_SAMPLE_RATE: "0.2"` — intentionally lowered from dev default (1.0) for production to reduce Sentry quota usage.
- `$PORT` — Render automatically injects the `PORT` env var for web services. The start command must bind to it.
- `healthCheckPath: /v1/health` — Render will GET this path to determine if the service is healthy. Returns HTTP 200 with `{"status": "healthy"}`.
- `rootDir` — tells Render where the service lives in the monorepo. Build and start commands run from that directory.
- The SPA rewrite rule (`/* → /index.html`) ensures React routing works if React Router is added later. Safe to include now even though the app doesn't use client-side routing yet.

### Updated `backend/.env.example`

Add after the existing `APP_ENV=development` line:
```
# Production CORS: set to the Render frontend URL (comma-separated for multiple origins)
# Example: CORS_ALLOW_ORIGINS=https://ocr-pinyin-frontend.onrender.com
CORS_ALLOW_ORIGINS=
```

### New File: `docs/deployment.md`

Create `docs/deployment.md` with the following content:

```markdown
# Deployment Guide — Render

This project deploys to Render using a Blueprint (`render.yaml` at repository root).

## One-Time Setup

### 1. Connect Repository

1. Log in to [render.com](https://render.com) and create a new **Blueprint** service.
2. Connect your GitHub repository.
3. Render will detect `render.yaml` and propose creating both services.

### 2. Set Dashboard Environment Variables

After Render creates the services, set the following secrets in each service's **Environment** tab.

#### Backend (`ocr-pinyin-backend`)

| Variable | Where to get it |
|---|---|
| `SENTRY_DSN` | Sentry project → Settings → Client Keys |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | GCP Console → IAM → Service Accounts → your key → JSON (paste as a single line) |
| `CORS_ALLOW_ORIGINS` | Set to `https://<frontend-service-name>.onrender.com` after frontend is deployed |

#### Frontend (`ocr-pinyin-frontend`)

| Variable | Where to get it |
|---|---|
| `VITE_API_BASE_URL` | Set to `https://<backend-service-name>.onrender.com` after backend is deployed |
| `VITE_SENTRY_DSN` | Same Sentry project DSN as backend (or a separate frontend project) |

> **Note:** `VITE_*` env vars are baked into the frontend bundle at **build time**. After setting them, trigger a manual redeploy of the frontend service so Vite picks them up.

### 3. Verify CORS Wiring

The backend `CORS_ALLOW_ORIGINS` must match the exact frontend origin (scheme + host, no trailing slash):
```
CORS_ALLOW_ORIGINS=https://ocr-pinyin-frontend.onrender.com
```

If the frontend URL changes, update this value and redeploy the backend.

## Verify the Deployment

1. **Backend health**: `GET https://<backend>.onrender.com/v1/health` → `{"status": "healthy"}`
2. **Frontend loads**: Open `https://<frontend>.onrender.com` in a browser — upload form should render.
3. **End-to-end**: Submit a test image — result should return pinyin output without CORS errors.

## Redeploy

Render auto-deploys on every push to the connected branch (usually `main`).

To trigger a manual redeploy without a code push: Render Dashboard → service → **Manual Deploy** → **Deploy latest commit**.

## Rollback

1. Open the service in the Render Dashboard.
2. Go to the **Deploys** tab.
3. Find the last successful deploy (green checkmark).
4. Click **⋯** → **Redeploy** to restore that version.

Rollback takes effect immediately — no code revert is required.
```

### File Structure Requirements

**New files:**
- `render.yaml` (repository root)
- `docs/deployment.md`

**Modified files:**
- `backend/.env.example` — add `CORS_ALLOW_ORIGINS` with production guidance comment

**Files NOT to touch:**
- `backend/app/main.py` — CORS is already env-var driven; no code change needed
- `frontend/src/lib/api-client.js` — `VITE_API_BASE_URL` is already env-var driven; no code change needed
- `frontend/vite.config.js` — proxy config is dev-only; Vite doesn't use it for production builds
- All test files — no new tests required for config-only changes
- `docker-compose.yml` — local dev stack is unchanged

### Architecture Compliance

- **No new API endpoints** — pure infrastructure story
- **`render.yaml` at repo root** — matches architecture decision in `_bmad-output/planning-artifacts/architecture.md#Infrastructure-Deployment`
- **Sentry DSN as dashboard secret** (`sync: false`) — matches NFR5 (secrets managed outside source code)
- **Health check at `/v1/health`** — already implemented in story 3-3; used as Render's liveness check
- **`SENTRY_TRACES_SAMPLE_RATE: "0.2"` in production** — production traffic doesn't need 100% transaction sampling; 20% is sufficient for a personal-use app and reduces Sentry quota consumption

### Previous Story Intelligence (3-4 → 3-5)

- **108 backend tests, 38 frontend tests** — run both before marking done to confirm no regressions from any accidental file edits.
- **`backend/.env.example`** already has `APP_ENV`, `APP_VERSION`, `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`, `GOOGLE_APPLICATION_CREDENTIALS_JSON`, `OCR_PROVIDER`. Only `CORS_ALLOW_ORIGINS` is missing.
- **`frontend/.env.example`** already has `VITE_API_BASE_URL=`, `VITE_SENTRY_DSN=`, `VITE_APP_ENV`, `VITE_APP_VERSION`, `VITE_SENTRY_TRACES_SAMPLE_RATE`. No changes needed.
- **No Dockerfile exists** — don't create one. Render's native runtimes are correct for this project.
- **`uv` is the package manager** (not `pip` directly). The build command must install `uv` first: `pip install uv && uv sync --no-dev --frozen`. `--frozen` ensures the exact versions from `uv.lock` are used in production.

### Git Intelligence

- `f8e1203` (current HEAD): Story 3-4 — Sentry added to backend and frontend.
- `25d7d6e`: Story 3-3 — health/metrics endpoints live at `/v1/health` and `/v1/metrics`.
- `674f74a`: Course correction — explicitly approved Render + Sentry as the operational stack.
- Commit convention: `feat: story 3-5 — deploy frontend and backend to Render`

### References

- [Source: _bmad-output/planning-artifacts/sprint-change-proposal-2026-03-26.md — Render deployment confirmed as Epic 3 story]
- [Source: _bmad-output/planning-artifacts/architecture.md#Infrastructure-Deployment — Render Blueprint as deployment config direction]
- [Source: backend/app/main.py — CORS already env-var driven via CORS_ALLOW_ORIGINS]
- [Source: frontend/src/lib/api-client.js — VITE_API_BASE_URL already used as API base; empty = relative URL]
- [Source: backend/app/api/v1/health.py — health check returns {status: "healthy"} at /v1/health]
- [Source: backend/app/adapters/google_cloud_vision_ocr_provider.py — GOOGLE_APPLICATION_CREDENTIALS_JSON read as inline JSON string]
- [Source: backend/.env.example — current env vars; CORS_ALLOW_ORIGINS is missing]
- [Source: frontend/.env.example — VITE_API_BASE_URL already present but blank; no changes needed]
- [Source: backend/pyproject.toml — uv is the package manager; uv.lock pins all dependency versions]

## Dev Agent Record

### Agent Model Used

gpt-5

### Implementation Plan

- Add the Render Blueprint at the repository root for backend and frontend services.
- Update the backend environment example with production CORS guidance for the Render frontend URL.
- Add a deployment runbook covering setup, required dashboard variables, verification, redeploy, and rollback.
- Run backend and frontend regression tests before checking off the story tasks.

### Debug Log References

- Added `render.yaml` Blueprint with backend and frontend Render service definitions.
- Added `docs/deployment.md` and updated `backend/.env.example` with production CORS guidance.
- Ran backend validation with `.venv/bin/python -m pytest` and `.venv/bin/ruff check .` because `uv` was not on the shell `PATH`.
- Removed one pre-existing unused import in `backend/tests/unit/core/test_sentry.py` so the configured backend lint gate passed.

### Completion Notes List

- Implemented the repository root Render Blueprint for the backend web service and frontend static site, including health checks, static publish settings, SPA rewrites, and dashboard-managed secrets.
- Documented `CORS_ALLOW_ORIGINS` usage in `backend/.env.example` for the Render frontend origin in production.
- Added `docs/deployment.md` covering one-time Render setup, required dashboard environment variables, deployment verification, redeploy, and rollback steps.
- Verified backend regressions with `.venv/bin/python -m pytest` (`108 passed`) and frontend regressions with `npm test` (`38 passed`).
- Verified lint checks with `.venv/bin/ruff check .` and `npm run lint`.

### File List

- _bmad-output/implementation-artifacts/3-5-deploy-frontend-and-backend-to-render.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- render.yaml
- docs/deployment.md
- backend/.env.example
- backend/tests/unit/core/test_sentry.py

### Change Log

- 2026-03-27: Added Render deployment configuration and operational runbook, documented production CORS setup, and completed full regression and lint validation for Story 3.5.
