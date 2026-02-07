#!/usr/bin/env python3
"""
Simple test to check if the 2gen generator function works
"""

# Test the calculate_parent_positions function directly
import sys
import os

sys.path.append("/home/user/CODE_BASE/namechart")

from apps.generator.utils.image_2generator import calculate_parent_positions
from apps.generator.utils.sunbeam_position_calculator import SunbeamPositionCalculator
from apps.parser.models import PersonData


# Create mock data
def test_calculate_parent_positions():
    # Create mock individuals
    individuals = {
        "I1": PersonData(
            id="I1",
            full_name="John Doe",
            given_name="John",
            surname="Doe",
            father="F1",
            mother="M1",
        ),
        "F1": PersonData(
            id="F1", full_name="Father Doe", given_name="Father", surname="Doe"
        ),
        "M1": PersonData(
            id="M1", full_name="Mother Doe", given_name="Mother", surname="Doe"
        ),
    }

    # Create family data structure
    family_data = {"individuals": individuals}

    # Create position calculator
    calculator = SunbeamPositionCalculator(canvas_size=1950)

    # Test the function
    try:
        positions = calculate_parent_positions(family_data, calculator)
        print(f"SUCCESS: Found {len(positions)} parent positions")
        for i, (parent_type, x, y, rotation, individual) in enumerate(positions):
            print(
                f"  Parent {i + 1}: {parent_type} at ({x}, {y}) rotation={rotation} - {individual.full_name if individual else 'None'}"
            )
        return True
    except Exception as e:
        import traceback

        print(f"ERROR: {e}")
        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_calculate_parent_positions()
    sys.exit(0 if success else 1)
