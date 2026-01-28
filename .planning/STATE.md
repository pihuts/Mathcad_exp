# Project State

**Project:** Mathcad Automator
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Current Position

**Phase:** 05 - Production Packaging
**Plan:** 02 of 04 in current phase
**Status:** In progress
**Last activity:** 2026-01-28 - Completed Plan 05-02 (pywebview Integration with native desktop window).

Progress: ████████████████░░░ 97% (33/34 plans complete)

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
| **3.4 Multi-Value String Inputs** | **List tab entry with deduplication** | **Complete** |
| **4. Library** | **Configuration persistence** | **Complete** |
| **5. Packaging** | **Standalone distribution** | **In progress** |

## Context & Memory

### Active Context
- **Focus:** Phase 4 (Library & Persistence) backend implementation complete - BatchConfig model, save, list, and load endpoints all functional.
- **Architecture:** Complete batch and workflow system with string/numeric input support, export options (PDF/MCDX), native file browsing, MathcadPy integration, and library persistence.
- **Risk:** None currently.

### Recent Decisions
- **pywebview Integration (05-02):** Implemented native desktop window using pywebview.create_window(). Server runs in multiprocessing.Process with wait_for_server() health check before UI launch. Window closure triggers server termination (terminate/kill sequence). Bundled webview, pythonnet, clr_loader, and WebView2 DLLs in PyInstaller spec.
- **Multiprocessing Architecture:** Main process manages pywebview GUI, subprocess runs FastAPI server. Clean separation enables proper lifecycle management and graceful shutdown.
- **urllib for Health Check:** Used urllib.request for server readiness polling (no external dependencies). Polls /health endpoint every 0.3s for up to 30s.
- **PyInstaller Configuration (05-01):** Created main.py entry point with freeze_support() and resource_path() helper. Configured main.spec with uvicorn collect_submodules(), hidden imports for pywin32/comtypes, and onedir mode to reduce antivirus false positives. Updated src/server/main.py with get_frontend_path() for PyInstaller/dev detection and added /health endpoint.
- **Packaging Dependencies (05-01):** Added pyinstaller>=6.0.0, pywebview>=5.0.0, and psutil>=5.9.0 to requirements.txt.
- **OneDir Bundle Mode:** Use onedir (folder-based) distribution instead of onefile to reduce antivirus false positives and improve startup time.
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
- **Library Persistence (04-01):** Created BatchConfig Pydantic model for type-safe config serialization. Implemented POST /library/save endpoint that stores configs as JSON in {filename}_configs/ directories with relative paths for portability.
- **Library List/Load (04-02):** Implemented GET /library/list endpoint for browsing saved configs (returns metadata only). Implemented POST /library/load endpoint for loading configs with path resolution (relative to absolute). Uses BatchConfig.model_validate() for validation.
- **Frontend Library API (04-03):** Created TypeScript interfaces in api.ts matching backend schemas exactly (LibraryConfigMetadata, ListLibraryConfigsResponse, SaveLibraryConfigRequest, SaveLibraryConfigResponse, LoadLibraryConfigRequest, LoadLibraryConfigResponse). Implemented saveLibraryConfig, listLibraryConfigs, loadLibraryConfig API functions using axios. Created useLibrary React Query hook with 5-minute cache, automatic invalidation after save, and loading/error states for UI binding.
- **Library UI Modal (04-04):** Created LibraryModal component with two-tab design (Save/Load) for configuration management. Save tab has name input with save button and success badge; Load tab displays table of saved configs with load buttons. Added Library button to Batch tab with IconFolder icon. Implemented handleLoadLibraryConfig function to convert loaded configs back to aliasConfigs structure. Used IconDeviceFloppy instead of IconSave (doesn't exist in @tabler/icons-react). Refetch configs when modal opens for fresh list. Auto-close modal 1.5s after successful save.
- **Multi-Value String List Tab (03.4-01):** Added List tab to InputModal for string type with textarea entry (one value per line). Implemented silent deduplication using Set for both List tab and CSV string modes. Added unique value count preview that updates live as user types. Changed default tab for string type from 'single' to 'list' since multi-value entry is the primary use case. Used split(/\r?\n/) regex for cross-platform line ending handling (Windows CRLF and Unix LF).
- **Iteration Breakdown Tooltip (03.4-01):** Added iterationBreakdown useMemo showing per-input counts, types (string/number), and multiplication formula. Replaced Total Iterations Text with conditional Tooltip wrapper featuring dotted underline and help cursor. Enhanced handleLoadLibraryConfig to restore aliasTypes via typeof detection on array elements for correct type labels in iteration tooltip.
- **Batch Threading:** BatchManager uses a background thread to prevent blocking the FastAPI event loop.
- **InputConfig Dataclass:** Added to protocol.py for type-safe, units-aware input configuration.
- **Workflow Data Models:** Added FileMapping, WorkflowFile, WorkflowConfig (Pydantic BaseModels).
- **BatchConfig Model:** Added Pydantic BaseModel for library persistence with version field and relative path support.
- **Library Save Endpoint:** POST /library/save saves configs as JSON in {filename}_configs/ directories adjacent to .mcdx files.
- **Relative Path Storage:** file_path stored as filename only, output_dir relative to mcdx parent for cross-machine portability.
- **Config Directory Pattern:** {mcdx_filename}_configs/ organization for natural discovery and management.

### Roadmap Evolution
- Phase 2.1 inserted after Phase 2: MathcadPy Migration (COMPLETED)
- Phase 2.2 inserted after Phase 2.1: Input Units Specification (COMPLETED)
- Phase 3: Workflow Orchestration (COMPLETED)
- Phase 3.1 inserted after Phase 3: Replace text inputs with browse buttons (COMPLETED) - Implemented native file browsing.
- Phase 3.2 inserted after Phase 3.1: Export Options (MCDX/PDF) (COMPLETED) - Implemented dynamic naming and native file opening.
- Phase 3.3 added: String Inputs - Support for string-type inputs in addition to numeric inputs (COMPLETED).
- Phase 3.4 added: Multi-Value String Inputs - List tab with textarea entry and deduplication (Complete).
- Phase 4: Library & Persistence (Complete).
- Phase 5: Production Packaging (In Progress) - 2 of 4 plans complete.

### Performance Metrics
- **Requirements Covered:** 100% (Phase 1), 100% (Phase 2), 100% (Phase 3.1)
- **Orphans:** 0
- **Known Gaps:** Parallel execution (deferred to v2).

## Session Continuity

**Session:** 2026-01-28 - Present
**Stopped at:** Completed Phase 05-02 (pywebview Integration with native desktop window)
**Resume file:** None

### Last Session
- Executed Plan 05-02 (pywebview Integration).
- Updated main.py with multiprocessing architecture: server_process runs FastAPI, webview.create_window() displays native GUI.
- Added wait_for_server() function using urllib for health check polling before UI launch.
- Updated main.spec with collect_submodules('webview'), collect_data_files('webview'), pythonnet/WinForms imports.
- Built executable (24.5 MB) with webview, pythonnet, clr_loader, and WebView2 DLLs bundled.
- Expected build warnings (System.* modules, bottle conditional) are normal and don't affect functionality.

### Next Steps
1. **Next:** Plan 05-03 (Process Lifecycle) - Implement dirty state checking and graceful shutdown
2. Phase 5 Plan 05-04 - Polish for distribution (console window, icons, final testing)
