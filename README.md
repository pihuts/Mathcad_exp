# Mathcad Automator

**Mathcad Automator** is a local Windows application that automates PTC Mathcad Prime calculations. It enables engineers to perform complex parameter studies and chain multiple Mathcad files together without writing scripts or VBA.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

---

## Features

- **Batch Processing**
  - Run your Mathcad file with hundreds of different input combinations automatically
  - Define input ranges (Start, End, Step) or enter specific value lists
  - Upload CSV files to import input data
  - Export results as PDF and/or MCDX files with automatic naming

- **Workflow Chaining**
  - Connect multiple Mathcad files together (File A → File B → File C)
  - Map outputs from one file to inputs in the next file
  - Run complex multi-step calculations automatically

- **Library Management**
  - Save your input configurations as named templates
  - Reuse common configurations without re-entering data
  - Share configurations with team members

- **Native Windows Integration**
  - Uses native file dialogs for easy file selection
  - Opens generated files with one click
  - Stores your data in standard Windows folders

---

## Installation

### Option 1: Using the Executable (Recommended)

1. **Download the distribution package** (`MathcadAutomator-v1.0.0.zip`)

2. **Extract the ZIP file** to any folder on your computer
   - Right-click the ZIP file
   - Select "Extract All..."
   - Choose a destination folder

3. **Run the application**
   - Open the extracted folder
   - Double-click `MathcadAutomator.exe`

That's it! The application will open in its own window.

### Option 2: Running from Source

If you want to modify the code or run from source:

**Prerequisites:**
- PTC Mathcad Prime (licensed and installed)
- Python 3.11 (required for MathcadPy compatibility)
- Node.js 18+ (for frontend development)

**Installation Steps:**

1. **Clone or download the repository**

2. **Set up Python environment**
   ```bash
   # Create a virtual environment
   python -m venv .venv

   # Activate the environment (Windows CMD)
   .venv\Scripts\activate.bat

   # Or activate the environment (PowerShell)
   .venv\Scripts\Activate.ps1

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Build the frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Run the application**
   ```bash
   python -m src.server.main
   ```

The application will open in your default browser at `http://localhost:8000`

---

## Quick Start

**Get a result in under 3 minutes:**

1. **Open the Application**
   - Double-click `MathcadAutomator.exe`

2. **Select Your Mathcad File**
   - Click the **Browse** button in the "Batch Processing" section
   - Select your `.mcdx` file

3. **Configure Your Inputs**
   - The app automatically finds all Input aliases in your file
   - Click an input name to configure it
   - Choose **"Range"** and enter: Start=1, End=10, Step=1
   - Click **Save**

4. **Run the Calculation**
   - Click **Start Batch**
   - Watch the progress bar
   - When complete, click any result file to open it

**That's it!** You've just run 10 calculations automatically.

![Main Interface](docs/screenshot-main.png)
*Main interface showing file selection and input configuration*

---

## Usage Guide

### Batch Processing

Batch processing runs your Mathcad file with many different input combinations.

**Step 1: Open Your File**
- Click **Browse** in the Batch Processing section
- Select your `.mcdx` worksheet

**Step 2: Configure Inputs**
- The app displays all Input aliases found in your file
- Click any input to configure it:

  - **Single Value:** Enter one number or string
  - **Range:** Define Start, End, and Step (for numeric inputs)
    - Example: Start=10, End=100, Step=10 generates [10, 20, 30, ..., 100]
  - **List:** Enter specific values separated by commas
    - Example: 1, 5, 10, 20
  - **CSV:** Upload a CSV file with column headers matching your input names

**Step 3: Choose Input Type**
- For each input, select **Number** or **String** type
- Number inputs support units (in, ft, kip, etc.)
- String inputs are for text values (material names, labels, etc.)

**Step 4: Configure Export Options**
- Check **Export as PDF** to save each calculation as a PDF
- Check **Export as MCDX** to save each calculation as a Mathcad file
- Choose an output folder (default is next to your source file)

**Step 5: Run**
- Click **Start Batch**
- The app shows progress and estimated time remaining
- Click **Stop** to cancel the batch
- View results in the list below (newest first)

**Result Files:**
- Batch exports are named: `Filename_InputName-Value.pdf`
- Example: `BeamCalc_Length-120.pdf`

![Results View](docs/screenshot-results.png)
*Completed batch with generated files listed*

### Workflow Chaining

Workflow chaining connects multiple Mathcad files so outputs from one file become inputs to the next file.

**Step 1: Switch to Workflow Tab**
- Click the **Workflow** tab at the top of the window

**Step 2: Add Files**
- Click **Add File** for each Mathcad file in your chain
- Files appear in order (top to bottom = execution order)

