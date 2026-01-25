from src.engine.manager import EngineManager

# Singleton instance
_manager = None

def get_engine_manager() -> EngineManager:
    global _manager
    if _manager is None:
        _manager = EngineManager()
    return _manager
