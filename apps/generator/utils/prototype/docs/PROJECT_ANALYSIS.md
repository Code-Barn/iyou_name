# Prototype Project SWOT Analysis

## Project: Modular Individual Printer for Multi-Generation Charts

### Strengths

1. **DRY Principle**
   - Single `print_individual()` function handles all name rendering
   - Eliminates code duplication across 7+ generator scripts
   
2. **Scalable Architecture**
   - Base position + rotation model works for any generation
   - 2gen: 2 positions (0°, 180°)
   - 3gen: 4 positions (0°, 90°, 180°, 270°)
   - Ngen: 2^(N-1) positions

3. **Standardized Centering**
   - All text uses same: `translate → rotate → center → draw`
   - Predictable, consistent behavior
   - Easy to debug

4. **Separation of Concerns**
   - Individual printer handles rendering
   - Generator scripts handle positioning logic
   - Constants define default positions

5. **Inheritance via Overlays**
   - 2gen composites 1gen
   - 3gen composites 2gen
   - Settings flow through automatically

### Weaknesses

1. **Complexity**
   - Many parameters in print_individual()
   - Rotation math can be confusing
   - Hard to visualize final output

2. **Debugging Difficulty**
   - Hidden canvas - need to render to see issues
   - draw.push/pop nesting critical
   - No visual feedback during development

3. **Tight Coupling**
   - Generator scripts must know exact parameter names
   - Easy to miss parameters when calling function

4. **Testing Gap**
   - No automated visual regression tests
   - Manual verification required

### Opportunities

1. **Higher Generations**
   - 10gen requires 512 positions
   - Current architecture scales naturally
   - Just calculate: `angle = position_index * (360 / total_positions)`

2. **User Customization**
   - Current offset parameters enable per-position tweaking
   - Could add UI controls for each position

3. **Performance**
   - Buffer caching already implemented
   - Could parallelize overlay generation

4. **Consistency**
   - Replace all 7 original generators
   - Single code path for all charts

### Threats

1. **Regression Risk**
   - Changes to individual_printer affect ALL generations
   - Must test all charts after any modification

2. **Parameter Explosion**
   - Each position needs multiple parameters
   - 7gen = 64 positions × many parameters = unwieldy

3. **Rotation Edge Cases**
   - 90°, 270° rotations less tested
   - May need adjustment for higher gens

4. **Legacy Compatibility**
   - Must match original output exactly
   - Risk of subtle differences

---

## Roadmap: Scaling to Higher Generations

### 3gen (4 positions)
```
Positions: 0°, 90°, 180°, 270°
Rotation math: already implemented
Base positions same as 2gen, rotated
```

### 4gen (8 positions)
```
Positions: 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°
New challenge: 45° angles
May need new positioning constants
```

### 10gen (512 positions)
```
Algorithm: angle = position_index * (360 / 512)
Dynamic calculation, not hardcoded
Future enhancement: generate positions mathematically
```

### Recommended Approach
1. Complete 2gen (add birth/death info)
2. Implement 3gen as test case
3. Refactor to use dynamic position calculation
4. Implement 4-7gen using same pattern
5. Consider mathematical generation for 8+

---

## Technical Notes

### Coordinate System
- Canvas: 1950 × 1950 pixels (at 300 DPI)
- Center: (975, 975)
- Edges: 0, 1950

### Rotation Convention
- Positive = clockwise
- Applied around center point

### Text Centering
- Always use: `translate(-text_width // 2, 0)`
- Works for both horizontal and vertical text
- After rotation, still centers correctly

### Overlay Scaling
- 1gen: no overlay
- 2gen: 1gen at 50% scale
- 3gen: 2gen at 25% scale (approximate)
- Formula: `scale = 1 / (generation_number)`
