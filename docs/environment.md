# Environment Files

This repository uses two env files for local development:

- `.env.example` is the checked-in template.
- `.env` is your local, secret-bearing copy.

## How they are used

- `docker compose` reads the service credentials and runtime settings from `.env`.
- The application also reads its configuration from environment variables.
- `.env.example` documents the available variables and the intended defaults or placeholders.

## What belongs where

- Keep non-secret reference values in `.env.example`.
- Put real passwords, tokens, and API keys in `.env`.
- Never commit `.env`.

## Variable groups

The template groups variables into a few areas:

- Application identity and runtime mode.
- Postgres credentials.
- Internal service URLs for the app, worker, and supporting services.
- MinIO root credentials and secure-storage settings.
- Langfuse self-hosting and runtime tracing settings.
- Brevo email provider settings.

## Local setup

1. Copy `.env.example` to `.env`.
2. Replace every `change-me` value with a real local secret.
3. Keep the same variable names so Docker Compose and the app can resolve them.

## Notes

- The comments inside `.env.example` explain each block in place.
- The compose stack is intended to run against the local `.env` file, not the template.
- Langfuse uses `LANGFUSE_BASE_URL`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY` for
  runtime tracing. In the Docker stack, the base URL points at `http://langfuse-web:3000` so
  containerized runtimes can reach it; host-side tools can override that to `http://localhost:3000`.
- The `LANGFUSE_INIT_*` values seed the local self-hosted instance.
