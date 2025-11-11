# ConsultantOS User Testing Guide

Comprehensive testing guide for the ConsultantOS Continuous Competitive Intelligence Platform. This guide covers both manual testing procedures and automated test execution.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Test Scenarios](#test-scenarios)
- [Manual Testing Procedures](#manual-testing-procedures)
- [Automated Testing](#automated-testing)
- [API Testing](#api-testing)
- [Expected Results](#expected-results)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

This guide provides step-by-step instructions for testing ConsultantOS across multiple dimensions:

- **User Experience**: First-time user flows, authentication, navigation
- **Core Functionality**: Analysis generation, framework application, report creation
- **Dashboard Features**: Real-time monitoring, alerts, data visualization
- **API Integration**: REST endpoints, WebSocket connections, error handling
- **Advanced Features**: Multi-framework analysis, scenario planning, exports

## Prerequisites

### Environment Setup

1. **Backend API** must be running on `http://localhost:8080`
   ```bash
   python main.py
   # or
   uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
   ```

2. **Frontend Dashboard** must be running on `http://localhost:3000`
   ```bash
   cd frontend && npm run dev
   ```

3. **Required Environment Variables**
   ```bash
   export TAVILY_API_KEY=your_tavily_api_key
   export GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Dependencies Installed**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

### Test Data

For consistent testing, use these standard test cases:

- **Company**: Tesla
- **Industry**: Electric Vehicles
- **Ticker**: TSLA (if applicable)
- **Frameworks**: porter, swot, pestel, blue_ocean

### Test User Account

Create a test user account for authentication testing:

- **Email**: `test@consultantos.com`
- **Password**: `TestPassword123!`
- **Name**: `Test User`

## Test Scenarios

### Scenario 1: First-Time User Experience

**Objective**: Verify new users can successfully register, authenticate, and access the platform.

#### 1.1: Access Application Without Authentication

**Steps**:
1. Navigate to `http://localhost:3000`
2. Observe initial page behavior

**Expected Results**:
- Application loads successfully
- User is redirected to login page OR
- Login form is visible on homepage
- No authentication errors in console

**Validation**:
- URL contains `/login` OR page displays "Login" or "Sign In" text
- No JavaScript errors in browser console
- Page loads within 3 seconds

#### 1.2: Registration Flow

**Steps**:
1. Navigate to registration page (`/register`)
2. Fill in registration form:
   - Email: `test@consultantos.com`
   - Password: `TestPassword123!`
   - Name: `Test User`
3. Submit registration form

**Expected Results**:
- Registration form displays correctly
- All fields are fillable
- Form validation works (if applicable)
- Submission either:
  - Creates account and redirects to dashboard, OR
  - Shows success message (if email verification required)

**Validation**:
- Form fields accept input
- Submit button is clickable
- No form validation errors for valid input
- Appropriate feedback after submission

#### 1.3: Login Flow

**Steps**:
1. Navigate to login page (`/login`)
2. Enter credentials:
   - Email: `test@consultantos.com`
   - Password: `TestPassword123!`
3. Click "Login" or "Sign In" button

**Expected Results**:
- Login form displays correctly
- Credentials are accepted
- User is redirected to dashboard
- API key is generated/retrieved (check browser network tab)

**Validation**:
- Successful redirect to dashboard (URL doesn't contain `/login`)
- User session is established
- API key is available for subsequent requests
- No authentication errors

### Scenario 2: Basic Analysis Generation

**Objective**: Verify core analysis generation functionality works end-to-end.

#### 2.1: Navigate to Analysis Creation Page

**Steps**:
1. Log in to the application
2. Navigate to analysis creation page (`/analysis`)

**Expected Results**:
- Analysis form/page loads successfully
- Form fields are visible:
  - Company name input
  - Industry input
  - Framework selection (checkboxes or multi-select)
- Page is responsive and usable

**Validation**:
- Page loads within 5 seconds
- Form elements are present and accessible
- No JavaScript errors

#### 2.2: Fill Analysis Form and Submit

**Steps**:
1. Fill in analysis form:
   - Company: `Tesla`
   - Industry: `Electric Vehicles`
   - Select frameworks: `Porter's Five Forces`, `SWOT`
2. Submit the form

**Expected Results**:
- Form accepts all inputs
- Submission triggers analysis request
- User receives feedback (loading state, progress indicator)
- Analysis begins processing

**Validation**:
- All form fields accept input
- Submit button triggers action
- Loading/processing state is visible
- Request is sent to backend API

#### 2.3: Monitor Analysis Progress

**Steps**:
1. After submitting analysis, observe progress indicators
2. Wait for analysis completion (or check status endpoint)

**Expected Results**:
- Progress indicator shows analysis status
- Status updates are visible (processing, completed, failed)
- Results are displayed when complete

**Validation**:
- Status updates in real-time
- Results page/section displays analysis data
- No timeout errors for reasonable wait times

### Scenario 3: Multi-Framework Analysis

**Objective**: Verify system handles multiple frameworks simultaneously.

#### 3.1: Request Analysis with Multiple Frameworks

**Steps**:
1. Navigate to analysis page
2. Fill form with:
   - Company: `Tesla`
   - Industry: `Electric Vehicles`
   - Select ALL frameworks: `Porter`, `SWOT`, `PESTEL`, `Blue Ocean`
3. Submit analysis

**Expected Results**:
- All selected frameworks are included in request
- Analysis processes all frameworks
- Results include sections for each framework

**Validation**:
- Request includes all selected frameworks
- Results contain analysis for each framework
- Framework sections are clearly labeled

#### 3.2: Verify Framework Output Quality

**Steps**:
1. Review generated analysis
2. Check each framework section for:
   - Completeness
   - Relevance
   - Structure

**Expected Results**:
- Each framework has dedicated section
- Content is relevant to company/industry
- Analysis follows framework structure (e.g., Porter's 5 forces has 5 sections)

**Validation**:
- All selected frameworks appear in results
- Content quality is reasonable (not empty or generic)
- Framework structure is maintained

### Scenario 4: Dashboard Navigation and Features

**Objective**: Verify dashboard functionality and user interface.

#### 4.1: Access Dashboard

**Steps**:
1. Log in to application
2. Navigate to dashboard (usually default after login)

**Expected Results**:
- Dashboard loads successfully
- Key sections are visible:
  - Monitor list/overview
  - Recent alerts
  - Usage statistics
  - Navigation menu

**Validation**:
- Dashboard renders within 3 seconds
- All major sections are visible
- Navigation is functional

#### 4.2: View Monitor List

**Steps**:
1. Navigate to monitors section
2. View list of active monitors

**Expected Results**:
- Monitor list displays correctly
- Each monitor shows:
  - Company name
  - Industry
  - Status (active, paused, error)
  - Last update time
  - Next scheduled check

**Validation**:
- Monitors are listed correctly
- Status indicators are accurate
- Timestamps are formatted correctly

#### 4.3: Create New Monitor

**Steps**:
1. Click "Create Monitor" or "New Monitor" button
2. Fill monitor configuration:
   - Company: `Apple`
   - Industry: `Technology`
   - Frequency: `Daily`
   - Frameworks: `porter`, `swot`
   - Alert threshold: `0.7`
3. Save monitor

**Expected Results**:
- Monitor creation form displays
- Form accepts all inputs
- Monitor is created successfully
- Monitor appears in list

**Validation**:
- Monitor is saved to database
- Monitor appears in list immediately
- Configuration is correct

### Scenario 5: Alert Management

**Objective**: Verify alert system functionality.

#### 5.1: View Alerts

**Steps**:
1. Navigate to alerts section
2. View list of alerts

**Expected Results**:
- Alerts list displays
- Each alert shows:
  - Company/monitor name
  - Alert type (change detected, threshold exceeded, etc.)
  - Confidence score
  - Timestamp
  - Read/unread status

**Validation**:
- Alerts are listed correctly
- Status indicators work
- Timestamps are accurate

#### 5.2: Mark Alert as Read

**Steps**:
1. Click on an unread alert
2. Mark as read (button or action)

**Expected Results**:
- Alert status changes to "read"
- Alert count updates
- UI reflects change immediately

**Validation**:
- Status updates in database
- UI updates without page refresh
- Alert count decreases

#### 5.3: Provide Alert Feedback

**Steps**:
1. Open an alert
2. Provide feedback (relevant/not relevant, helpful/not helpful)
3. Submit feedback

**Expected Results**:
- Feedback form/buttons are available
- Feedback is submitted successfully
- System acknowledges feedback

**Validation**:
- Feedback is saved
- Confirmation message appears
- Feedback affects alert quality (if implemented)

### Scenario 6: Report Export and Sharing

**Objective**: Verify export and sharing functionality.

#### 6.1: Export Report to PDF

**Steps**:
1. Navigate to a completed analysis/report
2. Click "Export PDF" or similar button
3. Wait for PDF generation
4. Download PDF

**Expected Results**:
- PDF export initiates
- PDF is generated successfully
- PDF contains:
  - Company information
  - Analysis sections
  - Charts/visualizations
  - Timestamp

**Validation**:
- PDF file downloads
- PDF is readable
- Content matches analysis data
- File size is reasonable

#### 6.2: Export Report to JSON

**Steps**:
1. Navigate to a completed analysis
2. Click "Export JSON" or use API endpoint
3. Download JSON file

**Expected Results**:
- JSON export works
- JSON contains structured analysis data
- JSON is valid and parseable

**Validation**:
- JSON file downloads
- JSON is valid (can be parsed)
- Contains expected fields

#### 6.3: Share Report

**Steps**:
1. Navigate to a report
2. Click "Share" button
3. Configure sharing:
   - Set permissions (view-only, comment, edit)
   - Set expiration (optional)
4. Generate share link

**Expected Results**:
- Share link is generated
- Link can be copied
- Link works when accessed (test in incognito/other browser)

**Validation**:
- Link is accessible
- Permissions are enforced
- Expiration works (if set)

### Scenario 7: API Integration Testing

**Objective**: Verify API endpoints work correctly.

#### 7.1: Health Check

**Steps**:
```bash
curl http://localhost:8080/health
```

**Expected Results**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Validation**:
- Status code: 200
- Response is valid JSON
- Status is "healthy"

#### 7.2: Create Analysis via API

**Steps**:
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

**Expected Results**:
- Status code: 200
- Response contains:
  - `report_id`
  - `company`
  - `status` (processing or completed)
  - Analysis data (if completed)

**Validation**:
- Request is accepted
- Analysis is queued/processed
- Response structure is correct

#### 7.3: Get Analysis Status

**Steps**:
```bash
curl "http://localhost:8080/reports/{report_id}" \
  -H "X-API-Key: your_api_key"
```

**Expected Results**:
- Status code: 200
- Response contains current analysis status
- Includes progress information if processing

**Validation**:
- Status is accurate
- Progress updates correctly
- Error handling works for invalid IDs

#### 7.4: List User Monitors

**Steps**:
```bash
curl "http://localhost:8080/monitors" \
  -H "X-API-Key: your_api_key"
```

**Expected Results**:
- Status code: 200
- Response contains array of monitors
- Each monitor has required fields

**Validation**:
- Only user's monitors are returned
- Data structure is correct
- Empty array if no monitors

### Scenario 8: Error Handling and Edge Cases

**Objective**: Verify system handles errors gracefully.

#### 8.1: Invalid API Key

**Steps**:
```bash
curl "http://localhost:8080/monitors" \
  -H "X-API-Key: invalid_key"
```

**Expected Results**:
- Status code: 401 Unauthorized
- Error message indicates authentication failure

**Validation**:
- Error is returned promptly
- No sensitive information leaked
- Error message is clear

#### 8.2: Missing Required Fields

**Steps**:
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company": "Tesla"}'
```

**Expected Results**:
- Status code: 422 Validation Error
- Error message lists missing fields

**Validation**:
- Validation errors are clear
- All missing fields are identified
- Error format is consistent

#### 8.3: Invalid Company/Industry

**Steps**:
1. Submit analysis with:
   - Company: `""` (empty string)
   - Industry: `Invalid Industry Name With Special Characters !@#$`

**Expected Results**:
- Validation errors are shown
- Request is rejected before processing
- Error messages are helpful

**Validation**:
- Input sanitization works
- Error messages guide user
- No system crashes

### Scenario 9: Frontend Dashboard Testing

**Objective**: Comprehensive frontend functionality testing.

#### 9A: Authentication & Registration Flow

**Steps**: Same as Scenario 1

**Additional Checks**:
- Form validation messages
- Password strength indicators
- Email format validation
- Error message display

#### 9B: Dashboard Layout and Responsiveness

**Steps**:
1. Access dashboard
2. Resize browser window
3. Test on different screen sizes (if possible)

**Expected Results**:
- Dashboard is responsive
- Layout adapts to screen size
- No horizontal scrolling on mobile
- All features remain accessible

**Validation**:
- Works on desktop (1920x1080)
- Works on tablet (768x1024)
- Works on mobile (375x667)
- Navigation remains functional

#### 9C: Data Visualization

**Steps**:
1. Navigate to a report with charts
2. View different chart types
3. Interact with charts (hover, click if interactive)

**Expected Results**:
- Charts render correctly
- Data is accurate
- Charts are readable
- Interactive features work

**Validation**:
- Charts display without errors
- Data matches analysis
- Tooltips work (if applicable)
- Charts are responsive

#### 9D: Real-Time Updates

**Steps**:
1. Open dashboard
2. Trigger an analysis or monitor update
3. Observe real-time updates

**Expected Results**:
- Updates appear without page refresh
- WebSocket connection is established (check network tab)
- Status changes are reflected immediately

**Validation**:
- WebSocket connects successfully
- Updates are received
- UI updates correctly
- No connection errors

### Scenario 10: API Integration Testing

**Objective**: Test API endpoints comprehensively.

#### 10.1: Authentication Endpoints

**Test Registration**:
```bash
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "SecurePass123!",
    "name": "New User"
  }'
```

**Test Login**:
```bash
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@consultantos.com",
    "password": "TestPassword123!"
  }'
```

**Expected Results**:
- Registration creates user
- Login returns API key/token
- Credentials are validated

#### 10.2: Analysis Endpoints

**Test Synchronous Analysis**:
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter"]
  }'
```

**Test Asynchronous Analysis**:
```bash
curl -X POST "http://localhost:8080/analyze/async" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "company": "Apple",
    "industry": "Technology",
    "frameworks": ["porter", "swot", "pestel"]
  }'
```

**Expected Results**:
- Synchronous: Returns completed analysis
- Asynchronous: Returns job_id, status can be checked

#### 10.3: Monitor Endpoints

**Create Monitor**:
```bash
curl -X POST "http://localhost:8080/monitors" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "config": {
      "frequency": "daily",
      "frameworks": ["porter", "swot"],
      "alert_threshold": 0.7
    }
  }'
```

**List Monitors**:
```bash
curl "http://localhost:8080/monitors" \
  -H "X-API-Key: your_api_key"
```

**Get Monitor**:
```bash
curl "http://localhost:8080/monitors/{monitor_id}" \
  -H "X-API-Key: your_api_key"
```

**Expected Results**:
- Monitor is created
- List returns all user monitors
- Get returns monitor details

#### 10.4: Dashboard Endpoints

**Create Dashboard**:
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "template": "executive_summary",
    "frameworks": ["porter", "swot"]
  }'
```

**Get Dashboard**:
```bash
curl "http://localhost:8080/dashboards/{dashboard_id}" \
  -H "X-API-Key: your_api_key"
```

**Expected Results**:
- Dashboard is created
- Dashboard data is returned
- Template is applied correctly

### Scenario 11: Performance Testing

**Objective**: Verify system performance under normal load.

#### 11.1: Page Load Times

**Steps**:
1. Open browser DevTools (Network tab)
2. Navigate to each major page
3. Record load times

**Expected Results**:
- Homepage: < 2 seconds
- Dashboard: < 3 seconds
- Analysis page: < 2 seconds
- Report view: < 3 seconds

**Validation**:
- All pages load within targets
- No blocking resources
- Images are optimized

#### 11.2: API Response Times

**Steps**:
1. Use API testing tool (Postman, curl with timing)
2. Test key endpoints
3. Measure response times

**Expected Results**:
- Health check: < 100ms
- Simple GET requests: < 500ms
- Analysis creation: < 2 seconds (queuing)
- Analysis status: < 500ms

**Validation**:
- Responses are within targets
- No timeouts for normal requests
- Caching works (repeated requests faster)

#### 11.3: Concurrent Requests

**Steps**:
1. Send multiple simultaneous requests
2. Observe system behavior

**Expected Results**:
- All requests are handled
- No errors from concurrency
- System remains stable

**Validation**:
- No race conditions
- Data consistency maintained
- Error handling works

### Scenario 12: Security Testing

**Objective**: Verify security measures are in place.

#### 12.1: Input Sanitization

**Steps**:
1. Submit analysis with SQL injection attempt:
   - Company: `'; DROP TABLE users; --`
2. Submit with XSS attempt:
   - Company: `<script>alert('XSS')</script>`

**Expected Results**:
- Input is sanitized
- No SQL injection possible
- No XSS execution
- Error messages don't reveal system details

**Validation**:
- Malicious input is rejected or sanitized
- No database errors
- No script execution

#### 12.2: Authentication Security

**Steps**:
1. Attempt to access protected endpoint without API key
2. Attempt with invalid API key
3. Attempt with expired token (if applicable)

**Expected Results**:
- All attempts are rejected
- Status code: 401 Unauthorized
- No sensitive information in error messages

**Validation**:
- Authentication is enforced
- Error messages don't leak information
- Rate limiting works (if implemented)

#### 12.3: Data Access Control

**Steps**:
1. Create monitor as User A
2. Attempt to access monitor as User B (different API key)

**Expected Results**:
- User B cannot access User A's monitor
- Status code: 403 Forbidden or 404 Not Found

**Validation**:
- Authorization is enforced
- Users can only access their own data
- No data leakage

### Scenario 13: Frontend-Backend Integration Testing

**Objective**: Verify frontend and backend work together correctly.

#### 13.1: End-to-End Analysis Flow

**Steps**:
1. Open frontend dashboard
2. Create new analysis via UI
3. Monitor progress in UI
4. View results in UI

**Expected Results**:
- Frontend sends correct request to backend
- Backend processes request
- Frontend receives and displays results
- All data flows correctly

**Validation**:
- Network requests are correct
- Data format matches
- UI updates reflect backend state
- No data loss or corruption

#### 13.2: Real-Time Updates Integration

**Steps**:
1. Open dashboard
2. Trigger backend update (via API or scheduled)
3. Observe frontend update

**Expected Results**:
- WebSocket connection established
- Frontend receives update
- UI updates automatically
- No manual refresh needed

**Validation**:
- WebSocket works end-to-end
- Updates are timely
- UI state is synchronized
- Connection recovery works

## Manual Testing Procedures

### Pre-Testing Checklist

- [ ] Backend API is running
- [ ] Frontend is running
- [ ] Environment variables are set
- [ ] Test user account exists
- [ ] Browser DevTools are open (for debugging)
- [ ] Network tab is open (to monitor requests)

### Testing Workflow

1. **Start Fresh**: Clear browser cache and cookies
2. **Test Each Scenario**: Follow scenarios in order
3. **Document Issues**: Note any bugs or unexpected behavior
4. **Verify Fixes**: Re-test after fixes
5. **Test Edge Cases**: Try unusual inputs and conditions

### Recording Test Results

For each test scenario, record:

- **Status**: Pass / Fail / Partial
- **Notes**: Any observations or issues
- **Screenshots**: Capture important states
- **Errors**: Any console or network errors
- **Time**: How long the test took

## Automated Testing

### Running E2E Tests

The project includes automated end-to-end tests using Puppeteer. These tests execute the scenarios defined in this guide.

#### Prerequisites

```bash
# Install dependencies
npm install
cd frontend && npm install
```

#### Run All Tests

```bash
# Option 1: Using test runner script
./tests/e2e/run-tests.sh

# Option 2: Using npm script
npm run test:e2e

# Option 3: Using Jest directly
jest --config jest.e2e.config.js --testPathPattern=tests/e2e
```

#### Run Specific Test Scenarios

```bash
# Run Scenario 1 only
jest --config jest.e2e.config.js tests/e2e/scenario1-first-time-user.test.js

# Run Scenario 2 only
jest --config jest.e2e.config.js tests/e2e/scenario2-basic-analysis.test.js
```

#### Test Configuration

Edit `tests/e2e/puppeteer.config.js` to customize:

- Frontend URL (default: `http://localhost:3000`)
- Backend URL (default: `http://localhost:8080`)
- Test user credentials
- Timeout values
- Test data

### Test Reports

After running tests:

- **Screenshots**: Saved to `tests/e2e/screenshots/`
- **Test Results**: Displayed in console
- **Error Logs**: Captured and reported

## API Testing

### Using curl

Basic curl examples are provided in each scenario. For more advanced testing, use:

- **Postman**: Import API collection
- **HTTPie**: More readable than curl
- **Insomnia**: GUI for API testing

### API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### Testing WebSocket Connections

For WebSocket testing, use a WebSocket client:

```javascript
// Example: Connect to dashboard WebSocket
const ws = new WebSocket('ws://localhost:8080/dashboards/{dashboard_id}/ws');

ws.onmessage = (event) => {
  console.log('Update received:', JSON.parse(event.data));
};
```

## Expected Results

### Success Criteria

For a test to be considered **PASSING**:

1. **Functional**: Feature works as described
2. **Performance**: Meets performance targets
3. **Error Handling**: Graceful error handling
4. **User Experience**: Intuitive and responsive
5. **Data Integrity**: Data is accurate and consistent

### Common Success Indicators

- ✅ Status codes: 200, 201, 204 for success
- ✅ Response times: Within targets
- ✅ No console errors: JavaScript errors resolved
- ✅ UI updates: Real-time updates work
- ✅ Data accuracy: Results match expectations

## Troubleshooting

### Common Issues

#### Backend Not Starting

**Symptoms**: Cannot connect to `http://localhost:8080`

**Solutions**:
1. Check if port 8080 is already in use:
   ```bash
   lsof -i :8080
   ```
2. Verify environment variables are set
3. Check backend logs for errors
4. Ensure dependencies are installed

#### Frontend Not Loading

**Symptoms**: Frontend page doesn't load or shows errors

**Solutions**:
1. Verify frontend is running on port 3000
2. Check browser console for errors
3. Clear browser cache
4. Verify `NEXT_PUBLIC_API_URL` is set correctly

#### Authentication Failures

**Symptoms**: Cannot log in or API returns 401

**Solutions**:
1. Verify user account exists
2. Check API key is correct
3. Verify API key format
4. Check backend authentication logs

#### Analysis Not Completing

**Symptoms**: Analysis stuck in "processing" state

**Solutions**:
1. Check backend logs for agent errors
2. Verify API keys (TAVILY_API_KEY, GEMINI_API_KEY)
3. Check job queue status
4. Verify database connectivity

#### WebSocket Connection Fails

**Symptoms**: Real-time updates not working

**Solutions**:
1. Check WebSocket endpoint is accessible
2. Verify dashboard_id is valid
3. Check browser console for WebSocket errors
4. Verify backend WebSocket handler is running

### Debugging Tips

1. **Check Logs**: Both frontend and backend logs
2. **Network Tab**: Monitor API requests/responses
3. **Console**: Check browser console for errors
4. **Database**: Verify data is being saved
5. **API Keys**: Ensure all required keys are set

### Getting Help

If issues persist:

1. Check [README.md](README.md) for setup instructions
2. Review [SETUP.md](SETUP.md) for detailed setup
3. Check [tests/README.md](tests/README.md) for test-specific help
4. Review backend logs in detail
5. Check GitHub issues (if applicable)

## Best Practices

### Testing Best Practices

1. **Test Incrementally**: Test one feature at a time
2. **Use Test Data**: Use consistent test data for reproducibility
3. **Clean State**: Start with clean state for each test
4. **Document Issues**: Record bugs with steps to reproduce
5. **Verify Fixes**: Re-test after fixes are applied

### Manual Testing Best Practices

1. **Follow Scenarios**: Use scenarios as guide, but explore edge cases
2. **Test Different Browsers**: Chrome, Firefox, Safari (if possible)
3. **Test Different Devices**: Desktop, tablet, mobile (if possible)
4. **Test Error Cases**: Intentionally trigger errors
5. **Test Performance**: Monitor load times and responsiveness

### Automated Testing Best Practices

1. **Keep Tests Updated**: Update tests when UI/API changes
2. **Use Descriptive Names**: Test names should describe what they test
3. **Isolate Tests**: Tests should not depend on each other
4. **Clean Up**: Tests should clean up after themselves
5. **Handle Flakiness**: Add retries for flaky tests

### Reporting Issues

When reporting bugs or issues, include:

1. **Scenario**: Which test scenario
2. **Steps**: Exact steps to reproduce
3. **Expected**: What should happen
4. **Actual**: What actually happened
5. **Environment**: OS, browser, versions
6. **Logs**: Relevant error logs
7. **Screenshots**: Visual evidence

## Additional Resources

- [API Documentation](API_Documentation.md) - Complete API reference
- [Setup Guide](SETUP.md) - Detailed setup instructions
- [Test Suite README](tests/README.md) - Backend test documentation
- [E2E Test README](tests/e2e/README.md) - Frontend test documentation
- [Architecture Documentation](ARCHITECTURE.md) - System architecture

## Test Coverage Summary

This guide covers:

- ✅ User authentication and registration
- ✅ Analysis generation (basic and multi-framework)
- ✅ Dashboard functionality
- ✅ Alert management
- ✅ Report export and sharing
- ✅ API endpoints
- ✅ Error handling
- ✅ Performance
- ✅ Security
- ✅ Frontend-backend integration

## Version History

- **v1.0** (2024-01-01): Initial comprehensive testing guide
  - All 13 scenarios documented
  - Manual and automated testing procedures
  - Troubleshooting guide

---

**Last Updated**: 2024-01-01  
**Maintained By**: ConsultantOS Team  
**For Questions**: See documentation or open an issue

