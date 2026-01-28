"""
Mathcad Automator - Desktop Application Entry Point

This script launches the application with:
- FastAPI backend server in a separate process
- pywebview native window for the UI
- Mathcad Prime detection on startup
- Operation-in-progress close confirmation
- Clean process termination on exit
- User data storage in AppData
- Window size/position persistence

Build: pyinstaller main.spec --clean
"""
import multiprocessing
import sys
import os
import time
import ctypes
import atexit
import json


# Application Info
APP_NAME = "MathcadAutomator"
APP_VERSION = "1.0.0"

# Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
WINDOW_TITLE = f"Mathcad Automator v{APP_VERSION}"
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800
SERVER_STARTUP_TIMEOUT = 30


# Global reference to server process for cleanup
_server_process = None


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to bundled resource.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_app_data_dir() -> str:
    """
    Get the application data directory for user-specific data.

    Returns %LOCALAPPDATA%\\MathcadAutomator in production,
    or ./data in development mode.

    Creates the directory if it doesn't exist.
    """
    if getattr(sys, 'frozen', False):
        # Running as executable - use AppData
        appdata = os.environ.get('LOCALAPPDATA')
        if not appdata:
            appdata = os.path.expanduser('~\\AppData\\Local')
        app_dir = os.path.join(appdata, APP_NAME)
    else:
        # Running in development - use local data folder
        app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def get_log_dir() -> str:
    """Get the log directory path."""
    log_dir = os.path.join(get_app_data_dir(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_library_dir() -> str:
    """Get the library configs directory path."""
    lib_dir = os.path.join(get_app_data_dir(), 'libraries')
    os.makedirs(lib_dir, exist_ok=True)
    return lib_dir


def load_window_config() -> dict:
    """
    Load saved window configuration (size, position).

    Returns default config if no saved config exists.
    """
    config_file = os.path.join(get_app_data_dir(), 'window_config.json')
    defaults = {
        'width': DEFAULT_WINDOW_WIDTH,
        'height': DEFAULT_WINDOW_HEIGHT,
        'x': None,  # None = center
        'y': None,
    }

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                # Merge saved values into defaults
                return {**defaults, **saved}
    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not load window config: {e}")

    return defaults


def save_window_config(window) -> None:
    """
    Save window configuration (size, position) for next session.
    """
    config_file = os.path.join(get_app_data_dir(), 'window_config.json')

    try:
        config = {
            'width': window.width,
            'height': window.height,
            'x': window.x,
            'y': window.y,
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except (OSError, AttributeError) as e:
        print(f"Warning: Could not save window config: {e}")


def detect_mathcad() -> tuple:
    """
    Detect Mathcad Prime installation via Windows registry.
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
                            return (True, version_key_name, None)
            except (OSError, WindowsError):
                continue

        return (False, None, None)
    except ImportError:
        return (False, None, None)


def show_mathcad_not_found_error():
    """Show a native Windows message box if Mathcad is not found."""
    error_msg = (
        "Mathcad Prime is not installed.\n\n"
        "This application requires Mathcad Prime to be installed on your computer.\n\n"
        "Please install Mathcad Prime and try again.\n\n"
        "Visit: https://www.ptc.com/en/products/mathcad"
    )
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
    Wait for the server to be ready.
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
    Main entry point.
    """
    global _server_process
    import webview

    print(f"Starting {WINDOW_TITLE}...")
    print(f"App data directory: {get_app_data_dir()}")

    # Check for Mathcad Prime installation
    installed, version, path = detect_mathcad()
    if not installed:
        print("ERROR: Mathcad Prime not detected")
        show_mathcad_not_found_error()
        sys.exit(1)

    print(f"Mathcad Prime {version or 'detected'} found{f' at {path}' if path else ''}")

    # Start backend server
    _server_process = multiprocessing.Process(
        target=run_server,
        daemon=False
    )
    _server_process.start()
    print(f"Server process started (PID: {_server_process.pid})")

    atexit.register(cleanup_server_process)

    # Wait for server
    server_url = f"http://{SERVER_HOST}:{SERVER_PORT}"
    print(f"Waiting for server at {server_url}...")

    if not wait_for_server(server_url):
        print("ERROR: Server failed to start within timeout")
        cleanup_server_process()
        sys.exit(1)

    print("Server is ready!")

    # Load saved window configuration
    window_config = load_window_config()

    def on_closing():
        """Handle window close request."""
        if check_operation_in_progress():
            try:
                result = window.evaluate_js(
                    'confirm("A calculation is in progress. Closing now will lose progress. Close anyway?")'
                )
                return result
            except Exception:
                return True
        return True

    def on_closed():
        """Handle window closed event."""
        print("Window closed, performing cleanup...")

        # Save window configuration
        save_window_config(window)

        # Terminate server
        if _server_process and _server_process.is_alive():
            print("Terminating server process...")
            _server_process.terminate()
            _server_process.join(timeout=5)
            if _server_process.is_alive():
                print("Force killing server process...")
                _server_process.kill()

        # Cleanup Mathcad processes
        cleanup_mathcad_processes()

        print("Cleanup complete.")

    # Create window with saved configuration
    window = webview.create_window(
        title=WINDOW_TITLE,
        url=server_url,
        width=window_config['width'],
        height=window_config['height'],
        x=window_config['x'],
        y=window_config['y'],
        resizable=True,
        min_size=(800, 600),
        confirm_close=False,
    )

    window.events.closing += on_closing
    window.events.closed += on_closed

    webview.start()

    cleanup_server_process()
    cleanup_mathcad_processes()

    print("Shutdown complete.")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
