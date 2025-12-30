"""
Storage layer for symbology mappings.

This implementation stores all data in memory. It performs no domain-level
validation; all symbology invariants are enforced by the domain layer.
"""

from datetime import date
from typing import List, Optional
from .models import Mapping


class MappingStorage:
    def __init__(self) -> None:
        self._mappings: List[Mapping] = []

    def insert(self, mapping: Mapping) -> None:
        self._mappings.append(mapping)

    def all(self) -> List[Mapping]:
        return list(self._mappings)

    def find_range(self, begin: date, end: date) -> List[Mapping]:
        """Return overlapping mappings [begin, end)."""
        results = []
        for m in self._mappings:
            mapping_end = m.end_date or date.max
            if m.start_date < end and mapping_end > begin:  # half-open interval
                results.append(m)
        return results

    def find_active_by_symbol(self, symbol: str, on: date) -> Optional[Mapping]:
        for m in self._mappings:
            if (
                m.symbol == symbol
                and m.start_date <= on
                and (m.end_date is None or m.end_date >= on)
            ):
                return m
        return None

    def find_active_by_identifier(self, identifier: int, on: date) -> Optional[Mapping]:
        for m in self._mappings:
            if (
                m.identifier == identifier
                and m.start_date <= on
                and (m.end_date is None or m.end_date >= on)
            ):
                return m
        return None

    def terminate(self, symbol: str, end_date: date) -> None:
        m = self.find_active_by_symbol(symbol, end_date)
        if not m:
            raise KeyError
        m.end_date = end_date
