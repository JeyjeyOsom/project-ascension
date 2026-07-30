# Architecture Decision Records

---

# ADR-001

## Title

Use FastAPI for Backend

### Status

Accepted

### Context

The project requires a modern backend framework that is performant, asynchronous, easy to document, and suitable for AI integrations.

### Decision

Use FastAPI.

### Consequences

Pros

- Automatic OpenAPI
- Excellent performance
- Strong typing
- Modern async support

Cons

- Smaller ecosystem than Django

---

# ADR-002

## Title

Use React for Frontend

### Status

Accepted

### Context

A modern SPA is required.

### Decision

React with TypeScript.

---

# ADR-003

## Title

PostgreSQL as Primary Database

### Status

Accepted

### Decision

Use PostgreSQL because it is reliable, scalable, and supports advanced indexing and JSON capabilities.

---

# ADR-004

## Title

Docker for Development

### Status

Accepted

### Decision

All local development should run through Docker Compose to ensure environment consistency.
