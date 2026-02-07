
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('Test_2026-02-06', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:8000');

    // Navigate to URL
    await page.goto('http://localhost:8000');

    // Navigate to URL
    await page.goto('http://localhost:8000/upload/');

    // Navigate to URL
    await page.goto('http://localhost:8000/upload-file/');

    // Click element
    await page.click('input[name="primary_background_color"]');

    // Fill input field
    await page.fill('input[name="primary_background_color"]', '#ff0000');

    // Click element
    await page.click('button[id="apply-settings"]');

    // Click element
    await page.click('button[id="apply-settings"]');
});