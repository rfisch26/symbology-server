# Symbology Server

A Python FastAPI Symbology Server that maintains persistent mappings between human-readable symbols (e.g. `NVDA`) and numeric identifiers via an HTTP API for querying/updating symbol and identifier mappings over time.

## Features
- HTTP API to register, terminate, and query symbology mappings
- Enforces the following domain constraints:
  - One identifier per symbol per date
  - One symbol per identifier per date
  - Persistent mappings until explicit termination
- Retrieve:
  - Identifier for a symbol on a specified date
  - Symbol for an identifier on a specified date
  - All mappings overlapping a specific half-open date range `[begin, end)`
- In-memory `MappingStorage` by default
- Fully automated test suite using `pytest`

## Requirements
- Python ≥ 3.10
- Dependencies listed in `requirements.txt` and `pyproject.toml`

## Design Notes
- **Temporal Semantics**: A symbol’s assignment to an identifier is **persistent**. A mapping becomes active
on its `start_date` and remains active until it is explicitly terminated. All dates are ISO-8601 (`YYYY-MM-DD`) and independent of wall-clock time.
- **Reassignment Behavior**: If a symbol is reassigned to a new identifier, the previously active mapping is
then terminated at the new mapping’s start date. Each symbol and identifier can only appear in one active mapping at a time.
- **Conflict Handling**: Violations of the following invariants raise explicit domain-level exceptions (surfaced as HTTP errors):
  - A symbol may have only one active identifier on a given date
  - An identifier may be assigned to only one symbol on a given date
- **Storage Model**: Uses an **in-memory storage layer** for clarity and correctness. Alternative storage backends (database, append-only log, etc.) can be introduced without changing the domain model.
- **Scope and Limitations**: This implementation omits:
  - Database persistence
  - Concurrency control
  - Timezone normalization
- **Determinism**: All query results are deterministic functions of input dates and stored mappings.

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

- The API will be available at http://localhost:8000.

## Running Tests

pytest tests/

## Example API Usage

### Add a mapping

curl -X POST http://localhost:8000/mapping \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","identifier":1,"start_date":"2024-01-01"}'


### Query identifier for a symbol

curl "http://localhost:8000/symbol/AAPL?date=2024-01-02"


### Terminate a mapping

curl -X POST http://localhost:8000/mapping/terminate \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","end_date":"2024-01-05"}'


### Query mappings in a date range

curl "http://localhost:8000/mappings?begin=2024-01-01&end=2024-01-10"

## Notes

- Dependencies are defined in pyproject.toml.
- requirements.txt is provided for convenience.
- Focus is on clarity and correctness of symbology semantics rather than production-scale performance.
