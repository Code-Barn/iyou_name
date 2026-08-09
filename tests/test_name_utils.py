"""
Tests for name parsing utilities.

This module tests the name parsing functionality that handles
edge cases like missing middle names across all generators.
"""

import pytest
from apps.generator.utils.name_utils import (
    parse_name_parts,
    format_name_multiline,
    get_name_display_info,
)


class TestNameParsing:
    """Test name parsing functionality for various edge cases."""

    def test_parse_name_parts_two_part_name(self):
        """Test parsing of names with first and last name only."""
        first, middle, last = parse_name_parts("John Doe")
        assert first == "John"
        assert middle == ""
        assert last == "Doe"

    def test_parse_name_parts_three_part_name(self):
        """Test parsing of names with first, middle, and last name."""
        first, middle, last = parse_name_parts("John Michael Smith")
        assert first == "John"
        assert middle == "Michael"
        assert last == "Smith"

    def test_parse_name_parts_single_name(self):
        """Test parsing of names with only first name."""
        first, middle, last = parse_name_parts("John")
        assert first == "John"
        assert middle == ""
        assert last == ""

    def test_parse_name_parts_empty_name(self):
        """Test parsing of empty name strings."""
        first, middle, last = parse_name_parts("")
        assert first == ""
        assert middle == ""
        assert last == ""

    def test_parse_name_parts_multiple_middle_names(self):
        """Test parsing of names with multiple middle names."""
        first, middle, last = parse_name_parts("John Michael Edward Smith")
        assert first == "John"
        assert middle == "Michael"  # Only first middle name
        assert last == "Smith"

    def test_parse_name_parts_with_spaces(self):
        """Test parsing of names with extra spaces."""
        first, middle, last = parse_name_parts("  John  Doe  ")
        assert first == "John"
        assert middle == ""
        assert last == "Doe"

    def test_parse_name_parts_hyphenated_names(self):
        """Test parsing of names with hyphens."""
        first, middle, last = parse_name_parts("Mary-Jane Smith")
        assert first == "Mary-Jane"
        assert middle == ""
        assert last == "Smith"


class TestNameFormatting:
    """Test name formatting functionality."""

    def test_format_name_multiline_two_part(self):
        """Test multiline formatting of two-part names."""
        result = format_name_multiline("John", "", "Doe")
        assert result == "John\nDoe"

    def test_format_name_multiline_three_part(self):
        """Test multiline formatting of three-part names."""
        result = format_name_multiline("John", "Michael", "Smith")
        assert result == "John\nMichael\nSmith"

    def test_format_name_multiline_single_part(self):
        """Test multiline formatting of single-part names."""
        result = format_name_multiline("John", "", "")
        assert result == "John"

    def test_format_name_multiline_all_empty(self):
        """Test multiline formatting of empty names."""
        result = format_name_multiline("", "", "")
        assert result == ""

    def test_format_name_multiline_ignores_empty_parts(self):
        """Test that empty parts are ignored in multiline formatting."""
        result = format_name_multiline("John", "", "Smith")
        assert result == "John\nSmith"
        assert result != "John\n\nSmith"


class TestNameDisplayInfo:
    """Test complete name display information functionality."""

    def test_get_name_display_info_two_part(self):
        """Test complete display info for two-part names."""
        info = get_name_display_info("John Doe")
        expected = {
            "first_name": "John",
            "middle_name": "",
            "last_name": "Doe",
            "display_text": "John\nDoe",
        }
        assert info == expected

    def test_get_name_display_info_three_part(self):
        """Test complete display info for three-part names."""
        info = get_name_display_info("John Michael Smith")
        expected = {
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Smith",
            "display_text": "John\nMichael\nSmith",
        }
        assert info == expected

    def test_get_name_display_info_single_part(self):
        """Test complete display info for single-part names."""
        info = get_name_display_info("John")
        expected = {
            "first_name": "John",
            "middle_name": "",
            "last_name": "",
            "display_text": "John",
        }
        assert info == expected


class TestRegressionCases:
    """Test regression cases for known issues."""

    def test_duplicate_last_name_bug_fixed(self):
        """
        Regression test for the duplicate last name bug.
        Before fix: "John Doe" would show "John\nDoe\nDoe"
        After fix: "John Doe" should show "John\nDoe"
        """
        info = get_name_display_info("John Doe")
        display_text = info["display_text"]

        # Count occurrences of "Doe" in display text
        doe_count = display_text.count("Doe")
        assert doe_count == 1, (
            f"Expected 1 occurrence of 'Doe', got {doe_count}. Display text: '{display_text}'"
        )

        # Verify the structure
        lines = display_text.split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}. Lines: {lines}"
        assert lines[0] == "John"
        assert lines[1] == "Doe"

    def test_no_empty_lines_in_display(self):
        """
        Regression test to ensure no empty lines in display text.
        """
        test_cases = [
            ("John Doe", ["John", "Doe"]),
            ("John", ["John"]),
            ("John Michael Smith", ["John", "Michael", "Smith"]),
            ("", []),
        ]

        for full_name, expected_lines in test_cases:
            info = get_name_display_info(full_name)
            display_text = info["display_text"]

            if display_text:
                lines = display_text.split("\n")
                # Ensure no empty lines
                assert all(line.strip() for line in lines), (
                    f"Empty line found in display for '{full_name}': {lines}"
                )
                assert lines == expected_lines, (
                    f"Lines mismatch for '{full_name}'. Expected: {expected_lines}, Got: {lines}"
                )
            else:
                assert expected_lines == [], (
                    f"Expected empty lines for empty name, got: {expected_lines}"
                )


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_name_with_numbers(self):
        """Test parsing names with numbers."""
        first, middle, last = parse_name_parts("John Smith II")
        assert first == "John"
        assert middle == "Smith"
        assert last == "II"

    def test_name_with_apostrophes(self):
        """Test parsing names with apostrophes."""
        first, middle, last = parse_name_parts("O'Connor Smith")
        assert first == "O'Connor"
        assert middle == ""
        assert last == "Smith"

    def test_very_long_name(self):
        """Test parsing of very long names."""
        long_name = "John Michael Edward Robert William Smith"
        first, middle, last = parse_name_parts(long_name)
        assert first == "John"
        assert middle == "Michael"
        assert last == "Smith"

    def test_name_with_only_spaces(self):
        """Test parsing of name with only spaces."""
        first, middle, last = parse_name_parts("   ")
        assert first == ""
        assert middle == ""
        assert last == ""


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
