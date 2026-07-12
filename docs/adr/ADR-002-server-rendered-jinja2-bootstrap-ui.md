# ADR-002: Server-rendered Jinja2 and Bootstrap for the MVP UI

**Status:** Accepted · **Date:** 2026-07-10 · **Deciders:** Codex + user approval

## Context

The MVP UI needs to support forms, lists, run inspection, approval actions, and a few status
states. It does not need a client-heavy SPA, but it does need to stay consistent across dashboard,
approval, and configuration screens.

## Decision

Use server-rendered Jinja2 templates with Bootstrap 5.3.8 and minimal vanilla JavaScript, layered on
top of the custom theme asset already available to the project.

## Alternatives considered

- React SPA was rejected because the MVP does not need a separate frontend application or build
  pipeline.
- HTMX was rejected for the MVP because the platform already has enough moving parts and plain
  server rendering is sufficient.
- A design-system-first frontend was rejected because the product needs a thin baseline now, not a
  large component library.

## Consequences

- The UI stays simple to run and easy to keep consistent.
- Server-side templates can reuse the same auth/session and permission checks as the API.
- Rich client-side interactions will need to stay small and deliberate until the product earns a
  larger frontend stack.

