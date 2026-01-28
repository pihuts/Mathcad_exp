# Mathcad Automator v1.0.0

## What's Included

- `MathcadAutomator.exe` - Main application (double-click to run)
- Support files and libraries required for operation

## Running the Application

1. Double-click `MathcadAutomator.exe`
2. The application window will open automatically
3. No installation required - runs directly from this folder

**Note:** On first run, Windows may show a SmartScreen warning. This is normal for unsigned applications. Click "More info" then "Run anyway".

## System Requirements

- **Windows 10 or later**
- **PTC Mathcad Prime** (licensed and installed)
- **100 MB free disk space**
- **4 GB RAM recommended**

## Quick Start

1. **Double-click `MathcadAutomator.exe`**
2. **Click "Browse"** to select your `.mcdx` file
3. **Configure your inputs:**
   - Click an input name
   - Choose "Range" and enter Start/End/Step values
   - Click "Save"
4. **Click "Start Batch"**
5. **Find your results** in the output folder

**That's it!** You've just automated multiple calculations.

## User Data Location

Your saved configurations and logs are stored in:
```
%LOCALAPPDATA%\MathcadAutomator
```

**To access this folder:**
1. Press Windows key + R
2. Type `%LOCALAPPDATA%\MathcadAutomator`
3. Press Enter

## What You Can Do

- **Batch Processing:** Run your Mathcad file with hundreds of different input combinations
- **Workflow Chaining:** Connect multiple Mathcad files together (File A → File B → File C)
- **Export Options:** Save results as PDF and/or MCDX files
- **Library Management:** Save and reuse common input configurations

## Troubleshooting

**"Mathcad Application not found"**
- Ensure Mathcad Prime is installed
- Open Mathcad Prime manually first, then restart the Automator

**Application won't start**
- Verify you're using Windows 10 or later
- Check antivirus software (add to exceptions if needed)
- Try running as Administrator (right-click → Run as administrator)

**File won't open**
- Close the file in Mathcad if it's already open
- Move file to a shorter path (avoid paths longer than 260 characters)

## For Detailed Documentation

See the full README.md file in the parent directory or visit the project repository for:
- Complete usage guide
- Step-by-step examples
- Advanced troubleshooting
- Workflow chaining tutorial

## License

MIT License

---

**Need Help?** Visit the project repository or contact support.
