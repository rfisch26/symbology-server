"""
Storage-layer tests for the symbology server.

Tests verify the in-memory storage backend in isolation from the domain layer,
including:
    - Insertion and retrieval
    - Half-open interval boundary behavior
    - Date-range overlap queries
    - Persistence round-trip (save and load)
"""

from datetime import date
from src.storage import MappingStorage
from src.models import Mapping


# ── Insertion and retrieval ───────────────────────────────────────────────────

def test_insert_and_find_active(storage: MappingStorage):
    storage.insert("AAPL", 1, date(2024, 1, 1))
    mapping = storage.find_active_by_symbol("AAPL", date(2024, 1, 2))
    assert mapping is not None
    assert mapping.identifier == 1


def test_find_active_before_start_returns_none(storage: MappingStorage):
    storage.insert("AAPL", 1, date(2024, 1, 5))
    assert storage.find_active_by_symbol("AAPL", date(2024, 1, 4)) is None


def test_find_active_on_end_date_returns_none(storage: MappingStorage):
    """end_date is exclusive — mapping should not be active on its own end_date."""
    storage._mappings.append(Mapping("AAPL", 1, date(2024, 1, 1), date(2024, 1, 5)))
    assert storage.find_active_by_symbol("AAPL", date(2024, 1, 5)) is None


def test_find_active_one_day_before_end_date(storage: MappingStorage):
    storage._mappings.append(Mapping("AAPL", 1, date(2024, 1, 1), date(2024, 1, 5)))
    mapping = storage.find_active_by_symbol("AAPL", date(2024, 1, 4))
    assert mapping is not None


# ── Range queries ─────────────────────────────────────────────────────────────

def test_range_query_returns_overlapping_mappings(storage: MappingStorage):
    storage._mappings.append(Mapping("A", 1, date(2024, 1, 1), date(2024, 1, 3)))
    storage._mappings.append(Mapping("B", 2, date(2024, 1, 3), date(2024, 1, 5)))

    results = storage.get_mappings_between(date(2024, 1, 2), date(2024, 1, 4))
    assert len(results) == 2


def test_range_query_excludes_non_overlapping(storage: MappingStorage):
    storage._mappings.append(Mapping("A", 1, date(2024, 1, 1), date(2024, 1, 3)))

    results = storage.get_mappings_between(date(2024, 1, 10), date(2024, 1, 20))
    assert results == []


def test_open_ended_mapping_included_in_range(storage: MappingStorage):
    storage.insert("AAPL", 1, date(2024, 1, 1))  # no end_date

    results = storage.get_mappings_between(date(2025, 1, 1), date(2025, 6, 1))
    assert len(results) == 1


# ── Persistence ───────────────────────────────────────────────────────────────

def test_persistence_round_trip(tmp_path):
    """Dates must survive a save/load cycle as date objects, not strings."""
    persist_file = str(tmp_path / "mappings.json")

    s1 = MappingStorage(persist_file=persist_file)
    s1.insert("AAPL", 1, date(2024, 1, 1))

    s2 = MappingStorage(persist_file=persist_file)
    mapping = s2.find_active_by_symbol("AAPL", date(2024, 1, 2))
    assert mapping is not None
    assert mapping.identifier == 1
    assert isinstance(mapping.start_date, date)


def test_persistence_preserves_end_date(tmp_path):
    persist_file = str(tmp_path / "mappings.json")

    s1 = MappingStorage(persist_file=persist_file)
    s1._mappings.append(Mapping("AAPL", 1, date(2024, 1, 1), date(2024, 6, 1)))
    s1.save()

    s2 = MappingStorage(persist_file=persist_file)
    assert s2._mappings[0].end_date == date(2024, 6, 1)
    assert isinstance(s2._mappings[0].end_date, date)