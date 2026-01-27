# Phase 4: Library & Persistence - Research

**Researched:** 2026-01-27
**Domain:** File-based configuration persistence, JSON serialization, cross-platform path handling
**Confidence:** HIGH

## Summary

This phase requires implementing a library system for saving and loading batch/workflow configurations as reusable templates. The research confirms that **JSON file storage with Pydantic validation** is the industry-standard approach for Python applications in 2025-2026. The implementation should leverage existing Pydantic models (`InputConfig`, `WorkflowConfig`, `FileMapping`) and use Python's `pathlib` for cross-platform path handling.

The architecture should be **file-based** (not database) to enable easy sharing between users via network drives, version control, or manual file transfer. Configs will be stored as JSON files with relative paths to support cross-machine compatibility. The frontend will use the existing REST API pattern to save/load configurations, with Mantine React Table providing the UI for browsing and searching the library.

**Primary recommendation:** Use Pydantic's built-in JSON serialization with `.model_dump()` and `.model_validate()` methods, store configs as `.json` files alongside `.mcdx` files, and implement a simple flat-file library with search/filter in the UI.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **Pydantic** | v2.x | Data validation & JSON serialization | De facto standard for FastAPI apps, provides type-safe config models with built-in JSON export/import |
| **pathlib** | Python 3.13+ | Cross-platform path handling | Modern Python standard for file paths, handles Windows/Linux differences automatically |
| **FastAPI** | Existing | REST API endpoints | Already in use, provides async file operations and automatic request/response validation |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Mantine React Table** | Latest | File list UI with search/filter | Already using Mantine UI, provides built-in sorting, filtering, pagination |
| **@tanstack/react-query** | ^5.90.20 (already installed) | Caching & state management for library | Already in use, ideal for API caching and background refetching |
| **jsonschema** (optional) | Latest | Additional validation layer | Only if needed for custom validation beyond Pydantic |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| File-based JSON | SQLite database | More complex setup, harder to share configs between users, overkill for simple templates |
| Relative paths | Absolute paths only | Breaks cross-machine sharing, requires re-browsing files on different computers |
| Pydantic JSON | Custom JSON serializers | Loses type safety, more error-prone, reinventing the wheel |

**Installation:**
```bash
# No new dependencies required - all libraries already installed
# Pydantic, pathlib, FastAPI, Mantine already in use
# Optional: pip install jsonschema (if custom validation needed)
```

## Architecture Patterns

### Recommended Project Structure

```
src/
├── server/
│   ├── routes.py          # Add: /library/* endpoints
│   ├── schemas.py         # Add: LibraryConfig, SaveRequest, LoadRequest
│   └── library/           # NEW: Library management module
│       ├── __init__.py
│       ├── manager.py     # Core save/load logic
│       ├── storage.py     # File I/O operations
│       └── validation.py  # Path resolution & validation
└── engine/
    └── protocol.py        # EXISTING: InputConfig, WorkflowConfig models

frontend/
├── src/
│   ├── services/
│   │   └── api.ts         # Add: saveConfig, loadConfig, listConfigs
│   ├── components/
│   │   ├── LibraryModal.tsx     # NEW: Save/Load modal
│   │   └── LibraryList.tsx      # NEW: File browser with search
│   └── hooks/
│       └── useLibrary.ts        # NEW: React Query hook for library ops
```

### Pattern 1: Pydantic Model Serialization

**What:** Use Pydantic's built-in methods for JSON export/import
**When to use:** All configuration save/load operations

**Example (Backend - Save):**
```python
# Source: Pydantic v2 best practices (Dec 2025)
# https://medium.com/algomart/working-with-pydantic-v2-the-best-practices-i-wish-i-had-known-earlier-83da3aa4d17a

from pathlib import Path
from src.engine.protocol import WorkflowConfig, InputConfig
import json

def save_workflow_config(config: WorkflowConfig, save_path: Path) -> None:
    """Save workflow config as JSON file"""
    # Pydantic v2: Use model_dump() instead of dict()
    config_dict = config.model_dump(mode='json')

    # Convert relative paths to strings
    config_json = json.dumps(config_dict, indent=2)

    # Write to file
    save_path.write_text(config_json, encoding='utf-8')
```

