# Namechart Developer Guide

## 🚀 Quick Start

This guide will get you up and running with the Namechart project quickly, understanding the architecture and development workflow.

## 📁 Project Structure Overview

```
namechart/
├── apps/
│   ├── core/              # 🏛 Foundation layer (templates, middleware, shared services)
│   ├── upload/            # 📤 File upload and GEDCOM processing
│   ├── users/             # 👤 User authentication and management  
│   ├── selector/          # 🎯 Individual selection interface
│   ├── browse/            # 🔍 Individual browsing and family details
│   ├── hud/               # 🎨 Interactive chart customization (LIVE PREVIEW)
│   ├── charts/            # 📊 Chart generation and download
│   ├── parser/            # 📚 GEDCOM parsing and data structure
│   └── generator/         # ⚙️ Core chart generation engine
├── config/                # Django settings and configuration
├── templates/             # Global templates
├── static/                 # Global static assets
└── manage.py             # Django management command
```

## 🎯 Key App Responsibilities

| App | Purpose | Key Files | Primary Users |
|------|---------|------------|--------------|
| **Core** | Foundation layer | `core/base.html`, middleware, shared services | All apps |
| **Upload** | File upload & processing | `upload/views.py`, file handling | New users |
| **Users** | Authentication & profiles | `users/views.py`, user management | User accounts |
| **Selector** | Individual selection | `selector/views.py`, choice interface | After upload |
| **Browse** | Data browsing | `browse/views.py`, family details | Data exploration |
| **HUD** | Live preview & customization | `hud/views.py`, real-time UI | Chart creation |
| **Charts** | Chart generation | `charts/views.py`, PDF download | Final output |
| **Parser** | GEDCOM processing | `parser/models.py`, data structure | All apps |
| **Generator** | Chart engine | `generator/utils/*`, core logic | Charts/HUD |

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- Django 4.2+
- PostgreSQL (recommended) or SQLite for development
- Node.js (for frontend development)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd namechart

# Install dependencies (using uv for faster installs)
pip install uv
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your database settings

# Run migrations
uv run python manage.py migrate

# Create superuser (if needed)
uv run python manage.py createsuperuser

# Start development server
uv run python manage.py runserver
```

## 🎨 Current Architecture Patterns

### Component System
**Use Core Templates**: All templates should extend `core/base.html`
```html
{% extends 'core/base.html' %}

{% block content %}
    <!-- Your app content -->
{% endblock %}
```

**Shared Components**: Use core components where possible
```html
{% include 'core/components/individual_header.html' with individual=person %}
{% include 'core/components/back_button.html' with back_url=previous_page %}
```

### Data Flow Pattern
1. **Upload** → Users upload GEDCOM files
2. **Parser** → Files processed into structured data
3. **Selector** → Users select individuals
4. **HUD** → Live preview and customization
5. **Charts** → Final chart generation
6. **Browse** → Data exploration and navigation

### Session Management
```python
# Standard session keys
request.session['current_gedcom_file_id'] = file_id
request.session['selected_individual_id'] = individual_id
request.session['selected_template'] = template_id
```

## 🔥 Current Development Priorities

Based on our recent analysis, focus areas:

### 🚨 **COMPLETED** (Security Issues - Phase 1)
1. ✅ **Fix Upload Security** - CSRF protection, validation, rate limiting
2. ✅ **Clean HUD Code** - Removed duplicate implementations, massive functions
3. ✅ **Remove Debug Code** - Replaced print() statements with proper logging
4. ✅ **Add Input Validation** - Comprehensive validation across all apps

### ✅ **Phase 2: HUD Optimization - COMPLETED**
1. ✅ **Fix HUD JavaScript errors** - Fixed duplicate code blocks
2. ✅ **Enable static file serving** - DEBUG=True for development
3. ✅ **Test HUD functionality** - saveAndApplySettings working
4. ✅ **Remove browser detection** - Already modern, no cleanup needed
5. ✅ **Fix HTML encoding** - Added charset declarations
6. ✅ **Local Bootstrap** - No internet required, all dependencies local
7. ✅ **Chart.js consolidation** - Not needed (server-side PDF generation)

### 📈 **REMAINING** (Performance & UX)
1. **Add File Content Scanning** - Detect malicious uploads
2. **Review User Permissions** - File access controls
3. **Implement Child Counting** - Compound relationships
4. **Security Audit** - Comprehensive penetration testing
5. **Error Handling** - Improvements and user feedback

## 🛠 Development Workflow

### 1. Code Quality Standards

**Python Style**: Follow PEP 8, use Black for formatting
```python
# Install dev dependencies
pip install black flake8 mypy

