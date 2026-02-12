"""
File content scanning and validation utilities for GEDCOM uploads.
Provides security checks to detect malicious or invalid file content.
"""

import logging
import re
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class FileValidationError(Exception):
    """Exception raised when file validation fails."""

    def __init__(self, message, error_code="VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class MaliciousContentError(Exception):
    """Exception raised when malicious content is detected."""

    def __init__(self, message, threat_type="UNKNOWN"):
        self.message = message
        self.threat_type = threat_type
        super().__init__(self.message)


GEDCOM_HEADER_PATTERN = re.compile(r"^0\s+HEAD", re.IGNORECASE)
GEDCOM_TRAILER_PATTERN = re.compile(r"^0\s+TRLR", re.IGNORECASE)

SUSPICIOUS_PATTERNS = [
    (re.compile(r"<script[^>]*>", re.IGNORECASE), "XSS_SCRIPT_TAG"),
    (re.compile(r"javascript:", re.IGNORECASE), "JAVASCRIPT_PROTOCOL"),
    (re.compile(r"on\w+\s*=", re.IGNORECASE), "EVENT_HANDLER"),
    (re.compile(r"<\?php", re.IGNORECASE), "PHP_CODE"),
    (re.compile(r"<%", re.IGNORECASE), "TEMPLATE_INJECTION"),
    (re.compile(r"eval\s*\(", re.IGNORECASE), "EVAL_FUNCTION"),
    (re.compile(r"exec\s*\(", re.IGNORECASE), "EXEC_FUNCTION"),
    (re.compile(r"system\s*\(", re.IGNORECASE), "SYSTEM_CALL"),
    (re.compile(r"shell_exec", re.IGNORECASE), "SHELL_EXEC"),
    (re.compile(r"base64_decode", re.IGNORECASE), "ENCODED_PAYLOAD"),
    (re.compile(r"UNC_PATH|\\\\", re.IGNORECASE), "PATH_traversal"),
    (re.compile(r"\.\./", re.IGNORECASE), "PATH_traversal"),
    (re.compile(r"%2e%2e%2f", re.IGNORECASE), "ENCODED_PATH_traversal"),
    (re.compile(r"<!DOCTYPE\s+html", re.IGNORECASE), "HTML_DOCUMENT"),
    (re.compile(r"<html[^>]*>", re.IGNORECASE), "HTML_CONTENT"),
    (re.compile(r"<\?xml", re.IGNORECASE), "XML_INJECTION"),
    (re.compile(r"<!ENTITY", re.IGNORECASE), "XXE_INJECTION"),
    (re.compile(r'SYSTEM\s+"', re.IGNORECASE), "XXE_INJECTION"),
]

MAX_HEADER_SIZE = 10 * 1024
MIN_VALID_SIZE = 10
MAX_LINE_LENGTH = 65535


def scan_file_content(
    file_content: bytes, filename: str = "unknown"
) -> Tuple[bool, Optional[str]]:
    """
    Scan file content for malicious patterns.

    Args:
        file_content: The raw file content as bytes
        filename: The name of the file being scanned

    Returns:
        Tuple of (is_safe, threat_type or None)
    """
    try:
        content_str = file_content.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Could not decode file {filename} as UTF-8: {e}")
        content_str = file_content.decode("latin-1", errors="ignore")

    lines = content_str.split("\n")

    if len(lines) < 3:
        logger.warning(
            f"File {filename} too short to be valid GEDCOM ({len(lines)} lines)"
        )
        return False, "FILE_TOO_SHORT"

    first_lines = "\n".join(lines[:50])

    for pattern, threat_type in SUSPICIOUS_PATTERNS:
        if pattern.search(content_str):
            logger.warning(f"Malicious pattern detected in {filename}: {threat_type}")
            return False, threat_type

    if len(content_str) > MAX_HEADER_SIZE * 10:
        if not GEDCOM_HEADER_PATTERN.search(content_str[:MAX_HEADER_SIZE]):
            logger.warning(f"File {filename} missing GEDCOM HEAD marker")
            return False, "INVALID_HEADER"

    return True, None


def validate_gedcom_structure(
    file_content: bytes, filename: str = "unknown"
) -> Tuple[bool, Optional[str]]:
    """
    Validate the basic structure of a GEDCOM file.

    Args:
        file_content: The raw file content as bytes
        filename: The name of the file being validated

    Returns:
        Tuple of (is_valid, error_message or None)
    """
    try:
        content_str = file_content.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Could not decode file {filename}: {e}")
        content_str = file_content.decode("latin-1", errors="ignore")

    lines = content_str.split("\n")

    if len(lines) < 3:
        return False, "File is too small to be a valid GEDCOM file"

    first_line = lines[0].strip()

    if not GEDCOM_HEADER_PATTERN.match(first_line):
        if not first_line.startswith("0 "):
            return (
                False,
                "File does not appear to be a valid GEDCOM file (missing '0 HEAD' header)",
            )

    has_valid_level_numbers = True
    for i, line in enumerate(lines[:100]):
        line = line.strip()
        if not line:
            continue

        parts = line.split(" ", 1)
        if parts and parts[0].isdigit():
            level = int(parts[0])
            if level < 0 or level > 99:
                logger.warning(f"Invalid level number {level} at line {i + 1}")
                has_valid_level_numbers = False
                break

    if not has_valid_level_numbers:
        logger.warning(f"File {filename} contains invalid level numbers")

    for i, line in enumerate(lines):
        if len(line) > MAX_LINE_LENGTH:
            logger.warning(
                f"Line {i + 1} in {filename} exceeds maximum length ({len(line)} chars)"
            )
            return False, f"Line {i + 1} exceeds maximum allowed length"

    return True, None


def validate_uploaded_file(
    file_content: bytes, filename: str = "unknown"
) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive validation of uploaded GEDCOM file.

    Combines content scanning and structure validation.

    Args:
        file_content: The raw file content as bytes
        filename: The name of the file being validated

    Returns:
        Tuple of (is_valid, error_message or None)
    """
    if len(file_content) < MIN_VALID_SIZE:
        logger.warning(f"File {filename} is too small ({len(file_content)} bytes)")
        return False, f"File is too small (minimum {MIN_VALID_SIZE} bytes)"

    is_safe, threat_type = scan_file_content(file_content, filename)
    if not is_safe:
        logger.error(f"Malicious content detected in {filename}: {threat_type}")
        return False, f"File contains potentially malicious content ({threat_type})"

    is_valid, error_message = validate_gedcom_structure(file_content, filename)
    if not is_valid:
        return False, error_message

    return True, None


def get_file_signature(file_content: bytes) -> str:
    """
    Get the file signature/magic bytes for identification.

    Args:
        file_content: The raw file content (first bytes)

    Returns:
        Hex representation of file signature
    """
    return file_content[:16].hex()


def detect_file_type(file_content: bytes) -> str:
    """
    Attempt to detect the actual file type from content.

    Args:
        file_content: The raw file content (first bytes)

    Returns:
        Detected file type or 'unknown'
    """
    signature = get_file_signature(file_content)

    if signature.startswith("efbbbf"):
        return "utf-8_bom"
    elif signature.startswith("ffeeddcc"):
        return "unknown"
    elif b"0 " in file_content[:100]:
        return "gedcom"
    elif b"HEAD" in file_content[:100]:
        return "gedcom"

    try:
        content_str = file_content.decode("utf-8", errors="ignore")
        if "<?xml" in content_str[:100]:
            return "xml"
    except:
        pass

    return "text"
