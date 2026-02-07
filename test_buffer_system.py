#!/usr/bin/env python3
"""
Simple test script to verify buffer system functionality.

Run this script to test if the buffer system is working correctly
before integrating with the HUD.
"""

import os
import sys
import django
from unittest.mock import Mock, patch

# Setup Django
sys.path.append("/home/user/CODE_BASE/namechart")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "namechart.settings")
django.setup()

from apps.generator.utils.chart_buffer_manager import buffer_manager, get_chart_buffer


def test_buffer_system():
    """Test the buffer system with mocked generators."""
    print("🧪 Testing Chart Buffer Management System...")
    print("=" * 50)

    # Create mock individual
    mock_individual = Mock()
    mock_individual.id = "TEST_001"
    mock_individual.full_name = "Test Person"

    # Mock family data
    mock_family_data = {
        "individuals": {"TEST_001": {"id": "TEST_001", "full_name": "Test Person"}}
    }

    # Mock user settings
    mock_settings = {
        "font_family": "Arial",
        "primary_name_font_size": 24,
    }

    print("📊 Test 1: Buffer Manager Initialization")
    print(f"   Initial buffers: {len(buffer_manager.buffers)}")
    print(f"   Current individual: {buffer_manager.current_individual_id}")
    assert len(buffer_manager.buffers) == 0
    assert buffer_manager.current_individual_id is None
    print("   ✅ Initialization test passed")

    print("\n📊 Test 2: Cache Generation with Mocks")

    # Mock the generators to avoid actual image generation
    with (
        patch(
            "apps.generator.utils.image_1generator.generate_1gen_preview"
        ) as mock_gen1,
        patch(
            "apps.generator.utils.image_2generator.generate_2gen_preview"
        ) as mock_gen2,
    ):
        from io import BytesIO

        mock_buffer1 = BytesIO(b"mock_1gen_data")
        mock_buffer2 = BytesIO(b"mock_2gen_data")
        mock_gen1.return_value = mock_buffer1
        mock_gen2.return_value = mock_buffer2

        # Generate chain up to 2 generations
        print("   Generating buffer chain...")
        buffers = buffer_manager.generate_chain(
            mock_individual, mock_family_data, mock_settings, max_generation=2
        )

        print(f"   Generated buffers: {len(buffers)}")
        print(f"   Cached buffers: {len(buffer_manager.buffers)}")
        print(f"   Generator 1 calls: {mock_gen1.call_count}")
        print(f"   Generator 2 calls: {mock_gen2.call_count}")

        assert len(buffers) == 2
        assert len(buffer_manager.buffers) == 2
        assert mock_gen1.call_count == 1
        assert mock_gen2.call_count == 1
        print("   ✅ Cache generation test passed")

    print("\n📊 Test 3: Cache Reuse (Performance Test)")

    with (
        patch(
            "apps.generator.utils.image_1generator.generate_1gen_preview"
        ) as mock_gen1,
        patch(
            "apps.generator.utils.image_2generator.generate_2gen_preview"
        ) as mock_gen2,
    ):
        from io import BytesIO

        mock_buffer1 = BytesIO(b"mock_1gen_data")
        mock_buffer2 = BytesIO(b"mock_2gen_data")
        mock_gen1.return_value = mock_buffer1
        mock_gen2.return_value = mock_buffer2

        import time

        # First generation (should use cache)
        start_time = time.time()
        buffers1 = buffer_manager.generate_chain(
            mock_individual, mock_family_data, mock_settings, max_generation=2
        )
        first_time = time.time() - start_time

        # Second generation (should use cache, no new generator calls)
        start_time = time.time()
        buffers2 = buffer_manager.generate_chain(
            mock_individual, mock_family_data, mock_settings, max_generation=2
        )
        second_time = time.time() - start_time

        print(f"   First generation time: {first_time:.4f}s")
        print(f"   Second generation time: {second_time:.4f}s")
        print(f"   Generator 1 calls: {mock_gen1.call_count}")
        print(f"   Generator 2 calls: {mock_gen2.call_count}")

        # Should be no new generator calls for second generation
        assert mock_gen1.call_count == 0
        assert mock_gen2.call_count == 0
        assert second_time < first_time
        print("   ✅ Cache reuse test passed")

    print("\n📊 Test 4: Get Buffer Method")

    # Test getting individual buffers
    buffer_1 = buffer_manager.get_buffer(1)
    buffer_2 = buffer_manager.get_buffer(2)
    buffer_99 = buffer_manager.get_buffer(99)

    print(f"   Buffer 1 exists: {buffer_1 is not None}")
    print(f"   Buffer 2 exists: {buffer_2 is not None}")
    print(f"   Buffer 99 exists: {buffer_99 is not None}")

    assert buffer_1 is not None
    assert buffer_2 is not None
    assert buffer_99 is None
    print("   ✅ Get buffer test passed")

    print("\n📊 Test 5: Cache Invalidation")

    # Change settings to invalidate cache
    new_settings = mock_settings.copy()
    new_settings["font_family"] = "Times New Roman"

    is_valid = buffer_manager.is_cache_valid(
        mock_individual.id, mock_family_data, new_settings
    )

    print(f"   Cache valid with new settings: {is_valid}")
    assert not is_valid
    print("   ✅ Cache invalidation test passed")

    print("\n📊 Test 6: Clear Cache")

    buffer_manager.clear_cache()

    print(f"   Buffers after clear: {len(buffer_manager.buffers)}")
    print(f"   Current individual after clear: {buffer_manager.current_individual_id}")

    assert len(buffer_manager.buffers) == 0
    assert buffer_manager.current_individual_id is None
    print("   ✅ Clear cache test passed")

    print("\n🎉 All tests passed! Buffer system is working correctly.")
    print("=" * 50)

    return True


def test_interface_functions():
    """Test the public interface functions."""
    print("\n🔧 Testing Interface Functions...")
    print("=" * 30)

    # Create mock data
    mock_individual = Mock()
    mock_individual.id = "INTERFACE_TEST_001"
    mock_individual.full_name = "Interface Test Person"

    mock_family_data = {
        "individuals": {
            "INTERFACE_TEST_001": {
                "id": "INTERFACE_TEST_001",
                "full_name": "Interface Test Person",
            }
        }
    }

    mock_settings = {"font_family": "Arial"}

    with patch(
        "apps.generator.utils.image_1generator.generate_1gen_preview"
    ) as mock_gen1:
        from io import BytesIO

        mock_buffer = BytesIO(b"interface_test_data")
        mock_gen1.return_value = mock_buffer

        # Test get_chart_buffer function
        print("📊 Testing get_chart_buffer()...")
        buffer = get_chart_buffer(
            mock_individual, mock_family_data, mock_settings, generation=1
        )

        assert buffer is not None
        assert buffer.read() == b"interface_test_data"
        print("   ✅ get_chart_buffer() works")

        # Test force_regenerate
        print("📊 Testing force_regenerate...")
        initial_calls = mock_gen1.call_count

        buffer2 = get_chart_buffer(
            mock_individual,
            mock_family_data,
            mock_settings,
            generation=1,
            force_regenerate=True,
        )

        # Should have called generator again due to force_regenerate
        assert mock_gen1.call_count > initial_calls
        print("   ✅ force_regenerate works")

    print("🎉 Interface functions working correctly!")
    return True


if __name__ == "__main__":
    try:
        # Run buffer system tests
        test_buffer_system()

        # Run interface function tests
        test_interface_functions()

        print("\n" + "=" * 60)
        print("🚀 ALL TESTS PASSED!")
        print("The buffer system is ready for integration.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
