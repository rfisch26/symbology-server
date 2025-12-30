"""
Tests for optional persistent storage in the Symbology Server.

These tests verify that symbology mappings are correctly saved to disk
and can be reloaded, ensuring persistence across application restarts.
"""

import tempfile
from datetime import date
from src.storage import MappingStorage
from src.domain import SymbologyServer


def test_persistence():
    with tempfile.NamedTemporaryFile() as tmp_file:
        storage1 = MappingStorage(persist_file=tmp_file.name)
        domain1 = SymbologyServer(storage1)
        domain1.add_mapping("AAPL", 1, date(2024, 1, 1))

        storage2 = MappingStorage(persist_file=tmp_file.name)
        domain2 = SymbologyServer(storage2)
        result = domain2.lookup("AAPL", date(2024, 1, 1))
        assert result.identifier == 1
