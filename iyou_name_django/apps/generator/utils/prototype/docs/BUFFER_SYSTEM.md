# Buffer System Documentation

## Overview

The buffer system caches generated chart images to avoid redundant computation. When users navigate between generations or apply settings, the system intelligently decides whether to regenerate or use cached data.

## How It Works

### Buffer Storage

Each generation (1-7) has its own buffer cache keyed by:
- Generation number (1-7)
- Individual ID 
- Settings hash (SHA256 of user settings)

```python
buffer_key = f"{generation}_{individual_id}_{settings_hash}"
```

### Navigation Flow

```
User at 1gen (buffer populated)
    │
    ▼ [Click "Next" → 2gen]
Use cached 2gen buffer if exists
    │
    ▼ [Click "Next" → 3gen]  
Use cached 3gen buffer if exists
    │
    ▼ [Click "Apply Settings" with changes]
INVALIDATE all buffers → Regenerate from current gen upward
```

## Key Principles

### 1. Sequential Navigation is Free

Once a generation's buffer is generated, navigating to it again (without settings changes) uses the cached buffer - no regeneration needed.

### 2. Settings Changes Invalidate All

When user clicks "Apply Settings" with any changes:
- All buffers are invalidated
- Charts regenerate starting from current generation
- Parent generations regenerate for overlay use

### 3. Overlay Dependencies

Higher generations (2-7) depend on lower generations (1-6) as overlays. This is why a settings change triggers regeneration up the chain.

```
1gen buffer → used by 2gen overlay
1gen + 2gen buffer → used by 3gen overlay
...
1-6gen buffers → used by 7gen overlay
```

## Implementation Details

### Buffer Manager

```python
class SimpleBufferManager:
    def __init__(self):
        self.buffers = {}  # buffer_key -> BytesIO
    
    def get_buffer(self, generation, individual_id, settings):
        """Return cached buffer if exists and settings match"""
        buffer_key = self._make_key(generation, individual_id, settings)
        return self.buffers.get(buffer_key)
    
    def store_buffer(self, generation, individual_id, settings, buffer):
        """Store generated buffer"""
        # Creates copy to avoid closure issues
        buffer.seek(0)
        buffer_data = buffer.read()
        buffer_size = len(buffer_data)
        buffer_copy = BytesIO(buffer_data)
        self.buffers[buffer_key] = buffer_copy
    
    def invalidate_all(self):
        """Clear all buffers - called on settings change"""
        self.buffers.clear()
```

### Cache Key Generation

```python
def _make_key(self, generation, individual_id, settings):
    settings_str = json.dumps(settings, sort_keys=True)
    settings_hash = hashlib.sha256(settings_str.encode()).hexdigest()[:16]
    return f"{generation}_{individual_id}_{settings_hash}"
```

## Current Behavior

### What Works Well ✅

1. **Initial load**: First visit to any generation generates fresh
2. **Navigate without changes**: Uses cached buffer (fast)
3. **Apply settings**: Invalidates all → regenerates (correct)
4. **Jump navigation**: Works but may miss intermediate buffers

### What Could Be Improved ⚠️

1. **Non-sequential jumps**: If user jumps from 1gen to 5gen directly, intermediate buffers (2-4) may not be populated
2. **No buffer pre-generation**: Could pre-populate next gen buffer on navigation for smoother experience

## Ideal User Flow

```
1. User loads page → 1gen generated
2. User clicks "Next" → 2gen generated, 1gen cached  
3. User clicks "Next" → 3gen generated, 1-2gen cached
4. User adjusts stroke color → clicks "Apply Settings"
5. ALL buffers invalidated
6. 1gen regenerated → cached
7. User clicks "Next" → 2gen uses 1gen overlay → cached
8. User clicks "Next" → 3gen uses 1-2gen overlays → cached
9. User clicks "Prev" → 2gen uses cached (no regen)
10. User clicks "Prev" → 1gen uses cached (no regen)
```

## Performance Benefits

- **No redundant generation**: Each chart generated exactly once per settings state
- **Fast navigation**: Back/forward uses cached images instantly
- **Sequential efficiency**: Walking through generations populates all buffers
- **Settings isolation**: Different settings = different cache entries

## Files

| File | Purpose |
|------|---------|
| `simple_buffer_manager.py` | Buffer storage and retrieval logic |
| `views_simple_buffered.py` | HTTP endpoints that use buffers |
| `hud-organized.js` | Frontend navigation and cache management |

## Future Improvements

1. **Predictive pre-generation**: When user is at gen N, pre-generate gen N+1 buffer in background
2. **Smart invalidation**: Only invalidate buffers affected by changed settings (e.g., color change doesn't affect position settings)
3. **Buffer size limits**: Limit total cache size to prevent memory issues
4. **Persistence**: Store buffers to disk for session recovery
