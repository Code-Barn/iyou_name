# Browse App - Current Features Documentation

## Overview
The Browse app provides functionality for navigating and viewing individual records from uploaded GEDCOM files. It serves as the primary interface for browsing family data and accessing individual details before chart generation.

## Core Features

### 1. Individual Browsing (`browse_individuals`)

**Purpose**: Display all individuals from the currently selected GEDCOM file
- **Session Integration**: Maintains current GEDCOM file context across requests
- **File Validation**: Ensures file exists and is processed
- **User Authorization**: Validates file ownership for authenticated users
- **Data Processing**: Converts raw GEDCOM data to PersonData objects

**Key Functionality**:
- POST handling for file selection and redirects
- Session management for file context
- Comprehensive logging for debugging
- Error handling for missing/unprocessed files

### 2. Individual Selection (`select_individual`)

**Purpose**: Redirect to unified selector interface
- **File Context Management**: Maintains GEDCOM file association
- **User Type Handling**: Different logic for authenticated vs anonymous users
- **File Discovery**: Automatically finds available files for user context
- **Redirect Logic**: Routes to appropriate selector interface

**Selection Features**:
- Authenticated users: Access their uploaded files
- Anonymous users: Access publicly available files
- File fallback: Redirects to upload if no files available
- Most recent file selection

### 3. Individual Detail View (`individual_detail`)

**Purpose**: Comprehensive individual information display
- **Family Relationships**: Complete family network visualization
- **Data Conversion**: Robust PersonData object handling
- **Home Person Detection**: Identifies primary individual in file
- **JSON Integration**: Provides data for JavaScript interactions

**Detail Features**:
- **Direct Family**: Father, mother, spouses, children
- **Extended Family**: Siblings, step relationships, adoptive/foster parents
- **Relationship Validation**: Ensures family members exist in dataset
- **Debug Information**: Extensive logging for family relationship resolution

### 4. Data Processing & Conversion

**PersonData Conversion**:
```python
# Robust conversion pattern
if isinstance(individual, dict):
    person = PersonData(**individual)
elif isinstance(individual, PersonData):
    person = individual  # Already correct type
else:
    person = PersonData(**individual.__dict__)  # Fallback conversion
```

**Family Relationship Resolution**:
- **Lookup Dictionary**: Creates efficient person lookup
- **Existence Validation**: Checks if family members exist in dataset
- **Object Conversion**: Converts all related individuals to PersonData objects
- **Relationship Categories**: Handles all GEDCOM relationship types

### 5. Session Management

**Session Data**:
- `current_gedcom_file_id`: Active GEDCOM file context
- File persistence across page navigation
- User-specific file association

**Session Features**:
- File context maintenance
- Redirect capability to specific individuals
- User authorization through file ownership

### 6. Error Handling & Validation

**Validation Checks**:
- File existence verification
- User ownership validation
- GEDCOM processing status
- Individual existence validation

**Error Scenarios**:
- No GEDCOM file selected
- File not processed yet
- GEDCOM file not found
- Individual not found
- Unauthorized access attempts

### 7. User Type Support

**Authenticated Users**:
- Personal file access
- File ownership validation
- Personal file listing

**Anonymous Users**:
- Public file access
- Session-based file management
- Automatic cleanup on session expiry

### 8. Logging & Debugging

**Comprehensive Logging**:
- File retrieval status
- Data processing steps
- Family relationship resolution
- Individual conversion details
- Error conditions and stack traces

**Debug Information**:
- Individual count reporting
- Data type verification
- Family member existence checks
- JSON serialization for frontend

## Current Working Features Summary

### ✅ Fully Functional
- Individual browsing from GEDCOM files
- Detailed individual information display
- Family relationship resolution
- User authentication and authorization
- Session-based file management
- Error handling and validation
- Comprehensive logging system

### ⚠️ Partial Implementation
- Some debugging information could be moved to proper debug levels
- Family relationship display could be enhanced
- Search functionality not implemented

