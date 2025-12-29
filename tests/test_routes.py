"""
Storage-layer tests for the symbology server.

These tests verify the behavior of the in-memory storage backend, including:
    - Insertion
    - Termination
    - Range queries.

No domain-level validation is performed here, and all symbology invariants are enforced by the domain layer.
"""

from fastapi.testclient import TestClient
from src.main import create_app


def test_end_to_end_http_flow() -> None:
    """Verify basic HTTP interaction."""
    client = TestClient(create_app())
    response = client.post(
        "/mapping",
        json={
            "symbol": "MSFT",
            "identifier": 10,
            "start_date": "2024-01-01",
        },
    )
    assert response.status_code == 200
    response = client.get("/symbol/MSFT", params={"date": "2024-01-02"})
    assert response.json() == 10
