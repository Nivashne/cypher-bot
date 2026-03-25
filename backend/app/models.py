from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class AlertIn(BaseModel):
    drone_type: str
    confidence: float = Field(ge=0, le=1)
    location: tuple[float, float]
    timestamp: datetime
    signal_strength: float
    doppler_shift: float
    terrain: str
    source_unit: str = "FDU-01"


class AlertOut(AlertIn):
    id: int
    threat_level: str


class SystemLog(BaseModel):
    timestamp: datetime
    source: str
    message: str