### ❌ Missing Features
- Search/filter capabilities for large files
- Pagination for files with many individuals
- Advanced relationship visualization
- Export functionality for individual data

## Usage Flow

1. **File Selection**: User selects GEDCOM file (or redirected from upload)
2. **Individual Browsing**: System displays all individuals in file
3. **Individual Selection**: User clicks on individual for details
4. **Family Resolution**: System resolves all family relationships
5. **Detail Display**: Comprehensive individual and family information shown
6. **Navigation Options**: User can generate charts or browse other individuals

## API Endpoints

### Primary Endpoints
- `/` - Browse all individuals (`browse_individuals`)
- `/select/` - Individual selection interface (`select_individual`)
- `/person/<str:ind_id>/` - Individual detail view (`individual_detail`)

### URL Patterns
```python
urlpatterns = [
    path("", browse_individuals, name="browse_individuals"),
    path("select/", select_individual, name="select_individual"),
    path("person/<str:ind_id>/", individual_detail, name="individual_detail"),
]
```

## Data Flow Architecture

### Input Processing
1. **Session Context**: Retrieve current GEDCOM file ID
2. **File Validation**: Check file existence and processing status
3. **Authorization**: Validate user permissions for file access
4. **Data Extraction**: Get individuals from parsed GEDCOM data

### Data Processing
1. **Type Conversion**: Convert dictionaries to PersonData objects
2. **Relationship Resolution**: Build complete family network
3. **Existence Validation**: Ensure referenced individuals exist
4. **Context Preparation**: Prepare data for template rendering

### Output Generation
1. **Template Rendering**: Use Django templates for HTML generation
2. **JSON Serialization**: Provide data for JavaScript interactions
3. **Context Variables**: Supply all necessary template context
4. **Error Responses**: Handle error conditions gracefully

## Integration Points

### Generator App Integration
- **GedcomFile Model**: Uses generator's file management
- **PersonData Model**: Relies on parser's person representation
- **Template System**: Prepares data for chart generation

### Parser App Dependencies
- **PersonData Model**: Core data structure for individuals
- **GEDCOM Processing**: Depends on parsed GEDCOM data
- **Relationship Data**: Uses parser's relationship extraction

### Upload App Integration
- **File Context**: Maintains context from upload process
- **Redirect Flow**: Handles file selection redirects
- **Session Management**: Coordinates with upload session handling

## Technical Dependencies

### Required Apps
- `apps.generator` - GedcomFile model and file management
- `apps.parser` - PersonData model and GEDCOM data structures

### Key Dependencies
- Django session framework
- Django authentication system
- Django ORM for database operations
- Python logging system

### File Structure
```
apps/browse/
├── views.py (304 lines, comprehensive functionality)
├── urls.py (12 lines, simple routing)
├── migrations/ (database migrations)
└── README.md (empty)
```

## Performance Characteristics

### Data Processing
- **Memory Usage**: Loads all individuals into memory for relationship resolution
- **Processing Time**: O(n) conversion for individuals, O(k) for relationships
- **Database Queries**: Single query for GEDCOM file retrieval

### Caching Strategy
- **Session Caching**: File context maintained in session
- **Object Caching**: PersonData objects created once per request
- **No Persistent Caching**: Fresh data loaded each request

## Security Considerations

### Access Control
- **User Authorization**: Validates file ownership for authenticated users
- **Anonymous Access**: Limited to publicly available files
- **Session Security**: Proper session management for file context

### Data Validation
- **Input Validation**: Individual ID validation
- **Existence Checks**: Validates file and individual existence
- **Type Safety**: Robust type conversion with fallbacks

## User Experience Features

### Navigation
- **Breadcrumb Context**: File and individual identification
- **Back Navigation**: Integration with core navigation components
- **Quick Actions**: Direct links to chart generation

### Information Display
- **Comprehensive Details**: Complete individual information
- **Family Context**: Visual family relationship display
- **Debug Information**: Development-friendly error messages

This documentation represents the current state of the Browse app as of the analysis date. The app serves as a crucial bridge between file upload and chart generation, providing essential data browsing and individual detail functionality.