"""
Buffer management utilities for family tree generators.

This module provides standardized buffer creation, validation, and management
functions to ensure consistent and reliable buffer handling across all
generation-specific image generators.
"""

import logging
from io import BytesIO
from typing import Optional, Union, BinaryIO
from wand.image import Image

logger = logging.getLogger(__name__)


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
        BytesIO buffer containing the image data

    Raises:
        BufferError: If buffer creation fails
    """
    try:
        buffer = BytesIO()

        # Set quality if specified
        if quality is not None and format_name.upper() in ["JPEG", "JPG"]:
            image.compression_quality = quality

        # Save image to buffer
        image.save(file=buffer)

        # Validate buffer has content
        if buffer.tell() == 0:
            raise BufferError(f"Created buffer is empty for format: {format_name}")

        # Reset position for reading
        buffer.seek(0)

        logger.debug(f"Created {format_name} buffer: {buffer.tell()} bytes")
        return buffer

    except Exception as e:
        logger.error(f"Failed to create {format_name} buffer: {e}")
        raise BufferError(f"Buffer creation failed: {e}")


def validate_buffer(buffer: Optional[BytesIO], buffer_name: str = "buffer") -> BytesIO:
    """
    Validate that a buffer is properly initialized and contains data.

    Args:
        buffer: BytesIO buffer to validate
        buffer_name: Name of the buffer for logging

    Returns:
        Validated buffer (same object if valid)

    Raises:
        BufferError: If buffer validation fails
    """
    if buffer is None:
        raise BufferError(f"Buffer '{buffer_name}' is None")

    if not isinstance(buffer, BytesIO):
        raise BufferError(f"Buffer '{buffer_name}' is not a BytesIO object")

    # Check current position and total size
    current_pos = buffer.tell()
    buffer.seek(0, 2)  # Seek to end
    buffer_size = buffer.tell()
    buffer.seek(current_pos)  # Restore position

    if buffer_size == 0:
        raise BufferError(f"Buffer '{buffer_name}' is empty (0 bytes)")

    logger.debug(
        f"Buffer '{buffer_name}' validated: {buffer_size} bytes at position {current_pos}"
    )
    return buffer


def reset_buffer_position(buffer: BytesIO, buffer_name: str = "buffer") -> BytesIO:
    """
    Reset buffer position to beginning for reading.

    Args:
        buffer: BytesIO buffer to reset
        buffer_name: Name of the buffer for logging

    Returns:
        Buffer with position reset to 0
    """
    validate_buffer(buffer, buffer_name)
    buffer.seek(0)
    logger.debug(f"Reset buffer '{buffer_name}' position to 0")
    return buffer


def get_buffer_contents(buffer: BytesIO, buffer_name: str = "buffer") -> bytes:
    """
    Get raw bytes from buffer with proper position management.

    Args:
        buffer: BytesIO buffer to read from
        buffer_name: Name of the buffer for logging

    Returns:
        Raw bytes from buffer

    Raises:
        BufferError: If buffer read fails
    """
    try:
        validate_buffer(buffer, buffer_name)

        # Save current position
        current_pos = buffer.tell()

        # Read contents
        buffer.seek(0)
        contents = buffer.getvalue()

        # Restore position
        buffer.seek(current_pos)

        if not contents:
            raise BufferError(f"Buffer '{buffer_name}' contains no data")

        logger.debug(f"Read {len(contents)} bytes from buffer '{buffer_name}'")
        return contents

    except Exception as e:
        logger.error(f"Failed to read buffer '{buffer_name}': {e}")
        raise BufferError(f"Buffer read failed: {e}")


def create_image_from_buffer(
    buffer: BytesIO, buffer_name: str = "buffer", resolution: Optional[int] = None
) -> Image:
    """
    Create a Wand Image from buffer with validation.

    Args:
        buffer: BytesIO buffer containing image data
        buffer_name: Name of the buffer for logging
        resolution: Optional resolution for the image

    Returns:
        Wand Image object created from buffer

    Raises:
        BufferError: If image creation fails
    """
    try:
        validate_buffer(buffer, buffer_name)

        # Get buffer contents for blob creation
        buffer_contents = get_buffer_contents(buffer, buffer_name)

        # Create image from blob
        if resolution:
            image = Image(blob=buffer_contents, resolution=resolution)
        else:
            image = Image(blob=buffer_contents)

        logger.debug(
            f"Created image from buffer '{buffer_name}': {image.width}x{image.height}"
        )
        return image

    except Exception as e:
        logger.error(f"Failed to create image from buffer '{buffer_name}': {e}")
        raise BufferError(f"Image creation from buffer failed: {e}")


def safe_buffer_composite(
    base_image: Image,
    overlay_buffer: BytesIO,
    left: int,
    top: int,
    buffer_name: str = "overlay",
) -> Image:
    """
    Safely composite an image from buffer onto a base image.

    Args:
        base_image: Base Wand Image
        overlay_buffer: Buffer containing overlay image
        left: Left position for compositing
        top: Top position for compositing
        buffer_name: Name of the overlay buffer for logging

    Returns:
        Base image with overlay composited

    Raises:
        BufferError: If compositing fails
    """
    try:
        # Create overlay image from buffer
        overlay_image = create_image_from_buffer(overlay_buffer, buffer_name)

        # Perform compositing
        base_image.composite(overlay_image, left=left, top=top)

        logger.debug(
            f"Composited overlay from buffer '{buffer_name}' at ({left}, {top})"
        )
        return base_image

    except Exception as e:
        logger.error(f"Failed to composite overlay from buffer '{buffer_name}': {e}")
        raise BufferError(f"Buffer compositing failed: {e}")


def clone_buffer(buffer: BytesIO, buffer_name: str = "buffer") -> BytesIO:
    """
    Create a safe clone of a buffer.

    Args:
        buffer: Original buffer to clone
        buffer_name: Name of the buffer for logging

    Returns:
        New BytesIO buffer with cloned contents
    """
    try:
        validate_buffer(buffer, buffer_name)

        # Get contents and create new buffer
        contents = get_buffer_contents(buffer, buffer_name)
        cloned_buffer = BytesIO(contents)

        logger.debug(f"Cloned buffer '{buffer_name}': {len(contents)} bytes")
        return cloned_buffer

    except Exception as e:
        logger.error(f"Failed to clone buffer '{buffer_name}': {e}")
        raise BufferError(f"Buffer cloning failed: {e}")


def cleanup_buffer(buffer: Optional[BytesIO], buffer_name: str = "buffer") -> None:
    """
    Clean up buffer resources (close and clear reference).

    Args:
        buffer: Buffer to clean up
        buffer_name: Name of the buffer for logging
    """
    if buffer is not None:
        try:
            buffer.close()
            logger.debug(f"Closed buffer '{buffer_name}'")
        except Exception as e:
            logger.warning(f"Failed to close buffer '{buffer_name}': {e}")


class BufferManager:
    """
    Context manager for standardized buffer lifecycle management.

    Example:
        >>> with BufferManager() as manager:
        ...     buffer = manager.create_buffer(image, "PNG")
        ...     return manager.get_validated_buffer(buffer)
    """

    def __init__(self):
        self.buffers = []
        self.logger = logging.getLogger(f"{__name__}.BufferManager")

    def create_buffer(
        self, image: Image, format_name: str = "PNG", buffer_name: Optional[str] = None
    ) -> BytesIO:
        """Create and track a buffer."""
        buffer_name = buffer_name or f"buffer_{len(self.buffers)}"
        buffer = create_image_buffer(image, format_name)
        self.buffers.append((buffer, buffer_name))
        self.logger.debug(f"Created and tracked buffer '{buffer_name}'")
        return buffer

    def get_validated_buffer(
        self, buffer: BytesIO, buffer_name: str = "buffer"
    ) -> BytesIO:
        """Get validated buffer with position reset."""
        return reset_buffer_position(validate_buffer(buffer, buffer_name), buffer_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up all tracked buffers
        for buffer, buffer_name in self.buffers:
            cleanup_buffer(buffer, buffer_name)
        self.buffers.clear()
        self.logger.debug("Cleaned up all tracked buffers")


# Standardized buffer creation functions for common use cases


def create_preview_buffer(image: Image) -> BytesIO:
    """Create a standard preview PNG buffer."""
    return create_image_buffer(image, "PNG")


def create_pdf_buffer(image: Image) -> BytesIO:
    """Create a standard PDF buffer."""
    return create_image_buffer(image, "PDF")


def create_compatible_buffer(image: Image, template_type: str) -> BytesIO:
    """
    Create buffer based on template type.

    Args:
        image: Wand Image to save
        template_type: 'preview' or 'final'

    Returns:
        Appropriate buffer for the template type
    """
    if template_type == "preview":
        return create_preview_buffer(image)
    elif template_type == "final":
        return create_pdf_buffer(image)
    else:
        raise BufferError(f"Unknown template type: {template_type}")
