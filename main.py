"""
Mathcad Automator - Desktop Application Entry Point

This script launches the application with:
- FastAPI backend server in a separate process
- pywebview native window for the UI
- Mathcad Prime detection on startup
- Operation-in-progress close confirmation
- Clean process termination on exit

Build: pyinstaller main.spec --clean
"""
import multiprocessing
import sys
import os
import time
import ctypes
import atexit


# Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
WINDOW_TITLE = "Mathcad Automator"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
SERVER_STARTUP_TIMEOUT = 30  # seconds


# Global reference to server process for cleanup
_server_process = None


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def detect_mathcad() -> tuple:
    """
    Detect Mathcad Prime installation via Windows registry.

    Returns: (installed: bool, version: str or None, path: str or None)
    """
    try:
        import winreg

        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\PTC\Mathcad Prime"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\PTC\Mathcad Prime"),
        ]

        for hkey, subkey_path in registry_paths:
            try:
                with winreg.OpenKey(hkey, subkey_path) as key:
                    num_subkeys = winreg.QueryInfoKey(key)[0]
                    if num_subkeys > 0:
                        version_key_name = winreg.EnumKey(key, 0)
                        try:
                            with winreg.OpenKey(key, version_key_name) as version_key:
                                install_path = winreg.QueryValueEx(version_key, "InstallPath")[0]
                                return (True, version_key_name, install_path)
                        except (OSError, WindowsError):
                            # Version key exists but no InstallPath - still consider installed
                            return (True, version_key_name, None)
            except (OSError, WindowsError):
                continue

        return (False, None, None)
    except ImportError:
        # winreg not available (non-Windows)
        return (False, None, None)


def show_mathcad_not_found_error():
    """Show a native Windows message box if Mathcad is not found."""
    error_msg = (
        "Mathcad Prime is not installed.\n\n"
        "This application requires Mathcad Prime to be installed on your computer.\n\n"
        "Please install Mathcad Prime and try again.\n\n"
        "Visit: https://www.ptc.com/en/products/mathcad"
    )

    # MB_OK | MB_ICONERROR = 0x10
    ctypes.windll.user32.MessageBoxW(0, error_msg, "Mathcad Prime Not Found", 0x10)


def run_server():
    """
    Run the FastAPI server in a separate process.
    """
    import uvicorn

    if getattr(sys, 'frozen', False):
        sys.path.insert(0, sys._MEIPASS)
    else:
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


def check_operation_in_progress() -> bool:
    """
    Check if any batch or workflow operation is currently running.

    Returns True if an operation is in progress, False otherwise.
    """
    import urllib.request
    import urllib.error
    import json

    status_url = f"http://{SERVER_HOST}:{SERVER_PORT}/api/v1/status"

    try:
        req = urllib.request.Request(status_url, method='GET')
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("operation_in_progress", False)
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return False


def cleanup_mathcad_processes():
    """
    Kill any orphaned Mathcad Prime processes.
    Uses psutil to find and terminate Mathcad processes.
    """
    try:
        import psutil

        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info.get('name', '').lower()
                if 'mathcad' in proc_name:
                    print(f"Terminating orphaned Mathcad process: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
    except ImportError:
        print("Warning: psutil not available, cannot cleanup Mathcad processes")


def cleanup_server_process():
    """Cleanup function to terminate server process."""
    global _server_process

    if _server_process and _server_process.is_alive():
        print("Cleaning up server process...")
        _server_process.terminate()
        _server_process.join(timeout=5)
        if _server_process.is_alive():
            _server_process.kill()


def main():
    """
    Main entry point - launches server and pywebview window.
    """
    global _server_process
    import webview

    print(f"Starting {WINDOW_TITLE}...")

    # Check for Mathcad Prime installation
    installed, version, path = detect_mathcad()
    if not installed:
        print("ERROR: Mathcad Prime not detected")
        show_mathcad_not_found_error()
        sys.exit(1)

    print(f"Mathcad Prime {version or 'detected'} found{f' at {path}' if path else ''}")

    # Start backend server in separate process
    _server_process = multiprocessing.Process(
        target=run_server,
        daemon=False
    )
    _server_process.start()
    print(f"Server process started (PID: {_server_process.pid})")

    # Register cleanup for unexpected exits
    atexit.register(cleanup_server_process)

    # Wait for server to be ready
    server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    print(f"Waiting for server at {server_url}...")

    if not wait_for_server(server_url):
        print("ERROR: Server failed to start within timeout")
        cleanup_server_process()
        sys.exit(1)

    print("Server is ready!")

    def on_closing():
        """
        Called when user attempts to close the window.
        Return False to cancel close, True to allow.
        """
        if check_operation_in_progress():
            # Use JavaScript confirm dialog in the webview
            try:
                result = window.evaluate_js(
                    'confirm("A calculation is in progress. Closing now will lose progress. Close anyway?")'
                )
                return result
            except Exception:
                # If JS fails, allow close
                return True
        return True

    def on_closed():
        """
        Called when window is about to be destroyed.
        Perform cleanup of all processes.
        """
        print("Window closed, performing cleanup...")

        # Terminate server process
        if _server_process and _server_process.is_alive():
            print("Terminating server process...")
            _server_process.terminate()
            _server_process.join(timeout=5)
            if _server_process.is_alive():
                print("Force killing server process...")
                _server_process.kill()

        # Cleanup any orphaned Mathcad processes
        cleanup_mathcad_processes()

        print("Cleanup complete.")

    # Create pywebview window
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=server_url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        resizable=True,
        min_size=(800, 600),
        confirm_close=False,  # We handle confirmation in on_closing
    )

    # Register event handlers
    window.events.closing += on_closing
    window.events.closed += on_closed

    # Start the GUI event loop (blocks until window closes)
    webview.start()

    # Ensure cleanup runs (belt and suspenders)
    cleanup_server_process()
    cleanup_mathcad_processes()

    print("Shutdown complete.")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
