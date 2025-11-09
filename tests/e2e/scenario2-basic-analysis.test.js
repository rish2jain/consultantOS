/**
 * Scenario 2: Basic Analysis Generation
 * Tests core functionality of generating a strategic analysis
 */

const puppeteer = require('puppeteer');
const config = require('./puppeteer.config');
const helpers = require('./helpers/test-helpers');
const buttonHelpers = require('./helpers/button-helpers');

describe('Scenario 2: Basic Analysis Generation', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: false,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  beforeEach(async () => {
    // Ensure we're logged in
    await page.goto(`${config.frontendUrl}/login`, { waitUntil: 'networkidle0' });
    
    const emailSelector = 'input[type="email"], input[name="email"]';
    const passwordSelector = 'input[type="password"]';
    
    if (await helpers.elementExists(page, emailSelector)) {
      await helpers.fillField(page, emailSelector, config.testUser.email);
    }
    
    if (await helpers.elementExists(page, passwordSelector)) {
      await helpers.fillField(page, passwordSelector, config.testUser.password);
    }
    
    const submitButton = await buttonHelpers.findButton(page, { 
      type: 'submit', 
      text: ['login', 'sign in'] 
    });
    if (submitButton) {
      await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 30000 }).catch(() => {}),
        submitButton.click()
      ]);
    }
  });

  test('2.1: Navigate to analysis creation page', async () => {
    // Navigate to analysis page
    await page.goto(`${config.frontendUrl}/analysis`, { waitUntil: 'networkidle0' });
    
    // Check for analysis form elements
    const hasForm = await helpers.waitForText(page, 'Company', 5000) ||
                    await helpers.elementExists(page, 'input[placeholder*="company" i]');
    
    expect(hasForm).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario2-1-analysis-page');
  }, 30000);

  test('2.2: Fill analysis form with Tesla data', async () => {
    await page.goto(`${config.frontendUrl}/analysis`, { waitUntil: 'networkidle0' });
    
    // Fill company name
    const companySelector = 'input[name="company"], input[placeholder*="company" i]';
    if (await helpers.elementExists(page, companySelector)) {
      await helpers.fillField(page, companySelector, 'Tesla');
    }
    
    // Fill industry
    const industrySelector = 'input[name="industry"], input[placeholder*="industry" i]';
    if (await helpers.elementExists(page, industrySelector)) {
      await helpers.fillField(page, industrySelector, 'Electric Vehicles');
    }
    
    // Select frameworks (Porter and SWOT)
    // Try checkbox selectors first
    const porterCheckbox = await page.$('input[type="checkbox"][value*="porter" i]');
    if (porterCheckbox) {
      await porterCheckbox.click();
    } else {
      // Try finding button by text using buttonHelpers
      const porterButton = await buttonHelpers.findButton(page, { text: 'Porter' });
      if (porterButton) {
        await porterButton.click();
      }
    }
    
    const swotCheckbox = await page.$('input[type="checkbox"][value*="swot" i]');
    if (swotCheckbox) {
      await swotCheckbox.click();
    } else {
      // Try finding button by text using buttonHelpers
      const swotButton = await buttonHelpers.findButton(page, { text: 'SWOT' });
      if (swotButton) {
        await swotButton.click();
      }
    }
    
    await helpers.takeScreenshot(page, 'scenario2-2-form-filled');
  }, 30000);

  test('2.3: Submit analysis request', async () => {
    await page.goto(`${config.frontendUrl}/analysis`, { waitUntil: 'networkidle0' });
    
    // Fill form (reuse from previous test)
    const companySelector = 'input[name="company"], input[placeholder*="company" i]';
    const industrySelector = 'input[name="industry"], input[placeholder*="industry" i]';
    
    if (await helpers.elementExists(page, companySelector)) {
      await helpers.fillField(page, companySelector, 'Tesla');
    }
    
    if (await helpers.elementExists(page, industrySelector)) {
      await helpers.fillField(page, industrySelector, 'Electric Vehicles');
    }
    
    // Select frameworks
    const porterCheckbox = await page.$('input[type="checkbox"][value*="porter" i]');
    if (porterCheckbox) {
      await porterCheckbox.click();
    }
    
    const swotCheckbox = await page.$('input[type="checkbox"][value*="swot" i]');
    if (swotCheckbox) {
      await swotCheckbox.click();
    }
    
    // Submit form
    const submitButton = await buttonHelpers.findButton(page, { 
      type: 'submit', 
      text: ['analyze', 'submit'] 
    });
    if (submitButton) {
      await submitButton.click();
      
      // Wait deterministically for expected condition: loading state, success, or error message
      const maxWaitTime = 10000; // 10 seconds total
      const pollInterval = 200; // Check every 200ms
      const startTime = Date.now();
      
      let conditionMet = false;
      while (Date.now() - startTime < maxWaitTime && !conditionMet) {
        // Single efficient DOM check for any of the target texts
        conditionMet = await page.evaluate(() => {
          const bodyText = document.body.innerText || '';
          const targetTexts = ['Loading', 'Processing', 'Generating', 'Success', 'Error'];
          return targetTexts.some(text => bodyText.includes(text));
        });
        
        if (!conditionMet) {
          await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
      }
      
      // Verify we got some response (loading, success, or error)
      expect(conditionMet).toBeTruthy();
    }
    
    await helpers.takeScreenshot(page, 'scenario2-3-submit-analysis');
  }, 120000); // Longer timeout for analysis completion
});

