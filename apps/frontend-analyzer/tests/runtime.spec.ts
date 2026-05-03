import { test, expect } from '@playwright/test';

test.describe('Runtime Monitoring', () => {
  test('no JS errors on home page load', async ({ page }) => {
    const jsErrors: string[] = [];
    page.on('pageerror', err => jsErrors.push(err.message));
    await page.goto('/');
    await page.waitForTimeout(2000);
    expect(jsErrors).toHaveLength(0);
  });

  test('no JS errors on theory page', async ({ page }) => {
    const jsErrors: string[] = [];
    page.on('pageerror', err => jsErrors.push(err.message));
    await page.goto('/theory');
    await page.waitForTimeout(1000);
    expect(jsErrors).toHaveLength(0);
  });

  test('no JS errors on stats page', async ({ page }) => {
    const jsErrors: string[] = [];
    page.on('pageerror', err => jsErrors.push(err.message));
    await page.goto('/stats');
    await page.waitForTimeout(2000);
    expect(jsErrors).toHaveLength(0);
  });

  test('failed API calls are handled gracefully', async ({ page }) => {
    // Backend may not be running; UI should not crash
    const jsErrors: string[] = [];
    page.on('pageerror', err => jsErrors.push(err.message));
    await page.goto('/stats');
    await page.waitForTimeout(3000);
    // Page should still be visible even if API fails
    await expect(page.locator('body')).toBeVisible();
    expect(jsErrors).toHaveLength(0);
  });

  test('console warnings logged for missing API', async ({ page }) => {
    const messages: { type: string; text: string }[] = [];
    page.on('console', msg => messages.push({ type: msg.type(), text: msg.text() }));
    await page.goto('/stats');
    await page.waitForTimeout(3000);
    const criticalErrors = messages.filter(m =>
      m.type === 'error' && !m.text.includes('favicon') && !m.text.includes('CORS') && !m.text.includes('ERR_CONNECTION_REFUSED')
    );
    expect(criticalErrors).toHaveLength(0);
  });
});
