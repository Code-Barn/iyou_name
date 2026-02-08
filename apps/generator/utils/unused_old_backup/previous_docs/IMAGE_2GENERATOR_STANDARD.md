# Image Generator Standard - 2 Generation Chart

## Overview

The `image_2generator.py` module generates 2-generation family tree charts displaying parents and the primary individual. This generator introduces advanced concepts including settings extraction, multi-generation overlay composition, and complex buffer management for standardization across the API.

## File Structure

```
apps/generator/utils/
├── image_2generator.py          # Main 2-generation chart generator
├── image_1generator.py          # Imported for overlay generation
├── name_utils.py               # Shared name parsing utilities
├── settings_helper.py          # Settings extraction and management
└── IMAGE_GENERATOR_STANDARD.md # This documentation
```

## Dependencies

- **Wand**: Python ImageMagick binding for image manipulation
- **Django**: For settings and file path resolution
- **image_1generator**: Imported for generating primary individual overlay
- **name_utils**: Shared utilities for name parsing (`parse_name_parts`)
- **settings_helper**: Settings extraction utilities (`extract_generation_settings`)

## Main Function

### `generate_2gen_preview(primary_individual, family_data, template="preview", user_settings=None)`

**Purpose**: Generate a 2-generation family tree chart showing parents and primary individual.

**Parameters**:
- `primary_individual`: PersonData object for the primary individual
- `family_data`: Dictionary containing family data with parents information
- `template`: String - "preview" for PNG, "final" for PDF output
- `user_settings`: Dictionary of customization settings (optional)

**Returns**: BytesIO buffer containing the generated image

**Raises**: Exception with detailed traceback and logging on generation failure

## Advanced Settings Management

### Settings Extraction Pattern

The 2-generation generator introduces a sophisticated settings management system:

```python
# Extract PARENT settings for 2gen-specific drawing
parent_settings = extract_generation_settings(user_settings, "PARENT")

# Extract PRIMARY settings for overlay generation
primary_settings = user_settings.get("primary_settings", {})
if not primary_settings:
    primary_settings = extract_generation_settings(user_settings, "PRIMARY")
```

### Settings Hierarchy

1. **Direct Settings**: User-provided settings without prefixes
2. **Generation-Specific Settings**: Extracted using `extract_generation_settings()`
3. **Stored Settings**: Nested settings (e.g., `primary_settings` for overlay)
4. **Fallback Settings**: Default values when user settings are missing

### Settings Categories

#### Parent Generation Settings
```python
parent_settings = {
    # Font settings (inherited from base)
    "font_family": "Arial",
    
    # Parent-specific styling
    "parent_stroke_color": "black",
    "default_stroke_width": 0.5,
    
    # Father-specific settings
    "father_font_color": "black",
    "father_birth_color": "black",
    "father_birth_place_color": "black",
    "father_death_color": "black",
    "father_death_place_color": "black",
    "father_first_translate_x": 975,
    "father_first_translate_y": 1700,
    "father_first_rotate": 0,
    # ... extensive father positioning settings
    
    # Mother-specific settings
    "mother_font_color": "black",
    "mother_birth_color": "black",
    "mother_birth_place_color": "black",
    "mother_death_color": "black",
    "mother_death_place_color": "black",
    "mother_first_translate_x": 0,
    "mother_first_translate_y": 0,
    "mother_first_rotate": 0,
    # ... extensive mother positioning settings
}
```

## Multi-Generation Architecture

### Overlay Composition System

The 2-generation generator uses a sophisticated overlay system:

1. **Base Layer**: 2-generation template with parent information
2. **Overlay Layer**: 1-generation primary individual chart
3. **Composition**: Overlay scaled and centered on base layer

#### Overlay Generation Process
```python
# Generate 1gen overlay with PRIMARY settings
gen1_img_buffer = generate_1gen_preview(
    primary_individual, family_data, "preview", primary_settings
)

# Convert buffer to image and scale
overlay_scale = 0.468  # 46.5% scale
with Image(blob=gen1_bytes) as gen1_overlay:
    overlay_size = int(content_img.width * overlay_scale)
    gen1_overlay.resize(overlay_size, overlay_size)
    
    # Center the overlay
    overlay_x = (content_img.width - overlay_size) // 2
    overlay_y = (content_img.height - overlay_size) // 2
    
    content_img.composite(gen1_overlay, left=overlay_x, top=overlay_y)
```

