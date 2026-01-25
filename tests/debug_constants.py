from src.engine.worker import MathcadWorker
import os

def test_discovery():
    worker = MathcadWorker()
    try:
        worker.connect()
        print("Connected to MathcadPrime.Application")
        worker.discover_constants()
        print("\nDiscovered constants:")
        for name, value in sorted(worker.constants.items()):
            print(f"{name}: {value}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_discovery()
