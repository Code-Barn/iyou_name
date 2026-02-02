# Multi-Generation Family Tree Image Generation System

## Overview

This system generates family tree charts for multiple generations (1-10) using a hierarchical composition approach. Each higher generation calls lower-generation generators and composites their results.

## Architecture

### Core Components

1. **Settings Helper** (`apps/generator/utils/settings_helper.py`)
2. **Image Generators** (`apps/generator/utils/image_Xgenerator.py`)
3. **Generic Preview Endpoint** (`apps/hud/views.py:get_template_preview()`)
4. **Frontend JavaScript** (`display_tree.html`)

### Generation Chaining Pattern

```
10gen → calls 9gen → calls 8gen → ... → calls 1gen → returns base image
       → composites 9gen overlay → composites 8gen overlay → ... → final result
```

## Settings Architecture

### Prefix System

Each generation uses a specific prefix for user settings:

- **PRIMARY_***: 1 Generation (primary individual)
- **PARENT_***: 2 Generations (parents)
- **GRANDPARENT_***: 3 Generations (grandparents)
- **GREATGRANDPARENT_***: 4 Generations (great-grandparents)
- etc.

### Settings Inheritance

```python
user_settings = {
    # Base settings inherited by all generations
    "font_family": "Arial",
    "primary_background_color": "#FFFFFF",
    "primary_stroke_color": "#000000",
    
    # Generation-specific overrides
    "PRIMARY_name_font_size": 84,
    "PARENT_name_font_size": 60,    # Smaller for parent generation
    "GRANDPARENT_name_font_size": 48, # Even smaller for grandparents
}

# 2gen overlay settings (Nested Settings Architecture)
request_data = {
    "individual_id": "I123",
    "user_settings": {
        # Current 2gen settings
        "father_font_color": "#000000",
        "mother_font_color": "#000000",
        "composite_1gen_scale": 48,
        # ... other 2gen settings
    },
    "primary_settings": {
        # Stored 1gen settings for overlay
        "primary_background_color": "#1a5fb4",
        "primary_name_font_size": 91,
        "primary_stroke_color": "#000000",
        # ... other 1gen settings
    }
}
```

## Implementation Guide

### 1. Creating a New Generator

Copy the pattern from `image_1generator.py`:

```python
def generate_Xgen_preview(primary_individual, family_data, template="preview", user_settings=None):
    """
    Generate X-generation family tree chart
    """
    # Import helper functions
    from apps.generator.utils.settings_helper import extract_generation_settings
    from apps.generator.utils.image_1generator import generate_1gen_preview
    
    # Extract generation-specific settings
    gen_settings = extract_generation_settings(user_settings, "GENERATION_PREFIX")
    
    # Generate lower-generation overlay
    overlay_buffer = generate_(X-1)gen_preview(primary_individual, family_data, "preview", overlay_settings)
    
    # Apply current generation drawing
    with Drawing() as draw:
        # ... your drawing logic here ...
        draw(content_img)
    
    # Composite overlay
    overlay_buffer.seek(0)
    overlay_bytes = overlay_buffer.getvalue()
    with Image(blob=overlay_bytes) as overlay:
        overlay.resize(scale_factor)
        content_img.composite(overlay, left=x_pos, top=y_pos)
    
    return buffer
```

### 2. Settings Helper Usage

```python
from apps.generator.utils.settings_helper import extract_generation_settings, get_default_settings

# Extract generation-specific settings
parent_settings = extract_generation_settings(user_settings, "PARENT")

# Get defaults if no settings provided
if not parent_settings:
    parent_settings = get_default_settings("PARENT")
```

### 3. Composite Pattern

```python
# Generate overlay first
overlay_buffer = generate_lower_gen_preview(...)

# Apply current generation drawing
draw(content_img)

# Composite overlay
overlay_buffer.seek(0)
overlay_bytes = overlay_buffer.getvalue()
with Image(blob=overlay_bytes) as overlay:
    overlay.resize(int(overlay.width * 0.48), int(overlay.height * 0.48))
    content_img.composite(overlay, left=800, top=1070)
```

## File Structure

```
apps/generator/utils/
├── settings_helper.py              # Settings extraction and defaults
├── image_1generator.py             # 1 Generation (base)
├── image_2generator.py             # 2 Generations (parents + 1gen overlay)
├── image_3generator.py             # 3 Generations (grandparents + 2gen overlay)
├── ...
└── image_10generator.py            # 10 Generations
```

## Frontend Integration

### Template Selection with Session Persistence

```javascript
function handleTemplateChange() {
    const templateValue = document.getElementById('template-select').value;
    
    // Load template-specific settings panel
    loadSettingsPanel(templateValue).then(() => {
        // Load settings from session and update form
        return HUD.Session.loadSettingsFromSession();
    }).then(sessionSettings => {
        if (sessionSettings) {
            HUD.Utils.updateFormWithStoredSettings(sessionSettings);
        } else {
            // Fallback to localStorage for 1gen
            if (templateValue === '1') {
                const stored1GenSettings = HUD.Storage.getStored1GenSettings();
                if (stored1GenSettings) {
                    HUD.Utils.updateFormWithStoredSettings(stored1GenSettings);
                }
            }
        }
        
        // Update preview image
        updatePreviewImage(templateValue);
    });
}

function updatePreviewImage(templateValue) {
    const previewImg = document.getElementById('hud-preview');
    
    if (templateValue === '2') {
        // 2gen needs POST with stored 1gen settings
        const stored1GenSettings = HUD.Storage.getStored1GenSettings();
        if (stored1GenSettings) {
            const form = HUD.Main.getForm();
            const formData = new FormData(form);
            const userSettings = HUD.Utils.collectUserSettings(formData);
            userSettings.primary_settings = stored1GenSettings;
            HUD.Preview.generatePreview(userSettings);
        }
    } else {
        // Other templates use simple GET request
        const timestamp = Date.now();
        const individualId = document.querySelector('input[name="individual_id"]').value;
        previewImg.src = `/hud/get-template-preview/${templateValue}/?individual_id=${individualId}&t=${timestamp}`;
    }
}
```

