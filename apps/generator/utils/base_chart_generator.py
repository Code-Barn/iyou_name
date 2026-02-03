"""
Base chart generator using SVG template positioning system.

This provides the foundation for all generation-specific generators
using the mathematical sunbeam positioning system.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any
from io import BytesIO

from django.conf import settings
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image

from apps.generator.utils.name_utils import get_name_display_info
from apps.generator.utils.sunbeam_position_calculator import SunbeamPositionCalculator


class BaseChartGenerator(ABC):
    """
    Base class for all family tree chart generators.

    Provides common functionality for positioning, rendering,
    and styling using the SVG template system.
    """

    def __init__(self, generation_count: int, canvas_size: int = 1950):
        """
        Initialize base generator.

        Args:
            generation_count: Number of generations this generator handles
            canvas_size: Canvas size (1950 for 1-7gen, 4700 for 8-10gen)
        """
        self.generation_count = generation_count
        self.canvas_size = canvas_size
        self.position_calculator = SunbeamPositionCalculator(canvas_size)

        # Default styling (can be overridden by user settings)
        self.default_colors = {
            "background": "#FFFFFF",
            "stroke": "#000000",
            "font": "#000000",
            "birth": "#000000",
            "birth_place": "#000000",
            "death": "#000000",
            "death_place": "#000000",
        }

        self.default_fonts = {
            "family": "Arial",
            "sizes": self.position_calculator.font_sizes,
        }

    @abstractmethod
    def get_template_path(self) -> str:
        """Get the path to the background template image."""
        pass

    @abstractmethod
    def extract_family_data(
        self, primary_individual, family_data
    ) -> Dict[int, List[Any]]:
        """Extract family data organized by generation."""
        pass

    def apply_user_settings(self, user_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply user settings to override defaults.

        Args:
            user_settings: Dictionary of user settings

        Returns:
            Merged settings dictionary
        """
        settings = {
            "colors": self.default_colors.copy(),
            "fonts": self.default_fonts.copy(),
            "positions": {},
        }

        # Apply color settings
        for key, default_value in self.default_colors.items():
            setting_key = (
                f"primary_{key}_color"
                if key == "background"
                else f"primary_{key}_color"
            )
            if setting_key in user_settings:
                settings["colors"][key] = user_settings[setting_key]

        # Apply font settings
        if "font_family" in user_settings:
            settings["fonts"]["family"] = user_settings["font_family"]

        # Apply font size settings
        for gen in range(self.generation_count + 1):
            if gen == 0:  # Primary individual
                size_key = f"primary_name_font_size"
                if size_key in user_settings:
                    settings["fonts"]["sizes"][gen] = int(user_settings[size_key])

        return settings

    def calculate_all_positions(
        self, family_data: Dict[int, List[Any]]
    ) -> Dict[str, Tuple[int, int, int, Any]]:
        """
        Calculate positions for all individuals in the family tree.

        Args:
            family_data: Dictionary mapping generation to list of individuals

        Returns:
            Dictionary mapping zone_id to (x, y, rotation, individual)
        """
        all_positions = {}

        for generation, individuals in family_data.items():
            if generation <= self.generation_count:
                positions = self.position_calculator.calculate_generation_positions(
                    generation, len(individuals)
                )

                for i, (x, y, rotation, zone_id) in enumerate(positions):
                    if i < len(individuals):
                        all_positions[zone_id] = (x, y, rotation, individuals[i])

        return all_positions

    def render_individual(
        self,
        draw: Drawing,
        individual: Any,
        x: int,
        y: int,
        rotation: int,
        settings: Dict[str, Any],
        generation: int,
    ) -> None:
        """
        Render a single individual at the specified position.

        Args:
            draw: Wand Drawing context
            individual: Individual data object
            x, y: Position coordinates
            rotation: Text rotation angle
            settings: Rendering settings
            generation: Generation number
        """
        # Get name display info
        name_info = get_name_display_info(individual.full_name)

        # Set font properties
        font_size = settings["fonts"]["sizes"].get(generation, 24)
        draw.font = settings["fonts"]["family"]
        draw.font_size = font_size
        draw.fill_color = Color(settings["colors"]["font"])

        # Apply rotation and translation
        draw.push()
        draw.translate(x, y)
        draw.rotate(rotation)

        # Draw name (multiline)
        lines = name_info["display_text"].split("\n")
        line_height = font_size * 1.2
        start_y = -(len(lines) - 1) * line_height / 2

        for i, line in enumerate(lines):
            line_y = start_y + (i * line_height)
            draw.text(0, line_y, line)

        draw.pop()

    def generate_chart(
        self, primary_individual, family_data, template="preview", user_settings=None
    ) -> BytesIO:
        """
        Generate the complete family tree chart.

        Args:
            primary_individual: Primary individual data
            family_data: Complete family data
            template: Template type ('preview' or 'final')
            user_settings: User customization settings

        Returns:
            BytesIO buffer containing the generated chart
        """
        # Apply user settings
        settings = self.apply_user_settings(user_settings or {})

        # Extract family data by generation
        family_by_generation = self.extract_family_data(primary_individual, family_data)

        # Calculate positions for all individuals
        all_positions = self.calculate_all_positions(family_by_generation)

        # Load background template
        template_path = self.get_template_path()

        with Image(filename=template_path, resolution=300) as img:
            # Create drawing context
            with Drawing() as draw:
                # Set initial properties
                draw.fill_color = Color(settings["colors"]["font"])
                draw.stroke_color = Color(settings["colors"]["stroke"])
                draw.stroke_width = 0.5

                # Render each individual
                for zone_id, (x, y, rotation, individual) in all_positions.items():
                    generation = self._get_generation_from_zone_id(zone_id)
                    self.render_individual(
                        draw, individual, x, y, rotation, settings, generation
                    )

                # Apply drawing to image
                draw.draw(img)

            # Convert to appropriate format
            if template == "preview":
                buffer = BytesIO()
                img.save(buffer, format="png")
                buffer.seek(0)
                return buffer
            else:  # final
                buffer = BytesIO()
                img.save(buffer, format="pdf")
                buffer.seek(0)
                return buffer

    def _get_generation_from_zone_id(self, zone_id: str) -> int:
        """Extract generation number from zone ID."""
        if zone_id == "0":
            return 0
        return int(zone_id.split("-")[0])


