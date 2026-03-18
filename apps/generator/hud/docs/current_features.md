# HUD App - Current Features Documentation

## Overview
The HUD (Heads-Up Display) app provides an interactive web interface for customizing and previewing family tree charts in real-time. It serves as the user-facing frontend for chart generation, allowing users to adjust settings and see live previews before generating final charts.

## Core Features

### 1. Main HUD Interface (`display-tree/`)
- **Purpose**: Primary interactive interface for chart customization
- **Functionality**:
  - Live preview of family tree charts
  - Real-time settings adjustment
  - Template switching (1-7 generation charts)
  - Responsive design with zoom controls
  - Session persistence for settings

### 2. Template System
**Supported Templates**:
- 1 Generation Chart (`1gen_settings.html`)
- 2 Generation Chart (`2gen_settings.html`) 
- 3 Generation Chart (`3gen_settings.html`)
- 4 Generation Chart (`4gen_settings.html`)
- 5 Generation Chart (`5gen_settings.html`)
- 6 Generation Chart (`6gen_settings.html`)
- 7 Generation Chart (`7gen_settings.html`)
- Default settings fallback (`default_settings.html`)

**Template Features**:
- Dynamic settings panel loading
- Template-specific configuration options
- Individual settings inheritance between templates

### 3. Settings Management

#### Color Customization
- **Primary Individual**: Background, font, birth info, death info colors
- **Parent Generation**: Father/mother specific colors (2gen+)
- **Stroke Colors**: Default and info stroke colors
- **Color Pickers**: Interactive color selection for all color options

#### Typography Settings
- **Font Family**: Arial (with support for additional fonts)
- **Font Sizes**: 
  - Primary name font size
  - Date info font size
  - Place info font size
  - Parent generation font sizes (2gen+)

#### Positioning & Transformation
- **Translation Controls**: X/Y positioning for all text elements
- **Rotation Controls**: Angle adjustment for name, birth, death info
- **Multi-generation Positioning**: Parent-specific positioning (2gen+)

#### Composite Settings (2gen+)
- **Overlay Scaling**: 1gen scale for composite charts
- **Overlay Positioning**: X/Y coordinates for overlay placement

### 4. Live Preview System

#### Preview Generation
- **Real-time Updates**: Settings changes trigger immediate preview refresh
- **Template-specific Generation**: Different generation logic per template
- **Buffer Integration**: Uses generator app's buffer system for efficiency

#### Preview Features
- **Zoom Controls**: Interactive zoom in/out with mouse wheel support
- **Rotation Controls**: Chart rotation capability
- **Visual Feedback**: Border highlighting on preview update
- **Error Handling**: Graceful fallback for preview errors

### 5. Session Management

#### Settings Persistence
- **Session Storage**: User settings saved to Django session
- **Template Memory**: Remembers last selected template
- **Individual Memory**: Remembers selected individual
- **File Context**: Maintains GEDCOM file association

#### Data Inheritance
- **1gen Settings Inheritance**: 1gen settings inherited by higher generations
- **Cumulative Settings**: Multi-generational settings accumulation
- **Settings Storage**: localStorage for client-side persistence

### 6. API Endpoints

#### Core Preview Endpoints
- `/get-template-preview/<template_id>/` - Generic template preview
- `/get-1gen-preview/` - Specific 1gen preview (legacy support)
- `/get-family-data/` - Family data retrieval

#### Settings Management
- `/save-settings/` - Save user settings to session
- `/apply-settings-change/` - Apply incremental setting changes
- `/get-settings-panel/<template_name>/` - Dynamic settings panel HTML

#### Utility Endpoints
- `/update-settings-timestamp/` - Force preview reload
- `/get-file-individuals/` - Get individual list for fallback
- `/get-buffer-stats/` - Buffer system statistics

#### Test Endpoints
- `/test-enhanced-1gen-preview/` - Enhanced 1gen testing
- `/test-enhanced-1gen-comparison/` - Side-by-side comparison testing

### 7. JavaScript Architecture