## Layout and Positioning

### Canvas Dimensions
- **Template Size**: Variable (based on 2GEN_PREVIEW.png)
- **Resolution**: 300 DPI
- **Initial Translation**: (350, 350) - offsets coordinate system

### Parent Positioning Strategy

#### Father Coordinates
- **First Name**: (975, 1700) with 0° rotation
- **Middle Name**: Translated from father position with -45° rotation
- **Last Name**: Further translated with -90° rotation
- **Birth Date**: Translated with 0° rotation
- **Birth Place**: Translated with 0° rotation
- **Death Date**: Translated with -90° rotation, 280px Y offset
- **Death Place**: Translated with -90° rotation, 280px Y offset

#### Mother Coordinates
- **First Name**: (0, 0) relative with 0° rotation
- **Middle Name**: Translated with -45° rotation
- **Last Name**: Further translated with -90° rotation
- **Birth/Death Info**: Similar pattern to father but with different base positions

## Drawing Pipeline

### 1. Template Loading
```python
preview_template_path = os.path.join(
    settings.BASE_DIR,
    "apps/hud/static/hud/images/preview_image_templates",
    "2GEN_PREVIEW.png"
)
```

### 2. Settings Processing
- Extract PARENT settings using `extract_generation_settings()`
- Extract PRIMARY settings for overlay generation
- Apply inheritance and fallback logic

