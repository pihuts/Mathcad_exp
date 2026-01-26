"""
Verification script for Task 1: Test Batch Export (PDF only)

Tests that batch processing correctly exports only PDF files when MCDX is disabled.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine.protocol import BatchConfig, InputConfig
from src.engine.batch_manager import BatchManager
import asyncio


async def test_batch_pdf_only():
    """Test batch export with PDF only (no MCDX)"""
    print("=" * 60)
    print("Task 1: Test Batch Export (PDF only)")
    print("=" * 60)

    # Get test file path
    test_file = Path("D:/Mathcad_exp/test_files/PF01.mcdx")
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False

    print(f"\nTest file: {test_file}")

    # Create batch config with PDF only
    config = BatchConfig(
        template_path=str(test_file),
        inputs=[
            InputConfig(name="Length", values=[5.0, 10.0], unit=None),
            InputConfig(name="Width", values=[3.0, 6.0], unit=None)
        ],
        export_pdf=True,   # Enable PDF
        export_mcdx=False  # Disable MCDX
    )

    print(f"\nBatch Configuration:")
    print(f"  Template: {config.template_path}")
    print(f"  Inputs: {len(config.inputs)} parameters")
    print(f"  Export PDF: {config.export_pdf}")
    print(f"  Export MCDX: {config.export_mcdx}")
    print(f"  Expected combinations: {len(config.inputs[0].values) * len(config.inputs[1].values)}")

    # Clear results directory
    results_dir = Path("D:/Mathcad_exp/results")
    if results_dir.exists():
        for f in results_dir.glob("*.pdf"):
            f.unlink()
        for f in results_dir.glob("*.mcdx"):
            f.unlink()
        print(f"\nCleared results directory")

    # Run batch
    print(f"\nStarting batch execution...")
    manager = BatchManager()

    try:
        results = await manager.run_batch(config)
        print(f"\nBatch completed!")
        print(f"  Total combinations: {results.total}")
        print(f"  Successful: {results.successful}")
        print(f"  Failed: {results.failed}")

        # Check results directory
        pdf_files = list(results_dir.glob("*.pdf"))
        mcdx_files = list(results_dir.glob("*.mcdx"))

        print(f"\nResults directory check:")
        print(f"  PDF files found: {len(pdf_files)}")
        print(f"  MCDX files found: {len(mcdx_files)}")

        # Verify naming pattern
        print(f"\nPDF files with parameter-based naming:")
        for pdf in sorted(pdf_files):
            file_size = pdf.stat().st_size
            print(f"  - {pdf.name} ({file_size} bytes)")

            # Check naming pattern: should include parameter values
            if "Length" not in pdf.name or "Width" not in pdf.name:
                print(f"    WARNING: File naming doesn't include parameter names!")

        # Verification
        success = True
        if len(mcdx_files) > 0:
            print(f"\n❌ FAIL: Found {len(mcdx_files)} MCDX files, expected 0")
            success = False
        else:
            print(f"\n✅ PASS: No MCDX files created")

        if len(pdf_files) != results.successful:
            print(f"❌ FAIL: Expected {results.successful} PDF files, found {len(pdf_files)}")
            success = False
        else:
            print(f"✅ PASS: Correct number of PDF files created")

        # Check for zero-byte files
        zero_byte_files = [f for f in pdf_files if f.stat().st_size == 0]
        if zero_byte_files:
            print(f"❌ FAIL: Found {len(zero_byte_files)} zero-byte PDF files")
            success = False
        else:
            print(f"✅ PASS: All PDF files have content (non-zero bytes)")

        return success

    except Exception as e:
        print(f"\n❌ ERROR: Batch execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_batch_pdf_only())
    sys.exit(0 if result else 1)
