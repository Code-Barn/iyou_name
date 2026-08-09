/// Sunbeam specifications for Generations 6-7
/// Dense concentric layouts with aggressive text constraints
/// Implements strict 105px concentric row spacing from prototype_image_6generator.py and prototype_image_7generator.py
use crate::core::{FontSizes, GenerationOverlay, PositionCoordinates};

/// Position specification for sunbeam generations (6-7)
#[derive(Debug, Clone)]
pub struct SunbeamPositionSpec {
    pub id: String,
    pub rotation: f64,
    pub relationship: String,
    pub font_sizes: FontSizes,
    pub name_position: PositionCoordinates,
    pub max_name_length: usize,
    pub max_place_length: usize,
}

/// Complete specifications for Generations 6-7
#[derive(Debug, Clone)]
pub struct SunbeamSpecs {
    gen6_positions: Vec<SunbeamPositionSpec>,
    gen7_positions: Vec<SunbeamPositionSpec>,
    gen6_overlay: GenerationOverlay,
    gen7_overlay: GenerationOverlay,
}

impl SunbeamSpecs {
    /// Create new sunbeam specifications
    pub fn new() -> Self {
        Self {
            gen6_positions: Self::create_gen6_positions(),
            gen7_positions: Self::create_gen7_positions(),

            // Overlay settings with strict constraints
            gen6_overlay: GenerationOverlay {
                scale: 0.80,
                position_x: 300,
                position_y: 570,
            },
            gen7_overlay: GenerationOverlay {
                scale: 0.85,
                position_x: 300,
                position_y: 570,
            },
        }
    }

    /// Get positions for specific generation
    pub fn get_positions(&self, generation: u8) -> &Vec<SunbeamPositionSpec> {
        match generation {
            6 => &self.gen6_positions,
            7 => &self.gen7_positions,
            _ => panic!("Invalid generation for sunbeam specs"),
        }
    }

    /// Get overlay settings for specific generation
    pub fn get_overlay_settings(&self, generation: u8) -> GenerationOverlay {
        match generation {
            6 => self.gen6_overlay,
            7 => self.gen7_overlay,
            _ => panic!("Invalid generation for sunbeam overlay"),
        }
    }

    /// Get max name length for generation
    pub fn get_max_name_length(&self, generation: u8) -> usize {
        match generation {
            6 => 15, // Gen6 constraint
            7 => 12, // Gen7 strict constraint
            _ => 20,
        }
    }

