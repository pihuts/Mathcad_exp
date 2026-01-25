# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 2.2 - Input Units Specification
**Plan:** 4 of 5 in current phase
**Status:** In progress
**Last activity:** 2026-01-26 - Added InputConfig TypeScript interface and units selector UI to InputModal.

Progress: ██████████░░░░ 84% (12/14 known plans complete)

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
- **Focus:** Frontend UI for units specification with InputConfig type safety.
- **Risk:** Mantine v7 Select doesn't support creatable prop - custom unit entry requires additional implementation.
- **Architecture:** Frontend now uses InputConfig interface matching backend dataclass structure.

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

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED) - Replaced fragile COM implementation with stable MathcadPy library
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED) - Added InputConfig dataclass for units-aware input specification (in, ft, kip, blank)

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), ~70% (Phase 2)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

### Last Session
- Completed Phase 2.2 Plan 04: Frontend Units UI Integration.
- Added InputConfig TypeScript interface to api.ts with alias, value, and optional units fields
- Created UNIT_PRESETS constant with 16 common engineering units in InputModal.tsx
- Updated InputModalProps interface to accept InputConfig instead of any[]
- Added units selector with Mantine Select component (searchable, clearable)
- Modified handleSave to return InputConfig object with alias, value, and units fields
- Note: Mantine v7 Select doesn't support creatable prop - custom unit entry not available

### Next Steps
1. **Next:** Phase 2.2 Plan 05 - E2E Testing with Units
2. Then: After Phase 2.2 complete: Phase 3 - Workflow Orchestration (multi-file chaining)
