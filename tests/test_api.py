import sys
import os
import time
from fastapi.testclient import TestClient

# Add root to path (parent of tests)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.server.main import app

def test_api_flow():
    print("Starting TestClient with lifespan...")
    with TestClient(app) as client:
        print("1. Root check")
        response = client.get("/")
        assert response.status_code == 200
        print(response.json())
        
        # Allow engine process to start
        time.sleep(2)
        
        print("\n2. Submit Job (ping)")
        response = client.post("/api/v1/jobs", json={"command": "ping", "payload": {}})
        if response.status_code != 200:
            print(f"Submit failed: {response.text}")
        assert response.status_code == 200
        data = response.json()
        job_id = data["job_id"]
        print(f"Job submitted: {job_id}")
        
        print("\n3. Poll Result")
        result = None
        for _ in range(20):
            resp = client.get(f"/api/v1/jobs/{job_id}")
            if resp.status_code == 200:
                result = resp.json()
                print("Result found!")
                break
            elif resp.status_code == 404:
                print(".", end="", flush=True)
            else:
                print(f"Error: {resp.status_code} {resp.text}")
            time.sleep(0.5)
        print()
            
        if result is None:
            print("Timed out waiting for result")
            
        assert result is not None
        print(f"Result: {result}")
        assert result["status"] == "success"
        
        print("\n4. Restart Engine")
        resp = client.post("/api/v1/control/restart")
        assert resp.status_code == 200
        print(resp.json())
        
        # Verify it still works
        time.sleep(3) # Restart takes a moment
        response = client.post("/api/v1/jobs", json={"command": "ping", "payload": {}})
        assert response.status_code == 200
        print("Submit after restart success")

if __name__ == "__main__":
    # Windows multiprocessing support
    import multiprocessing
    multiprocessing.freeze_support()
    test_api_flow()
