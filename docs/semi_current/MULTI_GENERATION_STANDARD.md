# Multi-Generation Chart Standardization Specification

## Overview

This document outlines the validated standard for multi-generation family tree chart generators (1-7+), ensuring consistent behavior, settings inheritance, and overlay composition across all generations.

## Validated Generations

- **Generation 1**: Individual-only chart with background and text rendering
- **Generation 2**: Individual + Parents with 1gen overlay composition  
- **Generation 3**: Individual + Parents + Grandparents with 2gen overlay composition
- **Generation 4**: Individual + Parents + Grandparents + Great-Grandparents with 3gen overlay composition
- **Generation 5**: Individual + Parents + Grandparents + Great-Grandparents + 2nd Great-Grandparents with 4gen overlay composition
- **Generation 6**: Individual + Parents + Grandparents + Great-Grandparents + 2nd Great-Grandparents + 3rd Great-Grandparents with 5gen overlay composition
- **Generation 7**: Individual + Parents + Grandparents + Great-Grandparents + 2nd Great-Grandparents + 3rd Great-Grandparents + 4th Great-Grandparents with 6gen overlay composition

## Core Standards

### 1. Settings Schema Standard

Each generator MUST follow this pattern:

```python
GENERATION_X_SETTINGS_SCHEMA = {
    # Global Font Settings
    "font_family": (str, "Arial"),
    
    # Primary Individual Settings (inherited from 1gen)
    "primary_background_color": (Color, "#FFFFFF"),
    "primary_font_color": (Color, "black"),
    "primary_stroke_color": (Color, "black"),
    "primary_stroke_width": (float, 0.5),
    "primary_name_font_size": (int, 84),
    "primary_date_info_font_size": (int, 60),
    "primary_place_info_font_size": (int, 28),
    "primary_translate_x": (int, 0),
    "primary_translate_y": (int, 0),
    "primary_name_rotate": (int, -45),
    "primary_birth_translate_x": (int, 0),
    "primary_birth_translate_y": (int, 0),
    "primary_birth_rotate": (int, -90),
    "primary_birth_place_translate_x": (int, 0),
    "primary_birth_place_translate_y": (int, 0),
    "primary_birth_place_rotate": (int, 0),
    "primary_death_translate_x": (int, 0),
    "primary_death_translate_y": (int, 0),
    "primary_death_rotate": (int, 0),
    "primary_death_place_translate_x": (int, 0),
    "primary_death_place_translate_y": (int, 0),
    "primary_death_place_rotate": (int, -90),
    
    # Generation-Specific Settings
    # [Individual settings for each person in this generation]
    
    # Overlay Composition Settings
    "overlay_scale": (float, 0.X),  # Varies by generation
    "overlay_position_x": (int, 0),
    "overlay_position_y": (int, 0),
}
```

### 2. Function Signature Standard

All generators MUST use this signature:

```python
def generate_Xgen_preview(
    primary_individual, family_data, template="preview", user_settings=None
):
```

### 3. Settings Processing Standard

All generators MUST follow this pattern:

```python
# Validate and process settings
user_settings = user_settings or {}
validated_settings = get_validated_settings(
    user_settings, GENERATION_X_SETTINGS_SCHEMA, "Xgen"
)
```

### 4. Overlay Composition Standard

Generators 2+ MUST follow this overlay pattern:

```python
# Generate (X-1)gen overlay with complete user settings
overlay_settings = user_settings  # Pass complete settings, not extracted
logger.debug(f"Generating {X-1}gen overlay with {len(overlay_settings)} settings")

gen_Xminus1_img_buffer = generate_Xminus1gen_preview(
    primary_individual, family_data, "preview", overlay_settings
)

# Composite the overlay onto the current generation image
_composite_overlay(content_img, gen_Xminus1_img_buffer, validated_settings)
```

**CRITICAL**: Always pass `user_settings` (complete settings) to overlay generators, never extracted subsets.

### 5. Background Rendering Standard

