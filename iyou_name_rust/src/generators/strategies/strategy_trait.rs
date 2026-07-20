use crate::core::{AncestorData, ChartError, ChartSettings, GenerationOverlay, PersonData};
/// Core execution trait for generation strategies
/// Defines the common interface for all polymorphic strategies
use magick_rust::MagickWand;

/// Common trait for all generation strategies
pub trait GenerationStrategyTrait: Send + Sync {
    /// Generate chart for this strategy using the provided wand
    /// Receives native borrowed MagickWand buffer for composition chain
    fn generate(
        &self,
        wand: &mut MagickWand,
        primary: &PersonData,
        ancestors: &AncestorData,
        settings: &ChartSettings,
    ) -> Result<(), ChartError>;

    /// Get the generation number this strategy handles
    fn generation(&self) -> u8;

    /// Validate that required ancestor data is present
    fn validate_ancestors(&self, ancestors: &AncestorData) -> Result<(), ChartError>;

    /// Get overlay settings for recursive composition
    fn overlay_settings(&self) -> GenerationOverlay;

    /// Get a descriptive name for this strategy
    fn name(&self) -> &'static str;
}

/// Blanket implementation for boxing strategies
impl GenerationStrategyTrait for Box<dyn GenerationStrategyTrait> {
    fn generate(
        &self,
        wand: &mut MagickWand,
        primary: &PersonData,
        ancestors: &AncestorData,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        self.as_ref().generate(wand, primary, ancestors, settings)
    }

    fn generation(&self) -> u8 {
        self.as_ref().generation()
    }

    fn validate_ancestors(&self, ancestors: &AncestorData) -> Result<(), ChartError> {
        self.as_ref().validate_ancestors(ancestors)
    }

    fn overlay_settings(&self) -> GenerationOverlay {
        self.as_ref().overlay_settings()
    }

    fn name(&self) -> &'static str {
        self.as_ref().name()
    }
}
