# Project Research Summary

**Project:** Mathcad Automation App
**Domain:** Engineering Automation / Desktop App
**Researched:** Jan 25, 2026
**Confidence:** MEDIUM

## Executive Summary

The Mathcad Automation App is a local desktop tool designed to automate batch processing of Mathcad Prime worksheets. Engineering experts typically build such tools using a "Sidecar" architecture, separating the unstable, blocking Mathcad COM interface from the user interface to ensure stability. The research confirms that a monolithic script is insufficient for robustness; a process-isolated engine is required.

The recommended approach combines a **Python/FastAPI** backend with a **React** frontend, wrapped in **pywebview** for a lightweight, native-feeling desktop experience. This avoids the overhead of Electron while leveraging the rich React ecosystem for complex UI requirements like mapping and data grids. Critical to this approach is the use of **mathcadpy** for COM abstraction and a strict "Engine Process" pattern that isolates Mathcad crashes from the main application.

Key risks involve the fragility of the Mathcad COM API (potential for "zombie" processes and memory leaks) and the complexity of packaging a hybrid Python/JS application into a single executable. Mitigations include implementing a "watchdog" process to recycle Mathcad instances and using standard, battle-tested packaging tools like PyInstaller with specific configurations for COM dependencies.

## Key Findings

### Recommended Stack

**Core technologies:**
- **Python 3.12+ & FastAPI:** Runtime and server. Selected for `mathcadpy` compatibility and async capabilities to handle long-running jobs.
- **pywebview:** GUI Wrapper. **Critical choice** to avoid Electron's 150MB+ overhead while providing a zero-install experience.
- **React 19 & TanStack Query:** Frontend. Industry standard for complex state management, ensuring the UI stays in sync with the backend.
- **mathcadpy (v0.5):** Mathcad COM wrapper. The only maintained library for this specific task, abstracting raw COM pain.
- **PyInstaller:** Packaging. Standard tool for bundling `win32com` and creating single-file executables.

### Expected Features

**Must have (table stakes):**
- **Excel Import/Export:** Engineers rely on Excel; manual data entry is a dealbreaker.
- **Alias Discovery:** Auto-detection of Input/Output regions in Mathcad files.
- **Series Generation:** Basic linear sweeps (e.g., 1 to 10) for sensitivity analysis.
- **Continue-on-Error:** robust handling so one failed case doesn't stop the batch.
- **Result Grid:** A consolidated view of inputs, outputs, and status.

**Should have (competitive):**
- **Permutations (DOE):** Full factorial generation for exploring design spaces.
- **Snapshot on Fail:** Saving a copy of the `.mcdx` file when a case fails for debugging.
- **Process Recycling:** Auto-restarting Mathcad to prevent memory leaks.

**Defer (v2+):**
- **Parallel Execution:** High technical risk/complexity regarding COM concurrency.
- **Monte Carlo:** Niche use case to be added after core stability is proven.
- **Interactive Charts:** Can be offloaded to Excel in v1.

### Architecture Approach

**Pattern:** Asynchronous Process-Based Engine (Sidecar Pattern)

**Major components:**
1.  **Web Server (FastAPI):** Serves the UI and accepts requests; remains responsive at all times.
2.  **State Manager & Queues:** Decouples request handling from execution; manages job distribution.
3.  **Engine Process (Worker):** A completely separate OS process that owns the Mathcad COM object. This isolation ensures that if Mathcad crashes or blocks, the UI remains alive.

### Critical Pitfalls

(Synthesized from Architecture, Stack, and Feature research)

