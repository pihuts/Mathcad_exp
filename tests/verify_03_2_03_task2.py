"""
Verification script for Task 2: Test Batch Export (Both formats)

Tests that batch processing correctly exports both PDF and MCDX files.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.engine.protocol import BatchConfig, InputConfig
from src.engine.batch_manager import BatchManager
import asyncio


async def test_batch_both_formats():
    """Test batch export with both PDF and MCDX"""
    print("=" * 60)
    print("Task 2: Test Batch Export (Both formats)")
    print("=" * 60)

    # Get test file path
    test_file = Path("D:/Mathcad_exp/test_files/PF01.mcdx")
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False

    print(f"\nTest file: {test_file}")

    # Create batch config with both formats
    config = BatchConfig(
        template_path=str(test_file),
        inputs=[
            InputConfig(name="Length", values=[15.0, 20.0], unit=None),
            InputConfig(name="Width", values=[8.0], unit=None)
        ],
        export_pdf=True,   # Enable PDF
        export_mcdx=True   # Enable MCDX
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

        # Verify naming pattern for PDFs
        print(f"\nPDF files with parameter-based naming:")
        for pdf in sorted(pdf_files):
            file_size = pdf.stat().st_size
            print(f"  - {pdf.name} ({file_size} bytes)")

        # Verify naming pattern for MCDX
        print(f"\nMCDX files with parameter-based naming:")
        for mcdx in sorted(mcdx_files):
            file_size = mcdx.stat().st_size
            print(f"  - {mcdx.name} ({file_size} bytes)")

        # Verification
        success = True

        if len(pdf_files) != results.successful:
            print(f"\n❌ FAIL: Expected {results.successful} PDF files, found {len(pdf_files)}")
            success = False
        else:
            print(f"\n✅ PASS: Correct number of PDF files created")

        if len(mcdx_files) != results.successful:
            print(f"❌ FAIL: Expected {results.successful} MCDX files, found {len(mcdx_files)}")
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

        return success

    except Exception as e:
        print(f"\n❌ ERROR: Batch execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_batch_both_formats())
    sys.exit(0 if result else 1)
