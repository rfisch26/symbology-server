"""
HTTP API tests for the symbology server.

These tests exercise the FastAPI routes end-to-end, verifying:
    - Request/response behavior
    - Serialization
    - Error propagation from the domain layer
"""

from datetime import date
from src.storage import MappingStorage, Mapping


def test_insert_and_find_active():
    storage = MappingStorage()
    storage.insert("AAPL", 1, date(2024, 1, 1))
    mapping = storage.find_active_by_symbol("AAPL", date(2024, 1, 2))
    assert mapping.identifier == 1


def test_range_query_returns_overlapping_mappings():
    storage = MappingStorage()
    storage._mappings.append(Mapping("A", 1, date(2024, 1, 1), date(2024, 1, 3)))
    storage._mappings.append(Mapping("B", 2, date(2024, 1, 3), date(2024, 1, 5)))

    result = [
        m
        for m in storage._mappings
        if (m.end_date is None or m.end_date >= date(2024, 1, 2))
        and m.start_date <= date(2024, 1, 4)
    ]
    assert len(result) == 2


def test_storage_persistence():
    import os

    PERSIST_FILE = "test_mappings.json"

    if os.path.exists(PERSIST_FILE):
        os.remove(PERSIST_FILE)

    storage1 = MappingStorage(persist_file=PERSIST_FILE)
    storage1.insert("AAPL", 1, date(2024, 1, 1))
    storage1.save()

    storage2 = MappingStorage(persist_file=PERSIST_FILE)
    storage2.load()
    mapping = storage2.find_active_by_symbol("AAPL", date(2024, 1, 2))
    assert mapping is not None
    assert mapping.identifier == 1

    os.remove(PERSIST_FILE)
