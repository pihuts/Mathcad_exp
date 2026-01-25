from contextlib import asynccontextmanager
from fastapi import FastAPI
from .dependencies import get_engine_manager
from .routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    manager = get_engine_manager()
    manager.start_engine()
    yield
    # Shutdown
    manager.stop_engine()

app = FastAPI(title="Mathcad Automator API", lifespan=lifespan)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "online", "service": "Mathcad Automator Engine"}
