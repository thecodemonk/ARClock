from __future__ import annotations

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.cache import cache
from app.core.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        # Send snapshot of all cached data on connect
        all_data = cache.get_all()
        for key, entry in all_data.items():
            await ws.send_text(json.dumps({"type": key, "data": entry["data"]}))

        # Keep connection alive and listen for client messages
        while True:
            data = await ws.receive_text()
            # Client can send ping/pong or other messages
            if data == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
    except Exception as e:
        logger.error("WebSocket error: %s", e)
        ws_manager.disconnect(ws)
