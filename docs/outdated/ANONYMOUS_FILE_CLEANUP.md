# Anonymous File Cleanup System

## Overview
This document describes the system for automatically deleting files uploaded by anonymous (not logged-in) users. The system ensures that anonymous files are not stored indefinitely and are cleaned up automatically after a period of inactivity.

## Components

### 1. Database Model Changes
- **`last_activity` Field**: Added to the `GedcomFile` model to track the last time the file was accessed.
  ```python
  last_activity = models.DateTimeField(auto_now=True)  # Automatically updated on save
  ```

### 2. Automatic Cleanup
- **Management Command**: `cleanup_anonymous_files`
  - Deletes anonymous files older than 1 hour.
  - Run manually or schedule using a cron job/Celery.

### 3. Session Expiry Cleanup
- **JavaScript Snippet**: Added to the base template to delete anonymous files when the user leaves the page.
  ```javascript
  document.addEventListener('beforeunload', function() {
      const fileId = '{{ current_gedcom_file_id|default:"" }}';
      if (fileId) {
          fetch('/delete-anonymous-file/', {
              method: 'POST',
              headers: {
                  'X-CSRFToken': '{{ csrf_token }}',
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ file_id: fileId }),
          });
      }
  });
  ```

### 4. Navigation Cleanup
- **Middleware**: `SessionCleanupMiddleware`
  - Deletes anonymous files when the user navigates away from the app.

### 5. Consolidated `upload_and_generate` Function
- **Location**: `apps/upload/views.py`
- **Purpose**: Handles file uploads and updates the `last_activity` field.

## Setup Instructions

### 1. Apply Migrations
```bash
cd /home/user/CODE_BASE/namechart && uv run python3 manage.py makemigrations
cd /home/user/CODE_BASE/namechart && uv run python3 manage.py migrate
```

### 2. Schedule the Cleanup Command
- **Cron Job** (Linux/macOS):
  ```bash
  0 * * * * /path/to/venv/bin/python /home/user/CODE_BASE/namechart/manage.py cleanup_anonymous_files
  ```
- **Celery Task** (for more scalability):
  ```python
  # apps/generator/tasks.py
  from celery import shared_task
  from django.utils import timezone
  from apps.generator.models import GedcomFile
  from datetime import timedelta

  @shared_task
  def cleanup_anonymous_files():
      one_hour_ago = timezone.now() - timedelta(hours=1)
      deleted_count, _ = GedcomFile.objects.filter(
          user=None,
          last_activity__lt=one_hour_ago
      ).delete()
      return deleted_count
  ```

### 3. Test the Implementation
1. **Upload a File as an Anonymous User**:
   - Navigate to the upload page.
   - Upload a file as an anonymous user.
   - Verify that the file is processed and the `last_activity` field is updated.

2. **Automatic Cleanup**:
   - Wait for 1 hour (or manually update the `last_activity` field to simulate inactivity).
   - Run the cleanup command:
     ```bash
     cd /home/user/CODE_BASE/namechart && uv run python3 manage.py cleanup_anonymous_files
     ```
   - Verify that the file is deleted.

3. **Session Expiry Cleanup**:
   - Upload a file as an anonymous user.
   - Navigate away from the page or close the browser tab.
   - Verify that the file is deleted.

4. **Navigation Cleanup**:
   - Upload a file as an anonymous user.
   - Navigate to another page or close the browser tab.
   - Verify that the file is deleted.

## Troubleshooting

### 1. Files Not Deleted
- **Check the `last_activity` Field**: Ensure the field is being updated correctly.
- **Check the Cleanup Command**: Verify that the command is running and deleting files.
- **Check the JavaScript Snippet**: Ensure the snippet is correctly sending the deletion request.
- **Check the Middleware**: Verify that the middleware is correctly deleting files.

### 2. Database Permissions
- **Grant Permissions**: Ensure the database user has the necessary permissions to delete records.
  ```sql
  ALTER USER namechart_user CREATEDB;
  GRANT ALL PRIVILEGES ON DATABASE namechart TO namechart_user;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO namechart_user;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO namechart_user;
  ```

### 3. Logging
- **Check the Logs**: Monitor the logs to ensure that the cleanup process is running correctly.
  ```bash
  tail -f debug.log
  ```

## Future Improvements

### 1. Configurable Cleanup Interval
- Allow the cleanup interval to be configured in the settings.

### 2. Notifications
- Notify users before their files are deleted.

### 3. Extended Retention
- Allow users to extend the retention period for their files.

### 4. File Recovery
- Implement a file recovery system for deleted files.
