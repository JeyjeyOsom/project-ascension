# Project Ascension

Project Ascension is a production-inspired full-stack platform built to explore modern software architecture, backend engineering, cloud-native development, and AI-powered systems.

The project is intentionally developed using professional engineering practices including sprint planning, architecture decision records, documentation-first development, testing, and CI/CD.

## Goals

- Build production-quality software
- Learn modern backend architecture
- Master scalable API development
- Implement authentication and authorization
- Build AI-powered features
- Deploy using cloud-native infrastructure
- Practice real software engineering workflows

---

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS

### Backend

- FastAPI
- Python
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis

### Infrastructure

- Docker
- Docker Compose
- GitHub Actions

## Run with Docker Compose

Copy `.env.example` to `.env` and replace the development secrets, then start
the complete stack:

```bash
docker compose up --build
```

The web app is available at `http://localhost:3000`, the API at
`http://localhost:8000`, and the API documentation at
`http://localhost:8000/docs`. The API waits for PostgreSQL, runs Alembic
migrations at startup, and the web service waits for the API health check.

Use `docker compose down` to stop the stack while retaining database data, or
`docker compose down -v` to remove the local service volumes.

### Authentication

- JWT
- Refresh Tokens

### Future

- OpenAI
- LangGraph
- Background Workers
- Event-driven Architecture

---

## Repository Structure

```
project-ascension
│
├── apps
│   ├── web
│   └── api
│
├── docs
│
├── infrastructure
│
├── scripts
│
└── README.md
```

---

## Current Sprint

Sprint 1

- Authentication
- Organizations
- Health Endpoint
- Docker Development Environment

---

## Long-Term Vision

Project Ascension will evolve into an AI-first business platform capable of managing organizations, users, documents, workflows, automation, and intelligent agents.

The project emphasizes maintainability, scalability, observability, and security while following modern engineering practices.
