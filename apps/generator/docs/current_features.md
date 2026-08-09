# Generator App - Current Features Documentation

## Overview
The Generator app is the core engine for family tree chart generation. It provides the backend logic for creating family tree charts from GEDCOM data across multiple generations (1-10), supporting both preview generation and final PDF output.

## Core Features

### 1. Multi-Generation Chart Generation

**Supported Templates** (1-10 Generations):
- **1 Generation**: Individual focused chart with detailed personal information
- **2 Generation**: Individual + parents with composite overlay system
- **3-10 Generation**: Extended family trees with multi-generational layouts

**Template Configuration**:
- Dynamic module loading via `template_mapping.py`
- Standardized generator functions across all templates
- Base PDF templates for each generation type
- Flexible naming and configuration system

### 2. Dynamic Template System

#### Template Mapping Architecture
- **Centralized Configuration**: Single source of truth in `template_mapping.py`
- **Module Pattern**: Each generation in separate utility module
- **Function Standardization**: Consistent function signatures across generators
- **Filename Management**: Standardized base template file paths

#### Template Features
- **Base Templates**: Pre-designed PDF templates for each generation
- **Dynamic Import**: Runtime module loading for extensibility
- **Configuration-Driven**: Template behavior controlled by mapping config

### 3. Buffer Management System

#### Simple Buffer Manager
- **Efficiency**: Avoids regenerating identical charts
- **Memory Management**: Proper buffer cleanup and garbage collection
- **Settings-Based Caching**: Unique buffers per settings combination
- **Statistics**: Buffer usage monitoring and optimization

#### Buffer Features
- **Storage Optimization**: Efficient memory usage for generated charts
- **Cache Invalidation**: Smart cache invalidation on settings changes
- **Multi-Template Support**: Separate buffer spaces per template type

### 4. Chart Generation Pipeline

#### Data Processing Pipeline
1. **GEDCOM Parsing**: Convert GEDCOM to structured PersonData objects
2. **Settings Collection**: Gather user customization settings
3. **Template Selection**: Choose appropriate generator based on template ID
4. **Chart Generation**: Execute specific generator with settings
5. **Output Processing**: Convert to appropriate format (PNG/PDF)

#### Settings System
- **Font Customization**: Family, size, color settings
- **Position Controls**: Translation, rotation, scaling
- **Color Schemes**: Individual and generation-specific colors
- **Layout Options**: Composite overlay positioning and sizing

### 5. Final Chart Generation

#### PDF Output System
- **High-Quality Output**: Production-ready PDF generation
- **Template Integration**: Uses professional base templates
- **Settings Preservation**: Applies all user customizations
- **Multi-Format Support**: Preview PNG + Final PDF pipeline

#### Generation Features
- **Cumulative Settings**: Multi-generational settings inheritance
- **Composite Overlays**: Layered chart generation for 2+ generations
- **Position Calculation**: Automatic positioning algorithms
- **Quality Optimization**: High-resolution output generation

### 6. Preview Generation System

#### Real-Time Preview
- **Live Updates**: Immediate preview generation for settings changes
- **Buffer Integration**: Uses buffer system for performance
- **Format Optimization**: PNG format for web display
- **Settings Synchronization**: Mirrors final generation settings

#### Preview Features
- **Multi-Template**: Supports all template types for preview
- **Settings Validation**: Ensures preview matches final output
- **Performance Optimization**: Efficient preview generation
- **Error Handling**: Graceful fallback for preview failures

### 7. Position Calculation System

#### Positioning Algorithms
- **NameChart Position Calculator**: Intelligent text positioning
- **Quadrant Calculator**: Family member quadrant placement
- **Sunbeam Position Calculator**: Alternative layout algorithms
- **Multi-Generation Support**: Scalable positioning for large families

#### Positioning Features
- **Automatic Layout**: Intelligent positioning based on family structure
- **Custom Offsets**: User-adjustable positioning overrides
- **Rotation Support**: Text rotation for better space utilization
- **Collision Detection**: Prevents text overlap in complex charts

### 8. Settings Validation & Processing

#### Settings Helper System
- **Validation**: Comprehensive input validation for all settings
- **Type Conversion**: Automatic string to number conversion
- **Default Values**: Sensible defaults for all settings
- **Range Checking**: Validates numeric ranges for fonts/sizes

#### Settings Categories
- **Typography**: Font family, sizes, colors
- **Positioning**: Translations, rotations, scales
- **Layout**: Composite settings, overlay positions
- **Styling**: Stroke widths, background colors

### 9. Data Models & Integration

