"""
Domain layer for symbology server.

This layer enforces all symbology server rules and invariants.
"""

from datetime import date
from typing import List
from .exceptions import ConflictError, NotFoundError
from .models import Mapping
from .storage import MappingStorage


class SymbologyServer:
    """Domain layer for symbology server."""
    
    def __init__(self, storage: MappingStorage) -> None:
        self.storage = storage

    def add_mapping(self, symbol: str, identifier: int, start_date: date) -> None:
        """
        Add a symbology mapping.

        A mapping is persistent until explicitly terminated.
        Adding a mapping that overlaps an existing one is a conflict.
        """
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

        self.storage.insert(
            Mapping(
                symbol=symbol,
                identifier=identifier,
                start_date=start_date,
                end_date=None,
            )
        )

    def terminate_mapping(self, symbol: str, end_date: date) -> None:
        """Terminate an active mapping for the given symbol on end_date."""
        try:
            self.storage.terminate(symbol, end_date)
        except KeyError:
            raise NotFoundError(
                f"No active mapping for symbol '{symbol}' on {end_date}"
            )

    def get_identifier(self, symbol: str, on: date) -> int:
        """Get the identifier for a symbol on a given date."""
        m = self.storage.find_active_by_symbol(symbol, on)
        if not m:
            raise NotFoundError(f"No mapping for symbol '{symbol}' on {on}")
        return m.identifier

    def get_symbol(self, identifier: int, on: date) -> str:
        """Get the symbol for an identifier on a given date."""
        m = self.storage.find_active_by_identifier(identifier, on)
        if not m:
            raise NotFoundError(f"No mapping for identifier '{identifier}' on {on}")
        return m.symbol

    def get_mappings_between(self, begin: date, end: date) -> List[Mapping]:
        """Get all mappings overlapping the given date range [begin, end)."""
        return self.storage.find_range(begin, end)
