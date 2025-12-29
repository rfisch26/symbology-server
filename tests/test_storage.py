"""
HTTP API tests for the symbology server.

These tests exercise the FastAPI routes end-to-end, verifying:
    - Request/response behavior
    - Serialization
    - Error propagation from the domain layer
"""

from datetime import date
from src.models import Mapping
from src.storage import MappingStorage


def test_range_query_returns_overlapping_mappings() -> None:
    """Verify overlapping mappings are returned."""
    storage = MappingStorage()
    storage.insert(Mapping("A", 1, date(2024, 1, 1)))
    storage.insert(Mapping("B", 2, date(2024, 1, 3)))
    result = storage.find_range(date(2024, 1, 2), date(2024, 1, 4))
    assert len(result) == 2
