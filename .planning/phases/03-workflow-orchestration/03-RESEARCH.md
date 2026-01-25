# Phase 03: Workflow Orchestration - Research

**Researched:** 2026-01-26
**Domain:** Workflow Orchestration, Data Mapping, Multi-File Chaining
**Confidence:** MEDIUM

## Summary

Phase 3 extends the batch processing system from single-file execution to multi-file chained workflows. The key challenge is creating a **Linear Chain Pattern** (A → B → C) with **Explicit Output-to-Input Mapping** where calculated data from File A drives inputs in File B.

Given the project constraints (single executable, local app, non-technical engineers), heavy workflow orchestration engines like Prefect or Airflow are **not appropriate**. Instead, a **Custom WorkflowManager** built on top of the existing `BatchManager` and `EngineManager` is the recommended approach.

The research identifies **Pydantic models** for workflow configuration, **Linear execution model** for simplicity, and **Mantine + DnD libraries** for the React UI. Critical considerations include unit consistency between stages, error propagation strategies, and intermediate result storage.

**Primary recommendation:** Build a **Custom WorkflowManager** with **Explicit Mappings**, executed linearly, using **Pydantic models** for type safety and **Mantine** for an intuitive drag-and-drop UI.

## Standard Stack

### Core Backend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **Pydantic** | 2.x | Data Validation | Type-safe workflow config, already in use (InputConfig) |
| **Custom WorkflowManager** | N/A | Orchestration | Lightweight, fits single-executable constraint |
| **Existing EngineManager** | N/A | Mathcad Execution | Reuse proven COM integration |

### Core Frontend
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **Mantine** | 7.x | UI Components | Already in use, excellent form support |
| **@hello-pangea/dnd** | 16.x | Drag-and-Drop | Modern React DnD library, maintained fork of react-beautiful-dnd |
| **TanStack Query** | 5.x | State Management | Already in use, handles async workflow execution |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Python Queue** | stdlib | Task Queuing | Built-in, sufficient for linear chains |
| **Threading** | stdlib | Background Execution | Already used in BatchManager |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| **Custom WorkflowManager** | **Prefect** | Prefect is powerful but requires server setup, adds 100+MB to executable, overkill for linear chains |
| **Custom WorkflowManager** | **Airflow** | Airflow needs database, scheduler, web server - violates single-executable constraint |
| **@hello-pangea/dnd** | **dnd-kit** | dnd-kit is more modern but smaller community; @hello-pangea/dnd has better stability record |

**Installation (Frontend additions):**
```bash
cd frontend
npm install @hello-pangea/dnd
npm install @mantine/droppable @mantine/drag-handle
```

## Architecture Patterns

### Workflow Configuration Data Structure

**Pattern:** Pydantic Models with Explicit Mappings
**Why:** Type safety, validation, serialization consistency with existing patterns

```python
# src/engine/workflow.py
from typing import List, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass

@dataclass
class FileMapping:
    """Maps an output from one file to an input in another"""
    source_file: str  # e.g., "file_a.mcdx"
    source_alias: str  # e.g., "Stress_Result"
    target_file: str  # e.g., "file_b.mcdx"
    target_alias: str  # e.g., "Input_Stress"

@dataclass
class WorkflowFile:
    """Single file in the workflow chain"""
    file_path: str
    inputs: List[InputConfig]  # Reuse existing InputConfig
    position: int  # 0, 1, 2 for linear chain A->B->C

@dataclass
class WorkflowConfig:
    """Complete workflow configuration"""
    name: str
    files: List[WorkflowFile]
    mappings: List[FileMapping]  # Links files together
    stop_on_error: bool = True  # Stop entire chain on failure
```

### Linear Execution Model

**Pattern:** Sequential Execution with Intermediate Results
**Why:** Simple, predictable, easy to debug, fits linear chain requirement

```python
# src/engine/workflow_manager.py
class WorkflowManager:
    def __init__(self, engine_manager: EngineManager):
        self.engine = engine_manager
        self.workflows: Dict[str, WorkflowState] = {}
    
    def start_workflow(self, workflow_id: str, config: WorkflowConfig):
        """Execute workflow in background thread"""
        thread = threading.Thread(
            target=self._execute_workflow,
            args=(workflow_id, config),
            daemon=True
        )
        thread.start()
    
    def _execute_workflow(self, workflow_id: str, config: WorkflowConfig):
        """Execute files in order (0, 1, 2...)"""
        state = self.workflows[workflow_id]
        intermediate_results = {}  # {file_path: {alias: value}}
        
        for file_config in config.files:
            try:
                # Build inputs for this file (may include mapped outputs)
                inputs = self._resolve_inputs(file_config, intermediate_results, config.mappings)
                
                # Execute calculation
                job_id = self.engine.submit_job("calculate_job", {
                    "path": file_config.file_path,
                    "inputs": inputs
                })
                
                result = self._poll_result(job_id)
                if result.status == "success":
                    # Store outputs for downstream mapping
                    intermediate_results[file_config.file_path] = result.data
                    state.completed_files.append(file_config.file_path)
                else:
                    raise Exception(result.error_message)
                    
            except Exception as e:
                state.status = "failed"
                state.error = str(e)
                if config.stop_on_error:
                    break  # Stop chain
```

