import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.protocol import JobRequest, JobResult, EngineStatus

def test_protocol():
    # Test Request
    req = JobRequest(command="ping", payload={"foo": "bar"})
    print(f"Request created: {req}")
    assert req.command == "ping"
    assert req.id is not None

    # Test Result
    res = JobResult(job_id=req.id, status="success", data={"response": "pong"})
    print(f"Result created: {res}")
    assert res.job_id == req.id
    assert res.is_success
    
    # Test Enum
    status = EngineStatus.IDLE
    print(f"Status: {status}")
    assert status == "IDLE"

if __name__ == "__main__":
    test_protocol()
