# Upload App - Current Features Documentation

## Overview
The Upload app serves as the primary entry point for the NameChart application, handling GEDCOM file uploads, parsing, and initial user flow setup. It provides both upload interface and file management functionality.

## Core Features

### 1. File Upload Interface (`upload_file`)

**Purpose**: Display file upload form and template information
- **Upload Form**: User-friendly interface for GEDCOM file submission
- **Template Integration**: Displays available chart templates from generator
- **User Context**: Different behavior for authenticated vs anonymous users
- **Error Handling**: Comprehensive error management for upload process

**Upload Features**:
- **GEDCOM File Support**: Specialized for genealogy file format
- **Template Preview**: Shows available chart templates and options
- **File Validation**: Client and server-side validation
- **Progress Feedback**: Visual feedback during upload process

### 2. Upload and Generate Workflow (`upload_and_generate`)

**Purpose**: Main workflow combining upload with immediate processing
- **File Processing**: Direct GEDCOM parsing on upload
- **Data Validation**: Comprehensive validation of parsed data
- **Database Storage**: Save file and parsed data to database
- **Workflow Integration**: Seamlessly transition to selection interface

**Processing Pipeline**:
```python
# Complete processing workflow
1. File Upload: Handle GEDCOM file upload
2. Content Reading: Read file content directly for parsing
3. Encoding Conversion: Convert to UTF-8 for parsing
4. GEDCOM Parsing: Extract family and individual data
5. Data Storage: Store file metadata and parsed data
6. Session Setup: Initialize session for next steps
7. Workflow Transition: Redirect to individual selection
```

### 3. File Management (`select_gedcom_file`, `set_current_gedcom_file`)

**Purpose**: User's uploaded file management interface
- **File Listing**: Display user's uploaded GEDCOM files
- **File Selection**: Allow users to select previously uploaded files
- **Session Management**: Set active file context
- **File Switching**: Easy switching between different genealogy projects

**Management Features**:
- **File Metadata**: Display upload date, processing status, file size
- **File Actions**: Options to select, delete, or manage files
- **Batch Operations**: Handle multiple files efficiently
- **File Validation**: Ensure file integrity and accessibility

### 4. Anonymous File Cleanup (`delete_anonymous_file`)

**Purpose**: AJAX endpoint for cleaning up anonymous user files
- **AJAX Interface**: Asynchronous file deletion
- **Anonymous Support**: Handle non-authenticated user files
- **Security Validation**: Ensure only anonymous files can be deleted
- **Cleanup Response**: JSON response for operation status

**Cleanup Features**:
- **File Validation**: Verify file exists and is anonymous
- **Safe Deletion**: Proper file removal with error handling
- **Response Formatting**: JSON response for AJAX integration
- **Error Handling**: Comprehensive error reporting

## GEDCOM Processing Pipeline

### File Content Processing
```python
# Multi-stage processing pipeline
gedcom_content_bytes = gedcom_file.read()
gedcom_content = convert_to_utf8(gedcom_content_bytes)  # Encoding conversion
family_data = parse_gedcom_data(gedcom_content)     # GEDCOM parsing
```

### Data Validation
```python
# Comprehensive validation checks
if not isinstance(family_data.get("individuals"), dict):
    logger.error("family_data['individuals'] is not a dictionary")
    raise ValueError("family_data['individuals'] must be a dictionary")
```

### Database Storage
```python
# Complete file record creation
gedcom_model = GedcomFile.objects.create(
    file=ContentFile(gedcom_content_bytes, name=gedcom_file.name),
    user=request.user if request.user.is_authenticated else None,
)

# Store parsed data with relationships
gedcom_model.parsed_data = {
    "individuals": {ind_id: person.to_dict() for ind_id, person in family_data["individuals"].items()},
    "families": family_data.get("families", {}),
    "root_individuals": family_data.get("root_individuals", []),
}

# Set metadata and status
gedcom_model.home_person_id = family_data["root_individuals"][0] if family_data["root_individuals"] else None
gedcom_model.is_processed = True
gedcom_model.processing_date = timezone.now()
```

## Current Working Features Summary

### ✅ Fully Functional
- GEDCOM file upload with validation
- Complete GEDCOM parsing pipeline
- Database storage of files and parsed data
- User file management interface
- Anonymous file cleanup system
- Session management for workflow
- Template integration from generator app
- Error handling throughout pipeline

### ⚠️ Partial Implementation
- File upload progress tracking
- Multiple file upload support
- File validation previews
- Advanced file management features

### ❌ Missing Features
- Drag-and-drop file upload
- File format validation beyond GEDCOM
- File processing progress reporting
- File sharing and collaboration
- Advanced file organization

## Usage Flow

1. **File Upload**: User selects and uploads GEDCOM file
2. **Processing**: System parses and validates file content
3. **Storage**: File and parsed data stored in database
4. **Session Setup**: User session configured with file context
5. **Selection**: User redirected to individual selection interface
6. **Chart Generation**: Complete workflow to chart creation

## API Endpoints

