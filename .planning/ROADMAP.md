# Project Roadmap

**Project:** Mathcad Automator
**Generated:** 2026-01-25
**Coverage:** 26/26 Requirements Mapped

## Overview

This roadmap delivers the Mathcad Automator in vertical slices, prioritizing the highest technical risk (COM integration) and core value (Batch Processing) before adding complexity (Workflows) and convenience (Library).

## Phase 1: Core Engine Integration

**Goal:** Application can reliably control Mathcad to read/write variables and handle instability.
**Focus:** Backend, MathcadPy, COM Stability

### Dependencies
- Local Mathcad Prime installation
- Python environment

### Requirements
- **ENG-01**: Connect to local Mathcad instance
- **ENG-02**: Open .mcdx file path
- **ENG-03**: Identify Input/Output aliases
- **ENG-04**: Set Input values
- **ENG-05**: Read Output values
- **ENG-06**: Handle crashes/hangs (Retry)

### Success Criteria
1. App can open a specified `.mcdx` file without user intervention.
2. App lists all defined Input and Output aliases from the opened file.
3. App successfully updates an input value, recalculates, and retrieves the correct output.
4. App recovers automatically (restarts process) if Mathcad is killed during execution.

---

## Phase 2: Batch Processing System

**Goal:** Users can execute parameter studies (ranges, CSVs) and receive structured results.
**Focus:** Batch Logic, UI Grid, Output Generation

### Dependencies
- Phase 1 (Core Engine)

### Requirements
- **BATCH-01**: Define "Single Value"
- **BATCH-02**: Define "Range" (Start/End/Increment)
- **BATCH-03**: Define "List" (Manual entry)
- **BATCH-04**: Upload CSV for inputs
- **BATCH-05**: Cartesian Product generation
- **BATCH-06**: Zip mode (row-by-row)
- **BATCH-07**: Sequential execution with progress
- **BATCH-08**: Log skipped/failed iterations
- **OUT-01**: Configure filename pattern
- **OUT-02**: Save results as .mcdx
- **OUT-03**: Export results as .pdf
- **OUT-04**: Generate Summary CSV
- **DIST-03**: Stop/Cancel button

### Success Criteria
1. User can upload a CSV to populate input lists.
2. User can define a numeric range and see the generated iteration list.
3. App executes all iterations sequentially, updating a progress bar.
4. User can abort a running batch operation using a "Stop" button.
5. User finds a Summary CSV and correctly named PDF/MCDX files in the output folder.

---

## Phase 3: Workflow Orchestration

**Goal:** Users can chain multiple Mathcad files where outputs drive downstream inputs.
**Focus:** Data Mapping, Chaining Logic

### Dependencies
- Phase 2 (Batch System)

### Requirements
- **FLOW-01**: Linear chain of files (A → B → C)
- **FLOW-02**: Explicit Output-to-Input mapping
- **FLOW-03**: Automatic downstream execution

### Success Criteria
1. User can add multiple Mathcad files to a single job configuration.
2. User can map an Output variable from File A to an Input variable in File B.
3. Execution automatically passes calculated data from File A to File B.
4. Final results include data from all files in the chain.

---

## Phase 4: Library & Persistence

**Goal:** Users can save and reuse common input configurations to save time.
**Focus:** Persistence, Usability

### Dependencies
- Phase 2 (Batch System)

### Requirements
- **LIB-01**: Save named input sets
- **LIB-02**: Load saved input sets

### Success Criteria
1. User can save the current configuration of inputs as a named template.
2. User can populate input fields by selecting a previously saved template.
3. Saved templates persist across application restarts.

---

## Phase 5: Production Packaging

**Goal:** Application runs as a standalone tool on a clean Windows machine.
**Focus:** PyInstaller, PyWebview, Installer

### Dependencies
- Phase 1-4 (Feature Complete)

### Requirements
- **DIST-01**: Single local .exe file
- **DIST-02**: Dedicated UI window (no browser)

### Success Criteria
1. Application runs from a single `.exe` file on a machine without Python installed.
2. UI opens in a native application window, removing browser chrome.
3. Application closes all child processes (Mathcad, Backend) when the window is closed.

---

## Progress

| Phase | Status | Requirements |
|-------|--------|--------------|
| 1 - Core Engine | **Complete** | 6 |
| 2 - Batch Processing | **In progress** (4/5 plans complete) | 13 |
| 3 - Workflow | **Planned** | 3 |
| 4 - Library | **Planned** | 2 |
| 5 - Packaging | **Planned** | 2 |
