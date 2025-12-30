"""
Storage layer for symbology mappings.

This implementation stores all data in memory. It performs no domain-level
validation; all symbology invariants are enforced by the domain layer.
"""

import os
import json
from dataclasses import dataclass
from datetime import date


@dataclass
class Mapping:
    symbol: str
    identifier: int
    start_date: date
    end_date: date | None = None


class MappingStorage:
    def __init__(self, persist_file: str | None = None):
        self._mappings: list[Mapping] = []
        self.persist_file = persist_file
        self.load()

    def insert(self, symbol: str, identifier: int, start_date: date) -> None:
        mapping = Mapping(symbol, identifier, start_date)
        self._mappings.append(mapping)
        self.save()

    def save(self):
        if not self.persist_file:
            return
        with open(self.persist_file, "w") as f:
            json.dump([m.__dict__ for m in self._mappings], f, default=str)

    def load(self) -> None:
        if not self.persist_file or not os.path.exists(self.persist_file):
            return
        with open(self.persist_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
        self._mappings = [Mapping(**item) for item in data]

    def find_active_by_symbol(self, symbol: str, query_date: date):
        """
        Return the active mapping for a symbol on a given date.
        Uses half-open interval [start_date, end_date).
        """
        for m in self._mappings:
            if m.symbol == symbol and (m.end_date is None or m.end_date > query_date):
                return m
        return None

    def find_active_by_identifier(self, identifier: int, query_date: date):
        """
        Return the active mapping for an identifier on a given date.
        Uses half-open interval [start_date, end_date).
        """
        for m in self._mappings:
            if m.identifier == identifier and (
                m.end_date is None or m.end_date > query_date
            ):
                return m
        return None

    def find_by_symbol(self, symbol: str, query_date: date):
        """Alias for lookup by symbol."""
        return self.find_active_by_symbol(symbol, query_date)
