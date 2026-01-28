# Phase 5: Production Packaging - Context

**Gathered:** 2026-01-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Transform the development setup (Python + Node + browser) into a standalone Windows application. Users should be able to run the tool from a single `.exe` file without installing Python, Node, or any dependencies. Application must open in a native window (not browser), and cleanly close all child processes (Mathcad, backend) when the window is closed.

</domain>

<decisions>
## Implementation Decisions

### Installer & Deployment
- **Single portable .exe** — No installer package, user can run from anywhere
- **No shortcuts** — User runs the .exe directly, no desktop or Start Menu entries created
- **No auto-update** — Users manually download new .exe versions when released

### Window Behavior
- **Native OS chrome** — Standard Windows title bar with minimize/maximize/close buttons
- **Prompt on close during operation** — Show "Operation in progress. Are you sure?" dialog before closing if batch/workflow is running
- **No system tray** — Standard window behavior only (minimize to taskbar, close exits app)

### Bundling Strategy
- **Require separate Mathcad install** — User must install Mathcad Prime separately (not bundled)
- **Bundle Python 3.11 runtime** — Embed Python 3.11 and all dependencies for true standalone operation (target users are non-technical)

### Error Handling & Recovery
- **Check for Mathcad on first run** — Display clear error message if Mathcad Prime not found, with installation instructions
- **No telemetry** — All errors stay local, users report issues manually if needed

### Claude's Discretion
- User-specific data storage location (AppData vs exe directory)
- Frontend asset packaging approach (embedded vs extracted)
- Window size/position persistence between sessions
- Log file storage location
- Corrupted state recovery strategy

</decisions>

<specifics>
## Specific Ideas

- Target users are "complete newbies (not techy)" — prioritize simplicity over advanced features
- Use Python 3.11 specifically for runtime bundling

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-production-packaging*
*Context gathered: 2026-01-28*
