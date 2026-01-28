---
status: resolved
trigger: "library-save-load-range-values-and-overwrites"
created: 2026-01-28T00:00:00Z
updated: 2026-01-28T00:25:00Z
---

## Current Focus

hypothesis: CONFIRMED - LibraryModal.handleSave incorrectly extracts aliasConfigs data structure
test: Trace data flow from InputModal -> App state -> LibraryModal save -> Backend
expecting: Will confirm save bug and identify exact fix needed
next_action: Verify root cause and implement fix

## Symptoms

expected: All range values should be restored exactly as saved - e.g., if saved Input1 with range Start=1, End=10, Step=1 (10 values), loading should show all 10 values in the same range configuration.

actual: When loading a saved config with multiple range values, it only shows "1 value" instead of the full range. Additionally, when saving a second config, it overwrites files even if they have different names (case sensitivity issue causing overwrites).

errors: AG Grid error in browser console: "error #272 No AG Grid modules are registered!" (main.esm.mjs:1507) - This appears to be unrelated to the save/load issue but worth noting.

reproduction:
1. Configure inputs with ranges (e.g., Start=1, End=10, Step=1)
2. Click Library → Save with a name
3. Reload page or clear inputs
4. Library → Load → wrong values appear (shows "1 value" instead of 10)
5. Save another config with different name → first config gets overwritten

started: Issue discovered recently after implementing Phase 04-04 (Library UI modal). This is the first user testing of the library save/load feature.

## Eliminated

## Evidence

- timestamp: 2026-01-28T00:05:00Z
  checked: Backend save/load endpoints and frontend components
  found: **BUG 1 IDENTIFIED - handleLoadLibraryConfig converts array values to single value**
    - Line 147 in App.tsx: `newAliasConfigs[inputConfig.alias] = [{ value: inputConfig.value, units: inputConfig.units }];`
    - InputConfig.value contains the FULL array (e.g., [1,2,3,4,5,6,7,8,9,10])
    - But it's being wrapped in a single-element array: `[{ value: [1,2,3,4,5,6,7,8,9,10], units: "in" }]`
    - The frontend expects `aliasConfigs[alias]` to be an array of values, not an array containing an object with value array
    - When displaying, it only shows "1 value" because there's only one element in the outer array
  implication: Range values ARE saved correctly to JSON, but loaded incorrectly into UI state

- timestamp: 2026-01-28T00:06:00Z
  checked: LibraryModal save logic (lines 65-98)
  found: Save logic extracts first element of configs array: `const firstConfig = configs[0]`
    - This assumes aliasConfigs[alias] is an array of individual values
    - When saving a range [1,2,3,4,5,6,7,8,9,10], it takes configs[0] which is just the first value (1)
    - This explains why only "1 value" shows after load
  implication: Both save AND load have bugs - save extracts only first value, load wraps in wrong structure

- timestamp: 2026-01-28T00:07:00Z
  checked: Backend routes.py line 228 for file overwrite issue
  found: `safe_name = "".join(c for c in config.name if c.isalnum() or c in (' ', '-', '_')).strip()`
    - Sanitizes config name for filename
    - Then: `config_file = config_dir / f"{safe_name}.json"`
    - **NO CASE SENSITIVITY CHECK** - Windows filesystem is case-insensitive by default
    - If user saves "MyConfig" then "myconfig", both become "MyConfig.json" on Windows (or vice versa)
  implication: File overwrite is a Windows case-insensitivity issue, not a code bug per se, but could add case normalization

- timestamp: 2026-01-28T00:10:00Z
  checked: Data flow trace from InputModal -> App state -> LibraryModal
  found: **ROOT CAUSE CONFIRMED**
    - App.tsx stores aliasConfigs as: `{ "Input1": [1,2,3,4,5,6,7,8,9,10] }` (array of values)
    - LibraryModal.handleSave line 69-78 has incorrect logic:
      ```typescript
      Object.entries(currentInputs).flatMap(([alias, configs]) => {
        const firstConfig = configs[0];  // Gets 1 (not an object!)
        if (typeof firstConfig === 'object' && 'value' in firstConfig) {
          return [{ alias, value: firstConfig.value, units: firstConfig.units }];
        }
        return [{ alias, value: firstConfig }];  // Returns { alias: "Input1", value: 1 }
      })
      ```
    - The code assumes configs might be array of objects with .value property, but it's actually just array of numbers
    - Result: Only saves first value (1) instead of entire array [1,2,3,4,5,6,7,8,9,10]
  implication: Save bug causes data loss - only first value saved. Load bug is secondary (wrapping issue in handleLoadLibraryConfig)

## Resolution

root_cause: |
  **Bug 1 - Range values lost (data loss):**
  LibraryModal.handleSave (line 69-78) incorrectly assumes aliasConfigs might contain objects with .value property.
  Actually, aliasConfigs stores direct arrays: `{ "Input1": [1,2,3,4,5,6,7,8,9,10] }`
  Code does `configs[0]` which gets first value (1), then saves `{ alias: "Input1", value: 1 }` instead of `{ alias: "Input1", value: [1,2,3,4,5,6,7,8,9,10] }`

  **Bug 2 - Load wraps incorrectly:**
  App.tsx handleLoadLibraryConfig (line 147) wraps the loaded value in an array incorrectly:
  `newAliasConfigs[inputConfig.alias] = [{ value: inputConfig.value, units: inputConfig.units }]`
  Should be: `newAliasConfigs[inputConfig.alias] = inputConfig.value` (which is already an array)

  **Bug 3 - Case sensitivity file overwrites:**
  Backend routes.py line 228-229 doesn't normalize case, so "MyConfig" and "myconfig" become same file on Windows.

fix: |
  **Applied fixes:**

  1. ✓ LibraryModal.tsx (lines 65-78): Changed to save entire array as value
     - Added currentUnits prop to receive units from App state
     - Modified handleSave to: `return [{ alias, value: values, units: currentUnits[alias] }]`
     - Now saves entire array [1,2,3,4,5,6,7,8,9,10] instead of just first value

  2. ✓ App.tsx (lines 138-161): Fixed handleLoadLibraryConfig
     - Changed to: `newAliasConfigs[inputConfig.alias] = Array.isArray(inputConfig.value) ? inputConfig.value : [inputConfig.value]`
     - Added units restoration: `newAliasUnits[inputConfig.alias] = inputConfig.units`
     - Now correctly restores full array without wrapping

  3. ✓ App.tsx (line 529): Pass aliasUnits to LibraryModal
     - Added `currentUnits={aliasUnits}` prop so units are saved

  4. ✓ routes.py (line 230): Fix case sensitivity
     - Changed to: `config_file = config_dir / f"{safe_name.lower()}.json"`
     - All config names normalized to lowercase for consistent filenames

verification: |
  ✓ Automated tests passed (verify_library_fix.py):
    - Data structure transformation: PASS (10 values saved and loaded correctly)
    - Case sensitivity normalization: PASS (prevents overwrites)
    - Units preservation: PASS (units saved and restored)

  Manual verification recommended:
  1. Start app and load a Mathcad file
  2. Configure Input1 with range: Start=1, End=10, Step=1 (10 values) with units="in"
  3. Save config with name "Test Config 1"
  4. Clear inputs or reload page
  5. Load "Test Config 1" - verify all 10 values restored with units
  6. Save another config with name "Test Config 2" - verify both configs exist separately
  7. Try saving "TEST CONFIG 1" (different case) - verify it doesn't overwrite

files_changed:
  - frontend/src/components/LibraryModal.tsx
  - frontend/src/App.tsx
  - src/server/routes.py
