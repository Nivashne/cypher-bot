from __future__ import annotations

import asyncio
import json
from collections import deque
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .database import fetch_alerts, init_db, insert_alert
from .models import AlertIn

app = FastAPI(title="DRDO Command Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alerts_memory: deque[dict[str, Any]] = deque(maxlen=2000)
logs_memory: deque[dict[str, Any]] = deque(maxlen=5000)
ws_clients: set[WebSocket] = set()


def classify_threat(confidence: float) -> str:
    if confidence < 0.75:
        return "LOW"
    if confidence <= 0.9:
        return "MEDIUM"
    return "CRITICAL"


def log_event(source: str, message: str) -> dict[str, str]:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "message": message,
    }
    logs_memory.append(entry)
    return entry


async def broadcast(payload: dict[str, Any]) -> None:
    dead: list[WebSocket] = []
    for ws in ws_clients:
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_clients.discard(ws)


@app.on_event("startup")
async def startup() -> None:
    await init_db()
    log_event("SYSTEM", "DRDO backend initialized and ready")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/alert")
async def receive_alert(alert: AlertIn) -> dict[str, Any]:
    log1 = log_event("FIELD_UNIT", "Signal received from field unit")
    log2 = log_event("ANALYZER", "Analyzing threat level...")

    enriched = {
        **alert.model_dump(),
        "timestamp": alert.timestamp.isoformat(),
        "threat_level": classify_threat(alert.confidence),
    }

    alert_id = await insert_alert(enriched)
    enriched["id"] = alert_id
    alerts_memory.appendleft(enriched)

    await asyncio.sleep(0.2)
    await broadcast({"type": "alert", "payload": enriched})
    await broadcast({"type": "log", "payload": log1})
    await broadcast({"type": "log", "payload": log2})

    return {"status": "received", "alert": enriched}


@app.get("/alerts")
async def get_alerts(limit: int = 200) -> list[dict[str, Any]]:
    if alerts_memory:
        return list(alerts_memory)[:limit]
    return await fetch_alerts(limit)


@app.get("/logs")
async def get_logs(limit: int = 200) -> list[dict[str, Any]]:
    return list(logs_memory)[-limit:]


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    ws_clients.add(websocket)
    await websocket.send_json({"type": "hello", "payload": "ws_connected"})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_clients.discard(websocket)
