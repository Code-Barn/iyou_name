"""
Test suite for the SimpleBufferManager chart buffer system.

This test suite verifies that:
1. The buffer manager caches generated charts correctly
2. Cached buffers are reused instead of regenerating
3. Cache invalidation works when the individual or settings change
4. The get_chart_buffer integration layer drives the prototype generators
"""

import logging
from io import BytesIO
from unittest.mock import Mock, patch

from django.test import TestCase

from apps.generator.utils.simple_buffer_manager import (
    SimpleBufferManager,
    apply_settings_change,
    create_image_buffer,
    get_buffer_stats,
    get_chart_buffer,
    simple_buffer_manager,
)

# Set up logging to capture debug output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestSimpleBufferManager(TestCase):
    """Test the SimpleBufferManager class functionality."""

    def setUp(self):
        self.manager = SimpleBufferManager()
        self.individual_id = "TEST_INDIVIDUAL_001"
        self.settings = {"font_family": "Arial", "primary_name_font_size": 24}

    def test_manager_initialization(self):
        self.assertEqual(len(self.manager.buffers), 0)
        self.assertIsNone(self.manager.current_individual_id)
        self.assertIsNone(self.manager.current_settings_hash)
        self.assertEqual(self.manager.cache_hits, 0)
        self.assertEqual(self.manager.cache_misses, 0)

    def test_store_and_get_buffer(self):
        self.manager.store_buffer(
            1, self.individual_id, self.settings, BytesIO(b"test_image_data")
        )
        cached = self.manager.get_buffer(1, self.individual_id, self.settings)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.read(), b"test_image_data")

    def test_get_missing_buffer_returns_none(self):
        self.assertIsNone(
            self.manager.get_buffer(1, self.individual_id, self.settings)
        )

    def test_cache_invalidated_when_individual_changes(self):
        self.manager.store_buffer(
            1, self.individual_id, self.settings, BytesIO(b"test_image_data")
        )
        self.assertIsNone(
            self.manager.get_buffer(1, "OTHER_INDIVIDUAL", self.settings)
        )

    def test_cache_invalidated_when_settings_change(self):
        self.manager.store_buffer(
            1, self.individual_id, self.settings, BytesIO(b"test_image_data")
        )
        new_settings = dict(self.settings)
        new_settings["font_family"] = "Times New Roman"
        self.assertIsNone(self.manager.get_buffer(1, self.individual_id, new_settings))

    def test_multiple_generations_cached_independently(self):
        self.manager.store_buffer(
            1, self.individual_id, self.settings, BytesIO(b"gen1_data")
        )
        self.manager.store_buffer(
            2, self.individual_id, self.settings, BytesIO(b"gen2_data")
        )
        self.assertEqual(len(self.manager.buffers), 2)
        self.assertEqual(
            self.manager.get_buffer(2, self.individual_id, self.settings).read(),
            b"gen2_data",
        )

    def test_invalidate_all_clears_cache(self):
        self.manager.store_buffer(
            1, self.individual_id, self.settings, BytesIO(b"test_image_data")
        )
        self.manager.invalidate_all()
        self.assertEqual(len(self.manager.buffers), 0)
        self.assertIsNone(self.manager.current_settings_hash)

    def test_get_stats_tracks_hits_and_misses(self):
        self.manager.store_buffer(
            1, self.individual_id, self.settings, BytesIO(b"test_image_data")
        )
        self.manager.get_buffer(1, self.individual_id, self.settings)
        self.manager.get_buffer(2, self.individual_id, self.settings)
        stats = self.manager.get_stats()
        self.assertEqual(stats["cache_hits"], 1)
        self.assertEqual(stats["cache_misses"], 1)
        self.assertEqual(stats["total_requests"], 2)
        self.assertEqual(stats["cached_buffers"], 1)


class TestGetChartBuffer(TestCase):
    """Test the get_chart_buffer integration layer."""

    def setUp(self):
        self.mock_individual = Mock()
        self.mock_individual.id = "TEST_INDIVIDUAL_002"
        self.mock_individual.full_name = "Integration Test Person"

        self.mock_family_data = {
            "individuals": {
                "TEST_INDIVIDUAL_002": {
                    "id": "TEST_INDIVIDUAL_002",
                    "full_name": "Integration Test Person",
                    "given_name": "Integration",
                    "surname": "Person",
                }
            }
        }

        self.mock_user_settings = {
            "font_family": "Arial",
            "primary_name_font_size": 24,
        }

    def tearDown(self):
        simple_buffer_manager.invalidate_all()

    @patch(
        "apps.generator.utils.prototype.prototype_image_1generator."
        "generate_prototype_1gen_preview"
    )
    def test_get_chart_buffer_generates_and_caches(self, mock_gen1):
        mock_gen1.return_value = BytesIO(b"test_image_data")

        buffer = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )

        self.assertIsNotNone(buffer)
        self.assertEqual(buffer.read(), b"test_image_data")
        mock_gen1.assert_called_once()
        # Generator is invoked with (individual, family_data, "preview", settings)
        self.assertEqual(mock_gen1.call_args.args[2], "preview")

    @patch(
        "apps.generator.utils.prototype.prototype_image_1generator."
        "generate_prototype_1gen_preview"
    )
    def test_second_call_reuses_cache(self, mock_gen1):
        mock_gen1.return_value = BytesIO(b"test_image_data")

        get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )
        buffer2 = get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )

        self.assertEqual(buffer2.read(), b"test_image_data")
        mock_gen1.assert_called_once()

    @patch(
        "apps.generator.utils.prototype.prototype_image_1generator."
        "generate_prototype_1gen_preview"
    )
    def test_settings_change_forces_regeneration(self, mock_gen1):
        mock_gen1.return_value = BytesIO(b"test_image_data")

        get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            self.mock_user_settings,
            generation=1,
        )
        new_settings = dict(self.mock_user_settings)
        new_settings["font_family"] = "Times New Roman"
        get_chart_buffer(
            self.mock_individual,
            self.mock_family_data,
            new_settings,
            generation=1,
        )

        self.assertEqual(mock_gen1.call_count, 2)

    def test_unsupported_generation_raises(self):
        with self.assertRaises(ValueError):
            get_chart_buffer(
                self.mock_individual,
                self.mock_family_data,
                self.mock_user_settings,
                generation=99,
            )

    def test_apply_settings_change_invalidates_cache(self):
        simple_buffer_manager.store_buffer(
            1, self.mock_individual.id, self.mock_user_settings, BytesIO(b"x")
        )
        apply_settings_change(
            self.mock_individual, self.mock_family_data, self.mock_user_settings, 1
        )
        self.assertEqual(len(simple_buffer_manager.buffers), 0)

    def test_get_buffer_stats(self):
        stats = get_buffer_stats()
        self.assertIn("cache_hits", stats)
        self.assertIn("cache_misses", stats)
        self.assertIn("total_requests", stats)


class TestCreateImageBuffer(TestCase):
    """Test the create_image_buffer helper."""

    def test_creates_buffer_from_image(self):
        img = Mock()
        img.width = 100
        img.height = 200
        img.format = "PNG"
        img.save = Mock(side_effect=lambda file: file.write(b"png-data"))

        buffer = create_image_buffer(img, "PNG")
        self.assertEqual(buffer.read(), b"png-data")

    def test_empty_buffer_raises(self):
        img = Mock()
        img.width = 100
        img.height = 200
        img.format = "PNG"
        img.save = Mock()

        from apps.generator.utils.simple_buffer_manager import BufferError

        with self.assertRaises(BufferError):
            create_image_buffer(img, "PNG")
