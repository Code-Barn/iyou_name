
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('GenerationTest_2026-02-11', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/selector/');

    // Take screenshot
    await page.screenshot({ path: 'selector_page_initial.png', { fullPage: true } });

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/');

    // Take screenshot
    await page.screenshot({ path: 'home_page.png', { fullPage: true } });

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/browse/');

    // Take screenshot
    await page.screenshot({ path: 'browse_page.png', { fullPage: true } });

    // Click element
    await page.click('a[href*="/select/"]');

    // Take screenshot
    await page.screenshot({ path: 'generator_page.png', { fullPage: true } });

    // Select option
    await page.selectOption('#chart_template', '5');

    // Select option
    await page.selectOption('#template-select', '5');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/hud/display-tree/');

    // Take screenshot
    await page.screenshot({ path: 'generator_page_refreshed.png', { fullPage: true } });

    // Select option
    await page.selectOption('#template-select', '5');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/hud/display-tree/');

    // Take screenshot
    await page.screenshot({ path: 'generator_after_server_restart.png', { fullPage: true } });

    // Select option
    await page.selectOption('#template-select', '5');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/static/hud/js/hud-organized.js');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/hud/display-tree/');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/static/hud/js/hud-organized.js?v=2026-02-11-17-02-23');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/hud/display-tree/');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/hud/display-tree/');

    // Navigate to URL
    await page.goto('http://127.0.0.1:8000/hud/display-tree/');
});