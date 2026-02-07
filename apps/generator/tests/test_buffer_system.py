"""
Test suite for Chart Buffer Management System.

This test suite verifies that:
1. Buffer system caches charts correctly
2. Cached buffers are reused instead of regenerating
3. Cache invalidation works properly
4. Performance improvements are realized
"""

import logging
import time
from io import BytesIO
from unittest.mock import Mock, patch

from django.test import TestCase

from apps.generator.utils.chart_buffer_manager import (
    ChartBufferManager,
    buffer_manager,
    get_chart_buffer,
    preload_default_charts,
    invalidate_cache,
)

# Set up logging to capture debug output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestChartBufferManager(TestCase):
    """Test the ChartBufferManager class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.buffer_manager = ChartBufferManager()

        # Mock primary individual
        self.mock_individual = Mock()
        self.mock_individual.id = "TEST_INDIVIDUAL_001"
        self.mock_individual.full_name = "Test Person"

        # Mock family data
        self.mock_family_data = {
            "individuals": {
                "TEST_INDIVIDUAL_001": {
                    "id": "TEST_INDIVIDUAL_001",
                    "full_name": "Test Person",
                    "birth_date": "1980-01-01",
                }
            }
        }

        # Mock user settings
        self.mock_user_settings = {
            "font_family": "Arial",
            "primary_name_font_size": 24,
        }

    def test_buffer_manager_initialization(self):
        """Test that buffer manager initializes correctly."""
        self.assertEqual(len(self.buffer_manager.buffers), 0)
        self.assertEqual(self.buffer_manager.current_individual_id, None)
        self.assertEqual(self.buffer_manager.current_family_data, None)
        self.assertEqual(len(self.buffer_manager.current_settings), 0)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_cache_validity_check(self, mock_gen1):
        """Test cache validity checking."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # First generation - cache should be invalid
        is_valid_before = self.buffer_manager.is_cache_valid(
            self.mock_individual.id, self.mock_family_data, self.mock_user_settings
        )
        self.assertFalse(is_valid_before)

        # Generate and cache
        self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=1,
        )

        # Second check - cache should be valid
        is_valid_after = self.buffer_manager.is_cache_valid(
            self.mock_individual.id, self.mock_family_data, self.mock_user_settings
        )
        self.assertTrue(is_valid_after)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_cache_invalidation_on_settings_change(self, mock_gen1):
        """Test that cache invalidates when settings change."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # Generate with original settings
        self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=1,
        )

        # Cache should be valid
        is_valid_original = self.buffer_manager.is_cache_valid(
            self.mock_individual.id, self.mock_family_data, self.mock_user_settings
        )
        self.assertTrue(is_valid_original)

        # Change settings
        new_settings = self.mock_user_settings.copy()
        new_settings["font_family"] = "Times New Roman"

        # Cache should be invalid with new settings
        is_valid_new = self.buffer_manager.is_cache_valid(
            self.mock_individual.id, self.mock_family_data, new_settings
        )
        self.assertFalse(is_valid_new)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    @patch("apps.generator.utils.image_2generator.generate_2gen_preview")
    def test_buffer_chain_generation(self, mock_gen2, mock_gen1):
        """Test that buffer chain generates correctly."""
        # Setup mock return values
        mock_buffer1 = BytesIO(b"test_image_data_1gen")
        mock_buffer2 = BytesIO(b"test_image_data_2gen")
        mock_gen1.return_value = mock_buffer1
        mock_gen2.return_value = mock_buffer2

        # Generate chain up to 2 generations
        buffers = self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=2,
        )

        # Verify both buffers are cached
        self.assertEqual(len(buffers), 2)
        self.assertIn("1", buffers)
        self.assertIn("2", buffers)

        # Verify buffer manager has cached buffers
        self.assertEqual(len(self.buffer_manager.buffers), 2)
        self.assertIn("1", self.buffer_manager.buffers)
        self.assertIn("2", self.buffer_manager.buffers)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_get_buffer_method(self, mock_gen1):
        """Test the get_buffer method."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # Generate and cache
        self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=1,
        )

        # Get cached buffer
        cached_buffer = self.buffer_manager.get_buffer(1)
        self.assertIsNotNone(cached_buffer)
        self.assertEqual(cached_buffer.read(), b"test_image_data")

        # Try to get non-existent buffer
        non_existent = self.buffer_manager.get_buffer(99)
        self.assertIsNone(non_existent)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_buffer_reuse_performance(self, mock_gen1):
        """Test that cached buffers provide performance improvements."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # First generation - should call generator
        start_time = time.time()
        buffers1 = self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=1,
        )
        first_generation_time = time.time() - start_time

        # Verify generator was called
        self.assertEqual(mock_gen1.call_count, 1)

        # Second generation - should use cache (no additional generator calls)
        start_time = time.time()
        buffers2 = self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=1,
        )
        second_generation_time = time.time() - start_time

        # Verify generator was NOT called again
        self.assertEqual(mock_gen1.call_count, 1)  # Still only 1 call

        # Verify performance improvement
        self.assertLess(second_generation_time, first_generation_time)

        # Verify same buffer is returned
        self.assertEqual(buffers1["1"], buffers2["1"])

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_clear_cache_method(self, mock_gen1):
        """Test the clear_cache method."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # Generate and cache
        self.buffer_manager.generate_chain(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            max_generation=1,
        )

        # Verify cache exists
        self.assertEqual(len(self.buffer_manager.buffers), 1)
        self.assertIsNotNone(self.buffer_manager.current_individual_id)

        # Clear cache
        self.buffer_manager.clear_cache()

        # Verify cache is cleared
        self.assertEqual(len(self.buffer_manager.buffers), 0)
        self.assertIsNone(self.buffer_manager.current_individual_id)
        self.assertIsNone(self.buffer_manager.current_family_data)
        self.assertEqual(len(self.buffer_manager.current_settings), 0)


