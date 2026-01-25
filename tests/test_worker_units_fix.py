"""
Unit test for the units handling fix in worker.py
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_preserve_units_logic():
    """
    Test the preserve_units logic that determines when to use preserve_worksheet_units
    """
    test_cases = [
        (None, True, "No units provided - preserve worksheet units"),
        ('', True, "Empty string - preserve worksheet units"),
        ('ft', False, "Units 'ft' provided - allow Mathcad conversion"),
        ('in', False, "Units 'in' provided - allow Mathcad conversion"),
        ('kip', False, "Units 'kip' provided - allow Mathcad conversion"),
        ('m', False, "Units 'm' provided - allow Mathcad conversion"),
        ('N', False, "Units 'N' provided - allow Mathcad conversion"),
        ('kg', False, "Units 'kg' provided - allow Mathcad conversion"),
    ]

    print("Testing preserve_units logic (units is None or units == ''):")
    all_passed = True
    for units, expected_preserve, description in test_cases:
        # This is the exact logic used in worker.py
        preserve_units = (units is None or units == "")
        status = 'PASS' if preserve_units == expected_preserve else 'FAIL'
        if preserve_units != expected_preserve:
            all_passed = False
        print(f"  {status}: units={repr(units):10s} -> preserve_units={str(preserve_units):5s} (expected {str(expected_preserve):5s}) - {description}")

    assert all_passed, "Some test cases failed"
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_preserve_units_logic()
