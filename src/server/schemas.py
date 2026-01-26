from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class JobSubmission(BaseModel):
    command: str
    payload: Dict[str, Any] = {}

class JobResponse(BaseModel):
    job_id: str
    status: str = "submitted"

class ControlResponse(BaseModel):
    status: str
    message: str

class BatchRequest(BaseModel):
    batch_id: str
    inputs: List[Dict[str, Any]]
    output_dir: str
    export_pdf: bool = True
    export_mcdx: bool = False

class BatchRow(BaseModel):
    row: int
    status: str
    stage: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    pdf: Optional[str] = None
    mcdx: Optional[str] = None
    error: Optional[str] = None

class BatchStatus(BaseModel):
    id: str
    total: int
    completed: int
    status: str
    results: List[BatchRow]
    generated_files: List[str] = []
    error: Optional[str] = None
