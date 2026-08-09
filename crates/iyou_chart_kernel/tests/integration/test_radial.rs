use iyou_chart_kernel::core::{ChartSettings, PersonData};
/// Integration tests for Radial Strategy (Generations 3-5)
/// Verifies quadrant tracking and recursive composition
use iyou_chart_kernel::{initialize_magick, AncestorData, UnifiedChartGenerator};

const PNG_MAGIC_HEADER: [u8; 8] = [137, 80, 78, 71, 13, 10, 26, 10];

fn create_test_settings() -> ChartSettings {
    ChartSettings {
        font_family: "Arial".to_string(),
        font_color: "black".to_string(),
        background_color: "white".to_string(),
        name_font_size: 74.0,
        date_font_size: 52.0,
        place_font_size: 48.0,
        use_outside_stroke: false,
        stroke_width: 4.0,
        stroke_color: "white".to_string(),
        flag_size: 666,
        flag_type: "birth".to_string(),
    }
}

fn create_primary_person() -> PersonData {
    PersonData {
        id: "I1".to_string(),
        full_name: "John Michael Smith".to_string(),
        given_name: "John".to_string(),
        surname: "Smith".to_string(),
        birth_date: Some("1970-05-15".to_string()),
        birth_place: Some("New York, NY".to_string()),
        death_date: Some("2020-01-01".to_string()),
        death_place: Some("Boston, MA".to_string()),
    }
}

fn create_father() -> PersonData {
    PersonData {
        id: "I2".to_string(),
        full_name: "Michael Johnson Smith".to_string(),
        given_name: "Michael".to_string(),
        surname: "Smith".to_string(),
        birth_date: Some("1945-03-22".to_string()),
        birth_place: Some("Chicago, IL".to_string()),
        death_date: None,
        death_place: None,
    }
}

fn create_mother() -> PersonData {
    PersonData {
        id: "I3".to_string(),
        full_name: "Sarah Elizabeth Wilson".to_string(),
        given_name: "Sarah".to_string(),
        surname: "Wilson".to_string(),
        birth_date: Some("1948-11-10".to_string()),
        birth_place: Some("Boston, MA".to_string()),
        death_date: None,
        death_place: None,
    }
}

fn create_paternal_grandfather() -> PersonData {
    PersonData {
        id: "I4".to_string(),
        full_name: "Robert James Smith".to_string(),
        given_name: "Robert".to_string(),
        surname: "Smith".to_string(),
        birth_date: Some("1920-06-18".to_string()),
        birth_place: Some("Detroit, MI".to_string()),
        death_date: Some("1995-08-23".to_string()),
        death_place: Some("Chicago, IL".to_string()),
    }
}

fn create_paternal_grandmother() -> PersonData {
    PersonData {
        id: "I5".to_string(),
        full_name: "Emily Louise Johnson".to_string(),
        given_name: "Emily".to_string(),
        surname: "Johnson".to_string(),
        birth_date: Some("1922-09-05".to_string()),
        birth_place: Some("Minneapolis, MN".to_string()),
        death_date: Some("2001-03-14".to_string()),
        death_place: Some("Chicago, IL".to_string()),
    }
}

fn create_maternal_grandfather() -> PersonData {
    PersonData {
        id: "I6".to_string(),
        full_name: "William Henry Wilson".to_string(),
        given_name: "William".to_string(),
        surname: "Wilson".to_string(),
        birth_date: Some("1925-11-30".to_string()),
        birth_place: Some("Portland, ME".to_string()),
        death_date: Some("1998-07-18".to_string()),
        death_place: Some("Boston, MA".to_string()),
    }
}

fn create_maternal_grandmother() -> PersonData {
    PersonData {
        id: "I7".to_string(),
        full_name: "Margaret Rose O'Brien".to_string(),
        given_name: "Margaret".to_string(),
        surname: "O'Brien".to_string(),
        birth_date: Some("1928-04-22".to_string()),
        birth_place: Some("Dublin, Ireland".to_string()),
        death_date: Some("2005-12-08".to_string()),
        death_place: Some("Boston, MA".to_string()),
    }
}

