# Symbology Server

A Python FastAPI Symbology Server that maintains persistent mappings between human-readable symbols (e.g. `NVDA`) and numeric identifiers via an HTTP API for querying/updating symbol and identifier mappings over time.

## Features
- HTTP API to:
  - Add a symbology mapping
  - Terminate an active mapping
  - Query identifier for a symbol on a given date
  - Query symbol for an identifier on a given date
  - Retrieve all mappings overlapping a date range `[begin, end)`
- Enforces the following domain constraints:
  - One identifier per symbol per date
  - One symbol per identifier per date
  - Persistent mappings until explicit termination
- **Important**: A mapping must be explicitly terminated before the same symbol or identifier can be reassigned.
- In-memory `MappingStorage` backend by default; optional **persistent storage** supported
- Fully automated test suite using `pytest`

## Requirements
- Python ≥ 3.10
- Dependencies listed in `requirements.txt` and `pyproject.toml`

## Design Notes
- **Temporal Semantics**: A symbol’s assignment to an identifier is **persistent**. A mapping becomes active on its `start_date` and remains active until it is explicitly terminated. Each mapping is active over a half-open interval, so if `end_date` is omitted, the mapping is open-ended. All dates are ISO-8601 (`YYYY-MM-DD`) and independent of wall-clock time.
- **Reassignment Behavior**: If a symbol is reassigned to a new identifier, the previously active mapping is then terminated at the new mapping’s start date. Each symbol and identifier can only appear in one active mapping at a time.
- **Conflict Handling**: Violations of the following invariants raise explicit domain-level exceptions (surfaced as HTTP errors):
  - A symbol may have only one active identifier on a given date
  - An identifier may be assigned to only one symbol on a given date
- **Storage Model**: Uses an **in-memory storage layer** for clarity and correctness. Alternative storage backends (database, append-only log, etc.) can be introduced without changing the domain model.
- **Scope and Limitations**: This implementation omits:
  - Database persistence
  - Concurrency control
  - Timezone normalization
- **Determinism**: All query results are deterministic functions of input dates and stored mappings.
- **Persistent Storage (Optional Stretch Goal)**: The server can save its state to disk and reload it on restart. By default, storage is in-memory, but persistent storage allows mappings to survive application restarts. Persistence uses JSON file serialization.


## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Server

### Example (if applicable):
```bash
uvicorn src.main:app --reload --port 8000
```
### Persistent storage is enabled by default if JSON file exists

- The API will be available at http://localhost:8000.

## Running Tests

pytest tests/

Tests cover:
  - Domain layer: temporal invariants, reassignment rules, conflict handling
  - Storage layer: range queries, overlap detection
  - HTTP API layer: end-to-end request/response validation

## Example API Usage

### Add a mapping

curl -X POST http://localhost:8000/mapping \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","identifier":1,"start_date":"2024-01-01"}'

### Expected response:

{
  "status": "ok",
  "symbol": "AAPL",
  "identifier": 1,
  "start_date": "2024-01-01"
}


### Query identifier for a symbol

curl "http://localhost:8000/symbol/AAPL?date=2024-01-02"

### Expected response:

1


### Terminate a mapping

curl -X POST http://localhost:8000/mapping/terminate \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","end_date":"2024-01-05"}'

### Expected response:

{
  "status": "terminated",
  "symbol": "AAPL",
  "end_date": "2024-01-05"
}


### Reassign after termination

curl -X POST http://localhost:8000/mapping \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","identifier":2,"start_date":"2024-01-05"}'

### Expected response:

{
  "status": "ok",
  "symbol": "AAPL",
  "identifier": 2,
  "start_date": "2024-01-05"
}


### Query mappings in a date range

curl "http://localhost:8000/mappings?begin=2024-01-01&end=2024-01-10"

### Expected response:
[
  {
    "symbol": "AAPL",
    "identifier": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-05"
  },
  {
    "symbol": "AAPL",
    "identifier": 2,
    "start_date": "2024-01-05",
    "end_date": null
  }
]

## Notes

- Dependencies are defined in pyproject.toml.
- requirements.txt is provided for convenience.
- Focus is on clarity and correctness of symbology semantics rather than production-scale performance.
- **Stretch Goal (Persistent State)**: Persistent storage is implemented as a stretch goal. Mappings are saved and reloaded from disk, maintaining state across restarts.
