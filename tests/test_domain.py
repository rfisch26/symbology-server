"""
Domain-level tests for the symbology server.

These tests validate core symbology semantics and invariants, including the following:
    - Persistence across dates
    - Reassignment behavior
    - Conflict detection.

The domain layer is tested in isolation from HTTP and storage concerns.
"""

from datetime import date
import pytest
from src.domain import SymbologyServer
from src.storage import MappingStorage
from src.exceptions import ConflictError, NotFoundError


def test_add_and_lookup_mapping():
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    assert domain.get_identifier("AAPL", date(2024, 1, 2)) == 1


def test_conflict_on_same_symbol():
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("AAPL", 2, date(2024, 1, 1))


def test_termination_and_notfound():
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    with pytest.raises(NotFoundError):
        domain.get_identifier("AAPL", date(2024, 1, 6))


def test_must_terminate_before_reassigning():
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))

    with pytest.raises(ConflictError):
        domain.add_mapping("AAPL", 2, date(2024, 1, 5))

    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    domain.add_mapping("AAPL", 2, date(2024, 1, 5))

    assert domain.get_identifier("AAPL", date(2024, 1, 6)) == 2


def test_conflict_on_same_identifier():
    domain = SymbologyServer(MappingStorage())
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))

    with pytest.raises(ConflictError):
        domain.add_mapping("MSFT", 1, date(2024, 1, 2))