#[test]
fn test_gen3_radial_strategy() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    // Add parents (required for Gen2, which is composed in Gen3)
    ancestors.add_individual("1", create_father());
    ancestors.add_individual("2", create_mother());

    // Add grandparents (required for Gen3)
    ancestors.add_individual("A", create_paternal_grandfather());
    ancestors.add_individual("B", create_paternal_grandmother());
    ancestors.add_individual("C", create_maternal_grandfather());
    ancestors.add_individual("D", create_maternal_grandmother());

    // Generate Gen3 chart
    let result = generator.generate(3, &primary, &ancestors);
    assert!(result.is_ok(), "Gen3 generation failed: {:?}", result);

    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty(), "Gen3 image is empty");

    // Verify PNG header
    assert!(
        image_bytes.len() >= PNG_MAGIC_HEADER.len(),
        "Gen3 image too small"
    );
    assert_eq!(
        &image_bytes[..8],
        PNG_MAGIC_HEADER,
        "Gen3 invalid PNG header"
    );

    // Verify reasonable size
    assert!(image_bytes.len() > 1000, "Gen3 image too small");
    assert!(image_bytes.len() < 2000000, "Gen3 image too large");
}

#[test]
fn test_gen4_radial_strategy() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    // Add parents
    ancestors.add_individual("1", create_father());
    ancestors.add_individual("2", create_mother());

    // Add grandparents
    ancestors.add_individual("A", create_paternal_grandfather());
    ancestors.add_individual("B", create_paternal_grandmother());
    ancestors.add_individual("C", create_maternal_grandfather());
    ancestors.add_individual("D", create_maternal_grandmother());

    // Add great-grandparents (required for Gen4)
    // We'll create minimal data for the 8 positions
    for i in 1..=2 {
        for suffix in ["1", "2"] {
            for prefix in ["A", "B", "C", "D"] {
                let id = format!("{}{}", prefix, suffix);
                ancestors.add_individual(
                    &id,
                    PersonData {
                        id: format!("I{}{}", prefix, suffix),
                        full_name: format!("Great-Grandparent {}{}", prefix, suffix),
                        given_name: "Test".to_string(),
                        surname: "Person".to_string(),
                        birth_date: Some("1900-01-01".to_string()),
                        birth_place: Some("Test City".to_string()),
                        death_date: None,
                        death_place: None,
                    },
                );
            }
        }
    }

    // Generate Gen4 chart
    let result = generator.generate(4, &primary, &ancestors);
    assert!(result.is_ok(), "Gen4 generation failed: {:?}", result);

    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty(), "Gen4 image is empty");

    // Verify PNG header
    assert!(
        image_bytes.len() >= PNG_MAGIC_HEADER.len(),
        "Gen4 image too small"
    );
    assert_eq!(
        &image_bytes[..8],
        PNG_MAGIC_HEADER,
        "Gen4 invalid PNG header"
    );

    // Verify reasonable size
    assert!(image_bytes.len() > 1000, "Gen4 image too small");
    assert!(image_bytes.len() < 2000000, "Gen4 image too large");
}

