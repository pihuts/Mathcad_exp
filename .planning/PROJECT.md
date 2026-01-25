# Mathcad Automator

## What This Is
A local, self-contained web application that automates Mathcad calculations. It allows engineers to batch process files with ranges of inputs (CSV or generated) and chain multiple Mathcad files together into workflows (Input A → File 1 → Output A → Input B → File 2). It is distributed as a single executable requiring no technical setup, targeting non-technical users who simply need to run calculations.

## Core Value
Enable non-technical engineers to perform complex parameter studies and multi-file workflows in Mathcad with zero programming or setup.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **Scan & Parse**: Automatically detect Input/Output aliases in selected Mathcad files using MathcadPy.
- [ ] **Batch Processing**: Allow users to define ranges (Start/End/Increment) or upload CSVs for specific inputs.
- [ ] **Library Management**: UI to save and reuse common input lists (e.g., "Bolt Diameters", "Structural Members").
- [ ] **Workflow Engine**: Interface to chain files and explicitly map Output X from File A to Input Y of File B.
- [ ] **Execution & Export**: Run calculations sequentially (showing progress) and save results as PDF and/or MCDX with custom naming (filename_parameter.extension).
- [ ] **Zero-Config Distribution**: Package entire application (Python, dependencies, server) into a single `.exe` or clickable folder.

### Out of Scope

- **Cloud Execution**: Must run locally to access the user's licensed Mathcad installation.
- **Parallel Processing**: Mathcad COM interface is single-threaded; files process one by one.

## Context

- **User Base**: Structural engineers who are "tech noobs." They cannot be expected to install Python, run pip commands, or configure environments.
- **Environment**: Windows Desktop with Mathcad installed.
- **Tech Stack**: Python (Backend), Web Frontend, MathcadPy (API), PyInstaller (Distribution).

## Constraints

- **Dependency**: Requires local Mathcad installation.
- **Distribution**: Must be a standalone executable (no external Python requirements for end user).
- **Concurrency**: Mathcad Automation API is single-threaded; app must handle queuing.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **Web-based Local App** | Allows rich UI for mapping workflows while keeping easy access to local file system. | — Pending |
| **Explicit Mapping** | "Magic" name matching is too error-prone for engineering; users must manually connect outputs to inputs. | — Pending |
