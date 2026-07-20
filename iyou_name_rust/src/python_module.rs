// Zero-copy JSON pass-through interface for iyou_chart_kernel
// Pure FFI bridge with no structural duplication

use crate::core::ancestor_data::AncestorData;
use crate::core::data_types::{ChartSettings, PersonData};
use crate::generators::unified_generator::UnifiedChartGenerator;
use pyo3::prelude::*;

/// Main chart generation function using zero-copy JSON pass-through
#[pyfunction]
pub fn render_chart_from_json(
    generation: u8,
    primary_json: &str,
    ancestors_json: &str,
    settings_json: &str,
) -> PyResult<Vec<u8>> {
    // Deserialize strings directly into frozen types using zero-copy references where possible
    let primary: PersonData = serde_json::from_str(primary_json).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid primary individual payload: {}",
            e
        ))
    })?;

    let ancestors: AncestorData = serde_json::from_str(ancestors_json).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!("Invalid ancestor data map payload: {}", e))
    })?;

    let settings: ChartSettings = serde_json::from_str(settings_json).map_err(|e| {
        pyo3::exceptions::PyValueError::new_err(format!(
            "Invalid visual chart configuration parameters: {}",
            e
        ))
    })?;

    // Execute performance-isolated strategy execution
    let generator = UnifiedChartGenerator::new(settings);
    let image_bytes = generator
        .generate(generation, &primary, &ancestors)
        .map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Core rendering pipeline exception: {:?}",
                e
            ))
        })?;

    // Return clean memory handle back to Django as a Python bytes block
    Ok(image_bytes)
}

/// Python module definition
#[pymodule]
pub fn iyou_chart_kernel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render_chart_from_json, m)?)?;
    Ok(())
}
