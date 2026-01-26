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

    def start_batch(self, batch_id: str, inputs_list: List[Dict[str, Any]], output_dir: str, 
                    export_pdf: bool = True, export_mcdx: bool = False):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        self.batches[batch_id] = {
            "id": batch_id,
            "total": len(inputs_list),
            "completed": 0,
            "results": [],
            "generated_files": [],
            "status": "running",
            "error": None
        }
        
        thread = threading.Thread(
            target=self._process_batch,
            args=(batch_id, inputs_list, output_dir, export_pdf, export_mcdx),
            daemon=True
        )
        thread.start()

    def _process_batch(self, batch_id: str, inputs_list: List[Dict[str, Any]], output_dir: str,
                       export_pdf: bool, export_mcdx: bool):
        batch = self.batches[batch_id]
        import re
        
        def sanitize(s: str) -> str:
            return re.sub(r'[<>:"/\\|?*]', '_', str(s))

        # Helper to update execution stage for current row
        def update_stage(row_idx, stage_msg):
            # Check if we already have a partial result for this row, if so update it
            # Otherwise create a new pending result
            found = False
            for res in batch["results"]:
                if res["row"] == row_idx:
                    res["stage"] = stage_msg
                    found = True
                    break
            if not found:
                batch["results"].append({
                    "row": row_idx,
                    "status": "running",
                    "stage": stage_msg
                })

        for i, row_input in enumerate(inputs_list):
            if batch["status"] == "stopped":
                break
                
            success = False
            retries = 1
            while not success and retries >= 0:
                try:
                    update_stage(i, "Calculating...")
                    
                    # 1. Submit job (assuming calculate_job command)
                    path = row_input.get("path")
                    base_name = os.path.splitext(os.path.basename(path))[0]

                    # Extract input configs and build suffix for filename
                    input_configs = []
                    suffix_parts = []
                    for k, v in row_input.items():
                        if k == "path":
                            continue
                        
                        val = v["value"] if isinstance(v, dict) and "value" in v else v
                        units = v.get("units") if isinstance(v, dict) else None
                        
                        input_configs.append(InputConfig(alias=k, value=val, units=units))
                        suffix_parts.append(f"{sanitize(k)}-{sanitize(val)}")

                    filename_base = f"{base_name}_{'_'.join(suffix_parts)}" if suffix_parts else f"{base_name}_{i}"
                    
                    job_id = self.engine.submit_job("calculate_job", {"path": path, "inputs": input_configs})
                    
                    # 2. Poll for completion - INCREASED TIMEOUT to 120s
                    result = self._poll_result(job_id, timeout=120.0)
                    if result and result.status == "success":
                        pdf_path = None
                        mcdx_path = None

                        # 3. Export as PDF if requested
                        if export_pdf:
                            update_stage(i, "Saving PDF...")
                            save_path = os.path.join(output_dir, f"{filename_base}.pdf")
                            # Delete if exists to avoid Mathcad prompt
                            if os.path.exists(save_path):
                                try:
                                    os.remove(save_path)
                                except:
                                    pass
                                    
                            save_job_id = self.engine.submit_job("save_as", {"path": save_path, "format": 3})
                            save_result = self._poll_result(save_job_id, timeout=120.0)
                            if save_result and save_result.status == "success":
                                pdf_path = save_path
                                batch["generated_files"].append(pdf_path)
                            else:
                                print(f"Warning: PDF export failed: {save_result.error_message if save_result else 'Timeout'}")
                        
                        # 4. Export as MCDX if requested
                        if export_mcdx:
                            update_stage(i, "Saving MCDX...")
                            save_path = os.path.join(output_dir, f"{filename_base}.mcdx")
                            # Delete if exists
                            if os.path.exists(save_path):
                                try:
                                    os.remove(save_path)
                                except:
                                    pass

                            save_job_id = self.engine.submit_job("save_as", {"path": save_path, "format": 0})
                            save_result = self._poll_result(save_job_id, timeout=120.0)
                            if save_result and save_result.status == "success":
                                mcdx_path = save_path
                                batch["generated_files"].append(mcdx_path)
                            else:
                                print(f"Warning: MCDX export failed: {save_result.error_message if save_result else 'Timeout'}")
                        
                        # Finalize row
                        # Update the existing 'running' entry
                        for res in batch["results"]:
                            if res["row"] == i:
                                res.update({
                                    "status": "success",
                                    "stage": "Completed",
                                    "data": result.data,
                                    "pdf": pdf_path,
                                    "mcdx": mcdx_path
                                })
                                break
                        
                        batch["completed"] += 1
                        success = True
                    else:
                        raise Exception(result.error_message if result else "Job timeout")
                except Exception as e:
                    print(f"Batch {batch_id} Row {i} failed: {e}")
                    retries -= 1
                    stages = [] # dummy
                    if retries >= 0:
                        update_stage(i, "Retrying (Engine Restart)...")
                        print("Restarting engine and retrying...")
                        try:
                            self.engine.restart_engine()
                            conn_job = self.engine.submit_job("connect")
                            self._poll_result(conn_job)
                        except:
                            pass
                    else:
                        # Update existing entry to failed
                        for res in batch["results"]:
                            if res["row"] == i:
                                res.update({
                                    "status": "failed",
                                    "stage": "Failed",
                                    "error": str(e)
                                })
                                break
                        batch["completed"] += 1
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
