# Contributing

## Branch Naming

feature/<name>

bugfix/<name>

hotfix/<name>

refactor/<name>

---

## Commit Messages

feat:

fix:

docs:

test:

refactor:

chore:

---

## Pull Requests

Every PR should include:

- Description
- Testing performed
- Screenshots (if UI)
- Related issue

---

## Coding Standards

- Use type hints
- Keep functions small
- Write meaningful names
- Add tests when appropriate
- Prefer composition over inheritance
- Keep documentation updated

## Quality Checks

Install API development dependencies before running Python checks:

```bash
python -m pip install -r apps/api/requirements-dev.txt
```

Start the API and its Swagger UI from the repository root:

```bash
npm run dev:infra
npm run dev:api
```

Then open `http://127.0.0.1:8000/docs`. If running the command from `apps/`
directly, use `uv run --with-requirements api/requirements.txt fastapi dev api/main.py`.
The API runs migrations on startup, so PostgreSQL must be healthy first when
`POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are configured in `.env`.

Run the full local quality gate from the repository root:

```bash
npm run lint
npm run format:check
npm run check-types
npm run test:api
```

Use `npm run format` to apply Prettier and Black formatting. Pull requests must
pass the same checks in GitHub Actions.