# Format code
black .

# Lint code
flake8 apps/
```

**Django Best Practices**:
- Use Django's built-in features (forms, auth, ORM)
- Implement proper error handling and logging
- Use Django's template system safely
- Follow Django URL patterns and naming conventions

### 2. Testing Strategy
```bash
# Run all tests
uv run python -m pytest

# Test specific app
uv run python -m pytest apps/parser/test_*.py

# Run with coverage
uv run python -m pytest --cov=apps --cov-report=html
```

### 3. Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature-name
# Open pull request for review
```

## 📚 Key Dependencies & Usage

### Django Apps Used
- **django.contrib.auth** - User authentication
- **django.contrib.sessions** - Session management
- **django.contrib.staticfiles** - Static file serving
- **django.contrib.messages** - User feedback messaging

### External Libraries
- **ged4py** - GEDCOM file parsing
- **chardet** - Character encoding detection
- **reportlab** - PDF generation (in generator)
- **pillow** - Image processing

### Database Models
```python
# Core User Model (Django built-in)
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Add custom fields as needed
    pass

# File Model (in generator/models.py)
class GedcomFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    parsed_data = models.JSONField(default=dict)
    home_person_id = models.CharField(max_length=50, blank=True, null=True)
```

## 🔍 Common Development Tasks

### Adding a New View
```python
# In apps/yourapp/views.py
from django.shortcuts import render

def new_view(request):
    if request.method == 'POST':
        # Handle form submission
        pass
    
    return render(request, 'yourapp/template.html', {
        'form': form
    })

# In apps/yourapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('new-view/', views.new_view, name='new_view'),
]
```

### Adding New Templates
```html
{% extends 'core/base.html' %}

{% block content %}
<div class="container">
    <h1>New Page</h1>
    
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
    
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
</div>
{% endblock %}
```

## 🎨 Frontend Development

### CSS Organization
```css
/* In apps/core/static/core/css/style.css */
.btn-primary {
    background-color: #007bff;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

/* Mobile-first responsive design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
}
```

### JavaScript Integration
```javascript
// In static files, include before closing body tag
document.addEventListener('DOMContentLoaded', function() {
    // Initialize interactive components
    initializeFileUpload();
    initializeSearch();
    initializeProgressIndicators();
});

function initializeFileUpload() {
    // File upload logic
}

function initializeSearch() {
    // Search functionality
}
```

## 🧪 Debugging & Troubleshooting

### Common Issues & Solutions
```python
# 1. Database Connection Errors
# Solution: Check DATABASE_URL in .env
# Run: uv run python manage.py check

# 2. Template Not Found Errors
# Solution: Check template paths and Django settings
# Run: uv run python manage.py findstatic --verbosity=2

# 3. Static Files Not Loading
# Solution: Run collectstatic in production
# Run: uv run python manage.py collectstatic --noinput

# 4. Import Errors
# Solution: Check INSTALLED_APPS and Python path
# Run: uv run python manage.py check --deploy
```

### Debugging Tools
```python
# Django Debug Toolbar (development only)
pip install django-debug-toolbar

# Add to INSTALLED_APPS for development
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
```

