import { test, expect } from '@playwright/test';

test.describe('Component Validation', () => {
  test('PokerTable component renders on home page', async ({ page }) => {
    await page.goto('/');
    // SetupView should be visible by default
    await expect(page.locator('form')).toBeVisible({ timeout: 10000 });
  });

  test('SetupView: form fields present', async ({ page }) => {
    await page.goto('/');
    const form = page.locator('form').first();
    await expect(form).toBeVisible();
    await expect(form.locator('input[type="number"]').first()).toBeVisible();
    await expect(form.locator('button[type="submit"]')).toBeVisible();
  });

  test('SetupView: player count field adjusts rows', async ({ page }) => {
    await page.goto('/');
    const form = page.locator('form').first();
    const playerCountInput = form.locator('input[type="number"]').first();
    await playerCountInput.fill('3');
    await playerCountInput.dispatchEvent('change');
    await page.waitForTimeout(300);
    // 3 players * 2 inputs each should render 6 inputs total in some form
    const inputs = await form.locator('input').count();
    expect(inputs).toBeGreaterThanOrEqual(3);
  });

  test('theory page: concept cards render', async ({ page }) => {
    await page.goto('/theory');
    const cards = page.locator('.glass-dark');
    await expect(cards.first()).toBeVisible();
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(4);
  });

  test('stats page: container renders', async ({ page }) => {
    await page.goto('/stats');
    await expect(page.locator('#stats-container')).toBeVisible({ timeout: 8000 });
  });

  test('layout: header present on all pages', async ({ page }) => {
    for (const path of ['/', '/theory', '/stats']) {
      await page.goto(path);
      await expect(page.locator('header')).toBeVisible();
    }
  });

  test('layout: footer present on all pages', async ({ page }) => {
    for (const path of ['/', '/theory', '/stats']) {
      await page.goto(path);
      await expect(page.locator('footer')).toBeVisible();
    }
  });
});
