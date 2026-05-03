"""
HTTP API tests for the symbology server.

Tests exercise the FastAPI routes end-to-end via TestClient, verifying:
    - Request/response serialization
    - Correct HTTP status codes (200, 201, 404, 409)
    - Error detail propagation from the domain layer
"""

from fastapi.testclient import TestClient


# ── Add mapping ───────────────────────────────────────────────────────────────

def test_add_mapping_returns_201(client: TestClient):
    response = client.post(
        "/mapping",
        json={"symbol": "MSFT", "identifier": 10, "start_date": "2024-01-01"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "MSFT"
    assert data["identifier"] == 10
    assert data["start_date"] == "2024-01-01"
    assert data["status"] == "ok"


def test_add_duplicate_mapping_returns_409(client: TestClient):
    client.post(
        "/mapping",
        json={"symbol": "AAPL", "identifier": 1, "start_date": "2024-01-01"},
    )
    response = client.post(
        "/mapping",
        json={"symbol": "AAPL", "identifier": 2, "start_date": "2024-01-02"},
    )
    assert response.status_code == 409
    assert "AAPL" in response.json()["detail"]


# ── Terminate mapping ─────────────────────────────────────────────────────────

def test_terminate_mapping(client: TestClient):
    client.post(
        "/mapping",
        json={"symbol": "MSFT", "identifier": 10, "start_date": "2024-01-01"},
    )
    response = client.post(
        "/mapping/terminate",
        json={"symbol": "MSFT", "end_date": "2024-01-10"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "terminated"
    assert data["symbol"] == "MSFT"


def test_terminate_nonexistent_mapping_returns_404(client: TestClient):
    response = client.post(
        "/mapping/terminate",
        json={"symbol": "UNKNOWN", "end_date": "2024-01-01"},
    )
    assert response.status_code == 404


# ── Symbol lookup ─────────────────────────────────────────────────────────────

def test_get_identifier_for_symbol(client: TestClient):
    client.post(
        "/mapping",
        json={"symbol": "AAPL", "identifier": 42, "start_date": "2024-01-01"},
    )
    response = client.get("/symbol/AAPL?date=2024-01-15")
    assert response.status_code == 200
    assert response.json() == 42


def test_get_identifier_for_unknown_symbol_returns_404(client: TestClient):
    response = client.get("/symbol/UNKNOWN?date=2024-01-01")
    assert response.status_code == 404


# ── Identifier lookup ─────────────────────────────────────────────────────────

def test_get_symbol_for_identifier(client: TestClient):
    client.post(
        "/mapping",
        json={"symbol": "NVDA", "identifier": 99, "start_date": "2024-01-01"},
    )
    response = client.get("/identifier/99?date=2024-01-15")
    assert response.status_code == 200
    assert response.json() == "NVDA"


def test_get_symbol_for_unknown_identifier_returns_404(client: TestClient):
    response = client.get("/identifier/9999?date=2024-01-01")
    assert response.status_code == 404


# ── Date range query ──────────────────────────────────────────────────────────

def test_get_mappings_in_range(client: TestClient):
    client.post(
        "/mapping",
        json={"symbol": "AAPL", "identifier": 1, "start_date": "2024-01-01"},
    )
    response = client.get("/mappings?begin=2024-01-01&end=2024-02-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "AAPL"


def test_get_mappings_empty_range(client: TestClient):
    client.post(
        "/mapping",
        json={"symbol": "AAPL", "identifier": 1, "start_date": "2024-01-01"},
    )
    response = client.get("/mappings?begin=2023-01-01&end=2023-06-01")
    assert response.status_code == 200
    assert response.json() == []