import { test, expect } from '@playwright/test';

const LOGIN_MODE = process.env.SAP_LOGIN_MODE || 'master';

test.describe('SAP-Python System', () => {
  test(`should access ${LOGIN_MODE} dashboard`, async ({ page, baseURL }) => {
    await page.goto(baseURL!);
    
    // Should be on dashboard, not login page
    await expect(page).not.toHaveURL(/.*\/login/);
    
    // Verify correct dashboard based on mode
    const expectedPath = LOGIN_MODE === 'master' ? /.*master-admin/ : LOGIN_MODE === 'company' ? /.*company/ : /.*service/;
    await expect(page).toHaveURL(expectedPath, { timeout: 10000 });
  });
});
