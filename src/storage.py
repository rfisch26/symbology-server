"""
Storage layer for symbology mappings.

This implementation stores all data in memory. It performs no domain-level
validation; all symbology invariants are enforced by the domain layer.
"""

import os
import json
from datetime import date
from src.models import Mapping


class MappingStorage:
    def __init__(self, persist_file: str | None = None):
        self._mappings: list[Mapping] = []
        self.persist_file = persist_file
        self.load()

    def insert(self, symbol: str, identifier: int, start_date: date) -> None:
        self._mappings.append(Mapping(symbol, identifier, start_date))
        self.save()

    def save(self) -> None:
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
        self._mappings = [
            Mapping(
                symbol=item["symbol"],
                identifier=item["identifier"],
                start_date=date.fromisoformat(item["start_date"]),
                end_date=date.fromisoformat(item["end_date"]) if item["end_date"] else None,
            )
            for item in data
        ]

    def find_active_by_symbol(self, symbol: str, query_date: date) -> Mapping | None:
        """
        Return the active mapping for a symbol on a given date, or None.
        A mapping is active on the half-open interval [start_date, end_date).
        """
        for m in self._mappings:
            if m.symbol == symbol and m.start_date <= query_date and (
                m.end_date is None or m.end_date > query_date
            ):
                return m
        return None

    def find_active_by_identifier(self, identifier: int, query_date: date) -> Mapping | None:
        """
        Return the active mapping for an identifier on a given date, or None.
        A mapping is active on the half-open interval [start_date, end_date).
        """
        for m in self._mappings:
            if m.identifier == identifier and m.start_date <= query_date and (
                m.end_date is None or m.end_date > query_date
            ):
                return m
        return None

    def get_mappings_between(self, begin: date, end: date) -> list[Mapping]:
        """
        Return all mappings that overlap the half-open date range [begin, end).
        A mapping overlaps if its start_date < end and its end_date (or infinity) > begin.
        """
        result = []
        for m in self._mappings:
            mapping_end = m.end_date or date.max
            if m.start_date < end and mapping_end > begin:
                result.append(m)
        return result