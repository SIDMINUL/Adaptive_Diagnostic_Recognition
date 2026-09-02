"""Adaptive Diagnostic Engine — FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.api import router
from app.services.database import close_db, connect_db

app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description=(
        "A one-dimensional adaptive testing system inspired by Item Response Theory "
        "(IRT), with MongoDB-backed sessions and Groq-powered personalized study plans."
    ),
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))


@app.get("/health", tags=["system"])
async def health_check():
    """Lightweight health endpoint for deployment monitoring."""
    return {"status": "ok", "service": "adaptive-diagnostic-recognition"}


@app.on_event("startup")
async def on_startup():
    await connect_db()


@app.on_event("shutdown")
async def on_shutdown():
    await close_db()