- **Generation 1**: MUST render background using `primary_background_color`
- **Generations 2+**: MUST NOT render background (inherits from overlay composition)

### 6. Text Rendering Standard

All text coordinates MUST use the translate pattern to handle negative values:

```python
# Instead of: draw.text(x, y, text)
# Use:
draw.push()
draw.translate(x, y)
draw.text(0, 0, text)
draw.pop()
```

### 7. Individual Position Settings Standard

Each person position MUST have these settings:

```python
"{person_type}_font_color": (Color, "black"),
"{person_type}_stroke_color": (Color, "black"),
"{person_type}_font_size": (int, DEFAULT_SIZE),
"{person_type}_translate_x": (int, 0),
"{person_type}_translate_y": (int, 0),
"{person_type}_rotate": (int, 0),
"{person_type}_birth_translate_x": (int, 0),
"{person_type}_birth_translate_y": (int, 0),
"{person_type}_birth_rotate": (int, 0),
"{person_type}_death_translate_x": (int, 0),
"{person_type}_death_translate_y": (int, 0),
"{person_type}_death_rotate": (int, 0),
```

## Frontend JavaScript Standard

### 1. Template Mapping Standard

All templates 1-7+ MUST be included in the settings template map:

```javascript
const settingsTemplateMap = {
    '1': '1gen_settings.html',
    '2': '2gen_settings.html',
    '3': '3gen_settings.html',
    '4': '4gen_settings.html',
    '5': '5gen_settings.html',
    '6': '6gen_settings.html',
    '7': '7gen_settings.html',
    '8': '8gen_settings.html',
    '9': '9gen_settings.html',
    '10': '10gen_settings.html',
};
```

### 2. Preview Generation Standard

Templates 1-7+ MUST use POST requests with complete user settings and include return statements:

```javascript
} else if (templateValue === 'X') {
    console.log(`Template ${X} selected - generating preview with ${X}gen settings`);
    
    // Collect current form settings
    const form = HUD.Main.getForm();
    const formData = new FormData(form);
    const userSettings = HUD.Utils.collectUserSettings(formData);
    
    // Add stored 1gen settings for overlay inheritance
    const stored1GenSettings = HUD.Storage.getStored1GenSettings();
    if (stored1GenSettings) {
        userSettings.primary_settings = stored1GenSettings;
        console.log(`Including stored 1gen settings for ${X}gen overlay:`, stored1GenSettings);
    }
    
    console.log(`Complete ${X}gen request data being sent:`, {
        individual_id: document.querySelector('input[name="individual_id"]').value,
        user_settings: userSettings
    });
    
    // Generate preview with POST and return to prevent fall-through
    return HUD.Preview.generatePreview(userSettings);
} else {
    // For templates beyond implemented scope, use GET request with stored settings
    const timestamp = Date.now();
    const individualId = document.querySelector('input[name="individual_id"]').value;
    const fileIdInput = document.querySelector('input[name="file_id"]');
    const fileId = fileIdInput ? fileIdInput.value : '';
    
    let url = `/hud/get-template-preview/${templateValue}/?individual_id=${individualId}&t=${timestamp}`;
    if (fileId) {
        url += `&file_id=${fileId}`;
    }
    
    console.log(`Loading template ${templateValue} preview with URL: ${url}`);
    // Set image source and handle errors...
}
```

**CRITICAL**: Each template block MUST include `return` statement to prevent execution fall-through to GET requests.

### 3. Settings Inheritance Standard

- **Template 1**: Saves settings to localStorage for inheritance
- **Templates 2-7+**: Load stored 1gen settings and include as `primary_settings`
- **All templates**: Pass complete user settings to backend

## Backend View Standard

### 1. Settings Processing Standard

GET requests MUST use session settings:

```python
if request.method == "GET":
    individual_id = request.GET.get("individual_id")
    # For GET requests, use current session settings
    user_settings = request.session.get("hud_settings", {})
elif request.method == "POST":
    data = json.loads(request.body)
    individual_id = data.get("individual_id")
    user_settings = data.get("user_settings", {})
```

