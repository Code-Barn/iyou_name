# Namechart Developer Quick Reference Guide

## 🚀 Getting Started

### Setup
```bash
# Install dependencies
uv pip install -r requirements.txt

# Run migrations
uv run python manage.py migrate

# Start development server
uv run python manage.py runserver

# Run all tests
uv run python test_basic_flow.py && uv run python test_edge_cases.py && uv run python test_logged_out_flow.py
```

## 📁 Project Structure

```
namechart/
├── apps/
│   ├── core/              # Core templates, base.html
│   ├── upload/            # File upload views and templates
│   ├── users/             # Authentication and profile management
│   ├── selector/          # NEW: Unified individual selection
│   ├── browse/            # Individual browsing functionality
│   ├── hud/               # Interactive chart customization
│   ├── charts/            # Chart generation
│   ├── generator/         # Core models (GedcomFile)
│   └── parser/            # GEDCOM parsing logic
├── config/                # Django settings and URLs
├── static/                # Static files
└── templates/             # Global templates
```

## 🔧 Common Tasks

### 1. Adding a New Feature

```python
# 1. Add view to views.py
def my_new_view(request):
    return render(request, "my_template.html", {})

# 2. Add URL to app/urls.py
path("my-url/", my_new_view, name="my_view")

# 3. Include in config/urls.py
path("prefix/", include("apps.myapp.urls")),

# 4. Create template in app/templates/app/my_template.html
{% extends "core/base.html" %}
{% block content %}...{% endblock %}

# 5. Add tests to test files
```

### 2. Working with GEDCOM Files

```python
from apps.generator.models import GedcomFile
from apps.parser.models import PersonData

# Get file for authenticated user
file = GedcomFile.objects.get(id=file_id, user=request.user)

# Get file for anonymous user (check session)
file_id = request.session.get("current_gedcom_file_id")
file = GedcomFile.objects.get(id=file_id)

# Access parsed data
individuals = file.parsed_data.get("individuals", {})
person = PersonData(**individuals["I1"])

# Update home person
file.home_person_id = "I1"
file.save()
```

### 3. Session Management

```python
# Set current file
request.session["current_gedcom_file_id"] = file.id

# Get current file
file_id = request.session.get("current_gedcom_file_id")

# Set selected individual
request.session["selected_individual_id"] = individual_id

# Get/Set HUD settings
settings = request.session.get("hud_settings", {
    "template": "4",
    "show_photos": True,
    # ...
})
request.session["hud_settings"] = settings
```

### 4. Access Control

```python
# Check file ownership
if file.user and file.user != request.user:
    return HttpResponse("Unauthorized", status=403)

# Check authentication
if not request.user.is_authenticated:
    return redirect("users:login")

# Anonymous user check
is_anonymous = not request.user.is_authenticated
```

## 🌐 URL Patterns Quick Reference

### Main URLs
```python
# Upload
reverse("upload:home")                # /
reverse("upload:upload_file")         # /upload-file/

# Users
reverse("users:profile")              # /users/profile/
reverse("users:login")               # /users/auth/login/
reverse("users:register")            # /users/auth/register/

# Selector (NEW)
reverse("selector:select_individual", args=[file_id])  # /selector/select/<file_id>/
reverse("selector:confirm_selection", args=[file_id])  # /selector/confirm/<file_id>/

# Browse
reverse("browse:browse_individuals")  # /browse/browse/
reverse("browse:individual_detail", args=["I1"])  # /browse/person/I1/

# HUD
reverse("hud:display_tree")           # /hud/display-tree/
reverse("hud:save_settings")          # /hud/save-settings/
reverse("hud:hud_family_data")        # /hud/api/family-data/
reverse("hud:hud_preview")            # /hud/api/preview/
reverse("hud:hud_settings")          # /hud/api/settings/

# Charts
reverse("charts:generate_chart")      # /charts/generate/
```

## 📦 Key Models

### GedcomFile
```python
# Fields
user = models.ForeignKey(User, null=True, blank=True)  # NULL for anonymous
file = models.FileField(upload_to="gedcom_files/")
parsed_data = JSONField()  # {individuals: {}, families: {}, root_individuals: []}
home_person_id = models.CharField(max_length=100, null=True, blank=True)
is_processed = models.BooleanField(default=False)
processing_date = models.DateTimeField(null=True, blank=True)
```

### PersonData (dataclass)
```python
id: str
full_name: str
given_name: str
surname: str
birth_date: Optional[str]
birth_place: Optional[str]
death_date: Optional[str]
death_place: Optional[str]
# ... additional fields
```

## 🧪 Testing Patterns

### Test Structure
```python
from django.test import TestCase
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore

class MyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.session = SessionStore()
        self.session.save()

    def test_my_feature(self):
        request = self.factory.get("/my-url/")
        request.user = self.user  # or AnonymousUser()
        request.session = self.session
        request.session.save()

        response = my_view(request)
        self.assertEqual(response.status_code, 200)
```

### Creating Test Data
```python
# Create unique user
import uuid
username = f"test_{uuid.uuid4().hex[:8]}"
user = User.objects.create_user(username=username, password="test123")

# Create GEDCOM file
file = GedcomFile.objects.create(
    user=user,
    file=f"test_{username}.ged",
    parsed_data={
        "individuals": {
            "I1": {"id": "I1", "full_name": "Test Person", ...}
        },
        "families": {},
        "root_individuals": ["I1"]
    },
    is_processed=True
)
```

