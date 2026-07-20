use crate::core::{ChartError, PersonData};
/// Ancestor data container for all generations
/// Manages individual data by position ID
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct AncestorData {
    /// Maps position IDs to individual data
    pub individuals: HashMap<String, PersonData>,
}

impl AncestorData {
    /// Create new empty ancestor data
    pub fn new() -> Self {
        Self {
            individuals: HashMap::new(),
        }
    }

    /// Create empty ancestor data
    pub fn empty() -> Self {
        Self::new()
    }

    /// Add individual by position ID
    pub fn add_individual(&mut self, position_id: &str, individual: PersonData) {
        self.individuals.insert(position_id.to_string(), individual);
    }

    /// Get individual by position ID
    pub fn get_individual(&self, position_id: &str) -> Option<&PersonData> {
        self.individuals.get(position_id)
    }

    /// Check if data is empty
    pub fn is_empty(&self) -> bool {
        self.individuals.is_empty()
    }

    /// Get count of individuals
    pub fn count(&self) -> usize {
        self.individuals.len()
    }

    /// Get father (position "1")
    pub fn get_father(&self) -> Option<&PersonData> {
        self.get_individual("1")
    }

    /// Get mother (position "2")
    pub fn get_mother(&self) -> Option<&PersonData> {
        self.get_individual("2")
    }

    /// Check if has father
    pub fn has_father(&self) -> bool {
        self.get_father().is_some()
    }

    /// Check if has mother
    pub fn has_mother(&self) -> bool {
        self.get_mother().is_some()
    }

    /// Validate data for specific generation
    pub fn validate_for_generation(&self, generation: u8) -> Result<(), ChartError> {
        match generation {
            1 => {
                if self.is_empty() {
                    Ok(())
                } else {
                    Err(ChartError::InvalidSettings(
                        "Gen1 should not have ancestors".to_string(),
                    ))
                }
            }
            2 => {
                if !self.has_father() {
                    return Err(ChartError::InvalidSettings(
                        "Gen2 requires father".to_string(),
                    ));
                }
                if !self.has_mother() {
                    return Err(ChartError::InvalidSettings(
                        "Gen2 requires mother".to_string(),
                    ));
                }
                if self.count() > 2 {
                    return Err(ChartError::InvalidSettings(
                        "Gen2 can only have father and mother".to_string(),
                    ));
                }
                Ok(())
            }
            3 => {
                // Requires 4 grandparents: A, B, C, D
                let required = ["A", "B", "C", "D"];
                for id in required {
                    if self.get_individual(id).is_none() {
                        return Err(ChartError::InvalidSettings(format!(
                            "Gen3 missing required ancestor: {}",
                            id
                        )));
                    }
                }
                Ok(())
            }
            4 => {
                // Requires 8 great-grandparents: A1, A2, B1, B2, C1, C2, D1, D2
                let required = ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"];
                for id in required {
                    if self.get_individual(id).is_none() {
                        return Err(ChartError::InvalidSettings(format!(
                            "Gen4 missing required ancestor: {}",
                            id
                        )));
                    }
                }
                Ok(())
            }
            5 => {
                // Gen5 requires 16 positions
                if self.count() < 16 {
                    return Err(ChartError::InvalidSettings(
                        "Gen5 requires at least 16 ancestors".to_string(),
                    ));
                }
                Ok(())
            }
            6 | 7 => {
                // Gen6-7 are more flexible, but should have reasonable data
                if self.count() < 8 {
                    return Err(ChartError::InvalidSettings(format!(
                        "Gen{} requires reasonable ancestor data",
                        generation
                    )));
                }
                Ok(())
            }
            _ => Err(ChartError::InvalidSettings(format!(
                "Invalid generation: {}",
                generation
            ))),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::PersonData;

    #[test]
    fn test_ancestor_data_validation() {
        let mut data = AncestorData::new();

        // Test Gen1 validation
        assert!(data.validate_for_generation(1).is_ok());

        // Add some data
        data.add_individual(
            "1",
            PersonData {
                id: "I1".to_string(),
                full_name: "Father".to_string(),
                given_name: "Father".to_string(),
                surname: "Test".to_string(),
                birth_date: None,
                birth_place: None,
                death_date: None,
                death_place: None,
            },
        );

        // Gen1 should fail with ancestors
        assert!(data.validate_for_generation(1).is_err());

        // Gen2 should fail with only father
        assert!(data.validate_for_generation(2).is_err());

        // Add mother
        data.add_individual(
            "2",
            PersonData {
                id: "I2".to_string(),
                full_name: "Mother".to_string(),
                given_name: "Mother".to_string(),
                surname: "Test".to_string(),
                birth_date: None,
                birth_place: None,
                death_date: None,
                death_place: None,
            },
        );

        // Gen2 should now pass
        assert!(data.validate_for_generation(2).is_ok());
    }
}
