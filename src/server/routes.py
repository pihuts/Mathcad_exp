from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import time
from .dependencies import get_engine_manager
from src.engine.manager import EngineManager
from .schemas import JobSubmission, JobResponse, ControlResponse, BatchRequest, BatchStatus

router = APIRouter()

@router.post("/jobs", response_model=JobResponse)
async def submit_job(job: JobSubmission, manager: EngineManager = Depends(get_engine_manager)):
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

# Batch Endpoints

@router.post("/batch/start", response_model=ControlResponse)
async def start_batch(req: BatchRequest, manager: EngineManager = Depends(get_engine_manager)):
    if not manager.is_running():
        raise HTTPException(status_code=503, detail="Engine is not running")
    
    manager.batch_manager.start_batch(req.batch_id, req.inputs, req.output_dir)
    return ControlResponse(status="started", message=f"Batch {req.batch_id} initiated")

@router.get("/batch/{batch_id}", response_model=BatchStatus)
async def get_batch_status(batch_id: str, manager: EngineManager = Depends(get_engine_manager)):
    status = manager.batch_manager.get_status(batch_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    return status

@router.post("/batch/{batch_id}/stop", response_model=ControlResponse)
async def stop_batch(batch_id: str, manager: EngineManager = Depends(get_engine_manager)):
    manager.batch_manager.stop_batch(batch_id)
    return ControlResponse(status="stopped", message=f"Batch {batch_id} stopping signal sent")

@router.post("/engine/analyze")
async def analyze_file(payload: Dict[str, Any], manager: EngineManager = Depends(get_engine_manager)):
    if not manager.is_running():
        raise HTTPException(status_code=503, detail="Engine is not running")

    path = payload.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Missing 'path' in payload")

    try:
        # We'll use a blocking wait for this simple analysis
        job_id = manager.submit_job("get_metadata", {"path": path})

        # Poll for result (max 60 seconds - Mathcad launch can be slow)
        start_time = time.time()
        while time.time() - start_time < 60:
            result = manager.get_job(job_id)
            if result:
                if result.status == "success":
                    return result.data
                else:
                    msg = result.error_message or "Unknown error"
                    if "No worksheet open" in msg or "Mathcad not connected" in msg:
                        msg += " (Ensure Mathcad Prime is installed and the file path is correct)"
                    raise HTTPException(status_code=500, detail=msg)
            time.sleep(0.5)

        raise HTTPException(status_code=504, detail="Analysis timed out (Mathcad took too long to respond)")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Endpoints

@router.post("/workflows")
async def create_workflow(req: Dict[str, Any], manager: EngineManager = Depends(get_engine_manager)):
    """Create and start a workflow from configuration"""
    if not manager.is_running():
        raise HTTPException(status_code=503, detail="Engine is not running")

    try:
        # Parse workflow config from request
        from src.engine.protocol import WorkflowConfig
        config = WorkflowConfig(**req)

        # Generate workflow ID
        workflow_id = f"workflow-{int(time.time())}"

        # Submit workflow
        manager.workflow_manager.submit_workflow(workflow_id, config)

        return {"workflow_id": workflow_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/workflows/{workflow_id}/start")
async def start_workflow(workflow_id: str, manager: EngineManager = Depends(get_engine_manager)):
    """Start a workflow (alias for create - workflows auto-start on submit)"""
    status = manager.workflow_manager.get_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    return {"workflow_id": workflow_id, "status": status["status"]}

@router.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str, manager: EngineManager = Depends(get_engine_manager)):
    """Get current workflow status"""
    status = manager.workflow_manager.get_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    return status

@router.post("/workflows/{workflow_id}/stop")
async def stop_workflow(workflow_id: str, manager: EngineManager = Depends(get_engine_manager)):
    """Stop a running workflow"""
    manager.workflow_manager.stop_workflow(workflow_id)
    return {"workflow_id": workflow_id, "status": "stopped"}

