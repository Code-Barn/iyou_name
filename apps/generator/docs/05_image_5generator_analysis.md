# 5-Generation Chart Generator File Structure

## Overview

This document outlines the complete file structure and implementation details for the 5-generation family tree chart generator (`image_5generator.py`).

## File Location
```
/home/user/CODE_BASE/namechart/apps/generator/utils/image_5generator.py
```

## Class Structure

### Generation5Constants [Lines 27-71]

Defines all constants and configuration for 5-generation charts:

```python
class Generation5Constants:
    # Layout constants for positioning
    # Color defaults
    # Font size defaults
    # Position offsets
    # Scaling factors
```

**Key Constants:**
- Layout dimensions and spacing
- Default colors for each person type
- Font sizes for names, dates, places
- Position coordinates for all family members
- Overlay scaling and positioning

## Main Functions

### generate_5gen_preview [Lines 321-433]

**Purpose**: Main entry point for generating 5-generation chart previews

**Signature**:
```python
def generate_5gen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
```

**Process Flow**:
1. Validate and process user settings
2. Load 5-generation template
3. Draw current generation elements (2x great-grandparents)
4. Generate 4-generation overlay with complete user settings
5. Composite overlay onto current generation
6. Return final image buffer

**Key Features**:
- Uses standardized settings validation
- Implements overlay composition pattern
- Handles both preview and final chart generation
- Integrates with buffer management system

### _draw_twox_great_grandparents [Lines 436-494]

**Purpose**: Draws all 2x great-grandparents on the current generation canvas

**Process**:
1. Get all 2x great-grandparents data
2. Position and draw each person
3. Apply individual styling settings
4. Handle birth/death information display

### _draw_twox_great_grandparent_at_position [Lines 497-586]

**Purpose**: Draws a single 2x great-grandparent at a specific position

**Parameters**:
- `person`: Individual data
- `position_type`: String identifier for position
- `draw`: Wand Drawing context
- `settings`: Validated user settings

**Features**:
- Individual positioning and styling
- Text rendering with Wand Drawing API
- Birth/death information handling
- Custom color and font application

### get_2x_great_grandparents [Lines 589-647]

**Purpose**: Retrieves and organizes 2x great-grandparents data

**Returns**: Dictionary of 2x great-grandparents organized by position

**Data Structure**:
```python
{
    'paternal_2x_great_grandfather': Individual,
    'paternal_2x_great_grandmother': Individual,
    'maternal_2x_great_grandfather': Individual,
    'maternal_2x_great_grandmother': Individual,
    # Additional positions as needed
}
```

### _composite_overlay [Lines 650-687]

**Purpose**: Composites the 4-generation overlay onto the 5-generation canvas

**Process**:
1. Scale and position overlay
2. Apply transparency settings
3. Composite with proper blending
4. Handle edge cases and errors

### _create_final_pdf [Lines 690-722]

**Purpose**: Converts the final image to PDF format for download

**Features**:
- High-quality PDF generation
- Proper sizing and scaling
- Metadata inclusion
- Error handling

### generate_family_tree [Lines 726-728]

**Purpose**: Public API entry point for chart generation

**Implementation**: Delegates to `generate_5gen_preview`

## Settings Schema

The 5-generation generator uses a comprehensive settings schema that includes:

### Primary Individual Settings (Inherited from 1gen)
```python
"primary_background_color": (Color, "#FFFFFF"),
"primary_font_color": (Color, "black"),
"primary_stroke_color": (Color, "black"),
"primary_name_font_size": (int, 84),
# ... all primary individual settings
```

### 2x Great-Grandparents Settings
```python
"twox_greatgrandparent_font_color": (Color, "black"),
"twox_greatgrandparent_stroke_color": (Color, "black"),
"twox_greatgrandparent_font_size": (int, DEFAULT_SIZE),
"twox_greatgrandparent_translate_x": (int, 0),
"twox_greatgrandparent_translate_y": (int, 0),
"twox_greatgrandparent_rotate": (int, 0),
# Individual settings for each position
```

