
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('Test_2026-02-06', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');
});