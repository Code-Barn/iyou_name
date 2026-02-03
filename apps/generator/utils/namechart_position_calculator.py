"""
NameChart positioning system with exact naming convention and layout specifications.

This system implements the user's specific naming convention and square chart layout
with corner-based positioning and special handling for the tricky 2nd generation spaces.
"""

import math
from typing import List, Tuple, Dict, Any


class NameChartPositionCalculator:
    """
    Calculate positions for family tree names following the user's exact specifications:

    Naming Convention:
    - '0' - Primary individual (center)
    - '1' - Father, '2' - Mother
    - 'A' - Father's father, 'B' - Father's mother, 'C' - Mother's father, 'D' - Mother's mother
    - 'A1111111' - Father's father's father's father's father's father's father's father
    - 'A1111112' - Father's father's father's father's father's father's father's mother

    Layout:
    - Square chart divided into 4 corners
    - Gen 2: Parents in corners with special 90°/45° text orientation
    - Gen 3+: More space, traditional positioning
    - Gen 8-10: Sunbeam orientation due to space constraints
    """

    def __init__(self, canvas_size: int = 1950):
        """
        Initialize calculator for given canvas size.

        Args:
            canvas_size: Size of square canvas (1950 for 1-7gen, 4700 for 8-10gen)
        """
        self.canvas_size = canvas_size
        self.center = canvas_size // 2

        # Design parameters based on canvas size
        if canvas_size == 4700:
            # 10gen parameters
            self.corner_positions = {
                "top_left": (1175, 1175),  # Father's father (A)
                "top_right": (3525, 1175),  # Mother's father (C)
                "bottom_left": (1175, 3525),  # Father's mother (B)
                "bottom_right": (3525, 3525),  # Mother's mother (D)
            }
            self.parent_positions = {
                "father": (2350, 800),  # Father (1)
                "mother": (2350, 3900),  # Mother (2)
            }
            self.gen_radii = {
                3: 600,  # Grandparents
                4: 900,  # Great-grandparents
                5: 1200,  # 4th generation
                6: 1500,  # 5th generation
                7: 1800,  # 6th generation
                8: 2100,  # 7th generation
                9: 2400,  # 8th generation (sunbeam starts)
                10: 2700,  # 9th generation
            }
        else:
            # 1-7gen parameters (1950px canvas)
            scale_factor = canvas_size / 4700
            self.corner_positions = {
                "top_left": (487, 487),
                "top_right": (1463, 487),
                "bottom_left": (487, 1463),
                "bottom_right": (1463, 1463),
            }
            self.parent_positions = {
                "father": (975, 400),
                "mother": (975, 1575),
            }
            self.gen_radii = {
                3: int(600 * scale_factor),
                4: int(900 * scale_factor),
                5: int(1200 * scale_factor),
                6: int(1500 * scale_factor),
                7: int(1800 * scale_factor),
            }

        # Font sizes
        self.font_sizes = {
            0: 84,  # Primary
            1: 72,  # Parents
            2: 72,  # Parents (same generation)
            3: 60,  # Grandparents
            4: 48,  # Great-grandparents
            5: 42,  # 4th gen
            6: 36,  # 5th gen
            7: 32,  # 6th gen
            8: 28,  # 7th gen
            9: 24,  # 8th gen
            10: 20,  # 9th gen
        }

    def calculate_all_positions(
        self, family_data: Dict[str, Any]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """
        Calculate positions for all individuals using the exact naming convention.

        Args:
            family_data: Dictionary with individuals keyed by naming convention

        Returns:
            Dictionary mapping name_id to (x, y, rotation, individual)
        """
        all_positions = {}

        # Primary individual (0) - center
        if "0" in family_data:
            all_positions["0"] = (self.center, self.center, 0, family_data["0"])

        # Parents (1, 2) - corners with special orientation
        if "1" in family_data:  # Father
            x, y = self.parent_positions["father"]
            all_positions["1"] = (
                x,
                y,
                0,
                family_data["1"],
            )  # Base position, text handled separately

        if "2" in family_data:  # Mother
            x, y = self.parent_positions["mother"]
            all_positions["2"] = (
                x,
                y,
                0,
                family_data["2"],
            )  # Base position, text handled separately

        # Grandparents (A, B, C, D) - corners
        corner_mapping = {
            "A": "top_left",  # Father's father
            "B": "bottom_left",  # Father's mother
            "C": "top_right",  # Mother's father
            "D": "bottom_right",  # Mother's mother
        }

        for corner_id, corner_pos in corner_mapping.items():
            if corner_id in family_data:
                x, y = self.corner_positions[corner_pos]
                # Grandparents have plenty of space, use traditional positioning
                rotation = self._get_corner_rotation(corner_pos)
                all_positions[corner_id] = (x, y, rotation, family_data[corner_id])

        # Higher generations (A111..., B111..., etc.)
        higher_gen_positions = self._calculate_higher_generation_positions(family_data)
        all_positions.update(higher_gen_positions)

        return all_positions

    def _get_corner_rotation(self, corner_pos: str) -> int:
        """Get rotation for corner-based positioning."""
        corner_rotations = {
            "top_left": -45,  # Father's father
            "bottom_left": 45,  # Father's mother
            "top_right": -135,  # Mother's father
            "bottom_right": 135,  # Mother's mother
        }
        return corner_rotations.get(corner_pos, 0)

    def _calculate_higher_generation_positions(
        self, family_data: Dict[str, Any]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """Calculate positions for higher generations (A111..., B111..., etc.)."""
        positions = {}

        # Group individuals by generation and leading letter
        gen_groups = self._group_by_generation(family_data)

        for gen_num, individuals in gen_groups.items():
            if gen_num >= 3:  # Start from great-grandparents
                gen_positions = self._calculate_generation_positions(
                    gen_num, individuals
                )
                positions.update(gen_positions)

        return positions

    def _group_by_generation(
        self, family_data: Dict[str, Any]
    ) -> Dict[int, List[Tuple[str, Any]]]:
        """Group individuals by generation number."""
        gen_groups = {}

        for name_id, individual in family_data.items():
            if name_id in ["0", "1", "2", "A", "B", "C", "D"]:
                continue  # Handle these separately

            # Parse generation from name ID
            gen_num = self._get_generation_from_name_id(name_id)
            if gen_num:
                if gen_num not in gen_groups:
                    gen_groups[gen_num] = []
                gen_groups[gen_num].append((name_id, individual))

        return gen_groups

    def _get_generation_from_name_id(self, name_id: str) -> int:
        """Extract generation number from name ID."""
        if len(name_id) == 1 and name_id.isalpha():
            return 2  # A, B, C, D are generation 2 (grandparents)
        elif len(name_id) >= 2 and name_id[0].isalpha() and name_id[1:].isdigit():
            return 2 + len(name_id[1:])  # A1 = gen 3, A11 = gen 4, etc.
        return 0

    def _calculate_generation_positions(
        self, gen_num: int, individuals: List[Tuple[str, Any]]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """Calculate positions for a specific generation."""
        positions = {}

        if gen_num <= 7:
            # Generations 3-7: Traditional corner/side positioning
            positions = self._calculate_traditional_positions(gen_num, individuals)
        else:
            # Generations 8+: Sunbeam positioning
            positions = self._calculate_sunbeam_positions(gen_num, individuals)

        return positions

    def _calculate_traditional_positions(
        self, gen_num: int, individuals: List[Tuple[str, Any]]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """Calculate traditional positions for generations 3-7."""
        positions = {}

        # Arrange individuals around the square perimeter
        perimeter_positions = self._get_perimeter_positions(gen_num, len(individuals))

        for i, (name_id, individual) in enumerate(individuals):
            if i < len(perimeter_positions):
                x, y, rotation = perimeter_positions[i]
                positions[name_id] = (x, y, rotation, individual)

        return positions

    def _calculate_sunbeam_positions(
        self, gen_num: int, individuals: List[Tuple[str, Any]]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """Calculate sunbeam positions for generations 8+."""
        positions = {}

        radius = self.gen_radii.get(gen_num, 2400)
        angle_step = 360 / len(individuals)
        start_angle = -180  # Start from left

        for i, (name_id, individual) in enumerate(individuals):
            angle = start_angle + (i * angle_step)
            angle_rad = math.radians(angle)

            x = self.center + radius * math.cos(angle_rad)
            y = self.center + radius * math.sin(angle_rad)
            rotation = angle + 90  # Text points away from center

            positions[name_id] = (int(x), int(y), int(rotation), individual)

        return positions

    def _get_perimeter_positions(
        self, gen_num: int, count: int
    ) -> List[Tuple[int, int, int]]:
        """Get positions along the square perimeter for traditional layout."""
        positions = []

        # Calculate spacing along perimeter
        perimeter = 4 * (self.canvas_size - 200)  # Leave margin from edges
        spacing = perimeter / count

        # Start from top-left corner and go clockwise
        current_distance = 0

        for i in range(count):
            distance = i * spacing

            # Determine which side and position
            side_length = self.canvas_size - 200

            if distance < side_length:
                # Top side
                x = 100 + distance
                y = 100
                rotation = 0
            elif distance < 2 * side_length:
                # Right side
                x = self.canvas_size - 100
                y = 100 + (distance - side_length)
                rotation = 90
            elif distance < 3 * side_length:
                # Bottom side
                x = self.canvas_size - 100 - (distance - 2 * side_length)
                y = self.canvas_size - 100
                rotation = 180
            else:
                # Left side
                x = 100
                y = self.canvas_size - 100 - (distance - 3 * side_length)
                rotation = 270

            positions.append((int(x), int(y), rotation))

        return positions

    def get_special_2gen_text_positions(
        self, parent_id: str
    ) -> Dict[str, Tuple[int, int, int]]:
        """
        Get special text positions for 2nd generation parents.

        For parents in corners:
        - First/last names at 90° angles
        - Middle name at 45° along corner

        Returns:
            Dictionary with positions for first_name, middle_name, last_name
        """
        if parent_id == "1":  # Father
            base_x, base_y = self.parent_positions["father"]
            return {
                "first_name": (base_x - 30, base_y - 30, -45),
                "middle_name": (base_x, base_y, 45),
                "last_name": (base_x + 30, base_y + 30, 45),
            }
        elif parent_id == "2":  # Mother
            base_x, base_y = self.parent_positions["mother"]
            return {
                "first_name": (base_x - 30, base_y + 30, -135),
                "middle_name": (base_x, base_y, -45),
                "last_name": (base_x + 30, base_y - 30, -135),
            }

        return {}


# Example usage and testing
if __name__ == "__main__":
    # Create calculator
    calculator = NameChartPositionCalculator(canvas_size=1950)

    # Example family data with your naming convention
    example_family = {
        "0": "Primary Individual",
        "1": "Father Name",
        "2": "Mother Name",
        "A": "Father's Father",
        "B": "Father's Mother",
        "C": "Mother's Father",
        "D": "Mother's Mother",
        "A1": "Father's Father's Father",
        "A2": "Father's Father's Mother",
        "B1": "Father's Mother's Father",
        "B2": "Father's Mother's Mother",
        "C1": "Mother's Father's Father",
        "C2": "Mother's Father's Mother",
        "D1": "Mother's Mother's Father",
        "D2": "Mother's Mother's Mother",
    }

    # Calculate positions
    positions = calculator.calculate_all_positions(example_family)

    print("NameChart Position Calculator with Your Naming Convention")
    print("=" * 60)

    for name_id, (x, y, rotation, individual) in positions.items():
        print(f"{name_id}: ({x:4d}, {y:4d}) rot:{rotation:3d}° -> {individual}")

    # Show special 2gen text positioning
    print(f"\nSpecial 2gen Text Positioning:")
    print("-" * 30)

    father_text_pos = calculator.get_special_2gen_text_positions("1")
    for text_part, (x, y, rot) in father_text_pos.items():
        print(f"Father {text_part}: ({x:4d}, {y:4d}) rot:{rot:3d}°")

    mother_text_pos = calculator.get_special_2gen_text_positions("2")
    for text_part, (x, y, rot) in mother_text_pos.items():
        print(f"Mother {text_part}: ({x:4d}, {y:4d}) rot:{rot:3d}°")
