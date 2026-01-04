# Upload App

## Purpose
Handles GEDCOM file uploads, processing, and management.

## Key Components

### Views
- `upload_file`: Display upload form
- `upload_and_generate`: Process uploaded files
- `select_gedcom_file`: Select from uploaded files
- `delete_gedcom_file`: Delete uploaded files

### Templates
- `upload_file.html`: Upload form
- `select_individual.html`: Individual selection
- `error.html`: Error display

### URLs
- `/`: Home page (upload)
- `/upload-file/`: Upload form
- `/select-file/<id>/`: Select file
- `/delete-file/<id>/`: Delete file

## Usage
```python
from apps.upload.views import upload_and_generate
from apps.upload.urls import urlpatterns as upload_urls
