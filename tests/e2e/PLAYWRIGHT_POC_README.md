# Playwright Video Recording POC

This directory contains a proof-of-concept demonstrating **Playwright with native video recording (no audio)** for automated testing.

## What's Different from Puppeteer?

### Puppeteer (Current)
- Takes screenshots at key moments
- Combines screenshots into video using FFmpeg
- Manual video creation step

### Playwright (POC)
- **Native video recording** - automatically records during test execution
- **No audio by default** - video-only recording
- **Automatic saving** - videos saved when test context closes
- **Better test reliability** - more stable than Puppeteer
- **One video per test** - easier to debug specific test failures

## Files

- `scenario1-playwright-poc.test.js` - Proof-of-concept test file
- `playwright.config.js` - Playwright-specific configuration
- `helpers/playwright-helpers.js` - Helper functions for Playwright (similar to Puppeteer helpers)

## Prerequisites

1. **Install Playwright**:
   ```bash
   npm install playwright
   ```

2. **Install Playwright browsers** (one-time setup):
   ```bash
   npx playwright install chromium
   ```

3. **Backend must be running** on `http://localhost:8080`
   ```bash
   python main.py
   # or
   uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080
   ```

4. **Frontend must be running** on `http://localhost:3000`
   ```bash
   cd frontend && npm run dev
   ```

## Running the POC

### Option 1: Run with Jest (recommended)
```bash
jest --config jest.e2e.config.js tests/e2e/scenario1-playwright-poc.test.js
```

### Option 2: Run with Playwright Test Runner
```bash
npx playwright test tests/e2e/scenario1-playwright-poc.test.js
```

### Option 3: Add npm script
Add to `package.json`:
```json
{
  "scripts": {
    "test:playwright": "jest --config jest.e2e.config.js tests/e2e/scenario1-playwright-poc.test.js"
  }
}
```

Then run:
```bash
npm run test:playwright
```

## Video Output

Videos are automatically saved to:
```
tests/e2e/videos/
```

Each test gets its own video file. The video:
- ✅ **Contains no audio** (video-only)
- ✅ **Records the entire test execution**
- ✅ **Saves automatically** when test context closes
- ✅ **1920x1080 resolution**

### Example Video Files
```
tests/e2e/videos/
├── test-1-1-access-app-2024-01-01T12-00-00.webm
├── test-1-2-registration-form-2024-01-01T12-00-15.webm
├── test-1-3-registration-submit-2024-01-01T12-00-30.webm
└── ...
```

## Key Features

### 1. Automatic Video Recording
```javascript
context = await browser.newContext({
  recordVideo: {
    dir: './tests/e2e/videos',
    size: { width: 1920, height: 1080 }
    // No audio by default
  }
});
```

### 2. Video Saved on Context Close
```javascript
afterAll(async () => {
  await context.close(); // Video saved here automatically
  await browser.close();
});
```

### 3. One Video Per Test
Each test in the suite gets its own video file, making it easy to:
- Debug specific test failures
- Share videos with team
- Review test execution

## Comparison: Puppeteer vs Playwright

| Feature | Puppeteer | Playwright |
|---------|-----------|------------|
| Video Recording | Manual (screenshots + FFmpeg) | ✅ Native |
| Audio Control | Manual (FFmpeg flags) | ✅ No audio by default |
| Test Reliability | Good | ✅ Better |
| Maintenance | Slower updates | ✅ Active development |
| API Similarity | - | ✅ Very similar |
| Browser Support | Chromium only | ✅ Chromium, Firefox, WebKit |

## Migration Path

If you want to migrate from Puppeteer to Playwright:

1. **Install Playwright** (already done if you ran the POC)
2. **Update test files** - Replace Puppeteer imports with Playwright
3. **Update helper functions** - Use Playwright API (helpers already created)
4. **Enable video recording** - Add `recordVideo` to context options
5. **Update CI/CD** - Install Playwright browsers in CI

### Example Migration

**Before (Puppeteer)**:
```javascript
const puppeteer = require('puppeteer');
const browser = await puppeteer.launch();
const page = await browser.newPage();
```

**After (Playwright)**:
```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch();
const context = await browser.newContext({
  recordVideo: { dir: './videos' }
});
const page = await context.newPage();
```

## Configuration

Edit `playwright.config.js` to customize:
- Video directory
- Video resolution
- Browser options (headless mode)
- Timeouts
- Test URLs

## Troubleshooting

### Videos not saving
- Ensure `context.close()` is called in `afterAll`
- Check directory permissions for `tests/e2e/videos/`
- Verify Playwright is installed correctly

### Tests fail with "Browser not found"
```bash
npx playwright install chromium
```

### Video files are too large
- Reduce video resolution in `playwright.config.js`
- Use `recordVideo: { mode: 'on-first-retry' }` to only record on failures

### Want to record audio too?
Add to context options:
```javascript
recordVideo: {
  dir: './videos',
  size: { width: 1920, height: 1080 }
},
// Note: Playwright doesn't record audio by default
// For audio, you'd need external tools or different approach
```

## Next Steps

1. **Try the POC**: Run the test and check the video output
2. **Compare**: Run both Puppeteer and Playwright versions side-by-side
3. **Decide**: Choose based on your needs (Playwright recommended)
4. **Migrate**: If satisfied, migrate other test files to Playwright

## Additional Resources

- [Playwright Video Recording Docs](https://playwright.dev/docs/videos)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Migration Guide](https://playwright.dev/docs/migration)

---

**Last Updated**: 2025-11-12  
**Status**: Proof of Concept - Ready for evaluation

