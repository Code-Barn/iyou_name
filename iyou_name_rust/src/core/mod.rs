//! Core module containing fundamental data structures and utilities

pub mod ancestor_data;
pub mod constants;
pub mod coordinate_system;
pub mod data_types;
pub mod error;

pub use ancestor_data::AncestorData;
pub use constants::*;
pub use coordinate_system::{rotate_around_center, rotate_coordinates};
pub use data_types::{
    ChartSettings, FlagPosition, FontSizes, GenerationOverlay, PersonData, PositionCoordinates,
};
pub use error::ChartError;
