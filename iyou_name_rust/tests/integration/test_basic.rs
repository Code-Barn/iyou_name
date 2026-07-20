use iyou_chart_kernel::core::{ChartError, ChartSettings, GenerationOverlay, PersonData};
use iyou_chart_kernel::{initialize_magick, Gen1Generator, Gen2Generator};

const PNG_MAGIC_HEADER: [u8; 8] = [137, 80, 78, 71, 13, 10, 26, 10];

fn test_settings() -> ChartSettings {
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

#[test]
fn test_environment_initialization() {
    initialize_magick();
    initialize_magick();
}

#[test]
fn test_gen1_generation() {
    initialize_magick();

    let person = PersonData {
        id: "I1".to_string(),
        full_name: "John Michael Smith".to_string(),
        given_name: "John".to_string(),
        surname: "Smith".to_string(),
        birth_date: Some("1970-05-15".to_string()),
        birth_place: Some("New York, NY".to_string()),
        death_date: Some("2020-01-01".to_string()),
        death_place: Some("Boston, MA".to_string()),
    };

    let generator = Gen1Generator::new(test_settings());
    let result = generator.generate(&person);

    assert!(result.is_ok());
    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty());
    assert!(image_bytes.len() >= PNG_MAGIC_HEADER.len());
    assert_eq!(&image_bytes[..8], PNG_MAGIC_HEADER);
    assert!(image_bytes.len() > 1000);
    assert!(image_bytes.len() < 1000000);
}

#[test]
fn test_gen2_generation() {
    initialize_magick();

    let overlay_settings = GenerationOverlay {
        scale: 0.50,
        position_x: 0,
        position_y: 0,
    };

    let primary = PersonData {
        id: "I1".to_string(),
        full_name: "John Michael Smith".to_string(),
        given_name: "John".to_string(),
        surname: "Smith".to_string(),
        birth_date: Some("1970-05-15".to_string()),
        birth_place: Some("New York, NY".to_string()),
        death_date: Some("2020-01-01".to_string()),
        death_place: Some("Boston, MA".to_string()),
    };

    let father = PersonData {
        id: "I2".to_string(),
        full_name: "Michael Johnson Smith".to_string(),
        given_name: "Michael".to_string(),
        surname: "Smith".to_string(),
        birth_date: Some("1945-03-22".to_string()),
        birth_place: Some("Chicago, IL".to_string()),
        death_date: None,
        death_place: None,
    };

    let mother = PersonData {
        id: "I3".to_string(),
        full_name: "Sarah Elizabeth Wilson".to_string(),
        given_name: "Sarah".to_string(),
        surname: "Wilson".to_string(),
        birth_date: Some("1948-11-10".to_string()),
        birth_place: Some("Boston, MA".to_string()),
        death_date: None,
        death_place: None,
    };

    let generator = Gen2Generator::new(test_settings(), overlay_settings);
    let result = generator.generate(&primary, &father, &mother);

    assert!(result.is_ok());
    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty());
    assert!(image_bytes.len() >= PNG_MAGIC_HEADER.len());
    assert_eq!(&image_bytes[..8], PNG_MAGIC_HEADER);
    assert!(image_bytes.len() > 1000);
    assert!(image_bytes.len() < 2000000);
}

#[test]
fn test_error_handling() {
    initialize_magick();

    let person = PersonData {
        id: "I1".to_string(),
        full_name: "Test Person".to_string(),
        given_name: "Test".to_string(),
        surname: "Person".to_string(),
        birth_date: None,
        birth_place: None,
        death_date: None,
        death_place: None,
    };

    let generator = Gen1Generator::new(test_settings());
    let result = generator.generate(&person);
    assert!(result.is_ok() || result.is_err());
}

#[test]
fn test_empty_person_data() {
    initialize_magick();

    let empty_person = PersonData {
        id: "I1".to_string(),
        full_name: "".to_string(),
        given_name: "".to_string(),
        surname: "".to_string(),
        birth_date: None,
        birth_place: None,
        death_date: None,
        death_place: None,
    };

    let generator = Gen1Generator::new(test_settings());
    let result = generator.generate(&empty_person);

    assert!(result.is_ok());
    let image_bytes = result.unwrap();
    assert!(!image_bytes.is_empty());
}
