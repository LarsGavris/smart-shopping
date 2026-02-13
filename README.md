# Smart Shopping Monorepo

This repository is initialized as a monorepo with a Python FastAPI backend and a Next.js frontend.

## Structure

- `backend/`: API service + worker with domain modules:
  - `sources/` supermarket connectors.
  - `extract/` normalization and parsing.
  - `offers/` API and business logic.
  - `alerts/` reminder logic.
- `frontend/`: Next.js application with routes:
  - `/offers`
  - `/products/:id` (implemented as `/products/[id]`)
  - `/alerts`
- `docker-compose.yml`: local orchestration for API, DB, worker, and frontend.

## Environment configuration

1. Copy `.env.example` to `.env`.
2. Edit values as required for your machine.

```bash
cp .env.example .env
```

### Key variables

- `DATABASE_URL`: backend database connection string.
- `NEXT_PUBLIC_API_URL`: frontend base URL for API requests.
- `API_PORT`, `FRONTEND_PORT`, `POSTGRES_PORT`: host-exposed ports.

## Local development

```bash
docker compose up --build
```

Service endpoints:
- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Postgres: `localhost:5432`

## Backend quick start (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend quick start (without Docker)

```bash
cd frontend
npm install
npm run dev
```
