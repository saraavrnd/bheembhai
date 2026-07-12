# ADR-003: Modular monolith with separate API, worker, and executor processes

**Status:** Accepted · **Date:** 2026-07-10 · **Deciders:** Codex + user approval

## Context

The PRD requires backend-owned orchestration, isolated execution, resumable runs, and clear seams
for later runtime changes. The product is still an MVP, so a service mesh or many independent
services would be too much operational cost.

## Decision

Build a modular monolith in one repository, but run it as separate API, worker, and executor
processes. Keep the internal feature boundaries explicit so they can later split if needed.

## Alternatives considered

- Microservices were rejected because the MVP does not need distributed system overhead.
- A single-process monolith was rejected because the worker and executor responsibilities should
  not be tangled with the HTTP request path.
- A multi-repo architecture was rejected because it adds coordination overhead without helping the
  MVP.

## Consequences

- The product keeps a simple deployment story while preserving clear seams for scale later.
- The API can remain fast and non-blocking while the worker handles orchestration work.
- The executor remains disposable and isolated, which matches the PRD's reliability goals.

