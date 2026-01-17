import { test, expect } from '@playwright/test';

test('Athens: open dashboard', async ({ page, baseURL }) => {
  await page.goto(baseURL || '');
  
  // Should be on dashboard, not login page
  await expect(page).not.toHaveURL(/.*login/);
  
  // Verify dashboard loaded
  await expect(page).toHaveTitle(/EHS Management Dashboard/);
});
