# Persistent Settings & Buffer Storage Design

## Overview

This document specifies the architecture for two related systems:
1. **Persistent Settings Storage**: Save user chart settings long-term, with presets and per-individual settings
2. **Persistent Buffer Storage**: Cache generated chart images for fast loading on return visits

---

## 1. Persistent Settings Storage

### 1.1 Requirements

- Users can save named presets (e.g., "My Home Chart", "Work Settings")
- Settings can be associated with a specific gedcom file + individual combination
- Multiple individuals can have different saved settings
- One "home person" per gedcom can be designated
- Settings can be exported/imported as JSON
- Privacy: Users can only access their own settings

### 1.2 Database Models

```python
from django.db import models
from django.contrib.auth.models import User


class UserStorageQuota(models.Model):
    """
    Tracks per-user storage usage for buffers.
    Default quota: 500MB per user.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='storage_quota'
    )
    bytes_used = models.PositiveBigIntegerField(default=0)
    bytes_limit = models.PositiveBigIntegerField(
        default=500 * 1024 * 1024  # 500MB default
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Storage Quota'
        verbose_name_plural = 'User Storage Quotas'

    def can_store(self, size_bytes: int) -> bool:
        """Check if user can store additional bytes"""
        return (self.bytes_used + size_bytes) <= self.bytes_limit

    def add_usage(self, size_bytes: int) -> bool:
        """Add to used bytes if within quota. Returns success."""
        if self.can_store(size_bytes):
            self.bytes_used += size_bytes
            self.save(update_fields=['bytes_used', 'updated_at'])
            return True
        return False

    def release_usage(self, size_bytes: int):
        """Release bytes from deleted buffer"""
        self.bytes_used = max(0, self.bytes_used - size_bytes)
        self.save(update_fields=['bytes_used', 'updated_at'])

    @property
    def usage_percentage(self) -> float:
        return (self.bytes_used / max(1, self.bytes_limit)) * 100


class UserSettingsPreset(models.Model):
    """
    Named preset configurations that users can save and recall.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='settings_presets'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    settings_json = models.JSONField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class IndividualSettings(models.Model):
    """
    Settings associated with a specific individual within a gedcom file.
    
    Key: {gedcom_hash}:{individual_id}
    - gedcom_hash: SHA256 of gedcom filename (not contents)
    - individual_id: The gedcom-level ID (e.g., @I1@)
    
    This ensures:
    - Same person in different gedcom files = different settings
    - Same gedcom re-uploaded = settings preserved
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='individual_settings'
    )
    gedcom_hash = models.CharField(max_length=64)  # SHA256 of filename
    gedcom_name = models.CharField(max_length=255)  # Display name
    individual_id = models.CharField(max_length=100)  # e.g., @I1@
    individual_name = models.CharField(max_length=255)  # For display
    settings_json = models.JSONField()
    is_home_person = models.BooleanField(default=False)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Individual Settings'
        unique_together = ['user', 'gedcom_hash', 'individual_id']
        indexes = [
            models.Index(fields=['user', 'gedcom_hash']),
            models.Index(fields=['user', 'gedcom_hash', 'is_home_person']),
        ]

    def __str__(self):
        return f"{self.individual_name} ({self.gedcom_name})"


class GedcomInfo(models.Model):
    """
    Metadata about uploaded gedcom files.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='gedcom_files'
    )
    gedcom_hash = models.CharField(max_length=64, unique=True)
    filename = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    individual_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.display_name} ({self.user.username})"
```

### 1.3 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hud/api/presets/` | GET | List user's saved presets |
| `/hud/api/presets/` | POST | Create new preset |
| `/hud/api/presets/<id>/` | GET | Get specific preset |
| `/hud/api/presets/<id>/` | PUT | Update preset |
| `/hud/api/presets/<id>/` | DELETE | Delete preset |
| `/hud/api/individual-settings/` | GET | List individual settings |
| `/hud/api/individual-settings/` | POST | Save settings for individual |
| `/hud/api/individual-settings/<gedcom_hash>/<individual_id>/` | GET | Get settings for specific individual |
| `/hud/api/individual-settings/<gedcom_hash>/<individual_id>/` | DELETE | Delete settings |
| `/hud/api/home-person/<gedcom_hash>/` | POST | Set home person for gedcom |
| `/hud/api/storage/usage/` | GET | Get storage usage |
| `/hud/api/settings/export/` | GET | Export all settings as JSON |
| `/hud/api/settings/import/` | POST | Import settings from JSON |

### 1.4 JavaScript Integration

