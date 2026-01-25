# Requirements: Mathcad Automator

**Defined:** 2025-01-25
**Core Value:** Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Core Engine (MathcadPy Integration)

- [ ] **ENG-01**: System can detect and connect to a local running Mathcad instance.
- [ ] **ENG-02**: System can open a specific `.mcdx` file path.
- [ ] **ENG-03**: System can identify all Input and Output aliases defined in the Mathcad file.
- [ ] **ENG-04**: System can set values for identified Input variables.
- [ ] **ENG-05**: System can read values from identified Output variables after calculation.
- [ ] **ENG-06**: System handles Mathcad crashes/hangs by restarting the process (retry mechanism).

### Batch Processing

- [ ] **BATCH-01**: User can define a "Single Value" for an input.
- [ ] **BATCH-02**: User can define a "Range" (Start, End, Increment) for a numeric input.
- [ ] **BATCH-03**: User can define a "List" (Comma-separated or pasted) for any input.
- [ ] **BATCH-04**: User can upload a CSV to populate an input list.
- [ ] **BATCH-05**: System generates a "Cartesian Product" (Permutations) of all variable input ranges.
- [ ] **BATCH-06**: User can choose "Zip" mode (row-by-row) instead of Permutations for inputs.
- [ ] **BATCH-07**: System executes the batch sequentially, showing a progress bar.
- [ ] **BATCH-08**: System logs skipped/failed iterations without stopping the entire batch.

### Workflow Engine

- [ ] **FLOW-01**: User can create a linear chain of multiple Mathcad files (File A → File B → File C).
- [ ] **FLOW-02**: User can explicitly map an Output from an upstream file to an Input of a downstream file.
- [ ] **FLOW-03**: Downstream files execute automatically using the outputs from the previous step.

### Library Management

- [ ] **LIB-01**: User can save a named set of input values (e.g., "Standard Bolt Sizes").
- [ ] **LIB-02**: User can load a saved set into an input field.

### Output & Export

- [ ] **OUT-01**: User can configure output filename pattern (e.g., `Result_{d}_{L}.pdf`).
- [ ] **OUT-02**: System saves the calculated Mathcad file as `.mcdx`.
- [ ] **OUT-03**: System exports the calculated Mathcad file as `.pdf`.
- [ ] **OUT-04**: System generates a Summary CSV containing Inputs + Outputs for all iterations.

### Distribution & UI

- [ ] **DIST-01**: Application runs as a single local `.exe` file.
- [ ] **DIST-02**: UI launches in a dedicated window (using pywebview or similar), not a browser tab.
- [ ] **DIST-03**: UI provides a "Stop/Cancel" button to abort running operations.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Workflow
- **FLOW-v2-01**: Branching workflows (File A → File B AND File C).
- **FLOW-v2-02**: Conditional execution (Run File B only if Output A > 100).

### Cloud & Collaboration
- **CLOUD-01**: Shared library definitions on a network drive.
- **CLOUD-02**: Headless execution mode for server environments.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Parallel Execution | Mathcad COM API is single-threaded; cannot run concurrently on one machine. |
| Mathcad 15 / Legacy | Focus is on Mathcad Prime (current version). |
| Cloud Hosting | User specified local execution only. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ENG-01 | Phase 1 | Pending |
| ENG-02 | Phase 1 | Pending |
| ENG-03 | Phase 1 | Pending |
| ENG-04 | Phase 1 | Pending |
| ENG-05 | Phase 1 | Pending |
| ENG-06 | Phase 1 | Pending |
| BATCH-01 | Phase 2 | Pending |
| BATCH-02 | Phase 2 | Pending |
| BATCH-03 | Phase 2 | Pending |
| BATCH-04 | Phase 2 | Pending |
| BATCH-05 | Phase 2 | Pending |
| BATCH-06 | Phase 2 | Pending |
| BATCH-07 | Phase 2 | Pending |
| BATCH-08 | Phase 2 | Pending |
| FLOW-01 | Phase 3 | Pending |
| FLOW-02 | Phase 3 | Pending |
| FLOW-03 | Phase 3 | Pending |
| LIB-01 | Phase 4 | Pending |
| LIB-02 | Phase 4 | Pending |
| OUT-01 | Phase 2 | Pending |
| OUT-02 | Phase 2 | Pending |
| OUT-03 | Phase 2 | Pending |
| OUT-04 | Phase 2 | Pending |
| DIST-01 | Phase 5 | Pending |
| DIST-02 | Phase 5 | Pending |
| DIST-03 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2025-01-25*
