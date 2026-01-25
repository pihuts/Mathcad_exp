# Technology Stack

**Project:** Mathcad Automation App
**Researched:** Jan 25, 2026
**Confidence:** HIGH

## Recommended Stack

### Core Framework (Backend & GUI)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.12+ | Runtime | Required for `mathcadpy` and robust COM automation. |
| **FastAPI** | 0.115+ | Web Server | Modern, async, typed. Serves the frontend and handles long-running job queues. superior to Flask for async COM tasks. |
| **pywebview** | 6.1+ | GUI Wrapper | **Critical choice.** Wraps the web app in a native Windows window (using Edge WebView2). Avoids the 150MB+ overhead of Electron. Zero-install experience. |
| **mathcadpy** | 0.5 | Mathcad COM | The only maintained Python wrapper for Mathcad Prime (updated Feb 2025). Abstracts raw COM pain. |

### Frontend (UI & Mapping)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **React** | 19.x | UI Library | Industry standard for "complex mapping" state management. specific ecosystem advantage for map components (react-leaflet, react-map-gl). |
| **Vite** | 6.x | Build Tool | Standard, fast build system. Compiles React to static files that FastAPI serves. |
| **TanStack Query** | 5.x | State Sync | Essential for keeping UI in sync with long-running Python jobs without manual polling chaos. |
| **Shadcn/UI** | Latest | UI Components | "Single Developer" shortcut. Copy-paste components (Tailwind) look professional out of the box. |

### Packaging & Distribution

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **PyInstaller** | 6.18+ | Packaging | **Standard.** Battle-tested for bundling `win32com` and `pywebview`. Supports `--onefile` for the requested single .exe. |
| **Inno Setup** | 6.x | Installer | (Optional) If the single .exe gets too large or needs to register file associations/admin privs. |

### Database

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **SQLite** | Built-in | Job Persistence | Zero-config, single-file. Perfect for local desktop apps. Handles concurrent reads well enough for a single user. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| **Packaging** | PyInstaller | **Nuitka** | Nuitka offers better performance/obfuscation, but debugging COM serialization issues in compiled C code is significantly harder. Stick to PyInstaller for maintainability unless performance is critical. |
| **Packaging** | PyInstaller | **PyOxidizer** | Too complex for this use case. Lacks the "just works" ecosystem for Windows COM DLLs that PyInstaller has. |
| **GUI** | pywebview | **Electron** | Adds ~150MB+ to bundle size. Overkill for a local tool. Requires a separate Node.js process management. |
| **GUI** | pywebview | **Tauri** | Excellent, but adds Rust complexity to the build chain. "Single Developer" constraint suggests sticking to Python/JS. |
| **Frontend** | React | **HTMX** | HTMX is great for CRUD, but "complex mapping" (drag-drop, canvas, vector layers) often requires heavy client-side state that HTMX struggles with. |
| **Frontend** | React | **NiceGUI** | NiceGUI (Vue wrapper) is faster to build simple tools, but might hit a wall with "complex mapping" customization. |

## Installation

```bash
# Backend
pip install fastapi uvicorn pywebview mathcadpy pywin32 sqlalchemy

# Frontend
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install lucide-react @tanstack/react-query axios
```

## Stack Patterns by Variant

**If "Zero Install" is strict (No Admin Rights):**
-   Use **PyInstaller --onefile**.
-   Ensure `mathcadpy` creates the COM object with `Dispatch()` not `EnsureDispatch()` if possible, to avoid writing to restricted registry keys (though Mathcad usually requires full registration).
-   *Warning:* Mathcad itself must be installed on the user's machine.

**If "Complex Mapping" involves heavy GIS data:**
-   Add **GeoPandas** to the Python backend.
-   Use **Deck.gl** (via React) for rendering large datasets in the browser.

## Version Compatibility & Pitfalls

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `mathcadpy` 0.5 | `pywin32` | Requires `pywin32` to be explicitly hidden-imported in PyInstaller: `--hidden-import=win32timezone`. |
| `pywebview` | `FastAPI` | Must run FastAPI in a separate thread. Pywebview must own the *main* thread on Windows (GUI loop). |
| `Mathcad Prime` | COM API | Mathcad Prime's COM API is **slow**. Do not block the FastAPI async loop with COM calls. Use `run_in_executor` or a dedicated background queue. |

## Sources

-   **MathcadPy:** Verified v0.5 released Feb 2025 (PyPI).
-   **pywebview:** Verified v6.1 released Oct 2025 (GitHub).
-   **PyInstaller:** Verified v6.18.0 released Jan 2026 (Docs).
