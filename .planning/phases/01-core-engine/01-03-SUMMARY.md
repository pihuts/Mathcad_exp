---
phase: 01-core-engine
plan: 03
subsystem: api
tags: [fastapi, python, rest, async]
requires: [02]
provides: [api-server]
affects: [04-batch-processing]
tech-stack:
  added: [fastapi, uvicorn, pydantic, requests, httpx]
  patterns: [dependency-injection, background-worker, polling]
key-files:
  created:
    - src/server/main.py
    - src/server/routes.py
    - src/server/dependencies.py
    - tests/test_api.py
  modified:
    - src/engine/manager.py
    - tests/test_manager.py
metrics:
  duration: "30 minutes"
  completed: "2026-01-25"
---

# Phase 1 Plan 03: API Layer Summary

Exposed the Mathcad Engine via a FastAPI REST interface, enabling asynchronous job submission, result polling, and remote lifecycle control.

## Key Accomplishments

1.  **FastAPI Integration**:
    - Established `src/server` structure with `main.py`, `routes.py`, and `dependencies.py`.
    - Implemented `lifespan` handler to automatically manage `EngineManager` startup/shutdown.

2.  **Async Result Handling**:
    - Modified `EngineManager` to spawn a background thread (`_collect_results`) that drains the output queue into a `results` dictionary.
    - This enables the API to serve `GET /jobs/{id}` instantly without blocking on the queue.

3.  **Control Endpoints**:
    - Implemented `/control/stop` and `/control/restart` to handle engine resets remotely.
    - Verified process PID changes on restart.

4.  **Verification**:
    - Created `tests/test_api.py` using `TestClient` to verify the full flow (Submit -> Poll -> Result -> Restart).
    - Updated `tests/test_manager.py` to align with the new polling architecture.

## Decisions Made

-   **Result Polling**: Decided to move result collection into the `EngineManager` itself (via background thread) rather than making the API endpoint block on the queue. This decouples the API response time from the engine processing time.
-   **Import Strategy**: Standardized on relative imports (e.g., `from .dependencies`) within `src/server` to ensure compatibility when running via `uvicorn src.server.main:app` from the project root.
-   **Job Identification**: The API returns a UUID `job_id` immediately upon submission, which the client uses to poll for completion.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Import Path Resolution**
-   **Issue**: `ModuleNotFoundError` when importing `server.dependencies` from `routes.py` and `main.py` depending on execution context (test vs uvicorn).
-   **Fix**: Converted all internal `src/server` imports to relative imports (`from . import ...`).
-   **Files modified**: `src/server/main.py`, `src/server/routes.py`.

**2. [Rule 3 - Blocking] Dependency Versions**
-   **Issue**: `fastapi` and `pydantic` version mismatch caused `TypeError` on startup.
-   **Fix**: Upgraded `fastapi`, `pydantic`, and `pydantic-core`.

**3. [Rule 1 - Bug] Test Regression**
-   **Issue**: `EngineManager.get_result()` (blocking pop) clashed with the new background collector thread consuming the queue.
-   **Fix**: Updated `tests/test_manager.py` to use `get_job(id)` with a polling loop, and kept `get_result` as a deprecated fallback that polls the internal dictionary.