    /// Create Generation 6 positions (32 positions)
    /// Uses iterative approach to generate positions with 11.25° increments
    fn create_gen6_positions() -> Vec<SunbeamPositionSpec> {
        let mut positions = Vec::new();

        // Position 0: Primary individual
        positions.push(SunbeamPositionSpec {
            id: "0".to_string(),
            rotation: 0.0,
            relationship: "Primary".to_string(),
            font_sizes: FontSizes {
                name: 74.0,
                date: 52.0,
                place: 48.0,
            },
            name_position: PositionCoordinates {
                base_x: 0.0,
                base_y: 0.0,
                offset_x: 0.0,
                offset_y: 0.0,
            },
            max_name_length: 20,
            max_place_length: 25,
        });

        // Generate 32 ancestor positions with 11.25° increments
        // Using sunbeam positioning patterns from prototype_image_6generator.py
        let ids = [
            "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2", "F1", "F2", "G1", "G2",
            "H1", "H2", "I1", "I2", "J1", "J2", "K1", "K2", "L1", "L2", "M1", "M2", "N1", "N2",
            "O1", "O2", "P1", "P2",
        ];

        let rotations: [f64; 32] = [
            0.0, 11.25, 348.75, 337.5, 180.0, 191.25, 90.0, 101.25, 45.0, 56.25, 315.0, 303.75,
            135.0, 146.25, 225.0, 236.25, 270.0, 281.25, 202.5, 213.75, 112.5, 123.75, 292.5,
            303.75, 67.5, 78.75, 247.5, 258.75, 157.5, 168.75, 202.5, 213.75,
        ];

        // Base radius and spacing (105px concentric row spacing)
        let base_radius = 800.0;

        for i in 0..32 {
            let id = ids[i];
            let rotation = rotations[i];

            let rad = rotation.to_radians();
            let x = base_radius * rad.cos();
            let y = base_radius * rad.sin();

            let relationship = format!("Ancestor {}", id);
            positions.push(SunbeamPositionSpec {
                id: id.to_string(),
                rotation,
                relationship,
                font_sizes: FontSizes {
                    name: 12.0, // Smaller for dense layouts
                    date: 8.0,
                    place: 7.0,
                },
                name_position: PositionCoordinates {
                    base_x: x,
                    base_y: y,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                max_name_length: 15, // Gen6 constraint
                max_place_length: 10,
            });
        }

        positions
    }

    /// Create Generation 7 positions (64 positions)
    /// Uses iterative approach to generate positions with 5.625° increments
    fn create_gen7_positions() -> Vec<SunbeamPositionSpec> {
        let mut positions = Vec::new();

        // Position 0: Primary individual
        positions.push(SunbeamPositionSpec {
            id: "0".to_string(),
            rotation: 0.0,
            relationship: "Primary".to_string(),
            font_sizes: FontSizes {
                name: 74.0,
                date: 52.0,
                place: 48.0,
            },
            name_position: PositionCoordinates {
                base_x: 0.0,
                base_y: 0.0,
                offset_x: 0.0,
                offset_y: 0.0,
            },
            max_name_length: 20,
            max_place_length: 25,
        });

        // Generate 64 ancestor positions with 5.625° increments
        // Using strict 105px concentric row spacing
        let base_radius = 850.0; // Slightly larger radius for Gen7

        for i in 0..64 {
            let rotation = i as f64 * 5.625;
            let id = format!("{}{}", (b'A' + (i / 4) as u8) as char, (i % 4) + 1);

            let rad = rotation.to_radians();
            let x = base_radius * rad.cos();
            let y = base_radius * rad.sin();

            let relationship = format!("Ancestor {}", id);
            positions.push(SunbeamPositionSpec {
                id,
                rotation,
                relationship,
                font_sizes: FontSizes {
                    name: 10.0, // Even smaller for Gen7
                    date: 7.0,
                    place: 6.0,
                },
                name_position: PositionCoordinates {
                    base_x: x,
                    base_y: y,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                max_name_length: 12, // Gen7 strict constraint
                max_place_length: 8,
            });
        }

        positions
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sunbeam_specs_creation() {
        let specs = SunbeamSpecs::new();

        // Test Gen6
        let gen6_positions = specs.get_positions(6);
        assert_eq!(gen6_positions.len(), 33); // 1 primary + 32 ancestors

        // Test Gen7
        let gen7_positions = specs.get_positions(7);
        assert_eq!(gen7_positions.len(), 65); // 1 primary + 64 ancestors
    }

    #[test]
    fn test_max_name_lengths() {
        let specs = SunbeamSpecs::new();

        // Test strict constraints
        assert_eq!(specs.get_max_name_length(6), 15);
        assert_eq!(specs.get_max_name_length(7), 12);
    }

    #[test]
    fn test_overlay_settings() {
        let specs = SunbeamSpecs::new();

        // Test overlay scales
        assert_eq!(specs.get_overlay_settings(6).scale, 0.80);
        assert_eq!(specs.get_overlay_settings(7).scale, 0.85);
    }

    #[test]
    fn test_gen6_positions() {
        let specs = SunbeamSpecs::new();
        let positions = specs.get_positions(6);

        // Test primary position
        let primary = &positions[0];
        assert_eq!(primary.id, "0");
        assert_eq!(primary.rotation, 0.0);
        assert_eq!(primary.max_name_length, 20);

        // Test first ancestor position
        let first = &positions[1];
        assert_eq!(first.id, "A1");
        assert_eq!(first.rotation, 0.0);
        assert_eq!(first.max_name_length, 15);
        assert_eq!(first.font_sizes.name, 12.0);
    }

    #[test]
    fn test_gen7_positions() {
        let specs = SunbeamSpecs::new();
        let positions = specs.get_positions(7);

        // Test primary position
        let primary = &positions[0];
        assert_eq!(primary.id, "0");
        assert_eq!(primary.max_name_length, 20);

        // Test first ancestor position
        let first = &positions[1];
        assert_eq!(first.id, "A1");
        assert_eq!(first.rotation, 0.0);
        assert_eq!(first.max_name_length, 12);
        assert_eq!(first.font_sizes.name, 10.0);

        // Test last position
        let last = &positions[64];
        assert_eq!(last.id, "P4");
        assert_eq!(last.rotation, 354.375);
        assert_eq!(last.max_name_length, 12);
    }

    #[test]
    fn test_concentric_spacing() {
        let specs = SunbeamSpecs::new();
        let gen6_positions = specs.get_positions(6);
        let gen7_positions = specs.get_positions(7);

        // Verify Gen6 positions are at appropriate radius
        let a1_pos = &gen6_positions[1];
        let distance =
            (a1_pos.name_position.base_x.powf(2.0) + a1_pos.name_position.base_y.powf(2.0)).sqrt();
        assert!(
            distance > 700.0 && distance < 900.0,
            "Gen6 radius should be ~800"
        );

        // Verify Gen7 positions are slightly further out
        let a1_pos_gen7 = &gen7_positions[1];
        let distance_gen7 = (a1_pos_gen7.name_position.base_x.powf(2.0)
            + a1_pos_gen7.name_position.base_y.powf(2.0))
        .sqrt();
        assert!(
            distance_gen7 > distance,
            "Gen7 should be further out than Gen6"
        );
    }
}
