# Tech Stack

**Status:** Approved · **Date:** 2026-07-10

This is the pinned stack for the MVP. The goal is not novelty; it is a reliable, small surface area
that matches the PRD and keeps the seams open for later changes.

## Runtime

| Component | Version | Why it is here |
|-----------|---------|----------------|
| Python | 3.13.14 | Primary application runtime for API, worker, and executor code. |
| FastAPI | 0.139.0 | API framework with typed contracts and OpenAPI generation. |
| Uvicorn | 0.51.0 | ASGI server for the API process. |
| SQLAlchemy | 2.0.51 | ORM and transaction handling for the relational core. |
| Alembic | 1.18.5 | Schema migration tool. |
| Pydantic | 2.13.4 | Request, response, and internal schema validation. |
| Jinja2 | 3.1.6 | Server-rendered HTML templates. |
| Bootstrap | 5.3.8 | UI system for forms, dashboards, and approval screens. |
| aio-pika | 10.0.1 | Async RabbitMQ client for job and result message handling. |
| RabbitMQ | 4.3.2 | Durable broker for orchestration jobs and result transport. |
| redis-py | 8.0.1 | Redis client for leases and ephemeral coordination. |
| Redis OSS | 8.8 | Lease and coordination store. |
| PostgreSQL | 18.4 | Source of truth for product state and audit history. |
| MinIO | RELEASE.2025-09-07T16-13-09Z | Secure blob storage for secrets and sensitive runtime payloads. |
| minio | 7.2.20 | Python client for the MinIO secure-storage adapter. |
| cryptography | 49.0.0 | Envelope encryption for secrets before they are written to MinIO. |
| git | system tool | Artifact persistence and branch/commit operations. |

## Product integrations

| Component | Version | Why it is here |
|-----------|---------|----------------|
| LiteLLM | 1.91.1 | Mandatory model proxy and cost metering seam. |
| Langfuse | v3 stable line | Tracing and run observability. |
| brevo-python | 5.0.1 | First email notification integration behind a plugin interface. |
| Atlassian Jira | API-based integration | Project setup and source issue linkage. |
| GitHub | API-based integration | Repository linkage, branches, commits, and PR creation. |

## Security and auth

| Component | Version | Why it is here |
|-----------|---------|----------------|
| argon2-cffi | 25.1.0 | Password hashing. |
| itsdangerous | 2.2.0 | Signed verification and password reset tokens. |

## Testing

| Component | Version | Why it is here |
|-----------|---------|----------------|
| pytest | 9.1.1 | Unit and integration test runner. |
| pytest-asyncio | 1.4.0 | Async test support. |
| Playwright | 1.61.0 | Browser automation for UI flows. |
| pytest-playwright | 0.8.0 | Test runner bridge for browser automation. |

## Deployment

- Local-first `docker compose` runs the API, worker, Postgres, RabbitMQ, Redis, MinIO, LiteLLM,
  Langfuse, and a mail sink or Brevo stub.
- The same containers can move to a single VM or Kubernetes later without changing the app's
  domain logic.
- The custom Bootstrap theme is part of the repository theme assets and is layered on top of the
  Bootstrap base package rather than replacing it.

## Notes

- The stack intentionally avoids a SPA build chain for the MVP.
- The email provider is plugin-based. Brevo is the first implementation, but the interface is
  provider-agnostic.
- The queueing model is RabbitMQ, not Redis Streams or Celery.
- Provider secrets are encrypted in the application before they are stored in MinIO and decrypted
  only when read back by the secure-storage adapter.
