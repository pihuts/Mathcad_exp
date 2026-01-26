# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 3.2 - Export Options (MCDX/PDF) (In Progress)
**Status:** Active
**Last activity:** 2026-01-27 - Completed Plan 03.2-02 (Export UI checkboxes).

Progress: ████████████████ 100% (25/25 plans complete)

| Phase | Goal | Status |
|-------|------|--------|
| **1. Core Engine** | **Reliable Mathcad control & COM stability** | **Complete** |
| 2. Batch Processing | Parameter studies & Output generation | Complete |
| **2.1 MathcadPy Migration** | **Replace COM with MathcadPy library** | **Complete** |
| **2.2 Input Units Specification** | **Add option to specify units for inputs** | **Complete** |
| 3. Workflow | Multi-file chaining | Complete |
| **3.1 Browse Buttons** | **Native file dialogs for file selection** | **Complete** |
| **3.2 Export Options** | **MCDX/PDF export options** | **Complete** |
| 4. Library | Configuration persistence | Pending |
| 5. Packaging | Standalone distribution | Pending |

## Context & Memory

### Active Context
- **Focus:** Export Options Implementation - PDF and MCDX format selection.
- **Architecture:** Frontend checkboxes pass export flags to backend, ResultsList displays generated files with native opening.
- **Risk:** None currently.

### Recent Decisions
- **Export Format Selection:** Added checkboxes for PDF and MCDX export in both Batch and Workflow tabs. Default: PDF enabled, MCDX disabled.
- **Checkboxes Over Radio Buttons:** Allow simultaneous export in both formats for maximum flexibility.
- **ResultsList Component:** Displays generated files newest-first with one-click native opening via backend API.
- **Native File Dialog:** Implemented `_open_file_dialog` in backend (`tkinter` running in `asyncio.to_thread`) to bypass browser security restrictions on file paths.
- **Backend-Driven Browsing:** Frontend Browse button calls API, API opens dialog on server (local machine), returns full path.
- **Browse Button UI:** Replaced plain text inputs with Browse button + filename display text. Full path shown in tooltip to keep UI clean.
- **MathcadPrime.Application:** Switched to this ProgID as it is the registered one in the environment.
- **Batch Threading:** BatchManager uses a background thread to prevent blocking the FastAPI event loop.
- **InputConfig Dataclass:** Added to protocol.py for type-safe, units-aware input configuration.
- **Workflow Data Models:** Added FileMapping, WorkflowFile, WorkflowConfig (Pydantic BaseModels).

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED)
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED)
- Phase 3: Workflow Orchestration (In Progress)
- Phase 3.1 inserted after Phase 3: Replace text inputs with browse buttons (COMPLETED) - Implemented native file browsing.
- Phase 3.2 inserted after Phase 3.1: Export Options (MCDX/PDF) (COMPLETED) - Implemented dynamic naming and native file opening.

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), 100% (Phase 2), 100% (Phase 3.1)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

**Session:** 2026-01-27 - Present
**Stopped at:** Completed Plan 03.2-02
**Resume file:** None

### Last Session
- Executed Plan 03.2-02 (Frontend export UI).
- Added export checkboxes to Batch and Workflow tabs.
- Created ResultsList and BisayaStatus components.
- Updated BatchGrid for native file opening.

### Next Steps
1. **Next:** Plan 03.2-03 - Verification testing (if exists)
2. Or proceed to next feature phase.
