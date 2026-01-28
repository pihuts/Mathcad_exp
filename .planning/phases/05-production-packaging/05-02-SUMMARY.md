---
phase: 05-production-packaging
plan: 02
subsystem: desktop-packaging
tags: [pywebview, multiprocessing, native-window, pyinstaller]

# Dependency graph
requires:
  - phase: 05-production-packaging
    plan: 01
    provides: PyInstaller basic integration with main.py entry point and main.spec configuration
provides:
  - Native desktop window using pywebview (no browser required)
  - Multiprocessing architecture with FastAPI server in separate process
  - Server readiness check before UI launch
  - Proper server cleanup on window close
affects: [05-03-process-lifecycle, 05-04-polish]

# Tech tracking
tech-stack:
  added: [pywebview>=5.0.0, pythonnet>=3.0.0]
  patterns: [multiprocessing for process isolation, health-check polling for startup coordination]

key-files:
  created: []
  modified: [main.py, main.spec]

key-decisions:
  - "Use pywebview for native window instead of browser"
  - "Server runs in multiprocessing.Process for clean separation"
  - "urllib for health check (no extra dependencies)"
  - "Window closure triggers server termination"

patterns-established:
  - "Pattern: Multiprocessing architecture for desktop apps - main process manages GUI, subprocess handles server"
  - "Pattern: Health check polling with timeout - wait_for_server() polls /health endpoint before launching UI"
  - "Pattern: Explicit process cleanup - terminate/kill sequence on window close"

# Metrics
duration: 28min
completed: 2026-01-28
---

# Phase 5 Plan 2: pywebview Integration Summary

**Native desktop window with multiprocessing architecture - pywebview displays React frontend in OS chrome window while FastAPI runs in separate process**

## Performance

- **Duration:** 28 min (1713 seconds)
- **Started:** 2026-01-28T12:29:05Z
- **Completed:** 2026-01-28T12:57:38Z
- **Tasks:** 3 (2 auto, 1 manual)
- **Files modified:** 2

## Accomplishments

- Implemented pywebview native window replacing browser-based UI access
- Configured multiprocessing architecture with FastAPI server in separate process
- Added server health check with urllib polling before UI launch
- Bundled pywebview dependencies (webview, pythonnet, clr_loader, WebView2 DLLs) in PyInstaller spec
- Built executable (24.5 MB) with all required dependencies

## Task Commits

Each task was committed atomically:

1. **Task 1: Update main.py with pywebview and multiprocessing architecture** - `07434be` (feat)
2. **Task 2: Update main.spec with pywebview dependencies** - `ca037cc` (feat)
3. **Task 3: Test pywebview integration** - N/A (manual verification)

**Plan metadata:** Not yet committed

## Files Created/Modified

- `main.py` - Complete rewrite with multiprocessing architecture, pywebview.create_window(), wait_for_server() health check, server cleanup on window close
- `main.spec` - Added collect_submodules('webview'), collect_data_files('webview'), pythonnet/WinForms hidden imports

## Technical Implementation

### Multiprocessing Architecture

```
main.py (Main Process)
  ├─> multiprocessing.Process -> run_server()
  │     └─> uvicorn.run(FastAPI app) :8000
  │
  └─> wait_for_server() - polls /health endpoint
        └─> webview.create_window() - native GUI
              └─> webview.start() - blocks until close
                    └─> server_process.terminate() - cleanup
```

### Configuration Constants

- `SERVER_HOST`: "127.0.0.1"
- `SERVER_PORT`: 8000
- `WINDOW_TITLE`: "Mathcad Automator"
- `WINDOW_WIDTH`: 1280, `WINDOW_HEIGHT`: 800
- `SERVER_STARTUP_TIMEOUT`: 30 seconds

### Bundled Dependencies (verified in dist/MathcadAutomator/_internal/)

- `webview/` - pywebview package with platform-specific code
- `pythonnet/` - .NET integration for WinForms backend
- `webview/lib/Microsoft.Web.WebView2.Core.dll` - WebView2 runtime
- `webview/lib/Microsoft.Web.WebView2.WinForms.dll` - WinForms wrapper
- `webview/lib/WebBrowserInterop.*.dll` - COM interop
- `webview/js/` - JavaScript injection files for bridge API

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

### PyInstaller Build Timing

- **Issue:** First build completed before main.spec changes were saved
- **Resolution:** Manually triggered rebuild with `rm -rf dist && pyinstaller main.spec -y`
- **Impact:** Minor delay, no code changes required

### Expected Build Warnings

- **System.* module not found:** Expected - pythonnet's clr module provides these at runtime
- **bottle conditional:** Expected - pywebview uses bottle optionally for HTTP server (not used in our architecture)
- **jnius missing:** Expected - Android-specific (Windows build)

These warnings are documented in PyInstaller hooks and do not affect functionality.

## User Setup Required

None - no external service configuration required.

## Verification Steps (Manual)

Since Task 3 requires manual GUI testing, verification steps for user:

1. **Development Mode Test:**
   ```bash
   pip install pywebview
   python main.py
   ```
   Expected: Native window opens, frontend loads, closing window terminates server

2. **Packaged Mode Test:**
   ```bash
   dist\MathcadAutomator\MathcadAutomator.exe
   ```
   Expected: Same behavior as dev mode, no browser window opens

3. **Process Verification:**
   ```bash
   tasklist | findstr MathcadAutomator
   ```
   Expected: Single main process (server is subprocess)

4. **Server Health Check:**
   ```bash
   curl http://127.0.0.1:8000/health
   ```
   Expected: `{"status": "healthy"}` while app is running

## Next Phase Readiness

### Ready for 05-03 (Process Lifecycle)

- Multiprocessing foundation in place
- Server process reference available (`server_process`)
- Window event loop running (`webview.start()`)

### Handoff Items for 05-03

- `confirm_close=False` placeholder in webview.create_window() - 05-03 will implement dirty state check
- Server cleanup logic exists but can be enhanced for graceful shutdown
- No open Mathcad worksheets tracking yet (needed for "operation in progress" prompt)

### Potential Improvements (Deferred)

- Bottle dependency not explicitly bundled (conditional dependency, may not be needed)
- Window size/position persistence (user preference, noted in CONTEXT.md as Claude's discretion)
- Single-instance enforcement (prevent multiple app windows)

---

*Phase: 05-production-packaging*
*Completed: 2026-01-28*
