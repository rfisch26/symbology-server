"""
Pydantic schemas for request validation and response serialization.

These are API boundary types only — separate from the domain model.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel

# ── Request schemas ───────────────────────────────────────────────────────────


class MappingCreate(BaseModel):
    symbol: str
    identifier: int
    start_date: date


class MappingTerminate(BaseModel):
    symbol: str
    end_date: date


# ── Response schemas ──────────────────────────────────────────────────────────


class MappingCreated(BaseModel):
    status: str = "ok"
    symbol: str
    identifier: int
    start_date: date


class MappingTerminated(BaseModel):
    status: str = "terminated"
    symbol: str
    end_date: date


class MappingResponse(BaseModel):
    symbol: str
    identifier: int
    start_date: date
    end_date: Optional[date] = None

    model_config = {"from_attributes": True}
