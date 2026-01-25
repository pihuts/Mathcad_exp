import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

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
