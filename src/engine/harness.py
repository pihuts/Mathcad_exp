import time
import multiprocessing
import traceback
import sys
import os
from queue import Empty

# Ensure we can import sibling modules when running in a separate process
# This might be redundant if the environment is set up correctly, but safe for standalone
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from engine.protocol import JobRequest, JobResult, InputConfig
from engine.worker import MathcadWorker

def run_harness(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue):
    """
    The entry point for the sidecar process.
    """
    print(f"Harness process started. PID: {os.getpid()}")
    
    worker = MathcadWorker()

    while True:
        try:
            # Blocking get with timeout
            try:
                job_data = input_queue.get(timeout=0.5)
            except Empty:
                continue
            
            # Check for exit signal
            if job_data is None:
                print("Harness received exit signal. Shutting down.")
                break
                
            # Parse job
            if not isinstance(job_data, JobRequest):
                 result = JobResult(
                     job_id="unknown",
                     status="error",
                     error_message=f"Invalid job data type: {type(job_data)}"
                 )
                 output_queue.put(result)
                 continue
            
            job: JobRequest = job_data
            # print(f"Processing job: {job.id} - {job.command}")
            
            try:
                # Process commands
                if job.command == "ping":
                    result = JobResult(
                        job_id=job.id,
                        status="success",
                        data={"response": "pong"}
                    )
                elif job.command == "connect":
                    worker.connect()
                    result = JobResult(
                        job_id=job.id,
                        status="success",
                        data={"message": "Connected to Mathcad"}
                    )
                elif job.command == "save_as":
                    path = job.payload.get("path")
                    format_enum = job.payload.get("format")
                    if not path:
                        raise ValueError("Payload missing 'path'")
                    worker.save_as(path, format_enum)
                    result = JobResult(
                        job_id=job.id,
                        status="success",
                        data={"message": f"Saved to {path}"}
                    )
                elif job.command == "load_file":
                    path = job.payload.get("path")
                    if not path:
                         raise ValueError("Payload missing 'path'")
                    worker.open_file(path)
                    result = JobResult(
                        job_id=job.id,
                        status="success",
                        data={"message": f"Opened {path}"}
                    )
                elif job.command == "get_metadata":
                    # Ensure connected
                    if not worker.is_connected():
                        worker.connect()

                    path = job.payload.get("path")
                    if path:
                        worker.open_file(path)
                        
                    inputs = worker.get_inputs()
                    outputs = worker.get_outputs()
                    result = JobResult(
                        job_id=job.id,
                        status="success",
                        data={
                            "inputs": inputs,
                            "outputs": outputs
                        }
                    )
                elif job.command == "calculate_job":
                    path = job.payload.get("path")
                    inputs_config = job.payload.get("inputs", [])  # Array of InputConfig objects

                    if path:
                        worker.open_file(path)

                    # Set inputs with units
                    for input_config in inputs_config:
                        # Support both old dict format and new InputConfig objects
                        if isinstance(input_config, dict):
                            alias = input_config.get("alias")
                            value = input_config.get("value")
                            units = input_config.get("units")
                        else:
                            # InputConfig object
                            alias = input_config.alias
                            value = input_config.value
                            units = input_config.units

                        if alias and value is not None:
                            worker.set_input(alias, value, units)

                    # Recalculate worksheet
                    worker.synchronize()

                    # Fetch all outputs
                    meta_outputs = worker.get_outputs()
                    output_data = {}

                    for out_meta in meta_outputs:
                        alias = out_meta["alias"]
                        try:
                            val = worker.get_output_value(alias)
                            output_data[alias] = val
                        except Exception as e:
                            output_data[alias] = f"Error: {str(e)}"

                    result = JobResult(
                        job_id=job.id,
                        status="success",
                        data={"outputs": output_data}
                    )
                else:
                    result = JobResult(
                        job_id=job.id,
                        status="error",
                        error_message=f"Unknown command: {job.command}"
                    )
                
                output_queue.put(result)
                
            except Exception as e:
                # Catch job-processing errors
                err_msg = "".join(traceback.format_exception(None, e, e.__traceback__))
                result = JobResult(
                    job_id=job.id,
                    status="error",
                    error_message=err_msg
                )
                output_queue.put(result)

        except KeyboardInterrupt:
             print("Harness caught KeyboardInterrupt. Exiting.")
             break
        except Exception as e:
            print(f"CRITICAL HARNESS ERROR: {e}")
            traceback.print_exc()
            time.sleep(1) 
