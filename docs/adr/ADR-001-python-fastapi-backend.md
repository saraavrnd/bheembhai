# ADR-001: Python and FastAPI for the backend

**Status:** Accepted · **Date:** 2026-07-10 · **Deciders:** Codex + user approval

## Context

The MVP is API-heavy and orchestration-heavy. It needs typed request and response contracts, worker
processes, async I/O, and an OpenAPI surface that downstream tooling can consume. The PRD also
requires replaceable seams for runner, proxy, and runtime integrations.

## Decision

Use Python 3.13.14 with FastAPI 0.139.0 as the backend framework and application runtime.

## Alternatives considered

- Django was rejected because the admin/auth batteries are not enough to offset the extra weight
  for an orchestration-first product.
- Node.js and NestJS were rejected because the existing product shape already fits Python and the
  AI/tooling ecosystem around the platform is strongest there.
- A lower-level ASGI stack was rejected because it would add hand-built contract and routing work
  without improving the MVP.

## Consequences

- The codebase gets typed endpoints, generated OpenAPI, and an easy path for worker-side Python
  orchestration code.
- The platform stays close to the agent and model tooling ecosystem already implied by the PRD.
- FastAPI remains a 0.x framework, so version pinning becomes part of the stack discipline.

