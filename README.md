# Symbology Server

A Python FastAPI Symbology Server that maintains persistent mappings between human-readable symbols (e.g. `NVDA`) and numeric identifiers via an HTTP API for querying/updating mappings over time.

## Features
- HTTP API to register, terminate, and query symbology mappings
- Enforces:
  - One identifier per symbol per date
  - One symbol per identifier per date
  - Persistent mappings until explicit termination
- Retrieve:
  - Identifier for a symbol on a specified date
  - Symbol for an identifier on a specified date
  - All mappings overlapping a specific half-open date range `[begin, end)`
- In-memory `MappingStorage` by default
- Fully automated test suite with `pytest`

## Requirements
- Python ≥ 3.10
- Dependencies listed in `requirements.txt`

## Design Notes
- **Temporal Semantics**: A symbol’s assignment to an identifier is **persistent**. A mapping becomes active
on its `start_date` and remains active until it is explicitly terminated. All dates are ISO-8601 (`YYYY-MM-DD`) and independent of wall-clock time.
- **Reassignment Behavior**: If a symbol is reassigned to a new identifier, the previously active mapping is
then terminated at the new mapping’s start date. This behavior applies to same-day and future-dated reassignments. At any point in time, a symbol and an identifier may be in at most one active mapping.
- **Conflict Handling**: The following invariants are enforced:
  - A symbol may have only one active identifier on a given date
  - An identifier may be assigned to only one symbol on a given date
  Violations raise explicit domain-level exceptions which are surfaced as HTTP errors at the API layer.
- **Storage Model**: The storage layer is implemented as an in-memory collection, which is optimal for clarity and correctness rather than performance or persistence. This helps to keep the focus on symbology semantics and temporal reasoning.
- **Scope and Limitations**: This symbology server implementation intentionally omits database persistence, concurrency control, and timezone normalization. These concerns are independent from the core problem and
can be layered on without changing the domain model.
- **Extensibility**: The domain model is intentionally decoupled from the storage layer, which allows alternative backends (e.g. database-backed, append-only log-based storage) to be introduced without changing any symbology semantics.
- **Determinism**: All query results are deterministic functions of the input date parameters and stored mappings.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Server

uvicorn src.main:app --reload --port 8000

## Running Tests

pytest tests/

## Example Usage of API

curl -X POST http://localhost:8000/mapping \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","identifier":1,"start_date":"2024-01-01"}'

## Notes

- Dependencies are defined in pyproject.toml.
- requirements.txt is provided for convenience (pip install -r requirements.txt).
- This project focuses on clarity and correctness of symbology semantics rather than concerns at a production scale.
