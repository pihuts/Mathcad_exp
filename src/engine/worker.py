from MathcadPy import Mathcad
from pathlib import Path
from typing import List, Dict, Any, Optional

class MathcadWorker:
    def __init__(self):
        self.mc = None  # Mathcad() instance
        self.worksheet = None  # Worksheet() instance
        self.current_file_path = None  # Track currently open file to avoid unnecessary reopening
        # COM initialization is handled internally by MathcadPy

    def connect(self) -> bool:
        """
        Connects to the Mathcad Prime Application.
        MathcadPy handles COM initialization automatically.
        """
        try:
            self.mc = Mathcad(visible=True)
            print(f"Connected to Mathcad version: {self.mc.version}")
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to Mathcad: {str(e)}")

    def is_connected(self) -> bool:
        """Check if Mathcad connection is alive by testing COM accessibility."""
        if not self.mc:
            return False

        try:
            # Test COM connection by accessing a property that requires live connection
            # Accessing Worksheets.Count will throw COM error if connection is dead
            _ = self.mc.worksheet_names()
            return True
        except Exception:
            # COM connection is dead
            return False

    def open_file(self, path: str, force_reopen: bool = False):
        """
        Open a Mathcad file. If the same file is already open, skip reopening unless force_reopen=True.
        This optimization significantly improves batch processing performance.
        """
        # Check if connection is alive, reconnect if necessary
        if not self.is_connected():
            print("Mathcad connection lost, reconnecting...")
            self.connect()

        abs_path = Path(path).resolve()
        if not abs_path.exists():
            raise FileNotFoundError(f"File not found: {abs_path}")

        # Performance optimization: Skip reopening if same file is already open
        if not force_reopen and self.current_file_path == str(abs_path):
            return  # File already open, skip reopening

        try:
            self.worksheet = self.mc.open(abs_path)
            self.worksheet.activate()
            self.current_file_path = str(abs_path)  # Track opened file
        except Exception as e:
            raise Exception(f"Failed to open file {abs_path}: {str(e)}")

    def get_inputs(self) -> List[Dict[str, Any]]:
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            input_names = self.worksheet.inputs()
            return [{"alias": name, "name": name, "units": ""} for name in input_names]
        except Exception as e:
            raise Exception(f"Failed to retrieve inputs: {str(e)}")

    def get_outputs(self) -> List[Dict[str, Any]]:
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            output_names = self.worksheet.outputs()
            return [{"alias": name, "name": name, "units": ""} for name in output_names]
        except Exception as e:
            raise Exception(f"Failed to retrieve outputs: {str(e)}")

    def set_input(self, alias: str, value: Any, units: Optional[str] = None):
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            if isinstance(value, str):
                error = self.worksheet.set_string_input(alias, value)
                if error != 0:
                    raise Exception(f"set_string_input returned error code {error}")
            else:
                # Pass units to MathcadPy's set_real_input
                # Treat None, empty string, or "unitless" as no units
                is_unitless = units is None or units == "" or units.lower() == "unitless"
                units_param = "" if is_unitless else units
                
                # Use preserve_worksheet_units=True ONLY if we are truly unitless
                # If we passed units="", MathcadPy might try to set units to "" which is valid
                preserve_units = is_unitless
                
                error = self.worksheet.set_real_input(
                    alias, float(value), units=units_param, preserve_worksheet_units=preserve_units
                )
                if error != 0:
                    raise Exception(f"set_real_input returned error code {error}")
        except Exception as e:
            raise Exception(f"Failed to set input {alias}: {str(e)}")

    def synchronize(self):
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            self.worksheet.calculate()  # Alias for synchronize()
        except Exception as e:
            raise Exception(f"Failed to synchronize worksheet: {str(e)}")

    def get_output_value(self, alias: str) -> Any:
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            value, units, error_code = self.worksheet.get_real_output(alias)
            if error_code != 0:
                raise Exception(f"Error getting output {alias}: ErrorCode {error_code}")
            return value  # Unwrap tuple, return only value
        except Exception as e:
            raise Exception(f"Failed to get output {alias}: {str(e)}")

    def save_as(self, path: str, format_enum: Optional[int] = None):
        """
        Saves the current worksheet.
        Auto-detects format from extension.
        Explicitly handles PDF export only for Mathcad > 4.
        """
        if not self.worksheet:
            raise Exception("No worksheet open")

        abs_path = Path(path).resolve()
        
        # Determine if we are saving as PDF
        is_pdf = abs_path.suffix.lower() == ".pdf"
        
        if is_pdf:
             if self.mc.version_major_int <= 4:
                 raise ValueError("PDF export requires Mathcad Prime 5+")
        
        try:
            # Bypass MathcadPy's save_as method because it passes a Path object 
            # to the COM method, which can fail in strict environments.
            # INSTEAD: Access the raw COM object (ws_object) and pass a string explicitly.
            if hasattr(self.worksheet, 'ws_object'):
                self.worksheet.ws_object.SaveAs(str(abs_path))
            else:
                 # Fallback if internal structure changes, though risky
                 self.worksheet.save_as(str(abs_path))
        except Exception as e:
             raise Exception(f"Failed to save to {abs_path}: {str(e)}")
