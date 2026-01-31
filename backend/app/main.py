from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import greyline, location, space_weather, station, ws
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ARClock backend")
    await start_scheduler()
    yield
    logger.info("Shutting down ARClock backend")
    await stop_scheduler()


app = FastAPI(title="ARClock", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(space_weather.router, prefix="/api/v1")
app.include_router(greyline.router, prefix="/api/v1")
app.include_router(station.router, prefix="/api/v1")
app.include_router(location.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


# Mount static files last so API routes take priority
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
