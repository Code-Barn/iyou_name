/// Coordinate system utilities and rotation matrix
use crate::core::constants::{IMAGE_CENTER_X, IMAGE_CENTER_Y};

/// Rotate coordinates around the center point using the standard rotation matrix
pub fn rotate_coordinates(
    dx: f64,
    dy: f64,
    angle_degrees: f64,
    center_x: f64,
    center_y: f64,
) -> (f64, f64) {
    let angle_rad = angle_degrees.to_radians();
    let rotated_x = dx * angle_rad.cos() - dy * angle_rad.sin();
    let rotated_y = dx * angle_rad.sin() + dy * angle_rad.cos();
    (center_x + rotated_x, center_y + rotated_y)
}

/// Default rotation around the image center
pub fn rotate_around_center(dx: f64, dy: f64, angle_degrees: f64) -> (f64, f64) {
    rotate_coordinates(dx, dy, angle_degrees, IMAGE_CENTER_X, IMAGE_CENTER_Y)
}
