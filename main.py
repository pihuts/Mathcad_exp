"""
Mathcad Automator - Entry Point for PyInstaller

This script serves as the entry point for the packaged executable.
It starts the FastAPI backend server and can be extended in later phases
to launch the pywebview window.
"""
import multiprocessing
import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.

    When running as a PyInstaller bundle, sys._MEIPASS points to the
    temporary folder where the bundle is extracted.
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def run_server():
    """Run the FastAPI server using uvicorn."""
    import uvicorn

    # Import app after ensuring paths are set up
    from src.server.main import app

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        workers=1,      # Must be 1 in frozen executable
        reload=False,   # Must be False in frozen executable
        log_level="info"
    )


def main():
    """Main entry point."""
    print("Starting Mathcad Automator...")

    # For now, just run the server directly
    # Phase 05-02 will add pywebview window
    run_server()


if __name__ == '__main__':
    # Required for Windows multiprocessing in frozen executables
    multiprocessing.freeze_support()
    main()
