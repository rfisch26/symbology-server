"""
API schemas for request validation and response serialization.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

class MappingCreate(BaseModel):
    """Request payload for creating a new mapping."""

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=8,
        pattern="^[A-Za-z]+$",  # Pydantic v2 replacement for `regex`
        description="Human-readable instrument symbol",
    )
    identifier: int = Field(
        ...,
        ge=0,
        description="Exchange-assigned numeric identifier",
    )
    start_date: date


class MappingTerminate(BaseModel):
    """Request payload for terminating an existing mapping."""

    symbol: str
    end_date: date

class MappingResponse(BaseModel):
    """Serialized representation of a mapping."""

    symbol: str
    identifier: int
    start_date: date
    end_date: Optional[date]