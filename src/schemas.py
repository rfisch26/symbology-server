"""
API schemas for request validation and response serialization.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel


class MappingCreate(BaseModel):
    symbol: str
    identifier: int
    start_date: date


class MappingTerminate(BaseModel):
    symbol: str
    end_date: date


class MappingResponse(BaseModel):
    symbol: str
    identifier: int
    start_date: date
    end_date: Optional[date]