class Generation1Generator(BaseChartGenerator):
    """Generator for 1-generation charts."""

    def __init__(self):
        super().__init__(generation_count=0, canvas_size=1950)

    def get_template_path(self) -> str:
        return os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "1GEN_PREVIEW.png",
        )

    def extract_family_data(
        self, primary_individual, family_data
    ) -> Dict[int, List[Any]]:
        return {0: [primary_individual]}


class Generation2Generator(BaseChartGenerator):
    """Generator for 2-generation charts."""

    def __init__(self):
        super().__init__(generation_count=1, canvas_size=1950)

    def get_template_path(self) -> str:
        return os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "2GEN_PREVIEW.png",
        )

    def extract_family_data(
        self, primary_individual, family_data
    ) -> Dict[int, List[Any]]:
        result = {0: [primary_individual]}

        # Add parents if available
        parents = []
        if hasattr(family_data, "father") and family_data.father:
            parents.append(family_data.father)
        if hasattr(family_data, "mother") and family_data.mother:
            parents.append(family_data.mother)

        if parents:
            result[1] = parents

        return result


class Generation10Generator(BaseChartGenerator):
    """Generator for 10-generation charts (full sunbeam layout)."""

    def __init__(self):
        super().__init__(generation_count=9, canvas_size=4700)

    def get_template_path(self) -> str:
        return os.path.join(
            settings.BASE_DIR,
            "apps/hud/static/hud/images/preview_image_templates",
            "10GEN_PREVIEW.png",
        )

    def extract_family_data(
        self, primary_individual, family_data
    ) -> Dict[int, List[Any]]:
        # This would need to be implemented based on your family data structure
        # For now, return a placeholder
        result = {0: [primary_individual]}

        # TODO: Extract all 10 generations from family_data
        # This would involve traversing up the family tree

        return result


# Factory function for creating generators
def create_generator(generation_count: int) -> BaseChartGenerator:
    """
    Factory function to create appropriate generator.

    Args:
        generation_count: Number of generations to generate

    Returns:
        BaseChartGenerator instance
    """
    generators = {
        1: Generation1Generator,
        2: Generation2Generator,
        10: Generation10Generator,
    }

    generator_class = generators.get(generation_count, Generation1Generator)
    return generator_class()
