# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 3.3 - String Inputs (Complete)
**Status:** Complete
**Last activity:** 2026-01-27 - Completed Plan 03.3-02 (End-to-end string input verification).

Progress: ███████████████████ 100% (27/27 plans complete)

| Phase | Goal | Status |
|-------|------|--------|
| **1. Core Engine** | **Reliable Mathcad control & COM stability** | **Complete** |
| 2. Batch Processing | Parameter studies & Output generation | Complete |
| **2.1 MathcadPy Migration** | **Replace COM with MathcadPy library** | **Complete** |
| **2.2 Input Units Specification** | **Add option to specify units for inputs** | **Complete** |
| 3. Workflow | Multi-file chaining | Complete |
| **3.1 Browse Buttons** | **Native file dialogs for file selection** | **Complete** |
| **3.2 Export Options** | **MCDX/PDF export options** | **Complete** |
| **3.3 String Inputs** | **Support for string-type inputs** | **Complete** |
| 4. Library | Configuration persistence | Pending |
| 5. Packaging | Standalone distribution | Pending |

## Context & Memory

### Active Context
- **Focus:** All core features complete - ready for Phase 4 (Library) or Phase 5 (Packaging).
- **Architecture:** Complete batch and workflow system with string/numeric input support, export options (PDF/MCDX), native file browsing, and MathcadPy integration.
- **Risk:** None currently.

### Recent Decisions
- **String Input Verification Complete:** End-to-end testing confirmed string input functionality working correctly in both batch and workflow modes with no numeric input regressions.
- **Type Detection via typeof:** Use typeof on first array element instead of explicit inputType field in InputConfig - keeps pipeline simple, YAGNI principle.
- **String Single Value Array Wrapping:** Wrap single string values in array [stringValue] for consistency with batch pipeline cartesian product logic.
- **Conditional Units UI:** Hide Units selector when String type is selected - strings don't have units, cleaner UX.
- **String CSV Preservation:** String CSV values use String() not Number() to preserve type through to MathcadPy set_string_input.
- **File Handle Reuse Optimization:** Track currently open file and skip reopening if same file already open - significant performance improvement for batch processing.
- **Fast Polling for Synchronous Operations:** Reduced polling interval from 0.5s to 0.1s - MathcadPy operations are synchronous, faster polling = faster response.
- **Dynamic File Naming:** Batch exports use `BaseName_ParamName-Value` pattern; Workflow exports use `WorkflowName_StepN_FileName` pattern for traceability.
- **Export Options Defaults:** PDF enabled by default, MCDX disabled by default for both batch and workflow operations.
- **Filename Sanitization:** Replace invalid Windows filename characters with underscore to prevent file system errors.
- **Delete Before Export:** Remove existing files before save_as to avoid Mathcad overwrite prompts that would hang automation.
- **Raw COM SaveAs:** Use raw COM ws_object.SaveAs(str(path)) instead of MathcadPy wrapper for reliable export.
- **Export Format Selection:** Added checkboxes for PDF and MCDX export in both Batch and Workflow tabs.
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
- Phase 3.3 added: String Inputs - Support for string-type inputs in addition to numeric inputs.

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), 100% (Phase 2), 100% (Phase 3.1)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

**Session:** 2026-01-27 - Present
**Stopped at:** Completed Phase 03.3-02 (End-to-end string input verification)
**Resume file:** None

### Last Session
- Executed Plan 03.3-02 (End-to-end string input verification).
- Verified frontend builds successfully with all string input changes.
- User verified string input UI working correctly (SegmentedControl, conditional tabs, string value entry).
- User verified numeric input functionality unchanged (no regressions).
- User verified string values preserved through batch and workflow pipelines.
- String input feature approved for production use.
- Phase 3.3 (String Inputs) complete - 100% of planned features implemented.

### Next Steps
1. **Next:** Phase 4 - Library (Configuration persistence)
2. Or Phase 5 - Packaging (Standalone distribution)
3. All core features complete - ready for deployment or library/packaging phases
