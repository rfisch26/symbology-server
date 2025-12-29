"""
Domain layer for symbology server.

This layer enforces all symbology server rules and invariants.
"""

from datetime import date
from typing import List
from .exceptions import NotFoundError
from .models import Mapping
from .storage import MappingStorage


class SymbologyServer:
    """Domain layer for symbology mappings."""

    def __init__(self, storage: MappingStorage) -> None:
        """Initialize the server with a storage backend."""
        self.storage = storage

    def add_mapping(self, symbol: str, identifier: int, start_date: date) -> None:
        """
        Add or update a symbology mapping.

        If the symbol or identifier already has an active mapping on the
        given date, the existing mapping is automatically terminated.
        """
        existing_symbol = self.storage.find_active_by_symbol(symbol, start_date)
        if existing_symbol:
            self.storage.terminate(symbol, start_date)

        existing_identifier = self.storage.find_active_by_identifier(
            identifier, start_date
        )
        if existing_identifier:
            self.storage.terminate(existing_identifier.symbol, start_date)

        self.storage.insert(
            Mapping(
                symbol=symbol,
                identifier=identifier,
                start_date=start_date,
                end_date=None,
            )
        )

    def terminate_mapping(self, symbol: str, end_date: date) -> None:
        """Explicitly terminate a mapping."""
        self.storage.terminate(symbol, end_date)

    def get_identifier(self, symbol: str, query_date: date) -> int:
        """Retrieve identifier for a symbol on a given date."""
        mapping = self.storage.find_active_by_symbol(symbol, query_date)
        if not mapping:
            raise NotFoundError(f"No mapping for symbol '{symbol}' on {query_date}")
        return mapping.identifier

    def get_symbol(self, identifier: int, query_date: date) -> str:
        """Retrieve symbol for an identifier on a given date."""
        mapping = self.storage.find_active_by_identifier(identifier, query_date)
        if not mapping:
            raise NotFoundError(
                f"No mapping for identifier '{identifier}' on {query_date}"
            )
        return mapping.symbol

    def get_mappings_between(self, begin: date, end: date) -> List[Mapping]:
        """Retrieve all mappings overlapping [begin, end)."""
        return self.storage.get_between(begin, end)
