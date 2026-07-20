"""
Mathematical positioning system for NameChart sunbeam layout.

This system calculates positions for names arranged in concentric squares
with sunbeam pattern for outer generations, matching the 4700x4700px
design described by the user.
"""

import math
from typing import List, Tuple, Dict


class SunbeamPositionCalculator:
    """
    Calculate positions for family tree names in sunbeam pattern.

    Design specifications:
    - 4700x4700px canvas for 10gen charts
    - 1950x1950px canvas for 1-7gen charts
    - Concentric square layout
    - Names angle away from center like sunbeams
    - Primary individual labeled '0' at center
    """

    def __init__(self, canvas_size: int = 4700):
        """
        Initialize calculator for given canvas size.

        Args:
            canvas_size: Size of square canvas (4700 for 10gen, 1950 for 1-7gen)
        """
        self.canvas_size = canvas_size
        self.center = canvas_size // 2

        # Design parameters based on canvas size
        if canvas_size == 4700:
            # 10gen parameters
            self.gen_radii = {
                0: 0,  # Primary at center
                1: 300,  # Parents
                2: 600,  # Grandparents
                3: 900,  # Great-grandparents
                4: 1200,  # 4th generation
                5: 1500,  # 5th generation
                6: 1800,  # 6th generation
                7: 2100,  # 7th generation
                8: 2400,  # 8th generation
                9: 2700,  # 9th generation
                10: 3000,  # 10th generation (outer edge)
            }
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
        else:
            # 1-7gen parameters (1950px canvas)
            scale_factor = canvas_size / 4700
            self.gen_radii = {
                gen: int(radius * scale_factor)
                for gen, radius in {
                    0: 0,
                    1: 300,
                    2: 600,
                    3: 900,
                    4: 1200,
                    5: 1500,
                    6: 1800,
                    7: 2100,
                }.items()
            }
            self.font_sizes = {0: 84, 1: 72, 2: 60, 3: 48, 4: 42, 5: 36, 6: 32, 7: 28}

    def calculate_generation_positions(
        self, generation: int, name_count: int
    ) -> List[Tuple[int, int, int, str]]:
        """
        Calculate positions for all names in a generation.

        Args:
            generation: Generation number (0-10)
            name_count: Number of names in this generation

        Returns:
            List of tuples: (x, y, rotation, zone_id)
        """
        if generation == 0:
            # Primary individual at center
            return [(self.center, self.center, 0, "0")]

        positions = []
        radius = self.gen_radii.get(generation, 300)

        # Calculate angular spacing
        if name_count == 2:
            # Parents - simple left/right layout
            angles = [-45, 45]  # Father at -45°, Mother at 45°
        elif name_count == 4:
            # Grandparents - corners
            angles = [-135, -45, 45, 135]
        else:
            # Higher generations - full sunbeam pattern
            angle_span = 360
            angle_step = angle_span / name_count
            start_angle = -angle_span / 2

            angles = [start_angle + (i * angle_step) for i in range(name_count)]

        for i, angle in enumerate(angles):
            # Calculate position
            angle_rad = math.radians(angle)
            x = self.center + radius * math.cos(angle_rad)
            y = self.center + radius * math.sin(angle_rad)

            # Calculate rotation (text points away from center)
            rotation = angle + 90

            # Create zone ID based on your naming convention
            zone_id = self._create_zone_id(generation, i)

            positions.append((int(x), int(y), int(rotation), zone_id))

        return positions

    def _create_zone_id(self, generation: int, index: int) -> str:
        """
        Create zone ID following your naming convention.

        Args:
            generation: Generation number
            index: Index within generation

        Returns:
            Zone ID string
        """
        if generation == 0:
            return "0"

        # Your naming convention appears to be systematic
        # We'll create a simple one that you can customize
        return f"{generation}-{index + 1:03d}"

    def get_all_positions(
        self, family_tree_data: Dict
    ) -> Dict[str, Tuple[int, int, int, str]]:
        """
        Calculate positions for entire family tree.

        Args:
            family_tree_data: Dictionary with generation data

        Returns:
            Dictionary mapping zone_id to (x, y, rotation, individual_data)
        """
        all_positions = {}

        for generation, individuals in family_tree_data.items():
            positions = self.calculate_generation_positions(
                generation, len(individuals)
            )

            for i, (x, y, rotation, zone_id) in enumerate(positions):
                if i < len(individuals):
                    all_positions[zone_id] = (x, y, rotation, individuals[i])

        return all_positions

    def create_svg_template(self, family_tree_data: Dict, output_path: str):
        """
        Create an SVG template with calculated positions.

        Args:
            family_tree_data: Dictionary with generation data
            output_path: Path to save SVG file
        """
        svg_content = f'''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
 "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg version="1.0" xmlns="http://www.w3.org/2000/svg"
 width="{self.canvas_size}.000000pt" height="{self.canvas_size}.000000pt" 
 viewBox="0 0 {self.canvas_size}.000000 {self.canvas_size}.000000"
 preserveAspectRatio="xMidYMid meet">
<metadata>
Created by NameChart Sunbeam Position Calculator
</metadata>
<g transform="translate(0.000000,{self.canvas_size}.000000) scale(0.100000,-0.100000)"
fill="#000000" stroke="none">
'''

        # Add background
        svg_content += f'<rect x="0" y="0" width="{self.canvas_size * 10}" height="{self.canvas_size * 10}" fill="white" stroke="none"/>\n'

        # Add chart structure (concentric squares)
        for gen in range(1, 11):
            if gen in self.gen_radii:
                radius = self.gen_radii[gen] * 10  # Scale for SVG coordinate system
                svg_content += f'<rect x="{self.center * 10 - radius}" y="{self.center * 10 - radius}" width="{radius * 2}" height="{radius * 2}" fill="none" stroke="#cccccc" stroke-width="10"/>\n'

        # Add name placeholders
        for generation, individuals in family_tree_data.items():
            positions = self.calculate_generation_positions(
                generation, len(individuals)
            )
            font_size = self.font_sizes.get(generation, 24) * 10  # Scale for SVG

            for i, (x, y, rotation, zone_id) in enumerate(positions):
                if i < len(individuals):
                    # Transform coordinates for SVG system
                    svg_x = x * 10
                    svg_y = (self.canvas_size - y) * 10  # Flip Y for SVG

                    svg_content += f'''<text id="{zone_id}" x="{svg_x}" y="{svg_y}" 
font-size="{font_size}" text-anchor="middle" font-family="Arial" 
transform="rotate({rotation} {svg_x} {svg_y})">{zone_id}</text>\n'''

        svg_content += "</g>\n</svg>"

        with open(output_path, "w") as f:
            f.write(svg_content)

        print(f"SVG template created: {output_path}")


