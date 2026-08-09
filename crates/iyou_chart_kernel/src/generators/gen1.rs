use crate::core::constants::*;
use crate::core::{ChartError, ChartSettings, PersonData};
use crate::rendering::text_renderer::TextRenderer;
use magick_rust::{DrawingWand, MagickWand, PixelWand};

pub struct Gen1Generator {
    settings: ChartSettings,
}

impl Gen1Generator {
    pub fn new(settings: ChartSettings) -> Self {
        Self { settings }
    }

    pub fn generate(&self, person: &PersonData) -> Result<Vec<u8>, ChartError> {
        let mut wand = MagickWand::new();
        wand.set_size(GEN1_CANVAS_WIDTH as usize, GEN1_CANVAS_HEIGHT as usize)?;
        let mut bg = PixelWand::new();
        bg.set_color(&self.settings.background_color)?;
        wand.new_image(GEN1_BACKGROUND_WIDTH as usize, GEN1_BACKGROUND_HEIGHT as usize, &bg)?;

        self.draw_background(&mut wand)?;
        self.draw_text(&mut wand, person)?;

        wand.write_image_blob("PNG").map_err(ChartError::from)
    }

    fn draw_background(&self, wand: &mut MagickWand) -> Result<(), ChartError> {
        let mut bg_pw = PixelWand::new();
        bg_pw.set_color(&self.settings.background_color)?;
        let mut draw = DrawingWand::new();
        draw.set_fill_color(&bg_pw);
        draw.draw_rectangle(
            0.0,
            0.0,
            GEN1_BACKGROUND_WIDTH as f64,
            GEN1_BACKGROUND_HEIGHT as f64,
        );
        wand.draw_image(&draw)?;
        Ok(())
    }

    fn draw_text(&self, wand: &mut MagickWand, person: &PersonData) -> Result<(), ChartError> {
        let text_renderer = TextRenderer::new(&self.settings);

        if let Some(metrics) = text_renderer.get_name_metrics(wand, &person.full_name)? {
            let mut fill_pw = PixelWand::new();
            fill_pw.set_color(&self.settings.font_color)?;
            let mut draw = DrawingWand::new();
            draw.set_font(&self.settings.font_family)?;
            draw.set_font_size(self.settings.name_font_size);
            draw.set_fill_color(&fill_pw);

            let x = IMAGE_CENTER_X - metrics.width / 2.0;
            let y = IMAGE_CENTER_Y;
            draw.draw_annotation(x, y, &person.full_name)?;

            if self.settings.use_outside_stroke {
                self.render_stroke_effect(wand, &person.full_name, x, y)?;
            }

            wand.draw_image(&draw)?;
        }

        Ok(())
    }

    fn render_stroke_effect(
        &self,
        wand: &mut MagickWand,
        text: &str,
        x: f64,
        y: f64,
    ) -> Result<(), ChartError> {
        let mut stroke_pw = PixelWand::new();
        stroke_pw.set_color(&self.settings.stroke_color)?;
        let mut stroke_draw = DrawingWand::new();
        stroke_draw.set_font(&self.settings.font_family)?;
        stroke_draw.set_font_size(self.settings.name_font_size);
        stroke_draw.set_fill_color(&stroke_pw);
        stroke_draw.set_stroke_color(&stroke_pw);
        stroke_draw.set_stroke_width(self.settings.stroke_width);
        stroke_draw.draw_annotation(x, y, text)?;
        wand.draw_image(&stroke_draw)?;
        Ok(())
    }
}
