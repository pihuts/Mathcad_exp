import pythoncom
import win32com.client
import os
from typing import List, Dict, Any, Optional

class MathcadWorker:
    def __init__(self):
        self.mc = None
        self.worksheet = None
        # Initialize COM library for this thread - CRITICAL for multiprocess
        pythoncom.CoInitialize()

    def connect(self) -> bool:
        """
        Connects to the Mathcad Prime Application.
        Returns True if successful, raises exception otherwise.
        """
        try:
            # mathcadpy research suggests "Mathcad.Application" is the ProgID
            self.mc = win32com.client.Dispatch("Mathcad.Application")
            if not self.mc:
                raise Exception("Dispatch returned None for Mathcad.Application")
            
            # Optional: Ensure it's visible or active if needed, but for background we might prefer hidden?
            # Usually better to see it during dev.
            self.mc.Visible = True 
            return True
        except Exception as e:
            # We want to propagate the error so the harness can report it
            raise Exception(f"Failed to connect to Mathcad: {str(e)}")

    def is_connected(self) -> bool:
        return self.mc is not None

    def open_file(self, path: str):
        if not self.mc:
            raise Exception("Mathcad not connected")
        
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
             raise FileNotFoundError(f"File not found: {abs_path}")
             
        try:
            self.worksheet = self.mc.Open(abs_path)
        except Exception as e:
            raise Exception(f"Failed to open file {abs_path}: {str(e)}")

    def get_inputs(self) -> List[Dict[str, Any]]:
        if not self.worksheet:
            raise Exception("No worksheet open")
        
        inputs = []
        try:
            # Mathcad Prime API: Worksheet.Inputs is a collection
            for item in self.worksheet.Inputs:
                inputs.append({
                    "alias": item.Alias,
                    "name": item.Name,
                    "units": item.Units
                })
        except Exception as e:
            raise Exception(f"Failed to retrieve inputs: {str(e)}")
        return inputs

    def get_outputs(self) -> List[Dict[str, Any]]:
        if not self.worksheet:
            raise Exception("No worksheet open")
        
        outputs = []
        try:
            for item in self.worksheet.Outputs:
                 outputs.append({
                    "alias": item.Alias,
                    "name": item.Name,
                    "units": item.Units
                })
        except Exception as e:
             raise Exception(f"Failed to retrieve outputs: {str(e)}")
        return outputs

    def set_input(self, alias: str, value: Any):
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            if isinstance(value, str):
                self.worksheet.SetStringValue(alias, value)
            else:
                # Default to Real with empty units
                self.worksheet.SetRealValue(alias, float(value), "")
        except Exception as e:
             raise Exception(f"Failed to set input {alias}: {str(e)}")

    def get_output_value(self, alias: str) -> Any:
        if not self.worksheet:
            raise Exception("No worksheet open")
        try:
            # Try Real first
            return self.worksheet.OutputGetRealValue(alias, "")
        except:
            # Try String
            try:
                return self.worksheet.OutputGetStringValue(alias)
            except Exception as e:
                raise Exception(f"Failed to get output {alias}: {str(e)}")
