import { test, expect } from '@playwright/test';

test('Athens E2E: Login and access dashboard', async ({ page }) => {
  const baseURL = process.env.ATHENS_BASE_URL;
  const username = process.env.ATHENS_TEST_USERNAME;
  const password = process.env.ATHENS_TEST_PASSWORD;

  // Navigate to login
  await page.goto(baseURL!);
  
  // Fill credentials
  await page.fill('#username', username!);
  await page.fill('#password', password!);
  await page.click('button[type="submit"]');
  
  // Wait for navigation away from login
  await page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 30_000 });
  
  // Verify token in localStorage
  const token = await page.evaluate(() => localStorage.getItem('token'));
  expect(token).toBeTruthy();
  
  // Verify dashboard title
  await expect(page).toHaveTitle(/EHS Management Dashboard/);
  
  console.log('✓ Athens login successful');
});
