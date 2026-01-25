import multiprocessing
import queue
import time
from typing import Optional, Dict, Any, Union
import sys
import os

# Ensure we can import sibling modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from engine.protocol import JobRequest, JobResult
from engine.harness import run_harness

class EngineManager:
    def __init__(self):
        self.process: Optional[multiprocessing.Process] = None
        self.input_queue: Optional[multiprocessing.Queue] = None
        self.output_queue: Optional[multiprocessing.Queue] = None
        
    def start_engine(self):
        """Starts the sidecar process."""
        if self.is_running():
            print("Engine already running.")
            return

        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
        
        self.process = multiprocessing.Process(
            target=run_harness,
            args=(self.input_queue, self.output_queue),
            daemon=True 
        )
        self.process.start()
        print(f"Engine started with PID: {self.process.pid}")

    def stop_engine(self):
        """Stops the sidecar process gracefully, then forcefully."""
        if not self.is_running():
            return

        print("Stopping engine...")
        try:
            self.input_queue.put(None)
            self.process.join(timeout=2.0)
        except Exception as e:
            print(f"Error during graceful shutdown: {e}")

        if self.process.is_alive():
            print("Engine did not stop gracefully, terminating...")
            self.process.terminate()
            self.process.join(timeout=1.0)
        
        self.process = None
        self.input_queue = None
        self.output_queue = None
        print("Engine stopped.")

    def restart_engine(self):
        self.stop_engine()
        self.start_engine()

    def is_running(self) -> bool:
        return self.process is not None and self.process.is_alive()

    def submit_job(self, command: str, payload: Dict[str, Any] = None) -> str:
        """
        Submits a job to the engine. Returns the job ID.
        Does not wait for result.
        """
        if not self.is_running():
            raise RuntimeError("Engine is not running")
            
        if payload is None:
            payload = {}
            
        req = JobRequest(command=command, payload=payload)
        self.input_queue.put(req)
        return req.id

    def get_result(self, timeout: float = 5.0) -> Optional[JobResult]:
        """
        Blocks waiting for the next result from the queue.
        """
        if not self.output_queue:
             raise RuntimeError("Engine not initialized")
             
        try:
            return self.output_queue.get(timeout=timeout)
        except queue.Empty:
            return None
