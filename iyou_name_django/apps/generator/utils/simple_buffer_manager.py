"""
Simplified Chart Buffer Management System.

This is a clean, simple implementation that focuses on reliability over complexity.
"""

import logging
import json
from io import BytesIO
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

from apps.parser.models import PersonData as PersonDataClass
from wand.image import Image


class BufferError(Exception):
    """Custom exception for buffer-related errors."""

    pass


def create_image_buffer(
    image: Image, format_name: str = "PNG", quality: Optional[int] = None
) -> BytesIO:
    """
    Create a standardized image buffer from a Wand Image.

    Args:
        image: Wand Image object to save to buffer
        format_name: Image format (PNG, PDF, etc.)
        quality: Optional quality setting for compression

    Returns:
        BytesIO buffer containing image data

    Raises:
        BufferError: If buffer creation fails
    """
    try:
        buffer = BytesIO()

        # Set quality if specified
        if quality is not None and format_name.upper() in ["JPEG", "JPG"]:
            image.compression_quality = quality

        # Debug: Log image properties before saving
        logger.debug(
            f"[BufferDebug] Image dimensions: {image.width}x{image.height}, "
            f"format: {image.format}, saving as: {format_name}"
        )

        # Save image to buffer
        image.save(file=buffer)

        # Get buffer size before seeking
        buffer_size = buffer.tell()
        logger.debug(f"[BufferDebug] Buffer tell() after save: {buffer_size} bytes")

        # Validate buffer has content
        if buffer_size == 0:
            logger.error(
                f"[BufferDebug] Created buffer is EMPTY (0 bytes) for format: {format_name}. "
                f"Image: {image.width}x{image.height}, format={image.format}"
            )
            raise BufferError(f"Created buffer is empty for format: {format_name}")

        # Reset position for reading
        buffer.seek(0)

        logger.debug(f"Created {format_name} buffer: {buffer_size} bytes")
        return buffer

    except BufferError:
        raise
    except Exception as e:
        logger.error(
            f"[BufferDebug] Failed to create {format_name} buffer: {e}. "
            f"Image dimensions: {image.width if hasattr(image, 'width') else 'N/A'}"
        )
        raise BufferError(f"Buffer creation failed: {e}")


def create_preview_buffer(image: Image) -> BytesIO:
    """Create a standard preview PNG buffer."""
    return create_image_buffer(image, "PNG")


def create_pdf_buffer(image: Image) -> BytesIO:
    """Create a standard PDF buffer."""
    return create_image_buffer(image, "PDF")


