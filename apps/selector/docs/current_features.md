# Selector App - Current Features Documentation

## Overview
The Selector app provides a unified interface for selecting individuals from GEDCOM files. It serves as the bridge between file upload/browsing and chart generation, offering both dropdown selection and detailed individual listing.

## Core Features

### 1. Individual Selection Interface (`select_individual`)

**Purpose**: Unified individual selection from GEDCOM files
- **File Access Control**: Validates user authorization for file access
- **Individual Display**: Lists all individuals with PersonData conversion
- **Session Management**: Maintains file context across requests
- **Authentication Awareness**: Different behavior for logged-in vs anonymous users

**Selection Features**:
- **Comprehensive Listing**: Shows all individuals in the GEDCOM file
- **PersonData Conversion**: Robust conversion of raw GEDCOM data
- **Visual Interface**: Clean, accessible selection interface
- **Error Handling**: Comprehensive error management

### 2. Selection Confirmation (`confirm_selection`)

**Purpose**: Handle individual selection actions
- **Home Person Setting**: Ability to set individual as file's home person
- **Chart Generation**: Direct path to HUD interface for selected individual
- **Action Processing**: Supports multiple actions from selection
- **Session Persistence**: Stores selection for subsequent workflows

**Confirmation Actions**:
- **Set Home Person**: Marks individual as primary for the file
- **Generate Chart**: Routes to HUD for chart generation
- **Session Storage**: Persists selection across app navigation
- **User Routing**: Different redirect for authenticated vs anonymous users

### 3. User Authorization System

**Access Control**:
- **File Ownership Validation**: Ensures users can only access their files
- **Anonymous Support**: Handles anonymous user file access appropriately
- **Permission Checks**: 403 response for unauthorized access attempts
- **Session Integration**: Works with Django's authentication system

**Authorization Features**:
- **User File Access**: Authenticated users can access their own files
- **Anonymous Access**: Anonymous users can access public/non-owned files
- **Security Headers**: Proper HTTP status codes for access violations
- **Session Validation**: Maintains user context across requests

### 4. Data Processing Pipeline

#### PersonData Conversion
```python
# Robust conversion pattern
processed_individuals = []
for ind_id, individual in individuals.items():
    if isinstance(individual, dict):
        person = PersonData(**individual)
        processed_individuals.append(person)
    elif isinstance(individual, PersonData):
        processed_individuals.append(individual)
    else:
        person = PersonData(**individual.__dict__)
        processed_individuals.append(person)
```

#### Session Management
```python
# File context persistence
request.session["current_gedcom_file_id"] = gedcom_file.id

# Selection persistence for chart generation
request.session["selected_individual_id"] = individual_id
```

### 5. Template Integration

#### Template Context
- **Individual Data**: Complete PersonData objects for template rendering
- **File Information**: GEDCOM file metadata and status
- **Authentication Status**: User login state for template logic
- **Action Options**: Available actions for selected individual

#### Template Features
- **Selection Interface**: `selector/select_individual.html`
- **Error Handling**: `selector/error.html` for error conditions
- **Responsive Design**: Mobile-friendly selection interface
- **Accessibility**: Semantic HTML and keyboard navigation

## Current Working Features Summary

### ✅ Fully Functional
- Individual selection from GEDCOM files
- User authorization and access control
- Home person setting capability
- Direct chart generation routing
- Session management and persistence
- Error handling and validation
- Anonymous user support

### ⚠️ Partial Implementation
- Search functionality for large files
- Pagination for files with many individuals
- Advanced filtering options
- Batch selection capabilities

### ❌ Missing Features
- Individual search/filter
- Favorites or recently selected
- Advanced relationship-based selection
- Selection history
- Bulk operations

## Usage Flow

1. **File Context**: User accesses file from upload or browse
2. **Individual Display**: System shows all individuals in the file
3. **Selection Action**: User clicks individual to select
4. **Action Choice**: User chooses action (set home, generate chart)
5. **Workflow Continuation**: System routes to appropriate next step

## API Endpoints

### Primary Endpoints
- `/select/<str:file_id>/` - Individual selection interface (`select_individual`)
- `/confirm/<str:file_id>/` - Selection confirmation (`confirm_selection`)

