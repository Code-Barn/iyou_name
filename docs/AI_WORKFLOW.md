# AI Workflow for Namechart Project

## Before Starting Any Task

1. **READ THE PROJECT STRUCTURE DOCUMENTATION**
   - Always start by reading `docs/PROJECT_STRUCTURE.md`
   - Understand the app structure and key principles

2. **EXAMINE THE RELEVANT APP**
   - Look at the app's `README.md` if it exists
   - Check the app's `apps.py` for its purpose
   - Review existing templates and their structure

3. **UNDERSTAND THE CURRENT STRUCTURE**
   - Use `find_path` to locate relevant files
   - Use `grep` to search for existing patterns
   - Check `INSTALLED_APPS` in settings if needed

## Key Rules to Remember

1. **SHARED COMPONENTS GO IN CORE**
   - Any component that might be used across multiple apps → `core/templates/core/components/`
   - Reference as: `{% include 'core/components/xxx.html' %}`

2. **APP-SPECIFIC COMPONENTS GO IN THEIR APP**
   - Components only used in one app → `app/templates/app/components/`
   - Reference as: `{% include 'app/components/xxx.html' %}`

3. **GENERATOR IS NOT FOR SHARED COMPONENTS**
   - Generator is a coordination layer only
   - Shared components belong in `core`, not `generator`

4. **ALWAYS EXTEND CORE/BASE.HTML**
   - All templates should extend: `{% extends 'core/base.html' %}`

## When Unsure

1. **LOOK FOR EXISTING PATTERNS**
   - Search for similar functionality in the codebase
   - Follow the same structure as existing code

2. **ASK FOR CLARIFICATION**
   - If I'm unsure about where something should go
   - If the best approach isn't clear
   - Before making structural changes

3. **DON'T RUSH**
   - Take time to understand the context
   - Read documentation and comments
   - Think through implications

## Common Mistakes to Avoid

1. **Putting shared components in generator** → Use core instead
2. **Creating duplicate components** → Reuse existing ones
3. **Not checking existing patterns** → Always look first
4. **Assuming I remember the structure** → Always verify
5. **Making changes without understanding** → Read first, act second

## Quick Reference

- **Core app**: `apps/core/` - Shared resources
- **Browse app**: `apps/browse/` - Individual browsing
- **Upload app**: `apps/upload/` - File uploads
- **Charts app**: `apps/charts/` - Chart generation
- **HUD app**: `apps/hud/` - Interactive preview
- **Users app**: `apps/users/` - Authentication
- **Generator app**: `apps/generator/` - Coordination layer ONLY