class SimpleBufferManager:
    """
    Simple, reliable buffer manager for chart generation.

    Key Features:
    - Basic caching with proper buffer management
    - Settings tracking for cache invalidation
    - Simple generation dependencies
    - No over-engineering
    """

    def __init__(self):
        # Core buffer storage
        self.buffers: Dict[str, BytesIO] = {}

        # Settings tracking
        self.current_settings_hash: Optional[str] = None
        self.current_individual_id: Optional[str] = None

        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info("SimpleBufferManager initialized")

    def _calculate_settings_hash(self, settings: Dict) -> str:
        """Calculate hash of settings for change detection."""
        # Sort keys to ensure consistent hashing
        settings_str = json.dumps(settings, sort_keys=True)
        return str(hash(settings_str))

    def _is_buffer_valid(
        self, generation: int, individual_id: str, settings: Dict
    ) -> bool:
        """Check if cached buffer is still valid."""
        buffer_key = str(generation)

        # Check if buffer exists
        if buffer_key not in self.buffers:
            logger.debug(f"[BufferDebug] No buffer found for generation {generation}")
            return False

        # Check if individual changed
        if self.current_individual_id != individual_id:
            logger.debug(
                f"[BufferDebug] Individual changed: {self.current_individual_id} -> {individual_id}"
            )
            return False

        # Check if settings changed
        current_hash = self._calculate_settings_hash(settings)
        if self.current_settings_hash != current_hash:
            logger.debug(
                f"[BufferDebug] Settings changed: {self.current_settings_hash} -> {current_hash}"
            )
            return False

        logger.debug(f"[BufferDebug] Buffer VALID for generation {generation}")
        return True

    def get_buffer(
        self, generation: int, individual_id: str, settings: Dict
    ) -> Optional[BytesIO]:
        """
        Get cached buffer if valid, otherwise return None.
        """
        if self._is_buffer_valid(generation, individual_id, settings):
            buffer_key = str(generation)
            buffer = self.buffers[buffer_key]

            # Create a fresh copy to avoid closed file issues
            buffer.seek(0)
            buffer_size = buffer.tell()
            buffer.seek(0)
            fresh_buffer = BytesIO(buffer.read())

            self.cache_hits += 1
            logger.debug(
                f"[BufferDebug] Cache HIT for generation {generation}: {buffer_size} bytes"
            )
            return fresh_buffer
        else:
            self.cache_misses += 1
            logger.debug(f"[BufferDebug] Cache MISS for generation {generation}")
            return None

    def store_buffer(
        self, generation: int, individual_id: str, settings: Dict, buffer: BytesIO
    ):
        """
        Store buffer in cache.
        """
        buffer_key = str(generation)

        # Store current context
        self.current_individual_id = individual_id
        self.current_settings_hash = self._calculate_settings_hash(settings)

        # Store buffer (create a copy to avoid external closure issues)
        buffer.seek(0)
        buffer_data = buffer.read()
        buffer_size = len(buffer_data)
        buffer_copy = BytesIO(buffer_data)
        self.buffers[buffer_key] = buffer_copy

        logger.debug(
            f"[BufferDebug] Stored buffer for generation {generation}: {buffer_size} bytes, "
            f"individual_id={individual_id}"
        )

    def invalidate_all(self):
        """Invalidate all cached buffers."""
        for buffer_key in self.buffers:
            if self.buffers[buffer_key]:
                try:
                    self.buffers[buffer_key].close()
                except:
                    pass  # Ignore errors during cleanup

        self.buffers.clear()
        self.current_settings_hash = None
        logger.info("All buffers invalidated")

    def get_stats(self) -> Dict:
        """Get performance statistics."""
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_requests": self.cache_hits + self.cache_misses,
            "cache_hit_rate": self.cache_hits
            / max(1, self.cache_hits + self.cache_misses),
            "cached_buffers": len(self.buffers),
            "current_individual": self.current_individual_id,
        }


# Global instance
simple_buffer_manager = SimpleBufferManager()


