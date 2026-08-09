use crate::core::constants::*;
use crate::core::{AncestorData, ChartError, ChartSettings, GenerationOverlay, PersonData};
use crate::generators::strategies::strategy_trait::GenerationStrategyTrait;
use crate::rendering::text_renderer::TextRenderer;
use magick_rust::{DrawingWand, MagickWand, PixelWand};

struct Gen1Specs {
    name_font_size: f64,
    date_font_size: f64,
    place_font_size: f64,
    background_width: u32,
    background_height: u32,
    composite_x: i32,
    composite_y: i32,
    flag_base_x: f64,
    flag_base_y: f64,
    flag_rotation: f64,
    flag_size: u32,
}

impl Gen1Specs {
    fn new() -> Self {
        Self {
            name_font_size: 74.0,
            date_font_size: 52.0,
            place_font_size: 48.0,
            background_width: 1950,
            background_height: 1950,
            composite_x: 300,
            composite_y: 570,
            flag_base_x: 609.0,
            flag_base_y: 609.0,
            flag_rotation: -45.0,
            flag_size: 666,
        }
    }
}

pub struct Gen1Strategy {
    specs: Gen1Specs,
    text_renderer: TextRenderer,
}

impl Gen1Strategy {
    pub fn new(settings: &ChartSettings) -> Self {
        Self {
            specs: Gen1Specs::new(),
            text_renderer: TextRenderer::new(settings),
        }
    }

    fn draw_background(
        &self,
        wand: &mut MagickWand,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        let mut bg_pw = PixelWand::new();
        bg_pw.set_color(&settings.background_color)?;
        let mut draw = DrawingWand::new();
        draw.set_fill_color(&bg_pw);
        draw.draw_rectangle(
            0.0,
            0.0,
            self.specs.background_width as f64,
            self.specs.background_height as f64,
        );
        wand.draw_image(&draw)?;
        Ok(())
    }

    fn draw_primary_individual(
        &self,
        wand: &mut MagickWand,
        individual: &PersonData,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        let mut fill_pw = PixelWand::new();
        fill_pw.set_color(&settings.font_color)?;
        let mut draw = DrawingWand::new();
        draw.set_font(&settings.font_family)?;
        draw.set_font_size(self.specs.name_font_size);
        draw.set_fill_color(&fill_pw);

        if let Some(metrics) = self
            .text_renderer
            .get_name_metrics(wand, &individual.full_name)?
        {
            let x = IMAGE_CENTER_X - metrics.width / 2.0;
            let y = IMAGE_CENTER_Y;
            draw.draw_annotation(x, y, &individual.full_name)?;
        }

        if settings.use_outside_stroke {
            let mut stroke_pw = PixelWand::new();
            stroke_pw.set_color(&settings.stroke_color)?;
            let mut stroke_draw = DrawingWand::new();
            stroke_draw.set_font(&settings.font_family)?;
            stroke_draw.set_font_size(self.specs.name_font_size);
            stroke_draw.set_fill_color(&stroke_pw);
            stroke_draw.set_stroke_color(&stroke_pw);
            stroke_draw.set_stroke_width(settings.stroke_width);
            if let Some(metrics) = self
                .text_renderer
                .get_name_metrics(wand, &individual.full_name)?
            {
                let x = IMAGE_CENTER_X - metrics.width / 2.0;
                let y = IMAGE_CENTER_Y;
                stroke_draw.draw_annotation(x, y, &individual.full_name)?;
            }
            wand.draw_image(&stroke_draw)?;
        }

        wand.draw_image(&draw)?;
        Ok(())
    }
}

impl GenerationStrategyTrait for Gen1Strategy {
    fn generate(
        &self,
        wand: &mut MagickWand,
        primary: &PersonData,
        ancestors: &AncestorData,
        settings: &ChartSettings,
    ) -> Result<(), ChartError> {
        ancestors.validate_for_generation(1)?;

        wand.set_size(GEN1_CANVAS_WIDTH as usize, GEN1_CANVAS_HEIGHT as usize)?;
        let mut bg_color = PixelWand::new();
        bg_color.set_color(&settings.background_color)?;
        wand.new_image(
            self.specs.background_width as usize,
            self.specs.background_height as usize,
            &bg_color,
        )?;

        self.draw_background(wand, settings)?;
        self.draw_primary_individual(wand, primary, settings)?;

        Ok(())
    }

    fn generation(&self) -> u8 {
        1
    }

    fn validate_ancestors(&self, ancestors: &AncestorData) -> Result<(), ChartError> {
        ancestors.validate_for_generation(1)
    }

    fn overlay_settings(&self) -> GenerationOverlay {
        GenerationOverlay {
            scale: 1.0,
            position_x: self.specs.composite_x,
            position_y: self.specs.composite_y,
        }
    }

    fn name(&self) -> &'static str {
        "Gen1Strategy"
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::ChartSettings;

    #[test]
    fn test_gen1_strategy_creation() {
        let settings = ChartSettings {
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
        };

        let strategy = Gen1Strategy::new(&settings);
        assert_eq!(strategy.generation(), 1);
        assert_eq!(strategy.name(), "Gen1Strategy");
    }
}
