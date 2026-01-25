# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 2.2 - Input Units Specification
**Plan:** 2 of 5 in current phase
**Status:** In progress
**Last activity:** 2026-01-26 - Worker and harness units support for InputConfig array.

Progress: ████████████░░░ 71% (10/14 known plans complete)

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

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED) - Replaced fragile COM implementation with stable MathcadPy library
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED) - Added InputConfig dataclass for units-aware input specification (in, ft, kip, blank)

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), ~70% (Phase 2)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

### Last Session
- Completed Phase 2.2 Plan 02: Worker and Harness Units Support.
- Updated worker.set_input() to accept optional units parameter with type hint
- Updated harness.calculate_job() to process InputConfig array instead of simple dict
- Backward compatibility maintained for old dict-based input format
- Units parameter correctly passed to MathcadPy's set_real_input()

### Next Steps
1. **Next:** Phase 2.2 Plan 03 - (check plan file for details)
2. Then: Remaining Phase 2.2 plans (04, 05)
3. After Phase 2.2 complete: Phase 3 - Workflow Orchestration (multi-file chaining)
