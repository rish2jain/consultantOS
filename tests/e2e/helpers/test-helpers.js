/**
 * Helper functions for Puppeteer E2E tests
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Wait for element to be visible
 */
async function waitForElement(page, selector, timeout = 10000) {
  try {
    await page.waitForSelector(selector, { visible: true, timeout });
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Wait for text to appear on page
 */
async function waitForText(page, text, timeout = 10000) {
  try {
    await page.waitForFunction(
      (text) => document.body.innerText.includes(text),
      { timeout },
      text
    );
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Take screenshot with timestamp
 */
async function takeScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const screenshotPath = path.join(
    __dirname,
    '../screenshots',
    `${name}-${timestamp}.png`
  );
  
  // Ensure directory exists
  await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
  
  await page.screenshot({ path: screenshotPath, fullPage: true });
  return screenshotPath;
}

/**
 * Fill form field
 */
async function fillField(page, selector, value) {
  await page.waitForSelector(selector);
  await page.click(selector);
  await page.evaluate((sel) => {
    document.querySelector(sel).value = '';
  }, selector);
  await page.type(selector, value);
}

/**
 * Click element and wait for navigation
 */
async function clickAndWait(page, selector, waitForUrl = null) {
  await page.waitForSelector(selector);
  const navigationPromise = page.waitForNavigation({ waitUntil: 'networkidle0' });
  await page.click(selector);
  await navigationPromise;
  
  if (waitForUrl) {
    await page.waitForFunction(
      (url) => window.location.href.includes(url),
      { timeout: 10000 },
      waitForUrl
    );
  }
}

/**
 * Get element text content
 */
async function getText(page, selector) {
  await page.waitForSelector(selector);
  return await page.$eval(selector, el => el.textContent.trim());
}

/**
 * Check if element exists
 */
async function elementExists(page, selector) {
  try {
    await page.waitForSelector(selector, { timeout: 2000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Wait for API response
 */
async function waitForAPIResponse(page, urlPattern, timeout = 30000) {
  // Use page.waitForResponse for better reliability and automatic cleanup
  return await page.waitForResponse(
    response => response.url().includes(urlPattern),
    { timeout }
  );
}

/**
 * Setup console error tracking and return a getter function
 * Usage:
 *   const getErrorsFn = setupConsoleErrorTracking(page);
 *   // ... perform actions ...
 *   const errors = getErrorsFn();
 *   // ... later, cleanup ...
 *   removeConsoleErrorTracking(page, getErrorsFn);
 */
function setupConsoleErrorTracking(page) {
  const errors = [];
  
  const handler = msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  };
  
  page.on('console', handler);
  
  // Return getter function and handler for cleanup
  const getErrors = () => [...errors];
  getErrors._handler = handler;
  
  return getErrors;
}

/**
 * Remove console error tracking handler
 */
function removeConsoleErrorTracking(page, getErrorsFn) {
  if (getErrorsFn && getErrorsFn._handler) {
    page.off('console', getErrorsFn._handler);
  }
}

/**
 * Get console errors during a test function execution (scoped helper)
 * Usage:
 *   const errors = await getConsoleErrorsDuring(page, async () => {
 *     await page.click('button');
 *     await page.waitForNavigation();
 *   });
 */
async function getConsoleErrorsDuring(page, testFn) {
  const errors = [];
  
  const handler = msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  };
  
  page.on('console', handler);
  
  try {
    await testFn();
  } finally {
    page.off('console', handler);
  }
  
  return errors;
}

/**
 * Get console errors (deprecated - use setupConsoleErrorTracking or getConsoleErrorsDuring)
 * @deprecated This function returns an empty array because listeners are registered asynchronously.
 * Use setupConsoleErrorTracking() or getConsoleErrorsDuring() instead.
 */
async function getConsoleErrors(page) {
  // Deprecated: Use setupConsoleErrorTracking or getConsoleErrorsDuring instead
  console.warn('getConsoleErrors is deprecated. Use setupConsoleErrorTracking or getConsoleErrorsDuring instead.');
  return [];
}

/**
 * Wait for network to be idle
 */
async function waitForNetworkIdle(page, timeout = 5000) {
  // Puppeteer doesn't have waitForLoadState, so we use waitForNavigation
  // or just wait a bit for network activity to settle
  try {
    await page.waitForNavigation({ waitUntil: 'networkidle0', timeout });
  } catch (e) {
    // Fallback: just wait a bit
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

module.exports = {
  waitForElement,
  waitForText,
  takeScreenshot,
  fillField,
  clickAndWait,
  getText,
  elementExists,
  waitForAPIResponse,
  getConsoleErrors,
  setupConsoleErrorTracking,
  removeConsoleErrorTracking,
  getConsoleErrorsDuring,
  waitForNetworkIdle
};

