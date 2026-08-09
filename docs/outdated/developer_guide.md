# Family Tree Generator - Developer Quick Reference Guide

## 🎯 File Handling Best Practices

### Core Principles

1. **Single Parsing**: Parse files once and store results
2. **Centralized Access**: Use `get_family_data()` for all data access
3. **Data Persistence**: Store parsed data in database, not sessions
4. **Proper Cleanup**: Remove associated data when files are deleted
5. **Session Management**: Store file IDs, not full data objects

## 🚀 Getting Started

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/your-repo/family-tree-generator.git
cd family-tree-generator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Essential Commands

```bash
# Run development server
python manage.py runserver

# Run tests
python manage.py test generator

# Create migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run specific management commands
python manage.py shell
python manage.py dbshell
```

## 📦 Project Structure

```
generator/
├── models.py                # Data models
├── views.py                 # Business logic and views
├── forms.py                 # Django forms
├── urls.py                  # URL routing
├── utils/                   # Utility modules
│   ├── gedcom_parser.py     # GEDCOM parsing
│   └── image_*generator.py  # Chart generators
├── templates/               # HTML templates
├── static/                  # Static assets
└── tests/                   # Test files
```

## 🔧 Development Workflow

### Feature Development

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Write tests first**: Add tests for new functionality
3. **Implement feature**: Write code to pass tests
4. **Run tests**: `python manage.py test generator`
5. **Commit changes**: `git commit -m "Add feature: description"`
6. **Push branch**: `git push origin feature/your-feature`
7. **Create PR**: Submit pull request for review

### Bug Fixing

1. **Create issue**: Document the bug
2. **Create branch**: `git checkout -b bugfix/issue-number`
3. **Add regression test**: Test that reproduces the bug
4. **Fix bug**: Implement the fix
5. **Verify fix**: Run tests and manual verification
6. **Commit and push**: Follow standard commit process

## 🧪 Testing Quick Reference

### Test Commands

```bash
# Run all tests
python manage.py test generator

# Run specific test class
python manage.py test generator.tests.GedcomParserTests

# Run specific test method
python manage.py test generator.tests.GedcomParserTests.test_parse_individuals

# Run tests with verbose output
python manage.py test generator -v 2

# Run tests matching pattern
python manage.py test generator -k "gedcom7"
```

### Common Test Patterns

```python
# Basic test structure
def test_feature_name(self):
    """Test description explaining what is being validated"""
    # Setup test data
    test_data = self._create_test_data()

    # Execute functionality
    result = function_under_test(test_data)

    # Assert expected outcomes
    self.assertEqual(result, expected_value)
    self.assertIsNotNone(result)
    self.assertGreater(len(result), 0)
```

## 📝 Coding Standards

### Python Style Guide

- **PEP 8 Compliance**: Follow Python style guide
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Comprehensive docstrings for all public functions
- **Line Length**: Maximum 88 characters per line
- **Imports**: Grouped by standard library, third-party, local

```python
# Good example
from typing import Dict, List, Optional
import os

from django.db import models

from .utils import helper_function

class ExampleClass:
    """Class docstring explaining purpose and usage."""

    def example_method(self, param1: str, param2: int) -> Optional[Dict]:
        """Method docstring with parameter and return type documentation."""
        # Method implementation
        return {"result": "success"}
```

### Django Best Practices

- **Fat models, thin views**: Business logic in models
- **Class-based views**: Prefer CBVs over function-based views
- **Template organization**: Logical template structure
- **URL naming**: Clear, descriptive URL names
- **Form handling**: Use Django forms for validation

## 🔍 Debugging Tips

### Common Debugging Techniques

```python
# Debug printing
print(f"Debug: variable_value = {variable}")

# Django debug toolbar
# Install: pip install django-debug-toolbar
# Add to INSTALLED_APPS and MIDDLEWARE

# Logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message: %s", variable)

# Django shell
python manage.py shell
>>> from generator.models import PersonData
>>> data = PersonData(id="I1", full_name="John Doe")
>>> print(data.to_dict())
```

### Debugging GEDCOM Parsing

```python
# Enable debug output in parser
from generator.utils.gedcom_parser import parse_gedcom_data

# Parse with debug output
result = parse_gedcom_data(gedcom_content)

# Examine parsed data
print(f"Individuals: {len(result['individuals'])}")
print(f"Families: {len(result['families'])}")
print(f"Root individuals: {result['root_individuals']}")

# Inspect specific individual
individual = result['individuals']['I1']
print(f"Individual: {individual.full_name}")
print(f"Spouse: {individual.spouse}")
print(f"Children: {individual.children}")
```

## 📊 Performance Optimization

### Common Performance Issues

