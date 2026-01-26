# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 3.0 - Workflow Orchestration
**Plan:** 3 of 8 in current phase
**Status:** In progress
**Last activity:** 2026-01-26 - Added workflow API endpoints to routes.py.

Progress: ████████████░░ 64% (14/22 plans complete)

| Phase | Goal | Status |
|-------|------|--------|
| **1. Core Engine** | **Reliable Mathcad control & COM stability** | **Complete** |
| 2. Batch Processing | Parameter studies & Output generation | Complete |
| **2.1 MathcadPy Migration** | **Replace COM with MathcadPy library** | **Complete** |
| **2.2 Input Units Specification** | **Add option to specify units for inputs** | **Complete** |
| 3. Workflow | Multi-file chaining | In Progress (1/8) |
| 4. Library | Configuration persistence | Pending |
| 5. Packaging | Standalone distribution | Pending |

## Context & Memory

### Active Context
- **Focus:** Workflow API endpoints for frontend integration.
- **Architecture:** REST API endpoints using manager.workflow_manager dependency, following batch endpoint patterns.

### Recent Decisions
- **MathcadPrime.Application:** Switched to this ProgID as it is the registered one in the environment.
- **Batch Threading:** BatchManager uses a background thread to prevent blocking the FastAPI event loop.
- **None-Safety:** Hardened EngineManager with checks to prevent crashes during process lifecycle transitions.
- **Lazy Imports:** Used to break circular dependency between EngineManager and BatchManager.
- **Per-Alias Configuration:** Frontend UI now allows configuring each input alias individually via Range or CSV.
- **MathcadPy Migration:** COMPLETED - Replaced fragile COM implementation with mature MathcadPy library. Uses file extension detection, automatic COM initialization, tuple unwrapping.
- **InputConfig Dataclass:** Added to protocol.py for type-safe, units-aware input configuration. Uses Optional[str] for units with None default to preserve worksheet default behavior.
- **Dual-Format Input Support:** Batch manager supports both new structured format ({"L": {"value": 10, "units": "ft"}}) and legacy simple dict ({"L": 10, "P": 5}) for gradual migration.
- **Frontend InputConfig Interface:** TypeScript interface mirroring backend dataclass with alias, value, and optional units fields for type safety across frontend.
- **Workflow Data Models:** Added FileMapping, WorkflowFile, WorkflowConfig (Pydantic BaseModels) for type-safe workflow configuration. Uses linear chain via position field (0,1,2 for A→B→C) and explicit mapping via FileMapping (source_alias→target_alias).

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED) - Replaced fragile COM implementation with stable MathcadPy library
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED) - Added InputConfig dataclass for units-aware input specification (in, ft, kip, blank)
- Phase 3: Workflow Orchestration (In Progress) - Multi-file chaining with explicit output-to-input mapping

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), 100% (Phase 2), 13% (Phase 3)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

### Last Session
- Completed Phase 3 Plan 01: Workflow Data Models.
- Added FileMapping Pydantic BaseModel for output-to-input mapping
- Added WorkflowFile Pydantic BaseModel with file_path, inputs, position fields
- Added WorkflowConfig Pydantic BaseModel with name, files, mappings, stop_on_error
- Added WorkflowStatus Enum (PENDING, RUNNING, COMPLETED, FAILED, STOPPED)
- Added WorkflowState dataclass for runtime execution tracking
- WorkflowFile reuses existing InputConfig type for inputs field

### Next Steps
1. **Next:** Phase 3 Plan 02 - Workflow Execution Engine
2. Then: Continue workflow orchestration plans
