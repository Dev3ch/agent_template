"""Healthcheck estándar para services FastAPI."""
from fastapi import APIRouter

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@health_router.get("/")
def root() -> dict:
    return {"status": "ok", "see": "/docs"}
