from MathcadPy import Mathcad
from pathlib import Path
from typing import List, Dict, Any, Optional

class MathcadWorker:
    def __init__(self):
        self.mc = None  # Mathcad() instance
        self.worksheet = None  # Worksheet() instance
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
        return self.mc is not None

    def open_file(self, path: str):
        if not self.mc:
            raise Exception("Mathcad not connected")

        abs_path = Path(path).resolve()
        if not abs_path.exists():
            raise FileNotFoundError(f"File not found: {abs_path}")

        try:
            self.worksheet = self.mc.open(abs_path)
            self.worksheet.activate()
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
                # Default to "" if not specified, preserving worksheet units
                units_param = units if units is not None else ""
                error = self.worksheet.set_real_input(
                    alias, float(value), units=units_param, preserve_worksheet_units=True
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
        Saves the current worksheet in the specified format.
        MathcadPy handles format detection from file extension.
        format_enum parameter ignored (kept for backward compatibility).
        """
        if not self.worksheet:
            raise Exception("No worksheet open")

        abs_path = Path(path)

        # Check PDF export support (only works with Mathcad Prime 5+)
        if abs_path.suffix.lower() == ".pdf":
            if self.mc.version_major_int <= 4:
                raise ValueError(
                    f"PDF export requires Mathcad Prime 5+, current version: {self.mc.version}"
                )

        try:
            self.worksheet.save_as(abs_path)  # MathcadPy auto-detects format from extension
        except Exception as e:
            raise Exception(f"Failed to save to {abs_path}: {str(e)}")
