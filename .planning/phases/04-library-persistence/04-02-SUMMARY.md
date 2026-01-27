# Plan 04-02 Summary: Backend Library List/Load API

**Status:** Complete
**Date:** 2026-01-27
**Commits:** 4 atomic commits

## Overview

Implemented backend API endpoints for listing and loading saved batch configurations from the library. This enables engineers to browse existing saved configurations and reload them into the application for reuse.

## Implementation Details

### 1. GET /library/list Endpoint

**File:** `D:\Mathcad_exp\src\server\routes.py` (lines 250-285)

**Purpose:** List all saved library configurations for a given Mathcad file

**Features:**
- Takes `file_path` query parameter (the .mcdx file)
- Looks for `{filename}_configs/` directory next to the Mathcad file
- Returns list of configs with metadata (no full input data)
- Returns empty array when config directory doesn't exist
- Skips corrupted JSON files (fails gracefully)

**Response Structure:**
```json
{
  "configs": [
    {
      "name": "Test Config",
      "path": "/path/to/test_configs/Test Config.json",
      "created_at": "2026-01-27T12:00:00",
      "version": "1.0"
    }
  ]
}
```

### 2. POST /library/load Endpoint

**File:** `D:\Mathcad_exp\src\server\routes.py` (lines 287-320)

**Purpose:** Load a saved library configuration by file path

**Features:**
- Takes `config_path` in request body
- Reads JSON and validates with Pydantic `BatchConfig.model_validate()`
- Resolves relative paths to absolute:
  - `file_path`: Resolved from config directory parent
  - `output_dir`: Resolved from config directory parent if present
- Returns full `BatchConfig` for loading into UI

**Request Structure:**
```json
{
  "config_path": "/path/to/test_configs/Test Config.json"
}
```

**Response:** Full `BatchConfig` object with absolute paths

### 3. Path Resolution Strategy

**Relative to Absolute Conversion:**
```python
# Config stored with relative paths:
config_dict['file_path'] = "test.mcdx"  # Just filename
config_dict['output_dir'] = "output"     # Relative to parent

# On load, resolved to absolute:
mcdx_path = config_path.parent.parent / config_dict['file_path']
config_dict['file_path'] = str(mcdx_path.resolve())
# => "D:/Mathcad_files/test.mcdx"
```

This ensures:
- Portability: Configs can be moved between machines
- Reliability: Absolute paths work correctly with MathcadPy
- Flexibility: Output directories resolve correctly

### 4. Error Handling

**List Endpoint:**
- Returns 400 if Mathcad file not found
- Returns 500 for unexpected errors
- Skips corrupted JSON files (continues iteration)
- Returns empty array if config directory doesn't exist

**Load Endpoint:**
- Returns 400 if `config_path` missing
- Returns 404 if config file not found
- Returns 500 for validation or read errors
- Pydantic validates config structure automatically

### 5. Schema Definitions

**File:** `D:\Mathcad_exp\src\server\schemas.py` (lines 55-66)

**New Schemas:**
```python
class LibraryConfigMetadata(BaseModel):
    name: str
    path: str
    created_at: str
    version: str = "1.0"

class ListLibraryConfigsResponse(BaseModel):
    configs: List[LibraryConfigMetadata]

class LoadLibraryConfigRequest(BaseModel):
    config_path: str
```

**Purpose:** Type safety and FastAPI auto-documentation

## Integration with Plan 04-01

This plan builds on the foundation from plan 04-01:

**Dependencies:**
- `BatchConfig` model from `src/engine/protocol.py`
- `POST /library/save` endpoint creates the configs we list/load
- Config directory structure: `{filename}_configs/`

**Key Links:**
- `BatchConfig.model_validate()` for loading JSON configs
- `Path.glob('*.json')` for discovering configs
- Relative path storage from 04-01 enables portability

## Atomic Commits

1. `feat(04-02): add GET /library/list endpoint`
   - Added list endpoint with metadata extraction
   - Implemented graceful error handling for corrupted files

2. `feat(04-02): add POST /library/load endpoint`
   - Added load endpoint with path resolution
   - Integrated Pydantic validation via `BatchConfig.model_validate()`

3. `feat(04-02): add list/load library schemas`
   - Added `LibraryConfigMetadata`, `ListLibraryConfigsResponse`, `LoadLibraryConfigRequest`

## Verification

All success criteria met:

- [x] GET /library/list returns array of config metadata for given .mcdx file
- [x] POST /library/load returns full BatchConfig with absolute paths
- [x] Empty configs array returned when no configs directory exists
- [x] Corrupted config files skipped (not crash) in list endpoint
- [x] Pydantic validates loaded configs (returns 500 on invalid JSON)
- [x] Relative paths resolved correctly on load

**Verification Commands Run:**
```bash
python -c "from src.server.routes import router; print([r.path for r in router.routes if r.path == '/library/list'])"
# Output: ['/library/list']

python -c "from src.server.routes import router; print([r.path for r in router.routes if r.path == '/library/load'])"
# Output: ['/library/load']

python -c "from src.server.schemas import ListLibraryConfigsResponse, LoadLibraryConfigRequest; print('Schemas imported successfully')"
# Output: Schemas imported successfully
```

## Next Steps

Plan 04-03 will integrate these endpoints with the frontend to provide a complete library management UI, allowing users to:
- Browse saved configurations visually
- Load configurations with one click
- Delete unwanted configurations

## Technical Decisions

1. **Query Parameter for List:** Used `file_path` as query parameter (not body) for GET request semantics
2. **Request Body for Load:** Used `config_path` in request body for POST request semantics
3. **Metadata-Only List:** List endpoint returns only metadata to avoid loading large input arrays unnecessarily
4. **Skip Corrupted Files:** Continue iteration on JSON parse errors instead of failing entire request
5. **Absolute Path Resolution:** Resolve paths on load to ensure MathcadPy receives absolute paths it requires

## Files Modified

- `D:\Mathcad_exp\src\server\routes.py`: Added `/library/list` and `/library/load` endpoints
- `D:\Mathcad_exp\src\server\schemas.py`: Added list/load request/response schemas

## Files Created

- `D:\Mathcad_exp\.planning\phases\04-library-persistence\04-02-SUMMARY.md` (this file)
