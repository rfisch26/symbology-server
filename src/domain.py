"""
Domain layer for the symbology server.

This layer enforces all symbology rules and invariants.
The domain has no knowledge of HTTP or serialization concerns.
"""

from datetime import date
from src.models import Mapping
from src.storage import MappingStorage
from src.exceptions import ConflictError, NotFoundError


class SymbologyServer:
    def __init__(self, storage: MappingStorage):
        self.storage = storage

    def add_mapping(self, symbol: str, identifier: int, start_date: date) -> None:
        """
        Create a new symbol↔identifier mapping starting on start_date.

        Raises ConflictError if the symbol or identifier already has an active
        mapping on start_date. The existing mapping must be terminated first.
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
        """
        Terminate the active mapping for symbol by setting its end_date.

        Raises NotFoundError if no active mapping exists for symbol on end_date.
        """
        mapping = self.storage.find_active_by_symbol(symbol, end_date)
        if not mapping:
            raise NotFoundError(f"No active mapping found for symbol '{symbol}' on {end_date}.")
        mapping.end_date = end_date
        self.storage.save()

    def lookup(self, symbol: str, query_date: date) -> Mapping:
        """Return the active Mapping for symbol on query_date, or raise NotFoundError."""
        mapping = self.storage.find_active_by_symbol(symbol, query_date)
        if not mapping:
            raise NotFoundError(f"No mapping found for '{symbol}' on {query_date}.")
        return mapping

    def get_identifier(self, symbol: str, query_date: date) -> int:
        """Return the identifier assigned to symbol on query_date."""
        return self.lookup(symbol, query_date).identifier

    def get_symbol(self, identifier: int, query_date: date) -> str:
        """
        Return the symbol assigned to identifier on query_date.

        Uses the same half-open interval semantics [start_date, end_date)
        as the rest of the domain.
        """
        mapping = self.storage.find_active_by_identifier(identifier, query_date)
        if not mapping:
            raise NotFoundError(
                f"No symbol found for identifier {identifier} on {query_date}."
            )
        return mapping.symbol

    def get_mappings_between(self, begin: date, end: date) -> list[Mapping]:
        """Return all mappings that overlap the half-open date range [begin, end)."""
        return self.storage.get_mappings_between(begin, end)