**Step 3: Map Outputs to Inputs**
- Click **Map Outputs** on any file
- The left side shows outputs from the previous file
- The right side shows inputs for the current file
- Click an output, then click an input to connect them

**Step 4: Configure Remaining Inputs**
- Any inputs not mapped from previous files need values
- Click the input name to configure (same as batch processing)

**Step 5: Run the Workflow**
- Click **Start Workflow**
- Files execute in sequence
- Data passes automatically through mapped connections

**Result Files:**
- Workflow exports include the step number: `WorkflowName_Step1_FileName.pdf`

### Saving and Loading Configurations

Save your input configurations to reuse later.

**Save a Configuration:**
1. Configure all your inputs
2. Click the **Library** button
3. Click the **Save** tab
4. Enter a name (e.g., "Standard Beam Study")
5. Click **Save Configuration**

**Load a Configuration:**
1. Open the same Mathcad file
2. Click the **Library** button
3. Click the **Load** tab
4. Select your saved configuration
5. Click **Load**

**Where Configurations Are Stored:**
- Windows: `%LOCALAPPDATA%\MathcadAutomator\library\`
- Each file has its own folder: `YourFilename_configs/`

### Export Options

Control how your results are saved.

**PDF Export:**
- Recommended for reports and sharing
- Smaller file size
- Viewable on any device

**MCDX Export:**
- Full Mathcad file with all calculations
- Larger file size
- Requires Mathcad Prime to open

**Both Formats:**
- Check both boxes to export in both formats
- Useful for archival (MCDX) and sharing (PDF)

---

## Troubleshooting

### "Mathcad Application not found"

**Cause:** Mathcad Prime is not installed or not registered in Windows.

**Solution:**
1. Verify Mathcad Prime is installed
   - Press Windows key, type "Mathcad Prime"
   - If it doesn't appear, install Mathcad Prime

2. Check Mathcad opens correctly
   - Open Mathcad Prime manually
   - Create a simple worksheet
   - Save and close

3. Restart Mathcad Automator

### "Cannot open file" or "File not accessible"

**Cause:** The file path is too long, file is in use, or permission denied.

**Solution:**
1. **Shorten the file path**
   - Move the file to a shorter path like `C:\MathcadFiles\`
   - Avoid paths longer than 260 characters

2. **Close the file in Mathcad**
   - If the file is open in Mathcad, close it first

3. **Check file permissions**
   - Right-click the file
   - Select Properties
   - Ensure "Read-only" is unchecked

4. **Run as Administrator**
   - Right-click `MathcadAutomator.exe`
   - Select "Run as administrator"

### Application hangs or freezes

**Cause:** Mathcad process is stuck or waiting for user input.

**Solution:**
1. **Check for Mathcad dialogs**
   - Look for Mathcad Prime windows behind other windows
   - Close any open dialogs in Mathcad

2. **Close Mathcad completely**
   - Close all Mathcad Prime windows
   - Check Task Manager (Ctrl+Shift+Esc) for `Mathcad.exe` processes
   - End any Mathcad processes

3. **Restart Mathcad Automator**

4. **Check your worksheet**
   - Open the file in Mathcad manually
   - Ensure it calculates without errors
   - Remove any password protection or dialog prompts

### "Invalid input value" error

**Cause:** The input value doesn't match the expected type or has invalid characters.

**Solution:**
1. **Check input type**
   - Number inputs must be numeric (e.g., 10, 5.5, -3)
   - String inputs must be text (e.g., "Steel", "A36")

2. **Check for special characters**
   - Remove commas from numbers (use 1000, not 1,000)
   - Avoid special characters in strings

3. **Check units**
   - If using units, ensure they're valid (in, ft, kip, psi, etc.)
   - Leave units blank for default behavior

### Batch stopped mid-execution

**Cause:** An iteration failed or the process was interrupted.

**Solution:**
1. **Check the batch log**
   - Look at which iteration failed
   - Check the inputs for that iteration

2. **Test the failing inputs manually**
   - Open the file in Mathcad
   - Enter the same inputs
   - See if Mathcad shows an error

3. **Use "Continue on Error"**
   - The app automatically logs failures and continues
   - Check the Results list for completed files
   - Fix the failing inputs and run again

### Application won't start

**Cause:** Missing dependencies or corrupted installation.

**Solution (for .exe users):**
1. **Verify Windows version**
   - Requires Windows 10 or later
   - Check Settings > System > About

2. **Check antivirus**
   - Some antivirus software blocks the app
   - Add `MathcadAutomator.exe` to antivirus exceptions

3. **Re-extract the ZIP**
   - Delete the extracted folder
   - Extract the ZIP file again
   - Try running the new `MathcadAutomator.exe`

**Solution (for source users):**
1. **Verify Python version**
   - Run `python --version`
   - Must be Python 3.11.x
   - MathcadPy is not compatible with Python 3.12+

2. **Reinstall dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Rebuild frontend**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

---

## Examples

### Example 1: Beam Length Parameter Study

**Scenario:** Calculate deflection for a beam with lengths from 10 to 20 feet.

**Setup:**
1. Open your beam calculation worksheet
2. Configure input `Length`:
   - Type: **Number**
   - Mode: **Range**
   - Start: 10
   - End: 20
   - Step: 1
   - Units: **ft**
3. Configure input `Load`:
   - Type: **Number**
   - Mode: **Single Value**
   - Value: 1000
   - Units: **kip**
4. Export: **PDF** checked
5. Click **Start Batch**

**Result:** 11 PDF files named `BeamCalc_Length-10.pdf`, `BeamCalc_Length-11.pdf`, ..., `BeamCalc_Length-20.pdf`

### Example 2: Material Comparison

**Scenario:** Compare three different materials with multiple load cases.

**Setup:**
1. Open your material calculation worksheet
2. Configure input `Material`:
   - Type: **String**
   - Mode: **List**
   - Values: A36, A572, A992
3. Configure input `Load`:
   - Type: **Number**
   - Mode: **CSV**
   - Upload CSV with column "Load" containing: 10, 20, 50, 100
4. Export: **Both PDF and MCDX** checked
5. Click **Start Batch**

**Result:** 12 calculations (3 materials × 4 loads) with both PDF and MCDX files

### Example 3: Multi-Step Workflow

**Scenario:** Calculate loads, then size members, then check deflection.

**Workflow:**
1. **File 1: LoadCalc.mcdx** - Calculates loads from geometry
2. **File 2: MemberSize.mcdx** - Sizes members based on loads
3. **File 3: DeflectionCheck.mcdx** - Checks deflection for sized members

**Setup:**
1. Switch to **Workflow** tab
2. Add all three files in order
3. Click **Map Outputs** on File 2
   - Map `TotalLoad` (from File 1) → `AppliedLoad` (in File 2)
4. Click **Map Outputs** on File 3
   - Map `MemberSize` (from File 2) → `SectionSize` (in File 3)
   - Map `CalculatedLoad` (from File 2) → `CheckLoad` (in File 3)
5. Configure any remaining inputs
6. Click **Start Workflow**

**Result:** All three files execute in sequence with data passing automatically

### Example 4: Using Saved Configurations

**Scenario:** Run the same parameter study every week with updated data.

**Setup:**
1. Open your weekly report worksheet
2. Configure all inputs for this week's study
3. Click **Library** → **Save** tab
4. Name it "Weekly Standard Study"
5. Click **Save Configuration**

**Next Week:**
1. Open the same worksheet
2. Click **Library** → **Load** tab
3. Select "Weekly Standard Study"
4. Click **Load**
5. Update any values that changed
6. Click **Start Batch**

**Time Saved:** No need to re-enter all inputs each week

---

## Process Diagrams

### Batch Processing Flow

```
┌─────────────────┐
│  Select File    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Configure Inputs│
│  (Range/List)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Choose Export   │
│  (PDF/MCDX)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Run Batch     │
│  (Auto for each │
│   combination)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  View Results   │
│  (Open files)   │
└─────────────────┘
```

### Workflow Chaining Flow

```
┌──────────────┐     Map      ┌──────────────┐
│   File A     │ Outputs →   │   File B     │
│ (Inputs set  ───────────────▶ (Inputs from │
│   manually)  │              │  File A +    │
└──────────────┘              │  manual)     │
                              └──────┬───────┘
                                     │ Map
                                     ▼
                              ┌──────────────┐
                              │   File C     │
                              │ (Inputs from │
                              │  File B +    │
                              │  manual)     │
                              └──────────────┘
```

---

## System Requirements

**For Executable Users:**
- Windows 10 or later
- PTC Mathcad Prime (licensed and installed)
- 100 MB free disk space
- 4 GB RAM recommended

**For Source Users:**
- All of the above, plus:
- Python 3.11 (specific version required)
- Node.js 18+ (for frontend development)

---

## Data Storage

**User Data Location:**
`%LOCALAPPDATA%\MathcadAutomator`

**Contains:**
- Saved library configurations
- Application logs
- Window position/size settings

**To access:**
1. Press Windows key + R
2. Type `%LOCALAPPDATA%\MathcadAutomator`
3. Press Enter

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues, questions, or feature requests, please visit the project repository.