1. **N+1 Query Problem**: Use `select_related` and `prefetch_related`
2. **Large GEDCOM Files**: Implement batch processing
3. **Memory Usage**: Stream large files instead of loading entirely
4. **Image Generation**: Optimize ImageMagick settings
5. **Database Queries**: Add proper indexing

### Optimization Techniques

```python
# Database query optimization
from django.db.models import Prefetch

# Optimized query example
files = GedcomFile.objects.select_related('user').prefetch_related(
    Prefetch('related_model_set', queryset=RelatedModel.objects.all())
).filter(user=request.user)

# Memory-efficient file processing
def process_large_file(file_path):
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):  # Process in 4KB chunks
            process_chunk(chunk)
```

## 🌐 API Development

### REST API Guidelines

- **Versioning**: Include API version in URLs (`/api/v1/`)
- **Authentication**: Use Django REST Framework authentication
- **Serialization**: Proper serialization of complex data
- **Pagination**: Implement pagination for large datasets
- **Documentation**: Use OpenAPI/Swagger documentation

```python
# Example API view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_individual_detail(request, individual_id):
    """API endpoint for individual details."""
    try:
        # Get individual data
        individual = get_individual_data(individual_id)

        # Serialize data
        serializer = IndividualSerializer(individual)

        return Response(serializer.data)
    except Individual.NotFound:
        return Response({"error": "Individual not found"}, status=404)
```

## 📁 File Handling

### GEDCOM File Processing

```python
# Safe file handling
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

def handle_uploaded_file(file):
    """Handle uploaded GEDCOM file safely."""
    # Validate file type
    if not file.name.endswith('.ged'):
        raise ValidationError("Only GEDCOM files (.ged) are allowed")

    # Validate file size
    if file.size > 10 * 1024 * 1024:  # 10MB limit
        raise ValidationError("File size exceeds 10MB limit")

    # Process file content
    if isinstance(file, InMemoryUploadedFile):
        content = file.read().decode('utf-8')
    else:
        with file.open('r', encoding='utf-8') as f:
            content = f.read()

    return parse_gedcom_data(content)
```

### File Storage Best Practices

- **User-specific directories**: Store files in user-specific paths
- **Secure filenames**: Sanitize filenames to prevent directory traversal
- **File cleanup**: Implement automatic cleanup of old files
- **Backup strategy**: Regular backups of user data

## 🔒 Security Best Practices

### Common Security Measures

```python
# Input validation
from django.core.exceptions import ValidationError

def validate_input(data):
    """Validate user input."""
    if not isinstance(data, str):
        raise ValidationError("Input must be a string")

    if len(data) > 1000:
        raise ValidationError("Input too long")

    # Additional validation logic
    return sanitized_data

# CSRF protection
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def secure_view(request):
    """View with CSRF protection."""
    # View implementation
```

### Security Checklist

1. **Authentication**: Secure login and session management
2. **Authorization**: Proper access control and permissions
3. **Input Validation**: Validate all user inputs
4. **Output Encoding**: Prevent XSS attacks
5. **File Uploads**: Validate file types and sizes
6. **Error Handling**: Don't expose sensitive information
7. **Logging**: Secure logging practices
8. **Dependencies**: Regularly update dependencies

## 📚 Documentation Standards

### Code Documentation

```python
# Function documentation example
def calculate_relationships(individual_id: str, family_data: Dict) -> List[Dict]:
    """
    Calculate family relationships for an individual.

    Args:
        individual_id: The ID of the individual to analyze
        family_data: Dictionary containing all family data

    Returns:
        List of relationship dictionaries containing:
        - relationship_type: Type of relationship
        - individual_id: Related individual ID
        - individual_name: Related individual name

    Raises:
        IndividualNotFound: If individual ID is not found
        InvalidFamilyData: If family data structure is invalid

    Example:
        >>> relationships = calculate_relationships("I1", family_data)
        >>> for rel in relationships:
        ...     print(f"{rel['relationship_type']}: {rel['individual_name']}")
    """
    # Function implementation
```

### Commenting Guidelines

- **Class-level comments**: Explain class purpose and usage
- **Method-level comments**: Document parameters, returns, and exceptions
- **Complex logic**: Explain non-obvious algorithms
- **TODO comments**: Mark incomplete features or improvements
- **FIXME comments**: Mark known issues that need fixing

## 🤝 Collaboration

### Code Review Guidelines

1. **Focus on quality**: Ensure code meets standards
2. **Be constructive**: Provide helpful feedback
3. **Check functionality**: Verify the code works as intended
4. **Review tests**: Ensure proper test coverage
5. **Check documentation**: Verify documentation is complete
6. **Consider performance**: Look for optimization opportunities
7. **Security review**: Check for potential vulnerabilities

### Pull Request Template

