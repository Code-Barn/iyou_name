//! Utility functions and helpers

/// Validate chart settings
pub fn validate_settings(
    settings: &crate::core::ChartSettings,
) -> Result<(), crate::core::ChartError> {
    if settings.name_font_size <= 0.0 {
        return Err(crate::core::ChartError::InvalidSettings(
            "Name font size must be positive".to_string(),
        ));
    }
    if settings.background_color.is_empty() {
        return Err(crate::core::ChartError::InvalidSettings(
            "Background color cannot be empty".to_string(),
        ));
    }
    Ok(())
}
