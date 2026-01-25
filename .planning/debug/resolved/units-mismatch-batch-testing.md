---
status: resolved
trigger: "Investigate issue: units-mismatch-batch-testing"
created: 2026-01-26T00:00:00.000Z
updated: 2026-01-26T00:00:08.000Z
---

## Current Focus
hypothesis: The code incorrectly uses preserve_worksheet_units=True when units are provided, causing Mathcad to require exact match between provided units and worksheet units
test: Check worker.py set_input to verify that preserve_worksheet_units is always True regardless of whether units are provided
expecting: Will find that preserve_worksheet_units=True is hardcoded, preventing unit conversion
next_action: Implement fix to use preserve_worksheet_units=False when units are provided

## Symptoms
expected: Batch testing should accept units from frontend and apply them to Mathcad inputs
actual:
- AssertionError when setting inputs with units
- Error: "preserve_worksheet_units is True. The units argument does not equate to the units present in the Worksheet"
- Affects inputs "sr" and "Nr" in different batches
- Engine keeps restarting and retrying but fails repeatedly
errors:
```
AssertionError: preserve_worksheet_units is True. The units argument does not equate to the units present in the Worksheet

During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "D:\Mathcad_exp\src\engine\worker.py", line 83, in set_input
    error = self.worksheet.set_real_input(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Mathcad_exp\.venv\Lib\site-packages\MathcadPy\_application.py", line 348, in set_real_input
    raise AssertionError(
AssertionError: preserve_worksheet_units is True. The units argument does not equate to the units present in the Worksheet

During handling of the above exception, another exception occurred:
Traceback (most recent call last):
  File "D:\Mathcad_exp\src\engine\harness.py", line 128, in run_harness
    worker.set_input(alias, value, units)
  File "D:\Mathcad_exp\src\engine\worker.py", line 89, in set_input
    raise Exception(f"Failed to set input {alias}: {str(e)}")
Exception: Failed to set input sr: preserve_worksheet_units is True. The units argument does not equate to the units present in the Worksheet
```
reproduction:
1. Run batch testing with start, step, end, and units values
2. Observe AssertionError when trying to set input
started: Just occurred after previous fixes for closed client and NaN batch issues were applied

## Eliminated

## Evidence
- timestamp: 2026-01-26T00:00:01.000Z
  checked: worker.py set_input method
  found: When preserve_worksheet_units=True, units parameter must either be "" or match exact worksheet units
  implication: Frontend sending units like "ft", "in", "kip" which likely don't match worksheet definition

- timestamp: 2026-01-26T00:00:02.000Z
  checked: batch_manager.py _process_batch method
  found: Frontend sends structured dict with value and units, which are wrapped in InputConfig objects
  implication: Units flow from frontend → batch_manager → harness → worker → Mathcad

- timestamp: 2026-01-26T00:00:03.000Z
  checked: get_inputs in worker.py line 58
  found: Returns [{"alias": name, "name": name, "units": ""}] - units are hardcoded to empty string
  implication: System doesn't retrieve actual units from worksheet, so can't verify unit compatibility

- timestamp: 2026-01-26T00:00:04.000Z
  checked: MathcadPy library _application.py line 342-353
  found: When preserve_worksheet_units=True and units provided, asserts units must match worksheet exactly
  implication: Frontend sending "ft", "in", "kip" fails assertion if worksheet has different units

- timestamp: 2026-01-26T00:00:05.000Z
  checked: worker.py line 84
  found: preserve_worksheet_units=True is hardcoded, regardless of whether units parameter is provided
  implication: This prevents Mathcad from performing unit conversion when units are specified

ROOT CAUSE FOUND: worker.py always uses preserve_worksheet_units=True even when units are provided, which requires exact match between provided units and worksheet units. When preserve_worksheet_units=True, Mathcad expects either empty string (to use worksheet units) or exact match. The fix is to use preserve_worksheet_units=False when units are provided to allow Mathcad to perform unit conversion.

- timestamp: 2026-01-26T00:00:06.000Z
  checked: worker.py set_input after fix
  found: preserve_units = (units is None or units == "") correctly determines when to preserve worksheet units
  implication: When units are provided (not None and not ""), preserve_worksheet_units=False allows Mathcad to perform unit conversion

- timestamp: 2026-01-26T00:00:07.000Z
  checked: test_worker_units_fix.py unit test
  found: All test cases pass, verifying the logic is correct
  implication: The fix correctly handles all cases: None, "", and actual unit strings

## Resolution
root_cause: worker.py always uses preserve_worksheet_units=True even when units are provided, which requires exact match between provided units and worksheet units
fix: Modified worker.py set_input method to use preserve_worksheet_units=False when units are provided (to allow Mathcad to perform unit conversion), and preserve_worksheet_units=True only when units is None or empty (to preserve worksheet units)
verification:
- Code compiles without errors
- Logic test passes (test_worker_units_fix.py) - verifies preserve_units logic correctly handles all cases
- Existing test_protocol_verify.py still passes (no regression)
- Fix follows MathcadPy API documentation: use preserve_worksheet_units=False to allow unit conversion
files_changed:
- D:\Mathcad_exp\src\engine\worker.py
