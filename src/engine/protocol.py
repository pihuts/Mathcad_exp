import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class EngineStatus(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    ERROR = "ERROR"
    DEAD = "DEAD"

@dataclass
class JobRequest:
    command: str
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class JobResult:
    job_id: str
    status: str  # "success" or "error"
    data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == "success"

@dataclass
class InputConfig:
    """Configuration for a single input in a batch calculation"""
    alias: str
    value: Any
    units: Optional[str] = None  # Units specification (e.g., "in", "ft", "kip", or None for default)


class FileMapping(BaseModel):
    """Maps an output from one file to an input in another"""
    source_file: str  # e.g., "file_a.mcdx"
    source_alias: str  # e.g., "Stress_Result"
    target_file: str  # e.g., "file_b.mcdx"
    target_alias: str  # e.g., "Input_Stress"


class WorkflowFile(BaseModel):
    """Single file in workflow chain"""
    file_path: str
    inputs: List[InputConfig]  # Reuse existing InputConfig
    position: int = Field(default=0, ge=0)  # 0, 1, 2 for linear chain A->B->C


class WorkflowConfig(BaseModel):
    """Complete workflow configuration"""
    name: str = Field(..., min_length=1, max_length=100)
    files: List[WorkflowFile]
    mappings: List[FileMapping]  # Links files together
    stop_on_error: bool = True  # Stop entire chain on failure
    export_pdf: bool = True
    export_mcdx: bool = False
    output_dir: Optional[str] = None


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