### Settings Persistence Architecture

```javascript
// Dual-layer persistence for robustness
HUD.Settings.saveAndApplySettings() {
    // 1. Store in localStorage for immediate cross-template use
    if (HUD.Main.getCurrentTemplate() === '1') {
        HUD.Storage.store1GenSettings(userSettings);
    }
    
    // 2. Update form and generate preview
    HUD.Utils.updateFinalChartForm(userSettings);
    HUD.Preview.generatePreview(userSettings);
    
    // 3. Save to session (non-critical)
    HUD.Session.saveSettings(formData);
}
```

### Backend Endpoint

```python
@csrf_exempt
def get_template_preview(request, template_id):
    """
    Generic preview endpoint for all templates
    """
    # Convert all individuals to PersonData objects
    person_data_objects = {}
    for person_id, person_data in individuals.items():
        person_data_objects[person_id] = PersonData(**person_data)
    
    # Update family_data with PersonData objects
    family_data_with_person_objects = gedcom_file.parsed_data.copy()
    family_data_with_person_objects["individuals"] = person_data_objects
    
    # Get template mapping and call appropriate generator
    template_mapping = get_template_mapping()
    template_config = template_mapping.get(template_id)
    module = importlib.import_module(template_config["module"])
    generator_function = getattr(module, template_config["function"])
    
    # Generate preview
    preview_buffer = generator_function(primary_individual, family_data_with_person_objects, "preview", user_settings)
    
    return HttpResponse(preview_buffer, content_type="image/png")
```

## Common Issues and Solutions

### Issue: "dict object has no attribute 'full_name'"
**Cause**: Family members returned as dictionaries instead of PersonData objects
**Solution**: Convert all individuals to PersonData objects before passing to generators

### Issue: "no decode delegate for this image format"
**Cause**: Trying to use BytesIO buffer as filename
**Solution**: Use `Image(blob=buffer_bytes)` instead of `Image(filename=buffer)`

### Issue: Browser redirect on template change
**Cause**: Form submission competing with preview update
**Solution**: Remove form submission, update preview immediately

### Issue: "body string cannot be empty" (2gen with missing parents)
**Cause**: Trying to draw empty text strings when parents don't exist
**Solution**: Wrap all parent drawing in conditional blocks with null checks:
```python
if father:
    # Safe name access
    name_parts = father.full_name.split()
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    
    # Only draw if we have content
    if first_name:
        draw.text(x, y, first_name)
    
    # Safe attribute access
    birth_date = father.birth_date if father and father.birth_date else " "
    draw.text(0, 0, birth_date)
else:
    print("Father not found - skipping drawing")
```

### Issue: 400 Bad Request for /hud/save-settings/
**Cause**: Duplicate form fields (template field appears twice)
**Solution**: Remove hidden template input, keep only select dropdown
**Non-critical workaround**: Session save failures don't break functionality due to localStorage fallback

### Issue: Settings not persisting across template switches
**Cause**: Session save failing, no fallback mechanism
**Solution**: Dual-layer persistence (localStorage + session) with graceful fallbacks

## Testing

### Unit Tests

```python
class TestSettingsHelper(TestCase):
    def test_extract_primary_settings(self):
        user_settings = {
            "PRIMARY_name_font_size": 84,
            "font_family": "Arial",
            "PARENT_name_font_size": 60
        }
        
        primary_settings = extract_generation_settings(user_settings, "PRIMARY")
        
        self.assertEqual(primary_settings["name_font_size"], 84)
        self.assertEqual(primary_settings["font_family"], "Arial")
        self.assertNotIn("name_font_size", primary_settings)  # PARENT setting excluded

class TestImageGeneration(TestCase):
    def test_2gen_composite(self):
        # Test that 2gen properly calls 1gen and composites
        pass
```

### Integration Tests

```python
class TestTemplatePreview(TestCase):
    def test_all_templates_return_image(self):
        for template_id in range(1, 11):
            response = self.client.get(f'/hud/get-template-preview/{template_id}/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'image/png')
```

## Performance Considerations

### Memory Management
- Always reset buffer position: `buffer.seek(0)`
- Use context managers for Wand images: `with Image(...) as img:`
- Revoke object URLs for frontend images: `URL.revokeObjectURL(url)`

### Caching
- Consider caching generated overlays
- Template mapping is static and can be cached

### Scaling
- Higher generations (8+) may need optimization
- Consider async generation for complex charts

## Future Enhancements

### Planned Features
1. **Configurable composite positioning/sizing**
2. **Async generation for performance**
3. **Template-specific styling options**
4. **Export to multiple formats (SVG, Canvas)**
5. **Real-time preview updates**

### Extension Points
1. **Custom drawing plugins**
2. **Theme system**
3. **Animation support**
4. **Interactive elements**

## Troubleshooting Checklist

### Generator Not Working?
- [ ] Check imports for helper functions
- [ ] Verify PersonData object conversion
- [ ] Check buffer handling (seek(0) before read)
- [ ] Verify composite positioning

### Settings Not Applied?
- [ ] Check prefix naming (PRIMARY_, PARENT_, etc.)
- [ ] Verify settings extraction
- [ ] Check defaults in settings_helper.py

### Frontend Issues?
- [ ] Check generic endpoint URL
- [ ] Verify template ID parameter
- [ ] Check for JavaScript errors

---

**Last Updated**: 2026-02-01  
**Version**: 1.0  
**Maintainer**: Development Team