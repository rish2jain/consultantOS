/**
 * Puppeteer E2E Test Configuration
 * Based on USER_TESTING_GUIDE.md scenarios
 */

module.exports = {
  // Test URLs
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:3000',
  backendUrl: process.env.BACKEND_URL || 'http://localhost:8080',
  
  // Test credentials (will be created during tests)
  testUser: {
    email: `test-${Date.now()}@consultantos.test`,
    password: 'TestPassword123!',
    name: 'Test User'
  },
  
  // Timeouts
  navigationTimeout: 30000,
  actionTimeout: 10000,
  apiTimeout: 30000,
  
  // Screenshot settings
  screenshotDir: './tests/e2e/screenshots',
  
  // Test data
  testCompanies: [
    { company: 'Tesla', industry: 'Electric Vehicles' },
    { company: 'Netflix', industry: 'Streaming Media' },
    { company: 'Apple', industry: 'Technology' }
  ]
};

