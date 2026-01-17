import { test, expect } from '@playwright/test';

test('Athens auth setup', async ({ page, baseURL }) => {
  if (!baseURL) throw new Error('ATHENS_BASE_URL missing');

  await page.goto(baseURL, { waitUntil: 'domcontentloaded' });

  await page.fill('#username', process.env.ATHENS_TEST_USERNAME || '');
  await page.fill('#password', process.env.ATHENS_TEST_PASSWORD || '');
  await page.click('button[type="submit"]');

  await page.waitForFunction(() => !!localStorage.getItem('token'), null, { timeout: 30_000 });

  await page.context().storageState({ path: './.auth/athens.json' });

  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeTruthy();
});
