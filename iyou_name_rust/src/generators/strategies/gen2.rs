use crate::core::constants::*;
use crate::core::{AncestorData, ChartError, ChartSettings, GenerationOverlay, PersonData};
use crate::generators::strategies::strategy_trait::GenerationStrategyTrait;
use crate::rendering::text_renderer::TextRenderer;
use magick_rust::{CompositeOperator, DrawingWand, MagickWand, PixelWand};

const LANCZOS_FILTER: u32 = 22;

struct Gen2Specs {
    parent_name_font_size: f64,
    parent_date_font_size: f64,
    parent_place_font_size: f64,
    parent_first_name_base_y: f64,
    parent_middle_name_base_x: f64,
    parent_middle_name_base_y: f64,
    parent_middle_name_rotation: f64,
    parent_last_name_base_x: f64,
    parent_last_name_base_y: f64,
    overlay_scale: f64,
    composite_x: i32,
    composite_y: i32,
}

impl Gen2Specs {
    fn new() -> Self {
        Self {
            parent_name_font_size: 44.0,
            parent_date_font_size: 28.0,
            parent_place_font_size: 24.0,
            parent_first_name_base_y: 1759.0,
            parent_middle_name_base_x: 1625.0,
            parent_middle_name_base_y: 1625.0,
            parent_middle_name_rotation: -45.0,
            parent_last_name_base_x: 1759.0,
            parent_last_name_base_y: 975.0,
            overlay_scale: 0.50,
            composite_x: 300,
            composite_y: 570,
        }
    }

    pub fn get_parent_offset(&self, rotation: f64) -> (f64, f64) {
        match rotation {
            0.0 => (0.0, self.parent_first_name_base_y - IMAGE_CENTER_Y),
            180.0 => (0.0, IMAGE_CENTER_Y - self.parent_first_name_base_y),
            _ => (0.0, 0.0),
        }
    }
}

pub struct Gen2Strategy {
    specs: Gen2Specs,
    text_renderer: TextRenderer,
}

impl Gen2Strategy {
    pub fn new(settings: &ChartSettings) -> Self {
        Self {
            specs: Gen2Specs::new(),
            text_renderer: TextRenderer::new(settings),
        }
    }

    fn draw_parent(
        &self,
        wand: &mut MagickWand,
        individual: &PersonData,
        rotation: f64,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        let (name_x, name_y) = self.specs.get_parent_offset(rotation);

        let mut fill_pw = PixelWand::new();
        fill_pw.set_color(&settings.font_color)?;
        let mut draw = DrawingWand::new();
        draw.set_font(&settings.font_family)?;
        draw.set_font_size(self.specs.parent_name_font_size);
        draw.set_fill_color(&fill_pw);

        draw.draw_annotation(name_x, name_y, &individual.full_name)?;

        if settings.use_outside_stroke {
            let mut stroke_pw = PixelWand::new();
            stroke_pw.set_color(&settings.stroke_color)?;
            let mut stroke_draw = DrawingWand::new();
            stroke_draw.set_font(&settings.font_family)?;
            stroke_draw.set_font_size(self.specs.parent_name_font_size);
            stroke_draw.set_fill_color(&stroke_pw);
            stroke_draw.set_stroke_color(&stroke_pw);
            stroke_draw.set_stroke_width(settings.stroke_width);
            stroke_draw.draw_annotation(name_x, name_y, &individual.full_name)?;
            wand.draw_image(&stroke_draw)?;
        }

        wand.draw_image(&draw)?;
        Ok(())
    }

    fn composite_overlay(
        &self,
        wand: &mut MagickWand,
        overlay_wand: &MagickWand,
    ) -> Result<(), ChartError> {
        let overlay_copy = overlay_wand.clone();

        let scaled_width = (1950.0 * self.specs.overlay_scale) as usize;
        let scaled_height = (1950.0 * self.specs.overlay_scale) as usize;
        overlay_copy.resize_image(scaled_width, scaled_height, LANCZOS_FILTER);

        let pos_x = ((1950 - scaled_width) / 2) as isize;
        let pos_y = ((1950 - scaled_height) / 2) as isize;

        wand.compose_images(&overlay_copy, CompositeOperator::Over, false, pos_x, pos_y)?;

        Ok(())
    }
}

impl GenerationStrategyTrait for Gen2Strategy {
    fn generate(
        &self,
        wand: &mut MagickWand,
        primary: &PersonData,
        ancestors: &AncestorData,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        ancestors.validate_for_generation(2)?;

        wand.set_size(CANVAS_WIDTH as usize, CANVAS_HEIGHT as usize)?;
        let mut white_color = PixelWand::new();
        white_color.set_color("white")?;
        wand.new_image(CANVAS_WIDTH as usize, CANVAS_HEIGHT as usize, &white_color)?;

        let gen1_strategy = super::gen1::Gen1Strategy::new(settings);
        let mut overlay_wand = MagickWand::new();
        overlay_wand.set_size(1950, 1950)?;
        let mut transparent_color = PixelWand::new();
        transparent_color.set_color("transparent")?;
        overlay_wand.new_image(1950, 1950, &transparent_color)?;

        gen1_strategy.generate(&mut overlay_wand, primary, &AncestorData::empty(), settings)?;

        if let Some(father) = ancestors.get_father() {
            self.draw_parent(wand, father, 0.0, settings)?;
        }

        if let Some(mother) = ancestors.get_mother() {
            self.draw_parent(wand, mother, 180.0, settings)?;
        }

        self.composite_overlay(wand, &overlay_wand)?;

        Ok(())
    }

    fn generation(&self) -> u8 {
        2
    }

    fn validate_ancestors(&self, ancestors: &AncestorData) -> Result<(), ChartError> {
        ancestors.validate_for_generation(2)
    }

    fn overlay_settings(&self) -> GenerationOverlay {
        GenerationOverlay {
            scale: self.specs.overlay_scale,
            position_x: self.specs.composite_x,
            position_y: self.specs.composite_y,
        }
    }

    fn name(&self) -> &'static str {
        "Gen2Strategy"
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
    fn test_gen2_strategy_creation() {
        let settings = test_settings();
        let strategy = Gen2Strategy::new(&settings);
        assert_eq!(strategy.generation(), 2);
        assert_eq!(strategy.name(), "Gen2Strategy");
    }

    #[test]
    fn test_gen2_parent_offsets() {
        let specs = Gen2Specs::new();
        let (x, y) = specs.get_parent_offset(0.0);
        assert_eq!(x, 0.0);
        assert_eq!(y, 1759.0 - 975.0);

        let (x, y) = specs.get_parent_offset(180.0);
        assert_eq!(x, 0.0);
        assert_eq!(y, 975.0 - 1759.0);
    }
}