```javascript
HUD.PresetManager = {
    savePreset(name, description = '') {
        const settings = HUD.Storage.getCumulativeSettings(HUD.Main.getCurrentTemplate());
        return fetch('/hud/api/presets/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description, settings_json: settings })
        });
    },
    
    loadPreset(presetId) {
        return fetch(`/hud/api/presets/${presetId}/`)
            .then(r => r.json())
            .then(preset => {
                HUD.Storage.storeGenerationSettings(
                    HUD.Main.getCurrentTemplate(), 
                    preset.settings_json
                );
                HUD.Utils.updateFormWithStoredSettings(preset.settings_json);
                HUD.Templates.updatePreviewImage(HUD.Main.getCurrentTemplate());
            });
    },
    
    setHomePerson(gedcomHash, individualId, individualName) {
        return fetch(`/hud/api/home-person/${gedcomHash}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                individual_id: individualId, 
                individual_name: individualName 
            })
        });
    },
    
    loadIndividualSettings(gedcomHash, individualId) {
        return fetch(`/hud/api/individual-settings/${gedcomHash}/${individualId}/`)
            .then(r => r.json())
            .then(data => {
                if (data.settings_json) {
                    HUD.Storage.storeGenerationSettings(
                        HUD.Main.getCurrentTemplate(),
                        data.settings_json
                    );
                    HUD.Utils.updateFormWithStoredSettings(data.settings_json);
                }
                return data;
            });
    }
};
```

---

## 2. Persistent Buffer Storage

### 2.1 Requirements

- Generated chart images stored to disk (not just memory)
- Fast loading on return visits (check disk before regenerating)
- Automatic invalidation when settings change
- Automatic invalidation when chart generation algorithm changes
- Per-user storage quota enforcement
- Cleanup utilities for maintenance

### 2.2 Database Model

```python
class ChartBuffer(models.Model):
    """
    Long-term stored chart buffer images.
    
    Cache key: {user_id}:{gedcom_hash}:{individual_id}:{generation}:{settings_hash}
    
    Invalidated when:
    - Settings change (settings_hash differs)
    - Chart algorithm changes (chart_version differs)
    - User deletes gedcom or individual
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chart_buffers'
    )
    gedcom_hash = models.CharField(max_length=64)
    individual_id = models.CharField(max_length=100)
    generation = models.PositiveSmallIntegerField()
    settings_hash = models.CharField(max_length=32)  # Hash of settings used
    chart_version = models.CharField(max_length=16)  # For algorithm changes
    buffer_file = models.FileField(upload_to='buffers/')
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            'user', 'gedcom_hash', 'individual_id', 'generation'
        ]
        indexes = [
            models.Index(fields=['user', 'gedcom_hash', 'individual_id']),
            models.Index(fields=['user', 'last_accessed']),
        ]

    def __str__(self):
        return f"{self.generation}gen for {self.individual_id}"
```

### 2.3 Storage Manager

```python
import hashlib
import os
from datetime import timedelta
from django.conf import settings
from django.core.files.storage import default_storage


class PersistentBufferManager:
    """
    Manages chart buffer storage with both memory and disk layers.
    
    Layer 1: Memory cache (SimpleBufferManager) - fastest
    Layer 2: Disk storage (this class) - persistent
    """
    
    # Chart version - bump this when generation algorithm changes
    CHART_VERSION = "2.0"
    
    def __init__(self):
        self.memory_manager = SimpleBufferManager()  # In-memory cache
    
    def _compute_gedcom_hash(self, filename: str) -> str:
        """Hash gedcom filename for identification"""
        return hashlib.sha256(filename.encode()).hexdigest()
    
    def _compute_settings_hash(self, settings: dict) -> str:
        """Hash settings for cache key"""
        import json
        settings_str = json.dumps(settings, sort_keys=True)
        return hashlib.md5(settings_str.encode()).hexdigest()[:16]
    
    def _get_buffer_path(self, user_id, gedcom_hash, individual_id, generation):
        """Generate storage path for buffer"""
        return f"buffers/{user_id}/{gedcom_hash}/{individual_id}/{generation}.png"
    
    def get_buffer(
        self, 
        user, 
        gedcom_name: str,
        individual_id: str, 
        generation: int, 
        settings: dict
    ):
        """
        Get buffer, trying memory first then disk.
        Returns BytesIO buffer or None if not found.
        """
        gedcom_hash = self._compute_gedcom_hash(gedcom_name)
        settings_hash = self._compute_settings_hash(settings)
        
        # 1. Try memory cache first
        memory_buffer = self.memory_manager.get_buffer(
            generation, individual_id, settings
        )
        if memory_buffer:
            return memory_buffer
        
        # 2. Try disk storage
        try:
            buffer_record = ChartBuffer.objects.get(
                user=user,
                gedcom_hash=gedcom_hash,
                individual_id=individual_id,
                generation=generation,
                settings_hash=settings_hash,
                chart_version=self.CHART_VERSION
            )
            
            # Verify file exists
            if buffer_record.buffer_file:
                # Load into memory and return
                buffer_data = buffer_record.buffer_file.read()
                buffer_record.last_accessed = timezone.now()
                buffer_record.save(update_fields=['last_accessed'])
                
                # Also promote to memory cache
                fresh_buffer = BytesIO(buffer_data)
                self.memory_manager.store_buffer(
                    generation, individual_id, settings, fresh_buffer
                )
                return BytesIO(buffer_data)
                
        except ChartBuffer.DoesNotExist:
            pass
        
        return None
    
    def store_buffer(
        self,
        user,
        gedcom_name: str,
        individual_id: str,
        generation: int,
        settings: dict,
        buffer_data: BytesIO
    ):
        """
        Store buffer to disk and memory.
        Returns success boolean.
        """
        gedcom_hash = self._compute_gedcom_hash(gedcom_name)
        settings_hash = self._compute_settings_hash(settings)
        file_size = len(buffer_data.getvalue())
        
        # Check quota
        quota, _ = UserStorageQuota.objects.get_or_create(user=user)
        if not quota.can_store(file_size):
            # Try to clean up old buffers
            self.cleanup_old_buffers(user, target_free=file_size)
            quota.refresh_from_db()
            if not quota.can_store(file_size):
                return False
        
        # Save to disk
        buffer_path = self._get_buffer_path(user.id, gedcom_hash, individual_id, generation)
        
        # Write to storage
        saved_path = default_storage.save(buffer_path, buffer_data)
        
        # Create or update database record
        buffer_record, created = ChartBuffer.objects.update_or_create(
            user=user,
            gedcom_hash=gedcom_hash,
            individual_id=individual_id,
            generation=generation,
            defaults={
                'settings_hash': settings_hash,
                'chart_version': self.CHART_VERSION,
                'buffer_file': saved_path,
                'file_size': file_size,
                'width': 1950,  # Standard chart width
                'height': 1950,  # Standard chart height
            }
        )
        
        # Update quota
        quota.add_usage(file_size)
        
        # Also store in memory
        buffer_data.seek(0)
        self.memory_manager.store_buffer(
            generation, individual_id, settings, buffer_data
        )
        
        return True
    
    def invalidate(
        self,
        user,
        gedcom_name: str,
        individual_id: str,
        generation: int = None
    ):
        """
        Invalidate buffers for specific individual/gedcom.
        If generation is None, invalidate all generations.
        """
        gedcom_hash = self._compute_gedcom_hash(gedcom_name)
        
        queryset = ChartBuffer.objects.filter(
            user=user,
            gedcom_hash=gedcom_hash,
            individual_id=individual_id
        )
        
        if generation is not None:
            queryset = queryset.filter(generation=generation)
        
        # Get sizes for quota adjustment
        total_size = queryset.aggregate(models.Sum('file_size'))['file_size__sum'] or 0
        
        # Delete files
        for record in queryset:
            if record.buffer_file:
                record.buffer_file.delete()
        
        # Update quota
        quota = UserStorageQuota.objects.get(user=user)
        quota.release_usage(total_size)
        
        # Delete records
        deleted_count, _ = queryset.delete()
        
        # Also invalidate memory
        if generation:
            # Invalidate specific generation in memory
            pass  # SimpleBufferManager doesn't support selective invalidation
        
        return deleted_count
    
    def cleanup_old_buffers(self, user, target_free: int = 0):
        """
        Delete oldest buffers until target_free bytes are available.
        """
        quota = UserStorageQuota.objects.get(user=user)
        
        if quota.bytes_used + target_free <= quota.bytes_limit:
            return  # Already have space
        
        # Get oldest buffers first
        buffers = ChartBuffer.objects.filter(
            user=user
        ).order_by('last_accessed')
        
        freed = 0
        for buffer in buffers:
            if freed >= target_free:
                break
            
            file_size = buffer.file_size
            buffer.buffer_file.delete()
            buffer.delete()
            freed += file_size
            quota.release_usage(file_size)
        
        return freed
    
    def get_storage_usage(self, user) -> dict:
        """Get storage usage statistics"""
        quota, _ = UserStorageQuota.objects.get_or_create(user=user)
        
        return {
            'bytes_used': quota.bytes_used,
            'bytes_limit': quota.bytes_limit,
            'usage_percentage': quota.usage_percentage,
            'buffer_count': ChartBuffer.objects.filter(user=user).count(),
        }
```

### 2.4 Privacy & Security

```python
# In views.py - ensure users can only access their own data

@login_required
def get_individual_settings(request, gedcom_hash, individual_id):
    try:
        settings = IndividualSettings.objects.get(
            user=request.user,
            gedcom_hash=gedcom_hash,
            individual_id=individual_id
        )
        return JsonResponse({'settings_json': settings.settings_json})
    except IndividualSettings.DoesNotExist:
        return JsonResponse({'settings_json': None})


@login_required  
def get_buffer(request, gedcom_name, individual_id, generation):
    manager = PersistentBufferManager()
    buffer = manager.get_buffer(
        user=request.user,
        gedcom_name=gedcom_name,
        individual_id=individual_id,
        generation=generation,
        settings=request.POST.get('settings', {})
    )
    
    if buffer:
        return HttpResponse(buffer, content_type='image/png')
    else:
        return JsonResponse({'error': 'Buffer not found'}, status=404)
```

### 2.5 File Storage Security

```python
# settings.py

# Private media root (not publicly accessible)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# For production, ensure buffers are not directly accessible:
# - Use X-Sendfile or similar
# - Or serve through Django view with authentication check

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
```

---

## 3. Integration with Current System

### 3.1 Modified Buffer Flow

```
User Request → PersistentBufferManager.get_buffer()
                    │
                    ├─→ Memory Cache (SimpleBufferManager)
                    │       └─→ Return if hit
                    │
                    ├─→ Database Lookup
                    │       ├─→ Found + version match → Return + promote to memory
                    │       └─→ Not found / version mismatch → Continue
                    │
                    └─→ Generate New → PersistentBufferManager.store_buffer()
                                            │
                                            ├─→ Check quota
                                            ├─→ Save to disk
                                            ├─→ Create DB record
                                            ├─→ Update quota
                                            └─→ Store in memory
```

### 3.2 Settings Auto-Load Flow

```
User Selects Individual → Check IndividualSettings
                                │
                                ├─→ Found → Apply settings to form → Generate preview
                                │
                                └─→ Not found → Check presets
                                                    │
                                                    ├─→ Default preset → Apply
                                                    └─→ No preset → Use defaults
```

### 3.3 Version Invalidation

```python
# When generating preview, check version
def generate_preview(request, template):
    user_settings = request.POST.get('user_settings', {})
    
    # This will return None if chart version changed
    buffer = persistent_buffer_manager.get_buffer(
        user=request.user,
        gedcom_name=gedcom_name,
        individual_id=individual_id,
        generation=int(template),
        settings=user_settings
    )
    
    if buffer is None:
        # Generate new (will be automatically stored)
        buffer = generate_chart(...)
        persistent_buffer_manager.store_buffer(...)
    
    return buffer
```

---

## 4. User Interface

### 4.1 Settings Panel Enhancements

```html
<!-- In display_tree.html or settings panel -->
<div class="settings-actions">
    <button id="save-preset" class="btn btn-secondary">
        Save as Preset
    </button>
    <button id="set-home-person" class="btn btn-primary">
        Set as Home Person
    </button>
    <button id="load-presets" class="btn btn-outline-secondary">
        Load Preset ▾
    </button>
</div>

<!-- Preset dropdown (populated via JS) -->
<div id="preset-dropdown" class="dropdown-menu">
    <!-- Populated from /hud/api/presets/ -->
</div>
```

### 4.2 Storage Management UI

```html
<div id="storage-usage" class="card">
    <div class="card-body">
        <h6>Storage Usage</h6>
        <div class="progress">
            <div class="progress-bar" style="width: {{ usage_percentage }}%">
                {{ bytes_used|filesizeformat }} / {{ bytes_limit|filesizeformat }}
            </div>
        </div>
        <button id="clear-cache" class="btn btn-sm btn-outline-danger mt-2">
            Clear All Cached Charts
        </button>
    </div>
</div>
```

---

## 5. Cleanup & Maintenance

### 5.1 Automatic Cleanup Tasks

```python
# management/commands/cleanup_buffers.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Clean up old or invalid buffers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete buffers not accessed in N days'
        )
        parser.add_argument(
            '--quota',
            action='store_true',
            help='Reclaim space if over quota'
        )

    def handle(self, *args, **options):
        # Delete old buffers
        if options['days']:
            cutoff = timezone.now() - timedelta(days=options['days'])
            old_buffers = ChartBuffer.objects.filter(
                last_accessed__lt=cutoff
            )
            count = old_buffers.count()
            old_buffers.delete()
            self.stdout.write(f'Deleted {count} old buffers')

        # Reclaim quota space
        if options['quota']:
            for quota in UserStorageQuota.objects.all():
                if quota.bytes_used > quota.bytes_limit:
                    # This would need custom logic
                    pass
```

### 5.2 User-Initiated Cleanup

```javascript
function clearAllBuffers() {
    if (!confirm('This will delete all cached charts. You will need to regenerate them. Continue?')) {
        return;
    }
    
    fetch('/hud/api/buffers/clear-all/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() }
    })
    .then(r => r.json())
    .then(data => {
        showMessage('All cached charts cleared');
        location.reload();
    });
}
```

---

## 6. Implementation Phases

### Phase 1: Database & Models ✅ COMPLETED
- [x] Create database models (`apps/chart_storage/models.py`)
- [x] Run migrations
- [x] Create UserStorageQuota on first login (signal) - NOT YET IMPLEMENTED (future)

### Phase 2: Settings Persistence ✅ COMPLETED
- [x] API endpoints for presets (`apps/chart_storage/preset_views.py`)
- [x] API endpoints for individual settings (`apps/chart_storage/individual_settings_views.py`)
- [x] JavaScript integration (`HUD.PresetManager` in `hud-organized.js`)
- [x] UI for save/load presets (buttons in HUD)
- [x] Home person designation with GedcomFile integration

### Phase 3: Buffer Persistence 🔄 PENDING
- [ ] PersistentBufferManager class (uses database + disk storage)
- [ ] Integrate with existing generator views for PDF downloads
- [ ] Quota enforcement when storing buffers
- [ ] Version checking (invalidate buffers when code changes)
- [ ] Storage usage display in UI
- [ ] User-initiated cache clearing

### Future Enhancements
- [ ] Export/Import settings as JSON
- [ ] Automatic cleanup tasks (delete old buffers)
- [ ] Signal to create UserStorageQuota on first login
- [ ] Cross-file matching for shared individuals (advanced)

### Phase 4: UI & Polish 🔄 PARTIALLY COMPLETE
- [x] Storage usage display in HUD
- [x] Clear cache button in HUD
- [ ] Export/import settings (future)
- [ ] Testing & bug fixes (ongoing)

---

## 7. Implemented API Endpoints

All endpoints require authentication (login).

### Settings Presets
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/storage/presets/` | GET | List all presets |
| `/storage/presets/create/` | POST | Create new preset |
| `/storage/presets/<id>/` | GET | Get preset details |
| `/storage/presets/<id>/update/` | PUT | Update preset |
| `/storage/presets/<id>/delete/` | DELETE | Delete preset |
| `/storage/presets/<id>/set-default/` | POST | Set as default preset |

### Individual Settings
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/storage/individual-settings/` | GET | List all individual settings |
| `/storage/individual-settings/save/` | POST | Save settings for individual |
| `/storage/individual-settings/<gedcom_hash>/<indi_id>/` | GET | Get settings for individual |
| `/storage/individual-settings/<gedcom_hash>/<indi_id>/delete/` | DELETE | Delete settings |
| `/storage/home-person/set/` | POST | Set home person |
| `/storage/home-person/<gedcom_hash>/` | GET | Get home person |

### Storage Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/storage/storage/usage/` | GET | Get storage quota usage |
| `/storage/storage/clear/` | POST | Clear all buffers |

---

## 8. Constants

```python
# In a constants file
class ChartConstants:
    # Chart dimensions
    CHART_WIDTH = 1950
    CHART_HEIGHT = 1950
    
    # Storage
    DEFAULT_STORAGE_QUOTA = 500 * 1024 * 1024  # 500MB
    
    # Buffer
    CHART_VERSION = "2.0"  # Bump on algorithm changes
    
    # Cleanup
    DEFAULT_CLEANUP_DAYS = 90  # Delete buffers not accessed in 90 days
    MAX_BUFFERS_PER_USER = 1000  # Safety limit
```

---

## 8. Testing Considerations

1. **Settings Persistence**
   - Save preset → reload page → preset still exists
   - Save individual settings → switch to different individual → switch back → settings restored
   - Set home person → appears as default when loading gedcom

2. **Buffer Persistence**
   - Generate 3gen chart → refresh page → loads from cache (no regeneration)
   - Change settings → buffer invalidated → regenerates
   - Code version changes → all buffers invalidated → regenerate

3. **Quota**
   - Fill quota → try to generate → appropriate error message
   - Clear cache → quota freed

4. **Privacy**
   - User A's buffers not accessible to User B
   - Export includes all user data
   - Delete account → all data removed
