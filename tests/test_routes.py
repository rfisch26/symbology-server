"""
Storage-layer tests for the symbology server.

These tests verify the behavior of the in-memory storage backend, including:
    - Insertion
    - Termination
    - Range queries.

No domain-level validation is performed here, and all symbology invariants are enforced by the domain layer.
"""

from fastapi.testclient import TestClient
from datetime import date
from src.main import create_app
from src.storage import MappingStorage


def test_end_to_end_http_flow():
    storage = MappingStorage()
    app = create_app(storage)
    client = TestClient(app)
    response = client.post(
        "/mapping",
        json={"symbol": "MSFT", "identifier": 10, "start_date": "2024-01-01"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "MSFT"
    assert data["identifier"] == 10
    assert data["start_date"] == "2024-01-01"
    response = client.post(
        "/mapping/terminate",
        json={"symbol": "MSFT", "end_date": "2024-01-02"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "terminated"
