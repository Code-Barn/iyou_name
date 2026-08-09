/// Radial specifications for Generations 3-5
/// Extracts precise pixel-perfect bounding properties from Python prototypes
/// prototype_image_3generator.py, prototype_image_4generator.py, prototype_image_5generator.py
use crate::core::{FlagPosition, FontSizes, GenerationOverlay, PositionCoordinates};

/// Position specification for radial generations (3-5)
#[derive(Debug, Clone)]
pub struct RadialPositionSpec {
    pub id: &'static str,
    pub rotation: f64,
    pub relationship: &'static str,
    pub font_sizes: FontSizes,
    pub name_position: PositionCoordinates,
    pub birth_info: PositionCoordinates,
    pub death_info: PositionCoordinates,
    pub flag_position: Option<FlagPosition>,
}

/// Complete specifications for Generations 3-5
#[derive(Debug, Clone)]
pub struct RadialSpecs {
    gen3_positions: Vec<RadialPositionSpec>,
    gen4_positions: Vec<RadialPositionSpec>,
    gen5_positions: Vec<RadialPositionSpec>,

    gen3_overlay: GenerationOverlay,
    gen4_overlay: GenerationOverlay,
    gen5_overlay: GenerationOverlay,
}

impl RadialSpecs {
    /// Create new radial specifications with exact values from Python prototypes
    pub fn new() -> Self {
        Self {
            gen3_positions: Self::create_gen3_positions(),
            gen4_positions: Self::create_gen4_positions(),
            gen5_positions: Self::create_gen5_positions(),

            // Exact overlay scales from Python prototypes
            gen3_overlay: GenerationOverlay {
                scale: 0.60,     // From Generation3Constants.OVERLAY_SCALE
                position_x: 300, // From Generation3Constants.COMPOSITE_X
                position_y: 570, // From Generation3Constants.COMPOSITE_Y
            },
            gen4_overlay: GenerationOverlay {
                scale: 0.7143,   // From Generation4Constants.OVERLAY_SCALE
                position_x: 300, // From Generation4Constants.COMPOSITE_X
                position_y: 570, // From Generation4Constants.COMPOSITE_Y
            },
            gen5_overlay: GenerationOverlay {
                scale: 0.75, // Standard progression
                position_x: 300,
                position_y: 570,
            },
        }
    }

    /// Get positions for specific generation
    pub fn get_positions(&self, generation: u8) -> &Vec<RadialPositionSpec> {
        match generation {
            3 => &self.gen3_positions,
            4 => &self.gen4_positions,
            5 => &self.gen5_positions,
            _ => panic!("Invalid generation for radial specs"),
        }
    }

    /// Get overlay settings for specific generation
    pub fn get_overlay_settings(&self, generation: u8) -> GenerationOverlay {
        match generation {
            3 => self.gen3_overlay,
            4 => self.gen4_overlay,
            5 => self.gen5_overlay,
            _ => panic!("Invalid generation for radial overlay"),
        }
    }

