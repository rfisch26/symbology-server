"""
Domain-level tests for the symbology server.

These tests validate core symbology semantics and invariants, including the following:
    - Persistence across dates
    - Reassignment behavior
    - Conflict detection.

The domain layer is tested in isolation from HTTP and storage concerns.
"""

from datetime import date
from src.domain import SymbologyServer
from src.storage import MappingStorage


def test_add_and_lookup_mapping() -> None:
    """Verify a mapping can be added and queried."""
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    assert domain.get_identifier("AAPL", date(2024, 1, 2)) == 1


def test_symbol_reassignment_same_date() -> None:
    """
    Verify that reassigning a symbol on the same date
    automatically terminates the existing mapping.
    """
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.add_mapping("AAPL", 2, date(2024, 1, 1))
    assert domain.get_identifier("AAPL", date(2024, 1, 1)) == 2