#### GedcomFile Model
- **File Management**: GEDCOM file upload and storage
- **Processing Status**: Track parsing completion
- **User Association**: Link files to user accounts
- **Metadata**: File information and processing stats

#### Parser Integration
- **PersonData Model**: Standardized person representation
- **Family Relationships**: Structured family relationship data
- **GEDCOM Processing**: Integration with parser app for data extraction

### 10. Utility Functions

#### Name Processing
- **Name Utils**: Name formatting and standardization
- **Display Names**: Proper name display formatting
- **Cultural Variations**: Support for different naming conventions

#### Chart Utilities
- **Base Chart Generator**: Common functionality for all generators
- **Image High-Gen Generator**: Extended generation support (8-10)
- **Settings Validator**: Comprehensive settings validation

## Template System Details

### Template Structure
```python
{
    "1": {
        "module": "apps.generator.utils.image_1generator",
        "function": "generate_1gen_preview", 
        "filename": ".../US_LETTER_1GEN_BW.pdf",
        "name": "1 Generation (Individual Only)",
        "template_type": "final"
    }
    # ... templates 2-10 follow same pattern
}
```

### Generator Functions
- **Standard Signature**: All generators follow same function signature
- **Consistent Parameters**: primary_individual, family_data, mode, user_settings
- **Return Type**: BytesIO buffer for image/PDF data
- **Error Handling**: Consistent error handling across all generators

## API Endpoints

### Main Generation Endpoint
- `/generate-final-chart/` - Final PDF generation
- Supports both GET and POST methods
- Session integration for settings persistence
- Template-based dynamic generation

### Utility Endpoints
- Various utility endpoints for testing and debugging
- Buffer statistics and management
- Settings validation endpoints

## Current Working Features Summary

### ✅ Fully Functional
- Multi-generation chart generation (1-10)
- Template system with dynamic loading
- Buffer management for performance
- Preview generation system
- Final PDF output
- Settings validation and processing
- Position calculation algorithms
- Name processing utilities
- GEDCOM integration

### ⚠️ Partial Implementation
- Some advanced positioning features may need refinement
- Buffer system could be enhanced with better cache invalidation
- Error handling could be more user-friendly

### ❌ Known Issues
- Hardcoded file paths in template mapping
- Limited error recovery in some generators
- Performance could be optimized for very large families

## Usage Flow

1. **Template Selection**: System selects template based on user choice
2. **Settings Collection**: User settings collected and validated
3. **Module Loading**: Appropriate generator module loaded dynamically
4. **Data Preparation**: GEDCOM data converted to PersonData objects
5. **Chart Generation**: Generator creates chart with settings
6. **Output Processing**: Chart converted to appropriate format
7. **Buffer Storage**: Generated chart cached in buffer system
8. **Response Delivery**: Chart delivered as PNG (preview) or PDF (final)

## Technical Dependencies

### Required Apps
- `apps.parser` - GEDCOM parsing and data models

### Key Dependencies
- ReportLab (PDF generation)
- Pillow (Image processing)
- Django models and views
- Dynamic Python module loading

### File Structure
```
apps/generator/
├── utils/
│   ├── image_1generator.py through image_10generator.py
│   ├── base_chart_generator.py (common functionality)
│   ├── image_high_gen_generator.py (8-10 gen support)
│   ├── namechart_position_calculator.py
│   ├── namechart_quadrant_calculator.py
│   ├── sunbeam_position_calculator.py
│   ├── settings_helper.py
│   ├── settings_validator.py
│   └── simple_buffer_manager.py
├── models/gedcom_file.py
├── template_mapping.py (central configuration)
└── views.py (main generation logic)
```

## Performance Characteristics

### Buffer System Benefits
- **Memory Efficiency**: Reuses generated charts when settings unchanged
- **Speed Improvement**: Avoids regenerating identical charts
- **Scalability**: Handles multiple concurrent chart generations

### Generation Performance
- **Template-based**: Efficient use of pre-designed templates
- **Modular Architecture**: Only loads required generator modules
- **Optimized Algorithms**: Efficient positioning and layout calculations

## Quality Assurance

### Output Quality
- **High Resolution**: Production-ready PDF output
- **Professional Templates**: Pre-designed base templates
- **Consistent Formatting**: Standardized output across generations
- **Color Management**: Proper color reproduction

### Data Integrity
- **Validation**: Comprehensive input validation
- **Error Handling**: Graceful failure recovery
- **Data Consistency**: Consistent data processing across generators
- **Type Safety**: Strong typing and conversion

This documentation represents the current state of the Generator app as of the analysis date. The app serves as the core engine for family tree chart generation with a robust, scalable architecture.