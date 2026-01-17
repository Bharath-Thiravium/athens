import { test, expect } from '@playwright/test';

test('SAP auth setup', async ({ page, baseURL }) => {
  if (!baseURL) throw new Error('SAP_BASE_URL missing');

  await page.goto(baseURL, { waitUntil: 'domcontentloaded' });

  const mode = process.env.SAP_LOGIN_MODE || 'master';
  if (mode === 'company') {
    await page.click('button:has-text("Company User")');
  } else if (mode === 'service') {
    await page.click('button:has-text("Service User")');
  }

  await page.fill('input[name="email"]', process.env.SAP_TEST_EMAIL || '');
  await page.fill('input[name="password"]', process.env.SAP_TEST_PASSWORD || '');
  await page.click('button:has-text("Sign In")');

  await page.waitForURL(/\/(master-admin|company|service)/, { timeout: 30_000 });

  await page.context().storageState({ path: './.auth/sap.json' });

  expect(page.url()).toMatch(/\/(master-admin|company|service)/);
});
