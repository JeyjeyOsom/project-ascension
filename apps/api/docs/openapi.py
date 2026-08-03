from fastapi import FastAPI


def configure_openapi(app: FastAPI) -> FastAPI:
    app.title = "Project Ascension API"
    app.description = "Authentication and organization management endpoints"
    app.version = "0.1.0"
    return app
