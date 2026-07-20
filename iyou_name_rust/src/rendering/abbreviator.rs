/// Text abbreviation engine for high-density layouts
/// Ensures name strings never exceed quadrant boundaries in outer tiers
use std::collections::HashMap;

/// Text abbreviator for truncating long names in dense layouts
#[derive(Debug, Clone)]
pub struct TextAbbreviator {
    max_length: usize,
    abbreviation_rules: HashMap<String, String>,
    common_geographic_abbreviations: HashMap<String, String>,
}

impl TextAbbreviator {
    /// Create a new text abbreviator with standard rules
    pub fn new() -> Self {
        Self {
            max_length: 20, // Default, can be overridden per position
            abbreviation_rules: Self::create_abbreviation_rules(),
            common_geographic_abbreviations: Self::create_geographic_abbreviations(),
        }
    }

    /// Create with specific maximum length
    pub fn with_max_length(max_length: usize) -> Self {
        Self {
            max_length,
            ..Self::new()
        }
    }

    /// Create standard abbreviation rules
    fn create_abbreviation_rules() -> HashMap<String, String> {
        let mut rules = HashMap::new();

        // Common title abbreviations
        rules.insert("Junior".to_string(), "Jr.".to_string());
        rules.insert("Senior".to_string(), "Sr.".to_string());
        rules.insert("II".to_string(), "II".to_string());
        rules.insert("III".to_string(), "III".to_string());
        rules.insert("IV".to_string(), "IV".to_string());

        // Common suffixes
        rules.insert("the".to_string(), "the".to_string());
        rules.insert("of".to_string(), "of".to_string());
        rules.insert("and".to_string(), "&".to_string());

        rules
    }

