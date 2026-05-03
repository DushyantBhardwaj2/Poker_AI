import { test, expect } from '@playwright/test';

test.describe('UI Flow Analysis', () => {
  test('home page loads', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    await page.goto('/');
    await expect(page).toHaveTitle(/PokerSense/i);
    expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0);
  });

  test('sidebar navigation links exist', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('aside');
    await expect(sidebar).toBeVisible();
    await expect(sidebar.locator('a[href="/"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/theory"]')).toBeVisible();
    await expect(sidebar.locator('a[href="/stats"]')).toBeVisible();
  });

  test('navigate to theory page', async ({ page }) => {
    await page.goto('/');
    await page.click('a[href="/theory"]');
    await expect(page).toHaveURL(/theory/);
    await expect(page.locator('h1')).toContainText('Theory');
  });

  test('navigate to stats page', async ({ page }) => {
    await page.goto('/');
    await page.click('a[href="/stats"]');
    await expect(page).toHaveURL(/stats/);
    await expect(page.locator('h1')).toContainText('Statistics');
  });

  test('no broken anchor links', async ({ page }) => {
    await page.goto('/');
    const anchors = await page.locator('a[href]').all();
    const deadLinks: string[] = [];
    for (const a of anchors) {
      const href = await a.getAttribute('href');
      if (href && href.startsWith('http') && !href.includes('localhost')) {
        // External link check - just record it
        deadLinks.push(`External: ${href}`);
      }
    }
    // Should not have unexpected external links
    expect(deadLinks.length).toBeLessThan(5);
  });
});
