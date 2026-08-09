use iyou_chart_kernel::core::{ChartSettings, PersonData};
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

fn create_test_person(id: &str, name: &str) -> PersonData {
    PersonData {
        id: id.to_string(),
        full_name: name.to_string(),
        given_name: "Test".to_string(),
        surname: "Person".to_string(),
        birth_date: Some("1900-01-01".to_string()),
        birth_place: Some("Test City".to_string()),
        death_date: None,
        death_place: None,
    }
}

#[test]
fn test_gen6_sunbeam_strategy() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    ancestors.add_individual("1", create_test_person("I2", "Father"));
    ancestors.add_individual("2", create_test_person("I3", "Mother"));

    ancestors.add_individual("A", create_test_person("I4", "Paternal Grandfather"));
    ancestors.add_individual("B", create_test_person("I5", "Paternal Grandmother"));
    ancestors.add_individual("C", create_test_person("I6", "Maternal Grandfather"));
    ancestors.add_individual("D", create_test_person("I7", "Maternal Grandmother"));

    let gen6_ids = [
        "A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2", "E1", "E2", "F1", "F2", "G1", "G2",
        "H1", "H2", "I1", "I2", "J1", "J2", "K1", "K2", "L1", "L2", "M1", "M2", "N1", "N2",
        "O1", "O2", "P1", "P2",
    ];

    for (i, id) in gen6_ids.iter().enumerate() {
        ancestors.add_individual(
            id,
            create_test_person(&format!("I{}", 10 + i), &format!("Ancestor {}", id)),
        );
    }

    let result = generator.generate(6, &primary, &ancestors);
    assert!(result.is_ok(), "Gen6 generation failed: {:?}", result);

    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty());
    assert!(image_bytes.len() >= PNG_MAGIC_HEADER.len());
    assert_eq!(&image_bytes[..8], PNG_MAGIC_HEADER);
}

#[test]
fn test_gen7_sunbeam_strategy() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    ancestors.add_individual("1", create_test_person("I2", "Father"));
    ancestors.add_individual("2", create_test_person("I3", "Mother"));

    ancestors.add_individual("A", create_test_person("I4", "Paternal Grandfather"));
    ancestors.add_individual("B", create_test_person("I5", "Paternal Grandmother"));
    ancestors.add_individual("C", create_test_person("I6", "Maternal Grandfather"));
    ancestors.add_individual("D", create_test_person("I7", "Maternal Grandmother"));

    for prefix in ["A", "B", "C", "D"] {
        for suffix in ["1", "2"] {
            let id = format!("{}{}", prefix, suffix);
            ancestors.add_individual(
                &id,
                create_test_person(
                    &format!("I{}{}", prefix, suffix),
                    &format!("Great-Grandparent {}{}", prefix, suffix),
                ),
            );
        }
    }

    for i in 0..64 {
        let prefix = (b'A' + (i / 4) as u8) as char;
        let suffix = (i % 4) + 1;
        let id = format!("{}{}", prefix, suffix);
        ancestors.add_individual(
            &id,
            create_test_person(
                &format!("I{}{}", prefix, suffix),
                &format!("Ancestor {}{}", prefix, suffix),
            ),
        );
    }

    let result = generator.generate(7, &primary, &ancestors);
    assert!(result.is_ok(), "Gen7 generation failed: {:?}", result);

    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty());
    assert!(image_bytes.len() >= PNG_MAGIC_HEADER.len());
    assert_eq!(&image_bytes[..8], PNG_MAGIC_HEADER);
}

#[test]
fn test_text_abbreviation_in_sunbeam() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let mut ancestors = AncestorData::new();

    ancestors.add_individual("1", create_test_person("I2", "Father"));
    ancestors.add_individual("2", create_test_person("I3", "Mother"));

    ancestors.add_individual("A", create_test_person("I4", "Paternal Grandfather"));
    ancestors.add_individual("B", create_test_person("I5", "Paternal Grandmother"));
    ancestors.add_individual("C", create_test_person("I6", "Maternal Grandfather"));
    ancestors.add_individual("D", create_test_person("I7", "Maternal Grandmother"));

    ancestors.add_individual(
        "A1",
        create_test_person("I10", "Alexander Hamilton Junior from New York County"),
    );
    ancestors.add_individual(
        "A2",
        create_test_person("I11", "Elizabeth Margaret Windsor of the United Kingdom"),
    );

    let result = generator.generate(6, &primary, &ancestors);
    assert!(result.is_ok(), "Gen6 with long names failed: {:?}", result);

    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty());
    assert_eq!(&image_bytes[..8], PNG_MAGIC_HEADER);
}

#[test]
fn test_strategy_access() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    for gen in 1..=7 {
        assert!(generator.is_supported(gen));
    }

    let gen6_strategy = generator.get_strategy(6).unwrap();
    assert_eq!(gen6_strategy.name(), "Gen6SunbeamStrategy");

    let gen7_strategy = generator.get_strategy(7).unwrap();
    assert_eq!(gen7_strategy.name(), "Gen7SunbeamStrategy");
}

#[test]
fn test_overlay_scales() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let gen6_strategy = generator.get_strategy(6).unwrap();
    assert_eq!(gen6_strategy.overlay_settings().scale, 0.80);

    let gen7_strategy = generator.get_strategy(7).unwrap();
    assert_eq!(gen7_strategy.overlay_settings().scale, 0.85);
}

#[test]
fn test_max_name_lengths() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let gen6 = generator.get_strategy(6).unwrap();
    assert_eq!(gen6.overlay_settings().scale, 0.80);

    let gen7 = generator.get_strategy(7).unwrap();
    assert_eq!(gen7.overlay_settings().scale, 0.85);
}

#[test]
fn test_invalid_generation() {
    initialize_magick();

    let settings = create_test_settings();
    let generator = UnifiedChartGenerator::new(settings);

    let primary = create_primary_person();
    let ancestors = AncestorData::new();

    let result = generator.generate(8, &primary, &ancestors);
    assert!(result.is_err());

    if let Err(error) = result {
        assert!(error.to_string().contains("Generation 8 not supported"));
    }
}
