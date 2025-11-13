# Playwright POC Setup Guide

Quick setup instructions for the Playwright video recording proof-of-concept.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

This will install Playwright (added to `package.json`).

### 2. Install Playwright Browsers

```bash
npx playwright install chromium
```

This is a one-time setup that downloads the Chromium browser.

### 3. Ensure Services Are Running

**Backend** (port 8080):
```bash
python main.py
# or
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080
```

**Frontend** (port 3000):
```bash
cd frontend && npm run dev
```

### 4. Run the POC Test

```bash
npm run test:playwright
```

Or directly with Jest:
```bash
jest --config jest.e2e.config.js tests/e2e/scenario1-playwright-poc.test.js
```

## What to Expect

1. **Browser opens** (headless: false by default)
2. **Tests execute** - you'll see the browser performing actions
3. **Videos are saved** automatically to `tests/e2e/videos/`
4. **Each test** gets its own video file (no audio)

## Video Output Location

```
tests/e2e/videos/
├── test-1-1-access-app-[timestamp].webm
├── test-1-2-registration-form-[timestamp].webm
├── test-1-3-registration-submit-[timestamp].webm
└── ...
```

## Verify It Works

After running the test:

1. Check that `tests/e2e/videos/` directory exists
2. Open one of the `.webm` video files
3. Verify:
   - ✅ Video plays correctly
   - ✅ No audio track (silent video)
   - ✅ Shows the test execution
   - ✅ 1920x1080 resolution

## Troubleshooting

### "playwright: command not found"
```bash
npm install playwright
npx playwright install chromium
```

### "Browser not found"
```bash
npx playwright install chromium
```

### Videos not saving
- Check that `tests/e2e/videos/` directory exists (created automatically)
- Verify write permissions
- Ensure `context.close()` is called (it is in the POC)

### Tests fail with connection errors
- Ensure backend is running on port 8080
- Ensure frontend is running on port 3000
- Check URLs in `playwright.config.js`

## Next Steps

1. ✅ Run the POC test
2. ✅ Review the video output
3. ✅ Compare with Puppeteer approach
4. ✅ Decide if you want to migrate

See `PLAYWRIGHT_POC_README.md` for more details.

