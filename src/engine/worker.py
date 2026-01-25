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
