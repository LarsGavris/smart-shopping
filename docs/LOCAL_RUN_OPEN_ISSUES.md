# Open Issues: Getting Smart Shopping Running Locally

This backlog lists concrete issues to open/track so local development is reliable.

## 1) Frontend should respect `NEXT_PUBLIC_API_URL` instead of hardcoding localhost

- **Problem**: `frontend/src/api.ts` hardcodes `API_BASE = "http://localhost:8000"`, while `.env.example` and Docker Compose define `NEXT_PUBLIC_API_URL` as the intended configuration knob.
- **Impact**: Running frontend and API on non-default ports/hosts (or inside containers) requires source edits.
- **Suggested issue title**: `frontend: use NEXT_PUBLIC_API_URL for API base URL`
- **Acceptance criteria**:
  - `frontend/src/api.ts` reads base URL from `process.env.NEXT_PUBLIC_API_URL` with a safe fallback.
  - README documents frontend API URL behavior for local and Docker usage.

## 2) Remove or consolidate duplicate backend API entrypoints

- **Problem**: There are two backend entrypoint paths with different behavior (`backend/app/main.py` and `backend/main.py`), and one imports an alternate router stack (`backend.offers.api`).
- **Impact**: Local startup path is ambiguous and can lead to different API surfaces depending on command used.
- **Suggested issue title**: `backend: consolidate API entrypoint and router wiring`
- **Acceptance criteria**:
  - A single documented FastAPI entrypoint is used across README, Dockerfile, and local commands.
  - Deprecated/duplicate entrypoint is removed or clearly marked as legacy.

## 3) Align frontend routes with implemented offer/alerts/product flows

- **Problem**: App routes (`/offers`, `/alerts`, `/products/[id]`) are currently placeholders in `frontend/app/**/page.tsx`, while richer offer/history/alert functionality exists in `frontend/src/App.tsx` but is not wired into routes.
- **Impact**: Running locally shows static pages instead of expected interactive flows.
- **Suggested issue title**: `frontend: wire offers/alerts/product pages to live API flows`
- **Acceptance criteria**:
  - Route pages fetch and render live data from API.
  - Alerts creation and product history are reachable from route-driven UI.

## 4) Add deterministic dependency lockfiles for local reproducibility

- **Problem**: Frontend has no committed npm lockfile, and backend has only top-level pins without a generated lock/constraints workflow.
- **Impact**: Local setup can diverge across environments and over time.
- **Suggested issue title**: `devx: add lockfile strategy for frontend/backend dependencies`
- **Acceptance criteria**:
  - Frontend lockfile is committed (npm/yarn/pnpm, whichever is standard for the repo).
  - Backend dependency locking approach is documented (e.g., constraints or lock generation step).

## 5) Add a one-command local verification checklist

- **Problem**: README provides startup commands but no explicit verification sequence (health endpoint, sample API call, and frontend route checks).
- **Impact**: Contributors cannot quickly determine if local setup succeeded.
- **Suggested issue title**: `docs: add local run verification checklist`
- **Acceptance criteria**:
  - README includes a minimal smoke-test section with copy-paste commands and expected outputs.
  - Includes at least API health, offers endpoint, and frontend URL checks.