### URL Patterns
```python
app_name = "selector"

urlpatterns = [
    path("select/<str:file_id>/", select_individual, name="select_individual"),
    path("confirm/<str:file_id>/", confirm_selection, name="confirm_selection"),
]
```

### HTTP Method Support
- **GET**: Individual listing and selection interface
- **POST**: Selection confirmation and action processing

## Data Flow Architecture

### Selection Flow
1. **File Validation**: Check file existence and user access
2. **Data Loading**: Extract individuals from parsed GEDCOM data
3. **Person Conversion**: Convert to PersonData objects for display
4. **Template Rendering**: Generate HTML selection interface
5. **Session Update**: Store file context for subsequent requests

### Confirmation Flow
1. **Action Processing**: Handle user's selected action
2. **Data Update**: Modify file or session as needed
3. **Workflow Routing**: Redirect to appropriate next step
4. **State Management**: Maintain user context and selections

## Integration Points

### Generator App Integration
- **GedcomFile Model**: Uses generator's file management
- **Template Mapping**: Integrates with generator's template system
- **Session Coordination**: Works with generator's session expectations

### HUD App Integration
- **Chart Generation**: Direct routing to HUD interface
- **Individual Selection**: Provides selected individual for chart generation
- **Settings Persistence**: Coordinates with HUD's settings system

### Browse App Integration
- **File Context**: Receives file context from browse workflow
- **Individual Detail**: Can redirect from browse to selection
- **Navigation Flow**: Part of cohesive user journey

### Upload App Integration
- **File Upload**: Receives newly uploaded files for selection
- **Initial Selection**: First selection after file upload
- **Session Coordination**: Maintains upload-to-selection workflow

## Technical Dependencies

### Required Apps
- `apps.generator` - GedcomFile model and file management
- `apps.parser` - PersonData model and individual representation

### Key Dependencies
- Django session framework
- Django authentication system
- Django ORM for database operations
- Django template system

### File Structure
```
apps/selector/
├── views.py (99 lines, selection and confirmation logic)
├── urls.py (URL routing)
├── templates/selector/
│   ├── select_individual.html (selection interface)
│   └── error.html (error handling)
└── migrations/ (database migrations)
```

## Performance Characteristics

### Data Processing
- **Memory Usage**: Moderate (loads all individuals into memory)
- **Processing Time**: O(n) conversion for PersonData objects
- **Database Queries**: Single query for GEDCOM file retrieval
- **Template Rendering**: Fast HTML generation for individual listing

### User Experience
- **Immediate Response**: Quick individual listing and selection
- **Session Persistence**: Maintains context across navigation
- **Error Recovery**: Graceful handling of error conditions
- **Mobile Support**: Responsive design for all devices

## Security Considerations

### Access Control
- **File Authorization**: Validates file ownership for authenticated users
- **Anonymous Support**: Secure handling of anonymous user access
- **Session Security**: Proper session management and validation
- **HTTP Security**: Appropriate status codes and responses

### Data Protection
- **Input Validation**: File ID and individual ID validation
- **SQL Injection Prevention**: Django ORM parameterization
- **XSS Prevention**: Django template auto-escaping
- **CSRF Protection**: Framework-level protection for forms

## User Experience Features

### Selection Interface
- **Comprehensive Listing**: All individuals displayed with details
- **Clear Navigation**: Back buttons and context preservation
- **Visual Hierarchy**: Organized display of individual information
- **Accessibility**: Semantic HTML and keyboard navigation

### Workflow Integration
- **Seamless Transitions**: Smooth flow from selection to chart generation
- **State Preservation**: Maintains user selections across app navigation
- **Error Recovery**: Clear error messages and recovery options
- **Progressive Enhancement**: Enhanced features for capable browsers

## Template System Details

### Selection Template Features
- **Individual Grid**: Organized display of all individuals
- **Interactive Elements**: Click-to-select functionality
- **Search Integration**: Placeholder for future search functionality
- **Responsive Layout**: Adapts to different screen sizes

### Error Handling Template
- **User-Friendly Messages**: Clear error descriptions
- **Recovery Options**: Links to appropriate next steps
- **Context Preservation**: Maintains user state during errors
- **Consistent Styling**: Matches overall site design

This documentation represents the current state of the Selector app as of the analysis date. The app provides a clean, focused interface for individual selection with solid security and integration into the broader NameChart workflow.