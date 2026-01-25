# Phase 02: Batch Processing System - Research

**Researched:** 2026-01-25
**Domain:** Batch Processing Logic & React Data Grid UI
**Confidence:** HIGH

## Summary

This phase introduces the user-facing "Batch Processing" capability, requiring a new Frontend application and significant enhancements to the Python Backend. The research identifies **React + Vite + Mantine** as the optimal frontend stack, with **AG Grid Community** handling the complex "Excel-like" grid requirements.

The backend requires a new `BatchManager` to orchestrate multi-row execution, as the current `EngineManager` is designed for single-job submissions. Mathcad COM integration for "Save as PDF" follows standard automation patterns, though the exact enum value for PDF requires runtime verification.

**Primary recommendation:** Build a **Single Page Application (SPA)** using **React and AG Grid**, managed by **TanStack Query** to sync batch state with the FastAPI backend.

## Standard Stack

### Core Frontend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **React** | 18.x | UI Framework | Ecosystem dominance, robust component model |
| **Vite** | 5.x | Build Tool | Extremely fast HMR, standard for modern React |
| **TypeScript** | 5.x | Language | Safety for complex data structures (batch rows) |
| **TanStack Query** | 5.x | State Management | Best-in-class for async server state (polling jobs) |

### UI & Grid
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **AG Grid Community** | 31.x | Data Grid | High-performance, Excel-like features (sorting, filtering) out of the box |
| **Mantine** | 7.x | Component Library | Modern, hook-based, excellent Modal/Popover support for "Input Configuration" |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| **AG Grid** | **TanStack Table** | TanStack is headless (more control) but requires building *every* UI feature (sorting, resizing) from scratch. AG Grid speeds up dev for "Excel" feel. |
| **Mantine** | **Chakra UI** | Chakra is similar but Mantine v7 has better performance and richer data-focused components. |

**Installation:**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @mantine/core @mantine/hooks @emotion/react
npm install ag-grid-react ag-grid-community
npm install @tanstack/react-query axios
```

## Architecture Patterns

### Batch State Management
The "Live Table" requirement means the frontend needs real-time-ish updates.
-   **Pattern:** **Short Polling** (e.g., every 1s) via TanStack Query.
-   **Why:** Simpler than WebSockets for this scale. The backend is local, so latency is negligible.
-   **Flow:**
    1.  User clicks "Run" -> POST `/batch` (returns `batch_id`)
    2.  Frontend polls GET `/batch/{batch_id}` (returns status of all 100 rows)
    3.  Grid updates `rowData` prop.

### Backend Orchestration
The current `EngineManager` is a singleton for *access*. We need a `BatchManager` for *orchestration*.
-   **Structure:**
    ```python
    class BatchManager:
        def start_batch(self, inputs: List[Dict]):
            # Creates a thread that loops through inputs
            # Calls EngineManager.submit_job() for each
            # Handles "Crash & Restart" logic here
    ```

### Output Generation
-   **Pattern:** **Job-Scoped Artifacts**
-   **Storage:** `D:\Mathcad_exp\Results\{Batch_ID}\{Row_ID}_{Params}.pdf`
-   **Access:** API serves these static files or provides `start file://...` commands.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Grid UI** | `<table>` with custom sort/filter | **AG Grid** | Virtualization, column resizing, and multi-sort are incredibly hard to get right. |
| **Async State** | `useEffect` + `fetch` | **TanStack Query** | Handles caching, polling, error retries, and race conditions automatically. |
| **Modals** | Custom CSS overlay | **Mantine Modal** | Accessible, manages focus trap, handles "Close on Escape" correctly. |

**Key insight:** The "UI Grid" is the core user interface. Hand-rolling a grid that handles 1000+ rows (pagination/virtualization) is a massive time sink.

## Common Pitfalls

### Pitfall 1: Blocking the Main Thread
**What goes wrong:** The Python backend loop blocks `await manager.submit_job()` preventing status updates.
**How to avoid:** Run the batch loop in a separate `threading.Thread` or `asyncio.create_task`. The FastAPI endpoints must remain responsive to return status.

### Pitfall 2: COM Locking
**What goes wrong:** User tries to open the `.mcdx` file while the Batch is running. Mathcad crashes or freezes.
**How to avoid:**
1.  **Strict File Locking:** The backend should `shutil.copy()` the template to a temp folder for execution if possible, OR
2.  **UI Feedback:** Explicitly disable "Open File" buttons during execution.

### Pitfall 3: React Render Thrashing
**What goes wrong:** Polling every 500ms causes the entire AG Grid to re-render, killing performance.
**How to avoid:** Use AG Grid's `api.applyTransaction()` or rely on its efficient diffing by providing stable `rowId`s.

## Code Examples

### Mathcad SaveAs (Python COM)
*Note: The exact PDF enum value needs verification (likely 3 or 4). Use this discovery pattern:*

```python
# src/engine/worker.py
def save_as_pdf(self, path: str):
    # Try standard enum values or inspect constants if available
    # Often: 0=MCDX, 3=PDF (Need to verify at runtime)
    try:
        self.worksheet.SaveAs(path, 3) 
    except Exception:
        # Fallback or log available formats
        pass
```

### React AG Grid Setup
```tsx
// frontend/src/components/BatchGrid.tsx
import { AgGridReact } from 'ag-grid-react';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';

export const BatchGrid = ({ data }) => {
  const [columnDefs] = useState([
    { field: 'status', cellRenderer: StatusBadge },
    { field: 'input_L', headerName: 'Length (mm)' },
    { field: 'output_Stress', headerName: 'Stress (MPa)' }
  ]);

  return (
    <div className="ag-theme-alpine" style={{ height: 600 }}>
      <AgGridReact
        rowData={data}
        columnDefs={columnDefs}
        getRowId={(params) => params.data.id} // Critical for performance
      />
    </div>
  );
};
```

## Open Questions

1.  **PDF Enum Value:** The specific integer constant for `SaveAs` PDF format in Mathcad Prime API is not documented in public web sources.
    -   **Recommendation:** Implement a `discover_constants` task in the plan to inspect the COM object during the first run.

## Metadata

**Confidence breakdown:**
-   Standard Stack: HIGH (React/AG Grid is industry standard)
-   Architecture: HIGH (Queue-based backend is established)
-   Mathcad API: MEDIUM (SaveAs exists, but enum value needs runtime check)

**Research date:** 2026-01-25
**Valid until:** 2026-02-25
