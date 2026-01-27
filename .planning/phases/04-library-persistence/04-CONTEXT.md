# Phase 4: Library & Persistence - Context

**Gathered:** 2026-01-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can save complete batch and workflow configurations as reusable templates. Configs are stored as files in a user-specified folder (or auto-created next to .mcdx files) for easy sharing across teams. The Library tab displays available configs with search functionality, allowing users to load and modify saved configurations.

</domain>

<decisions>
## Implementation Decisions

### Save Scope & Granularity
- **Full config saving:** Save complete batch configurations (file path, all input definitions, ranges/CSVs, export options) AND complete workflow chains (multiple files + mappings)
- **Shareability focus:** Configs must be easily shareable between users/machines
- **Relative paths:** Save file paths as relative paths (from config location) to enable cross-machine sharing
- **Auto-detection:** Configs saved in folder next to .mcdx file are automatically shown in Library tab when that file is opened
- **User-specified storage:** Allow user to specify config folder location OR auto-create folder if not specified

### Library Organization
- **Flat list with search:** Simple list of all configs with text search to filter
- **Minimal user input:** No description/notes required from user — display filename, folder name, and organized list of inputs
- **Smart display:** For configs with many inputs, show most important details (avoid overwhelming UI)
- **Save from active tab:** Save button appears in Batch/Workflow tab (not a separate Library creation flow)

### Load & Apply Behavior
- **Replace all inputs:** Loading a config clears existing inputs and replaces with saved config values
- **Path validation with prompting:** If saved config references missing file paths, prompt user to browse and locate the file
- **Editable configs:** Users can load a config, modify inputs, and save updates (overwrites existing config)

### Storage & Format
- **User-controlled folder location:** User specifies where to save configs, OR app auto-creates folder if not specified
- **No in-app deletion:** Configs are files on disk — users delete via file explorer if needed (no delete button in Library tab)

### Claude's Discretion
- File format choice (JSON vs custom format)
- Folder naming convention when auto-creating
- Exact search algorithm implementation
- UI layout for config list and input preview
- Error messaging for path validation failures

</decisions>

<specifics>
## Specific Ideas

- Configs should work seamlessly when shared via network drives or version control
- Focus on "tech noobs" — minimal friction, minimal required fields
- The workflow should feel like: set up batch → click Save → config appears in folder → other users can load it

</specifics>

<deferred>
## Deferred Ideas

- **String input support (Phase 3.3):** Add string input type alongside numeric inputs for member names like "W36X231" or other string parameters. This should be a separate phase before Phase 4 to ensure Library can save string inputs when implemented.
  - Uses MathcadPy string input command
  - Example use cases: member names, material designations, any string parameters

</deferred>

---

*Phase: 04-library-persistence*
*Context gathered: 2026-01-27*
