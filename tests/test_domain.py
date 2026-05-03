"""
Domain-layer tests for the symbology server.

Tests validate core symbology semantics and invariants in isolation
from HTTP and storage concerns, including:
    - Basic add and lookup
    - Half-open interval boundary behavior
    - Conflict detection (duplicate symbol, duplicate identifier)
    - Termination and post-termination lookup
    - Reassignment after explicit termination
    - Reverse lookup (identifier → symbol)
    - Date-range queries
"""

import pytest
from datetime import date
from src.domain import SymbologyServer
from src.exceptions import ConflictError, NotFoundError

# ── Basic add and lookup ──────────────────────────────────────────────────────


def test_add_and_lookup_mapping(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    result = domain.lookup("AAPL", date(2024, 1, 2))
    assert result.identifier == 1


def test_lookup_on_start_date(domain: SymbologyServer):
    """A mapping should be active on its own start_date."""
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    result = domain.lookup("AAPL", date(2024, 1, 1))
    assert result.identifier == 1


def test_lookup_before_start_date_raises(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 5))
    with pytest.raises(NotFoundError):
        domain.lookup("AAPL", date(2024, 1, 4))


# ── Conflict detection ────────────────────────────────────────────────────────


def test_conflict_on_duplicate_symbol(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("AAPL", 2, date(2024, 1, 2))


def test_conflict_on_duplicate_identifier(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("MSFT", 1, date(2024, 1, 1))


# ── Termination ───────────────────────────────────────────────────────────────


def test_termination_makes_mapping_inactive(domain: SymbologyServer):
    """A mapping terminated on end_date should not be active on end_date (half-open)."""
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    with pytest.raises(NotFoundError):
        domain.lookup("AAPL", date(2024, 1, 5))


def test_mapping_active_one_day_before_termination(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    result = domain.lookup("AAPL", date(2024, 1, 4))
    assert result.identifier == 1


def test_terminate_nonexistent_mapping_raises(domain: SymbologyServer):
    with pytest.raises(NotFoundError):
        domain.terminate_mapping("AAPL", date(2024, 1, 1))


# ── Reassignment after termination ────────────────────────────────────────────


def test_reassign_symbol_after_termination(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    domain.add_mapping("AAPL", 2, date(2024, 1, 5))
    assert domain.get_identifier("AAPL", date(2024, 1, 5)) == 2


def test_reassign_without_termination_raises(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    with pytest.raises(ConflictError):
        domain.add_mapping("AAPL", 2, date(2024, 1, 1))


# ── Reverse lookup ────────────────────────────────────────────────────────────


def test_get_symbol_by_identifier(domain: SymbologyServer):
    domain.add_mapping("AAPL", 42, date(2024, 1, 1))
    assert domain.get_symbol(42, date(2024, 1, 2)) == "AAPL"


def test_get_symbol_after_termination_raises(domain: SymbologyServer):
    domain.add_mapping("AAPL", 42, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    with pytest.raises(NotFoundError):
        domain.get_symbol(42, date(2024, 1, 5))


# ── Date-range queries ────────────────────────────────────────────────────────


def test_get_mappings_between_returns_overlapping(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 5))
    domain.add_mapping("AAPL", 2, date(2024, 1, 5))

    results = domain.get_mappings_between(date(2024, 1, 3), date(2024, 1, 6))
    identifiers = {m.identifier for m in results}
    assert identifiers == {1, 2}


def test_get_mappings_between_excludes_non_overlapping(domain: SymbologyServer):
    domain.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain.terminate_mapping("AAPL", date(2024, 1, 3))

    results = domain.get_mappings_between(date(2024, 1, 10), date(2024, 1, 20))
    assert results == []
