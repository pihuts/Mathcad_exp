from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import time
import asyncio
import os
import sys
from .dependencies import get_engine_manager
from src.engine.manager import EngineManager
from .schemas import JobSubmission, JobResponse, ControlResponse, BatchRequest, BatchStatus

def _open_file_dialog():
    """Open native file dialog - runs in separate thread"""
    from tkinter import Tk, filedialog
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.focus_force()

    file_path = filedialog.askopenfilename(
        title="Select Mathcad Prime file",
        filetypes=[
            ("Mathcad Prime", "*.mcdx"),
            ("All files", "*.*")
        ]
    )

    root.destroy()
    return file_path

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
    
    manager.batch_manager.start_batch(
        req.batch_id, 
        req.inputs, 
        req.output_dir,
        export_pdf=req.export_pdf,
        export_mcdx=req.export_mcdx
    )
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

@router.post("/files/open")
async def open_file_natively(payload: Dict[str, Any]):
    """Open a file using the system default application"""
    path = payload.get("path")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=400, detail="Invalid or missing path")
    
    try:
        # Use startfile on Windows, open on Mac, xdg-open on Linux
        if hasattr(os, 'startfile'):
            os.startfile(path)
        else:
            import subprocess
            subprocess.call(['open', path] if sys.platform == 'darwin' else ['xdg-open', path])
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/browse")
async def browse_for_file():
    """
    Open native Windows file dialog and return selected path.
    Runs tkinter in separate thread to avoid blocking FastAPI.
    """
    try:
        file_path = await asyncio.to_thread(_open_file_dialog)
        if not file_path:
            return {"file_path": None, "cancelled": True}
        return {"file_path": file_path, "cancelled": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File dialog error: {str(e)}")


# Library Endpoints

@router.post("/library/save")
async def save_library_config(req: Dict[str, Any]):
    """
    Save a batch configuration as a named library template.
    Configs are stored as JSON files in {mcdx_file_parent}/{mcdx_filename}_configs/
    """
    from pathlib import Path
    from src.engine.protocol import BatchConfig
    import json

    try:
        # Parse and validate request using Pydantic
        config = BatchConfig(**req)

        # Determine config directory (next to the .mcdx file)
        mcdx_path = Path(config.file_path)
        if not mcdx_path.exists():
            raise HTTPException(status_code=400, detail=f"Mathcad file not found: {config.file_path}")

        config_dir = mcdx_path.parent / f"{mcdx_path.stem}_configs"
        config_dir.mkdir(exist_ok=True)

        # Sanitize config name for filename
        safe_name = "".join(c for c in config.name if c.isalnum() or c in (' ', '-', '_')).strip()
        config_file = config_dir / f"{safe_name}.json"

        # Convert to relative paths for portability
        config_dict = config.model_dump(mode='json')
        config_dict['file_path'] = str(mcdx_path.name)  # Store just filename
        if config_dict.get('output_dir'):
            output_rel = str(Path(config_dict['output_dir']).relative_to(mcdx_path.parent))
            config_dict['output_dir'] = output_rel

        # Write JSON file
        config_file.write_text(json.dumps(config_dict, indent=2), encoding='utf-8')

        return {
            "status": "success",
            "config_path": str(config_file),
            "config_name": config.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/library/list")
async def list_library_configs(file_path: str):
    """
    List all saved library configurations for a given Mathcad file.
    Returns metadata (name, path, created_at) for each config.
    """
    from pathlib import Path
    import json

    try:
        mcdx_path = Path(file_path)
        if not mcdx_path.exists():
            raise HTTPException(status_code=400, detail=f"Mathcad file not found: {file_path}")

        config_dir = mcdx_path.parent / f"{mcdx_path.stem}_configs"

        if not config_dir.exists():
            return {"configs": []}

        configs = []
        for config_file in config_dir.glob("*.json"):
            try:
                config_data = json.loads(config_file.read_text(encoding='utf-8'))
                configs.append({
                    "name": config_data.get("name", config_file.stem),
                    "path": str(config_file),
                    "created_at": config_data.get("created_at", "unknown"),
                    "version": config_data.get("version", "1.0")
                })
            except Exception:
                # Skip corrupted config files
                continue

        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/library/load")
async def load_library_config(req: Dict[str, Any]):
    """
    Load a saved library configuration by file path.
    Returns BatchConfig with absolute paths resolved.
    """
    from pathlib import Path
    from src.engine.protocol import BatchConfig
    import json

    try:
        config_path_str = req.get("config_path")
        if not config_path_str:
            raise HTTPException(status_code=400, detail="Missing config_path")

        config_path = Path(config_path_str)
        if not config_path.exists():
            raise HTTPException(status_code=404, detail=f"Config file not found: {config_path_str}")

        # Read and validate using Pydantic
        config_json = config_path.read_text(encoding='utf-8')
        config_dict = json.loads(config_json)

        # Resolve relative paths to absolute
        mcdx_path = config_path.parent.parent / config_dict['file_path']
        config_dict['file_path'] = str(mcdx_path.resolve())

        if config_dict.get('output_dir'):
            output_abs = config_path.parent.parent / config_dict['output_dir']
            config_dict['output_dir'] = str(output_abs.resolve())

        # Validate with Pydantic
        config = BatchConfig.model_validate(config_dict)

        return config.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Workflow Library Endpoints

@router.post("/library/save/workflow")
async def save_workflow_config(req: Dict[str, Any]):
    """
    Save a workflow configuration as a named library template.
    Workflows stored in workflow_library/ directory at project root.
    """
    from pathlib import Path
    from src.engine.protocol import WorkflowConfig
    import json

    try:
        # Parse and validate request using Pydantic
        config = WorkflowConfig(**req)

        # Use workflow_library/ at project root (cross-workflow configs)
        # Or could store next to first file in workflow
        if config.files and len(config.files) > 0:
            first_file = Path(config.files[0].file_path)
            library_dir = first_file.parent.parent / "workflow_library"
        else:
            # Fallback to current directory
            library_dir = Path.cwd() / "workflow_library"

        library_dir.mkdir(exist_ok=True)

        # Sanitize config name for filename
        safe_name = "".join(c for c in config.name if c.isalnum() or c in (' ', '-', '_')).strip()
        config_file = library_dir / f"{safe_name}.json"

        # Convert to relative paths for portability
        # For workflows, store paths relative to library_dir
        config_dict = config.model_dump(mode='json')
        base_path = library_dir.parent

        for file in config_dict.get('files', []):
            if file.get('file_path'):
                try:
                    rel_path = Path(file['file_path']).relative_to(base_path)
                    file['file_path'] = str(rel_path)
                except ValueError:
                    # File on different drive - keep absolute
                    pass

        if config_dict.get('output_dir'):
            try:
                output_rel = Path(config_dict['output_dir']).relative_to(base_path)
                config_dict['output_dir'] = str(output_rel)
            except ValueError:
                pass

        # Write JSON file
        config_file.write_text(json.dumps(config_dict, indent=2), encoding='utf-8')

        return {
            "status": "success",
            "config_path": str(config_file),
            "config_name": config.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/library/list/workflows")
async def list_workflow_configs():
    """
    List all saved workflow configurations.
    Returns metadata (name, path, created_at) for each config.
    """
    from pathlib import Path
    import json

    try:
        library_dir = Path.cwd() / "workflow_library"

        if not library_dir.exists():
            return {"configs": []}

        configs = []
        for config_file in library_dir.glob("*.json"):
            try:
                config_data = json.loads(config_file.read_text(encoding='utf-8'))
                configs.append({
                    "name": config_data.get("name", config_file.stem),
                    "path": str(config_file),
                    "created_at": config_data.get("created_at", "unknown"),
                    "files_count": len(config_data.get("files", [])),
                })
            except Exception:
                continue

        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/library/load/workflow")
async def load_workflow_config(req: Dict[str, Any]):
    """
    Load a saved workflow configuration by file path.
    Returns WorkflowConfig with absolute paths resolved.
    """
    from pathlib import Path
    from src.engine.protocol import WorkflowConfig
    import json

    try:
        config_path_str = req.get("config_path")
        if not config_path_str:
            raise HTTPException(status_code=400, detail="Missing config_path")

        config_path = Path(config_path_str)
        if not config_path.exists():
            raise HTTPException(status_code=404, detail=f"Config file not found: {config_path_str}")

        # Read and validate using Pydantic
        config_json = config_path.read_text(encoding='utf-8')
        config_dict = json.loads(config_json)

        # Resolve relative paths to absolute
        base_path = config_path.parent.parent

        for file in config_dict.get('files', []):
            if file.get('file_path'):
                resolved_path = base_path / file['file_path']
                file['file_path'] = str(resolved_path.resolve())

        if config_dict.get('output_dir'):
            output_abs = base_path / config_dict['output_dir']
            config_dict['output_dir'] = str(output_abs.resolve())

        # Validate with Pydantic
        config = WorkflowConfig.model_validate(config_dict)

        return config.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

