/**
 * Helper functions for Playwright E2E tests
 * Similar to Puppeteer helpers but using Playwright API
 */

const fs = require('fs').promises;
const path = require('path');

/**
 * Wait for element to be visible
 */
async function waitForElement(page, selector, timeout = 10000) {
  try {
    await page.waitForSelector(selector, { state: 'visible', timeout });
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
      text,
      { timeout }
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
  await page.fill(selector, value);
}

/**
 * Click element and wait for navigation
 */
async function clickAndWait(page, selector, waitForUrl = null) {
  await page.waitForSelector(selector);
  
  if (waitForUrl) {
    await Promise.all([
      page.waitForURL(waitForUrl, { timeout: 10000 }),
      page.click(selector)
    ]);
  } else {
    await page.click(selector);
    await page.waitForLoadState('networkidle');
  }
}

/**
 * Get element text content
 */
async function getText(page, selector) {
  await page.waitForSelector(selector);
  return await page.textContent(selector);
}

/**
 * Check if element exists
 */
async function elementExists(page, selector) {
  try {
    await page.waitForSelector(selector, { timeout: 2000, state: 'attached' });
    return true;
  } catch {
    return false;
  }
}

/**
 * Wait for API response
 */
async function waitForAPIResponse(page, urlPattern, timeout = 30000) {
  const response = await page.waitForResponse(
    response => response.url().includes(urlPattern),
    { timeout }
  );
  return response;
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
 * Wait for network to be idle
 */
async function waitForNetworkIdle(page, timeout = 5000) {
  try {
    await page.waitForLoadState('networkidle', { timeout });
  } catch (e) {
    // Fallback: just wait a bit
    await page.waitForTimeout(1000);
  }
}

/**
 * Find button by text or attributes (similar to button-helpers)
 */
async function findButton(page, options = {}) {
  const { text, type, ariaLabel } = options;
  
  let selector = 'button';
  
  if (type === 'submit') {
    selector = 'button[type="submit"]';
  }
  
  if (text) {
    const textArray = Array.isArray(text) ? text : [text];
    for (const t of textArray) {
      const button = await page.locator(selector).filter({ hasText: new RegExp(t, 'i') }).first();
      if (await button.count() > 0) {
        return button;
      }
    }
  }
  
  if (ariaLabel) {
    const button = page.locator(`button[aria-label*="${ariaLabel}" i]`);
    if (await button.count() > 0) {
      return button;
    }
  }
  
  // Fallback: return first button
  const button = page.locator(selector).first();
  if (await button.count() > 0) {
    return button;
  }
  
  return null;
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
  setupConsoleErrorTracking,
  removeConsoleErrorTracking,
  getConsoleErrorsDuring,
  waitForNetworkIdle,
  findButton
};

