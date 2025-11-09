/**
 * Jest configuration for E2E tests
 */

module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/e2e/**/*.test.js'],
  testTimeout: 120000, // 2 minutes per test
  maxWorkers: 1, // Run tests sequentially to avoid port conflicts
  verbose: true,
  collectCoverage: false,
  setupFilesAfterEnv: [],
  globalSetup: undefined,
  globalTeardown: undefined,
};

