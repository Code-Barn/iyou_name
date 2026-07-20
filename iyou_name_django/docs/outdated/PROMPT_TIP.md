# Prompt Tip for Working with Me on Namechart Project

## When Starting a New Session

Please begin with this prompt to help me quickly understand the context:

```
Let's work on the Namechart Django project. Here's what you need to know:

1. PROJECT STRUCTURE:
   - Read docs/PROJECT_STRUCTURE.md for the complete app structure
   - Key apps: core (shared), browse, upload, charts, hud, users, generator (coordination only)

2. CURRENT TASK:
   [Briefly describe what we're working on]

3. IMPORTANT RULES:
   - Shared components go in: apps/core/templates/core/components/
   - App-specific components go in: apps/[app]/templates/[app]/components/
   - Generator is NOT for shared components - use core instead
   - All templates extend: {% extends 'core/base.html' %}

4. RELEVANT FILES:
   [List any specific files we're working with]

Let me know when you've read and understood the project structure.
```

## How This Helps

1. **Sets clear expectations** about what I need to know
2. **Forces me to read** the project structure documentation
3. **Provides context** for the current task
4. **Establishes rules** upfront to avoid mistakes

## Additional Tips

- If I start rushing or making assumptions, remind me: "Please read the project structure documentation first"
- If I suggest putting something in the wrong place, ask: "Does this belong in core (shared) or the specific app?"
- If I seem confused about the structure, direct me: "Check docs/PROJECT_STRUCTURE.md"

This will help me provide better, more accurate assistance with less frustration for both of us.