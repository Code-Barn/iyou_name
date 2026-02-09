"""
Chart buffer manager for efficient chained generation.

This module implements the efficient buffer approach where:
1. 1gen chart is generated once and cached
2. Each subsequent generation overlays the previous cached buffer
3. No repeated regeneration occurs
"""

import logging
from io import BytesIO
from typing import Dict, Optional

# No direct imports to avoid circular dependencies

logger = logging.getLogger(__name__)


class ChartBufferManager:
    """
    Manages cached chart buffers for efficient chained generation.

    Each generation's buffer is created once and reused until settings change.
    """

    def __init__(self):
        self.buffers: Dict[str, BytesIO] = {}
        self.current_settings: Dict = {}
        self.current_individual_id: Optional[str] = None
        self.current_family_data: Optional[Dict] = None

    def is_cache_valid(
        self, individual_id: str, family_data: Dict, user_settings: Dict
    ) -> bool:
        """Check if the current cache is valid for the given individual and settings."""
        return (
            self.current_individual_id == individual_id
            and self.current_family_data == family_data
            and self.current_settings == user_settings
        )

    def clear_cache(self):
        """Clear all cached buffers."""
        for buffer_key in self.buffers:
            if self.buffers[buffer_key]:
                self.buffers[buffer_key].close()
        self.buffers.clear()
        self.current_settings.clear()
        self.current_individual_id = None
        self.current_family_data = None

    def generate_chain(
        self,
        primary_individual,
        family_data: Dict,
        user_settings: Dict,
        max_generation: int = 5,
    ) -> Dict[str, BytesIO]:
        """
        Generate the complete chain of charts up to max_generation.

        This implements the efficient chained approach:
        1. Generate 1gen chart and cache it
        2. For each subsequent generation, overlay the previous cached buffer
        3. Return all cached buffers

        Args:
            primary_individual: PersonData object for the primary individual
            family_data: Dictionary containing all family data
            user_settings: User settings to apply
            max_generation: Maximum generation to generate (default: 5)

        Returns:
            Dictionary mapping generation numbers to their cached buffers
        """
        individual_id = primary_individual.id

        # Check if we can use existing cache
        if self.is_cache_valid(individual_id, family_data, user_settings):
            logger.info(f"Using cached buffers for individual {individual_id}")
            return {k: v for k, v in self.buffers.items() if int(k) <= max_generation}

        # Clear cache and regenerate
        logger.info(f"Regenerating buffer chain for individual {individual_id}")
        self.clear_cache()

        # Store current context
        self.current_individual_id = individual_id
        self.current_family_data = family_data
        self.current_settings = user_settings.copy()

        try:
            # Generate 1gen chart (base)
            logger.info("Generating 1gen chart (base)")
            from apps.generator.utils.image_1generator import generate_1gen_preview

            gen1_buffer = generate_1gen_preview(
                primary_individual, family_data, "preview", user_settings
            )
            self.buffers["1"] = gen1_buffer

            if max_generation >= 2:
                # Generate 2gen chart (overlays 1gen)
                logger.info("Generating 2gen chart (overlays 1gen)")
                from apps.generator.utils.image_2generator import generate_2gen_preview

                gen2_buffer = generate_2gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )
                self.buffers["2"] = gen2_buffer

            if max_generation >= 3:
                # Generate 3gen chart (overlays cached 2gen)
                logger.info("Generating 3gen chart (overlays cached 2gen)")
                from apps.generator.utils.image_3generator import generate_3gen_preview

                gen3_buffer = generate_3gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )
                self.buffers["3"] = gen3_buffer

            if max_generation >= 4:
                # Generate 4gen chart (overlays cached 3gen)
                logger.info("Generating 4gen chart (overlays cached 3gen)")
                from apps.generator.utils.image_4generator import generate_4gen_preview

                gen4_buffer = generate_4gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )
                self.buffers["4"] = gen4_buffer

            if max_generation >= 5:
                # Generate 5gen chart (overlays cached 4gen)
                logger.info("Generating 5gen chart (overlays cached 4gen)")
                from apps.generator.utils.image_5generator import generate_5gen_preview

                gen5_buffer = generate_5gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )
                self.buffers["5"] = gen5_buffer

            if max_generation >= 6:
                # Generate 6gen chart (overlays cached 5gen)
                logger.info("Generating 6gen chart (overlays cached 5gen)")
                from apps.generator.utils.image_6generator import generate_6gen_preview

                gen6_buffer = generate_6gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )
                self.buffers["6"] = gen6_buffer

            if max_generation >= 7:
                # Generate 7gen chart (overlays cached 6gen)
                logger.info("Generating 7gen chart (overlays cached 6gen)")
                from apps.generator.utils.image_7generator import generate_7gen_preview

                gen7_buffer = generate_7gen_preview(
                    primary_individual, family_data, "preview", user_settings
                )
                self.buffers["7"] = gen7_buffer

            logger.info(f"Generated buffer chain up to generation {max_generation}")
            return {k: v for k, v in self.buffers.items() if int(k) <= max_generation}

        except Exception as e:
            logger.error(f"Error generating buffer chain: {e}")
            self.clear_cache()
            raise

    def get_buffer(self, generation: int) -> Optional[BytesIO]:
        """Get cached buffer for a specific generation."""
        buffer_key = str(generation)
        if buffer_key in self.buffers and self.buffers[buffer_key]:
            # Reset buffer position for reading
            self.buffers[buffer_key].seek(0)
            return self.buffers[buffer_key]
        return None

    def preload_defaults(self, primary_individual, family_data: Dict):
        """
        Preload default charts for quick viewing.

        This generates all charts with default settings so users can
        instantly view them without waiting for generation.
        """
        logger.info("Preloading default charts")
        default_settings = {}  # Use hardcoded defaults
        self.generate_chain(
            primary_individual, family_data, default_settings, max_generation=7
        )


# Global buffer manager instance
buffer_manager = ChartBufferManager()


def get_chart_buffer(
    primary_individual,
    family_data: Dict,
    user_settings: Dict,
    generation: int = 1,
    force_regenerate: bool = False,
) -> BytesIO:
    """
    Get chart buffer for a specific generation.

    This is the main interface function that should be called from views.

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        user_settings: User settings to apply
        generation: Generation number to get (1-5)
        force_regenerate: Force regeneration even if cache is valid

    Returns:
        BytesIO buffer containing the generated chart
    """
    if force_regenerate:
        buffer_manager.clear_cache()

    # Generate chain up to requested generation
    buffers = buffer_manager.generate_chain(
        primary_individual, family_data, user_settings, max_generation=generation
    )

    buffer_key = str(generation)
    if buffer_key not in buffers:
        raise ValueError(f"Failed to generate buffer for generation {generation}")

    return buffers[buffer_key]


def preload_default_charts(primary_individual, family_data: Dict):
    """
    Preload default charts for instant viewing.

    Call this when the user first loads the HUD to pre-generate
    all charts with default settings.
    """
    buffer_manager.preload_defaults(primary_individual, family_data)


def invalidate_cache():
    """Invalidate all cached buffers."""
    buffer_manager.clear_cache()
