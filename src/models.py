"""
Domain models for the symbology service.

These are plain data containers with no business logic.
All symbology invariants are enforced by the domain layer.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Mapping:
    """
    Represents a symbol↔identifier assignment over a time interval.

    A mapping is active on the half-open interval [start_date, end_date).
    If end_date is None, the mapping is open-ended (still active).
    """

    symbol: str
    identifier: int
    start_date: date
    end_date: Optional[date] = None
