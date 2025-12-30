"""
Domain layer for symbology server.

This layer enforces all symbology server rules and invariants.
"""

from datetime import date
from src.storage import MappingStorage
from src.exceptions import ConflictError, NotFoundError


class SymbologyServer:
    def __init__(self, storage: MappingStorage):
        self.storage = storage

    def add_mapping(self, symbol: str, identifier: int, start_date: date) -> None:
        if self.storage.find_active_by_symbol(symbol, start_date):
            raise ConflictError(
                f"Symbol '{symbol}' already has an active mapping on {start_date}. "
                "Terminate it before reassignment."
            )

        if self.storage.find_active_by_identifier(identifier, start_date):
            raise ConflictError(
                f"Identifier '{identifier}' is already assigned on {start_date}. "
                "Terminate it before reassignment."
            )

        self.storage.insert(symbol, identifier, start_date)

    def terminate_mapping(self, symbol: str, end_date: date) -> None:
        mapping = self.storage.find_active_by_symbol(symbol, end_date)
        if not mapping:
            raise NotFoundError(f"No active mapping found for symbol {symbol}")
        mapping.end_date = end_date
        self.storage.save()

    def lookup(self, symbol: str, query_date: date):
        mapping = self.storage.find_by_symbol(symbol, query_date)
        if not mapping:
            raise NotFoundError(f"No mapping found for {symbol} on {query_date}")
        return mapping

    def get_identifier(self, symbol: str, query_date: date) -> int:
        mapping = self.lookup(symbol, query_date)
        return mapping.identifier

    def get_symbol(self, identifier: int, query_date: date) -> str:
        for m in self.storage._mappings:
            if m.identifier == identifier and (
                m.end_date is None or m.end_date >= query_date
            ):
                return m.symbol
        raise NotFoundError(
            f"No symbol found for identifier {identifier} on {query_date}"
        )

    def get_mappings_between(self, begin: date, end: date):
        """Return all mappings that overlap the date range [begin, end)."""
        result = []
        for m in self.storage._mappings:
            mapping_start = m.start_date
            mapping_end = m.end_date or date.max
            if mapping_start < end and mapping_end >= begin:
                result.append(m)
        return result
