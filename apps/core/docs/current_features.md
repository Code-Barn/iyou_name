# Core App - Current Features Documentation

## Overview
The Core app serves as the central foundation for the NameChart application, providing shared components, base templates, middleware, and common utilities. It acts as the architectural backbone that other apps depend on for consistent functionality and user experience.

## Core Features

### 1. Base Template System

**Purpose**: Provides foundational HTML templates for consistent UI
- **Base Template**: `templates/core/base.html` - Master template for all pages
- **Component Library**: Reusable UI components for common patterns
- **Navigation Framework**: Consistent navigation and user interface elements
- **Responsive Design**: Mobile-friendly base layout structure

#### Template Components
- **Individual Header**: Standardized individual information display
- **Basic Info**: Common information display patterns
- **Family Info**: Family relationship presentation components
- **Locations**: Geographic and location-based information display
- **Back Button**: Consistent navigation back button

### 2. Static Asset Management

**CSS Framework**: `static/core/css/style.css`
- **Global Styles**: Site-wide CSS definitions
- **Component Styles**: Styled components for reuse
- **Responsive Design**: Mobile-first CSS approach
- **Theme Support**: Base styling for custom themes

**Image Assets**: Site branding and icons
- **Logo Variants**: Multiple logo formats and sizes
- **Brand Images**: Created in DeKalb branding
- **Favicon**: Site icon for browser tabs
- **Icon Set**: Navigation and UI icon collection

#### Asset Organization
```
static/core/
├── css/
│   └── style.css (global styles)
├── images/
│   ├── createdinDeKalb.png (brand origin)
│   ├── namechartharp.png (brand identity)
│   ├── tinylogo.png (small logo)
│   ├── tinynamelogo.png (alternative logo)
│   ├── tinyname.png (brand text)
│   └── favicon.ico (browser icon)
└── favicon.ico (root favicon)
```

### 3. Middleware System

**SessionCleanupMiddleware**: Automated session and file management
- **Session Expiry Detection**: Monitors session lifecycle
- **Anonymous File Cleanup**: Automatic removal of anonymous user files
- **Resource Management**: Prevents accumulation of orphaned files
- **User Privacy**: Ensures data cleanup for anonymous sessions

#### Middleware Features
- **Request Lifecycle**: Hooks into Django request/response cycle
- **Session Monitoring**: Tracks session state and expiration
- **File Association**: Links anonymous files to session lifecycle
- **Graceful Cleanup**: Safe file deletion with error handling

### 4. Navigation Components

**Back Button Component**: Consistent navigation pattern
- **Context Awareness**: Maintains navigation context
- **Breadcrumb Support**: Integration with breadcrumb systems
- **URL Generation**: Dynamic back link creation
- **State Preservation**: Maintains user state during navigation

**Individual Header Component**: Standardized person display
- **Name Display**: Consistent individual name formatting
- **Life Dates**: Birth/death information presentation
- **Relationship Context**: Family position information
- **Visual Hierarchy**: Clear information hierarchy

### 5. Base Layout Structure

#### HTML Template Architecture
```html
<!-- base.html structure -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}NameChart{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'core/css/style.css' %}">
    <link rel="icon" href="{% static 'core/images/favicon.ico' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        {% include 'core/components/individual_header.html' %}
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        {% include 'core/components/back_button.html' %}
    </footer>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 6. Component System

#### Reusable Component Templates
- **Individual Header**: Standardized person information display
- **Basic Info**: Generic information display component
- **Family Info**: Family relationship information
- **Locations**: Geographic and location data display
- **Back Button**: Navigation component with context

#### Component Features
- **Template Inheritance**: Component-based template structure
- **Parameter Passing**: Flexible component configuration
- **Context Integration**: Django template context support
- **Customization**: Overridable component behavior

### 7. Brand Identity System

#### Visual Branding
- **Created in DeKalb**: Geographic origin story
- **NameChart Harp**: Visual brand identity
- **Logo System**: Multiple logo variants for different contexts
- **Consistent Theme**: Unified visual presentation

#### Brand Assets
- **Primary Logo**: Main brand identifier
- **Alternative Logos**: Context-specific variations
- **Color Scheme**: Consistent color palette
- **Typography**: Standardized font usage

## Integration Points

### App Dependencies
All other apps depend on Core for:
- **Base Templates**: Extended through template inheritance
- **CSS Framework**: Global styling and responsive design
- **Components**: Reusable UI components
- **Middleware**: Session cleanup functionality

### Template Usage Pattern
```python
# In other app templates
{% extends 'core/base.html' %}