## 📊 Performance Optimization

### Database Optimization
```python
# Use select_related to reduce queries
files = GedcomFile.objects.select_related('user').all()

# Use prefetch_related for many-to-many
users = User.objects.prefetch_related('gedcomfile_set').all()

# Add database indexes
class GedcomFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'uploaded_at']),
            models.Index(fields=['is_processed']),
        ]
```

### Caching Strategy
```python
# View caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def expensive_view(request):
    # View logic
    pass

# Template fragment caching
from django.core.cache import cache

def get_expensive_data():
    data = cache.get('expensive_data_key')
    if data is None:
        data = compute_expensive_data()
        cache.set('expensive_data_key', data, 60 * 60)
    return data
```

## 🔐 Security Best Practices

### Input Validation
```python
from django.core.exceptions import ValidationError
import re

def validate_gedcom_file(file):
    # File size validation
    if file.size > 100 * 1024 * 1024:  # 100MB limit
        raise ValidationError("File too large")
    
    # File type validation
    allowed_extensions = ['.ged', '.gedcom']
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in allowed_extensions:
        raise ValidationError("Invalid file type")
    
    # Content validation
    if not is_valid_gedcom_content(file):
        raise ValidationError("Invalid GEDCOM file")
```

### Authentication Security
```python
# Custom middleware for security
class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
```

## 📋 API Development

### RESTful Patterns
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@require_http_methods(["GET", "POST"])
def api_endpoint(request):
    if request.method == 'GET':
        return JsonResponse({'data': get_data()})
    
    elif request.method == 'POST':
        if request.is_ajax():
            data = json.loads(request.body)
            result = process_data(data)
            return JsonResponse({'status': 'success', 'data': result})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

### Error Handling
```python
# Structured error responses
class APIError(Exception):
    def __init__(self, message, error_code='UNKNOWN', status=400):
        self.message = message
        self.error_code = error_code
        self.status = status

def handle_api_error(request, error):
    return JsonResponse({
        'error': error.message,
        'error_code': error.error_code,
        'timestamp': timezone.now().isoformat()
    }, status=error.status)
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Remove all debug code and print statements
- [ ] Set DEBUG=False in production settings
- [ ] Configure proper database settings
- [ ] Run all tests and ensure they pass
- [ ] Collect static files: `manage.py collectstatic`
- [ ] Verify all environment variables
- [ ] Check security settings (ALLOWED_HOSTS, etc.)

### Production Settings
```python
# SECURITY SETTINGS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_X_FRAME_OPTIONS = 'DENY'

# DATABASE SETTINGS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# CACHE SETTINGS (Redis recommended for production)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 📞 Getting Help

### Common Issues & Solutions
1. **"No module named X"** → Check INSTALLED_APPS, run `pip install X`
2. **"Template does not exist"** → Check template paths, run `findstatic`
3. **"Can't connect to database"** → Check DATABASE_URL, run `check --deploy`
4. **"Static files not loading"** → Check STATIC_URL, run `collectstatic`
5. **"Permission denied"** → Check file permissions, database user rights

### Useful Commands
```bash
# Check project health
uv run python manage.py check --deploy

# Create migrations after model changes
uv run python manage.py makemigrations appname

# Reset migrations if needed
uv run python manage.py migrate appname zero

# Shell access for debugging
uv run python manage.py shell

# Create superuser if needed
uv run python manage.py createsuperuser
```

## 🎯 Success Metrics

### Code Quality Goals
- 90%+ test coverage
- Zero security vulnerabilities
- <5 second average page load time
- <500ms average API response time
- Zero production debug statements

### Development Efficiency
- Consistent code style
- Comprehensive documentation
- Automated testing pipeline
- Fast development feedback loop

This guide provides a solid foundation for Namechart development. Start with the security fixes (highest priority), then move to performance and feature enhancements. Good luck! 🚀