# Multi-Generation System Quick Reference

## 🚀 Quick Start

### Adding a New Generator (3gen Example)

```python
# 1. Create image_3generator.py
from apps.generator.utils.settings_helper import extract_generation_settings
from apps.generator.utils.image_2generator import generate_2gen_preview

def generate_3gen_preview(primary_individual, family_data, template="preview", user_settings=None):
    # Extract GRANDPARENT settings
    gen3_settings = extract_generation_settings(user_settings, "GRANDPARENT")
    
    # Generate 2gen overlay
    gen2_buffer = generate_2gen_preview(primary_individual, family_data, "preview", gen2_settings)
    
    # Apply 3gen drawing
    with Drawing() as draw:
        # ... your 3gen drawing logic ...
        draw(content_img)
    
    # Composite 2gen overlay
    gen2_buffer.seek(0)
    gen2_bytes = gen2_buffer.getvalue()
    with Image(blob=gen2_bytes) as gen2_overlay:
        gen2_overlay.resize(scale_factor)
        content_img.composite(gen2_overlay, left=x, top=y)
    
    return buffer
```

### Settings Prefix System

| Generation | Prefix | Example Settings |
|------------|--------|------------------|
| 1 | PRIMARY_ | PRIMARY_name_font_size: 84 |
| 2 | PARENT_ | PARENT_name_font_size: 60 |
| 3 | GRANDPARENT_ | GRANDPARENT_name_font_size: 48 |
| 4 | GREATGRANDPARENT_ | GREATGRANDPARENT_name_font_size: 36 |

## 🔧 Common Code Patterns

### Settings Extraction
```python
from apps.generator.utils.settings_helper import extract_generation_settings

# Extract generation-specific settings
parent_settings = extract_generation_settings(user_settings, "PARENT")
```

### Buffer Composite Pattern
```python
# Generate overlay
overlay_buffer = generate_lower_gen_preview(...)

# Apply current drawing
draw(content_img)

# Composite overlay
overlay_buffer.seek(0)
overlay_bytes = overlay_buffer.getvalue()
with Image(blob=overlay_bytes) as overlay:
    overlay.resize(int(overlay.width * 0.48), int(overlay.height * 0.48))
    content_img.composite(overlay, left=800, top=1070)
```

### Frontend Template Update
```javascript
function updatePreviewImage(templateValue) {
    const previewImg = document.getElementById('hud-preview');
    const timestamp = Date.now();
    previewImg.src = `/hud/get-template-preview/${templateValue}/?individual_id=${id}&t=${timestamp}`;
}
```

## 🐛 Common Issues & Fixes

### Issue: "dict object has no attribute 'full_name'"
```python
# ❌ Wrong (family_data contains dicts)
father = family_data["individuals"].get(primary_individual.father)

# ✅ Right (convert to PersonData objects first)
person_data_objects = {}
for person_id, person_data in individuals.items():
    person_data_objects[person_id] = PersonData(**person_data)
family_data["individuals"] = person_data_objects
```

### Issue: "no decode delegate for this image format"
```python
# ❌ Wrong (BytesIO is not a filename)
with Image(filename=buffer) as img:

# ✅ Right (use blob parameter)
buffer.seek(0)
with Image(blob=buffer.read()) as img:
```

### Issue: Browser redirect on template change
```javascript
// ❌ Wrong (form submission redirects)
tempForm.submit();

// ✅ Right (update preview immediately)
updatePreviewImage(templateValue);
// Settings saved when user clicks "Apply Settings"
```

## 📁 File Structure

```
apps/generator/
├── utils/
│   ├── settings_helper.py              # ✨ Settings extraction
│   ├── image_1generator.py             # 🏛️ Base generator
│   ├── image_2generator.py             # 👨‍👩‍👧‍👦 Parents + 1gen
│   ├── image_3generator.py             # 👨‍👩‍👧‍👦 Grandparents + 2gen
│   └── ...
├── tests/
│   └── test_multi_generation.py        # 🧪 Test suite
└── template_mapping.py                 # 🗺️ Template config
```

## 🎯 Key Functions

### Backend
- `extract_generation_settings(user_settings, prefix)` - Extract settings by generation
- `get_template_preview(request, template_id)` - Generic preview endpoint
- `generate_Xgen_preview(...)` - Main generator functions

### Frontend
- `handleTemplateChange()` - Template dropdown handler
- `updatePreviewImage(templateValue)` - Preview image updater
- `saveAndApplySettings()` - Settings application

## 🔍 Debug Checklist

### Generator Not Working?
- [ ] Imports: `from apps.generator.utils.settings_helper import extract_generation_settings`
- [ ] PersonData: Convert all individuals to PersonData objects
- [ ] Buffer: Use `Image(blob=buffer_bytes)` not `Image(filename=buffer)`
- [ ] Position: Check composite coordinates (left, top)

### Settings Not Applied?
- [ ] Prefix: Use correct generation prefix (PRIMARY_, PARENT_, etc.)
- [ ] Extraction: Call `extract_generation_settings(user_settings, "PREFIX")`
- [ ] Defaults: Check `get_default_settings("PREFIX")` in settings_helper.py

### Frontend Issues?
- [ ] URL: `/hud/get-template-preview/{template_id}/`
- [ ] Parameters: `individual_id` and timestamp `t`
- [ ] Console: Check for JavaScript errors

## 🚀 Performance Tips

### Memory Management
```python
# Always reset buffer position
buffer.seek(0)

# Use context managers
with Image(blob=buffer_bytes) as img:
    # ... image operations ...

# Revoke frontend URLs
URL.revokeObjectURL(url)
```

### Settings Optimization
```python
# Cache extracted settings
if not hasattr(self, '_cached_settings'):
    self._cached_settings = extract_generation_settings(user_settings, "PRIMARY")
```

## 🧪 Running Tests

```bash
# Run all multi-generation tests
python manage.py test apps.generator.tests.test_multi_generation

# Run specific test class
python manage.py test apps.generator.tests.test_multi_generation.TestSettingsHelper

# Run with coverage
python manage.py test --coverage apps.generator
```

## 📚 Further Reading

- **Wand Documentation**: https://docs.wand-py.org/
- **Django Testing**: https://docs.djangoproject.com/en/stable/topics/testing/
- **PersonData Model**: `apps/parser/models.py`

---

**Need Help?** Check the full documentation: `docs/MULTI_GENERATION_SYSTEM.md`