### Explicit Output-to-Input Mapping

**Pattern:** Direct Reference Mapping (not name-based)
**Why:** Explicit is more intuitive for non-technical users, avoids "magic" name matching

```python
def _resolve_inputs(self, file_config: WorkflowFile, 
                    intermediate_results: Dict, 
                    mappings: List[FileMapping]) -> List[InputConfig]:
    """Build InputConfigs combining explicit inputs and mapped outputs"""
    inputs = []
    
    # Start with explicit user inputs
    for input_config in file_config.inputs:
        inputs.append(input_config)
    
    # Add mapped outputs from upstream files
    relevant_mappings = [m for m in mappings if m.target_file == file_config.file_path]
    for mapping in relevant_mappings:
        source_data = intermediate_results.get(mapping.source_file, {})
        if mapping.source_alias in source_data:
            inputs.append(InputConfig(
                alias=mapping.target_alias,
                value=source_data[mapping.source_alias]
            ))
    
    return inputs
```

### React Workflow Configuration UI

**Pattern:** Drag-and-Drop Chain Builder with Mapping Modal
**Why:** Visual, intuitive for non-technical engineers, Mantine provides all needed components

```tsx
// frontend/src/components/WorkflowBuilder.tsx
import { DndContext, DragEndEvent } from '@hello-pangea/dnd';
import { Stack, Paper, Text, Badge, Button } from '@mantine/core';

export const WorkflowBuilder = () => {
  const [files, setFiles] = useState<WorkflowFile[]>([]);
  const [mappings, setMappings] = useState<FileMapping[]>([]);

  const handleDragEnd = (event: DragEndEvent) => {
    // Reorder files to define execution order
    const { active, over } = event;
    if (over && active.id !== over.id) {
      setFiles((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <Stack gap="md">
        <Text fw={500}>Workflow Files (drag to reorder)</Text>
        {files.map((file, index) => (
          <Paper key={file.id} p="md" withBorder>
            <Group justify="space-between">
              <Text>
                {index + 1}. {file.file_path}
              </Text>
              <Button size="xs" onClick={() => openMappingModal(file)}>
                Configure Mappings
              </Button>
            </Group>
            {getMappingsForFile(file.id).length > 0 && (
              <Badge size="sm" mt="xs">
                {getMappingsForFile(file.id).length} mappings
              </Badge>
            )}
          </Paper>
        ))}
      </Stack>
    </DndContext>
  );
};
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| **Workflow Engine** | Custom scheduler, DAG runner | **Prefect/Airflow** OR **Custom Linear Execution** | For simple linear chains, custom is fine. For complex DAGs, use established engines. |
| **Drag-and-Drop** | Native HTML5 drag API | **@hello-pangea/dnd** | HTML5 DnD has cross-browser issues, poor mobile support. Library handles edge cases. |
| **Form Validation** | Manual validation logic | **Mantine Form** | Handles error display, focus management, accessibility automatically. |
| **State Management** | React Context + useEffect | **TanStack Query** | Already in use, handles caching, polling, error states automatically. |
| **Type Safety** | Plain dicts | **Pydantic Models** | Prevents runtime errors, auto-serialization, documentation generation. |

**Key insight:** For **linear chains** (A→B→C), a custom WorkflowManager is simpler and lighter than Prefect/Airflow. Only consider heavy engines if requirements evolve to branching workflows, conditional execution, or external triggers.

## Common Pitfalls

### Pitfall 1: Unit Mismatch Between Stages
**What goes wrong:** File A outputs stress in "MPa", File B expects input in "ksi". Calculation fails silently or produces wrong results.
**Why it happens:** Mathcad units are opaque to Python; `read_outputs()` returns numeric values without units metadata.
**How to avoid:**
- **Document mapping requirements:** UI should show expected units for each input/output
- **Warning system:** If unit conversion needed, warn user during configuration
- **Test execution:** Run with known values to verify chain before production
**Warning signs:** ValueError from MathcadPy when setting input, unexpected calculation results

### Pitfall 2: Memory Leak from Intermediate Results
**What goes wrong:** Each workflow stores all intermediate results; after 100 workflows, memory is exhausted.
**Why it happens:** Results dict never cleared; large datasets from File A accumulate.
**How to avoid:**
- **Cleanup after workflow:** Clear `intermediate_results` dict when workflow completes
- **Optional persistence:** Allow saving intermediate results to disk instead of memory
- **Result limiting:** Only store results for active workflows
**Warning signs:** Process memory grows monotonically, slow GC pauses

### Pitfall 3: Silent Failure in Mapped Inputs
**What goes wrong:** File A fails to calculate output, but File B runs with default/cached value. User sees "success" but wrong result.
**Why it happens:** No validation that mapped source alias exists in upstream result.
**How to avoid:**
- **Pre-execution validation:** Check all mappings have valid source aliases
- **Fail-fast:** Stop chain if mapping resolution fails
- **Clear error messages:** "Cannot map 'Stress_Result' from File A - output not found"
**Warning signs:** Files complete but some values look "default", missing data in final results

### Pitfall 4: UI Complexity for Non-Technical Users
**What goes wrong:** Drag-and-drop is confusing; users can't figure out how to link outputs to inputs.
**Why it happens:** Workflow orchestration is inherently technical; visual metaphors may not map well to user mental model.
**How to avoid:**
- **Step-by-step wizard:** Instead of free-form DnD, guide users through "Add File → Configure Inputs → Link Outputs"
- **Preview mode:** Show data flow before execution
- **Templates:** Provide pre-built workflow templates (e.g., "Beam Analysis Chain")
**Warning signs:** Users asking "how do I connect files?", low feature adoption

### Pitfall 5: Blocking the Batch System
**What goes wrong:** Running a workflow blocks the existing batch system; users can't process single files during workflow execution.
**Why it happens:** WorkflowManager and BatchManager both use EngineManager; may compete for COM access.
**How to avoid:**
- **Queue integration:** Workflow uses same job queue as batch (EngineManager.submit_job)
- **Priority system:** Batch jobs get priority over workflow jobs
- **Separate tracking:** Maintain separate status endpoints but share execution engine
**Warning signs:** POST /batch/start times out, workflow slows down batch execution

## Code Examples

### Workflow Configuration Validation

```python
# src/engine/workflow.py
from pydantic import BaseModel, Field, validator

