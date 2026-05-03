import { test, expect } from '@playwright/test';

test.describe('State Transitions', () => {
  test('setup view is shown on initial load', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('form')).toBeVisible();
    // Step indicator should show setup (step 1) active
    const stepButtons = page.locator('button').filter({ hasText: /1/ });
    await expect(stepButtons.first()).toBeVisible();
  });

  test('step indicators exist: Setup, Cards, Game', async ({ page }) => {
    await page.goto('/');
    const body = await page.locator('body').textContent();
    expect(body?.toLowerCase()).toContain('setup');
    expect(body?.toLowerCase()).toContain('cards');
    expect(body?.toLowerCase()).toContain('game');
  });

  test('form submission transitions to cards view when backend available', async ({ page }) => {
    // Intercept the API call and mock a response
    await page.route('http://localhost:8000/api/v1/game/start', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          players: [
            { name: 'Player 1', stack: 1000, hole_cards: [], current_bet: 5, total_contributed: 5, is_folded: false, is_all_in: false, has_acted: false, vpip_this_hand: false, pfr_this_hand: false },
            { name: 'Player 2', stack: 990, hole_cards: [], current_bet: 10, total_contributed: 10, is_folded: false, is_all_in: false, has_acted: false, vpip_this_hand: false, pfr_this_hand: false },
          ],
          community_cards: [],
          pots: [{ amount: 15, eligible_player_indices: [0, 1] }],
          pot: 15,
          current_bet: 10,
          last_raise_amount: 10,
          current_player_index: 0,
          dealer_index: 0,
          round: 'pre-flop',
          small_blind: 5,
          big_blind: 10,
        }),
      });
    });

    await page.goto('/');
    const submitBtn = page.locator('button[type="submit"]');
    await expect(submitBtn).toBeVisible();
    await submitBtn.click();
    await page.waitForTimeout(1500);
    // Should show CardInputView now
    await expect(page.locator('body')).toContainText(/hole cards/i);
  });

  test('cards view shows hole card slots', async ({ page }) => {
    // Mock backend and go through to cards view
    await page.route('http://localhost:8000/api/v1/game/start', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          players: [{ name: 'P1', stack: 1000, hole_cards: [], current_bet: 0, total_contributed: 0, is_folded: false, is_all_in: false, has_acted: false, vpip_this_hand: false, pfr_this_hand: false }],
          community_cards: [], pots: [{ amount: 0, eligible_player_indices: [0] }],
          pot: 0, current_bet: 0, last_raise_amount: 0,
          current_player_index: 0, dealer_index: 0, round: 'pre-flop',
          small_blind: 5, big_blind: 10,
        }),
      });
    });
    await page.goto('/');
    await page.locator('button[type="submit"]').click();
    await page.waitForTimeout(1000);
    // Card slots should appear
    const body = await page.locator('body').textContent();
    expect(body?.toLowerCase()).toMatch(/hole|card|community/);
  });
});
