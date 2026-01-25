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

def run_harness(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue):
    """
    The entry point for the sidecar process.
    """
    print(f"Harness process started. PID: {os.getpid()}")
    
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
