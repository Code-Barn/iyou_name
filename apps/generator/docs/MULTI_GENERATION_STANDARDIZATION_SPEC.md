# Multi-Generation Chart Standardization Specification

## Overview

This document outlines the validated standard for multi-generation family tree chart generators (1-7), ensuring consistent behavior, settings inheritance, and overlay composition across all generations.

## ✅ VALIDATED GENERATIONS (ALL WORKING)

- **Generation 1**: Individual-only chart with background and text rendering
- **Generation 2**: Individual + Parents with 1gen overlay composition  
- **Generation 3**: Individual + Parents + Grandparents with 2gen overlay composition
- **Generation 4**: Individual + Parents + Grandparents + Great-Grandparents with 3gen overlay composition
- **Generation 5**: Individual + Parents + Grandparents + Great-Grandparents + 2x Great-Grandparents with 4gen overlay composition
- **Generation 6**: Individual + Parents + Grandparents + Great-Grandparents + 2x Great-Grandparents + 3x Great-Grandparents with 5gen overlay composition
- **Generation 7**: Individual + Parents + Grandparents + Great-Grandparents + 2x Great-Grandparents + 3x Great-Grandparents + 4x Great-Grandparents with 6gen overlay composition

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

Generations 2+ MUST follow this overlay pattern:

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

All templates 1-7 MUST be included in the settings template map:

```javascript
const settingsTemplateMap = {
    '1': '1gen_settings.html',
    '2': '2gen_settings.html',
    '3': '3gen_settings.html',
    '4': '4gen_settings.html',
    '5': '5gen_settings.html',
    '6': '6gen_settings.html',
    '7': '7gen_settings.html',
};
```

### 2. Preview Generation Standard

Templates 2-7 MUST use POST requests with complete user settings:

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
    
    // Generate preview with POST
    HUD.Preview.generatePreview(userSettings);
}
```

### 3. Settings Inheritance Standard

- **Template 1**: Saves settings to localStorage for inheritance
- **Templates 2-7**: Load stored 1gen settings and include as `primary_settings`
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

### ✅ Working Correctly (ALL GENERATIONS 1-7)

1. **Settings Inheritance**: 1gen background color carries through to 2gen, 3gen, 4gen, 5gen, 6gen, 7gen
2. **Overlay Composition**: Each generation properly composites the previous generation
3. **Individual Settings**: Each person position can be customized independently
4. **Text Rendering**: Negative coordinates handled properly with translate pattern
5. **Buffer Caching**: Settings changes properly invalidate cache
6. **JavaScript Integration**: All templates 1-7 use consistent POST pattern

### ⚠️ Previously Identified Issues (RESOLVED)

1. **Settings Schema Inconsistency**: Fixed - all generators now have individual person settings
2. **Overlay Settings Pattern**: Fixed - all generators now use complete user_settings
3. **JavaScript Version Mismatch**: Fixed - all JavaScript versions now include template 5-7 blocks
4. **Static File Conflicts**: Fixed - removed duplicate static files causing serving conflicts

## Critical Lessons Learned

### 🚨 Static File Serving Conflicts

**Issue**: Django was serving old JavaScript files from root `/static/` directory instead of updated files from app `/static/` directories.

**Root Cause**: Django's `STATICFILES_DIRS` listed root `static/` first, so it took priority over app directories.

**Solution**: 
- Remove duplicate static files from root directory
- Use only app-level static files for consistency
- Clear staticfiles cache with `collectstatic --clear`

**Prevention**: 
- Never have duplicate static files in root and app directories
- Always use app-level static files for app-specific content
- Test with browser tools to verify correct JavaScript is being served

### 🔧 JavaScript Syntax Error Detection

**Issue**: Extra closing brace in JavaScript prevented module loading silently.

**Root Cause**: Manual editing introduced syntax error that broke module but didn't crash page.

**Solution**: 
- Use `node -c filename.js` to check syntax
- Test JavaScript functionality in browser console
- Verify all modules load properly with `typeof window.HUD.Templates`

**Prevention**: 
- Always check JavaScript syntax after edits
- Test in browser before committing changes
- Use linter tools to catch syntax errors

### 🧪 End-to-End Testing Importance

**Issue**: Assumed fixes worked without proper verification.

**Root Cause**: Static file caching served old code despite correct source files.

**Solution**: 
- Use Playwright for actual browser testing
- Verify JavaScript functions are loaded and working
- Test complete user workflows end-to-end

**Prevention**: 
- Always test with real browser automation
- Verify both frontend and backend integration
- Check console logs for actual behavior vs expected

## Implementation Checklist for New Generations

When applying this standard to new generations:

### ✅ Required Changes

1. **Settings Schema**: Add individual settings for each person position
2. **Overlay Composition**: Pass complete `user_settings` to overlay generators
3. **JavaScript**: Add template block in all JavaScript versions
4. **Background Rendering**: Do not render background (inherit from overlays)
5. **Text Rendering**: Use translate pattern for all coordinates
6. **Buffer Integration**: Use `get_chart_buffer()` for caching
7. **Static File Management**: Ensure no duplicate files exist

### ✅ Validation Tests

1. Change 1gen background color → Verify it appears in generation X
2. Adjust individual person settings → Verify they work independently
3. Switch between generations → Verify settings inheritance works
4. Check browser console → Verify POST requests with user_settings
5. Test buffer caching → Verify settings changes invalidate cache
6. Verify JavaScript serving → Check correct file is being loaded

## File Locations

### Generator Files
- `apps/generator/utils/image_Xgenerator.py`

### Settings Templates  
- `apps/hud/templates/hud/settings/Xgen_settings.html`

### JavaScript Files (CRITICAL - All must be identical)
- `apps/hud/static/hud/js/hud-organized.js` (PRIMARY SOURCE)
- `static/hud/js/hud-organized.js` (REMOVE - causes conflicts)
- `staticfiles/hud/js/hud-organized.js` (Generated - don't edit)

### Backend Views
- `apps/hud/views_simple_buffered.py`

## Conclusion

This standard ensures consistent behavior across all multi-generation chart generators (1-7). By following these patterns, we guarantee that:

1. User settings properly inherit through the generation chain
2. Individual customizations work independently
3. Overlay composition functions correctly
4. Buffer caching provides optimal performance
5. Frontend-backend integration is seamless
6. Static file serving conflicts are avoided
7. JavaScript syntax errors are caught early

**ALL GENERATIONS 1-7 ARE NOW FULLY STANDARDIZED AND WORKING CORRECTLY** ✅