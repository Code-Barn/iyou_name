/// Unit tests for coordinate system utilities
/// Verifies that native DrawingWand translations mirror historical 2D coordinate matrices
use approx::assert_relative_eq;
use iyou_chart_kernel::core::constants::{IMAGE_CENTER_X, IMAGE_CENTER_Y};
use iyou_chart_kernel::core::coordinate_system::{rotate_around_center, rotate_coordinates};

#[test]
fn test_rotate_coordinates_exact() {
    // Test 0° rotation (identity)
    let (x, y) = rotate_coordinates(100.0, 50.0, 0.0, 0.0, 0.0);
    assert_relative_eq!(x, 100.0, epsilon = 1e-6);
    assert_relative_eq!(y, 50.0, epsilon = 1e-6);

    // Test 90° rotation around origin
    let (x, y) = rotate_coordinates(100.0, 0.0, 90.0, 0.0, 0.0);
    assert_relative_eq!(x, 0.0, epsilon = 1e-6);
    assert_relative_eq!(y, 100.0, epsilon = 1e-6);

    // Test 180° rotation around origin
    let (x, y) = rotate_coordinates(100.0, 0.0, 180.0, 0.0, 0.0);
    assert_relative_eq!(x, -100.0, epsilon = 1e-6);
    assert_relative_eq!(y, 0.0, epsilon = 1e-6);

    // Test 270° rotation around origin
    let (x, y) = rotate_coordinates(100.0, 0.0, 270.0, 0.0, 0.0);
    assert_relative_eq!(x, 0.0, epsilon = 1e-6);
    assert_relative_eq!(y, -100.0, epsilon = 1e-6);

    // Test rotation around center point (975, 975)
    let (x, y) = rotate_coordinates(100.0, 0.0, 90.0, IMAGE_CENTER_X, IMAGE_CENTER_Y);
    assert_relative_eq!(x, IMAGE_CENTER_X, epsilon = 1e-6);
    assert_relative_eq!(y, IMAGE_CENTER_Y + 100.0, epsilon = 1e-6);
}

#[test]
fn test_rotate_around_center_quadrants() {
    // Test that points map accurately to visual quadrantal centers
    // These tests verify the historical 2D coordinate matrices are preserved

    // 0° rotation - right quadrant
    let (x, y) = rotate_around_center(100.0, 0.0, 0.0);
    assert_relative_eq!(x, IMAGE_CENTER_X + 100.0, epsilon = 1e-6);
    assert_relative_eq!(y, IMAGE_CENTER_Y, epsilon = 1e-6);

    // 90° rotation - top quadrant
    let (x, y) = rotate_around_center(100.0, 0.0, 90.0);
    assert_relative_eq!(x, IMAGE_CENTER_X, epsilon = 1e-6);
    assert_relative_eq!(y, IMAGE_CENTER_Y + 100.0, epsilon = 1e-6);

    // 180° rotation - left quadrant
    let (x, y) = rotate_around_center(100.0, 0.0, 180.0);
    assert_relative_eq!(x, IMAGE_CENTER_X - 100.0, epsilon = 1e-6);
    assert_relative_eq!(y, IMAGE_CENTER_Y, epsilon = 1e-6);

    // 270° rotation - bottom quadrant
    let (x, y) = rotate_around_center(100.0, 0.0, 270.0);
    assert_relative_eq!(x, IMAGE_CENTER_X, epsilon = 1e-6);
    assert_relative_eq!(y, IMAGE_CENTER_Y - 100.0, epsilon = 1e-6);
}

#[test]
fn test_center_constants() {
    // Verify the absolute visual center point constants
    assert_relative_eq!(IMAGE_CENTER_X, 975.0, epsilon = 1e-6);
    assert_relative_eq!(IMAGE_CENTER_Y, 975.0, epsilon = 1e-6);
}

#[test]
fn test_rotation_matrix_orthogonality() {
    // Test that rotation matrices preserve orthogonality
    // Rotating by 360 degrees should return to original position
    let (x, y) = rotate_around_center(123.0, 456.0, 360.0);
    assert_relative_eq!(x, IMAGE_CENTER_X + 123.0, epsilon = 1e-6);
    assert_relative_eq!(y, IMAGE_CENTER_Y + 456.0, epsilon = 1e-6);

    // Test that multiple 90° rotations compose correctly
    let (x1, y1) = rotate_around_center(100.0, 0.0, 90.0);
    let dx = x1 - IMAGE_CENTER_X;
    let dy = y1 - IMAGE_CENTER_Y;
    let (x2, y2) = rotate_coordinates(dx, dy, 90.0, IMAGE_CENTER_X, IMAGE_CENTER_Y);

    // Should be equivalent to 180° rotation
    let (x3, y3) = rotate_around_center(100.0, 0.0, 180.0);
    assert_relative_eq!(x2, x3, epsilon = 1e-6);
    assert_relative_eq!(y2, y3, epsilon = 1e-6);
}
