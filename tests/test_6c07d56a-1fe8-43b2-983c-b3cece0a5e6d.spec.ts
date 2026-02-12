
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('Test_2026-02-03', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:8000/hud/');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Select option
    await page.selectOption('#template-select', '3');

    // Wait for response
    const 3gen-previewResponse = page.waitForResponse('**/get-template-preview/3/**');

    // Assert response
    expect(3gen-previewResponse.ok()).toBeTruthy();

    // Take screenshot
    await page.screenshot({ path: '3gen-preview.png' });

    // Navigate to URL
    await page.goto('http://localhost:8000/upload/');

    // Navigate to URL
    await page.goto('http://localhost:8000/upload-file/');
});