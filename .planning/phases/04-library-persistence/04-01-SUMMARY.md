---
phase: 04-library-persistence
plan: 01
subsystem: api
tags: [pydantic, fastapi, json-persistence, relative-paths]

# Dependency graph
requires:
  - phase: 02-batch-processing-system
    provides: InputConfig dataclass, batch processing infrastructure
  - phase: 03-workflow-orchestration
    provides: WorkflowConfig pattern, export options
provides:
  - BatchConfig Pydantic model for type-safe config serialization
  - POST /library/save endpoint for saving batch configurations
  - SaveLibraryConfigRequest/Response schemas for API validation
  - JSON-based persistence with relative path storage
affects: [04-02-list-and-load, 04-03-frontend-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: Pydantic BaseModel versioning, relative path portability, config directory adjacency

key-files:
  created: []
  modified:
    - src/engine/protocol.py - Added BatchConfig model
    - src/server/routes.py - Added POST /library/save endpoint
    - src/server/schemas.py - Added SaveLibraryConfigRequest/Response (pre-existing)

key-decisions:
  - "Reuse InputConfig dataclass for inputs field - maintains consistency with batch/workflow systems"
  - "Store configs in {filename}_configs/ directories adjacent to .mcdx files - natural organization, easy to find"
  - "Convert paths to relative before saving - enables cross-machine portability"
  - "Include version field in BatchConfig - future-proofing for format changes"

patterns-established:
  - "Pattern 1: Pydantic BaseModel version field - all config models now include version for migration support"
  - "Pattern 2: Relative path storage - file paths stored as filename only, resolved relative to mcdx parent"
  - "Pattern 3: Config directory naming - {mcdx_filename}_configs/ pattern for discoverability"

# Metrics
duration: 2 min
completed: 2026-01-27
---

# Phase 4 Plan 1: Backend Library Persistence Summary

**BatchConfig Pydantic model with POST /library/save endpoint for JSON-based configuration persistence with relative path portability**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-27T15:36:00Z
- **Completed:** 2026-01-27T15:38:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Created BatchConfig Pydantic model with validation and version field
- Implemented POST /library/save endpoint with relative path conversion
- Added SaveLibraryConfigRequest/Response schemas for type-safe API
- Configs stored as JSON in {filename}_configs/ directories next to .mcdx files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create BatchConfig Pydantic model in protocol.py** - `c7ebc62` (feat)
2. **Task 2: Add library save endpoint to routes.py** - `526204b` (feat)
3. **Task 3: Add library request/response schemas to schemas.py** - `dc0765d` (feat, pre-existing)

**Plan metadata:** TBD (docs commit pending)

## Files Created/Modified
- `src/engine/protocol.py` - Added BatchConfig Pydantic model with validation, version, and relative path support
- `src/server/routes.py` - Added POST /library/save endpoint with config validation and JSON persistence
- `src/server/schemas.py` - Added SaveLibraryConfigRequest/Response Pydantic models (pre-existing commit)

## Decisions Made

### Model Design
- **Reuse InputConfig dataclass**: Maintains consistency with existing batch/workflow systems, avoids duplication
- **Version field**: All config models include version string for future migration support
- **Relative path storage**: file_path stored as filename only, output_dir stored relative to mcdx parent
- **base_path field**: Optional field for runtime path resolution (not persisted)

### File Organization
- **{filename}_configs/ pattern**: Config directory created adjacent to .mcdx file with sanitized name
- **Name sanitization**: Only alphanumeric, space, dash, underscore characters allowed in config filenames
- **JSON format**: Human-readable, diff-able, easy to inspect and debug

### API Design
- **Pydantic validation**: Request validated via BatchConfig model before filesystem operations
- **400 on missing mcdx**: Explicit check that source file exists before creating config
- **500 on errors**: Generic error handler for JSON write failures, path resolution issues

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all implementations worked on first attempt, all verification tests passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Backend persistence foundation complete. Ready for:
- **Plan 04-02**: List and load endpoints for retrieving saved configurations
- **Plan 04-03**: Frontend API service and useLibrary hook
- **Plan 04-04**: LibraryModal component for save/load UI

**Blockers/Concerns:** None identified. Relative path approach validated for cross-machine portability.

---
*Phase: 04-library-persistence*
*Completed: 2026-01-27*
