"""
Domain-level tests for the symbology server.

These tests validate core symbology semantics and invariants, including the following:
    - Persistence across dates
    - Reassignment behavior
    - Conflict detection.

The domain layer is tested in isolation from HTTP and storage concerns.
"""

import pytest
from datetime import date
from src.domain import SymbologyServer
from src.storage import MappingStorage
from src.exceptions import ConflictError, NotFoundError


@pytest.fixture
def fresh_domain():
    storage = MappingStorage()
    return SymbologyServer(storage)


def test_add_and_lookup_mapping(fresh_domain):
    domain = fresh_domain
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    result = domain.lookup("AAPL", date(2024, 1, 2))
    assert result.identifier == 1


def test_conflict_on_same_symbol(fresh_domain):
    domain = fresh_domain
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("AAPL", 2, date(2024, 1, 2))


def test_termination_and_notfound(fresh_domain):
    domain = fresh_domain
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 2))
    result = domain.lookup("AAPL", date(2024, 1, 2))
    assert result is None


def test_must_terminate_before_reassigning(fresh_domain):
    domain = fresh_domain
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("AAPL", 2, date(2024, 1, 1))


def test_conflict_on_same_identifier(fresh_domain):
    domain = fresh_domain
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("MSFT", 1, date(2024, 1, 1))
