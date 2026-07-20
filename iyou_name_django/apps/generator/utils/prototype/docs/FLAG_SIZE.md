# Flag Size and Positioning

## Overview

Flags are rendered within `print_individual()` for generations 1-7. Each generation uses its own generation-specific flag size setting.

## Generation-Specific Flag Sizes

| Generation | Setting | Default |
|------------|---------|---------|
| 1gen | `gen1_flag_size` | 666 |
| 2gen | `gen2_flag_size` | 333 |
| 3gen | `gen3_flag_size` | 200 |
| 4gen | `gen4_flag_size` | 142 |
| 5gen | `gen5_flag_size` | 111 |
| 6gen | `gen6_flag_size` | 90 |
| 7gen | `gen7_flag_size` | 77 |

## Implementation

Each generator passes `flag_size` explicitly to `print_individual()`:

```python
flag_size=validated_settings.get("genX_flag_size", DEFAULT)
```

## Position Constants

Each generation defines flag position constants in their `GenerationXConstants` class:

- 4gen: `FLAG_A1_BASE_X/Y`, `FLAG_A2_BASE_X/Y` (2 master positions)
- 5gen: `FLAG_A11-A22_BASE_X/Y` (4 master positions)
- 6gen: `FLAG_A111-A222_BASE_X/Y` (8 master positions)
- 7gen: `FLAG_A1111-A2222_BASE_X/Y` (16 master positions)

Flag positions are offsets from the image center (975, 975) and are rotated based on the subclade's rotation parameter.

## To Remove genX_flag_size

If you ever need to remove generation-specific flag sizes:

1. Remove `genX_flag_size` from each generator's `GENERATION_X_SETTINGS_SCHEMA`
2. Remove flag position constants from each generator's `GenerationXConstants` class
3. Remove flag parameter passing from `print_individual()` calls
4. Update settings templates to remove flag size sliders

## Legacy Note (March 2026)

`place_flag_size` was previously used as a global setting. It has been removed in favor of generation-specific settings. The fallback in `individual_printer.py` was removed.

If you need to restore backwards compatibility with old saved settings that might contain `place_flag_size`, you could add a fallback:

```python
flag_size = flag_size or settings.get("genX_flag_size", settings.get("place_flag_size", 48))
```
