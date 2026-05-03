"""
Shared pytest fixtures for the symbology server test suite.
"""

import pytest
from fastapi.testclient import TestClient
from src.domain import SymbologyServer
from src.storage import MappingStorage
from src.main import create_app


@pytest.fixture
def storage() -> MappingStorage:
    return MappingStorage()


@pytest.fixture
def domain(storage: MappingStorage) -> SymbologyServer:
    return SymbologyServer(storage)


@pytest.fixture
def client(storage: MappingStorage) -> TestClient:
    app = create_app(storage)
    return TestClient(app)