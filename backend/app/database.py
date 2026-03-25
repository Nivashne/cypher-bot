from __future__ import annotations

import aiosqlite
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "alerts.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drone_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timestamp TEXT NOT NULL,
    signal_strength REAL NOT NULL,
    doppler_shift REAL NOT NULL,
    terrain TEXT NOT NULL,
    threat_level TEXT NOT NULL,
    source_unit TEXT NOT NULL
);
"""


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def insert_alert(row: dict[str, Any]) -> int:
    query = """
    INSERT INTO alerts (
        drone_type, confidence, latitude, longitude, timestamp,
        signal_strength, doppler_shift, terrain, threat_level, source_unit
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        row["drone_type"],
        row["confidence"],
        row["location"][0],
        row["location"][1],
        row["timestamp"],
        row["signal_strength"],
        row["doppler_shift"],
        row["terrain"],
        row["threat_level"],
        row["source_unit"],
    )

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, values)
        await db.commit()
        return cursor.lastrowid


async def fetch_alerts(limit: int = 500) -> list[dict[str, Any]]:
    query = """
    SELECT id, drone_type, confidence, latitude, longitude, timestamp,
           signal_strength, doppler_shift, terrain, threat_level, source_unit
    FROM alerts
    ORDER BY id DESC
    LIMIT ?
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, (limit,))
        rows = await cursor.fetchall()

    return [
        {
            "id": row["id"],
            "drone_type": row["drone_type"],
            "confidence": row["confidence"],
            "location": [row["latitude"], row["longitude"]],
            "timestamp": row["timestamp"],
            "signal_strength": row["signal_strength"],
            "doppler_shift": row["doppler_shift"],
            "terrain": row["terrain"],
            "threat_level": row["threat_level"],
            "source_unit": row["source_unit"],
        }
        for row in rows
    ]
