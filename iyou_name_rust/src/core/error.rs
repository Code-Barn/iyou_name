/// Custom error types for the chart generation engine
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ChartError {
    #[error("Magick error: {0}")]
    MagickError(#[from] magick_rust::MagickError),

    #[error("Invalid coordinate: {0}")]
    InvalidCoordinate(String),

    #[error("Font metrics error: {0}")]
    FontMetricsError(String),

    #[error("Image composition error: {0}")]
    CompositionError(String),

    #[error("Invalid settings: {0}")]
    InvalidSettings(String),

    #[error("Environment not initialized: ImageMagick must be initialized first")]
    EnvironmentNotInitialized,
}
