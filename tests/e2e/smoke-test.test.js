/**
 * Smoke Test - Basic connectivity and setup verification
 * Run this first to ensure services are accessible
 */

const puppeteer = require('puppeteer');
const config = require('./puppeteer.config');
const http = require('http');

// Helper to check if URL is accessible
function checkUrl(url) {
  return new Promise((resolve) => {
    try {
      const urlObj = new URL(url);
      const isHttps = urlObj.protocol === 'https:';
      const port = urlObj.port || (isHttps ? 443 : 80);
      
      // Use http module for http, https module for https
      const httpModule = isHttps ? require('https') : http;
      
      const options = {
        hostname: urlObj.hostname,
        port: port,
        path: urlObj.pathname,
        method: 'GET',
        timeout: 5000
      };

      const req = httpModule.request(options, (res) => {
        resolve(res.statusCode < 500);
      });

      req.on('error', () => resolve(false));
      req.on('timeout', () => {
        req.destroy();
        resolve(false);
      });

      req.setTimeout(5000);
      req.end();
    } catch (error) {
      resolve(false);
    }
  });
}

describe('Smoke Test - Service Connectivity', () => {
  test('Backend health check is accessible', async () => {
    const isAccessible = await checkUrl(`${config.backendUrl}/health`);
    expect(isAccessible).toBeTruthy();
  }, 10000);

  test('Frontend is accessible', async () => {
    const isAccessible = await checkUrl(config.frontendUrl);
    expect(isAccessible).toBeTruthy();
  }, 10000);

  test('Can launch browser and navigate to frontend', async () => {
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
      const page = await browser.newPage();
      await page.goto(config.frontendUrl, { 
        waitUntil: 'domcontentloaded',
        timeout: 30000 
      });
      
      const title = await page.title();
      expect(title).toBeTruthy();
      
      await browser.close();
    } catch (error) {
      await browser.close();
      throw error;
    }
  }, 60000);
});

