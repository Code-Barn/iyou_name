
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('Test_2026-02-03', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Select option
    await page.selectOption('#template-select', '3');

    // Select option
    await page.selectOption('#template-select', '2');

    // Select option
    await page.selectOption('#template-select', '1');
});