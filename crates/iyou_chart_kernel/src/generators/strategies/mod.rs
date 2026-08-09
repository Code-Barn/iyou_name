//! Polymorphic strategy implementations for different generations

pub mod gen1;
pub mod gen2;
pub mod radial;
pub mod strategy_trait;
pub mod sunbeam;

pub use gen1::Gen1Strategy;
pub use gen2::Gen2Strategy;
pub use radial::RadialStrategy;
pub use strategy_trait::GenerationStrategyTrait;
pub use sunbeam::SunbeamStrategy;
