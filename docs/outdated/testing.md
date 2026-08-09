# Testing Guide

## Current Test Status

### Working Tests
- ✅ Database setup and teardown
- ✅ URL resolution
- ✅ View routing
- ✅ Template rendering (mostly)

### Known Issues
- ❌ Some templates still reference old paths
- ❌ Some views show error templates instead of expected content
- ❌ Test data setup needs improvement

## Running Tests

### Basic Test Execution
```bash
# Run all tests
python manage.py test --settings=config.settings_test

# Run specific app tests
python manage.py test apps.upload.tests --settings=config.settings_test
python manage.py test apps.browse.tests --settings=config.settings_test
