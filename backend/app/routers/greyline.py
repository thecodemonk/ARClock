from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.cache import cache

router = APIRouter(tags=["greyline"])


@router.get("/greyline")
async def get_greyline():
    entry = cache.get("greyline")
    if not entry:
        raise HTTPException(status_code=503, detail="Grey line data not yet computed")
    return entry["data"]
