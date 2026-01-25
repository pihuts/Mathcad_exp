import pytest
from unittest.mock import MagicMock, patch
from engine.batch_manager import BatchManager
from engine.protocol import JobResult
import os

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.is_running.return_value = True
    return engine

def test_batch_manager_start(mock_engine):
    bm = BatchManager(mock_engine)
    
    inputs = [{"a": 1}, {"a": 2}]
    batch_id = "test_batch"
    output_dir = "test_output"
    
    # Mock submit_job and get_job
    mock_engine.submit_job.side_effect = ["job1", "save1", "job2", "save2"]
    
    # Mock get_job results
    res1 = JobResult(job_id="job1", status="success", data={"val": 10})
    save1 = JobResult(job_id="save1", status="success", data={})
    res2 = JobResult(job_id="job2", status="success", data={"val": 20})
    save2 = JobResult(job_id="save2", status="success", data={})
    
    mock_engine.get_job.side_effect = [res1, save1, res2, save2]
    
    bm.start_batch(batch_id, inputs, output_dir)
    
    # Wait for completion (it runs in a thread)
    import time
    start = time.time()
    while bm.get_status(batch_id)["status"] == "running" and time.time() - start < 5:
        time.sleep(0.1)
        
    status = bm.get_status(batch_id)
    assert status["status"] == "completed"
    assert status["completed"] == 2
    assert len(status["results"]) == 2
    assert status["results"][0]["data"]["val"] == 10
    
    # Clean up test output dir
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

if __name__ == "__main__":
    # If run directly, use pytest
    pytest.main([__file__])
