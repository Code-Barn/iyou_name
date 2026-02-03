"""
NameChart positioning system with correct triangular quadrant layout.

This system implements the user's corrected specifications:
- Square chart divided into 4 triangular quadrants by diagonal lines
- Concentric squares create triangular wedges within each quadrant
- Naming convention: 0, 1, 2, A, B, C, D, A1111111, etc.
"""

import math
from typing import List, Tuple, Dict, Any


class NameChartQuadrantCalculator:
    """
    Calculate positions for family tree names in triangular quadrant layout.

    Layout:
    - Square chart with diagonal lines corner-to-corner creating 4 triangular quadrants
    - Concentric squares create triangular wedges within each quadrant
    - Primary individual (0) at center
    - Parents (1, 2) in their respective quadrants
    - Higher generations in triangular wedges along diagonals
    """

    def __init__(self, canvas_size: int = 1950):
        """
        Initialize calculator for given canvas size.

        Args:
            canvas_size: Size of square canvas (1950 for 1-7gen, 4700 for 8-10gen)
        """
        self.canvas_size = canvas_size
        self.center = canvas_size // 2

        # Define the 4 triangular quadrants
        self.quadrants = {
            "top_right": {  # Mother's father's side (C)
                "angle_range": (-90, 0),
                "center_angle": -45,
                "color": "#FF6B6B",
            },
            "bottom_right": {  # Mother's mother's side (D)
                "angle_range": (0, 90),
                "center_angle": 45,
                "color": "#4ECDC4",
            },
            "bottom_left": {  # Father's mother's side (B)
                "angle_range": (90, 180),
                "center_angle": 135,
                "color": "#45B7D1",
            },
            "top_left": {  # Father's father's side (A)
                "angle_range": (180, 270),
                "center_angle": 225,
                "color": "#96CEB4",
            },
        }

        # Canvas-specific parameters
        if canvas_size == 4700:
            # 10gen parameters
            self.quadrant_radii = {
                1: 400,  # Parents
                2: 800,  # Grandparents
                3: 1200,  # Great-grandparents
                4: 1600,  # 4th generation
                5: 2000,  # 5th generation
                6: 2400,  # 6th generation
                7: 2800,  # 7th generation
                8: 3200,  # 8th generation
                9: 3600,  # 9th generation
                10: 4000,  # 10th generation
            }
        else:
            # 1-7gen parameters (1950px canvas)
            scale_factor = canvas_size / 4700
            self.quadrant_radii = {
                gen: int(radius * scale_factor)
                for gen, radius in {
                    1: 400,
                    2: 800,
                    3: 1200,
                    4: 1600,
                    5: 2000,
                    6: 2400,
                    7: 2800,
                }.items()
            }

        # Font sizes
        self.font_sizes = {
            0: 84,  # Primary
            1: 72,  # Parents
            2: 60,  # Grandparents
            3: 48,  # Great-grandparents
            4: 42,  # 4th gen
            5: 36,  # 5th gen
            6: 32,  # 6th gen
            7: 28,  # 7th gen
            8: 24,  # 8th gen
            9: 20,  # 9th gen
            10: 18,  # 10th gen
        }

    def calculate_all_positions(
        self, family_data: Dict[str, Any]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """
        Calculate positions for all individuals using triangular quadrant layout.

        Args:
            family_data: Dictionary with individuals keyed by naming convention

        Returns:
            Dictionary mapping name_id to (x, y, rotation, individual)
        """
        all_positions = {}

        # Primary individual (0) - center
        if "0" in family_data:
            all_positions["0"] = (self.center, self.center, 0, family_data["0"])

        # Parents (1, 2) - in their respective quadrants
        if "1" in family_data:  # Father - bottom left quadrant
            x, y, rotation = self._get_quadrant_position("bottom_left", 1, 0)
            all_positions["1"] = (x, y, rotation, family_data["1"])

        if "2" in family_data:  # Mother - top right quadrant
            x, y, rotation = self._get_quadrant_position("top_right", 1, 0)
            all_positions["2"] = (x, y, rotation, family_data["2"])

        # Grandparents (A, B, C, D) - in their respective quadrants
        quadrant_mapping = {
            "A": "top_left",  # Father's father
            "B": "bottom_left",  # Father's mother
            "C": "top_right",  # Mother's father
            "D": "bottom_right",  # Mother's mother
        }

        for corner_id, quadrant in quadrant_mapping.items():
            if corner_id in family_data:
                x, y, rotation = self._get_quadrant_position(quadrant, 2, 0)
                all_positions[corner_id] = (x, y, rotation, family_data[corner_id])

        # Higher generations (A111..., B111..., etc.)
        higher_gen_positions = self._calculate_higher_generation_positions(family_data)
        all_positions.update(higher_gen_positions)

        return all_positions

    def _get_quadrant_position(
        self, quadrant: str, generation: int, index: int = 0
    ) -> Tuple[int, int, int]:
        """
        Get position within a specific quadrant.

        Args:
            quadrant: Quadrant name ('top_left', 'top_right', 'bottom_left', 'bottom_right')
            generation: Generation number
            index: Index within generation (for multiple people per quadrant)

        Returns:
            Tuple of (x, y, rotation)
        """
        quadrant_info = self.quadrants[quadrant]
        radius = self.quadrant_radii.get(generation, 400)

        # Calculate base angle for this quadrant
        if generation == 1 and index == 0:
            # Parents get center position of their quadrant
            angle = quadrant_info["center_angle"]
        else:
            # Higher generations get positioned within the quadrant
            angle_range = quadrant_info["angle_range"]
            if generation == 2:
                # Grandparents - center of quadrant
                angle = quadrant_info["center_angle"]
            else:
                # Higher generations - spread within quadrant
                angle_span = angle_range[1] - angle_range[0]
                angle = angle_range[0] + (angle_span / 2)

        # Convert to radians and calculate position
        angle_rad = math.radians(angle)
        x = self.center + radius * math.cos(angle_rad)
        y = self.center + radius * math.sin(angle_rad)

        # Text rotation - point toward center for readability
        rotation = angle + 180

        return (int(x), int(y), int(rotation))

    def _calculate_higher_generation_positions(
        self, family_data: Dict[str, Any]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """Calculate positions for higher generations (A111..., B111..., etc.)."""
        positions = {}

        # Group individuals by quadrant and generation
        quadrant_groups = self._group_by_quadrant_and_generation(family_data)

        for quadrant, generations in quadrant_groups.items():
            for gen_num, individuals in generations.items():
                if gen_num >= 3:  # Start from great-grandparents
                    gen_positions = self._calculate_quadrant_generation_positions(
                        quadrant, gen_num, individuals
                    )
                    positions.update(gen_positions)

        return positions

    def _group_by_quadrant_and_generation(
        self, family_data: Dict[str, Any]
    ) -> Dict[str, Dict[int, List[Tuple[str, Any]]]]:
        """Group individuals by quadrant and generation."""
        quadrant_groups = {
            "top_left": {},
            "top_right": {},
            "bottom_left": {},
            "bottom_right": {},
        }

        # Mapping from name prefix to quadrant
        quadrant_mapping = {
            "A": "top_left",
            "B": "bottom_left",
            "C": "top_right",
            "D": "bottom_right",
        }

        for name_id, individual in family_data.items():
            if name_id in ["0", "1", "2"]:
                continue  # Handle these separately

            # Determine quadrant from name prefix
            if len(name_id) > 0 and name_id[0] in quadrant_mapping:
                quadrant = quadrant_mapping[name_id[0]]
                gen_num = self._get_generation_from_name_id(name_id)

                if quadrant not in quadrant_groups:
                    quadrant_groups[quadrant] = {}
                if gen_num not in quadrant_groups[quadrant]:
                    quadrant_groups[quadrant][gen_num] = []

                quadrant_groups[quadrant][gen_num].append((name_id, individual))

        return quadrant_groups

    def _get_generation_from_name_id(self, name_id: str) -> int:
        """Extract generation number from name ID."""
        if len(name_id) == 1 and name_id.isalpha():
            return 2  # A, B, C, D are generation 2 (grandparents)
        elif len(name_id) >= 2 and name_id[0].isalpha() and name_id[1:].isdigit():
            return 2 + len(name_id[1:])  # A1 = gen 3, A11 = gen 4, etc.
        return 0

    def _calculate_quadrant_generation_positions(
        self, quadrant: str, gen_num: int, individuals: List[Tuple[str, Any]]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """Calculate positions for individuals within a specific quadrant and generation."""
        positions = {}

        quadrant_info = self.quadrants[quadrant]
        radius = self.quadrant_radii.get(gen_num, 400)

        # Spread individuals within the quadrant's triangular wedge
        angle_range = quadrant_info["angle_range"]
        angle_span = angle_range[1] - angle_range[0]

        # For multiple individuals, spread them within the quadrant
        if len(individuals) == 1:
            # Single individual gets center of quadrant
            angle = quadrant_info["center_angle"]
        else:
            # Multiple individuals spread within the quadrant
            angle_step = angle_span / len(individuals)
            start_angle = angle_range[0] + (angle_step / 2)

            for i, (name_id, individual) in enumerate(individuals):
                angle = start_angle + (i * angle_step)
                angle_rad = math.radians(angle)
                x = self.center + radius * math.cos(angle_rad)
                y = self.center + radius * math.sin(angle_rad)

                # Text rotation - point toward center for readability
                rotation = angle + 180

                positions[name_id] = (int(x), int(y), int(rotation), individual)

            return positions

        # Single individual positioning
        angle_rad = math.radians(angle)
        x = self.center + radius * math.cos(angle_rad)
        y = self.center + radius * math.sin(angle_rad)
        rotation = angle + 180

        name_id, individual = individuals[0]
        positions[name_id] = (int(x), int(y), int(rotation), individual)

        return positions

    def get_special_2gen_text_positions(
        self, parent_id: str
    ) -> Dict[str, Tuple[int, int, int]]:
        """
        Get special text positions for 2nd generation parents in triangular quadrants.

        For parents in triangular quadrants:
        - Text oriented toward center for readability
        - First/middle/last names stacked appropriately

        Returns:
            Dictionary with positions for name parts
        """
        if parent_id == "1":  # Father - bottom left quadrant
            base_x, base_y, base_rotation = self._get_quadrant_position(
                "bottom_left", 1, 0
            )
            return {
                "first_name": (base_x, base_y - 20, base_rotation),
                "middle_name": (base_x, base_y, base_rotation),
                "last_name": (base_x, base_y + 20, base_rotation),
            }
        elif parent_id == "2":  # Mother - top right quadrant
            base_x, base_y, base_rotation = self._get_quadrant_position(
                "top_right", 1, 0
            )
            return {
                "first_name": (base_x, base_y - 20, base_rotation),
                "middle_name": (base_x, base_y, base_rotation),
                "last_name": (base_x, base_y + 20, base_rotation),
            }

        return {}

    def get_quadrant_info(self) -> Dict[str, Dict]:
        """Get information about all quadrants for debugging/visualization."""
        return self.quadrants


# Example usage and testing
if __name__ == "__main__":
    # Create calculator
    calculator = NameChartQuadrantCalculator(canvas_size=1950)

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

    print("NameChart Quadrant Calculator - Triangular Layout")
    print("=" * 60)

    # Group by quadrant for display
    quadrant_groups = {}
    for name_id, (x, y, rotation, individual) in positions.items():
        # Determine quadrant for display
        if name_id == "0":
            quadrant = "Center"
        elif name_id == "1":
            quadrant = "Bottom Left (Father)"
        elif name_id == "2":
            quadrant = "Top Right (Mother)"
        elif name_id in ["A"]:
            quadrant = "Top Left (Father's Father)"
        elif name_id in ["B"]:
            quadrant = "Bottom Left (Father's Mother)"
        elif name_id in ["C"]:
            quadrant = "Top Right (Mother's Father)"
        elif name_id in ["D"]:
            quadrant = "Bottom Right (Mother's Mother)"
        elif name_id.startswith("A"):
            quadrant = "Top Left (Father's Line)"
        elif name_id.startswith("B"):
            quadrant = "Bottom Left (Father's Line)"
        elif name_id.startswith("C"):
            quadrant = "Top Right (Mother's Line)"
        elif name_id.startswith("D"):
            quadrant = "Bottom Right (Mother's Line)"
        else:
            quadrant = "Unknown"

        if quadrant not in quadrant_groups:
            quadrant_groups[quadrant] = []
        quadrant_groups[quadrant].append((name_id, x, y, rotation, individual))

    # Display by quadrant
    for quadrant, individuals in quadrant_groups.items():
        print(f"\n{quadrant}:")
        print("-" * 40)
        for name_id, x, y, rotation, individual in individuals:
            print(f"  {name_id}: ({x:4d}, {y:4d}) rot:{rotation:3d}° -> {individual}")

    # Show quadrant information
    print(f"\nQuadrant Information:")
    print("-" * 20)
    for quad_name, quad_info in calculator.get_quadrant_info().items():
        print(
            f"{quad_name}: {quad_info['angle_range']}°, center: {quad_info['center_angle']}°"
        )
