# AVALYOS Quantum Backend - Status Summary

## Status: ✅ Production Ready

### What's Working

1. **Backend Service** (`aval_backend.py`)
   - Single-file FastAPI application
   - All 4 endpoints registered and functional:
     - `GET /` - Health check
     - `GET /sample` - Sample one branch via Q#
     - `GET /sample/many/{n}` - Monte Carlo sampling (n samples)
     - `GET /branches/{company}` - List branches by company
   - Worker thread for Q# operations (thread-safe)
   - Rate limiting per API key
   - CORS enabled
   - Optional authentication via `AVAL_API_KEY` env var

2. **Dataset**
   - Complete `companies.json` with hierarchical structure
   - 20 companies across multiple continents/countries/states/cities
   - Indexed by company for fast lookups
   - Auto-loaded at startup

3. **Unit Tests** (`tests/test_backend.py`)
   - ✅ 4/4 tests passing
   - Health check test
   - Sample one branch test
   - Sample many branches test (with distribution)
   - Branches lookup test
   - Tests mock Q# calls to avoid runtime dependencies

4. **Dependencies**
   - All required packages installed in virtualenv:
     - FastAPI 0.122.0
     - Uvicorn 0.38.0
     - Pydantic 2.12.5
     - pytest 9.0.1
     - qsharp 1.22.0

### Running the Backend

```bash
# Development mode with auto-reload
uvicorn aval_backend:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn aval_backend:app --host 0.0.0.0 --port 8000 --workers 1
```

### Running Tests

```bash
# All tests
pytest tests/test_backend.py -v

# Specific test
pytest tests/test_backend.py::test_sample_one -v
```

### API Examples

```bash
# Health check
curl http://localhost:8000/

# Sample one branch
curl http://localhost:8000/sample

# Sample 5 branches with distribution
curl http://localhost:8000/sample/many/5

# Get branches for a company
curl http://localhost:8000/branches/Microsoft
```

### With Authentication

```bash
export AVAL_API_KEY=my-secret-key
uvicorn aval_backend:app --host 0.0.0.0 --port 8000

# Requests must include the API key
curl -H "X-API-Key: my-secret-key" http://localhost:8000/sample
```

### Known Limitations / Notes

1. **Q# Thread-Safety**: The Q# interpreter is not thread-safe. All Q# operations are serialized through a dedicated worker thread using a task queue. This prevents the "unsendable across threads" panic.

2. **Q# Runtime**: The backend optionally initializes Q# at startup. If Q# fails to initialize (e.g., missing `qsharp.json`), endpoints that call Q# will fail gracefully with 500 errors. Unit tests don't require Q# since they mock the calls.

3. **Rate Limiting**: Configurable via `AVAL_RATE_PER_MIN` env var (default 60 requests/min per API key).

4. **Queue Backpressure**: Returns 429 (Server Busy) if the Q# operation queue is full. Max queue size configurable via `QSHARP_QUEUE_MAX` env var (default 64).

5. **CORS**: Locked to `ALLOWED_ORIGINS` env var or localhost. Adjust for production.

### Recent Fixes

- Fixed `from __future__ import annotations` placement (moved to top of file)
- Removed duplicate endpoint definitions
- Cleaned up malformed imports section
- Verified all tests pass with mocked Q# calls
- Confirmed routes are registered correctly

