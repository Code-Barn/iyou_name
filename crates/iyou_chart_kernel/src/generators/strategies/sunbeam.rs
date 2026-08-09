use crate::core::constants::*;
use crate::core::coordinate_system::rotate_coordinates;
use crate::core::{AncestorData, ChartError, ChartSettings, GenerationOverlay, PersonData};
use crate::generators::specs::SunbeamSpecs;
use crate::generators::strategies::strategy_trait::GenerationStrategyTrait;
use crate::rendering::{TextAbbreviator, TextRenderer};
use magick_rust::{CompositeOperator, DrawingWand, MagickWand, PixelWand};

const LANCZOS_FILTER: u32 = 22;

pub struct SunbeamStrategy {
    generation: u8,
    specs: SunbeamSpecs,
    text_renderer: TextRenderer,
    pub abbreviator: TextAbbreviator,
}

impl SunbeamStrategy {
    pub fn new(generation: u8, settings: &ChartSettings) -> Result<Self, ChartError> {
        if generation >= 6 && generation <= 7 {
            let max_name_length = SunbeamSpecs::new().get_max_name_length(generation);

            Ok(Self {
                generation,
                specs: SunbeamSpecs::new(),
                text_renderer: TextRenderer::new(settings),
                abbreviator: TextAbbreviator::with_max_length(max_name_length),
            })
        } else {
            Err(ChartError::InvalidSettings(format!(
                "SunbeamStrategy only handles generations 6-7, got {}",
                generation
            )))
        }
    }

    fn draw_individual_at_position(
        &self,
        wand: &mut MagickWand,
        individual: &PersonData,
        position: &crate::generators::specs::sunbeam_specs::SunbeamPositionSpec,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        let (final_x, final_y) = rotate_coordinates(
            position.name_position.base_x,
            position.name_position.base_y,
            position.rotation,
            IMAGE_CENTER_X,
            IMAGE_CENTER_Y,
        );

        let display_name = self
            .abbreviator
            .abbreviate(&individual.full_name, position.max_name_length);

        let mut fill_pw = PixelWand::new();
        fill_pw.set_color(&settings.font_color)?;

        let mut draw = DrawingWand::new();
        draw.set_font(&settings.font_family)?;
        draw.set_font_size(position.font_sizes.name);
        draw.set_fill_color(&fill_pw);

        let _name_metrics =
            self.text_renderer
                .get_font_metrics(wand, &display_name, position.font_sizes.name)?;

        draw.draw_annotation(final_x, final_y, &display_name)?;

        if settings.use_outside_stroke {
            let mut stroke_pw = PixelWand::new();
            stroke_pw.set_color(&settings.stroke_color)?;
            let mut stroke_draw = DrawingWand::new();
            stroke_draw.set_font(&settings.font_family)?;
            stroke_draw.set_font_size(position.font_sizes.name);
            stroke_draw.set_fill_color(&stroke_pw);
            stroke_draw.set_stroke_color(&stroke_pw);
            stroke_draw.set_stroke_width(settings.stroke_width);
            stroke_draw.draw_annotation(final_x, final_y, &display_name)?;
            wand.draw_image(&stroke_draw)?;
        }

        wand.draw_image(&draw)?;
        Ok(())
    }

    fn create_previous_strategy(
        &self,
        generation: u8,
        settings: &ChartSettings,
    ) -> Box<dyn GenerationStrategyTrait> {
        match generation {
            1 => Box::new(super::gen1::Gen1Strategy::new(settings)),
            2 => Box::new(super::gen2::Gen2Strategy::new(settings)),
            3 | 4 | 5 => {
                Box::new(super::radial::RadialStrategy::new(generation, settings).unwrap())
            }
            6 | 7 => Box::new(Self::new(generation, settings).unwrap()),
            _ => panic!("Invalid previous generation"),
        }
    }

