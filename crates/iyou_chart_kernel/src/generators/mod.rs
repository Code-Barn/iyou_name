//! Chart generators for different generations

pub mod gen1;
pub mod gen2;
pub mod specs;
pub mod strategies;
pub mod unified_generator;

pub use gen1::Gen1Generator;
pub use gen2::Gen2Generator;
pub use specs::{RadialSpecs, SunbeamSpecs};
pub use strategies::{
    Gen1Strategy, Gen2Strategy, GenerationStrategyTrait, RadialStrategy, SunbeamStrategy,
};
pub use unified_generator::UnifiedChartGenerator;