{% block title %}Individual Details{% endblock %}

{% block content %}
    {% include 'core/components/individual_header.html' with individual=person %}
    <!-- App-specific content -->
{% endblock %}
```

## Current Working Features Summary

### ✅ Fully Functional
- Base template system with inheritance
- Global CSS framework
- Component library for UI patterns
- Session cleanup middleware
- Static asset management
- Brand identity system
- Navigation components

### ⚠️ Partial Implementation
- Component documentation could be enhanced
- CSS could be more modular
- Middleware could be more configurable

### ❌ Missing Features
- Advanced component system (props, events)
- Theme switching capability
- Asset optimization and bundling
- Accessibility features
- Internationalization support

## Usage Flow

1. **Template Inheritance**: Other apps extend core/base.html
2. **Component Usage**: Apps include reusable components
3. **Asset Loading**: Static CSS and images loaded automatically
4. **Middleware Processing**: Session cleanup runs on each request
5. **Brand Application**: Consistent branding across all pages

## Technical Dependencies

### Django Integration
- **Template System**: Django template inheritance and includes
- **Static Files**: Django static file management
- **Middleware**: Django middleware framework
- **Context Processors**: Template context integration

### Required Apps
- **All Other Apps**: Core serves as foundation for entire project

### File Structure
```
apps/core/
├── templates/core/
│   ├── base.html (master template)
│   └── components/ (reusable UI components)
├── static/core/
│   ├── css/style.css (global styles)
│   └── images/ (brand assets and icons)
├── middleware.py (session cleanup)
├── models.py (empty - no database models)
├── views.py (empty - no direct views)
└── signals.py (empty - available for Django signals)
```

## Performance Characteristics

### Asset Management
- **CSS Loading**: Single global stylesheet
- **Image Optimization**: Optimized logo and icon files
- **Caching**: Browser caching through static file handling
- **CDN Ready**: Static asset structure supports CDN deployment

### Middleware Performance
- **Session Monitoring**: Minimal overhead per request
- **File Cleanup**: Background processing to avoid request delays
- **Database Efficiency**: Optimized queries for file cleanup
- **Memory Management**: Proper cleanup of file references

## Security Considerations

### Session Management
- **Automatic Cleanup**: Prevents data accumulation
- **Anonymous Privacy**: Removes anonymous user data on session expiry
- **File Association**: Secure linking of files to sessions
- **Resource Limits**: Prevents unlimited file accumulation

### Template Security
- **XSS Prevention**: Django template auto-escaping
- **CSRF Protection**: Framework-level protection
- **Content Security**: Safe static file serving
- **Input Validation**: Template-level input sanitization

## User Experience Features

### Consistent Interface
- **Unified Design**: Common look and feel across all apps
- **Navigation Patterns**: Predictable navigation behavior
- **Component Reuse**: Familiar UI elements throughout
- **Responsive Design**: Mobile-friendly interface

### Brand Experience
- **Professional Identity**: Consistent branding
- **Geographic Connection**: "Created in DeKalb" story
- **Visual Recognition**: Distinctive logo and color scheme
- **Trust Building**: Professional presentation

## Component System Details

### Individual Header Component
```html
<!-- core/components/individual_header.html -->
<div class="individual-header">
    <h1>{{ individual.full_name }}</h1>
    {% if individual.birth_date or individual.death_date %}
        <p class="life-dates">
            {{ individual.birth_date|default:"" }} - {{ individual.death_date|default:"" }}
        </p>
    {% endif %}
</div>
```

### Back Button Component
```html
<!-- core/components/back_button.html -->
<a href="{{ back_url|default:'javascript:history.back()' }}" class="back-button">
    ← Back
</a>
```

## Middleware Implementation

### SessionCleanupMiddleware
```python
class SessionCleanupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_response(self, request, response):
        if hasattr(request, "user") and not request.user.is_authenticated:
            if "current_gedcom_file_id" in request.session:
                self.cleanup_anonymous_files(request)
        return response
```

## CSS Architecture

### Global Style Structure
```css
/* Responsive design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
}

/* Component styles */
.individual-header {
    border-bottom: 2px solid #333;
    margin-bottom: 20px;
}

.back-button {
    display: inline-block;
    padding: 8px 16px;
    background: #007bff;
    color: white;
    text-decoration: none;
}
```

This documentation represents the current state of the Core app as of the analysis date. The app provides essential foundational functionality that enables consistency and maintainability across the entire NameChart application.