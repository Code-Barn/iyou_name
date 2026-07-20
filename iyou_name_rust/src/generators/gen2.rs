use crate::core::constants::*;
use crate::core::{ChartError, ChartSettings, GenerationOverlay, PersonData};
use crate::generators::gen1::Gen1Generator;
use magick_rust::{CompositeOperator, DrawingWand, MagickWand, PixelWand};

const LANCZOS_FILTER: u32 = 22;

pub struct Gen2Generator {
    settings: ChartSettings,
    overlay_settings: GenerationOverlay,
}

impl Gen2Generator {
    pub fn new(settings: ChartSettings, overlay_settings: GenerationOverlay) -> Self {
        Self {
            settings,
            overlay_settings,
        }
    }

    pub fn generate(
        &self,
        primary: &PersonData,
        father: &PersonData,
        mother: &PersonData,
    ) -> Result<Vec<u8>, ChartError> {
        let gen1_generator = Gen1Generator::new(self.settings.clone());
        let gen1_image = gen1_generator.generate(primary)?;

        let mut wand = MagickWand::new();
        wand.set_size(CANVAS_WIDTH as usize, CANVAS_HEIGHT as usize)?;
        let mut white = PixelWand::new();
        white.set_color("white")?;
        wand.new_image(CANVAS_WIDTH as usize, CANVAS_HEIGHT as usize, &white)?;

        self.draw_parent(&mut wand, father, 0.0)?;
        self.draw_parent(&mut wand, mother, 180.0)?;

        self.composite_overlay(&mut wand, &gen1_image)?;

        wand.write_image_blob("PNG").map_err(ChartError::from)
    }

    fn draw_parent(
        &self,
        wand: &mut MagickWand,
        person: &PersonData,
        rotation: f64,
    ) -> Result<(), ChartError> {
        let (name_x, name_y) = match rotation {
            0.0 => (0.0, PARENT_FIRST_NAME_BASE_Y - IMAGE_CENTER_Y),
            180.0 => (0.0, IMAGE_CENTER_Y - PARENT_FIRST_NAME_BASE_Y),
            _ => (0.0, 0.0),
        };

        let mut fill_pw = PixelWand::new();
        fill_pw.set_color(&self.settings.font_color)?;
        let mut draw = DrawingWand::new();
        draw.set_font(&self.settings.font_family)?;
        draw.set_font_size(GEN2_PARENT_NAME_FONT_SIZE);
        draw.set_fill_color(&fill_pw);

        draw.draw_annotation(name_x, name_y, &person.full_name)?;

        if self.settings.use_outside_stroke {
            let mut stroke_pw = PixelWand::new();
            stroke_pw.set_color(&self.settings.stroke_color)?;
            let mut stroke_draw = DrawingWand::new();
            stroke_draw.set_font(&self.settings.font_family)?;
            stroke_draw.set_font_size(GEN2_PARENT_NAME_FONT_SIZE);
            stroke_draw.set_fill_color(&stroke_pw);
            stroke_draw.set_stroke_color(&stroke_pw);
            stroke_draw.set_stroke_width(self.settings.stroke_width);
            stroke_draw.draw_annotation(name_x, name_y, &person.full_name)?;
            wand.draw_image(&stroke_draw)?;
        }

        wand.draw_image(&draw)?;
        Ok(())
    }

    fn composite_overlay(
        &self,
        wand: &mut MagickWand,
        overlay_data: &[u8],
    ) -> Result<(), ChartError> {
        let overlay_wand = MagickWand::new();
        overlay_wand.read_image_blob(overlay_data)?;

        let scaled_width = (CANVAS_WIDTH as f64 * self.overlay_settings.scale) as usize;
        let scaled_height = (CANVAS_HEIGHT as f64 * self.overlay_settings.scale) as usize;
        overlay_wand.resize_image(scaled_width, scaled_height, LANCZOS_FILTER);

        let pos_x = ((CANVAS_WIDTH as i32 - scaled_width as i32) / 2) as isize;
        let pos_y = ((CANVAS_HEIGHT as i32 - scaled_height as i32) / 2) as isize;

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