**Example (Backend - Load):**
```python
def load_workflow_config(load_path: Path) -> WorkflowConfig:
    """Load workflow config from JSON file"""
    # Read JSON
    config_json = load_path.read_text(encoding='utf-8')
    config_dict = json.loads(config_json)

    # Validate and convert to Pydantic model
    # Pydantic v2: Use model_validate() instead of parse_obj()
    config = WorkflowConfig.model_validate(config_dict)

    return config
```

### Pattern 2: Relative Path Resolution

**What:** Store file paths relative to config location for cross-machine compatibility
**When to use:** All file path storage in configs

**Example:**
```python
# Source: Python pathlib cross-platform patterns (May 2025)
# https://python.plainenglish.io/from-static-to-dynamic-mastering-file-paths-in-python-like-a-pro-94dd8c8aa0e7

from pathlib import Path

def make_relative_path(file_path: Path, base_path: Path) -> str:
    """Convert absolute path to relative path"""
    try:
        return str(file_path.relative_to(base_path))
    except ValueError:
        # File on different drive - fall back to absolute path
        return str(file_path)

def resolve_path(relative_path: str, base_path: Path) -> Path:
    """Convert relative path back to absolute path"""
    path = Path(relative_path)
    if path.is_absolute():
        return path
    return (base_path / path).resolve()
```

### Pattern 3: Auto-Detection of Config Folders

**What:** Automatically discover configs next to `.mcdx` files
**When to use:** When a Mathcad file is opened

**Example:**
```python
def discover_configs(mcdx_path: Path) -> list[Path]:
    """Find config files next to a Mathcad file"""
    config_folder = mcdx_path.parent / f"{mcdx.stem}_configs"

    if config_folder.is_dir():
        return list(config_folder.glob("*.json"))
    return []
```

### Pattern 4: Frontend Library Management

**What:** Use React Query for caching + Mantine for UI
**When to use:** All library operations in frontend

**Example (React Query Hook):**
```typescript
// Source: @tanstack/react-query best practices
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useLibrary = (mcdxPath: string) => {
  const queryClient = useQueryClient();

  const { data: configs } = useQuery({
    queryKey: ['library', mcdxPath],
    queryFn: () => listConfigs(mcdxPath),
    enabled: !!mcdxPath,
  });

  const saveMutation = useMutation({
    mutationFn: (config: WorkflowConfig) => saveConfig(mcdxPath, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library', mcdxPath] });
    },
  });

  return { configs, saveConfig: saveMutation.mutate };
};
```

**Example (Mantine Table with Search):**
```typescript
// Source: Mantine React Table docs
// https://www.mantine-react-table.com/docs/guides/column-filtering

import { MantineReactTable } from 'mantine-react-table';

<MantineReactTable
  columns={columns}
  data={configs}
  enableColumnFiltering
  enableGlobalFilter
  state={{ globalFilter: searchQuery }}
  onRowDoubleClick={({ row }) => loadConfig(row.original)}
/>
```

### Anti-Patterns to Avoid

- **Absolute paths only:** Breaks cross-machine sharing. Use relative paths from config location.
- **Database for templates:** Overcomplicated, hard to share. Use flat JSON files.
- **Custom JSON serialization:** Error-prone. Use Pydantic's `.model_dump()` and `.model_validate()`.
- **Frontend file system access:** Browser security restrictions. Always go through backend API.
- **Ignoring path validation:** Leads to "file not found" errors. Validate paths exist before saving.
- **Manual error messages:** Confusing for users. Use Pydantic's built-in validation errors.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSON validation | Custom schema checking | **Pydantic models** | Handles type coercion, nested models, validation errors automatically |
| Path handling | String manipulation | **pathlib** | Cross-platform, handles edge cases (network drives, symlinks, different path separators) |
| File watching | Polling loops | **watchdog** (if needed) | Efficient OS-level file change detection, handles race conditions |
| Search/filter | Manual array filtering | **Mantine React Table** | Built-in sorting, pagination, fuzzy search, accessible UI |
| API caching | Manual state management | **React Query** | Automatic caching, background refetching, loading/error states |

