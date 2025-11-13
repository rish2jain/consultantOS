/**
 * Scenario 9: Frontend Dashboard Testing
 * Comprehensive testing of the web interface
 */

const puppeteer = require('puppeteer');
const config = require('./puppeteer.config');
const helpers = require('./helpers/test-helpers');
const buttonHelpers = require('./helpers/button-helpers');

describe('Scenario 9: Frontend Dashboard Testing', () => {
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
    // Login before each test
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

  test('9A.1: Authentication & Registration Flow - Access Dashboard', async () => {
    await page.goto(config.frontendUrl, { waitUntil: 'networkidle0' });
    
    // Should be on dashboard or redirect to login
    const currentUrl = page.url();
    const isAuthenticated = !currentUrl.includes('/login') && !currentUrl.includes('/register');
    
    expect(isAuthenticated).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9A-1-dashboard-access');
  }, 30000);

  test('9B.1: Dashboard Home Page - Metrics Display', async () => {
    await page.goto(config.frontendUrl, { waitUntil: 'networkidle0' });
    
    // Check for metric cards or dashboard content
    const hasMetrics = await helpers.waitForText(page, 'Reports', 5000) ||
                       await helpers.waitForText(page, 'Total', 5000) ||
                       await helpers.elementExists(page, '[class*="metric"], [class*="card"]');
    
    expect(hasMetrics).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9B-1-metrics');
  }, 30000);

  test('9C.1: Analysis Creation Page - Tabbed Interface', async () => {
    await page.goto(`${config.frontendUrl}/analysis`, { waitUntil: 'networkidle0' });
    
    // Check for tabs or analysis form
    // Check for tabs using valid selectors
    const hasTabs = await helpers.elementExists(page, '[role="tab"]') ||
                    await page.evaluate(() => {
                      const buttons = Array.from(document.querySelectorAll('button'));
                      return buttons.some(btn => btn.textContent?.includes('Quick') || btn.textContent?.includes('Batch'));
                    });
    const hasForm = await helpers.elementExists(page, 'input[placeholder*="company" i], input[name="company"]');
    
    expect(hasTabs || hasForm).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9C-1-analysis-tabs');
  }, 30000);

  test('9D.1: Reports List Page - DataTable Functionality', async () => {
    await page.goto(`${config.frontendUrl}/reports`, { waitUntil: 'networkidle0' });
    
    // Check for reports table or list
    const hasTable = await helpers.elementExists(page, 'table, [class*="table"], [class*="list"]') ||
                     await helpers.waitForText(page, 'Reports', 5000);
    
    expect(hasTable).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9D-1-reports-list');
  }, 30000);

  test('9F.1: Jobs Queue Page - Job List Display', async () => {
    await page.goto(`${config.frontendUrl}/jobs`, { waitUntil: 'networkidle0' });
    
    // Check for jobs page content
    const hasJobs = await helpers.waitForText(page, 'Jobs', 5000) ||
                    await helpers.waitForText(page, 'Queue', 5000) ||
                    await helpers.elementExists(page, '[class*="job"], [class*="queue"]');
    
    expect(hasJobs).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9F-1-jobs-queue');
  }, 30000);

  test('9G.1: Templates Page - Template Library', async () => {
    await page.goto(`${config.frontendUrl}/templates`, { waitUntil: 'networkidle0' });
    
    // Check for templates page
    const hasTemplates = await helpers.waitForText(page, 'Template', 5000) ||
                         await helpers.elementExists(page, '[class*="template"]');
    
    expect(hasTemplates).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9G-1-templates');
  }, 30000);

  test('9H.1: Profile & Settings Page - Profile Information', async () => {
    await page.goto(`${config.frontendUrl}/profile`, { waitUntil: 'networkidle0' });
    
    // Check for profile page
    const hasProfile = await helpers.waitForText(page, 'Profile', 5000) ||
                       await helpers.waitForText(page, 'Settings', 5000) ||
                       await helpers.elementExists(page, 'input[name="email"], input[name="name"]');
    
    expect(hasProfile).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9H-1-profile');
  }, 30000);

  test('9K.1: Navigation & Responsive Design - Navigation Menu', async () => {
    await page.goto(config.frontendUrl, { waitUntil: 'networkidle0' });
    
    // Check for navigation elements
    const hasNav = await helpers.elementExists(page, 'nav, [class*="nav"], [role="navigation"]') ||
                   await helpers.elementExists(page, 'a[href*="/reports"], a[href*="/analysis"]');
    
    expect(hasNav).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario9K-1-navigation');
  }, 30000);
});

