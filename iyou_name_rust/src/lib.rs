//! iyou_chart_kernel - High-performance family tree chart generation engine
//!
//! This crate provides a native Rust implementation of the family tree chart generation
//! system, using magick-rust for ImageMagick bindings.

use magick_rust::magick_wand_genesis;
use std::sync::Once;

static INIT: Once = Once::new();

/// Initialize the ImageMagick environment
/// Must be called once before any generator operations
pub fn initialize_magick() {
    INIT.call_once(|| {
        magick_wand_genesis();
    });
}

pub mod core;
pub mod generators;
pub mod rendering;
pub mod utils;

pub use core::ancestor_data::AncestorData;
pub use core::data_types::{ChartSettings, GenerationOverlay, PersonData};
pub use core::error::ChartError;
pub use generators::gen1::Gen1Generator;
pub use generators::gen2::Gen2Generator;
pub use generators::{GenerationStrategyTrait, RadialSpecs, SunbeamSpecs, UnifiedChartGenerator};

#[cfg(feature = "python")]
pub mod python_module;
