use crate::core::{AncestorData, ChartError, ChartSettings, PersonData};
use crate::generators::strategies::{
    Gen1Strategy, Gen2Strategy, GenerationStrategyTrait, RadialStrategy, SunbeamStrategy,
};
use magick_rust::{MagickWand, PixelWand};
use std::collections::HashMap;

pub struct UnifiedChartGenerator {
    settings: ChartSettings,
    strategies: HashMap<u8, Box<dyn GenerationStrategyTrait>>,
}

impl UnifiedChartGenerator {
    pub fn new(settings: ChartSettings) -> Self {
        let mut strategies: HashMap<u8, Box<dyn GenerationStrategyTrait>> = HashMap::new();

        strategies.insert(1, Box::new(Gen1Strategy::new(&settings)));
        strategies.insert(2, Box::new(Gen2Strategy::new(&settings)));
        strategies.insert(3, Box::new(RadialStrategy::new(3, &settings).unwrap()));
        strategies.insert(4, Box::new(RadialStrategy::new(4, &settings).unwrap()));
        strategies.insert(5, Box::new(RadialStrategy::new(5, &settings).unwrap()));
        strategies.insert(6, Box::new(SunbeamStrategy::new(6, &settings).unwrap()));
        strategies.insert(7, Box::new(SunbeamStrategy::new(7, &settings).unwrap()));

        Self {
            settings,
            strategies,
        }
    }

    pub fn generate(
        &self,
        generation: u8,
        primary: &PersonData,
        ancestors: &AncestorData,
    ) -> Result<Vec<u8>, ChartError> {
        let strategy = self.strategies.get(&generation).ok_or_else(|| {
            ChartError::InvalidSettings(format!("Generation {} not supported", generation))
        })?;

        let mut wand = MagickWand::new();
        wand.set_size(1950, 1950)?;
        let mut bg = PixelWand::new();
        bg.set_color("white")?;
        wand.new_image(1950, 1950, &bg)?;

        strategy.generate(&mut wand, primary, ancestors, &self.settings)?;

        wand.write_image_blob("PNG").map_err(ChartError::from)
    }

    pub fn get_strategy(&self, generation: u8) -> Option<&Box<dyn GenerationStrategyTrait>> {
        self.strategies.get(&generation)
    }

    pub fn is_supported(&self, generation: u8) -> bool {
        self.strategies.contains_key(&generation)
    }

    pub fn supported_generations(&self) -> Vec<u8> {
        self.strategies.keys().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::ChartSettings;

    fn test_settings() -> ChartSettings {
        ChartSettings {
            font_family: "Arial".to_string(),
            font_color: "black".to_string(),
            background_color: "white".to_string(),
            name_font_size: 74.0,
            date_font_size: 52.0,
            place_font_size: 48.0,
            use_outside_stroke: false,
            stroke_width: 4.0,
            stroke_color: "white".to_string(),
            flag_size: 666,
            flag_type: "birth".to_string(),
        }
    }

    #[test]
    fn test_unified_generator_creation() {
        let generator = UnifiedChartGenerator::new(test_settings());
        assert_eq!(generator.supported_generations().len(), 7);
        for gen in 1..=7 {
            assert!(generator.is_supported(gen));
        }
        assert!(!generator.is_supported(8));
    }

    #[test]
    fn test_strategy_access() {
        let generator = UnifiedChartGenerator::new(test_settings());

        let gen1_strategy = generator.get_strategy(1).unwrap();
        assert_eq!(gen1_strategy.name(), "Gen1Strategy");
        assert_eq!(gen1_strategy.generation(), 1);

        let gen2_strategy = generator.get_strategy(2).unwrap();
        assert_eq!(gen2_strategy.name(), "Gen2Strategy");
        assert_eq!(gen2_strategy.generation(), 2);
    }
}
