import { test, expect } from '@playwright/test';

const LOGIN_MODE = process.env.SAP_LOGIN_MODE || 'master';

test(`SAP E2E: Login as ${LOGIN_MODE} and access dashboard`, async ({ page }) => {
  const baseURL = process.env.SAP_BASE_URL;
  const email = process.env.SAP_TEST_EMAIL;
  const password = process.env.SAP_TEST_PASSWORD;

  // Navigate to login
  await page.goto(baseURL!);
  
  // Select login mode
  if (LOGIN_MODE === 'company') {
    await page.click('button:has-text("Company User")');
  } else if (LOGIN_MODE === 'service') {
    await page.click('button:has-text("Service User")');
  }
  
  // Fill credentials
  await page.fill('input[name="email"]', email!);
  await page.fill('input[name="password"]', password!);
  await page.click('button:has-text("Sign In")');
  
  // Wait for dashboard
  const expectedPath = LOGIN_MODE === 'master' ? /.*master-admin/ : LOGIN_MODE === 'company' ? /.*company/ : /.*service/;
  await page.waitForURL(expectedPath, { timeout: 30_000 });
  
  // Verify not on login page
  await expect(page).not.toHaveURL(/.*\/login/);
  
  console.log(`✓ SAP ${LOGIN_MODE} login successful`);
});
