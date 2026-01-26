# Verification Guide: Export Options (MCDX/PDF)

**Phase:** 3.2
**Plan:** 03
**Purpose:** End-to-end verification of export functionality

## Prerequisites

1. **Backend server running:** `python -m uvicorn src.server.main:app --reload`
2. **Frontend running:** `cd frontend && npm start`
3. **Mathcad Prime installed** and accessible
4. **Test file available:** `test_files/PF01.mcdx`

## Task 1: Test Batch Export (PDF only)

### Steps

1. Navigate to the **Batch** tab in the web UI
2. Click "Browse" and select `test_files/PF01.mcdx`
3. Configure inputs:
   - Add input: `Length` with values: `5, 10`
   - Add input: `Width` with values: `3, 6`
4. **Configure export options:**
   - **Uncheck** "Save as MCDX"
   - **Check** "Save as PDF"
5. Click "Run Batch"
6. Wait for batch to complete

### Verification Checklist

- [ ] Batch completes successfully (all 4 combinations)
- [ ] Results directory contains **only PDF files** (no .mcdx files)
- [ ] PDF count matches combinations: **4 PDF files**
- [ ] **Filename Check:** Files follow pattern `PF01_Length-5_Width-3.pdf`, `PF01_Length-5_Width-6.pdf`, etc.
- [ ] **Parameter values visible in filenames**
- [ ] **File integrity:** All PDFs have non-zero file size (>0 bytes)
- [ ] **UI Link Check:** Click PDF link in progress bar - file opens in default PDF viewer

### Expected Results

**Results directory should contain:**
```
results/
  PF01_Length-5_Width-3.pdf   (>0 bytes)
  PF01_Length-5_Width-6.pdf   (>0 bytes)
  PF01_Length-10_Width-3.pdf  (>0 bytes)
  PF01_Length-10_Width-6.pdf  (>0 bytes)
```

**No MCDX files should be present.**

---

## Task 2: Test Batch Export (Both formats)

### Steps

1. Stay in the **Batch** tab
2. Keep the same file selected (or reselect `test_files/PF01.mcdx`)
3. Configure inputs:
   - Add input: `Length` with values: `15, 20`
   - Add input: `Width` with value: `8`
4. **Configure export options:**
   - **Check** "Save as MCDX"
   - **Check** "Save as PDF"
5. Click "Run Batch"
6. Wait for batch to complete

### Verification Checklist

- [ ] Batch completes successfully (all 2 combinations)
- [ ] Results directory contains **both PDF and MCDX files**
- [ ] File count: **2 PDF files + 2 MCDX files = 4 total**
- [ ] **Filename matching:** Each combination has matching PDF and MCDX:
  - `PF01_Length-15_Width-8.pdf` and `PF01_Length-15_Width-8.mcdx`
  - `PF01_Length-20_Width-8.pdf` and `PF01_Length-20_Width-8.mcdx`
- [ ] **Parameter values visible in filenames**
- [ ] **File integrity:** All files have non-zero file size (>0 bytes)
- [ ] **UI Links:** Both PDF and MCDX links work in progress bar

### Expected Results

**Results directory should contain (in addition to Task 1 files):**
```
results/
  PF01_Length-15_Width-8.pdf   (>0 bytes)
  PF01_Length-15_Width-8.mcdx  (>0 bytes)
  PF01_Length-20_Width-8.pdf   (>0 bytes)
  PF01_Length-20_Width-8.mcdx  (>0 bytes)
```

---

## Task 3: Test Workflow Export

### Steps

1. Navigate to the **Workflow** tab in the web UI
2. **Create a 2-file workflow:**

   **File 1:**
   - Click "Browse" and select `test_files/PF01.mcdx`
   - Add input: `Length` with value: `25`
   - Add input: `Width` with value: `12`
   - No mappings (first file in chain)

   **File 2:**
   - Click "+ Add File"
   - Click "Browse" and select `test_files/PF01.mcdx`
   - Add input: `Length` with value: `30`
   - **Add mapping:**
     - Source: File 1 → Output: `Width`
     - Target Input: `Width`

3. **Configure workflow export options (global):**
   - **Check** "Export as PDF"
   - **Check** "Export as MCDX"
4. **Name the workflow:** `TestWorkflow`
5. Click "Run Workflow"
6. Wait for workflow to complete

### Verification Checklist

- [ ] Workflow completes successfully (both steps)
- [ ] Results directory contains **workflow-named files**
- [ ] File count: **2 steps × 2 formats = 4 files**
- [ ] **Filename pattern:** Files follow `WorkflowName_StepN_FileName` format:
  - `TestWorkflow_Step1_PF01.pdf`
  - `TestWorkflow_Step1_PF01.mcdx`
  - `TestWorkflow_Step2_PF01.pdf`
  - `TestWorkflow_Step2_PF01.mcdx`
- [ ] **Step numbers visible** in filenames (Step1, Step2)
- [ ] **File integrity:** All files have non-zero file size (>0 bytes)
- [ ] **UI Links:** All PDF and MCDX links work in results panel
- [ ] **Data propagation:** Step 2 received Width value from Step 1 output

### Expected Results

**Results directory should contain (workflow files):**
```
results/
  TestWorkflow_Step1_PF01.pdf   (>0 bytes)
  TestWorkflow_Step1_PF01.mcdx  (>0 bytes)
  TestWorkflow_Step2_PF01.pdf   (>0 bytes)
  TestWorkflow_Step2_PF01.mcdx  (>0 bytes)
```

---

## Overall Success Criteria

### All Three Tasks Must Pass:

1. **Batch PDF-only export** works correctly
2. **Batch dual-format export** works correctly
3. **Workflow dual-format export** works correctly with step-based naming

### File Naming Validation:

- **Batch files:** Include parameter names and values
- **Workflow files:** Include workflow name and step numbers
- **No invalid characters** in filenames (properly sanitized)

### File Integrity:

- **No zero-byte files** (all files have content)
- **Files are openable** via UI links
- **Native applications** open files correctly (PDF viewer, Mathcad Prime)

### UI Functionality:

- **Export checkboxes** control format selection
- **Progress indicators** show file generation
- **Result links** enable one-click file opening
- **ResultsList component** displays generated files

---

## Screenshots to Capture

For documentation purposes, capture:

1. **Batch Tab:** Export options selected (PDF only, then both)
2. **Results Panel:** Showing parameter-based filenames for batch
3. **Workflow Tab:** Export options and file mappings
4. **Results Directory:** Windows Explorer showing all generated files with sizes
5. **File Opening:** PDF opened from UI link (demonstrates native integration)

---

## Troubleshooting

**If batch fails:**
- Check that Mathcad Prime is installed
- Verify `test_files/PF01.mcdx` exists and is valid
- Check backend console for error messages

**If files not generated:**
- Verify export checkboxes are selected
- Check `results/` directory permissions
- Review browser console and backend logs

**If filenames don't match pattern:**
- This is a FAIL - parameter naming is broken
- Check batch_manager.py and workflow_manager.py export logic

**If zero-byte files appear:**
- This is a FAIL - export process is broken
- Check worker.py save_as implementation
