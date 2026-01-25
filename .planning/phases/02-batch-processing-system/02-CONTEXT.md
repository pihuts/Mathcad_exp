# Phase 2: Batch Processing System - Context

**Gathered:** 2026-01-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Domain: Logic and UI for defining, executing, and tracking parameter studies (ranges, CSVs) and receiving structured results.
</domain>

<decisions>
## Implementation Decisions

### Input Definition UI
- **Configuration:** Popover/Modal for configuring Single/Range/List/CSV details. Main grid remains clean.
- **Visual Indicator:** Show an icon/badge on the main grid row to indicate "Complex Input" configuration.
- **CSV Mapping:** Per-input binding inside the modal (select "From CSV Column..."), rather than a central wizard.
- **Validation:** Real-time strict validation inside the modal (cannot save invalid config like Step=0).

### Execution Feedback
- **Primary View:** Live Table showing all iterations updating row-by-row (Pending -> Running -> Done).
- **Data Visibility:** Show Full Data (Input + Output values) in the table columns, not just status.
- **Large Datasets:** Use Pagination to handle large batches (1000+ rows).
- **Intermediate Access:** Allow opening generated PDFs immediately. **Lock MCDX files** during execution to prevent COM conflicts.

### Output Organization
- **Structure:** Create a new timestamped subfolder for each batch run (e.g., `Results_YYYY-MM-DD_HH-mm`).
- **Naming:** Use Dynamic Variables pattern (e.g., `Beam_{Length}mm.pdf`).
- **Formats:** User selects desired formats via checkboxes (PDF, MCDX, CSV) before running.
- **Collisions:** Auto-rename duplicates with `_N` suffix (e.g., `file_1.pdf`) if they occur within the same batch.

### Error Policy
- **Crash Handling:** Restart Mathcad and Continue (Best Effort). If Row 5 crashes, kill process, restart, and attempt Row 6.
- **CSV Reporting:** (Claude's Discretion) Use a specific "Status" column in the Summary CSV to indicate success/failure/crash.
- **Retry:** (Claude's Discretion) specific "Retry Failed" button after batch completion to create a new job with only the failed rows.

</decisions>

<specifics>
## Specific Ideas

- "Only the pdf file since it might cause errors if the mathcad program is running and we open a mathcad file" (User constraint on intermediate access).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-batch-processing-system*
*Context gathered: 2026-01-25*
