import threading
import time
from typing import List, Dict, Any, Optional
import sys
import os

# Ensure we can import sibling modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from engine.protocol import (
    WorkflowConfig, WorkflowState, WorkflowStatus,
    InputConfig, FileMapping
)

class WorkflowManager:
    def __init__(self, engine_manager):
        self.engine = engine_manager
        self.workflows: Dict[str, WorkflowState] = {}

    def submit_workflow(self, workflow_id: str, config: WorkflowConfig) -> str:
        """Submit a workflow for execution in background thread"""
        state = WorkflowState(workflow_id=workflow_id, config=config)
        self.workflows[workflow_id] = state

        thread = threading.Thread(
            target=self._execute_workflow,
            args=(workflow_id,),
            daemon=True
        )
        thread.start()
        return workflow_id

    def _execute_workflow(self, workflow_id: str):
        """Execute workflow in linear order (0,1,2...)"""
        state = self.workflows[workflow_id]
        state.status = WorkflowStatus.RUNNING
        intermediate_results = {}  # {file_path: {alias: value}}

        for file_config in state.config.files:
            try:
                # Build inputs for this file (explicit + mapped)
                inputs = self._resolve_inputs(file_config, intermediate_results, state.config.mappings)

                # Execute calculation
                job_id = self.engine.submit_job("calculate_job", {
                    "path": file_config.file_path,
                    "inputs": inputs
                })

                result = self._poll_result(job_id)
                if result and result.status == "success":
                    # Store outputs for downstream mapping
                    intermediate_results[file_config.file_path] = result.data
                    state.completed_files.append(file_config.file_path)
                else:
                    raise Exception(result.error_message if result else "Job timeout")

                state.current_file_index += 1

            except Exception as e:
                state.status = WorkflowStatus.FAILED
                state.error = str(e)
                if state.config.stop_on_error:
                    break

        if state.status != WorkflowStatus.FAILED:
            state.status = WorkflowStatus.COMPLETED
            state.final_results = intermediate_results

    def _resolve_inputs(self, file_config, intermediate_results, mappings) -> List[InputConfig]:
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

    def _poll_result(self, job_id: str, timeout: float = 30.0) -> Optional[Any]:
        """Poll EngineManager for job completion (reuse BatchManager pattern)"""
        start = time.time()
        while time.time() - start < timeout:
            res = self.engine.get_job(job_id)
            if res:
                return res
            time.sleep(0.5)
        return None

    def get_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current workflow status"""
        state = self.workflows.get(workflow_id)
        if not state:
            return None

        return {
            "workflow_id": state.workflow_id,
            "status": state.status.value,
            "current_file_index": state.current_file_index,
            "total_files": len(state.config.files),
            "completed_files": state.completed_files,
            "progress": int((state.current_file_index / len(state.config.files)) * 100) if state.config.files else 0,
            "error": state.error
        }

    def stop_workflow(self, workflow_id: str):
        """Stop a running workflow"""
        state = self.workflows.get(workflow_id)
        if state and state.status == WorkflowStatus.RUNNING:
            state.status = WorkflowStatus.STOPPED