**Key insight:** Configuration management has been solved many times. The combination of Pydantic + pathlib + Mantine provides a production-ready stack with zero custom code needed for core functionality.

## Common Pitfalls

### Pitfall 1: Path Mismatches on Different Machines
**What goes wrong:** Config saved on Machine A with path `C:\Users\John\Documents\file.mcdx` fails to load on Machine B.
**Why it happens:** Absolute paths are machine-specific.
**How to avoid:** Always store paths relative to config location. Fall back to absolute paths only if files are on different drives (Windows) or can't be made relative.
**Warning signs:** Testing reveals "file not found" errors when sharing configs.

### Pitfall 2: Missing Files After Loading
**What goes wrong:** User loads a config, but referenced `.mcdx` files were moved or deleted.
**Why it happens:** Config paths point to non-existent files.
**How to avoid:** Implement path validation on load. Prompt user to browse for missing files (similar to existing "Browse" button pattern).
**Warning signs:** Batch/workflow fails immediately after loading config.

### Pitfall 3: Pydantic v1 vs v2 Confusion
**What goes wrong:** Code uses deprecated methods (`.dict()`, `.parse_obj()`) that still work but aren't v2-idiomatic.
**Why it happens:** Pydantic v2 changed API names.
**How to avoid:** Use `.model_dump()` instead of `.dict()`, `.model_validate()` instead of `.parse_obj()`.
**Warning signs:** IDE shows deprecated warnings on Pydantic methods.

### Pitfall 4: Encoding Issues with Special Characters
**What goes wrong:** Configs fail to load if filenames contain non-ASCII characters.
**Why it happens:** Default encoding varies by platform.
**How to avoid:** Always specify `encoding='utf-8'` when reading/writing JSON files.
**Warning signs:** Tests fail with unicode filenames or non-English paths.

### Pitfall 5: Race Conditions in File Watching
**What goes wrong:** Multiple events fire for single file save operation.
**Why it happens:** OS sends create + modify + close events in sequence.
**How to avoid:** Debounce file system events (wait 500ms after last event before reloading).
**Warning signs:** Library UI flickers or refreshes multiple times after save.

### Pitfall 6: Frontend State Desynchronization
**What goes wrong:** UI shows stale config list after backend changes.
**Why it happens:** No caching invalidation strategy.
**How to avoid:** Use React Query's `invalidateQueries()` after mutations.
**Warning signs:** User must refresh page to see new configs.

## Code Examples

Verified patterns from official sources:

### Save Batch Config (Backend)
```python
# Source: Pydantic v2 best practices, Real Python JSON guide
# https://realpython.com/python-json/

from pathlib import Path
import json
from typing import List
from src.engine.protocol import InputConfig

def save_batch_config(
    file_path: str,
    inputs: List[InputConfig],
    export_pdf: bool,
    export_mcdx: bool,
    save_dir: Path
) -> Path:
    """Save batch configuration to JSON file"""
    config = {
        "type": "batch",
        "file_path": file_path,
        "inputs": [inp.model_dump(mode='json') for inp in inputs],
        "export_pdf": export_pdf,
        "export_mcdx": export_mcdx,
        "version": "1.0"
    }

    # Generate filename from Mathcad file name
    mcdx_name = Path(file_path).stem
    config_file = save_dir / f"{mcdx_name}_batch.json"

    # Write with UTF-8 encoding
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return config_file
```

