import multiprocessing
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.harness import run_harness
from engine.protocol import JobRequest, JobResult

def test_harness_manual():
    # Use multiprocessing.Queue
    q_in = multiprocessing.Queue()
    q_out = multiprocessing.Queue()
    
    print("Starting harness process...")
    p = multiprocessing.Process(target=run_harness, args=(q_in, q_out))
    p.start()
    
    try:
        # Give it a moment to start
        time.sleep(1)
        if not p.is_alive():
            print("Process died immediately!")
            return

        # Send Ping
        print("Sending ping...")
        req = JobRequest(command="ping")
        q_in.put(req)
        
        # Wait for result
        print("Waiting for response...")
        try:
            res = q_out.get(timeout=5)
            print(f"Received: {res}")
            assert res.job_id == req.id
            assert res.status == "success"
            assert res.data["response"] == "pong"
            print("Ping test passed!")
        except Exception as e:
            print(f"Failed to get response: {e}")
            
    finally:
        print("Terminating process...")
        q_in.put(None) # Soft exit
        p.join(timeout=2)
        if p.is_alive():
            print("Force terminating...")
            p.terminate()
            p.join()
        print("Process ended.")

if __name__ == "__main__":
    # Windows support for multiprocessing
    multiprocessing.freeze_support()
    test_harness_manual()
