import multiprocessing
import queue
import time
import threading
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
        
        # Result storage
        self.results: Dict[str, JobResult] = {}
        self.collector_thread: Optional[threading.Thread] = None
        self.stop_collector: bool = False
        
    def start_engine(self):
        """Starts the sidecar process and result collector."""
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
        
        # Start collector thread
        self.stop_collector = False
        self.collector_thread = threading.Thread(target=self._collect_results, daemon=True)
        self.collector_thread.start()

    def stop_engine(self):
        """Stops the sidecar process gracefully, then forcefully."""
        if not self.is_running():
            return

        print("Stopping engine...")
        
        # Stop collector
        self.stop_collector = True
        if self.collector_thread:
            self.collector_thread.join(timeout=1.0)
            
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
        self.collector_thread = None
        self.results.clear()
        print("Engine stopped.")

    def restart_engine(self):
        self.stop_engine()
        self.start_engine()

    def is_running(self) -> bool:
        return self.process is not None and self.process.is_alive()

    def submit_job(self, command: str, payload: Dict[str, Any] = None) -> str:
        """
        Submits a job to the engine. Returns the job ID.
        """
        if not self.is_running():
            raise RuntimeError("Engine is not running")
            
        if payload is None:
            payload = {}
            
        req = JobRequest(command=command, payload=payload)
        self.input_queue.put(req)
        return req.id
        
    def _collect_results(self):
        """Background thread to drain output queue into results dict."""
        while not self.stop_collector:
            if not self.output_queue:
                break
            try:
                # Short timeout to allow checking stop_collector
                result = self.output_queue.get(timeout=0.1)
                if result:
                    self.results[result.job_id] = result
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in result collector: {e}")
                
    def get_job(self, job_id: str) -> Optional[JobResult]:
        """Returns the result of a job if available."""
        return self.results.get(job_id)

    def get_result(self, timeout: float = 5.0) -> Optional[JobResult]:
        """
        Blocks waiting for the next result from the queue.
        DEPRECATED: Use get_job(job_id) instead.
        Kept for backward compatibility by polling self.results.
        """
        # This is hacky: wait for *any* result to appear in self.results
        # that wasn't there before? No, we don't know state.
        # Simple implementation: Wait for ANY result to be in the dict.
        # Ideally, tests should be updated.
        
        start = time.time()
        while time.time() - start < timeout:
             if self.results:
                 # Return the most recent one (arbitrary)
                 return list(self.results.values())[-1]
             time.sleep(0.1)
        return None
