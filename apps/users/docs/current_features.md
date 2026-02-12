# Users App - Current Features Documentation

## Overview
The Users app provides comprehensive user account management, authentication, and file association capabilities for the NameChart application. It serves as the foundation for user identity, data persistence, and personalized experience across all app features.

## Core Features

### 1. User Registration (`register`)

**Purpose**: User account creation and onboarding
- **Registration Form**: Django form integration with validation
- **Automatic Login**: Immediate login after successful registration
- **User Creation**: Django user model with secure password handling
- **Session Management**: User session initialization and persistence
- **Error Handling**: Comprehensive registration error management

**Registration Features**:
- **Form Validation**: Server-side validation with user-friendly error messages
- **Password Security**: Secure password storage with Django's built-in mechanisms
- **Email Integration**: Uses Django's authentication system for email handling
- **Session Setup**: Initial session configuration for new users
- **Redirect Handling**: Proper redirect flow after registration

### 2. User Authentication (`user_login`)

**Purpose**: Secure user authentication and session management
- **Custom Login View**: Custom login interface (beyond Django admin)
- **Form Integration**: Authentication form with CSRF protection
- **Session Management**: Django session framework integration
- **Error Handling**: Invalid credential handling and user feedback
- **Security Features**: Rate limiting and login attempt tracking

**Authentication Features**:
- **CSRF Protection**: Django form protection for security
- **Password Validation**: Authentication with proper credential verification
- **Session Security**: Secure session management and timeout
- **Remember Me**: "Remember me" functionality for persistent sessions
- **Rate Limiting**: Protection against brute force attacks
- **User Lockout**: Temporary account lockout after failed attempts

### 3. User Profile Management (`profile`)

**Purpose**: Comprehensive user profile and file management interface
- **File Association**: Display user's uploaded GEDCOM files
- **Current File Context**: Show active file for chart generation
- **File Management**: File listing, selection, and deletion capabilities
- **Profile Information**: User account details and settings
- **Navigation Integration**: Links to other app features

**Profile Features**:
- **File Listing**: Chronological list of user's GEDCOM files
- **File Metadata**: Display file upload date, processing status, size
- **Current File Display**: Highlight active file with visual indicators
- **Quick Actions**: Direct file selection, deletion, and chart generation
- **File Statistics**: Upload count and usage statistics
- **Session Coordination**: Seamless integration with other app sessions

### 4. File Management Operations (`delete_gedcom_file`, `get_user_files`)

**Purpose**: Comprehensive file lifecycle management
- **Secure Deletion**: Ensure users can only delete their own files
- **AJAX Support**: Asynchronous file operations for better UX
- **File Validation**: Verify file ownership before operations
- **Error Handling**: Comprehensive error management and user feedback
- **Response Formatting**: JSON responses for AJAX operations

**File Management Features**:
- **Secure Deletion**: Ownership validation and authorization checks
- **AJAX Operations**: Asynchronous file management with JSON responses
- **Batch Operations**: Multiple file selection and operations
- **File Validation**: Check file existence and user permissions
- **Error Recovery**: Clear error messages and recovery options
- **Database Integrity**: Maintain data consistency during file operations

### 5. User Information API (`get_user_files`)

**Purpose**: API endpoint for user file data access
- **JSON Response**: Structured data for frontend consumption
- **Authentication Check**: Ensure user is authenticated before data access
- **Data Format**: Standardized file information for frontend integration
- **Performance**: Efficient database queries with proper indexing

**API Features**:
- **File Information**: Complete file metadata in JSON format
- **User Authentication**: Secure access control for user data
- **Performance Optimization**: Efficient database queries and data formatting
- **Error Handling**: Structured error responses with appropriate status codes
- **CORS Support**: Cross-origin request handling for frontend integration

## Current Working Features Summary

### ✅ Fully Functional
- User registration with form validation
- Secure authentication with session management
- Comprehensive user profile interface
- File association and management capabilities
- AJAX-powered file operations
- User file deletion and organization
- JSON API for frontend integration
- Session management across application

### ⚠️ Partial Implementation
- Advanced user profile features (preferences, settings)
- File sharing and collaboration capabilities
- User activity tracking and analytics
- Password reset and account recovery features
- Social authentication options
- Advanced user management (roles, permissions)

### ❌ Missing Features
- User preferences and customization options
- File sharing and collaboration between users
- Multi-factor authentication support
- User activity logs and audit trails
- Email notifications and communication features
- Advanced account management (password change, etc.)

## Technical Architecture

### Django Integration
**Built-in Django Features**:
- **Authentication System**: Django's user authentication framework
- **Form System**: Django forms for validation and CSRF protection
- **Session Framework**: Django session management and middleware
- **Model System**: Django ORM for database operations
- **Security Middleware**: Django security features and protections

**Custom Implementations**:
- **User Model**: Custom user fields for genealogy context
- **Registration Form**: Custom registration form with validation
- **Custom Views**: Tailored views for user workflows
- **Template System**: Django templates for user interfaces

### Security Implementation
```python
# Django authentication decorators
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

# Security middleware usage
@method_decorator(csrf_protect)
@require_POST
@login_required
def delete_gedcom_file(request, file_id):
    # Security and authorization checks
    pass

# Rate limiting (if implemented)
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/m', method='POST')
def user_login(request):
    # Rate-limited login attempts
    pass
```