    fn composite_overlay(
        &self,
        wand: &mut MagickWand,
        overlay_data: &[u8],
        overlay_settings: &GenerationOverlay,
    ) -> Result<(), ChartError> {
        let overlay_wand = MagickWand::new();
        overlay_wand.read_image_blob(overlay_data)?;

        let scaled_width = (1950.0 * overlay_settings.scale) as usize;
        let scaled_height = (1950.0 * overlay_settings.scale) as usize;
        overlay_wand.resize_image(scaled_width, scaled_height, LANCZOS_FILTER);

        let pos_x = ((1950 - scaled_width) / 2) as isize;
        let pos_y = ((1950 - scaled_height) / 2) as isize;

        wand.compose_images(
            &overlay_wand,
            CompositeOperator::Over,
            false,
            pos_x,
            pos_y,
        )?;

        Ok(())
    }
}

impl GenerationStrategyTrait for SunbeamStrategy {
    fn generate(
        &self,
        wand: &mut MagickWand,
        primary: &PersonData,
        ancestors: &AncestorData,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        if ancestors.count() < 8 {
            return Err(ChartError::InvalidSettings(format!(
                "Gen{} requires reasonable ancestor data (at least 8 ancestors)",
                self.generation
            )));
        }

        wand.set_size(1950, 1950)?;
        let mut white = PixelWand::new();
        white.set_color("white")?;
        wand.new_image(1950, 1950, &white)?;

        let positions = self.specs.get_positions(self.generation);

        self.draw_individual_at_position(wand, primary, &positions[0], settings)?;

        for position in &positions[1..] {
            if let Some(individual) = ancestors.get_individual(&position.id) {
                self.draw_individual_at_position(wand, individual, position, settings)?;
            }
        }

        let prev_gen = self.generation - 1;
        let prev_strategy = self.create_previous_strategy(prev_gen, settings);

        let mut overlay_wand = MagickWand::new();
        overlay_wand.set_size(1950, 1950)?;
        let mut transparent = PixelWand::new();
        transparent.set_color("transparent")?;
        overlay_wand.new_image(1950, 1950, &transparent)?;

        prev_strategy.generate(&mut overlay_wand, primary, ancestors, settings)?;

        let overlay_settings = self.specs.get_overlay_settings(self.generation);

        let overlay_blob = overlay_wand.write_image_blob("PNG")?;
        self.composite_overlay(wand, &overlay_blob, &overlay_settings)?;

        Ok(())
    }

    fn generation(&self) -> u8 {
        self.generation
    }

    fn validate_ancestors(&self, ancestors: &AncestorData) -> Result<(), ChartError> {
        if ancestors.count() >= 8 {
            Ok(())
        } else {
            Err(ChartError::InvalidSettings(format!(
                "Gen{} requires at least 8 ancestors",
                self.generation
            )))
        }
    }

    fn overlay_settings(&self) -> GenerationOverlay {
        self.specs.get_overlay_settings(self.generation)
    }

    fn name(&self) -> &'static str {
        match self.generation {
            6 => "Gen6SunbeamStrategy",
            7 => "Gen7SunbeamStrategy",
            _ => "SunbeamStrategy",
        }
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
    fn test_sunbeam_strategy_creation() {
        let settings = test_settings();
        let gen6 = SunbeamStrategy::new(6, &settings).unwrap();
        assert_eq!(gen6.generation(), 6);
        assert_eq!(gen6.name(), "Gen6SunbeamStrategy");
        assert_eq!(gen6.abbreviator.get_max_length(), 15);

        let gen7 = SunbeamStrategy::new(7, &settings).unwrap();
        assert_eq!(gen7.generation(), 7);
        assert_eq!(gen7.name(), "Gen7SunbeamStrategy");
        assert_eq!(gen7.abbreviator.get_max_length(), 12);

        assert!(SunbeamStrategy::new(5, &settings).is_err());
    }

    #[test]
    fn test_overlay_settings() {
        let settings = test_settings();
        assert_eq!(SunbeamStrategy::new(6, &settings).unwrap().overlay_settings().scale, 0.80);
        assert_eq!(SunbeamStrategy::new(7, &settings).unwrap().overlay_settings().scale, 0.85);
    }

    #[test]
    fn test_text_abbreviation() {
        let settings = test_settings();
        let gen6 = SunbeamStrategy::new(6, &settings).unwrap();
        let long_name = "Alexander Hamilton Junior from New York County";
        let abbreviated = gen6.abbreviator.abbreviate(long_name, 15);
        assert!(abbreviated.len() <= 15);
    }
}
