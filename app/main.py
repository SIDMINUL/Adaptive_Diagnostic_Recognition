"""
Adaptive Diagnostic Engine — FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.services.database import connect_db, close_db
from app.routers.api import router

app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description=(
        "A 1-Dimension Adaptive Testing system using IRT (Item Response Theory) "
        "to dynamically select questions and estimate student ability. "
        "Integrates Claude AI for personalized study plan generation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routes ────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")

# ── Static frontend ───────────────────────────────────────────────────────────
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))


# ── Lifecycle ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    await connect_db()


@app.on_event("shutdown")
async def on_shutdown():
    await close_db()
