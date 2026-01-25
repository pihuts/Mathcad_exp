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

from engine.protocol import JobRequest, JobResult
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
                    inputs = job.payload.get("inputs", {})
                    
                    if path:
                        worker.open_file(path)
                    
                    # Set inputs
                    for alias, value in inputs.items():
                        worker.set_input(alias, value)
                        
                    # Fetch all outputs
                    # We get the list of available outputs first
                    meta_outputs = worker.get_outputs()
                    output_data = {}
                    
                    for out_meta in meta_outputs:
                        alias = out_meta["alias"]
                        try:
                            val = worker.get_output_value(alias)
                            output_data[alias] = val
                        except Exception as e:
                            # Log error but don't fail the whole job? 
                            # Or maybe return error?
                            # For now, return error string as value
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
