# AGENTS.md - Guidelines for AI Coding Agents

This document provides guidelines for AI agents operating in the namechart codebase.

---

## 1. Project Overview

- **Framework**: Django 6.0+
- **Language**: Python 3.13+
- **Database**: PostgreSQL (via dj-database-url)
- **Frontend**: Vanilla JavaScript, Bootstrap 5
- **Image Processing**: Wand (ImageMagick)
- **Testing**: Django test framework, Playwright for e2e
- **Package Manager**: uv

---

## 2. Execution Rules

- **Always use `uv run`** for executing Python scripts or Django management commands.
- **Use `uv add`** or **`uv remove`** for dependency changes.
- **Never use bare `python`** or **`pip`** commands.

---

## 3. Build & Run Commands

### Django Server
```bash
cd /home/user/CODE_BASE/namechart
uv run python manage.py runserver
```

### Database Migrations
```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Running Tests

**Run all tests:**
```bash
uv run python manage.py test
```

**Run specific test file:**
```bash
uv run python manage.py test tests.test_buffer_system
```

**Run specific test class:**
```bash
uv run python manage.py test apps.generator.tests.test_multi_generation.MultiGenerationTests
```

**Run single test method:**
```bash
uv run python manage.py test apps.generator.tests.test_multi_generation.MultiGenerationTests.test_prototype_2gen
```

**Run tests in debug mode (with output):**
```bash
uv run python manage.py test --verbosity=2
```

### Linting

**Ruff (Python):**
```bash
ruff check apps/
ruff check --fix apps/
```

**JavaScript (no formal linter configured - follow style below)**

---

## 3. Code Style Guidelines

### Python - General

- **Indentation**: 4 spaces
- **Line length**: 100 characters max
- **Docstrings**: Google style for functions
- **Type hints**: Use where reasonable, but don't over-engineer

### Python - Imports

Order (separated by blank lines):
1. Standard library
2. Third-party Django
3. Third-party other
4. Local apps

```python
# Standard library
import hashlib
import json
import logging
from datetime import timedelta

# Django
from django.conf import settings
from django.db import models
from django.views.decorators import require_http_methods

# Third-party
from wand.color import Color
from wand.drawing import Drawing

# Local apps
from apps.parser.models import PersonData
from apps.generator.utils.prototype.individual_printer import print_individual
```

### Python - Naming

- **Classes**: `PascalCase` (e.g., `Generation5Constants`)
- **Functions/methods**: `snake_case` (e.g., `get_validated_settings`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `IMAGE_CENTER_X`)
- **Private methods**: `_leading_underscore`

### Python - Error Handling

- Use specific exception types
- Log errors with logger
- Return meaningful error messages
- Never expose raw exceptions to users

```python
try:
    result = do_something()
except SpecificError as e:
    logger.warning(f"Handled gracefully: {e}")
    return fallback_value
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return JsonResponse({"error": "Something went wrong"}, status=500)
```

### Django Views

- Use `@login_required` for authenticated routes
- Use `@csrf_protect` for POST forms
- Return `JsonResponse` for API endpoints
- Use Django's built-in auth decorators

### JavaScript

- **Indentation**: 4 spaces
- **Semicolons**: Required
- **Variable declarations**: Use `const` by default, `let` when mutating
- **Names**: camelCase
- **Module pattern**: Use IIFE or ES6 modules where appropriate

```javascript
// Use const by default
const getCSRFToken = function() {
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return token ? token.value : '';
};

// Namespace pattern used in this project
window.HUD = window.HUD || {};
HUD.ModuleName = (function() {
    'use strict';
    
    function privateFunction() {
        // ...
    }
    
    return {
        publicFunction: privateFunction
    };
})();
```

### HTML/Django Templates

- Use Django template tags: `{% tag %}` with spaces inside
- Use filters: `{{ variable|filter }}`
- Load template tags at top: `{% load custom_filters %}`

---

## 4. Project Structure

```
/home/user/CODE_BASE/namechart/
├── apps/
│   ├── browse/        # Individual browsing
│   ├── chart_storage/ # Persistent settings/buffers (NEW)
│   ├── charts/        # Chart serving
│   ├── core/         # Shared utilities
│   ├── generator/    # Chart generation
│   ├── hud/          # Interactive HUD
│   ├── parser/       # GEDCOM parsing
│   ├── selector/     # Individual selection
│   ├── upload/       # File upload
│   └── users/        # User accounts
├── config/           # Django settings
├── tests/            # Test files
└── manage.py
```

---

## 5. Key Patterns

### Buffer System
The buffer caching system uses `SimpleBufferManager` for in-memory caching. Generators should use `get_chart_buffer()` for overlays instead of calling generator functions directly.

### Settings Flow
1. Settings stored in localStorage per-generation
2. Cumulative settings retrieved for consistent cache keys
3. Settings hash validates cache freshness

### Home Person Integration
- GedcomFile.home_person_id for navigation
- IndividualSettings (chart_storage) for custom settings
- Both synced when home person is set

---

## 6. Testing Guidelines

### Writing Tests
```python
from django.test import TestCase

class MyFeatureTests(TestCase):
    def setUp(self):
        # Create test data
    
    def test_something(self):
        response = self.client.get('/path/')
        self.assertEqual(response.status_code, 200)
```

### Debugging Tests
```bash
# Add print statements visible in test output
python manage.py test --verbosity=2 tests.test_buffer_system
```

---

## 7. Common Tasks

### Adding a new model
1. Create model in `models.py`
2. Run `makemigrations`
3. Add to admin if needed

### Adding a new API endpoint
1. Create view in appropriate `views.py`
2. Add URL to `urls.py`
3. Add `@login_required` and `@require_http_methods`

### Adding JavaScript to HUD
- Edit `apps/hud/static/hud/js/hud-organized.js`
- Use existing `HUD.*` namespace pattern
- Add debug logging with `console.log`

---

## 8. Important Notes

- **No type checking configured** - Be consistent with existing types
- **LSP errors in generators** - Pre-existing, not from your changes
- **Database** - Use migrations, never edit schema directly
- **Secrets** - Never commit API keys or credentials

---

## 9. GrampsWeb Integration

### Overview
namechart can integrate with GrampsWeb to fetch genealogy data via the REST API.

### Configuration
Set these environment variables:
- `GRAMPSWEB_API_URL` - Base URL of GrampsWeb (e.g., `http://grampsweb:5000`)
- `GRAMPSWEB_API_TOKEN` - JWT token from GrampsWeb API access
- `GRAMPSWEB_API_TIMEOUT` - Request timeout in seconds (default: 30)

### API Client
Use `apps.core.grampsweb` module:
```python
from apps.core.grampsweb import get_client, fetch_gedcom_from_grampsweb

# Get configured client
client = get_client()
if client:
    gedcom_bytes = fetch_gedcom_from_grampsweb()
```

### Deployment
- Docker: See `deploy/docker/docker-compose.yml`
- Kubernetes: See `deploy/kubernetes/` directory
- GrampsWeb runs on subdomain (e.g., `genealogy.example.com`)