    /// Create geographic abbreviation rules (matching place_name_utils.py patterns)
    fn create_geographic_abbreviations() -> HashMap<String, String> {
        let mut geo_abbrevs = HashMap::new();

        // US States
        geo_abbrevs.insert("Alabama".to_string(), "AL".to_string());
        geo_abbrevs.insert("Alaska".to_string(), "AK".to_string());
        geo_abbrevs.insert("Arizona".to_string(), "AZ".to_string());
        geo_abbrevs.insert("Arkansas".to_string(), "AR".to_string());
        geo_abbrevs.insert("California".to_string(), "CA".to_string());
        geo_abbrevs.insert("Colorado".to_string(), "CO".to_string());
        geo_abbrevs.insert("Connecticut".to_string(), "CT".to_string());
        geo_abbrevs.insert("Delaware".to_string(), "DE".to_string());
        geo_abbrevs.insert("Florida".to_string(), "FL".to_string());
        geo_abbrevs.insert("Georgia".to_string(), "GA".to_string());
        geo_abbrevs.insert("Hawaii".to_string(), "HI".to_string());
        geo_abbrevs.insert("Idaho".to_string(), "ID".to_string());
        geo_abbrevs.insert("Illinois".to_string(), "IL".to_string());
        geo_abbrevs.insert("Indiana".to_string(), "IN".to_string());
        geo_abbrevs.insert("Iowa".to_string(), "IA".to_string());
        geo_abbrevs.insert("Kansas".to_string(), "KS".to_string());
        geo_abbrevs.insert("Kentucky".to_string(), "KY".to_string());
        geo_abbrevs.insert("Louisiana".to_string(), "LA".to_string());
        geo_abbrevs.insert("Maine".to_string(), "ME".to_string());
        geo_abbrevs.insert("Maryland".to_string(), "MD".to_string());
        geo_abbrevs.insert("Massachusetts".to_string(), "MA".to_string());
        geo_abbrevs.insert("Michigan".to_string(), "MI".to_string());
        geo_abbrevs.insert("Minnesota".to_string(), "MN".to_string());
        geo_abbrevs.insert("Mississippi".to_string(), "MS".to_string());
        geo_abbrevs.insert("Missouri".to_string(), "MO".to_string());
        geo_abbrevs.insert("Montana".to_string(), "MT".to_string());
        geo_abbrevs.insert("Nebraska".to_string(), "NE".to_string());
        geo_abbrevs.insert("Nevada".to_string(), "NV".to_string());
        geo_abbrevs.insert("New Hampshire".to_string(), "NH".to_string());
        geo_abbrevs.insert("New Jersey".to_string(), "NJ".to_string());
        geo_abbrevs.insert("New Mexico".to_string(), "NM".to_string());
        geo_abbrevs.insert("New York".to_string(), "NY".to_string());
        geo_abbrevs.insert("North Carolina".to_string(), "NC".to_string());
        geo_abbrevs.insert("North Dakota".to_string(), "ND".to_string());
        geo_abbrevs.insert("Ohio".to_string(), "OH".to_string());
        geo_abbrevs.insert("Oklahoma".to_string(), "OK".to_string());
        geo_abbrevs.insert("Oregon".to_string(), "OR".to_string());
        geo_abbrevs.insert("Pennsylvania".to_string(), "PA".to_string());
        geo_abbrevs.insert("Rhode Island".to_string(), "RI".to_string());
        geo_abbrevs.insert("South Carolina".to_string(), "SC".to_string());
        geo_abbrevs.insert("South Dakota".to_string(), "SD".to_string());
        geo_abbrevs.insert("Tennessee".to_string(), "TN".to_string());
        geo_abbrevs.insert("Texas".to_string(), "TX".to_string());
        geo_abbrevs.insert("Utah".to_string(), "UT".to_string());
        geo_abbrevs.insert("Vermont".to_string(), "VT".to_string());
        geo_abbrevs.insert("Virginia".to_string(), "VA".to_string());
        geo_abbrevs.insert("Washington".to_string(), "WA".to_string());
        geo_abbrevs.insert("West Virginia".to_string(), "WV".to_string());
        geo_abbrevs.insert("Wisconsin".to_string(), "WI".to_string());
        geo_abbrevs.insert("Wyoming".to_string(), "WY".to_string());

        // Common geographic terms
        geo_abbrevs.insert("County".to_string(), "Co.".to_string());
        geo_abbrevs.insert("Mountain".to_string(), "Mt.".to_string());
        geo_abbrevs.insert("Saint".to_string(), "St.".to_string());
        geo_abbrevs.insert("Fort".to_string(), "Ft.".to_string());
        geo_abbrevs.insert("Lake".to_string(), "Lk.".to_string());
        geo_abbrevs.insert("River".to_string(), "Riv.".to_string());
        geo_abbrevs.insert("City".to_string(), "City".to_string());
        geo_abbrevs.insert("Town".to_string(), "Twn.".to_string());
        geo_abbrevs.insert("Village".to_string(), "Vlg.".to_string());
        geo_abbrevs.insert("Spring".to_string(), "Sp.".to_string());
        geo_abbrevs.insert("Valley".to_string(), "Vly.".to_string());
        geo_abbrevs.insert("Hill".to_string(), "Hl.".to_string());
        geo_abbrevs.insert("Island".to_string(), "Is.".to_string());
        geo_abbrevs.insert("Point".to_string(), "Pt.".to_string());
        geo_abbrevs.insert("Creek".to_string(), "Cr.".to_string());
        geo_abbrevs.insert("Road".to_string(), "Rd.".to_string());
        geo_abbrevs.insert("Street".to_string(), "St.".to_string());
        geo_abbrevs.insert("Avenue".to_string(), "Ave.".to_string());
        geo_abbrevs.insert("Boulevard".to_string(), "Blvd.".to_string());

        geo_abbrevs
    }

    /// Abbreviate text to fit within maximum length
    /// Always applies abbreviation rules, then truncates if still too long
    pub fn abbreviate(&self, text: &str, max_len: usize) -> String {
        let mut result = self.apply_abbreviations(text);

        if result.len() > max_len {
            result = self.truncate_cleanly(&result, max_len);
        }

        result
    }

