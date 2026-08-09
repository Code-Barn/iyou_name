/// Pixel-perfect constants extracted from Python prototypes
/// These values represent years of tuning and must not be recalculated

// Generation 1 Constants
pub const GEN1_CANVAS_WIDTH: u32 = 1822;
pub const GEN1_CANVAS_HEIGHT: u32 = 1822;
pub const GEN1_BACKGROUND_WIDTH: u32 = 1950;
pub const GEN1_BACKGROUND_HEIGHT: u32 = 1950;
pub const GEN1_COMPOSITE_X: i32 = 300;
pub const GEN1_COMPOSITE_Y: i32 = 570;

// Generation 2 Constants - Parent Positions
pub const GEN2_PARENT_NAME_FONT_SIZE: f64 = 44.0;
pub const GEN2_PARENT_DATE_FONT_SIZE: f64 = 28.0;
pub const GEN2_PARENT_PLACE_FONT_SIZE: f64 = 24.0;
pub const GEN2_OVERLAY_SCALE: f64 = 0.50;

// Outward offset constants for parent positioning
pub const PARENT_FIRST_NAME_BASE_Y: f64 = 1759.0;
pub const PARENT_MIDDLE_NAME_BASE_X: f64 = 1625.0;
pub const PARENT_MIDDLE_NAME_BASE_Y: f64 = 1625.0;
pub const PARENT_MIDDLE_NAME_ROTATION: f64 = -45.0;
pub const PARENT_LAST_NAME_BASE_X: f64 = 1759.0;
pub const PARENT_LAST_NAME_BASE_Y: f64 = 975.0;

// Birth/Death info positions
pub const PARENT_BIRTH_DATE_BASE_Y: f64 = 1565.0;
pub const PARENT_BIRTH_PLACE_BASE_Y: f64 = 1890.0;
pub const PARENT_DEATH_DATE_BASE_X: f64 = 1565.0;
pub const PARENT_DEATH_DATE_BASE_Y: f64 = 975.0;
pub const PARENT_DEATH_PLACE_BASE_X: f64 = 1890.0;
pub const PARENT_DEATH_PLACE_BASE_Y: f64 = 975.0;

// Flag positioning constants
pub const FLAG_BASE_OFFSET_X: f64 = 609.0;
pub const FLAG_BASE_OFFSET_Y: f64 = 609.0;
pub const FLAG_ROTATION: f64 = -45.0;

// Coordinate system constants
pub const IMAGE_CENTER_X: f64 = 975.0;
pub const IMAGE_CENTER_Y: f64 = 975.0;
pub const CANVAS_WIDTH: u32 = 1950;
pub const CANVAS_HEIGHT: u32 = 1950;
pub const RESOLUTION: f64 = 300.0;
