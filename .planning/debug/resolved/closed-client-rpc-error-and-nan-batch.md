---
status: resolved
trigger: "closed-client-rpc-error-and-nan-batch"
created: 2026-01-26T00:00:00.000Z
updated: 2026-01-26T00:00:00.000Z
---

## Current Focus

hypothesis:
- Issue 1: is_connected() only checks if self.mc is not None, but doesn't verify COM connection is alive
- Issue 2: Type mismatch - InputModal sends {alias, value, units} object but handleSaveAliasConfig expects array
test: Verify the code paths that cause these issues
expecting: Confirm both root causes
next_action: Update debug file with findings and formulate fixes

## Symptoms

expected:
- Issue 1: Program should detect closed Mathcad client and create new one before opening next file
- Issue 2: Batch testing should show total combinations when entering start, step, end values
actual:
- Issue 1: Gets "RPC server is unavailable" COM error when trying to open file after client closed
- Issue 2: Shows "NaN" for total iterations, clicking "Run batch" does nothing
errors:
```
Traceback (most recent call last):
  File "D:\Mathcad_exp\src\engine\worker.py", line 35, in open_file
    self.worksheet = self.mc.open(abs_path)
  File "D:\Mathcad_exp\.venv\Lib\site-packages\MathcadPy\_application.py", line 97, in open
    local_obj = self.__mcadapp.Open(str(filepath))
  File "<COMObject MathcadPrime.Application>", line 2, in Open
pywintypes.com_error: (-2147023174, 'The RPC server is unavailable.', None, None)
During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "D:\Mathcad_exp\src\engine\harness.py", line 95, in run_harness
    worker.open_file(path)
  File "D:\Mathcad_exp\src\engine\worker.py", line 38, in open_file
    raise Exception(f"Failed to open file {abs_path}: {str(e)}")
Exception: Failed to open file C:\Users\peter\OneDrive\Desktop\Mathcad\Shear Tab.mcdx: (-2147023174, 'The RPC server is unavailable.', None, None)
```
reproduction:
- Issue 1: Open a Mathcad file successfully, close the Mathcad client, then try to open another file
- Issue 2: In batch testing UI, enter start, step, end and units values, observe "NaN" in total iteration, click "Run batch" and note nothing happens
timeline: User just identified these issues after first-time use works but subsequent uses fail

## Eliminated

## Evidence

- timestamp: 2026-01-26T00:00:00.000Z
  checked: src/engine/worker.py lines 23-24 and 26-38
  found:
    - is_connected() only checks "return self.mc is not None"
    - open_file() checks "if not self.mc" but doesn't verify COM connection is alive
    - When Mathcad is closed externally, self.mc still exists but COM server is unavailable
  implication: Need to verify COM connection is alive before using it

- timestamp: 2026-01-26T00:00:00.000Z
  checked: frontend/src/App.tsx lines 48 and 52-56
  found:
    - handleSaveAliasConfig expects (alias: string, values: any[]) where values is an array
    - iterationCount uses aliasConfigs[key].length to calculate total
  implication: aliasConfigs must contain arrays of values, not objects

- timestamp: 2026-01-26T00:00:00.000Z
  checked: frontend/src/components/InputModal.tsx lines 59-73
  found:
    - handleSave calls onSave with {alias, value, units} (InputConfig object)
    - value is the actual array of values from generateRange()
  implication: Type mismatch - sending object when function expects array

- timestamp: 2026-01-26T00:00:00.000Z
  checked: frontend/src/App.tsx line 48
  found: handleSaveAliasConfig signature: (alias: string, values: any[]) => void
  checked: frontend/src/components/InputModal.tsx line 30
  found: InputModal's onSave signature expects InputConfig: (config: InputConfig) => void
  checked: frontend/src/App.tsx line 189
  found: InputModal used as: onSave={(values) => handleSaveAliasConfig(selectedAlias!, values)}
  implication: Type mismatch causes aliasConfigs to store InputConfig objects instead of value arrays


## Resolution

root_cause:
- Issue 1: worker.is_connected() only checks "self.mc is not None" without verifying COM connection is alive. When Mathcad is closed externally, self.mc still exists but COM server is unavailable, causing "RPC server is unavailable" error.
- Issue 2: Type mismatch in App.tsx. InputModal.onSave sends InputConfig object {alias, value, units}, but handleSaveAliasConfig expects raw array values. This causes aliasConfigs to store objects instead of arrays, so aliasConfigs[key].length is undefined, resulting in NaN.

fix:
- Issue 1: Updated worker.is_connected() to test COM connection by calling worksheet_names() which will throw COM error if connection is dead. Also updated open_file() to auto-reconnect if connection is lost.
- Issue 2:
  - Added aliasUnits state to preserve units information
  - Updated handleSaveAliasConfig to handle InputConfig object and extract both values and units
  - Updated handleRun to apply units to inputs when creating batch request

verification:
- Test Issue 1: Open file, close Mathcad, open another file - should auto-reconnect
- Test Issue 2: Configure batch parameters - should show correct iteration count, Run button should work, units should be preserved

- timestamp: 2026-01-26T00:00:00.000Z
  checked: Frontend build
  found: Build completed successfully with no TypeScript errors
  implication: Code is syntactically correct and type-safe

- timestamp: 2026-01-26T00:00:00.000Z
  checked: worker.py is_connected() and open_file() methods
  found: is_connected() now tests COM connection, open_file() auto-reconnects
  implication: Issue 1 fix implemented correctly

- timestamp: 2026-01-26T00:00:00.000Z
  checked: App.tsx aliasConfigs, aliasUnits, handleSaveAliasConfig, handleRun
  found:
    - aliasUnits state added to preserve units
    - handleSaveAliasConfig extracts both values and units from InputConfig
    - handleRun applies units to inputs when creating batch request
    - iterationCount uses aliasConfigs[key].length (now works correctly)
  implication: Issue 2 fix implemented correctly, units preserved

files_changed:
- src/engine/worker.py: Updated is_connected() and open_file() methods
- frontend/src/App.tsx: Added aliasUnits state, updated handleSaveAliasConfig and handleRun functions

