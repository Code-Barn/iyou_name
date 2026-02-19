# 6-Generation Position Debugging Guide

## Overview

This document captures the debugging journey and learnings from positioning the 6-generation chart great-great-great-grandparent positions.

## Key Discoveries

### 1. Position Ordering
The 6-gen chart has 32 positions (A111-A222, B111-B222, C111-C222, D111-D222) arranged in 4 quadrants:
- **A Subclade**: Paternal grandfather's line (rotation=0, bottom edge)
- **B Subclade**: Paternal grandmother's line (rotation=270, right edge)
- **C Subclade**: Maternal grandfather's line (rotation=180, top edge)
- **D Subclade**: Maternal grandmother's line (rotation=90, left edge)

### 2. Master-Master (A1) Position Logic
The A1 positions (A111, A112, A121, A122) are the "master" positions. All other A2 positions mirror these across the centerline (x=975).

**Spacing Formula**:
- Positions are evenly spaced at 211px intervals
- Starting position: A111 at x=225
- Subsequent: A112 at x=436, A121 at x=647, A122 at x=858

### 3. Mirroring Formula
For A2 positions, mirror across x=975:
```
A222_x = 975 + (975 - A111_x) = 1950 - A111_x
A221_x = 975 + (975 - A112_x) = 1950 - A112_x
A212_x = 975 + (975 - A121_x) = 1950 - A121_x
A211_x = 975 + (975 - A122_x) = 1950 - A122_x
```

### 4. Y-Axis Adjustment
After visual testing, positions needed a 30px downward shift to align with template compartments:
- Original Y: 1835
- Final Y: 1865 (for names)
- Birth date Y: 1815 (50px above name)
- Birth place Y: 1949 (84px below name)

## Final Position Constants

| Position | Name X | Name Y | Birth Date X | Birth Date Y | Birth Place X | Birth Place Y |
|----------|--------|--------|--------------|--------------|---------------|---------------|
| A111     | 225    | 1865   | 265          | 1815         | 185           | 1949          |
| A112     | 436    | 1865   | 476          | 1815         | 396           | 1949          |
| A121     | 647    | 1865   | 687          | 1815         | 607           | 1949          |
| A122     | 858    | 1865   | 898          | 1815         | 818           | 1949          |
| A211     | 1092   | 1865   | 1052         | 1815         | 1132          | 1949          |
| A212     | 1303   | 1865   | 1263         | 1815         | 1343          | 1949          |
| A221     | 1514   | 1865   | 1474         | 1815         | 1554          | 1949          |
| A222     | 1725   | 1865   | 1685         | 1815         | 1765          | 1949          |

## Debug Script Usage

Run the debug script to visualize positions:
```bash
cd /home/user/CODE_BASE/namechart
PYTHONPATH=/home/user/CODE_BASE/namechart uv run python apps/generator/utils/prototype/debug_6gen_positions.py
```

Output: `debug_6gen_positions.png`

## Rotation Application

The B, C, D subclades use the SAME position constants as A, with rotation applied:
- B Subclade: rotation=270 (right side, text reads upward)
- C Subclade: rotation=180 (top, text reads upside down)
- D Subclade: rotation=90 (left side, text reads downward)

This ensures all subclades follow the same ordering pattern automatically.

## Lessons Learned

1. **Define once, rotate many times**: Position constants should only be defined for the A subclade; B/C/D reuse them with rotation
2. **Visual debugging is essential**: Template inspection revealed the 8-compartment-per-edge structure
3. **Mirroring simplifies maintenance**: Calculate A2 from A1 rather than manually specifying both
4. **Order matters**: A111→A112→A121→A122→A211→A212→A221→A222 ensures proper left-to-right reading
