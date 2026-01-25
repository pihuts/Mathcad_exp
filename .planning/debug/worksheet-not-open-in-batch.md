---
status: verifying
trigger: "Investigate issue: worksheet-not-open-in-batch - Batch processing fails with 'No worksheet open' error when trying to set input values"
created: 2026-01-25T00:00:00.000Z
updated: 2026-01-25T00:00:00.000Z
---

## Current Focus
hypothesis: Fix verified through unit tests - path extraction works correctly
test: All tests pass
expecting: Ready to archive session
next_action: Update debug file and archive

## Symptoms
expected: Mathcad opens the worksheet and calculates with batch inputs
actual: Fails immediately with "No worksheet open" error when trying to set inputs
errors: "Exception: No worksheet open" at worker.py:102 in set_input()
reproduction: Click Run Batch after configuring batch inputs
timeline: Just started testing batch processing after previous fixes

## Eliminated

## Evidence
- timestamp: 2026-01-25T00:00:00.000Z
  checked: worker.py:100-102
  found: set_input() raises "No worksheet open" if self.worksheet is None
  implication: worksheet must be opened before set_input() is called

- timestamp: 2026-01-25T00:00:00.000Z
  checked: harness.py:109-118 (calculate_job command)
  found: worksheet is opened only if path exists in payload: `if path: worker.open_file(path)`
  implication: if path is missing from payload, worksheet is never opened

- timestamp: 2026-01-25T00:00:00.000Z
  checked: batch_manager.py:47
  found: submit_job sends only `{"inputs": row_input}`, path not included
  implication: calculate_job receives no path, worksheet never opens

- timestamp: 2026-01-25T00:00:00.000Z
  checked: frontend/src/App.tsx:64-67
  found: Frontend DOES include path in each input: `const inputs = combinations.map(combo => ({...combo, path: filePath}));`
  implication: The path is available in each row but not being used by BatchManager

- timestamp: 2026-01-25T00:00:00.000Z
  checked: tests/test_batch_path_extraction.py
  found: Both tests pass - path extraction works correctly
  implication: Fix is verified - path is extracted from row_input and passed to calculate_job

- timestamp: 2026-01-25T00:00:00.000Z
  checked: tests/test_batch_manager.py
  found: Original test still passes
  implication: Backward compatibility maintained - works with and without path

## Resolution
root_cause: BatchManager receives path field in each input row from frontend, but doesn't extract it and pass to calculate_job. calculate_job expects {"path": Optional[str], "inputs": Dict} but only receives {"inputs": row_input} without path, so worksheet.open_file(path) is never called, causing set_input() to fail with "No worksheet open"
fix: Modified batch_manager.py:44-50 to extract path from each row_input and pass it to calculate_job payload:
  ```python
  path = row_input.get("path")
  inputs_dict = {k: v for k, v in row_input.items() if k != "path"}
  job_id = self.engine.submit_job("calculate_job", {"path": path, "inputs": inputs_dict})
  ```
verification: Created comprehensive tests in test_batch_path_extraction.py that verify:
  1. Path is correctly extracted when present in input row
  2. Path is set to None when not present (backward compatibility)
  3. All tests pass including original test_batch_manager.py
files_changed: ["src/engine/batch_manager.py", "tests/test_batch_path_extraction.py"]