### Overlay Composition Settings
```python
"overlay_scale": (float, 0.4),  # Scaled for 5gen composition
"overlay_position_x": (int, 0),
"overlay_position_y": (int, 0),
```

## Overlay Composition Pattern

The 5-generation generator follows the standardized overlay pattern:

```python
# Generate 4gen overlay with complete user settings
overlay_settings = user_settings  # Pass complete settings
gen_4gen_img_buffer = generate_4gen_preview(
    primary_individual, family_data, "preview", overlay_settings
)

# Composite the overlay onto the 5gen canvas
_composite_overlay(content_img, gen_4gen_img_buffer, validated_settings)
```

**Critical**: Always passes complete `user_settings` to overlay generators, never extracted subsets.

## Text Rendering Standard

Uses the translate pattern for all text coordinates:

```python
# Standard text rendering with translate
draw.push()
draw.translate(x, y)
draw.text(0, 0, text)
draw.pop()
```

This handles negative coordinates properly and ensures consistent positioning.

## Background Rendering

**5-generation does NOT render background** - it inherits from the 4-generation overlay composition, which ultimately inherits from the 1gen background color.

## Buffer Integration

Integrates with the standardized buffer management system:

```python
buffer = get_chart_buffer(
    primary_individual, family_data, user_settings, generation=5
)
```

This provides caching and performance optimization.

## Error Handling

Comprehensive error handling throughout:

- Invalid family data
- Missing individuals
- Image processing errors
- Settings validation failures
- File system errors

## Testing Considerations

When testing the 5-generation generator:

1. **Settings Inheritance**: Verify 1gen background color appears in 5gen
2. **Individual Styling**: Test each 2x great-grandparent position independently
3. **Overlay Composition**: Verify 4gen overlay composites correctly
4. **Buffer Caching**: Test settings changes invalidate cache properly
5. **Error Scenarios**: Test with incomplete family data

## Integration Points

### Frontend Integration
- JavaScript template 5 block in `hud-organized.js`
- Settings template: `5gen_settings.html`
- POST request handling with complete user_settings

### Backend Integration
- View: `get_template_preview_simple` in `views_simple_buffered.py`
- Buffer manager: `simple_buffer_manager.py`
- Settings validation: Standardized pattern

### File System Integration
- Template loading: Standardized pattern
- PDF generation: Standardized pattern
- Error handling: Standardized pattern

## Dependencies

### Internal Dependencies
- `generate_4gen_preview` for overlay composition
- `simple_buffer_manager` for caching
- Standardized settings validation functions
- Common utility functions

### External Dependencies
- Wand (ImageMagick binding) for image processing
- Django models for family data
- Standard Python libraries

## Performance Considerations

- **Buffer Caching**: Reduces redundant generation
- **Overlay Composition**: More efficient than redrawing all elements
- **Settings Validation**: Optimized for repeated calls
- **Memory Management**: Proper cleanup of image resources

## Maintenance Notes

### When Modifying This File:

1. **Maintain Standards**: Follow all multi-generation standards
2. **Update Constants**: Keep Generation5Constants in sync
3. **Test Overlay**: Verify overlay composition works correctly
4. **Check Settings**: Ensure all settings are properly validated
5. **Update Documentation**: Keep this doc current

### Common Issues:

- **Settings Not Inheriting**: Check overlay composition pattern
- **Positioning Problems**: Verify translate pattern usage
- **Color Issues**: Check settings validation and defaults
- **Performance Problems**: Verify buffer caching is working

## Conclusion

The 5-generation generator is a critical component of the multi-generation chart system, providing the foundation for higher generations (6-7) through its standardized overlay composition pattern.

Its proper functioning is essential for the complete family tree visualization system and must adhere to all established standards for consistency and reliability.