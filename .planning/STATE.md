# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 2.2 - Input Units Specification
**Plan:** 3 of 5 in current phase
**Status:** Phase complete
**Last activity:** 2026-01-26 - Batch manager builds InputConfig objects with units preservation.

Progress: ███████████░░░░ 79% (11/14 known plans complete)

| Phase | Goal | Status |
|-------|------|--------|
| **1. Core Engine** | **Reliable Mathcad control & COM stability** | **Complete** |
| 2. Batch Processing | Parameter studies & Output generation | In Progress (5/6) |
| **2.1 MathcadPy Migration** | **Replace COM with MathcadPy library** | **Complete** |
| **2.2 Input Units Specification** | **Add option to specify units for inputs** | **Complete** |
| 3. Workflow | Multi-file chaining | Pending |
| 4. Library | Configuration persistence | Pending |
| 5. Packaging | Standalone distribution | Pending |

## Context & Memory

### Active Context
- **Focus:** Backend orchestration with stable MathcadPy integration.
- **Risk:** MathcadPy library provides tested COM abstraction; needs real-world validation.
- **Architecture:** Sidecar pattern operational. BatchManager runs in background thread. Worker uses MathcadPy abstraction.

### Recent Decisions
- **MathcadPrime.Application:** Switched to this ProgID as it is the registered one in the environment.
- **Batch Threading:** BatchManager uses a background thread to prevent blocking the FastAPI event loop.
- **None-Safety:** Hardened EngineManager with checks to prevent crashes during process lifecycle transitions.
- **Lazy Imports:** Used to break circular dependency between EngineManager and BatchManager.
- **Per-Alias Configuration:** Frontend UI now allows configuring each input alias individually via Range or CSV.
- **MathcadPy Migration:** COMPLETED - Replaced fragile COM implementation with mature MathcadPy library. Uses file extension detection, automatic COM initialization, tuple unwrapping.
- **InputConfig Dataclass:** Added to protocol.py for type-safe, units-aware input configuration. Uses Optional[str] for units with None default to preserve worksheet default behavior.
- **Dual-Format Input Support:** Batch manager supports both new structured format ({"L": {"value": 10, "units": "ft"}}) and legacy simple dict ({"L": 10, "P": 5}) for gradual migration.

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED) - Replaced fragile COM implementation with stable MathcadPy library
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED) - Added InputConfig dataclass for units-aware input specification (in, ft, kip, blank)

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), ~70% (Phase 2)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

### Last Session
- Completed Phase 2.2 Plan 03: Batch Manager InputConfig Integration.
- Updated batch_manager to import InputConfig and build InputConfig objects from row_input
- Implemented dual-format support: new structured format with units and legacy simple dict format
- Units field preserved when present in row_input, defaults to None for legacy compatibility
- Harness already updated in plan 02.2-02 to process InputConfig array with units

### Next Steps
1. **Next:** Phase 2.2 Plan 04 - Frontend Units UI Integration
2. Then: Phase 2.2 Plan 05 - E2E Testing with Units
3. After Phase 2.2 complete: Phase 3 - Workflow Orchestration (multi-file chaining)
