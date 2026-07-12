# ADR-004: PostgreSQL, RabbitMQ, Redis, MinIO, and Git for state and transport

**Status:** Accepted · **Date:** 2026-07-10 · **Deciders:** Codex + user approval

## Context

The platform needs a durable system of record, a durable job/result transport, a lightweight lease
store, secure secret storage, and a durable artifact store. The design also needs an immutable
transition log so audit, notifications, and cost rollup can all read the same history.

## Decision

Use PostgreSQL 18.4 as the system of record, RabbitMQ 4.3.2 as the job and result broker, Redis
8.8 for leases and ephemeral coordination, MinIO for secret blobs, Git/GitHub for artifacts, and an
append-only `StateTransition` log in PostgreSQL as the audit spine.

## Alternatives considered

- Redis Streams as the primary broker was rejected because RabbitMQ gives the platform a clearer
  durable queue model and cleaner separation of job and result messages.
- A queue-only architecture without a transition log was rejected because audit and observability
  need immutable state history.
- Storing secrets in plain database rows was rejected because the PRD explicitly requires secure
  secret handling.

## Consequences

- The architecture gets a clean separation between durable domain state and ephemeral orchestration
  plumbing.
- Audit, notifications, and reporting can all subscribe to the same append-only history.
- The product can later swap execution runtime without changing the state model.

