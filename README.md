# BheemBhai

BheemBhai is a governed workflow orchestration platform for reusable agent skills across the
software delivery lifecycle.

## Stack

- Python 3.13.14
- FastAPI 0.139.0
- Jinja2 3.1.6
- Bootstrap 5.3.8
- PostgreSQL 18.4
- RabbitMQ 4.3.2
- Redis OSS 8.8
- MinIO

## Prerequisites

- Docker and Docker Compose
- `uv` 0.11.19
- Python 3.13
- Playwright browser binaries for the e2e test: `uv run playwright install chromium`

## Install

```bash
uv sync --group dev
uv run playwright install chromium
```

## Run

```bash
uv run beembhai-api
```

or start the full local stack:

```bash
./scripts/dev-up.sh
```

The compose stack reads sensitive values from `.env`. If you are setting up a fresh checkout,
start by copying `.env.example` to `.env` and filling in the secrets there.
For a fuller description of the variables, see [docs/environment.md](/home/fusiongamingmasterpc/projects/beembhai/development/codebase/bheembhai/docs/environment.md).

To stop the stack:

```bash
./scripts/dev-down.sh
```

To force a rebuild and recreate containers:

```bash
./scripts/dev-rebuild.sh
```

Then open:

- `http://localhost:8000/` for the walking-skeleton page
- `http://localhost:8000/api/v1/health` for the versioned API health endpoint
- `http://localhost:8000/health` for the unversioned container health check

## Test

```bash
uv run ruff check .
uv run pytest
```

## Develop

- Keep feature work inside the existing `app/<module>/` homes.
- Write failing tests first, then implement the smallest change that makes them pass.
- Follow the repo layout in `AGENTS.md` for all docs and artifact paths.
- Claude Code can load the repo skills from `.claude/skills`, which is a symlink to `.agents/skills`.
- `AGENTS.md` is the repo-specific instruction file for Codex and other repo-aware agents.

## Branching and PRs

- Branch format: `feat/BB-21-short-slug`
- Use `.github/PULL_REQUEST_TEMPLATE.md`

## Architecture

See `docs/architecture.md` and `docs/adr/`.
