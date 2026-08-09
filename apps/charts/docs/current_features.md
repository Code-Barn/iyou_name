# Charts App - Current Features Documentation

## Overview
The Charts app provides functionality for generating and downloading family tree charts as PDF files. It serves as a bridge between the browsing interface and the core chart generation engine.

## Core Features

### 1. Chart Generation (`generate_chart`)

**Purpose**: Generate family tree charts as downloadable PDF files
- **Template Support**: Dynamic template selection (1-10 generations)
- **File Processing**: Validates GEDCOM file processing status
- **Individual Validation**: Ensures selected individual exists
- **Error Handling**: Comprehensive error management

**Generation Features**:
- **Multi-Template Support**: Uses generator app's template mapping
- **Dynamic Module Loading**: Runtime import of appropriate generators
- **PDF Output**: Production-ready PDF file generation
- **File Download**: Direct download with proper headers

### 2. Template Selection (`chart_selection`)

**Purpose**: Interface for selecting chart templates
- **Template Display**: Shows available chart templates
- **Session Integration**: Maintains template selection context
- **Individual Context**: Displays selected individual information
- **Template Mapping**: Uses centralized template configuration

**Selection Features**:
- **Default Template**: 4-generation chart as default
- **Template Information**: Displays all available templates
- **Individual Context**: Shows current individual for chart generation
- **Visual Interface**: Template selection form

### 3. Dynamic Template System

#### Template Integration
- **Generator App Integration**: Uses `template_mapping.py` from generator
- **Module Loading**: Dynamic import of generator modules
- **Function Resolution**: Runtime function discovery and execution
- **Configuration Access**: Template metadata and settings

#### Template Features
- **Version Support**: Templates 1-10 generation charts
- **File Management**: Base template file handling
- **Error Recovery**: Graceful handling of import failures
- **Consistent Interface**: Standardized generator function signatures

### 4. Data Processing Pipeline

#### Input Validation
```python
# GEDCOM file validation
gedcom_file = GedcomFile.objects.get(id=file_id)
if not gedcom_file.parsed_data:
    return render(request, "charts/error.html", {"error": "File not processed yet"})

# Individual validation
if individual_id not in individuals:
    return render(request, "charts/error.html", {"error": "Individual not found"})
```

#### Data Conversion
- **PersonData Conversion**: Robust type conversion for individuals
- **Template Data**: Extract individuals and families from parsed data
- **Generator Interface**: Standardized data format for generators

### 5. Error Handling System

#### Comprehensive Error Categories
- **File Not Found**: GEDCOM file doesn't exist
- **File Not Processed**: GEDCOM parsing incomplete
- **Individual Not Found**: Selected individual missing
- **Template Import Failure**: Generator module import error
- **Function Not Found**: Generator function missing
- **Generation Failure**: Chart generation errors

#### Error Response Pattern
```python
# Consistent error handling
return render(request, "charts/error.html", {"error": error_message})
```

### 6. File Download System

#### HTTP Response Management
- **Content Type**: `application/pdf` for proper download
- **Content Disposition**: Filename specification for download
- **File Content**: Binary PDF data transmission
- **Browser Integration**: Native download handling

#### Download Features
- **Direct Download**: No intermediate storage required
- **Filename Management**: Template-based filename generation
- **Browser Compatibility**: Standard HTTP headers
- **Error Fallback**: Error page on generation failure

## Template System Integration

### Generator App Connection
```python
# Dynamic template system
template_mapping = get_template_mapping()
template_config = template_mapping[template_id]
module = importlib.import_module(template_config["module"])
generator_function = getattr(module, template_config["function"])
```

### Template Configuration
- **Module Path**: Dynamic import from `apps.generator.utils`
- **Function Name**: Standardized generator function discovery
- **Base Template**: PDF template file for generation
- **Template Metadata**: Name and type information

## API Endpoints

### Primary Endpoints
- `/generate/<str:file_id>/<str:individual_id>/` - Chart generation (`generate_chart`)
- `/select/<str:file_id>/<str:individual_id>/` - Template selection (`chart_selection`)

### URL Patterns
```python
urlpatterns = [
    path("generate/<str:file_id>/<str:individual_id>/", generate_chart, name="generate_chart"),
    path("select/<str:file_id>/<str:individual_id>/", chart_selection, name="chart_selection"),
]
```

### HTTP Method Support
- **GET and POST**: Both endpoints support both methods
- **Flexible Input**: Template selection via POST, file context via URL parameters

## Data Flow Architecture

### Chart Generation Flow
1. **Request Processing**: Extract file_id, individual_id, template from request
2. **File Validation**: Verify GEDCOM file exists and is processed
3. **Individual Validation**: Confirm selected individual exists in file
4. **Template Resolution**: Get template configuration from generator app
5. **Module Loading**: Dynamically import appropriate generator
6. **Chart Generation**: Execute generator with individual and family data
7. **File Response**: Return PDF as HTTP download

