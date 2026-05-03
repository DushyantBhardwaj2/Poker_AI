import { test, expect } from '@playwright/test';

const VIEWPORTS = [
  { name: 'Mobile S', width: 320, height: 568 },
  { name: 'Tablet', width: 768, height: 1024 },
  { name: 'Laptop', width: 1024, height: 768 },
  { name: 'Desktop', width: 1440, height: 900 },
];

for (const vp of VIEWPORTS) {
  test.describe(`Responsive [${vp.name} ${vp.width}x${vp.height}]`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } });

    test('home page renders without overflow', async ({ page }) => {
      await page.goto('/');
      // Check no horizontal scrollbar
      const hasHScroll = await page.evaluate(() =>
        document.documentElement.scrollWidth > document.documentElement.clientWidth
      );
      expect(hasHScroll).toBe(false);
    });

    test('sidebar is visible', async ({ page }) => {
      await page.goto('/');
      await expect(page.locator('aside')).toBeVisible();
    });

    test('main content visible', async ({ page }) => {
      await page.goto('/');
      await expect(page.locator('main')).toBeVisible();
    });

    test('theory page renders at viewport', async ({ page }) => {
      await page.goto('/theory');
      await expect(page.locator('h1')).toBeVisible();
    });
  });
}
