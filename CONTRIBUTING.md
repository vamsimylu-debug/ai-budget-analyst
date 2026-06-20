# Contributing to AI Budget Analyst

Thank you for contributing! This repository is a demo full-stack project with Django backend, Next.js frontend, and Playwright E2E tests.

## Local setup
1. Copy `.env.example` to `.env`.
2. Run the app locally:
   ```bash
   docker compose up
   ```
3. Open `http://localhost:3000`.

## Running tests
- Backend tests:
  ```bash
  docker compose run --rm backend python manage.py test
  ```
- Frontend E2E tests:
  ```bash
  cd frontend
  npm install
  npx playwright install --with-deps
  APP_URL=http://localhost:3000 npm run test:e2e
  ```

## Suggested workflow
1. Create a new branch.
2. Make changes and add tests.
3. Run unit and E2E tests locally.
4. Open a pull request with a clear description.

## Notes
- The backend can fallback to deterministic analysis when `OPENAI_API_KEY` is not set.
- The repo uses `docker compose` for local development and a GitHub Actions workflow for CI.