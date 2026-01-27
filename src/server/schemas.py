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

class SaveLibraryConfigRequest(BaseModel):
    name: str
    file_path: str
    inputs: List[Dict[str, Any]]
    export_pdf: bool = True
    export_mcdx: bool = False
    output_dir: Optional[str] = None

class SaveLibraryConfigResponse(BaseModel):
    status: str
    config_path: str
    config_name: str

class LibraryConfigMetadata(BaseModel):
    name: str
    path: str
    created_at: str
    version: str = "1.0"

class ListLibraryConfigsResponse(BaseModel):
    configs: List[LibraryConfigMetadata]

class LoadLibraryConfigRequest(BaseModel):
    config_path: str
