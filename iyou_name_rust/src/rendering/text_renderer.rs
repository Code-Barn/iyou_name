use crate::core::{ChartError, ChartSettings};
use magick_rust::{DrawingWand, MagickWand, PixelWand};

#[derive(Debug, Clone)]
pub struct TextMetrics {
    pub width: f64,
    pub height: f64,
    pub ascent: f64,
    pub descent: f64,
}

pub struct TextRenderer {
    settings: ChartSettings,
}

impl TextRenderer {
    pub fn new(settings: &ChartSettings) -> Self {
        Self {
            settings: settings.clone(),
        }
    }

    pub fn get_font_metrics(
        &self,
        _active_canvas: &MagickWand,
        text: &str,
        font_size: f64,
    ) -> Result<TextMetrics, ChartError> {
        let estimated_width = text.len() as f64 * font_size * 0.6;
        Ok(TextMetrics {
            width: estimated_width,
            height: font_size,
            ascent: font_size * 0.8,
            descent: font_size * 0.2,
        })
    }

    pub fn get_name_metrics(
        &self,
        active_canvas: &MagickWand,
        name: &str,
    ) -> Result<Option<TextMetrics>, ChartError> {
        if name.is_empty() {
            return Ok(None);
        }
        let metrics = self.get_font_metrics(active_canvas, name, self.settings.name_font_size)?;
        Ok(Some(metrics))
    }

    pub fn render_text_with_stroke(
        &self,
        wand: &mut MagickWand,
        text: &str,
        x: f64,
        y: f64,
        font_size: f64,
        _rotation: f64,
    ) -> Result<(), ChartError> {
        if self.settings.use_outside_stroke {
            let mut stroke_pw = PixelWand::new();
            stroke_pw.set_color(&self.settings.stroke_color)?;
            let mut stroke_draw = DrawingWand::new();
            stroke_draw.set_font(&self.settings.font_family)?;
            stroke_draw.set_font_size(font_size);
            stroke_draw.set_fill_color(&stroke_pw);
            stroke_draw.set_stroke_color(&stroke_pw);
            stroke_draw.set_stroke_width(self.settings.stroke_width);
            stroke_draw.draw_annotation(x, y, text)?;
            wand.draw_image(&stroke_draw)?;
        }

        let mut fill_pw = PixelWand::new();
        fill_pw.set_color(&self.settings.font_color)?;
        let mut main_draw = DrawingWand::new();
        main_draw.set_font(&self.settings.font_family)?;
        main_draw.set_font_size(font_size);
        main_draw.set_fill_color(&fill_pw);
        main_draw.draw_annotation(x, y, text)?;
        wand.draw_image(&main_draw)?;

        Ok(())
    }
}
