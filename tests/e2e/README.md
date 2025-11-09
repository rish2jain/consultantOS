# E2E Test Suite for ConsultantOS

This directory contains end-to-end tests using Puppeteer, based on the scenarios defined in `USER_TESTING_GUIDE.md`.

## Prerequisites

1. **Backend must be running** on `http://localhost:8080`
   ```bash
   python main.py
   # or
   uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080
   ```

2. **Frontend must be running** on `http://localhost:3000`
   ```bash
   cd frontend && npm run dev
   ```

3. **Dependencies installed**
   ```bash
   npm install
   cd frontend && npm install
   ```

## Running Tests

### Option 1: Using the test runner script
```bash
./tests/e2e/run-tests.sh
```

### Option 2: Using npm script
```bash
npm run test:e2e
```

### Option 3: Using Jest directly
```bash
jest --config jest.e2e.config.js --testPathPattern=tests/e2e
```

## Test Scenarios

The test suite covers the following scenarios from `USER_TESTING_GUIDE.md`:

- **Scenario 1**: First-Time User Experience
- **Scenario 2**: Basic Analysis Generation
- **Scenario 9**: Frontend Dashboard Testing
- **Scenario 10**: API Integration Testing

## Test Structure

```
tests/e2e/
├── puppeteer.config.js          # Test configuration
├── helpers/
│   └── test-helpers.js          # Helper functions
├── scenario1-first-time-user.test.js
├── scenario2-basic-analysis.test.js
├── scenario9-frontend-dashboard.test.js
├── scenario10-api-integration.test.js
├── screenshots/                 # Screenshots (created during tests)
└── run-tests.sh                 # Test runner script
```

## Configuration

Edit `puppeteer.config.js` to customize:
- Frontend/Backend URLs
- Test user credentials
- Timeouts
- Test data

## Screenshots

Screenshots are automatically captured during test execution and saved to `tests/e2e/screenshots/`. Each screenshot is named with the test scenario and timestamp.

## Troubleshooting

### Tests fail with "Navigation timeout"
- Ensure both backend and frontend are running
- Check network connectivity
- Increase timeout values in `puppeteer.config.js`

### Tests fail with "Element not found"
- The frontend UI may have changed
- Check selectors in test files match current UI
- Use browser DevTools to verify element selectors

### Browser doesn't launch
- Ensure Chrome/Chromium is installed
- Puppeteer will download Chromium automatically on first run
- Check system permissions for browser execution

## Adding New Tests

1. Create a new test file: `scenarioX-description.test.js`
2. Follow the existing test structure
3. Use helper functions from `helpers/test-helpers.js`
4. Add test to `jest.e2e.config.js` if needed

## Notes

- Tests run in non-headless mode by default (visible browser)
- Set `headless: true` in test files for CI/CD
- Tests create a new user account for each run (with timestamp)
- Screenshots help debug test failures

