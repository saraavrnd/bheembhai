# ADR-005: Integration provider registry and Brevo email plugin

**Status:** Accepted · **Date:** 2026-07-10 · **Deciders:** Codex + user approval

## Context

The PRD requires pluggable providers by category and secure credential handling. Project setup must
support GitHub and Jira, and email notifications must be available at MVP time. The platform should
not hardcode provider names into workflow logic.

## Decision

Model integrations with a provider registry and project binding layer. Use a plugin-based email
adapter, with Brevo 5.0.1 as the first implementation and the API key supplied via environment
variable and secure storage references.

## Alternatives considered

- Hardcoding GitHub, Jira, and Brevo into workflow code was rejected because it would make later
  provider expansion painful.
- Generic SMTP only was rejected because the user explicitly wants Brevo first and the product needs
  a concrete notification integration.
- A provider-specific email path without a plugin boundary was rejected because it would not satisfy
  the PRD's replaceable-seams goal.

## Consequences

- The platform can support new providers inside an existing integration category without changing
  workflows.
- Brevo is the first concrete email integration while the boundary stays swappable.
- Secure credential handling becomes a first-class concern of the integration layer, not an afterthought.