### Load with Path Validation (Backend)
```python
# Source: Python pathlib cross-platform patterns
# https://realpython.com/python-pathlib/

from pathlib import Path
import json

def validate_and_resolve_paths(config: dict, config_dir: Path) -> dict:
    """Validate file paths exist, prompt user if missing"""
    file_path = config["file_path"]

    # Resolve relative path
    if not Path(file_path).is_absolute():
        resolved = (config_dir / file_path).resolve()
    else:
        resolved = Path(file_path)

    # Check if file exists
    if not resolved.exists():
        raise FileNotFoundError(
            f"Referenced file not found: {file_path}\n"
            f"Expected location: {resolved}\n"
            f"Please locate the file or update the config."
        )

    config["file_path"] = str(resolved)
    return config
```

### Library API Endpoints (Backend)
```python
# Source: FastAPI best practices, existing routes.py pattern
# https://fastapi.tiangolo.com/advanced/settings/

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

class SaveConfigRequest(BaseModel):
    config_type: Literal["batch", "workflow"]
    config: dict
    save_name: str

@router.post("/library/save")
async def save_config(req: SaveConfigRequest):
    """Save configuration to library folder"""
    try:
        config_path = library_manager.save(req.config_type, req.config, req.save_name)
        return {"status": "saved", "path": str(config_path)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/library/list")
async def list_configs(mcdx_path: str):
    """List available configs for a Mathcad file"""
    configs = library_manager.list_configs(Path(mcdx_path))
    return {"configs": configs}

@router.post("/library/load")
async def load_config(config_path: str):
    """Load configuration from file"""
    try:
        config = library_manager.load(Path(config_path))
        return {"status": "loaded", "config": config}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### Library Modal Component (Frontend)
```typescript
// Source: Mantine UI patterns, React Query best practices
import { Modal, TextInput, Button, Stack, Group } from '@mantine/core';
import { useMutation } from '@tanstack/react-query';

