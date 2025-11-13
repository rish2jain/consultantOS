/**
 * Quick script to capture fresh screenshots of key views
 * Run with: node tests/e2e/capture_fresh_screenshots.js
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs').promises;

const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
const screenshotsDir = path.join(__dirname, 'screenshots');

async function captureScreenshots() {
  const browser = await chromium.launch({ headless: true });
  
  // Ensure screenshots directory exists
  await fs.mkdir(screenshotsDir, { recursive: true });

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  // Split views into public and protected
  const publicViews = [
    { name: 'access-app', url: '/', waitFor: 'body' },
    { name: 'login', url: '/login', waitFor: 'input[type="email"], input[name="email"]' },
    { name: 'registration-form', url: '/register', waitFor: 'input[type="email"], input[name="email"]' },
  ];
  
  const protectedViews = [
    { name: 'dashboard', url: '/dashboard', waitFor: 'body' },
    { name: 'analysis-page', url: '/analysis', waitFor: 'body' },
    { name: 'report-view', url: '/reports', waitFor: 'body' },
    { name: 'report-detail', url: '/reports/1', waitFor: 'body' }, // Example report ID
  ];

  console.log('📸 Capturing fresh screenshots...\n');

  // Create context for public views (no authentication)
  const publicContext = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const publicPage = await publicContext.newPage();

  // Capture public views
  for (const view of publicViews) {
    try {
      console.log(`  Capturing: ${view.name}...`);
      await publicPage.goto(`${frontendUrl}${view.url}`, { 
        waitUntil: 'domcontentloaded',
        timeout: 15000 
      });
      
      // Wait for loading screens to disappear
      try {
        // Wait for loading indicators to disappear
        await publicPage.waitForSelector('.loading, [data-loading], .spinner', { 
          state: 'hidden', 
          timeout: 5000 
        }).catch(() => {}); // Ignore if no loading indicator
      } catch (e) {}
      
      // Wait for specific element if specified
      if (view.waitFor) {
        await publicPage.waitForSelector(view.waitFor, { timeout: 10000 }).catch(() => {});
      }
      
      // Wait for any animations/transitions to complete
      await publicPage.waitForTimeout(2000);
      
      // Check if we're still on a loading screen
      let retries = 0;
      while (retries < 5) {
        const isLoading = await publicPage.$('.loading, [data-loading], .spinner, [class*="loading"], [class*="spinner"]');
        if (!isLoading) {
          break;
        }
        console.log(`    ⏳ Waiting for loading to complete (attempt ${retries + 1}/5)...`);
        await publicPage.waitForSelector('.loading, [data-loading], .spinner, [class*="loading"], [class*="spinner"]', { 
          state: 'hidden', 
          timeout: 5000 
        }).catch(() => {});
        await publicPage.waitForTimeout(1500);
        retries++;
      }
      
      // Additional wait to ensure content is fully rendered
      await publicPage.waitForTimeout(1000);
      
      // Check if we're on a login/auth screen (avoid duplicates)
      const currentUrl = publicPage.url();
      const pageContent = await publicPage.textContent('body').catch(() => '');
      if (currentUrl.includes('/login') && view.name !== 'login') {
        console.log(`    ⚠️  Redirected to login, skipping duplicate...`);
        continue;
      }
      
      const screenshotPath = path.join(
        screenshotsDir,
        `fresh-${view.name}-${timestamp}.png`
      );
      
      await publicPage.screenshot({ 
        path: screenshotPath, 
        fullPage: true 
      });
      
      console.log(`    ✅ Saved: ${path.basename(screenshotPath)}`);
    } catch (error) {
      console.log(`    ⚠️  Failed: ${view.name} - ${error.message}`);
    }
  }

  await publicContext.close();

  // Authenticate for protected views
  console.log('\n🔐 Authenticating for protected routes...');
  const authContext = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const authPage = await authContext.newPage();

  try {
    // Perform login (adjust selectors and credentials as needed)
    await authPage.goto(`${frontendUrl}/login`, { waitUntil: 'networkidle' });
    
    // Try to find and fill login form (adjust selectors based on your app)
    const emailInput = await authPage.$('input[type="email"], input[name="email"], input[id="email"]');
    const passwordInput = await authPage.$('input[type="password"], input[name="password"], input[id="password"]');
    const submitButton = await authPage.$('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
    
    if (emailInput && passwordInput && submitButton) {
      // Use test credentials from environment or defaults
      const testEmail = process.env.TEST_EMAIL || 'test@example.com';
      const testPassword = process.env.TEST_PASSWORD || 'testpassword';
      
      await emailInput.fill(testEmail);
      await passwordInput.fill(testPassword);
      await submitButton.click();
      
      // Wait for navigation after login
      await authPage.waitForNavigation({ waitUntil: 'networkidle', timeout: 10000 });
      console.log('    ✅ Authentication successful');
    } else {
      console.log('    ⚠️  Login form not found, attempting to use existing session');
    }
    
    // Save authentication state
    await authContext.storageState({ path: path.join(__dirname, 'auth-state.json') });
  } catch (error) {
    console.log(`    ⚠️  Authentication failed: ${error.message}`);
    console.log('    Continuing with unauthenticated context...');
  }

  // Capture protected views with authenticated context
  for (const view of protectedViews) {
    try {
      console.log(`  Capturing: ${view.name}...`);
      await authPage.goto(`${frontendUrl}${view.url}`, { 
        waitUntil: 'domcontentloaded',
        timeout: 15000 
      });
      
      // Wait for loading screens to disappear
      try {
        await authPage.waitForSelector('.loading, [data-loading], .spinner', { 
          state: 'hidden', 
          timeout: 5000 
        }).catch(() => {});
      } catch (e) {}
      
      // Wait for specific element if specified
      if (view.waitFor) {
        await authPage.waitForSelector(view.waitFor, { timeout: 10000 }).catch(() => {});
      }
      
      // Wait for any animations/transitions
      await authPage.waitForTimeout(2000);
      
      // Check if we're still on a loading screen
      let retries = 0;
      while (retries < 5) {
        const isLoading = await authPage.$('.loading, [data-loading], .spinner, [class*="loading"], [class*="spinner"]');
        if (!isLoading) {
          break;
        }
        console.log(`    ⏳ Waiting for loading to complete (attempt ${retries + 1}/5)...`);
        await authPage.waitForSelector('.loading, [data-loading], .spinner, [class*="loading"], [class*="spinner"]', { 
          state: 'hidden', 
          timeout: 5000 
        }).catch(() => {});
        await authPage.waitForTimeout(1500);
        retries++;
      }
      
      // Additional wait to ensure content is fully rendered
      await authPage.waitForTimeout(1000);
      
      // Check if redirected to login (not authenticated) - avoid duplicates
      const currentUrl = authPage.url();
      if (currentUrl.includes('/login') && view.name !== 'login') {
        console.log(`    ⚠️  Redirected to login (not authenticated), skipping duplicate...`);
        continue;
      }
      
      // Check if we already captured this view (avoid duplicates)
      const pageContent = await authPage.textContent('body').catch(() => '');
      if (view.name === 'login' && currentUrl.includes('/login')) {
        // Only capture login once
        const existingLogin = await fs.access(
          path.join(screenshotsDir, `fresh-login-${timestamp}.png`)
        ).then(() => true).catch(() => false);
        if (existingLogin) {
          console.log(`    ⚠️  Login already captured, skipping duplicate...`);
          continue;
        }
      }
      
      const screenshotPath = path.join(
        screenshotsDir,
        `fresh-${view.name}-${timestamp}.png`
      );
      
      await authPage.screenshot({ 
        path: screenshotPath, 
        fullPage: true 
      });
      
      console.log(`    ✅ Saved: ${path.basename(screenshotPath)}`);
    } catch (error) {
      console.log(`    ⚠️  Failed: ${view.name} - ${error.message}`);
    }
  }

  await authContext.close();
  await browser.close();
  console.log('\n✅ Screenshot capture complete!');
}

captureScreenshots().catch(console.error);

