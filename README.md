# Symbology Server

A FastAPI service that maintains temporal mappings between human-readable symbols (e.g. `NVDA`) and numeric identifiers, with point-in-time lookups and explicit lifecycle management.

## Features

- **Point-in-time queries** — look up what identifier a symbol held on any given date, or which symbol an identifier belonged to
- **Temporal lifecycle** — mappings are persistent until explicitly terminated; the server enforces that a symbol or identifier can only appear in one active mapping at a time
- **Date-range queries** — retrieve all mappings overlapping a `[begin, end)` window
- **Optional persistence** — mappings survive restarts via JSON file serialization; defaults to in-memory
- **35 tests** across domain, storage, HTTP, and persistence layers

## Design

The codebase follows a strict three-layer architecture:

```
HTTP (routes.py)       → translates requests/responses, handles HTTP errors
Domain (domain.py)     → enforces all symbology invariants
Storage (storage.py)   → stores and retrieves Mapping objects, no validation
```

Each layer only talks to the one below it. The domain layer has no knowledge of FastAPI; the storage layer has no knowledge of symbology rules.

**Temporal semantics** — every mapping is active over a half-open interval `[start_date, end_date)`. A mapping with no `end_date` is open-ended. All date arithmetic is consistent across every layer.

**Conflict handling** — attempting to assign an already-active symbol or identifier raises a `ConflictError`, surfaced as HTTP 409. The existing mapping must be explicitly terminated before reassignment.

## Project Structure

```
.
├── src/
│   ├── main.py             # App factory with optional storage injection
│   ├── domain.py           # Business logic and invariants
│   ├── storage.py          # In-memory store with optional persistence
│   ├── models.py           # Mapping dataclass (single source of truth)
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── routes.py           # FastAPI route definitions
│   └── exceptions.py       # NotFoundError, ConflictError
├── tests/
│   ├── conftest.py         # Shared fixtures (storage, domain, client)
│   ├── test_domain.py      # Invariants, termination, reassignment, range queries
│   ├── test_storage.py     # Interval boundary behavior, persistence round-trips
│   ├── test_routes.py      # End-to-end HTTP: status codes, 404s, 409s
│   └── test_persistence.py # Save/load across server restarts
├── pyproject.toml
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn src.main:app --reload --port 8000
```

Interactive docs at http://localhost:8000/docs.

## Running Tests

```bash
pytest tests/ -v
```

## API Reference

### `POST /mapping`
Create a new symbol↔identifier mapping.

```bash
curl -X POST http://localhost:8000/mapping \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "identifier": 1, "start_date": "2024-01-01"}'
```
```json
{"status": "ok", "symbol": "AAPL", "identifier": 1, "start_date": "2024-01-01"}
```
Returns `409` if the symbol or identifier already has an active mapping.

---

### `POST /mapping/terminate`
Terminate an active mapping. The mapping becomes inactive on `end_date` (exclusive).

```bash
curl -X POST http://localhost:8000/mapping/terminate \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "end_date": "2024-06-01"}'
```
```json
{"status": "terminated", "symbol": "AAPL", "end_date": "2024-06-01"}
```
Returns `404` if no active mapping exists for that symbol.

---

### `GET /symbol/{symbol}?date=YYYY-MM-DD`
Get the identifier assigned to a symbol on a given date.

```bash
curl "http://localhost:8000/symbol/AAPL?date=2024-03-15"
# → 1
```

---

### `GET /identifier/{identifier}?date=YYYY-MM-DD`
Get the symbol assigned to an identifier on a given date.

```bash
curl "http://localhost:8000/identifier/1?date=2024-03-15"
# → "AAPL"
```

---

### `GET /mappings?begin=YYYY-MM-DD&end=YYYY-MM-DD`
Get all mappings overlapping the half-open range `[begin, end)`.

```bash
curl "http://localhost:8000/mappings?begin=2024-01-01&end=2024-07-01"
```
```json
[
  {"symbol": "AAPL", "identifier": 1, "start_date": "2024-01-01", "end_date": "2024-06-01"},
  {"symbol": "AAPL", "identifier": 2, "start_date": "2024-06-01", "end_date": null}
]
```

## Data Format

| Field | Type | Description |
|---|---|---|
| `symbol` | `string` | Human-readable ticker or label |
| `identifier` | `integer` | Numeric ID |
| `start_date` | ISO 8601 date | First date the mapping is active (inclusive) |
| `end_date` | ISO 8601 date or `null` | First date inactive (exclusive); `null` = open-ended |