from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .dependencies import get_engine_manager
from src.engine.manager import EngineManager

router = APIRouter()

class JobSubmission(BaseModel):
    command: str
    payload: Dict[str, Any] = {}

class JobResponse(BaseModel):
    job_id: str
    status: str = "submitted"

class ControlResponse(BaseModel):
    status: str
    message: str

@router.post("/jobs", response_model=JobResponse)
async def submit_job(job: JobSubmission, manager: EngineManager = Depends(get_engine_manager)):
    """
    Submit a command to the engine.
    Common commands:
    - 'ping': {}
    - 'open_file': {'path': '...'}
    - 'set_input': {'variable': '...', 'value': ...}
    - 'get_output': {'variable': '...'}
    """
    if not manager.is_running():
        raise HTTPException(status_code=503, detail="Engine is not running")
    
    try:
        job_id = manager.submit_job(job.command, job.payload)
        return JobResponse(job_id=job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}")
async def get_job_result(job_id: str, manager: EngineManager = Depends(get_engine_manager)):
    result = manager.get_job(job_id)
    if not result:
        # Since we don't track pending jobs explicitly (they are in the queue),
        # 404 is appropriate for "result not found yet".
        # A 202 Accepted could be better if we knew it was valid.
        raise HTTPException(status_code=404, detail="Job result not found or pending")
    
    return result

@router.post("/control/stop", response_model=ControlResponse)
async def stop_engine(manager: EngineManager = Depends(get_engine_manager)):
    manager.stop_engine()
    return ControlResponse(status="stopped", message="Engine stopped")

@router.post("/control/restart", response_model=ControlResponse)
async def restart_engine(manager: EngineManager = Depends(get_engine_manager)):
    manager.restart_engine()
    return ControlResponse(status="restarted", message="Engine restarted")