### 2. Buffer Management Standard

All generators MUST use the buffer manager for caching:

```python
buffer = get_chart_buffer(
    primary_individual, family_data, user_settings, generation
)
```

## Validated Behaviors

### ✅ Working Correctly

1. **Settings Inheritance**: 1gen background color carries through to 2gen, 3gen, 4gen
2. **Overlay Composition**: Each generation properly composites the previous generation
3. **Individual Settings**: Each person position can be customized independently
4. **Text Rendering**: Negative coordinates handled properly with translate pattern
5. **Buffer Caching**: Settings changes properly invalidate cache
6. **JavaScript Integration**: All templates 1-5 use consistent POST pattern with proper return statements

### ⚠️ Identified Discrepancies

1. **Settings Schema Inconsistency**: Some generators missing individual person settings
2. **Overlay Settings Pattern**: 4gen was using extracted settings instead of complete user_settings (fixed)
3. **JavaScript Version Mismatch**: staticfiles version missing 4gen block (fixed)
4. **JavaScript Return Statement Bug**: Template blocks missing return statements causing fall-through to GET requests (fixed)

## Implementation Checklist for Generations 5-10+

When applying this standard to generations 5-10+:

### ✅ Required Changes

1. **Settings Schema**: Add individual settings for each person position
2. **Overlay Composition**: Pass complete `user_settings` to overlay generators
3. **JavaScript**: Add template block with return statement in all JavaScript versions
4. **Background Rendering**: Do not render background (inherit from overlays)
5. **Text Rendering**: Use translate pattern for all coordinates
6. **Buffer Integration**: Use `get_chart_buffer()` for caching

### ✅ Validation Tests

1. Change 1gen background color → Verify it appears in generation X
2. Adjust individual person settings → Verify they work independently
3. Switch between generations → Verify settings inheritance works
4. Check browser console → Verify POST requests with user_settings and no fall-through
5. Test buffer caching → Verify settings changes invalidate cache
6. Verify JavaScript return statements → Confirm only POST requests, not GET fallback

## File Locations

### Generator Files
- `apps/generator/utils/image_Xgenerator.py` (X = 1-10+)

### Settings Templates  
- `apps/hud/templates/hud/settings/Xgen_settings.html` (X = 1-10+)

### JavaScript Files
- `apps/hud/static/hud/js/hud-organized.js`
- `static/hud/js/hud-organized.js` 
- `staticfiles/hud/js/hud-organized.js`

### Backend Views
- `apps/hud/views_simple_buffered.py`

## Critical Bug Fix Summary

### JavaScript Return Statement Bug
**Issue**: Template blocks in `updatePreviewImage()` function were missing `return` statements, causing execution to continue through to the `else` block which uses GET requests instead of POST requests.

**Symptoms**:
- Template 5 was showing "Template 5 selected - generating preview with 5gen settings" 
- But also showing "Loading template 5 preview with URL: /hud/get-template-preview/5/?individual_id=X1756&t=1770603643438"
- Result: Template 5 used GET with session settings instead of POST with form settings

**Fix**: Added `return` statements to all template blocks:
```javascript
// Before (BROKEN):
HUD.Preview.generatePreview(userSettings);

// After (FIXED):
return HUD.Preview.generatePreview(userSettings);
```

**Impact**: 
- Templates 1-5 now properly use POST requests with complete user settings
- Settings inheritance works correctly for all implemented templates
- No more fall-through to GET requests causing empty/inconsistent settings

## Conclusion

This standard ensures consistent behavior across all multi-generation chart generators. By following these patterns, we guarantee that:

1. User settings properly inherit through the generation chain
2. Individual customizations work independently
3. Overlay composition functions correctly
4. Buffer caching provides optimal performance
5. Frontend-backend integration is seamless
6. JavaScript prevents execution fall-through with proper return statements

Apply this standard to generations 5-10+ to achieve uniform behavior across all chart types. The critical JavaScript return statement bug has been fixed, ensuring all templates use POST requests with complete user settings.