# Example usage and testing
if __name__ == "__main__":
    # Create calculator for 10gen chart
    calculator = SunbeamPositionCalculator(canvas_size=4700)

    # Example family tree structure
    example_family = {
        0: ["Primary Individual"],  # 1 person
        1: ["Father", "Mother"],  # 2 people
        2: ["Paternal GF", "Paternal GM", "Maternal GF", "Maternal GM"],  # 4 people
        3: [f"GG{i + 1}" for i in range(8)],  # 8 people
        4: [f"GGGG{i + 1}" for i in range(16)],  # 16 people
        5: [f"GGGGG{i + 1}" for i in range(32)],  # 32 people
        6: [f"GGGGGG{i + 1}" for i in range(64)],  # 64 people
        7: [f"GGGGGGG{i + 1}" for i in range(128)],  # 128 people
        8: [f"GGGGGGGG{i + 1}" for i in range(256)],  # 256 people
        9: [f"GGGGGGGGG{i + 1}" for i in range(512)],  # 512 people (would exceed 10gen)
    }

    # Test position calculation for a few generations
    print("Testing position calculations:")
    print("=" * 50)

    for gen in range(0, 4):
        if gen in example_family:
            positions = calculator.calculate_generation_positions(
                gen, len(example_family[gen])
            )
            print(f"\nGeneration {gen} ({len(example_family[gen])} people):")
            for i, (x, y, rotation, zone_id) in enumerate(positions):
                print(f"  {zone_id}: ({x:4d}, {y:4d}) rot:{rotation:3d}°")

    # Create SVG template
    calculator.create_svg_template(
        example_family, "generated_10gen_template.svg"
    )

    print(f"\nSVG template generated for {calculator.canvas_size}px canvas")
