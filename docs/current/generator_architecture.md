# NameChart Generator Architecture

## Overview
NameChart is a multi-generation family tree visualization system that supports 1-10 generation charts with customizable styling and positioning.

## Core Components

### 1. Image Generators (`apps/generator/utils/`)
- **`image_1generator.py`**: 1-generation charts (primary individual only)
- **`image_2generator.py`**: 2-generation charts (primary + parents)
- **`image_3-10generator.py`**: Future expansion (rough state)

### 2. HUD System (`apps/hud/`)
- **Interactive Preview**: Live chart preview with real-time settings
- **Settings Management**: Cross-template settings persistence
- **User Interface**: Template selection and customization controls

### 3. Shared Utilities (`apps/generator/utils/`)
- **`name_utils.py`**: Name parsing and formatting utilities
- **`settings_helper.py`**: Settings extraction and management
- **`gedcom_parser.py`**: GEDCOM file parsing

## Key Features Implemented

### Name Parsing System
**Problem**: Duplicate last names when no middle name present
**Solution**: Intelligent name parsing in `name_utils.py`

```python
def parse_name_parts(full_name):
    # Handles: "John Doe" -> ("John", "", "Doe")
    #          "John Michael Smith" -> ("John", "Michael", "Smith")
    #          "John" -> ("John", "", "")
```

### Settings Architecture
**1gen Settings**: ~30 configurable parameters
- Colors: background, stroke, font, birth/death info
- Fonts: family, sizes for name/date/place
- Positioning: translate X/Y, rotation for each element

**2gen Settings**: ~60 configurable parameters  
- Inherits all 1gen settings
- Adds parent-specific settings (father/mother)
- Composite overlay system for 2gen charts

### Interactive Features
- **Live Preview**: Real-time chart updates
- **Template Switching**: Seamless 1gen↔2gen transitions
- **Settings Persistence**: Cross-template memory
- **Rotation Controls**: CSS-based preview rotation (15° steps)

## Scaling Strategy for 10 Generations

### Challenges
1. **Settings Complexity**: 10gen = ~300+ settings vs 1gen = ~30
2. **Layout Complexity**: 512 individuals vs 1 individual
3. **Performance**: Rendering time and memory usage

### Proposed Solutions

#### 1. Hierarchical Settings System
```python
SETTINGS_HIERARCHY = {
    'primary': {...},      # Individual settings
    'parents': {...},      # Generation 1 settings  
    'grandparents': {...}, # Generation 2 settings
    # ... inherit from parent levels
}
```

#### 2. Configurable Layout System
```python
LAYOUT_CONFIGS = {
    '1gen': {'grid': (1,1), 'positions': {...}},
    '2gen': {'grid': (2,2), 'positions': {...}},
    '10gen': {'grid': (32,16), 'positions': {...}}
}
```

#### 3. Modular Generator Architecture
- Base generator class with common functionality
- Generation-specific layout and rendering modules
- Progressive rendering with caching

#### 4. Template Management
- Dynamic template loading based on generation
- Reusable component templates
- SVG-based layouts for better scalability

## Testing Strategy

### Unit Tests
- Name parsing edge cases
- Settings extraction and validation
- Individual coordinate calculations

### Integration Tests  
- End-to-end chart generation
- Settings persistence across templates
- HUD interaction workflows

### Performance Tests
- Rendering time benchmarks
- Memory usage profiling
- Large dataset handling

## Development Roadmap

### Phase 1: Foundation (Complete)
- ✅ 1gen generator with full customization
- ✅ 2gen generator with parent overlay
- ✅ HUD system with live preview
- ✅ Name parsing utilities
- ✅ Settings persistence

### Phase 2: Architecture Refactoring
- 🔄 Hierarchical settings system
- 🔄 Modular generator architecture
- 🔄 Configurable layout system
- 🔄 Shared utility consolidation

### Phase 3: Scaling Implementation
- ⏳ 3-5 generation generators
- ⏳ Performance optimization
- ⏳ Advanced layout algorithms
- ⏳ Template system enhancement

### Phase 4: Advanced Features
- ⏳ 6-10 generation generators
- ⏳ Interactive chart features
- ⏳ Export format variety
- ⏳ Advanced styling options

## Technical Debt & Improvements

### Immediate
- [ ] Consolidate name parsing across all generators
- [ ] Implement hierarchical settings
- [ ] Add comprehensive error handling
- [ ] Create generator base class

### Medium Term
- [ ] Dynamic layout configuration
- [ ] Performance profiling and optimization
- [ ] Advanced template system
- [ ] Interactive chart features

### Long Term
- [ ] Multi-format export (SVG, PDF, PNG)
- [ ] Advanced styling (themes, templates)
- [ ] Real-time collaboration features
- [ ] Cloud-based rendering

## Code Quality Standards

### Documentation
- All functions have docstrings with examples
- Complex algorithms have inline comments
- Architecture decisions are documented

### Testing
- 90%+ code coverage for core functionality
- Integration tests for user workflows
- Performance benchmarks for scaling

### Code Style
- PEP 8 compliance
- Type hints where appropriate
- Consistent naming conventions
- Modular, reusable components

## Conclusion

The current 1gen/2gen system provides a solid foundation for scaling to 10 generations. The key is implementing hierarchical systems for settings and layouts, while maintaining the modular architecture that allows for incremental development and testing.