def get_chart_buffer(
    primary_individual,
    family_data: Dict,
    user_settings: Dict,
    generation: int = 1,
) -> BytesIO:
    """
    Get chart buffer using simple system.

    Args:
        primary_individual: PersonData object for the primary individual
        family_data: Dictionary containing all family data
        user_settings: User settings to apply
        generation: Generation number to get (1-7)

    Returns:
        BytesIO buffer containing the generated chart
    """
    # Try to get cached buffer
    cached_buffer = simple_buffer_manager.get_buffer(
        generation, primary_individual.id, user_settings
    )

    if cached_buffer:
        logger.info(f"Using cached buffer for generation {generation}")
        return cached_buffer

    # Generate new buffer
    logger.info(f"Generating fresh buffer for generation {generation}")

    # Dynamic import and generation - using prototype generators
    try:
        if generation == 1:
            from apps.generator.utils.prototype.prototype_image_1generator import (
                generate_prototype_1gen_preview,
            )

            generator_func = generate_prototype_1gen_preview
        elif generation == 2:
            from apps.generator.utils.prototype.prototype_image_2generator import (
                generate_prototype_2gen_preview,
            )

            generator_func = generate_prototype_2gen_preview
        elif generation == 3:
            from apps.generator.utils.prototype.prototype_image_3generator import (
                generate_prototype_3gen_preview,
            )

            generator_func = generate_prototype_3gen_preview
        elif generation == 4:
            from apps.generator.utils.prototype.prototype_image_4generator import (
                generate_prototype_4gen_preview,
            )

            generator_func = generate_prototype_4gen_preview
        elif generation == 5:
            from apps.generator.utils.prototype.prototype_image_5generator import (
                generate_prototype_5gen_preview,
            )

            generator_func = generate_prototype_5gen_preview
        elif generation == 6:
            from apps.generator.utils.prototype.prototype_image_6generator import (
                generate_prototype_6gen_preview,
            )

            generator_func = generate_prototype_6gen_preview
        elif generation == 7:
            from apps.generator.utils.prototype.prototype_image_7generator import (
                generate_prototype_7gen_preview,
            )

            generator_func = generate_prototype_7gen_preview
        elif generation == 8:
            from apps.generator.utils.prototype.prototype_image_7generator import (
                generate_prototype_7gen_preview,
            )

            generator_func = (
                lambda primary_individual,
                family_data,
                template,
                user_settings: generate_prototype_7gen_preview(
                    primary_individual, family_data, template, user_settings
                )
            )
        elif generation == 9:
            from apps.generator.utils.prototype.prototype_image_7generator import (
                generate_prototype_7gen_preview,
            )

            generator_func = (
                lambda primary_individual,
                family_data,
                template,
                user_settings: generate_prototype_7gen_preview(
                    primary_individual, family_data, template, user_settings
                )
            )
        elif generation == 10:
            from apps.generator.utils.prototype.prototype_image_7generator import (
                generate_prototype_7gen_preview,
            )

            generator_func = (
                lambda primary_individual,
                family_data,
                template,
                user_settings: generate_prototype_7gen_preview(
                    primary_individual, family_data, template, user_settings
                )
            )
        else:
            raise ValueError(f"Unsupported generation: {generation}")

        # Convert all individuals to PersonData objects for multi-generational charts
        person_data_objects = {}
        for person_id, person_data in family_data.get("individuals", {}).items():
            # If already a PersonData object, use it directly
            if isinstance(person_data, PersonDataClass):
                person_data_objects[person_id] = person_data
            else:
                # Convert dict to PersonData object
                person_data_objects[person_id] = PersonDataClass(**person_data)

        # Update family_data with PersonData objects
        family_data_with_person_objects = family_data.copy()
        family_data_with_person_objects["individuals"] = person_data_objects

        # Generate chart directly
        # All generators expect (primary_individual, family_data, template, user_settings)
        buffer = generator_func(
            primary_individual,
            family_data_with_person_objects,
            "preview",
            user_settings,
        )

        if buffer is None:
            logger.error(
                f"Generator function returned None for generation {generation}"
            )
            raise Exception(f"Failed to generate chart for generation {generation}")

        # Store in cache
        simple_buffer_manager.store_buffer(
            generation, primary_individual.id, user_settings, buffer
        )

        # Return fresh copy
        buffer.seek(0)
        return BytesIO(buffer.read())

    except Exception as e:
        logger.error(f"Error generating chart for generation {generation}: {e}")
        raise


def apply_settings_change(
    primary_individual, family_data: Dict, user_settings: Dict, changed_generation: int
):
    """
    Apply settings changes by invalidating cache.

    Args:
        primary_individual: PersonData object
        family_data: Family data dictionary
        user_settings: New user settings
        changed_generation: Generation where settings were changed
    """
    logger.info(f"Applying settings change from generation {changed_generation}")

    # Simple approach: invalidate all buffers when settings change
    simple_buffer_manager.invalidate_all()

    logger.info("All buffers invalidated due to settings change")


def get_buffer_stats() -> Dict:
    """Get buffer performance statistics."""
    return simple_buffer_manager.get_stats()
