
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('GenerateFinalChart_2026-01-16', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Wait for response
    const generate_chart_responseResponse = page.waitForResponse('**/generator/generate/');

    // Click element
    await page.click('#hud-generate');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Wait for response
    const generate_chart_responseResponse = page.waitForResponse('**/generator/generate/');

    // Click element
    await page.click('#hud-generate');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Wait for response
    const generate_chart_responseResponse = page.waitForResponse('**/generator/generate/');

    // Click element
    await page.click('#hud-generate');

    // Assert response
    const responseText = await generate_chart_responseResponse.text();
    expect(responseText).toContain('PDF');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');

    // Wait for response
    const generate_chart_responseResponse = page.waitForResponse('**/generator/generate/');

    // Click element
    await page.click('#hud-generate');

    // Assert response
    const responseText = await generate_chart_responseResponse.text();
    expect(responseText).toContain('PDF');

    // Navigate to URL
    await page.goto('http://localhost:8000/hud/display-tree/');
});