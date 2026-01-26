# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 3.0 - Workflow Orchestration
**Plan:** 5 of 8 in current phase
**Status:** In progress
**Last activity:** 2026-01-26 - Completed 03-05-PLAN.md.

Progress: ███████████████░ 91% (20/22 plans complete)

| Phase | Goal | Status |
|-------|------|--------|
| **1. Core Engine** | **Reliable Mathcad control & COM stability** | **Complete** |
| 2. Batch Processing | Parameter studies & Output generation | Complete |
| **2.1 MathcadPy Migration** | **Replace COM with MathcadPy library** | **Complete** |
| **2.2 Input Units Specification** | **Add option to specify units for inputs** | **Complete** |
| 3. Workflow | Multi-file chaining | In Progress (7/8) |
| 4. Library | Configuration persistence | Pending |
| 5. Packaging | Standalone distribution | Pending |

## Context & Memory

### Active Context
- **Focus:** WorkflowBuilder component with drag-and-drop reordering for workflow file management.
- **Architecture:** DndContext with closestCenter collision detection, DragOverlay for visual feedback during drag operations.
- **Risk:** @mantine/drag-handle package doesn't exist in npm registry (excluded from install).

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
- **Workflow API:** Added 4 REST endpoints (POST /workflows, POST /workflows/{id}/start, GET /workflows/{id}, POST /workflows/{id}/stop) using manager.workflow_manager dependency. Auto-start on submit, time-based ID generation.
- **MappingModal UI:** Modal component for creating FileMapping objects with grouped source selection (upstream files → outputs), target input selection, duplicate detection, add/remove functionality.
- **WorkflowManager Engine:** Background thread execution for multi-file workflows. Linear chain (0,1,2...) with output-to-input mapping. Polls EngineManager.get_job() for completion (30s timeout, 0.5s intervals). Stores intermediate_results dict for downstream mapping.
- **useWorkflow Hook:** Custom React hook with TanStack Query for workflow creation, status polling (1-second interval), and stop functionality. Follows useBatch pattern for consistency.
- **Drag-and-Drop Library:** Selected @hello-pangea/dnd for WorkflowBuilder component (React 18 compatible, maintains focus on drag, closestCenter collision detection). Excluded @mantine/drag-handle (not found in registry).

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED) - Replaced fragile COM implementation with stable MathcadPy library
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED) - Added InputConfig dataclass for units-aware input specification (in, ft, kip, blank)
- Phase 3: Workflow Orchestration (In Progress) - Multi-file chaining with explicit output-to-input mapping

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), 100% (Phase 2), 88% (Phase 3)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

**Session:** 2026-01-26 00:49 - 00:52 UTC
**Stopped at:** Completed 03-05-PLAN.md
**Resume file:** None

### Last Session
- Completed Phase 3 Plan 05: WorkflowBuilder Component.
- Installed @hello-pangea/dnd v18.0.1 for drag-and-drop functionality
- Verified WorkflowBuilder component matches plan specification exactly (168 lines)
- Component enables users to add, reorder, and remove workflow files
- Automatic position updates when files are reordered
- Mappings count badge displays number of input mappings per file
- File removal also removes related mappings
- Deviation: @mantine/drag-handle not found (excluded from install)
- Note: Component was pre-existing from plan 03-02, identical implementation

### Next Steps
1. **Next:** Phase 3 Plan 06 - Next plan in workflow orchestration
2. Then: Complete remaining workflow orchestration plans (2 more)
