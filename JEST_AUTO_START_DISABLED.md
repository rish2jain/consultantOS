# Jest Auto-Start Disabled

## Changes Made

I've configured the repository to prevent Jest from starting automatically. Here's what was changed:

### 1. Jest Configuration (`jest.e2e.config.js`)
- Added explicit `watch: false` to disable watch mode
- Added `watchAll: false` to prevent watching all files
- Added `watchman: false` to disable watchman integration

### 2. Package.json Scripts
- Updated all test scripts to include `--watch=false` flag:
  - `npm test` - now runs without watch mode
  - `npm run test:e2e` - now runs without watch mode
  - `npm run test:smoke` - now runs without watch mode

### 3. Frontend Package.json
- Updated `test:e2e` script to include `--watch=false`

### 4. VS Code Settings (`.vscode/settings.json`)
- Set `jest.autoRun` to `"off"` - disables Jest extension auto-run
- Set `jest.runMode` to `"on-demand"` - tests only run when you explicitly trigger them
- Set `jest.jestCommandLine` to use `--watch=false`
- Disabled auto-running tests on save

### 5. VS Code Extensions (`.vscode/extensions.json`)
- Marked Jest-related extensions as "unwanted" to prevent auto-installation

## Verification

To verify Jest won't auto-start:

1. **Check Jest config**:
   ```bash
   cat jest.e2e.config.js | grep watch
   ```
   Should show: `watch: false, watchAll: false, watchman: false`

2. **Check npm scripts**:
   ```bash
   cat package.json | grep test
   ```
   All test scripts should include `--watch=false`

3. **Check VS Code settings**:
   ```bash
   cat .vscode/settings.json | grep jest
   ```
   Should show Jest auto-run is disabled

## Running Tests Manually

Tests will now only run when you explicitly invoke them:

```bash
# Run tests once (no watch mode)
npm test

# Run E2E tests once
npm run test:e2e

# Run smoke tests once
npm run test:smoke
```

## If Jest Still Auto-Starts

If Jest still starts automatically after these changes:

1. **Restart VS Code** - Settings changes require a restart
2. **Disable Jest extension** - Go to Extensions and disable "Jest" or "Jest Runner"
3. **Check for other test runners** - Some editors have built-in test runners
4. **Check git hooks** - Run `ls -la .git/hooks` to see if any hooks trigger tests
5. **Check CI/CD** - Verify your CI/CD pipeline isn't auto-running tests

## Re-enabling Watch Mode (if needed)

If you want to enable watch mode for a specific test run:

```bash
# Run with watch mode explicitly
npm test -- --watch

# Or temporarily
jest --config jest.e2e.config.js --watch
```

