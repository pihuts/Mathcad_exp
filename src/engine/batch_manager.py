import threading
import time
import os
from typing import List, Dict, Any, Optional
from engine.manager import EngineManager
from engine.protocol import JobResult, InputConfig

class BatchManager:
    def __init__(self, engine_manager: EngineManager):
        self.engine = engine_manager
        self.batches: Dict[str, Dict[str, Any]] = {}

    def start_batch(self, batch_id: str, inputs_list: List[Dict[str, Any]], output_dir: str):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        self.batches[batch_id] = {
            "id": batch_id,
            "total": len(inputs_list),
            "completed": 0,
            "results": [],
            "status": "running",
            "error": None
        }
        
        thread = threading.Thread(
            target=self._process_batch,
            args=(batch_id, inputs_list, output_dir),
            daemon=True
        )
        thread.start()

    def _process_batch(self, batch_id: str, inputs_list: List[Dict[str, Any]], output_dir: str):
        batch = self.batches[batch_id]
        
        for i, row_input in enumerate(inputs_list):
            if batch["status"] == "stopped":
                break
                
            success = False
            retries = 1
            while not success and retries >= 0:
                try:
                    # 1. Submit job (assuming calculate_job command)
                    # Build InputConfig objects to preserve units
                    path = row_input.get("path")

                    # Extract input configs from row_input
                    # Frontend sends: {"path": "file.mcdx", "L": {"value": 10, "units": "ft"}, "P": {"value": 5}}
                    # Legacy format: {"path": "file.mcdx", "L": 10, "P": 5}
                    input_configs = []
                    for k, v in row_input.items():
                        if k == "path":
                            continue  # Skip path field
                        if isinstance(v, dict) and "value" in v:
                            # New format: structured dict with value and units
                            units = v.get("units")
                            input_configs.append(InputConfig(alias=k, value=v["value"], units=units))
                        else:
                            # Legacy format: simple key-value (units not specified)
                            # Wrap in InputConfig with units=None
                            input_configs.append(InputConfig(alias=k, value=v, units=None))

                    job_id = self.engine.submit_job("calculate_job", {"path": path, "inputs": input_configs})
                    
                    # 2. Poll for completion
                    result = self._poll_result(job_id)
                    if result and result.status == "success":
                        # 3. Save as PDF
                        # We use 3 as default for PDF
                        save_path = os.path.join(output_dir, f"result_{i}.pdf")
                        save_job_id = self.engine.submit_job("save_as", {"path": save_path, "format": 3})
                        save_result = self._poll_result(save_job_id)
                        
                        batch["completed"] += 1
                        batch["results"].append({
                            "row": i,
                            "status": "success",
                            "data": result.data,
                            "pdf": save_path if save_result and save_result.status == "success" else None
                        })
                        success = True
                    else:
                        raise Exception(result.error_message if result else "Job timeout")
                except Exception as e:
                    print(f"Batch {batch_id} Row {i} failed: {e}")
                    retries -= 1
                    if retries >= 0:
                        print("Restarting engine and retrying...")
                        try:
                            self.engine.restart_engine()
                            # Re-connect after restart
                            conn_job = self.engine.submit_job("connect")
                            self._poll_result(conn_job)
                        except:
                            pass
                    else:
                        batch["results"].append({
                            "row": i,
                            "status": "failed",
                            "error": str(e)
                        })
                        batch["completed"] += 1 # We count failed rows as completed in terms of progress
                        success = True 

        if batch["status"] == "running":
            batch["status"] = "completed"

    def _poll_result(self, job_id: str, timeout: float = 30.0) -> Optional[JobResult]:
        start = time.time()
        while time.time() - start < timeout:
            res = self.engine.get_job(job_id)
            if res:
                return res
            time.sleep(0.5)
        return None

    def get_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        return self.batches.get(batch_id)

    def stop_batch(self, batch_id: str):
        if batch_id in self.batches:
            self.batches[batch_id]["status"] = "stopped"