### Primary Endpoints
- `/upload/` - File upload form display (`upload_file`)
- `/upload/` - Upload and generate workflow (`upload_and_generate`)
- `/select/<str:file_id>/` - File selection (`select_gedcom_file`)
- `/set/<str:file_id>/` - Set current file (`set_current_gedcom_file`)
- `/delete/` - Anonymous file cleanup (`delete_anonymous_file`)

### AJAX Endpoints
- `/delete/` (POST) - Asynchronous file deletion
- Files can be deleted via AJAX for better UX

### URL Patterns
```python
app_name = "upload"

urlpatterns = [
    path("", upload_file, name="home"),
    path("select/<str:file_id>/", select_gedcom_file, name="select_gedcom_file"),
    path("set/<str:file_id>/", set_current_gedcom_file, name="set_current_gedcom_file"),
]
```

## Technical Dependencies

### Required Apps
- `apps.generator` - GedcomFile model and RegisterForm
- `apps.parser` - GEDCOM parsing utilities and PersonData model

### Key Dependencies
- Django file handling and storage system
- Django forms for validation and rendering
- Django session framework
- Django ORM for database operations
- Django authentication system

### External Libraries
- **ged4py**: GEDCOM file format parsing
- **chardet**: Character encoding detection
- **content-management**: Django's ContentFile handling

## File Structure
```
apps/upload/
├── views.py (154 lines, comprehensive upload and file management)
├── urls.py (URL routing)
├── templates/upload/
│   ├── upload_file.html (main upload interface)
│   └── error.html (error handling)
├── signals.py (Django signals integration)
└── migrations/ (database migrations)
```

## Performance Characteristics

### File Processing
- **Memory Usage**: File content loaded entirely into memory
- **Processing Time**: Depends on file size and complexity
- **Database Storage**: Efficient storage of parsed data
- **Session Management**: Lightweight session data

### Scalability
- **File Size Limits**: Implicit browser and server limits
- **Concurrent Uploads**: Django handles concurrent requests
- **Storage Management**: Database storage scales with user base
- **Parsing Performance**: Optimized GEDCOM parsing

## Security Considerations

### File Upload Security
- **File Type Validation**: GEDCOM format validation
- **File Size Limits**: Server-side file size restrictions
- **Content Scanning**: Basic validation of uploaded content
- **Path Traversal Prevention**: Django's secure file handling

### User Data Protection
- **User Isolation**: Users can only access their own files
- **Anonymous File Management**: Secure handling of anonymous uploads
- **Session Security**: Proper session management and cleanup
- **CSRF Protection**: Django form protection enabled

### Access Control
```python
# File ownership validation
if gedcom_file.user and gedcom_file.user != request.user:
    return HttpResponse(b"Unauthorized", status=403)

# Anonymous file operations
gedcom_file.objects.get(id=file_id, user=None)  # Only anonymous files
```

## User Experience Features

### Upload Interface
- **Drag-and-Drop Ready**: Modern upload interface potential
- **Progress Feedback**: Visual feedback during upload
- **Error Recovery**: Clear error messages and recovery options
- **Mobile Support**: Responsive design for mobile devices

### File Management
- **File Organization**: Clear file listing and metadata
- **Quick Actions**: Direct access to common operations
- **Workflow Integration**: Seamless flow to chart generation
- **Multi-File Support**: Handle multiple genealogy projects

## Integration Points

### Generator App Integration
- **GedcomFile Model**: Central file storage model
- **Template Mapping**: Uses generator's template system
- **RegisterForm**: User registration form from generator
- **Database Sharing**: Shared database models and structure

### Parser App Integration
- **GEDCOM Parsing**: Uses parser's gedcom4py utilities
- **PersonData Model**: Stores individuals in standardized format
- **Character Encoding**: Robust encoding detection and conversion
- **Data Validation**: Validates parsed data structure

### Selector App Integration
- **Workflow Transition**: Direct routing to individual selection
- **Session Coordination**: Maintains session context
- **File Context**: Provides file context for selection
- **Template Preferences**: Default template selection

### Users App Integration
- **User Registration**: Integration with user management
- **Authentication**: Django auth system integration
- **Profile Connection**: Links to user profile management
- **File Association**: User-file relationship management

## Template System Details

### Upload Template Features
- **File Upload Form**: Modern HTML5 file input
- **Template Display**: Available chart templates and options
- **User Context**: Different interface for logged-in vs anonymous users
- **Error Handling**: Comprehensive error display and recovery

### Form Integration
```html
<!-- Django form integration -->
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Upload and Process</button>
</form>
```

## Error Handling Strategy

### Processing Errors
- **File Format Errors**: Invalid or corrupted GEDCOM files
- **Encoding Issues**: Character encoding problems
- **Parsing Errors**: GEDCOM structure validation failures
- **Storage Errors**: Database or file system errors

### User Communication
- **Clear Error Messages**: User-friendly error descriptions
- **Recovery Options**: Alternative actions when errors occur
- **Logging**: Comprehensive error tracking for debugging
- **Status Reporting**: HTTP status codes for API responses

This documentation represents the current state of the Upload app as of the analysis date. The app serves as a comprehensive entry point with robust file processing, security measures, and seamless integration into the broader NameChart workflow.