class FileMapping(BaseModel):
    source_file: str
    source_alias: str
    target_file: str
    target_alias: str
    
    @validator('source_file')
    def file_must_exist(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Source file not found: {v}")
        return v

class WorkflowConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    files: List[WorkflowFile]
    mappings: List[FileMapping]
    stop_on_error: bool = True
    
    @validator('files')
    def files_must_be_unique(cls, v):
        paths = [f.file_path for f in v]
        if len(paths) != len(set(paths)):
            raise ValueError("Duplicate files in workflow")
        return v
    
    @validator('mappings')
    def mappings_must_be_valid(cls, v, values):
        """Ensure all mappings reference files in this workflow"""
        if 'files' not in values:
            return v
        
        file_paths = {f.file_path for f in values['files']}
        for mapping in v:
            if mapping.source_file not in file_paths:
                raise ValueError(f"Mapping source file not in workflow: {mapping.source_file}")
            if mapping.target_file not in file_paths:
                raise ValueError(f"Mapping target file not in workflow: {mapping.target_file}")
        return v
```

### Workflow Execution State Tracking

```python
# src/engine/workflow_manager.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

@dataclass
class WorkflowState:
    workflow_id: str
    config: WorkflowConfig
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_file_index: int = 0
    completed_files: List[str] = field(default_factory=list)
    intermediate_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    error: Optional[str] = None
    final_results: Optional[Dict[str, Any]] = None
```

### React Mapping Configuration Modal

```tsx
// frontend/src/components/MappingModal.tsx
import { Modal, Stack, Select, NumberInput, Button, Text } from '@mantine/core';

interface MappingModalProps {
  opened: boolean;
  onClose: () => void;
  targetFile: WorkflowFile;
  availableOutputs: Array<{file: string, alias: string}>;
  onSave: (mappings: FileMapping[]) => void;
}

export const MappingModal = ({ opened, onClose, targetFile, availableOutputs, onSave }: MappingModalProps) => {
  const [mappings, setMappings] = useState<FileMapping[]>([]);

  const addMapping = () => {
    setMappings([...mappings, {
      source_file: '',
      source_alias: '',
      target_file: targetFile.file_path,
      target_alias: ''
    }]);
  };

  return (
    <Modal opened={opened} onClose={onClose} title={`Configure Mappings for ${targetFile.file_path}`}>
      <Stack>
        {mappings.map((mapping, idx) => (
          <Stack key={idx} gap="xs">
            <Text size="sm">Map to input:</Text>
            <Select
              label="Source File"
              data={Array.from(new Set(availableOutputs.map(o => o.file)))}
              value={mapping.source_file}
              onChange={(v) => updateMapping(idx, 'source_file', v!)}
            />
            <Select
              label="Output Alias"
              data={availableOutputs
                .filter(o => o.file === mapping.source_file)
                .map(o => ({ value: o.alias, label: o.alias }))}
              value={mapping.source_alias}
              onChange={(v) => updateMapping(idx, 'source_alias', v!)}
            />
            <Select
              label="Target Input Alias"
              data={targetFile.inputs.map(i => ({ value: i.alias, label: i.alias }))}
              value={mapping.target_alias}
              onChange={(v) => updateMapping(idx, 'target_alias', v!)}
            />
          </Stack>
        ))}
        <Button onClick={addMapping}>Add Mapping</Button>
        <Button onClick={() => onSave(mappings)}>Save Mappings</Button>
      </Stack>
    </Modal>
  );
};
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| **Imperative Chains** | **Declarative Workflows** | 2020+ (Prefect, Dagster) | Separation of definition and execution enables better testing |
| **Monolithic Batch** | **Pipeline-based Orchestration** | 2018+ (Airflow 2.0) | Breaking workflows into stages enables parallelism, retry logic |
| **Name-based Mapping** | **Explicit Mappings** | Industry shift | Explicit mappings reduce bugs, improve maintainability |

**Deprecated/outdated:**
- **XML-based workflow configs**: Replaced by code-first (Python decorators) or JSON/YAML
- **Hardcoded execution order**: Replaced by DAG-based dependency resolution
- **Manual result passing**: Replaced by automatic state management (XCom, state stores)

## Open Questions

1. **Unit Conversion Strategy**
   - **What we know:** Mathcad outputs have units, but Python sees them as numeric values. Different files may use different unit systems.
   - **What's unclear:** Should the system attempt automatic unit conversion, or require user to ensure consistency? How do we detect when units don't match?
   - **Recommendation:** For MVP, require user consistency (document expected units). Future enhancement: integrate units library (pint) for automatic conversion with explicit warnings.

2. **Intermediate Result Persistence**
   - **What we know:** Need to store intermediate results for mapping. Memory vs. disk tradeoff.
   - **What's unclear:** Should intermediate results be saved to disk (for debugging, replay)? What format (CSV, JSON, binary)?
   - **Recommendation:** Store in memory during execution, optionally save to disk on workflow completion. Use JSON for portability.

3. **Error Propagation Strategy**
   - **What we know:** `stop_on_error` flag allows two strategies. But what about partial execution?
   - **What's unclear:** If File B fails, should we still return results from File A? Should we allow "retry single file" without restarting entire chain?
   - **Recommendation:** Default to `stop_on_error=True` (safest). Allow partial results retrieval via API endpoint for debugging. Consider "resume from file X" feature for post-MVP.

## Sources

### Primary (HIGH confidence)
- **Pydantic Documentation** (https://docs.pydantic.dev) - Data validation patterns, model validation
- **Mantine Documentation** (https://mantine.dev) - Form components, modal patterns, drag-and-drop integration
- **@hello-pangea/dnd** (https://github.com/hello-pangea/dnd) - React drag-and-drop patterns

### Secondary (MEDIUM confidence)
- **Prefect Documentation** (https://docs.prefect.io) - Workflow orchestration patterns (rejected for use case but informs design)
- **Existing Codebase** - BatchManager, EngineManager, InputConfig patterns (verified by code inspection)

### Tertiary (LOW confidence)
- **Airflow Documentation** (https://airflow.apache.org/docs) - Workflow engine comparison (rejected based on project constraints)

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH - Pydantic, Mantine, TanStack Query are industry standards, @hello-pangea/dnd is established
- Architecture: MEDIUM - Linear execution is straightforward, but error handling strategy needs validation with real users
- Pitfalls: MEDIUM - Identified based on common patterns, but unit conversion issue requires runtime testing

**Research date:** 2026-01-26
**Valid until:** 2026-03-01 (30 days - stack is stable, but error handling strategy may need adjustment after user testing)