### 3. Parent Generation Rendering
- Parse parents from `family_data["individuals"]`
- Use `parse_name_parts()` for name parsing (different from 1gen's `get_name_display_info`)
- Render each parent component with separate drawing contexts
- Apply extensive translation and rotation transformations

### 4. Overlay Generation
- Call `generate_1gen_preview()` with extracted PRIMARY settings
- Handle buffer management and conversion
- Scale and composite overlay onto base image

### 5. Output Generation

#### Preview Mode (template="preview")
- Returns composited image directly as PNG
- Saved to BytesIO buffer with proper positioning

#### Final Mode (template="final")
- Loads PDF base template: `US_LETTER_2GEN_BW.pdf`
- Composites content image at position (300, 570)
- Returns final PDF as BytesIO buffer

## Buffer Management Patterns

### Buffer Creation and Storage
```python
# Preview buffer creation
gen2_image_buffer = BytesIO()
content_img.save(file=gen2_image_buffer)
gen2_image_buffer.seek(0)
return gen2_image_buffer

# Final PDF buffer creation
pdf_buffer = BytesIO()
base_img.save(file=pdf_buffer)
pdf_buffer.seek(0)
return pdf_buffer
```

### Buffer Handling for Overlay
```python
# Generate overlay buffer
gen1_img_buffer = generate_1gen_preview(...)
gen1_img_buffer.seek(0)  # Reset position
gen1_bytes = gen1_img_buffer.getvalue()

# Convert to image for composition
with Image(blob=gen1_bytes) as gen1_overlay:
    # Process and composite
```

### Key Buffer Management Principles
1. **Always seek(0)** before reading from buffer
2. **Use getvalue()** for raw bytes when creating Image from blob
3. **Proper context management** with `with` statements
4. **Consistent naming** (gen1/gen2/prefix for clarity)

## Error Handling and Logging

### Enhanced Error Management
```python
except Exception as e:
    import traceback
    error_details = f"Error generating 2gen preview: {e}\n{traceback.format_exc()}"
    logger.error(error_details)
    print(f"ERROR: {error_details}")
    raise
```

### Logging Strategy
- **logger.error()**: For structured logging
- **print()**: For debug output (should be replaced with proper logging)
- **traceback.format_exc()**: For detailed error context

## Code Quality Assessment

### Documented Code
✅ **Fully Documented**: Comprehensive docstrings and inline comments

### Unused Code
⚠️ **Potential Unused Code**:
- `parent_settings` variable: Extracted but not directly used (settings accessed from user_settings)
- Some debug print statements: Could be removed in production
- Redundant parent lookups: Parents looked up multiple times

### Unreachable Code
✅ **No Unreachable Code**: All code paths serve a purpose

### Code Organization Issues
⚠️ **Standardization Opportunities**:
- **Inconsistent Name Parsing**: Uses `parse_name_parts()` instead of `get_name_display_info()`
- **Settings Access**: Mix of direct access and extracted settings
- **Buffer Variable Naming**: Inconsistent naming patterns

## Integration Points

### Settings Helper Integration
- Uses `extract_generation_settings()` for generation-specific settings
- Implements settings hierarchy and inheritance
- Supports nested settings for overlay generation

### 1-Generator Integration
- Imports and calls `generate_1gen_preview()` for overlay
- Passes extracted PRIMARY settings
- Handles buffer conversion and composition

### Name Utils Integration
- Uses `parse_name_parts()` instead of `get_name_display_info()`
- **INCONSISTENCY**: Different from 1gen generator's approach

## Standardization Analysis

### Settings Management
✅ **ADVANCED**: Sophisticated extraction and hierarchy system
⚠️ **INCONSISTENT**: Mix of direct and extracted settings access

### Buffer Management
✅ **CONSISTENT**: Proper BytesIO usage with seek(0) and context management
✅ **WELL PATTERNED**: Clear buffer creation and return patterns

### Name Parsing
❌ **INCONSISTENT**: Uses different utility than 1gen generator
- **2gen**: `parse_name_parts()` - returns tuple
- **1gen**: `get_name_display_info()` - returns dict with display_text

### Error Handling
✅ **ENHANCED**: Better logging and error context than 1gen
✅ **CONSISTENT**: Same exception raising pattern

### Output Generation
✅ **CONSISTENT**: Same preview/final pattern as 1gen
✅ **STANDARDIZED**: Same buffer return mechanism

## Performance Considerations

### Memory Usage
- **Overlay Buffer Management**: Additional buffer for 1gen overlay
- **Image Composition**: Memory-intensive scaling and compositing
- **Multiple Generations**: Calls 1gen generator internally

### Processing Speed
- **Dual Generation**: Generates both 2gen and 1gen content
- **Complex Composition**: Overlay scaling and centering
- **Settings Extraction**: Additional processing for settings hierarchy

## Recommendations

### Immediate Standardization Needs

1. **Name Parsing Consistency**
   ```python
   # Should match 1gen pattern
   name_info = get_name_display_info(father.full_name)
   display_text = name_info["display_text"]
   ```

2. **Settings Access Consistency**
   ```python
   # Use extracted settings consistently
   parent_settings = extract_generation_settings(user_settings, "PARENT")
   # Access all parent settings from parent_settings dict
   ```

3. **Debug Output Removal**
   - Replace print statements with proper logger calls
   - Add debug level configuration

### Future Enhancements

1. **Buffer Management Standardization**
   - Create shared buffer utility functions
   - Standardize variable naming conventions

2. **Settings System Enhancement**
   - Validate settings extraction results
   - Add settings merge utilities

3. **Performance Optimization**
   - Cache overlay generation when settings unchanged
   - Optimize image composition pipeline

### Maintenance Notes

- **Settings Complexity**: Monitor settings extraction performance
- **Overlay Dependencies**: Ensure 1gen generator compatibility
- **Memory Usage**: Watch for buffer leaks in composition pipeline
- **Template Consistency**: Verify template dimensions match expectations

## Template Dependencies

### Required Files
```
apps/hud/static/hud/images/preview_image_templates/2GEN_PREVIEW.png
apps/charts/static/charts/images/base_image_templates/US_LETTER_2GEN_BW.pdf
```

### Overlay Template Dependencies
- Requires 1GEN_PREVIEW.png (via image_1generator import)
- Requires US_LETTER_1GEN_BW.pdf (via 1gen final generation)

## Comparison with 1-Generation Generator

### Advantages over 1gen
- **Advanced Settings**: Sophisticated extraction and hierarchy
- **Overlay System**: Multi-generation composition capability
- **Enhanced Error Handling**: Better logging and error context
- **Family Data Usage**: Actually uses family_data parameter

### Standardization Issues
- **Name Parsing**: Inconsistent utility usage
- **Settings Access**: Mixed direct/extracted patterns
- **Complexity**: Significantly more complex than 1gen

### Best Practices to Adopt
- **Buffer Management**: Excellent pattern to standardize
- **Settings Hierarchy**: Advanced system worth standardizing
- **Error Logging**: Enhanced error handling pattern

## Version History

- **Current Version**: Advanced multi-generation with overlay composition
- **Major Features**: Settings extraction, overlay composition, enhanced error handling
- **Dependencies**: image_1generator, settings_helper, name_utils
- **Standardization Status**: Partially standardized with some inconsistencies
