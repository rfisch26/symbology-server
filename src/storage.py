"""
Storage layer for symbology mappings.

This implementation stores all data in memory. It performs no domain-level
validation; all symbology invariants are enforced by the domain layer.
"""

from datetime import date
from typing import List, Optional
from .exceptions import NotFoundError
from .models import Mapping

class MappingStorage:
    """In-memory storage for symbology mappings."""

    def __init__(self) -> None:
        """Initialize empty storage."""
        self._mappings: List[Mapping] = []

    def insert(self, mapping: Mapping) -> None:
        """Insert a mapping into storage."""
        self._mappings.append(mapping)
        
    def find_range(self, begin: date, end: date) -> list[Mapping]:
        """
        Return all mappings whose active interval overlaps [begin, end).
        """
        return [
            m
            for m in self._mappings
            if m.start_date < end
            and (m.end_date is None or m.end_date > begin)
        ]

    def find_active_by_symbol(
        self, symbol: str, query_date: date
    ) -> Optional[Mapping]:
        """Find active mapping by symbol."""
        for m in self._mappings:
            if (
                m.symbol == symbol
                and m.start_date <= query_date
                and (m.end_date is None or query_date < m.end_date)
            ):
                return m
        return None

    def find_active_by_identifier(
        self, identifier: int, query_date: date
    ) -> Optional[Mapping]:
        """Find active mapping by identifier."""
        for m in self._mappings:
            if (
                m.identifier == identifier
                and m.start_date <= query_date
                and (m.end_date is None or query_date < m.end_date)
            ):
                return m
        return None

    def terminate(self, symbol: str, end_date: date) -> None:
        """Terminate the active mapping for a symbol."""
        mapping = self.find_active_by_symbol(symbol, end_date)
        if not mapping:
            raise NotFoundError(
                f"No active mapping for symbol '{symbol}' on {end_date}"
            )
        mapping.end_date = end_date

    def get_between(self, begin: date, end: date) -> List[Mapping]:
        """Return mappings overlapping [begin, end)."""
        results: List[Mapping] = []
        for m in self._mappings:
            if m.start_date < end and (m.end_date is None or m.end_date > begin):
                results.append(m)
        return results