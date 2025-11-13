/**
 * Playwright E2E Test Configuration
 * Based on USER_TESTING_GUIDE.md scenarios
 * 
 * This configuration enables video recording without audio for all tests
 */

module.exports = {
  // Test URLs
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000',
  backendUrl: process.env.BACKEND_URL || 'http://localhost:8080',
  
  // Test credentials (will be created during tests)
  testUser: {
    email: `test-${Date.now()}@consultantos.test`,
    password: process.env.TEST_USER_PASSWORD || 'TestPassword123!',
    name: 'Test User'
  },
  
  // Timeouts
  navigationTimeout: 30000,
  actionTimeout: 10000,
  apiTimeout: 30000,
  
  // Video recording settings
  video: {
    dir: './tests/e2e/videos',
    mode: 'on', // Record video for all tests
    size: { width: 1920, height: 1080 }
    // No audio by default - video only
  },
  
  // Screenshot settings (can be used alongside video)
  screenshotDir: './tests/e2e/screenshots',
  
  // Test data
  testCompanies: [
    { company: 'Tesla', industry: 'Electric Vehicles' },
    { company: 'Netflix', industry: 'Streaming Media' },
    { company: 'Apple', industry: 'Technology' }
  ],
  
  // Browser settings
  browserOptions: {
    headless: false, // Set to true for CI
    viewport: { width: 1920, height: 1080 }
  }
};