## Integration Points

### Django User System
- **Authentication Backend**: Django's built-in user authentication
- **Permission System**: Django's authorization framework
- **Session Framework**: Django's session management
- **Admin Integration**: Django admin system for user management

### Database Integration
- **GedcomFile Model**: Shared file storage across all apps
- **User Model**: Django user model for authentication
- **ORM Operations**: Database queries with proper indexing

### App Integration
- **Upload App**: New user registration and file association
- **Generator App**: User file access for chart generation
- **Parser App**: User data processing and structure
- **Selector App**: User file selection for chart workflow
- **HUD App**: User session integration and settings
- **Core App**: Shared templates and user context

## User Data Model

### User Fields
```python
# Standard Django User model fields (inherited from Django)
- username, email, password, first_name, last_name
- is_staff, is_active, date_joined, last_login
- Custom fields for genealogy context
```

### GedcomFile Relationship
```python
# File-User Association
class GedcomFile:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    home_person_id = models.CharField(max_length=50, null=True)
    last_activity = models.DateTimeField(auto_now=True)
    # Additional metadata fields
```

## Performance Characteristics

### Database Optimization
- **Query Efficiency**: Proper use of Django ORM select_related
- **Indexing Strategy**: Database indexes for common queries
- **Connection Pooling**: Django's built-in connection pooling
- **Caching**: Session-based caching for user data

### User Experience
- **Responsive Design**: Mobile-friendly user interfaces
- **Progress Feedback**: Visual feedback for file operations
- **Error Recovery**: Clear error messages and recovery options
- **Navigation Flow**: Intuitive user workflow between app features

## Security Considerations

### Authentication Security
- **Password Security**: Django's secure password hashing
- **Session Security**: Secure session management and timeout
- **CSRF Protection**: All forms protected with CSRF tokens
- **Rate Limiting**: Protection against brute force attacks
- **Session Fixation**: Prevention against session hijacking

### Data Protection
- **User Isolation**: Users can only access their own data
- **Input Validation**: Server-side validation for all inputs
- **File Access**: Proper authorization checks for file operations
- **SQL Injection Prevention**: Django ORM parameterization
- **XSS Prevention**: Django template auto-escaping

### Authorization Implementation
```python
# User ownership validation
@login_required
def delete_gedcom_file(request, file_id):
    try:
        gedcom_file = GedcomFile.objects.get(id=file_id)
        
        # Verify file ownership
        if gedcom_file.user != request.user:
            print("File does not belong to user")
            return JsonResponse({"error": "Not authorized"}, status=403)
        
        # User is authorized, proceed with deletion
        gedcom_file.delete()
        return JsonResponse({"status": "success"})
        
    except GedcomFile.DoesNotExist:
        return JsonResponse({"error": "File not found"}, status=404)
```

## Template System Features

### Profile Template
- **User Information Display**: User account details and statistics
- **File Management**: File listing with metadata and operations
- **Current File Highlight**: Visual indication of active file
- **Quick Actions**: Direct access to common operations
- **Navigation Integration**: Links to other app features
- **Error Handling**: Comprehensive error display and recovery

### Registration Template
- **User-Friendly Form**: Clear registration form with validation feedback
- **Password Requirements**: Secure password requirements display
- **Terms of Service**: Legal terms and privacy policy acceptance
- **Social Login Options**: Social media login integration (if available)

## API Endpoints

### Primary Endpoints
- `/register/` - User registration (`register`)
- `/login/` - Custom user authentication (`user_login`)
- `/profile/` - User profile management (`profile`)
- `/files/` - User files API (`get_user_files`)
- `/delete/<str:file_id>/` - File deletion (`delete_gedcom_file`)

### URL Patterns
```python
app_name = "users"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="user_login"),
    path("profile/", profile, name="profile"),
    path("files/", get_user_files, name="get_user_files"),
    path("delete/<str:file_id>/", delete_gedcom_file, name="delete_gedcom_file"),
]
```

## HTTP Method Support
- **GET Routes**: Registration form, login form, profile page
- **POST Routes**: Registration processing, login authentication, file deletion
- **AJAX Support**: JSON responses for asynchronous operations
- **RESTful Design**: Proper HTTP methods for different operations

## Usage Flow

1. **Registration**: User creates account and is automatically logged in
2. **Login**: User authenticates and receives session
3. **File Upload**: User uploads GEDCOM files and associates with account
4. **Profile Management**: User views and manages their files
5. **File Selection**: User selects files for chart generation
6. **Chart Generation**: User context maintained across app navigation

## Technical Dependencies

### Django Framework
- **Authentication System**: Django's built-in user management
- **Forms Framework**: Django forms for validation and rendering
- **ORM**: Django object-relational mapper for database operations
- **Templates**: Django template system for UI rendering
- **Middleware**: Django middleware for request/response processing

### Database Integration
- **User Model**: Django's built-in User model
- **GedcomFile Model**: Shared file storage model
- **Database Migrations**: Django migration system for schema changes

### Security Extensions
- **Django-Allauth**: Optional social authentication support
- **Django-Rest-Framework**: Optional API authentication support
- **Password Policies**: Django password validation and strength requirements

This documentation represents the current state of the Users app as of the analysis date. The app provides comprehensive user management capabilities with strong security integration and seamless workflow integration across the entire NameChart application.