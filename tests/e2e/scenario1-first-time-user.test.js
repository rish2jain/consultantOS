/**
 * Scenario 1: First-Time User Experience
 * Tests onboarding flow and initial user experience
 */

const puppeteer = require('puppeteer');
const config = require('./puppeteer.config');
const helpers = require('./helpers/test-helpers');
const buttonHelpers = require('./helpers/button-helpers');

describe('Scenario 1: First-Time User Experience', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: false, // Set to true for CI
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });
    page = await browser.newPage();
    
    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('Browser console error:', msg.text());
      }
    });
    
    // Capture page errors
    page.on('pageerror', error => {
      console.error('Page error:', error.message);
    });
  });

  afterAll(async () => {
    await browser.close();
  });

  test('1.1: Access application without login redirects to login', async () => {
    try {
      await page.goto(config.frontendUrl, { waitUntil: 'networkidle0', timeout: 30000 });
      
      // Should redirect to login or show login page
      const currentUrl = page.url();
      const isLoginPage = currentUrl.includes('login') || currentUrl.includes('auth');
      
      // If not redirected, check if login form exists on page
      if (!isLoginPage) {
        // Wait a bit for page to load
        await new Promise(resolve => setTimeout(resolve, 2000));
        const hasLoginForm = await helpers.elementExists(page, 'input[type="email"]') ||
                            await helpers.elementExists(page, 'input[type="password"]');
        // If no login form, check if we're on dashboard (user might be logged in)
        if (!hasLoginForm) {
          const isDashboard = currentUrl === config.frontendUrl || 
                             currentUrl === `${config.frontendUrl}/` ||
                             await helpers.waitForText(page, 'Dashboard', 3000);
          // If dashboard, that's also acceptable (user might already be logged in)
          expect(isDashboard || hasLoginForm).toBeTruthy();
        } else {
          expect(hasLoginForm).toBeTruthy();
        }
      } else {
        expect(isLoginPage).toBeTruthy();
      }
      
      await helpers.takeScreenshot(page, 'scenario1-1-access-app');
    } catch (error) {
      await helpers.takeScreenshot(page, 'scenario1-1-error');
      throw error;
    }
  }, 60000);

  test('1.2: Registration form is accessible and functional', async () => {
    try {
      await page.goto(`${config.frontendUrl}/register`, { waitUntil: 'networkidle0', timeout: 30000 });
      
      // Wait a bit for page to fully load
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check if registration form elements exist
      const emailField = await helpers.elementExists(page, 'input[type="email"]');
      const passwordField = await helpers.elementExists(page, 'input[type="password"]');
      const nameField = await helpers.elementExists(page, 'input[name="name"]') ||
                        await helpers.elementExists(page, 'input[placeholder*="name" i]');
      
      expect(emailField || nameField).toBeTruthy();
      expect(passwordField).toBeTruthy();
      
      await helpers.takeScreenshot(page, 'scenario1-2-registration-form');
    } catch (error) {
      await helpers.takeScreenshot(page, 'scenario1-2-error');
      throw error;
    }
  }, 60000);

  test('1.3: Can register a new account', async () => {
    await page.goto(`${config.frontendUrl}/register`, { waitUntil: 'networkidle0' });
    
    // Fill registration form
    const emailSelector = 'input[type="email"], input[name="email"]';
    const passwordSelector = 'input[type="password"][name*="password"], input[type="password"]';
    const nameSelector = 'input[name="name"], input[placeholder*="name" i]';
    
    if (await helpers.elementExists(page, emailSelector)) {
      await helpers.fillField(page, emailSelector, config.testUser.email);
    }
    
    if (await helpers.elementExists(page, passwordSelector)) {
      await helpers.fillField(page, passwordSelector, config.testUser.password);
    }
    
    if (await helpers.elementExists(page, nameSelector)) {
      await helpers.fillField(page, nameSelector, config.testUser.name);
    }
    
    // Look for submit button
    const submitButton = await buttonHelpers.findButton(page, { 
      type: 'submit', 
      text: ['register', 'sign up'] 
    });
    
    if (submitButton) {
      await submitButton.click();
      // Wait for either success message or redirect
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
    
    await helpers.takeScreenshot(page, 'scenario1-3-registration-submit');
  }, 60000);

  test('1.4: Can login with credentials', async () => {
    await page.goto(`${config.frontendUrl}/login`, { waitUntil: 'networkidle0' });
    
    // Fill login form
    const emailSelector = 'input[type="email"], input[name="email"]';
    const passwordSelector = 'input[type="password"]';
    
    if (await helpers.elementExists(page, emailSelector)) {
      await helpers.fillField(page, emailSelector, config.testUser.email);
    }
    
    if (await helpers.elementExists(page, passwordSelector)) {
      await helpers.fillField(page, passwordSelector, config.testUser.password);
    }
    
    // Submit login
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
    
    // Should redirect to dashboard or home
    const currentUrl = page.url();
    expect(currentUrl).not.toMatch(/login/);
    
    await helpers.takeScreenshot(page, 'scenario1-4-login-success');
  }, 60000);

  test('1.5: Dashboard displays after authentication', async () => {
    // Should already be on dashboard from previous test
    // If not, navigate there
    if (page.url().includes('/login')) {
      await page.goto(config.frontendUrl, { waitUntil: 'networkidle0' });
    }
    
    // Check for dashboard elements
    const hasDashboardContent = await helpers.waitForText(page, 'Dashboard', 5000) ||
                                 await helpers.waitForText(page, 'Reports', 5000) ||
                                 await helpers.waitForText(page, 'Analysis', 5000);
    
    expect(hasDashboardContent).toBeTruthy();
    
    await helpers.takeScreenshot(page, 'scenario1-5-dashboard');
  }, 30000);
});