### Template Selection Flow
1. **Context Setup**: Load file and individual information
2. **Template Mapping**: Get available template configurations
3. **Session Integration**: Maintain template selection state
4. **Interface Rendering**: Display template selection form
5. **User Interaction**: Handle template selection and redirect

## Integration Points

### Generator App Dependencies
- **Template Mapping**: Uses `get_template_mapping()` function
- **Generator Modules**: Dynamically imports from `apps.generator.utils`
- **Base Templates**: Uses template PDF files from generator's static files
- **Standardized Interface**: Follows generator app's function signatures

### Parser App Integration
- **PersonData Model**: Uses parser's individual representation
- **GEDCOM Data**: Depends on parsed GEDCOM structures
- **Family Data**: Uses families data from parser output

### Browse App Integration
- **File Context**: Receives file context from browse app
- **Individual Selection**: Gets individual selection from browse flow
- **Navigation Integration**: Provides next step in user workflow

## Current Working Features Summary

### ✅ Fully Functional
- Chart generation for all templates (1-10 generations)
- Dynamic template system with runtime module loading
- PDF file download with proper HTTP headers
- Template selection interface
- Comprehensive error handling
- Integration with generator app's template system

### ⚠️ Partial Implementation
- Error handling could be more user-friendly
- Template preview could be enhanced
- Generation progress tracking missing

### ❌ Missing Features
- Real-time generation progress
- Chart preview before download
- Batch chart generation
- Chart customization beyond template selection
- Generation history

## Usage Flow

1. **Individual Selection**: User selects individual from browse interface
2. **Template Choice**: User chooses chart template (or uses default)
3. **Chart Generation**: System generates PDF using appropriate generator
4. **File Download**: Browser automatically downloads generated PDF
5. **Navigation**: User can return to browse or HUD interface

## Technical Dependencies

### Required Apps
- `apps.generator` - Template mapping and generator modules
- `apps.parser` - PersonData model and GEDCOM data structures

### Key Dependencies
- Django HTTP response handling
- Python dynamic module loading (`importlib`)
- PDF generation through generator modules
- File download management

### File Structure
```
apps/charts/
├── views.py (171 lines, generation and selection logic)
├── urls.py (simple routing for 2 endpoints)
├── models.py (empty - no database models)
├── admin.py (empty - no admin interface)
├── static/charts/images/base_image_templates/ (PDF templates)
└── migrations/ (database migrations - minimal)
```

## Performance Characteristics

### Generation Process
- **Memory Usage**: Moderate (loads individual and family data)
- **Processing Time**: Depends on template complexity and family size
- **File I/O**: Reads base template PDF, writes generated PDF
- **Network**: Single HTTP response for file download

### Template System
- **Dynamic Loading**: Runtime module import (performance overhead)
- **Caching**: No caching of template configurations
- **Modularity**: Good separation of concerns

## Security Considerations

### Access Control
- **File Validation**: Validates file ownership indirectly through session
- **Input Sanitization**: Basic validation of file_id and individual_id
- **Path Security**: Uses generator's controlled template paths

### Data Protection
- **No Persistent Storage**: Generated files not stored on server
- **Session Integration**: Relies on session for file context
- **Error Information**: Generic error messages prevent information leakage

## User Experience Features

### Download Experience
- **Immediate Download**: No intermediate pages required
- **Proper Filename**: Template-based filename specification
- **Browser Integration**: Native download handling
- **Error Feedback**: Clear error messages for failures

### Template Selection
- **Visual Interface**: Clear template presentation
- **Context Preservation**: Maintains individual selection
- **Default Selection**: Sensible default template choice
- **Navigation Flow**: Logical progression from browse to generate

## Template System Details

### Supported Templates
- **1 Generation**: Individual-focused charts
- **2-7 Generation**: Multi-generational family trees
- **8-10 Generation**: Extended family charts (if available)

### Template Configuration
```python
template_config = {
    "module": "apps.generator.utils.image_Xgenerator",
    "function": "generate_Xgen_preview",
    "filename": "US_LETTER_XGEN_BW.pdf",
    "name": "X Generation Chart",
    "template_type": "final"
}
```

## Error Handling Strategy

### Error Categories
1. **Input Validation Errors**: Missing or invalid parameters
2. **Data Access Errors**: File or individual not found
3. **Processing Errors**: Template import or generation failures
4. **System Errors**: Unexpected runtime errors

### Error Response Format
- **Consistent Template**: Single error template for all errors
- **User-Friendly Messages**: Clear error descriptions
- **HTTP Status**: Appropriate status codes (implicitly handled by Django)

This documentation represents the current state of the Charts app as of the analysis date. The app serves as a focused bridge between data browsing and chart generation, with solid integration into the broader template system.