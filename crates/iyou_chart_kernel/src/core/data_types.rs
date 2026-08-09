/// Core data structures for the chart generation engine
use serde::{Deserialize, Serialize};

/// Font sizes for different text elements
#[derive(Debug, Clone, Copy)]
pub struct FontSizes {
    pub name: f64,
    pub date: f64,
    pub place: f64,
}

/// 2D position coordinates with optional offsets
#[derive(Debug, Clone, Copy)]
pub struct PositionCoordinates {
    pub base_x: f64,
    pub base_y: f64,
    pub offset_x: f64,
    pub offset_y: f64,
}

/// Flag position and size information
#[derive(Debug, Clone, Copy)]
pub struct FlagPosition {
    pub base_x: f64,
    pub base_y: f64,
    pub rotation: f64,
    pub size: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PersonData {
    pub id: String,
    pub full_name: String,
    pub given_name: String,
    pub surname: String,
    pub birth_date: Option<String>,
    pub birth_place: Option<String>,
    pub death_date: Option<String>,
    pub death_place: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChartSettings {
    pub font_family: String,
    pub font_color: String,
    pub background_color: String,
    pub name_font_size: f64,
    pub date_font_size: f64,
    pub place_font_size: f64,
    pub use_outside_stroke: bool,
    pub stroke_width: f64,
    pub stroke_color: String,
    pub flag_size: u32,
    pub flag_type: String,
}

#[derive(Debug, Clone, Copy)]
pub struct GenerationOverlay {
    pub scale: f64,
    pub position_x: i32,
    pub position_y: i32,
}
