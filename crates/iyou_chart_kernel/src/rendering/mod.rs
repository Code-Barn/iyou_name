//! Text and graphics rendering utilities

pub mod abbreviator;
pub mod text_renderer;

pub use abbreviator::TextAbbreviator;
pub use text_renderer::{TextMetrics, TextRenderer};
