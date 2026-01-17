import { chromium } from '@playwright/test';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.e2e' });

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  console.log('Navigating to Athens login...');
  await page.goto(process.env.ATHENS_BASE_URL, { waitUntil: 'networkidle' });
  
  console.log('\n=== Page Title ===');
  console.log(await page.title());
  
  console.log('\n=== Input Fields ===');
  const inputs = await page.$$eval('input', els => els.map(el => ({
    type: el.type,
    name: el.name,
    id: el.id,
    placeholder: el.placeholder,
    className: el.className
  })));
  console.log(JSON.stringify(inputs, null, 2));
  
  console.log('\n=== Buttons ===');
  const buttons = await page.$$eval('button', els => els.map(el => ({
    type: el.type,
    text: el.textContent?.trim(),
    className: el.className
  })));
  console.log(JSON.stringify(buttons, null, 2));
  
  console.log('\n\n=== SAP LOGIN ===\n');
  await page.goto(process.env.SAP_BASE_URL, { waitUntil: 'networkidle' });
  
  console.log('\n=== SAP Page Title ===');
  console.log(await page.title());
  
  console.log('\n=== SAP Input Fields ===');
  const sapInputs = await page.$$eval('input', els => els.map(el => ({
    type: el.type,
    name: el.name,
    id: el.id,
    placeholder: el.placeholder,
    className: el.className
  })));
  console.log(JSON.stringify(sapInputs, null, 2));
  
  console.log('\n=== SAP Buttons ===');
  const sapButtons = await page.$$eval('button', els => els.map(el => ({
    type: el.type,
    text: el.textContent?.trim(),
    className: el.className
  })));
  console.log(JSON.stringify(sapButtons, null, 2));
  
  await page.screenshot({ path: 'test-results/sap-login-page.png', fullPage: true });
  console.log('\n✓ SAP Screenshot saved to test-results/sap-login-page.png');
  
  await browser.close();
})();
