"""
Verification script for Task 3: Test Workflow Export

Tests that workflow orchestration correctly exports both formats for each step.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine.protocol import WorkflowConfig, WorkflowFile, FileMapping, InputConfig
from src.engine.workflow_manager import WorkflowManager
import asyncio


async def test_workflow_export():
    """Test workflow export with both PDF and MCDX"""
    print("=" * 60)
    print("Task 3: Test Workflow Export")
    print("=" * 60)

    # Get test file path
    test_file = Path("D:/Mathcad_exp/test_files/PF01.mcdx")
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False

    print(f"\nTest file: {test_file}")

    # Create workflow config with 2 files
    config = WorkflowConfig(
        name="TestWorkflow",
        files=[
            WorkflowFile(
                path=str(test_file),
                inputs=[
                    InputConfig(name="Length", values=[25.0], unit=None),
                    InputConfig(name="Width", values=[12.0], unit=None)
                ],
                mappings=[]
            ),
            WorkflowFile(
                path=str(test_file),
                inputs=[
                    InputConfig(name="Length", values=[30.0], unit=None)
                ],
                mappings=[
                    FileMapping(source_file=0, source_output="Width", target_input="Width")
                ]
            )
        ],
        export_pdf=True,   # Enable PDF
        export_mcdx=True   # Enable MCDX
    )

    print(f"\nWorkflow Configuration:")
    print(f"  Name: {config.name}")
    print(f"  Files: {len(config.files)}")
    print(f"  Export PDF: {config.export_pdf}")
    print(f"  Export MCDX: {config.export_mcdx}")

    # Clear results directory
    results_dir = Path("D:/Mathcad_exp/results")
    if results_dir.exists():
        for f in results_dir.glob("*.pdf"):
            f.unlink()
        for f in results_dir.glob("*.mcdx"):
            f.unlink()
        print(f"\nCleared results directory")

    # Run workflow
    print(f"\nStarting workflow execution...")
    manager = WorkflowManager()

    try:
        results = await manager.run_workflow(config)
        print(f"\nWorkflow completed!")
        print(f"  Total files: {results.total_files}")
        print(f"  Successful: {results.successful_files}")
        print(f"  Failed: {results.failed_files}")

        # Check results directory
        pdf_files = list(results_dir.glob("*.pdf"))
        mcdx_files = list(results_dir.glob("*.mcdx"))

        print(f"\nResults directory check:")
        print(f"  PDF files found: {len(pdf_files)}")
        print(f"  MCDX files found: {len(mcdx_files)}")

        # Verify naming pattern for PDFs
        print(f"\nPDF files (workflow naming pattern):")
        for pdf in sorted(pdf_files):
            file_size = pdf.stat().st_size
            print(f"  - {pdf.name} ({file_size} bytes)")

            # Check naming pattern: should include workflow name and step number
            if "TestWorkflow" not in pdf.name or "Step" not in pdf.name:
                print(f"    WARNING: File naming doesn't follow workflow pattern!")

        # Verify naming pattern for MCDX
        print(f"\nMCDX files (workflow naming pattern):")
        for mcdx in sorted(mcdx_files):
            file_size = mcdx.stat().st_size
            print(f"  - {mcdx.name} ({file_size} bytes)")

            if "TestWorkflow" not in mcdx.name or "Step" not in mcdx.name:
                print(f"    WARNING: File naming doesn't follow workflow pattern!")

        # Verification
        success = True

        # Should have 2 PDF files (one per step)
        expected_files = results.successful_files
        if len(pdf_files) != expected_files:
            print(f"\n❌ FAIL: Expected {expected_files} PDF files, found {len(pdf_files)}")
            success = False
        else:
            print(f"\n✅ PASS: Correct number of PDF files created")

        if len(mcdx_files) != expected_files:
            print(f"❌ FAIL: Expected {expected_files} MCDX files, found {len(mcdx_files)}")
            success = False
        else:
            print(f"✅ PASS: Correct number of MCDX files created")

        # Check for zero-byte files
        zero_byte_pdfs = [f for f in pdf_files if f.stat().st_size == 0]
        zero_byte_mcdx = [f for f in mcdx_files if f.stat().st_size == 0]

        if zero_byte_pdfs:
            print(f"❌ FAIL: Found {len(zero_byte_pdfs)} zero-byte PDF files")
            success = False
        else:
            print(f"✅ PASS: All PDF files have content")

        if zero_byte_mcdx:
            print(f"❌ FAIL: Found {len(zero_byte_mcdx)} zero-byte MCDX files")
            success = False
        else:
            print(f"✅ PASS: All MCDX files have content")

        # Check naming pattern consistency
        pdf_names = {f.stem for f in pdf_files}
        mcdx_names = {f.stem for f in mcdx_files}

        if pdf_names != mcdx_names:
            print(f"❌ FAIL: PDF and MCDX file names don't match")
            print(f"  PDF only: {pdf_names - mcdx_names}")
            print(f"  MCDX only: {mcdx_names - pdf_names}")
            success = False
        else:
            print(f"✅ PASS: PDF and MCDX files have matching names")

        # Check for step numbers in names
        step_pattern_ok = all("Step" in f.name for f in pdf_files)
        if not step_pattern_ok:
            print(f"❌ FAIL: Not all files follow workflow step naming pattern")
            success = False
        else:
            print(f"✅ PASS: All files follow workflow step naming pattern")

        return success

    except Exception as e:
        print(f"\n❌ ERROR: Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_workflow_export())
    sys.exit(0 if result else 1)