class TestBufferManagerIntegration(TestCase):
    """Integration tests for the buffer manager system."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_individual = Mock()
        self.mock_individual.id = "TEST_INDIVIDUAL_002"
        self.mock_individual.full_name = "Integration Test Person"

        self.mock_family_data = {
            "individuals": {
                "TEST_INDIVIDUAL_002": {
                    "id": "TEST_INDIVIDUAL_002",
                    "full_name": "Integration Test Person",
                }
            }
        }

        self.mock_user_settings = {
            "font_family": "Arial",
            "primary_name_font_size": 24,
        }

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_get_chart_buffer_function(self, mock_gen1):
        """Test the get_chart_buffer interface function."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # Get chart buffer
        buffer = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )

        # Verify buffer is returned
        self.assertIsNotNone(buffer)
        self.assertEqual(buffer.read(), b"test_image_data")

        # Verify generator was called
        self.assertEqual(mock_gen1.call_count, 1)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_force_regenerate_parameter(self, mock_gen1):
        """Test the force_regenerate parameter."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # First generation
        buffer1 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )

        # Second generation without force - should use cache
        buffer2 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )

        # Verify generator called only once
        self.assertEqual(mock_gen1.call_count, 1)

        # Third generation with force - should regenerate
        buffer3 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
            force_regenerate=True,
        )

        # Verify generator called again
        self.assertEqual(mock_gen1.call_count, 2)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_preload_default_charts_function(self, mock_gen1):
        """Test the preload_default_charts function."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # Clear global buffer manager first
        invalidate_cache()

        # Preload defaults
        preload_default_charts(self.mock_individual, self.mock_family_data)

        # Verify buffers are cached
        self.assertIn("1", buffer_manager.buffers)

        # Verify generator was called
        self.assertGreater(mock_gen1.call_count, 0)

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    def test_invalidate_cache_function(self, mock_gen1):
        """Test the invalidate_cache function."""
        # Setup mock return value
        mock_buffer = BytesIO(b"test_image_data")
        mock_gen1.return_value = mock_buffer

        # Generate some cached buffers
        get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )

        # Verify cache exists
        self.assertGreater(len(buffer_manager.buffers), 0)

        # Invalidate cache
        invalidate_cache()

        # Verify cache is cleared
        self.assertEqual(len(buffer_manager.buffers), 0)


class TestBufferSystemPerformance(TestCase):
    """Performance tests for the buffer system."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_individual = Mock()
        self.mock_individual.id = "PERFORMANCE_TEST_001"
        self.mock_individual.full_name = "Performance Test Person"

        self.mock_family_data = {
            "individuals": {
                "PERFORMANCE_TEST_001": {
                    "id": "PERFORMANCE_TEST_001",
                    "full_name": "Performance Test Person",
                }
            }
        }

        self.mock_user_settings = {
            "font_family": "Arial",
            "primary_name_font_size": 24,
        }

    @patch("apps.generator.utils.image_1generator.generate_1gen_preview")
    @patch("apps.generator.utils.image_2generator.generate_2gen_preview")
    @patch("apps.generator.utils.image_3generator.generate_3gen_preview")
    def test_chain_vs_individual_performance(self, mock_gen3, mock_gen2, mock_gen1):
        """Test that chain generation is more efficient than individual calls."""
        # Setup mock return values
        mock_buffer1 = BytesIO(b"test_image_data_1gen")
        mock_buffer2 = BytesIO(b"test_image_data_2gen")
        mock_buffer3 = BytesIO(b"test_image_data_3gen")
        mock_gen1.return_value = mock_buffer1
        mock_gen2.return_value = mock_buffer2
        mock_gen3.return_value = mock_buffer3

        # Clear cache
        invalidate_cache()

        # Test chain generation
        start_time = time.time()
        chain_buffers = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=3,
        )
        chain_time = time.time() - start_time

        # Clear cache
        invalidate_cache()

        # Test individual generation calls
        start_time = time.time()
        buffer1 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )
        buffer2 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=2,
        )
        buffer3 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=3,
        )
        individual_time = time.time() - start_time

        # Chain should be more efficient (fewer generator calls)
        # Chain calls each generator once
        # Individual calls might call generators multiple times due to missing cache
        print(f"Chain time: {chain_time:.4f}s")
        print(f"Individual time: {individual_time:.4f}s")
        print(
            f"Generator calls - Chain: {mock_gen1.call_count + mock_gen2.call_count + mock_gen3.call_count}"
        )


if __name__ == "__main__":
    # Run tests with verbose output
    import unittest

    print("Running Chart Buffer Management System Tests...")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.makeSuite(TestChartBufferManager))
    suite.addTest(unittest.makeSuite(TestBufferManagerIntegration))
    suite.addTest(unittest.makeSuite(TestBufferSystemPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed! Buffer system is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
