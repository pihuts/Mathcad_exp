# MathcadPy Parametric Runner

## What This Is

A portable web application that automates parametric analysis using Mathcad. Users select a Mathcad file, the app scans for designated input variables, and users can assign values (single, ranges, CSV imports, or predefined lists) to run multiple combinations. Each combination saves as PDF and/or .mcdx with parameters in the filename. Built for non-technical users in connection engineering who need to run batch calculations without understanding Mathcad internals.

## Core Value

Non-technical users can run parametric Mathcad calculations through a simple web interface without touching Mathcad directly.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] User can browse and select a Mathcad file (.mcdx)
- [ ] App scans and displays all designated input variables from the file
- [ ] User can assign single values to inputs
- [ ] User can assign a range of values to inputs
- [ ] User can import values from CSV files
- [ ] User can select from predefined lists (bolt diameters, plate thicknesses in 1/8" increments)
- [ ] User can create and save custom input lists for reuse
- [ ] User can generate all combinations of selected input values
- [ ] App runs each combination through Mathcad via MathcadPy API
- [ ] User can choose to save output as .mcdx file
- [ ] User can choose to save output as PDF
- [ ] Output filenames include parameter values (e.g., `template_bolt0.75_plate0.5.pdf`)
- [ ] Progress bar shows completion during batch processing
- [ ] App is portable (copy folder, run single file/script)

### Out of Scope

- Multi-file workflow chaining — deferred to v2
- Output-to-input mapping between files — deferred to v2
- Saved workflow configurations — deferred to v2
- Cloud deployment — local only
- Mathcad installation/licensing — user must have Mathcad installed

## Context

**Technical Environment:**
- Python backend (required for MathcadPy API)
- MathcadPy library: https://github.com/MattWoodhead/MathcadPy
- Requires Mathcad installed on user's machine (API dependency)
- Web interface for local use
- Target: 20-100 combinations per run

**User Context:**
- Primary users are non-technical staff in connection engineering
- Engineers create the Mathcad templates with designated input variables
- Non-technical users run the batch calculations
- Users need to see the same variable names as in Mathcad (no translation)

**Distribution:**
- Must be portable — copy a folder, run a file
- No installation steps for end users
- Shared locally within offices/teams

## Constraints

- **Tech Stack**: Python backend — required for MathcadPy integration
- **Dependency**: Mathcad must be installed on the machine running the app
- **Portability**: Must run from a single folder with minimal/no setup
- **Users**: Interface must be simple enough for non-technical users

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Single file mode for v1 | Reduce complexity, validate core value first | — Pending |
| Web interface over desktop GUI | Easier to share, familiar to users | — Pending |
| Parameters in filename | Easy identification of outputs | — Pending |

---
*Last updated: 2025-01-25 after initialization*
