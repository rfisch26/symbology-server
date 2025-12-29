"""
Domain models for the symbology service.

These objects are immutable and contain no domain logic.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Mapping:
    """
    Represents a symbol and identifier assignment over a time interval.

    The mapping is active on the half-open interval:
        [start_date, end_date)

    If end_date is None, the mapping is considered open-ended.
    """

    symbol: str
    identifier: int
    start_date: date
    end_date: Optional[date] = None