```markdown
## Description

[Brief description of the changes]

## Related Issue

[Link to related issue or requirement]

## Changes Made

- Change 1: [Description]
- Change 2: [Description]
- Change 3: [Description]

## Testing

- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing performed
- [ ] Edge cases tested

## Documentation

- [ ] Code documentation updated
- [ ] User documentation updated (if applicable)
- [ ] API documentation updated (if applicable)

## Checklist

- [ ] Code follows project standards
- [ ] Tests pass successfully
- [ ] No breaking changes
- [ ] Backward compatibility maintained
- [ ] Security considerations addressed
```

## 🚀 Deployment Checklist

### Pre-deployment Checklist

1. **Test coverage**: All tests passing
2. **Code review**: All changes reviewed and approved
3. **Documentation**: All documentation updated
4. **Dependencies**: All dependencies up to date
5. **Configuration**: Production configuration verified
6. **Backup**: Database and files backed up
7. **Migration plan**: Deployment migration plan ready
8. **Rollback plan**: Rollback procedure documented

### Deployment Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements-prod.txt

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 6. Verify deployment
curl https://yourdomain.com/health-check
```

## 📊 Monitoring and Maintenance

### Monitoring Setup

1. **Error tracking**: Set up Sentry or similar
2. **Performance monitoring**: New Relic or Datadog
3. **Log aggregation**: ELK stack or similar
4. **Uptime monitoring**: Pingdom or UptimeRobot
5. **Database monitoring**: PGAdmin or MySQL Workbench

### Maintenance Tasks

```bash
# Regular maintenance commands

# Clear cache
python manage.py clear_cache

# Clean up old files
python manage.py cleanup_files --days=30

# Optimize database
python manage.py dbshell
> VACUUM ANALYZE;

# Check for security updates
pip list --outdated
pip install --upgrade package-name
```

## 🎯 Troubleshooting Guide

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| GEDCOM parsing fails | Invalid GEDCOM format | Validate file format and structure |
| Slow performance | Large GEDCOM files | Implement batch processing |
| Memory errors | Excessive data loading | Use streaming or pagination |
| Image generation fails | Missing ImageMagick | Install ImageMagick dependencies |
| Test failures | Database state issues | Use test fixtures or factories |
| Deployment errors | Missing dependencies | Check requirements.txt |
| File upload issues | Permission problems | Verify file permissions |
| Authentication failures | Session issues | Check session configuration |

### Debugging Workflow

1. **Reproduce the issue**: Get consistent reproduction steps
2. **Check logs**: Examine application and server logs
3. **Isolate the problem**: Narrow down the affected component
4. **Add debug output**: Insert strategic debug statements
5. **Test hypotheses**: Verify potential causes
6. **Implement fix**: Apply the solution
7. **Verify fix**: Test the resolution
8. **Add regression test**: Prevent future occurrences

## 📚 Learning Resources

### Recommended Reading

- **Django Documentation**: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Python Documentation**: [https://docs.python.org/3/](https://docs.python.org/3/)
- **GEDCOM Specification**: [https://gedcom.io/](https://gedcom.io/)
- **ImageMagick Documentation**: [https://imagemagick.org/](https://imagemagick.org/)

### Online Courses

- **Django for Beginners**: [https://djangoforbeginners.com/](https://djangoforbeginners.com/)
- **Test-Driven Development with Python**: [https://www.obeythetestinggoat.com/](https://www.obeythetestinggoat.com/)
- **Advanced Django**: [https://www.django-advanced.com/](https://www.django-advanced.com/)

### Community Resources

- **Django Forum**: [https://forum.djangoproject.com/](https://forum.djangoproject.com/)
- **Stack Overflow**: [https://stackoverflow.com/questions/tagged/django](https://stackoverflow.com/questions/tagged/django)
- **Django Discord**: [https://discord.gg/django](https://discord.gg/django)
- **Python Discord**: [https://discord.gg/python](https://discord.gg/python)

## 📝 Quick Reference Commands

### Django Management Commands

```bash
# Database operations
python manage.py migrate
python manage.py makemigrations
python manage.py sqlmigrate app_name migration_number
python manage.py showmigrations

# User management
python manage.py createsuperuser
python manage.py changepassword username

# Development tools
python manage.py shell
python manage.py dbshell
python manage.py runserver 0.0.0.0:8000
python manage.py check --deploy

# Static files
python manage.py collectstatic
python manage.py findstatic file_path
```

### Git Commands

```bash
# Basic workflow
git status
git add file_path
git commit -m "Commit message"
git push origin branch_name
git pull origin branch_name

# Branch management
git branch
git branch new_branch_name
git checkout branch_name
git merge branch_name
git branch -d branch_name

# History and changes
git log
git diff
git show commit_hash
git reset file_path
git revert commit_hash
```

---

**© 2023 Family Tree Generator. All rights reserved.**