export function LibraryModal({ opened, onClose, config, onSave }) {
  const [name, setName] = useState('');

  const saveMutation = useMutation({
    mutationFn: (saveName: string) =>
      saveConfig(saveName, config),
    onSuccess: () => {
      onClose();
      // Show success notification
    },
  });

  return (
    <Modal opened={opened} onClose={onClose} title="Save Configuration">
      <Stack>
        <TextInput
          label="Configuration Name"
          placeholder="My Batch Config"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
        />
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>Cancel</Button>
          <Button
            onClick={() => saveMutation.mutate(name)}
            loading={saveMutation.isPending}
          >
            Save
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| **ConfigParser (.ini files)** | **JSON + Pydantic** | 2020-2022 | JSON is language-agnostic, Pydantic provides type safety |
| **dict() / parse_obj()** | **model_dump() / model_validate()** | Pydantic v2 (2023) | v2 methods are more explicit and performant |
| **os.path** | **pathlib** | Python 3.4+ (2014) | pathlib provides object-oriented path handling |
| **Manual state mgmt** | **React Query** | React Query v5 (2024) | Automatic caching, refetching, loading states |
| **Mantine DataTable** | **Mantine React Table** | 2023-2024 | New library with built-in filtering/sorting |

**Deprecated/outdated:**
- **Pydantic v1 methods (`.dict()`, `.parse_obj()`)**: Still work but deprecated. Use v2 methods for new code.
- **os.path module**: Superseded by pathlib. Still works but pathlib is more modern.
- **Custom JSON serializers**: Unnecessary with Pydantic. Use built-in methods.

## Open Questions

1. **Config folder naming convention**
   - What we know: Context says "auto-create folder if not specified"
   - What's unclear: Exact folder name pattern (e.g., `file_configs/`, `file_templates/`, `.library/`)
   - Recommendation: Use `{filename}_configs/` pattern (e.g., `beam_calc_configs/`) to avoid conflicts

2. **Batch config structure**
   - What we know: Workflow config is defined in protocol.py
   - What's unclear: Should batch configs use a Pydantic model like WorkflowConfig, or remain as dict?
   - Recommendation: Create `BatchConfig` Pydantic model in protocol.py for consistency

3. **Config versioning**
   - What we know: Configs may evolve over time
   - What's unclear: Do we need migration logic for old config formats?
   - Recommendation: Add `"version": "1.0"` field now, implement migration later if needed

4. **String input preservation**
   - What we know: Phase 3.3 added string input support
   - What's unclear: Will string types serialize correctly through JSON?
   - Recommendation: Test thoroughly - Pydantic should preserve type information

5. **Search algorithm**
   - What we know: Context says "text search to filter"
   - What's unclear: Exact search behavior (case-sensitive? substring? fuzzy?)
   - Recommendation: Start with case-insensitive substring search, enhance later if needed

## Sources

### Primary (HIGH confidence)
- [Working With Pydantic v2: The Best Practices](https://medium.com/algomart/working-with-pydantic-v2-the-best-practices-i-wish-i-had-known-earlier-83da3aa4d17a) - Pydantic v2 patterns, .model_dump() and .model_validate() methods (Dec 2025)
- [Loading Pydantic models from JSON without running out of memory](https://pythonspeed.com/articles/pydantic-json-memory/) - Memory-efficient JSON parsing (May 2025)
- [Python's pathlib Module: Taming the File System](https://realpython.com/python-pathlib/) - Official pathlib patterns (Real Python, updated 2024)
- [How to Master Python's pathlib Module](https://medium.com/the-pythonworld/how-to-master-pythons-pathlib-module-and-finally-stop-using-os-path-f55ea713542d) - Cross-platform path handling (Medium, 2024)
- [FastAPI Settings and Environment Variables](https://fastapi.tiangolo.com/advanced/settings/) - Official FastAPI config patterns
- [Mantine React Table Documentation](https://www.mantine-react-table.com/) - Official docs for filtering/search
- [Column Filtering Guide - Mantine React Table](https://www.mantine-react-table.com/docs/guides/column-filtering) - Filter implementation patterns

### Secondary (MEDIUM confidence)
- [Load Unload Data Pydantic](https://medium.easyread.co/load-unload-data-pydantic-0e5f3c0aaf6) - Practical Pydantic JSON examples (June 2024)
- [From Static to Dynamic: Mastering File Paths in Python](https://python.plainenglish.io/from-static-to-dynamic-mastering-file-paths-in-python-like-a-pro-94dd8c8aa0e7) - Dynamic path patterns (May 2025)
- [Master Cross-Platform Path Handling in Python](https://www.linkedin.com/advice/0/how-do-you-handle-path-differences-python-ym42f) - Cross-platform strategies (May 2024)
- [Working With JSON Data in Python](https://realpython.com/python-json/) - JSON encoding best practices (Aug 2025)
- [How are you all handling config files?](https://www.reddit.com/r/Python/comments/w1utza/how_are_you_all_handling_config_files/) - Community practices (Reddit, verified discussion)

### Tertiary (LOW confidence)
- [Best Practices for Using Pydantic in Python](https://dev.to/devasservice/best-practices-for-using-pydantic-in-python-2021) - General Pydantic tips (2021, older but still relevant)
- [How to Store and Read Configuration Files Using React](https://www.pluralsight.com/resources/blog/guides/how-to-store-and-read-configuration-files-using-react) - React config patterns (2020, verified approach)
- [Table Search Tutorial | Refine v5](https://refine.dev/core/docs/advanced-tutorials/search/table-search/) - Table search patterns (verified against Mantine docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pydantic, pathlib, FastAPI are industry standards with official documentation
- Architecture: HIGH - Patterns verified against official docs and recent (2024-2025) best practices
- Pitfalls: HIGH - Common issues documented in official docs and community discussions
- Frontend patterns: MEDIUM - Mantine React Table is verified, but specific UI patterns are up to developer discretion

**Research date:** 2026-01-27
**Valid until:** 2026-03-01 (60 days - Pydantic v2 patterns are stable, unlikely to change)

**Researcher notes:**
- All core technologies (Pydantic v2, pathlib, FastAPI) are mature and stable
- No experimental features required - this is a well-solved problem space
- Main implementation risk is path validation edge cases (network drives, different OS)
- String input support from Phase 3.3 should serialize cleanly through JSON, but needs verification
