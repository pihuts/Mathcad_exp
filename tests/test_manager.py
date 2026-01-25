import unittest
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.manager import EngineManager

class TestEngineManager(unittest.TestCase):
    def setUp(self):
        self.manager = EngineManager()

    def tearDown(self):
        if self.manager.is_running():
            self.manager.stop_engine()

    def test_lifecycle_and_ping(self):
        print("\nTesting Engine Lifecycle and Ping...")
        
        # 1. Start Engine
        self.manager.start_engine()
        self.assertTrue(self.manager.is_running(), "Engine should be running")
        
        # 2. Submit Job
        job_id = self.manager.submit_job("ping")
        print(f"Submitted job {job_id}")
        
        # 3. Get Result
        result = self.manager.get_result(timeout=5.0)
        self.assertIsNotNone(result, "Should receive a result")
        print(f"Received result: {result}")
        
        self.assertEqual(result.job_id, job_id)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["response"], "pong")
        
        # 4. Stop Engine
        self.manager.stop_engine()
        self.assertFalse(self.manager.is_running(), "Engine should be stopped")
        print("Engine stopped successfully.")

    def test_restart(self):
        print("\nTesting Restart...")
        self.manager.start_engine()
        pid1 = self.manager.process.pid
        
        self.manager.restart_engine()
        self.assertTrue(self.manager.is_running())
        pid2 = self.manager.process.pid
        
        self.assertNotEqual(pid1, pid2, "PID should change after restart")
        print(f"Restart successful. PID {pid1} -> {pid2}")

if __name__ == '__main__':
    # Windows multiprocessing support
    import multiprocessing
    multiprocessing.freeze_support()
    
    unittest.main()