    /// Apply common abbreviations to text
    fn apply_abbreviations(&self, text: &str) -> String {
        let mut result = text.to_string();

        // Apply geographic abbreviations first (they're more specific)
        for (full, abbr) in &self.common_geographic_abbreviations {
            result = result.replace(full, abbr);
        }

        // Apply general abbreviation rules
        for (full, abbr) in &self.abbreviation_rules {
            result = result.replace(full, abbr);
        }

        result
    }

    /// Truncate text cleanly at word boundaries
    fn truncate_cleanly(&self, text: &str, max_len: usize) -> String {
        if text.len() <= max_len {
            return text.to_string();
        }

        if let Some(last_space) = text[..max_len].rfind(' ') {
            if last_space > 0 {
                format!("{}…", &text[..last_space])
            } else {
                format!("{}…", &text[..max_len - 1])
            }
        } else {
            format!("{}…", &text[..max_len - 1])
        }
    }

    /// Set maximum length for this abbreviator
    pub fn set_max_length(&mut self, max_length: usize) {
        self.max_length = max_length;
    }

    /// Get current maximum length
    pub fn get_max_length(&self) -> usize {
        self.max_length
    }
}

/// Character normalization utilities
pub mod char_normalization {
    use once_cell::sync::Lazy;
    use regex::Regex;

    static MULTIPLE_SPACES: Lazy<Regex> = Lazy::new(|| Regex::new(r"\s+").unwrap());
    static LEADING_TRAILING_SPACES: Lazy<Regex> = Lazy::new(|| Regex::new(r"^\s+|\s+$").unwrap());

    /// Normalize whitespace in text
    pub fn normalize_whitespace(text: &str) -> String {
        let trimmed = LEADING_TRAILING_SPACES.replace_all(text, "");
        MULTIPLE_SPACES.replace_all(&trimmed, " ").to_string()
    }

    /// Normalize case for comparison
    pub fn normalize_case(text: &str) -> String {
        text.to_lowercase()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_abbreviator_creation() {
        let abbrev = TextAbbreviator::new();
        assert_eq!(abbrev.get_max_length(), 20);

        let abbrev = TextAbbreviator::with_max_length(15);
        assert_eq!(abbrev.get_max_length(), 15);
    }

    #[test]
    fn test_abbreviation_rules() {
        let abbrev = TextAbbreviator::new();

        // Test common abbreviations
        assert_eq!(abbrev.abbreviate("Junior", 10), "Jr.");
        assert_eq!(abbrev.abbreviate("Senior", 10), "Sr.");
        assert_eq!(abbrev.abbreviate("and", 10), "&");
    }

    #[test]
    fn test_geographic_abbreviations() {
        let abbrev = TextAbbreviator::new();

        // Test state abbreviations
        assert_eq!(abbrev.abbreviate("California", 10), "CA");
        assert_eq!(abbrev.abbreviate("New York", 10), "NY");

        // Test common geographic terms
        assert_eq!(abbrev.abbreviate("County", 10), "Co.");
        assert_eq!(abbrev.abbreviate("Mountain", 10), "Mt.");
        assert_eq!(abbrev.abbreviate("Saint Louis", 10), "St. Louis");
    }

    #[test]
    fn test_truncation() {
        let abbrev = TextAbbreviator::with_max_length(10);

        // Test clean truncation
        assert_eq!(abbrev.abbreviate("Hello World", 10), "Hello…");
        assert_eq!(abbrev.abbreviate("This is a test", 10), "This is a…");

        // Test no truncation needed
        assert_eq!(abbrev.abbreviate("Short", 10), "Short");
    }

    #[test]
    fn test_complex_abbreviation() {
        let abbrev = TextAbbreviator::with_max_length(15);

        // Test combination of abbreviations and truncation
        let long_text = "John Smith Junior from California County";
        let result = abbrev.abbreviate(long_text, 15);
        assert!(result.chars().count() <= 15);
        assert!(result.contains("Jr.") || result.contains("CA") || result.contains("Co."));
    }
}
