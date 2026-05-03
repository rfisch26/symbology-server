"""
Persistence tests for the symbology server.

Verifies that mappings survive a save/load cycle — i.e. are correctly
written to disk and reloaded by a fresh MappingStorage instance.
"""

from datetime import date
from src.storage import MappingStorage
from src.domain import SymbologyServer


def test_mapping_survives_restart(tmp_path):
    """A mapping added in one server instance should be visible in a fresh one."""
    persist_file = str(tmp_path / "mappings.json")

    storage1 = MappingStorage(persist_file=persist_file)
    domain1 = SymbologyServer(storage1)
    domain1.add_mapping("AAPL", 1, date(2024, 1, 1))

    storage2 = MappingStorage(persist_file=persist_file)
    domain2 = SymbologyServer(storage2)
    result = domain2.lookup("AAPL", date(2024, 1, 2))
    assert result.identifier == 1


def test_termination_survives_restart(tmp_path):
    """A terminated mapping should remain terminated after reload."""
    persist_file = str(tmp_path / "mappings.json")

    storage1 = MappingStorage(persist_file=persist_file)
    domain1 = SymbologyServer(storage1)
    domain1.add_mapping("AAPL", 1, date(2024, 1, 1))
    domain1.terminate_mapping("AAPL", date(2024, 1, 10))

    storage2 = MappingStorage(persist_file=persist_file)
    domain2 = SymbologyServer(storage2)

    # Should still be active before end_date
    result = domain2.lookup("AAPL", date(2024, 1, 9))
    assert result.identifier == 1

    # Should be inactive on end_date (half-open interval)
    from src.exceptions import NotFoundError
    import pytest
    with pytest.raises(NotFoundError):
        domain2.lookup("AAPL", date(2024, 1, 10))