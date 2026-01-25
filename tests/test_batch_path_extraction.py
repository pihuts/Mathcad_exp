import pytest
from unittest.mock import MagicMock, patch, call
from engine.batch_manager import BatchManager
from engine.protocol import JobResult
import os

@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.is_running.return_value = True
    return engine

def test_batch_manager_with_path_extraction(mock_engine):
    """Test that BatchManager correctly extracts path from input rows"""
    bm = BatchManager(mock_engine)

    # Inputs with path field (as sent by frontend)
    inputs = [{"a": 1, "path": "C:\\test\\file.mcdx"}, {"a": 2, "path": "C:\\test\\file.mcdx"}]
    batch_id = "test_batch_with_path"
    output_dir = "test_output_path"

    # Track submit_job calls to verify correct payload structure
    submit_calls = []

    def capture_submit(command, payload):
        submit_calls.append({"command": command, "payload": payload})
        return f"job_{len(submit_calls)}"

    mock_engine.submit_job.side_effect = capture_submit

    # Mock get_job results
    res1 = JobResult(job_id="job_1", status="success", data={"val": 10})
    save1 = JobResult(job_id="job_2", status="success", data={})
    res2 = JobResult(job_id="job_3", status="success", data={"val": 20})
    save2 = JobResult(job_id="job_4", status="success", data={})

    mock_engine.get_job.side_effect = [res1, save1, res2, save2]

    bm.start_batch(batch_id, inputs, output_dir)

    # Wait for completion
    import time
    start = time.time()
    while bm.get_status(batch_id)["status"] == "running" and time.time() - start < 5:
        time.sleep(0.1)

    status = bm.get_status(batch_id)
    assert status["status"] == "completed"
    assert status["completed"] == 2

    # Verify submit_job was called with correct payload structure
    assert len(submit_calls) == 4  # 2 calculate_job + 2 save_as

    # First calculate_job call
    assert submit_calls[0]["command"] == "calculate_job"
    assert submit_calls[0]["payload"]["path"] == "C:\\test\\file.mcdx"
    assert submit_calls[0]["payload"]["inputs"] == {"a": 1}
    assert "path" not in submit_calls[0]["payload"]["inputs"]  # Path should not be in inputs dict

    # Second calculate_job call
    assert submit_calls[2]["command"] == "calculate_job"
    assert submit_calls[2]["payload"]["path"] == "C:\\test\\file.mcdx"
    assert submit_calls[2]["payload"]["inputs"] == {"a": 2}
    assert "path" not in submit_calls[2]["payload"]["inputs"]

    # Clean up
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

def test_batch_manager_without_path(mock_engine):
    """Test that BatchManager handles inputs without path gracefully"""
    bm = BatchManager(mock_engine)

    # Inputs without path field (backward compatibility)
    inputs = [{"a": 1}, {"a": 2}]
    batch_id = "test_batch_no_path"
    output_dir = "test_output_no_path"

    # Track submit_job calls
    submit_calls = []

    def capture_submit(command, payload):
        submit_calls.append({"command": command, "payload": payload})
        return f"job_{len(submit_calls)}"

    mock_engine.submit_job.side_effect = capture_submit

    # Mock get_job results
    res1 = JobResult(job_id="job_1", status="success", data={"val": 10})
    save1 = JobResult(job_id="job_2", status="success", data={})
    res2 = JobResult(job_id="job_3", status="success", data={"val": 20})
    save2 = JobResult(job_id="job_4", status="success", data={})

    mock_engine.get_job.side_effect = [res1, save1, res2, save2]

    bm.start_batch(batch_id, inputs, output_dir)

    # Wait for completion
    import time
    start = time.time()
    while bm.get_status(batch_id)["status"] == "running" and time.time() - start < 5:
        time.sleep(0.1)

    status = bm.get_status(batch_id)
    assert status["status"] == "completed"

    # Verify path is None when not provided
    assert submit_calls[0]["payload"]["path"] is None
    assert submit_calls[2]["payload"]["path"] is None

    # Clean up
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
