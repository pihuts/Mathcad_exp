"""
Mathcad Automator - Desktop Application Entry Point

This script launches the application with:
- FastAPI backend server in a separate process
- pywebview native window for the UI

Build: pyinstaller main.spec --clean
"""
import multiprocessing
import sys
import os
import time


# Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
WINDOW_TITLE = "Mathcad Automator"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
SERVER_STARTUP_TIMEOUT = 30  # seconds


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.

    When running as a PyInstaller bundle, sys._MEIPASS points to the
    temporary folder where the bundle is extracted.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def run_server():
    """
    Run the FastAPI server in a separate process.

    This function is the target for multiprocessing.Process.
    It must be defined at module level for Windows multiprocessing to work.
    """
    import uvicorn

    # Set up path for src module import
    if getattr(sys, 'frozen', False):
        # In PyInstaller bundle, src is in _MEIPASS
        sys.path.insert(0, sys._MEIPASS)
    else:
        # In development, add project root
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

    from src.server.main import app

    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        workers=1,
        reload=False,
        log_level="info"
    )


def wait_for_server(url: str, timeout: float = SERVER_STARTUP_TIMEOUT) -> bool:
    """
    Wait for the server to be ready by polling the health endpoint.

    Returns True if server is ready, False if timeout reached.
    """
    import urllib.request
    import urllib.error

    health_url = f"{url}/health"
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(health_url, method='GET')
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.3)

    return False


def main():
    """
    Main entry point - launches server and pywebview window.
    """
    import webview

    print(f"Starting {WINDOW_TITLE}...")

    # Start backend server in separate process
    server_process = multiprocessing.Process(
        target=run_server,
        daemon=False  # We want explicit cleanup
    )
    server_process.start()
    print(f"Server process started (PID: {server_process.pid})")

    # Wait for server to be ready
    server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    print(f"Waiting for server at {server_url}...")

    if not wait_for_server(server_url):
        print("ERROR: Server failed to start within timeout")
        server_process.terminate()
        server_process.join(timeout=2)
        sys.exit(1)

    print("Server is ready!")

    # Create pywebview window
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=server_url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(800, 600),
        confirm_close=False,  # Will be handled in 05-03
    )

    # Start the GUI event loop (blocks until window closes)
    webview.start()

    # Cleanup: terminate server when window closes
    print("Window closed, shutting down server...")
    if server_process.is_alive():
        server_process.terminate()
        server_process.join(timeout=5)
        if server_process.is_alive():
            print("Server did not terminate gracefully, forcing kill...")
            server_process.kill()

    print("Shutdown complete.")


if __name__ == '__main__':
    # Required for Windows multiprocessing in frozen executables
    multiprocessing.freeze_support()
    main()
