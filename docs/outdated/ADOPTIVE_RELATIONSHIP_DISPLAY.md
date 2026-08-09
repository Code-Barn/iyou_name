# Adoptive/Foster Relationship Display Plan

## Overview
This document outlines the display strategy for adoptive and foster relationships across the individual detail page.

## Relationship Types

### 1. Adopted Child's Page (Joe Williams)
**Display in Parents section:**
- Father: Robert Eugene Williams **(adoptive)** ← change from "(adopted)"
- Mother: Mary Ann Wilson

**If biological parents are known:**
- Show "(biological father: [name] or unknown)" 
- Show "(biological mother: [name] or unknown)"

**Example:**
- Joe Williams → Father: Robert Williams (adoptive), biological mother: Mary Ann Wilson

### 2. Adoptive Parent's Page (Robert Williams)
**Display in Children section:**
- Joe Williams **(adopted)** ← keep as-is, don't show biological parent names

### 3. Spouse's Page Who Is Biological Parent (Mary Ann Wilson)
**Display in Children section under spouse:**
- Joe Williams **(biological father: unknown)** ← shows spouse is NOT the biological father

### 4. Adopted Child With No Biological Parents Known
**Display:**
- Joe Williams (biological father: unknown, biological mother: unknown)

## Implementation Plan

### Step 1: Change "(adopted)" to "(adoptive)" on child's page
- Update template to show "(adoptive)" instead of "(adopted)" for parents

### Step 2: Add biological parent display for adopted children on their own page
- When showing father/mother, also indicate biological parent if different

### Step 3: Fix spouse's children section
- Always show biological parent info when current spouse is not the biological parent
- Use "unknown" when biological parent is not in the system

### Step 4: Handle case of adopted child with one biological parent
- Show both biological parents if known (or unknown if not)

## Template Locations
- `/apps/core/templates/core/components/family_info.html`
  - Parents section (father/mother labels)
  - Children section under spouses

## View Changes
- `/apps/browse/views.py` - already has `children_relationship` dict
- May need to pass additional context for biological parent info