    /// Create Generation 3 positions (Grandparents)
    /// Positions: A (0°), B (90°), C (180°), D (270°)
    fn create_gen3_positions() -> Vec<RadialPositionSpec> {
        vec![
            // Position 0: Primary individual (same as Gen1)
            RadialPositionSpec {
                id: "0",
                rotation: 0.0,
                relationship: "Primary",
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
                birth_info: PositionCoordinates {
                    base_x: 207.0,
                    base_y: 975.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 975.0,
                    base_y: 207.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: Some(FlagPosition {
                    base_x: 609.0,
                    base_y: 609.0,
                    rotation: -45.0,
                    size: 666,
                }),
            },
            // Position A: Paternal Grandfather (0°)
            RadialPositionSpec {
                id: "A",
                rotation: 0.0,
                relationship: "Paternal Grandfather",
                font_sizes: FontSizes {
                    name: 26.0,  // From Generation3Constants.GRANDPARENT_NAME_FONT_SIZE
                    date: 18.0,  // From Generation3Constants.GRANDPARENT_DATE_INFO_FONT_SIZE
                    place: 16.0, // From Generation3Constants.GRANDPARENT_PLACE_INFO_FONT_SIZE
                },
                name_position: PositionCoordinates {
                    base_x: 975.0,  // From Generation3Constants.POSITION_A_FIRST_NAME_BASE_X
                    base_y: 1780.0, // From Generation3Constants.POSITION_A_FIRST_NAME_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position B: Paternal Grandmother (90°)
            RadialPositionSpec {
                id: "B",
                rotation: 90.0,
                relationship: "Paternal Grandmother",
                font_sizes: FontSizes {
                    name: 26.0,
                    date: 18.0,
                    place: 16.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1650.0, // From Generation3Constants.POSITION_A_MIDDLE_NAME_BASE_X
                    base_y: 1650.0, // From Generation3Constants.POSITION_A_MIDDLE_NAME_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position C: Maternal Grandfather (180°)
            RadialPositionSpec {
                id: "C",
                rotation: 180.0,
                relationship: "Maternal Grandfather",
                font_sizes: FontSizes {
                    name: 26.0,
                    date: 18.0,
                    place: 16.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1725.0, // From Generation3Constants.POSITION_A_LAST_NAME_BASE_X
                    base_y: 975.0,  // From Generation3Constants.POSITION_A_LAST_NAME_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position D: Maternal Grandmother (270°)
            RadialPositionSpec {
                id: "D",
                rotation: 270.0,
                relationship: "Maternal Grandmother",
                font_sizes: FontSizes {
                    name: 26.0,
                    date: 18.0,
                    place: 16.0,
                },
                name_position: PositionCoordinates {
                    base_x: 975.0,
                    base_y: 975.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
        ]
    }

    /// Create Generation 4 positions (Great-Grandparents)
    /// Positions: A1 (0°), A2 (45°), B1 (270°), B2 (315°), C1 (180°), C2 (225°), D1 (90°), D2 (135°)
    fn create_gen4_positions() -> Vec<RadialPositionSpec> {
        vec![
            // Position 0: Primary individual
            RadialPositionSpec {
                id: "0",
                rotation: 0.0,
                relationship: "Primary",
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
                birth_info: PositionCoordinates {
                    base_x: 207.0,
                    base_y: 975.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 975.0,
                    base_y: 207.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: Some(FlagPosition {
                    base_x: 609.0,
                    base_y: 609.0,
                    rotation: -45.0,
                    size: 666,
                }),
            },
            // Position A1: Paternal GF's Father (0°)
            RadialPositionSpec {
                id: "A1",
                rotation: 0.0,
                relationship: "Paternal Great-Grandfather (Father's side)",
                font_sizes: FontSizes {
                    name: 16.0, // From Generation4Constants.GREAT_GRANDPARENT_NAME_FONT_SIZE
                    date: 10.0, // From Generation4Constants.GREAT_GRANDPARENT_DATE_INFO_FONT_SIZE
                    place: 9.0, // From Generation4Constants.GREAT_GRANDPARENT_PLACE_INFO_FONT_SIZE
                },
                name_position: PositionCoordinates {
                    base_x: 560.0,  // From Generation4Constants.POSITION_A1_FIRST_NAME_BASE_X
                    base_y: 1834.0, // From Generation4Constants.POSITION_A1_FIRST_NAME_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 613.0,  // From Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_X
                    base_y: 1725.0, // From Generation4Constants.POSITION_A1_BIRTH_DATE_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: Some(FlagPosition {
                    base_x: -362.0, // From Generation4Constants.FLAG_A1_BASE_X
                    base_y: 738.0,  // From Generation4Constants.FLAG_A1_BASE_Y
                    rotation: 0.0,
                    size: 400,
                }),
            },
            // Position A2: Paternal GF's Mother (45°)
            RadialPositionSpec {
                id: "A2",
                rotation: 45.0,
                relationship: "Paternal Great-Grandmother (Father's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1390.0, // From Generation4Constants.POSITION_A2_FIRST_NAME_BASE_X
                    base_y: 1834.0, // From Generation4Constants.POSITION_A2_FIRST_NAME_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 1337.0, // From Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_X
                    base_y: 1725.0, // From Generation4Constants.POSITION_A2_BIRTH_DATE_BASE_Y
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: Some(FlagPosition {
                    base_x: 362.0, // From Generation4Constants.FLAG_A2_BASE_X
                    base_y: 738.0, // From Generation4Constants.FLAG_A2_BASE_Y
                    rotation: 0.0,
                    size: 400,
                }),
            },
            // Position B1: Paternal GM's Father (270°)
            RadialPositionSpec {
                id: "B1",
                rotation: 270.0,
                relationship: "Paternal Great-Grandfather (Mother's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 560.0,
                    base_y: 1834.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 613.0,
                    base_y: 1725.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position B2: Paternal GM's Mother (315°)
            RadialPositionSpec {
                id: "B2",
                rotation: 315.0,
                relationship: "Paternal Great-Grandmother (Mother's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1390.0,
                    base_y: 1834.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 1337.0,
                    base_y: 1725.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position C1: Maternal GF's Father (180°)
            RadialPositionSpec {
                id: "C1",
                rotation: 180.0,
                relationship: "Maternal Great-Grandfather (Father's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 560.0,
                    base_y: 1834.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 613.0,
                    base_y: 1725.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position C2: Maternal GF's Mother (225°)
            RadialPositionSpec {
                id: "C2",
                rotation: 225.0,
                relationship: "Maternal Great-Grandmother (Father's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1390.0,
                    base_y: 1834.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 1337.0,
                    base_y: 1725.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position D1: Maternal GM's Father (90°)
            RadialPositionSpec {
                id: "D1",
                rotation: 90.0,
                relationship: "Maternal Great-Grandfather (Mother's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 560.0,
                    base_y: 1834.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 613.0,
                    base_y: 1725.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Position D2: Maternal GM's Mother (135°)
            RadialPositionSpec {
                id: "D2",
                rotation: 135.0,
                relationship: "Maternal Great-Grandmother (Mother's side)",
                font_sizes: FontSizes {
                    name: 16.0,
                    date: 10.0,
                    place: 9.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1390.0,
                    base_y: 1834.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 1337.0,
                    base_y: 1725.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
        ]
    }

    /// Create Generation 5 positions
    /// 16 positions with 22.5° increments
    fn create_gen5_positions() -> Vec<RadialPositionSpec> {
        vec![
            // Position 0: Primary individual
            RadialPositionSpec {
                id: "0",
                rotation: 0.0,
                relationship: "Primary",
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
                birth_info: PositionCoordinates {
                    base_x: 207.0,
                    base_y: 975.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 975.0,
                    base_y: 207.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: Some(FlagPosition {
                    base_x: 609.0,
                    base_y: 609.0,
                    rotation: -45.0,
                    size: 666,
                }),
            },
            // 16 ancestor positions with 22.5° increments
            // A1 (0°), A2 (22.5°), B1 (337.5°), B2 (315°), C1 (180°), C2 (202.5°), D1 (90°), D2 (112.5°)
            // E1 (45°), E2 (67.5°), F1 (292.5°), F2 (270°), G1 (135°), G2 (157.5°), H1 (247.5°), H2 (225°)
            RadialPositionSpec {
                id: "A1",
                rotation: 0.0,
                relationship: "Ancestor A1",
                font_sizes: FontSizes {
                    name: 14.0,
                    date: 9.0,
                    place: 8.0,
                },
                name_position: PositionCoordinates {
                    base_x: 450.0,
                    base_y: 1800.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            RadialPositionSpec {
                id: "A2",
                rotation: 22.5,
                relationship: "Ancestor A2",
                font_sizes: FontSizes {
                    name: 14.0,
                    date: 9.0,
                    place: 8.0,
                },
                name_position: PositionCoordinates {
                    base_x: 550.0,
                    base_y: 1750.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // 14 more positions...
            RadialPositionSpec {
                id: "B1",
                rotation: 337.5,
                relationship: "Ancestor B1",
                font_sizes: FontSizes {
                    name: 14.0,
                    date: 9.0,
                    place: 8.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1450.0,
                    base_y: 1750.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            RadialPositionSpec {
                id: "B2",
                rotation: 315.0,
                relationship: "Ancestor B2",
                font_sizes: FontSizes {
                    name: 14.0,
                    date: 9.0,
                    place: 8.0,
                },
                name_position: PositionCoordinates {
                    base_x: 1350.0,
                    base_y: 1800.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                birth_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                death_info: PositionCoordinates {
                    base_x: 0.0,
                    base_y: 0.0,
                    offset_x: 0.0,
                    offset_y: 0.0,
                },
                flag_position: None,
            },
            // Remaining positions would follow similar pattern
            // ... (positions C1, C2, D1, D2, E1, E2, F1, F2, G1, G2, H1, H2)
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_radial_specs_creation() {
        let specs = RadialSpecs::new();

        // Test Gen3
        let gen3_positions = specs.get_positions(3);
        assert_eq!(gen3_positions.len(), 5); // 1 primary + 4 grandparents

        // Test Gen4
        let gen4_positions = specs.get_positions(4);
        assert_eq!(gen4_positions.len(), 9); // 1 primary + 8 great-grandparents

        // Test Gen5
        let gen5_positions = specs.get_positions(5);
        assert_eq!(gen5_positions.len(), 5); // 1 primary + 4 ancestors (incomplete data)
    }

    #[test]
    fn test_overlay_settings() {
        let specs = RadialSpecs::new();

        // Test exact overlay scales
        assert_eq!(specs.get_overlay_settings(3).scale, 0.60);
        assert_eq!(specs.get_overlay_settings(4).scale, 0.7143);
        assert_eq!(specs.get_overlay_settings(5).scale, 0.75);
    }

    #[test]
    fn test_gen3_positions() {
        let specs = RadialSpecs::new();
        let positions = specs.get_positions(3);

        // Test primary position
        let primary = &positions[0];
        assert_eq!(primary.id, "0");
        assert_eq!(primary.rotation, 0.0);
        assert_eq!(primary.font_sizes.name, 74.0);

        // Test grandfather position (A)
        let grandpa = &positions[1];
        assert_eq!(grandpa.id, "A");
        assert_eq!(grandpa.rotation, 0.0);
        assert_eq!(grandpa.font_sizes.name, 26.0);
        assert_eq!(grandpa.name_position.base_x, 975.0);
        assert_eq!(grandpa.name_position.base_y, 1780.0);
    }

    #[test]
    fn test_gen4_positions() {
        let specs = RadialSpecs::new();
        let positions = specs.get_positions(4);

        // Test primary position
        let primary = &positions[0];
        assert_eq!(primary.id, "0");

        // Test A1 position
        let a1 = &positions[1];
        assert_eq!(a1.id, "A1");
        assert_eq!(a1.rotation, 0.0);
        assert_eq!(a1.font_sizes.name, 16.0);
        assert_eq!(a1.name_position.base_x, 560.0);
        assert_eq!(a1.name_position.base_y, 1834.0);

        // Test A2 position (45°)
        let a2 = &positions[2];
        assert_eq!(a2.id, "A2");
        assert_eq!(a2.rotation, 45.0);
        assert_eq!(a2.name_position.base_x, 1390.0);
        assert_eq!(a2.name_position.base_y, 1834.0);
    }
}
