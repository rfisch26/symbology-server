"""
Domain layer for symbology server.

This layer enforces all symbology server rules and invariants.
"""

from datetime import date
from src.storage import MappingStorage
from src.exceptions import ConflictError


class SymbologyServer:
    def __init__(self, storage: MappingStorage):
        self.storage = storage

    def add_mapping(self, symbol: str, identifier: int, start_date: date) -> None:
        """
        Add a symbology mapping.
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

        self.storage.insert(symbol, identifier, start_date)

    def terminate_mapping(self, symbol: str, end_date: date) -> None:
        mapping = self.storage.find_active_by_symbol(symbol, end_date)
        if not mapping:
            raise ValueError(f"No active mapping found for symbol {symbol}")
        mapping.end_date = end_date
        self.storage.save()

    def lookup(self, symbol: str, query_date: date):
        """
        Return the active mapping for a symbol on a given date.
        Return None if no active mapping exists.
        """
        mapping = self.storage.find_active_by_symbol(symbol, query_date)
        return mapping
