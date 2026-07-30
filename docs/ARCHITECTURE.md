# Architecture

## Overview

Project Ascension follows a modular architecture that separates concerns between frontend, backend, infrastructure, and documentation.

```
React
      │
      ▼

 REST API

      │

 FastAPI

      │

Service Layer

      │

Repository Layer

      │

PostgreSQL

Redis
```

---

## Principles

- Separation of Concerns
- Single Responsibility
- Dependency Injection
- Domain-driven organization
- API-first development
- Documentation-first development

---

## Backend Layers

Controllers

↓

Services

↓

Repositories

↓

Database

---

## Frontend Layers

Pages

↓

Components

↓

Hooks

↓

API Client

↓

Backend

---

## Authentication

JWT Access Token

Refresh Token

Role-based Authorization

---

## Database

PostgreSQL

Future additions:

- Read replicas
- Full text search
- Audit logs

---

## Infrastructure

Docker

Docker Compose

GitHub Actions

Future

AWS

Terraform

Kubernetes

Redis

S3

CloudFront