## 🎨 Template Structure

### Base Template
```html
{% extends "core/base.html" %}
{% load static %}

{% block content %}
<!-- Your content here -->
{% endblock %}

{% block extra_css %}
<!-- Additional CSS -->
{% endblock %}

{% block extra_js %}
<!-- Additional JavaScript -->
{% endblock %}
```

### Common Template Variables
```python
# Selector template
{
    "individuals": [PersonData objects],
    "gedcom_file": GedcomFile object,
    "is_logged_in": bool
}

# HUD template
{
    "gedcom_file_id": int,
    "individual": PersonData object,
    "hud_settings": dict,
    "TEMPLATE_MAPPING": dict
}

# Profile template
{
    "user": User object,
    "gedcom_files": [GedcomFile objects],
    "current_file": GedcomFile object
}
```

## 🔧 Common Utilities

### Template Mapping
```python
def get_template_mapping():
    return {
        "1": {
            "module": "apps.generator.utils.image_1generator",
            "function": "generate_family_tree",
            "filename": "US_LETTER_1GEN_BW.pdf",
            "name": "1 Generation (Individual Only)",
        },
        "2": {...},  # 2 Generation Chart
        "3": {...},  # 3 Generation Chart
        "4": {...},  # 4 Generation Chart (default)
        "5": {...},  # 5 Generation Chart
        "6": {...},  # 6 Generation Chart
        "7": {...},  # 7 Generation Chart
    }
```

### File Processing
```python
from apps.parser.utils import convert_to_utf8, parse_gedcom_data

# Process uploaded file
gedcom_content_bytes = request.FILES["gedcom_file"].read()
gedcom_content = convert_to_utf8(gedcom_content_bytes)
family_data = parse_gedcom_data(gedcom_content)

# Store parsed data
gedcom_file.parsed_data = {
    "individuals": {ind_id: person.to_dict() for ind_id, person in family_data["individuals"].items()},
    "families": family_data.get("families", {}),
    "root_individuals": family_data.get("root_individuals", [])
}
gedcom_file.save()
```

## 💡 Best Practices

### 1. Always Check Access
```python
# For user-specific files
if file.user and file.user != request.user:
    return HttpResponse("Unauthorized", status=403)

# For authenticated-only views
if not request.user.is_authenticated:
    return redirect("users:login")
```

### 2. Handle Both Authenticated and Anonymous Users
```python
if request.user.is_authenticated:
    # Redirect to profile
    return redirect("users:profile")
else:
    # Check session for anonymous user files
    if request.session.get("current_gedcom_file_id"):
        return redirect("browse:browse_individuals")
    else:
        return redirect("upload:home")
```

### 3. Use Session for Anonymous User State
```python
# Store file ID in session for anonymous users
request.session["current_gedcom_file_id"] = gedcom_file.id

# Get file from session
file_id = request.session.get("current_gedcom_file_id")
```

### 4. Provide Clear Error Messages
```python
try:
    # Operation that might fail
    gedcom_file = GedcomFile.objects.get(id=file_id)
except GedcomFile.DoesNotExist:
    return render(request, "error.html", {
        "error": "GEDCOM file not found",
        "suggested_action": "Upload a new file"
    })
```

## 🚀 Deployment Checklist

### Before Deployment
- [ ] Run all tests: `uv run python test_*.py`
- [ ] Check for migrations: `uv run python manage.py makemigrations`
- [ ] Apply migrations: `uv run python manage.py migrate`
- [ ] Collect static files: `uv run python manage.py collectstatic`
- [ ] Set `DEBUG=False` in settings
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up proper database backups

### Environment Variables
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,localhost
DATABASE_URL=postgres://user:password@host:port/dbname
```

### Monitoring
- Set up error monitoring (Sentry, etc.)
- Configure logging
- Monitor database performance
- Set up backup verification

## 📚 Troubleshooting

### Common Issues

**Database Constraints**
- Use unique usernames in tests
- Clean up test data properly
- Check foreign key constraints

**Session Issues**
- Ensure session middleware is enabled
- Check session storage configuration
- Verify session data is being saved

**Template Errors**
- Check template inheritance
- Verify template paths
- Ensure all template variables are defined

**URL Reversals**
- Use `reverse("app_name:url_name")` format
- Check URL names in urls.py
- Verify app_name is defined in urls.py

## 🎯 Quick Reference Commands

```bash
# Run specific test
uv run python test_basic_flow.py BasicFlowTest.test_selector_view

# Create superuser
uv run python manage.py createsuperuser

# Shell access
uv run python manage.py shell

# Check URL patterns
uv run python manage.py show_urls  # If available

# Database shell
uv run python manage.py dbshell

# Run management command
uv run python manage.py my_command
```

## 🤝 Contributing

### Code Style
- Follow Django best practices
- Use descriptive variable names
- Add docstrings to functions
- Keep functions focused and small
- Write comprehensive tests

### Pull Request Process
1. Create feature branch
2. Write tests first
3. Implement functionality
4. Update documentation
5. Run all tests
6. Submit pull request

### Commit Messages
- Use imperative mood ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Add detailed description if needed
- Reference related issues
