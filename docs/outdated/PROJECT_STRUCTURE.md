# Namechart Django Project Structure

## Overview
This document provides a quick reference for the project's app structure and organization.

## App Structure

```
apps/
├── core/                  # Core application - shared resources and base templates
│   ├── templates/core/    # Base templates and shared components
│   │   ├── base.html      # Main base template (extends all pages)
│   │   └── components/    # SHARED COMPONENTS (available to all apps)
│   │       ├── individual_header.html
│   │       ├── basic_info.html
│   │       ├── locations.html
│   │       ├── family_info.html
│   │       └── back_button.html
│   └── static/core/       # Core static files (CSS, JS, images)
│
├── generator/             # Generator application - coordination layer
│   ├── templates/generator/ # Generator-specific templates
│   ├── utils/              # Chart generation utilities
│   └── ...                 # Minimal views/urls (most functionality in specific apps)
│
├── browse/                # Browse application - individual browsing
│   ├── templates/browse/  # Browse-specific templates
│   │   ├── browse_individuals.html
│   │   ├── individual_detail.html  # Uses core/components/
│   │   ├── select_individual.html
│   │   └── error.html
│   └── ...                 # Browse-specific views/models
│
├── upload/                # Upload application - GEDCOM file handling
│   ├── templates/upload/  # Upload-specific templates
│   └── ...                 # Upload-specific views/models
│
├── charts/                # Charts application - chart generation
│   ├── templates/charts/  # Chart-specific templates
│   └── ...                 # Chart-specific views/models
│
├── hud/                   # HUD application - interactive preview
│   ├── templates/hud/     # HUD-specific templates
│   └── ...                 # HUD-specific views/models
│
└── users/                 # Users application - authentication
    ├── templates/users/   # User-specific templates
    └── ...                 # User-specific views/models
```

## Key Principles

1. **Core App**: Contains ALL shared resources (base templates, components, static files)
   - Use `core/components/` for any template components that might be used across multiple apps
   - All apps extend `core/base.html`

2. **Generator App**: Coordination layer only
   - Minimal functionality - mostly delegates to specific apps
   - NOT for shared components (use core instead)

3. **Specific Apps**: Each has its own purpose
   - `browse`: Individual browsing and detail views
   - `upload`: GEDCOM file upload and management
   - `charts`: Family tree chart generation
   - `hud`: Interactive preview system
   - `users`: Authentication and user management

4. **Template References**:
   - Shared components: `{% include 'core/components/xxx.html' %}`
   - App-specific templates: `{% include 'app_name/template.html' %}`
   - Always extend: `{% extends 'core/base.html' %}`

## Common Patterns

### Adding a new shared component:
1. Create in `apps/core/templates/core/components/`
2. Reference as `{% include 'core/components/your_component.html' %}`

### Adding an app-specific component:
1. Create in `apps/your_app/templates/your_app/components/`
2. Reference as `{% include 'your_app/components/your_component.html' %}`

## Quick Reference for Future Work

When I (the AI) start working on this project, I should:
1. **First**, read this document to understand the structure
2. **Check** if components should go in `core/` (shared) or specific app (app-specific)
3. **Remember** that `generator` is NOT for shared components - use `core` instead
4. **Look** at existing patterns before creating new structures
5. **Ask** if I'm unsure about where something should go