1.  **Zombie Mathcad Processes:** Mathcad instances staying open after the app closes. **Avoid by:** Using `atexit` handlers and a startup cleanup routine.
2.  **Blocking the Main Loop:** Running COM calls in the web server thread. **Avoid by:** Strictly using the "Engine Process" pattern with queues.
3.  **COM Threading Violations:** `CoInitialize` errors when using threads. **Avoid by:** Initializing COM explicitly within the worker process, not globally.
4.  **Packaging Failures:** Missing COM DLLs in the built EXE. **Avoid by:** Using PyInstaller hidden-imports (e.g., `--hidden-import=win32timezone`).

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core Engine & Prototype
**Rationale:** The biggest risk is the Mathcad COM integration. We must validate that we can reliably drive Mathcad before building the UI.
**Delivers:** A CLI or basic script that can take inputs, run Mathcad, and return outputs using the `mathcadpy` wrapper.
**Addresses:** Basic "Series Generation" and "Continue-on-Error".
**Avoids:** "Blocking the Main Loop" by establishing the multiprocessing pattern early.

### Phase 2: Backend Foundation & State
**Rationale:** Once the engine works, we need the "nervous system" to manage it.
**Delivers:** FastAPI server, Job Queue, and State Manager.
**Uses:** FastAPI, SQLite (for persistence).
**Implements:** The "State Manager" and "Job Queue" architecture components.

### Phase 3: Frontend Skeleton & Basic UI
**Rationale:** Now that the backend can process jobs, we build the interface.
**Delivers:** React app running inside pywebview, connecting to the FastAPI backend.
**Addresses:** "Result Grid" and basic job submission.

### Phase 4: Integration & Packaging
**Rationale:** Connecting the pieces and ensuring it runs on a user's machine without setup.
**Delivers:** "Excel Import/Export", "Alias Discovery", and the final `.exe` installer.
**Uses:** PyInstaller.
**Avoids:** Packaging failures and "Zombie Processes" (final polish of lifecycle hooks).

### Phase Ordering Rationale

- **Risk-First:** We tackle the Mathcad COM instability (Phase 1) immediately. If this fails, the project fails.
- **Backend-Driven:** The architecture relies heavily on the "Sidecar" pattern, so the backend orchestration must be solid before the UI tries to talk to it.
- **Packaging Last:** While important, packaging can be debugged once the code is stable.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1 (Core Engine):** Needs validation of `mathcadpy` 0.5 capabilities specifically with the target version of Mathcad Prime.
- **Phase 4 (Packaging):** PyInstaller configuration for `pywebview` + `win32com` often requires trial-and-error research.

Phases with standard patterns (skip research-phase):
- **Phase 2 (Backend):** FastAPI + SQLite is a standard pattern.
- **Phase 3 (Frontend):** React + Vite is standard.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Validated versions and compatibility (Python 3.12, React 19). |
| Features | MEDIUM | Core features are clear, but "Parallel Execution" feasibility is low. |
| Architecture | HIGH | The "Sidecar" pattern is the industry standard for this problem. |
| Pitfalls | MEDIUM | `PITFALLS.md` was missing; pitfalls were synthesized from other docs. |

**Overall confidence:** HIGH

### Gaps to Address

- **Missing Pitfalls Document:** The dedicated `PITFALLS.md` file was not found. Pitfalls were inferred from other research files, but a dedicated review of Mathcad API idiosyncrasies might be beneficial during Phase 1.
- **Parallel Execution Feasibility:** It is currently unknown if the Mathcad API supports concurrent instances reliably. This is deferred to v2 but represents a knowledge gap.
- **Licensing:** Server-side licensing for Mathcad is a known grey area/bottleneck that needs clarification if the tool moves beyond "Local Desktop" use.

## Sources

### Primary (HIGH confidence)
- **STACK.md:** Library versions (MathcadPy 0.5, pywebview 6.1) and compatibility notes.
- **ARCHITECTURE.md:** Detailed "Sidecar" pattern and COM isolation strategies.
- **FEATURES.md:** MVP definition and feature prioritization matrix.

### Secondary (MEDIUM confidence)
- **Inferred Pitfalls:** Derived from "Anti-Patterns" in Architecture and "Version Compatibility" in Stack.

---
*Research completed: Jan 25, 2026*
*Ready for roadmap: yes*