#### Module Structure
```
HUD.Main - Core functionality (form access, template management)
HUD.Preview - Preview generation and display
HUD.Storage - Settings persistence (localStorage/sessionStorage)
HUD.Session - Session management
HUD.Utils - Utility functions
HUD.Templates - Template management
HUD.Sliders - Interactive slider controls
HUD.Rotation - Chart rotation functionality
```

#### Key JavaScript Features
- **Modular Architecture**: Organized into functional modules
- **Event Handling**: Comprehensive event listeners for UI interactions
- **Settings Synchronization**: Client-server settings sync
- **Error Recovery**: Fallback mechanisms for failed operations
- **Performance Optimization**: Debounced updates and efficient DOM manipulation

### 8. Error Handling & Fallbacks

#### Client-side Error Handling
- **Network Failures**: Graceful degradation for API failures
- **Invalid Settings**: Validation and default fallbacks
- **Template Loading**: Fallback to default template on errors
- **Preview Failures**: Error messages and retry mechanisms

#### Server-side Error Handling
- **Missing Data**: Validation for required parameters
- **File Processing**: Checks for GEDCOM processing status
- **Individual Validation**: Validates individual existence
- **Template Validation**: Checks for template availability

### 9. Responsive Design

#### Mobile Support
- **Responsive Layout**: Adapts to different screen sizes
- **Touch Support**: Touch-friendly controls for mobile devices
- **Zoom Optimization**: Mobile-optimized zoom controls

#### Desktop Features
- **Keyboard Shortcuts**: Keyboard navigation support
- **Mouse Wheel Zoom**: Desktop-specific zoom interaction
- **Hover States**: Enhanced desktop interactivity

### 10. Integration Points

#### Generator App Integration
- **Template Mapping**: Uses generator's template mapping system
- **Buffer System**: Leverages generator's buffer management
- **Image Generation**: Calls generator's image generation functions

#### Parser App Integration
- **Person Data**: Uses parser's PersonData model
- **GEDCOM Processing**: Depends on parser's GEDCOM processing
- **Family Relationships**: Uses parser's relationship data

## Current Working Features Summary

### ✅ Fully Functional
- Live preview generation for all templates (1-7)
- Real-time settings adjustment
- Template switching with settings inheritance
- Color customization for all elements
- Font size and family customization
- Position and rotation controls
- Session persistence
- Responsive design
- Error handling
- API endpoints
- JavaScript module architecture

### ⚠️ Partial Implementation
- Some advanced positioning controls may need refinement
- Composite settings could use more intuitive UI
- Mobile experience could be enhanced

### ❌ Known Issues
- Session save failures (non-critical, localStorage fallback works)
- Some template-specific settings may have redundant validation
- Console warnings for deprecated function calls (cleanup needed)

## Usage Flow

1. **User Selection**: User selects individual and GEDCOM file
2. **Template Choice**: User chooses template (defaults to 1gen)
3. **Settings Adjustment**: User modifies visual settings via controls
4. **Live Preview**: Preview updates in real-time as settings change
5. **Template Switching**: User can switch templates with settings inheritance
6. **Final Generation**: User generates final chart via generator app

## Technical Dependencies

### Required Apps
- `apps.generator` - Chart generation and template mapping
- `apps.parser` - GEDCOM parsing and data models

### Key Dependencies
- Django session framework
- JavaScript ES6+ modules
- Bootstrap CSS framework
- jQuery (for some AJAX operations)

### File Structure
```
apps/hud/
├── static/hud/
│   ├── css/hud.css
│   ├── js/hud-organized.js (main)
│   ├── js/hud.js (legacy)
│   └── images/preview_image_templates/
├── templates/hud/
│   ├── settings/ (7 template settings files)
│   ├── display_tree.html (main interface)
│   └── error.html
└── views.py (926 lines, comprehensive functionality)
```

This documentation represents the current state of the HUD app as of the analysis date. The app is functionally complete for its core purpose but has opportunities for optimization and cleanup.