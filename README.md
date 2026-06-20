# AI Budget Analyst

A small full-stack budget review workspace with a Django REST backend, a Next.js frontend, and an AI assistant that analyzes saved budget scenarios.

## What I built
- Budget scenario and line item CRUD with Django REST Framework
- AI assistant chat interface backed by a scenario-aware backend workflow
- SSE-based stream from backend to frontend for chat responses
- Interactive result rendering with tables and summary cards
- Demo seed data for immediate review

## Run locally
1. Copy `.env.example` to `.env` and set a real `OPENAI_API_KEY` if you want OpenAI-backed answers.
2. From the project root run:
   ```bash
   docker compose up
   ```
3. Open `http://localhost:3000`

The backend seeds demo data automatically when it starts if no scenarios are present.

If you encounter stale Next.js manifest or runtime client manifest errors, run:

```bash
cd frontend
npm run clean
npm run dev
```

## Required environment variables
- `OPENAI_API_KEY` (optional) — if omitted, the app falls back to deterministic scenario analysis so the assistant still works for demo queries.
- `DJANGO_SECRET_KEY` — optional; defaults are provided for local development.

## Demo chat query
Use this exact query in the AI chat input or curl to reproduce the high-risk grouping example used in tests:

Paid Ads Travel 15000 7500 High Medium Group this by department and show only high-risk items

## Run tests

### Backend unit tests
From the project root:

```bash
docker compose run --rm backend python manage.py test
```

### Frontend E2E tests
From `frontend/` after `npm install` and `npx playwright install --with-deps`:

```bash
APP_URL=http://localhost:3000 npm run test:e2e
```

If port `3000` is already in use, start the frontend on a different port and update `APP_URL` accordingly.

The suite includes a lightweight API-level SSE test that validates the grouping and high-risk filtering.

## GitHub Actions CI
A GitHub Actions workflow is included to run backend Django tests and frontend Playwright E2E tests on push and pull requests.

## Architecture and trade-offs
- Backend: Django + DRF, SQLite, simple budget line model, SSE chat endpoint.
- Frontend: Next.js + TypeScript, one page with scenario management and assistant chat.
- AI: OpenAI ChatCompletion is used when an API key is available; otherwise, the backend falls back to deterministic data-driven results.

## Assumptions / limitations
- No authentication or multi-user handling.
- Chat history is kept only in frontend state; not persisted.
- The assistant is scenario-scoped and uses a combination of structured analysis plus LLM prompt context.

## What I would improve with more time
- Add per-turn session persistence and conversation breadcrumbs.
- Support richer chart widgets and drag-to-adjust budget scenarios.
- Add better validation and inline editing for line items.
- Add production-ready static build and nginx proxy.