#[test]
fn test_gen5_radial_strategy() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    // Add parents
    ancestors.add_individual("1", create_father());
    ancestors.add_individual("2", create_mother());

    // Add grandparents
    ancestors.add_individual("A", create_paternal_grandfather());
    ancestors.add_individual("B", create_paternal_grandmother());
    ancestors.add_individual("C", create_maternal_grandfather());
    ancestors.add_individual("D", create_maternal_grandmother());

    // Add great-grandparents
    for prefix in ["A", "B", "C", "D"] {
        for suffix in ["1", "2"] {
            let id = format!("{}{}", prefix, suffix);
            ancestors.add_individual(
                &id,
                PersonData {
                    id: format!("I{}{}", prefix, suffix),
                    full_name: format!("Great-Grandparent {}{}", prefix, suffix),
                    given_name: "Test".to_string(),
                    surname: "Person".to_string(),
                    birth_date: Some("1900-01-01".to_string()),
                    birth_place: Some("Test City".to_string()),
                    death_date: None,
                    death_place: None,
                },
            );
        }
    }

    // Add 16 ancestors for Gen5 (positions A1, A2, B1, B2, C1, C2, D1, D2, E1, E2, F1, F2, G1, G2, H1, H2)
    let gen5_ids = [
        "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2", "F1", "F2", "G1", "G2", "H1",
        "H2",
    ];

    for (i, id) in gen5_ids.iter().enumerate() {
        ancestors.add_individual(
            id,
            PersonData {
                id: format!("I{}", 10 + i),
                full_name: format!("Ancestor {}", id),
                given_name: "Test".to_string(),
                surname: "Person".to_string(),
                birth_date: Some("1880-01-01".to_string()),
                birth_place: Some("Test City".to_string()),
                death_date: None,
                death_place: None,
            },
        );
    }

    // Generate Gen5 chart
    let result = generator.generate(5, &primary, &ancestors);
    assert!(result.is_ok(), "Gen5 generation failed: {:?}", result);

    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty(), "Gen5 image is empty");

    // Verify PNG header
    assert!(
        image_bytes.len() >= PNG_MAGIC_HEADER.len(),
        "Gen5 image too small"
    );
    assert_eq!(
        &image_bytes[..8],
        PNG_MAGIC_HEADER,
        "Gen5 invalid PNG header"
    );

    // Verify reasonable size
    assert!(image_bytes.len() > 1000, "Gen5 image too small");
    assert!(image_bytes.len() < 2000000, "Gen5 image too large");
}

#[test]
fn test_missing_ancestor_graceful_handling() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    // Add parents
    ancestors.add_individual("1", create_father());
    ancestors.add_individual("2", create_mother());

    // Add only 3 out of 4 grandparents (missing one)
    ancestors.add_individual("A", create_paternal_grandfather());
    ancestors.add_individual("B", create_paternal_grandmother());
    ancestors.add_individual("C", create_maternal_grandfather());
    // Intentionally missing "D" (maternal grandmother)

    // This should fail validation for Gen3
    let result = generator.generate(3, &primary, &ancestors);
    assert!(result.is_err(), "Gen3 should fail with missing ancestor");

    if let Err(error) = result {
        assert!(
            error.to_string().contains("missing required ancestor"),
            "Should indicate missing ancestor"
        );
    }
}

#[test]
fn test_strategy_access() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    // Test that Gen3-5 strategies are now supported
    assert!(generator.is_supported(1));
    assert!(generator.is_supported(2));
    assert!(generator.is_supported(3));
    assert!(generator.is_supported(4));
    assert!(generator.is_supported(5));

    // Test strategy names
    let gen3_strategy = generator.get_strategy(3).unwrap();
    assert_eq!(gen3_strategy.name(), "Gen3RadialStrategy");

    let gen4_strategy = generator.get_strategy(4).unwrap();
    assert_eq!(gen4_strategy.name(), "Gen4RadialStrategy");

    let gen5_strategy = generator.get_strategy(5).unwrap();
    assert_eq!(gen5_strategy.name(), "Gen5RadialStrategy");
}

#[test]
fn test_overlay_scales() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    // Verify exact overlay scales from Python prototypes
    let gen3_strategy = generator.get_strategy(3).unwrap();
    assert_eq!(gen3_strategy.overlay_settings().scale, 0.60);

    let gen4_strategy = generator.get_strategy(4).unwrap();
    assert_eq!(gen4_strategy.overlay_settings().scale, 0.7143);

    let gen5_strategy = generator.get_strategy(5).unwrap();
    assert_eq!(gen5_strategy.overlay_settings().scale, 0.75);
}
