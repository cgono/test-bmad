# test-bmad

Baseline monorepo for Story 1.1 using FastAPI backend and Vite + React frontend.

## Prerequisites

- Python 3.12+
- Node.js 24+
- npm 11+

## Local Startup (without Docker)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and posts to `POST /v1/process`.

## Docker Compose Startup

```bash
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Tests

### Backend smoke tests

```bash
cd backend
pytest
```

### Frontend smoke tests

```bash
cd frontend
npm test
```

## CI Quality Gates

CI runs on pull requests and pushes to `main` with three required checks:

- `backend-checks` (Ruff + backend pytest suite)
- `frontend-checks` (ESLint + frontend Vitest suite)
- `contract-checks` (`/v1/process` response envelope contract tests)

Use these exact job names in branch protection rules so merges are blocked when any quality gate fails.
