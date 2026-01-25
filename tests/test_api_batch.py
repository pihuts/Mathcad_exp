from fastapi.testclient import TestClient
from src.server.main import app
import pytest

def test_batch_api_flow():
    with TestClient(app) as client:
        # 1. Start Batch
        batch_data = {
            "batch_id": "api_test_batch",
            "inputs": [{"L": 10}, {"L": 20}],
            "output_dir": "api_test_results"
        }
        # We use /api/v1/batch/start
        response = client.post("/api/v1/batch/start", json=batch_data)
        if response.status_code != 200:
            print(f"Error starting batch: {response.status_code} - {response.text}")
        assert response.status_code == 200
        assert response.json()["status"] == "started"

        # 2. Get Status
        response = client.get("/api/v1/batch/api_test_batch")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "api_test_batch"
        assert data["total"] == 2
        
        # 3. Stop Batch
        response = client.post("/api/v1/batch/api_test_batch/stop")
        assert response.status_code == 200
        assert response.json()["status"] == "stopped"

    # Clean up (usually we'd mock the manager to avoid side effects)
    import os
    if os.path.exists("api_test_results"):
        import shutil
        shutil.rmtree("api_test_results")

if __name__ == "__main__":
    test_batch_api_flow()
