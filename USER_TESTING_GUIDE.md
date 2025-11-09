# ConsultantOS - User Testing Guide

## Table of Contents

1. [Overview](#overview)
2. [Pre-Testing Setup](#pre-testing-setup)
3. [Test Scenarios](#test-scenarios)
   - Scenario 1: First-Time User Experience
   - Scenario 2: Basic Analysis Generation
   - Scenario 3: Multi-Framework Analysis
   - Scenario 3B: Async Analysis Processing
   - Scenario 4: Report Retrieval and Management
   - Scenario 5: Framework-Specific Testing
   - Scenario 6: Edge Cases and Error Handling
   - Scenario 7: Performance Testing
   - Scenario 8: Report Quality Assessment
   - Scenario 9: Frontend Dashboard Testing (11 sub-tests)
   - Scenario 10: API Integration Testing
   - Scenario 11: Export Formats Testing
   - Scenario 12: Data Source Reliability
   - Scenario 13: Frontend-Backend Integration Testing
4. [What to Observe](#what-to-observe)
5. [Reporting Findings](#reporting-findings)
6. [Best Practices](#best-practices)
7. [Appendix](#appendix)

---

## Overview

### Purpose

This guide provides a comprehensive framework for testing ConsultantOS, a multi-agent AI system that generates McKinsey-grade business framework analyses. The goal is to validate functionality, usability, performance, and quality from the perspective of independent strategy consultants.

### Testing Objectives

1. **Functional Testing**: Verify all features work as intended
2. **Usability Testing**: Assess ease of use and user experience
3. **Performance Testing**: Validate response times and system performance
4. **Quality Testing**: Evaluate report quality and accuracy
5. **Edge Case Testing**: Test error handling and boundary conditions
6. **Integration Testing**: Verify API and frontend integration

### Target Users

- **Primary**: Independent strategy consultants (ex-Big 4, solo practitioners)
- **Secondary**: Boutique firm owners/principals
- **Tertiary**: Engagement managers

### Success Criteria

- **Performance**: API response <5s, end-to-end analysis 30-60s
- **Quality**: ≥60% "McKinsey-comparable" rating from ex-consultants
- **Usability**: Users can complete analysis without documentation
- **Reliability**: ≥99% success rate, graceful error handling

---

## Pre-Testing Setup

### Environment Requirements

1. **Backend Server**

   ```bash
   # Start the API server
   python main.py
   # Or
   uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080
   ```

2. **Frontend Dashboard** (Recommended for comprehensive testing)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   **Note**: The frontend provides a complete UI for testing all features including:

   - User authentication and registration
   - Analysis creation (synchronous and asynchronous)
   - Report management and viewing
   - Job queue monitoring
   - Template library
   - Version comparison and history
   - Comments and collaboration
   - Sharing and permissions
   - Profile and API key management

3. **Required Environment Variables**

   ```bash
   export TAVILY_API_KEY=your_tavily_key
   export GEMINI_API_KEY=your_gemini_key
   ```

   **Frontend Environment** (optional, for frontend testing):

   ```bash
   # Create frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```

4. **API Access**
   - API Base URL: `http://localhost:8080`
   - Swagger UI: `http://localhost:8080/docs`
   - ReDoc: `http://localhost:8080/redoc`
   - Frontend Dashboard: `http://localhost:3000` (when frontend is running)

### Test Data Preparation

Prepare test cases for different scenarios:

1. **Well-Known Companies** (for baseline testing)

   - Tesla (Electric Vehicles)
   - Netflix (Streaming Media)
   - Apple (Technology)
   - Amazon (E-commerce)

2. **Private Companies** (for edge case testing)

   - Small local businesses
   - Startups with limited public data

3. **Niche Industries** (for data availability testing)

   - Industrial IoT
   - B2B SaaS
   - Healthcare Technology

4. **Invalid Inputs** (for error handling)
   - Empty fields
   - Special characters
   - Extremely long strings
   - Invalid framework names

### Testing Tools

- **API Testing**: Postman, curl, or HTTPie
- **Browser Testing**: Chrome, Firefox, Safari
- **Screen Recording**: OBS, QuickTime (for session recording)
- **Note-Taking**: Spreadsheet or document for findings

### Test Account Setup

1. **Create Test User Account**

   ```bash
   curl -X POST "http://localhost:8080/users/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@consultantos.com",
       "password": "TestPassword123!",
       "name": "Test User"
     }'
   ```

2. **Login and Get API Key**

   ```bash
   curl -X POST "http://localhost:8080/users/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@consultantos.com",
       "password": "TestPassword123!"
     }'
   ```

   **Response:**

   ```json
   {
     "access_token": "your_api_key_here",
     "token_type": "bearer",
     "user": {
       "user_id": "...",
       "email": "test@consultantos.com"
     }
   }
   ```

3. **Save API Key** (`access_token` from response) for subsequent requests

---

## Test Scenarios

### Scenario 1: First-Time User Experience

**Objective**: Test the onboarding flow and initial user experience

**Steps**:

1. Access the application (API or frontend)
2. If using frontend, attempt to access dashboard without login
3. Register a new account
4. Login with credentials
5. Explore the dashboard/interface
6. Review available documentation or help

**Expected Results**:

- Registration process is clear and straightforward
- Login works correctly
- Dashboard displays correctly after authentication
- User can understand how to start an analysis

**What to Record**:

- Time to complete registration
- Number of clicks to start first analysis
- Clarity of instructions
- Any confusion or questions

---

### Scenario 2: Basic Analysis Generation

**Objective**: Test the core functionality of generating a strategic analysis

**Steps**:

1. Navigate to analysis creation (API or UI)
2. Enter company name: "Tesla"
3. Enter industry: "Electric Vehicles"
4. Select frameworks: ["porter", "swot"]
5. Submit the analysis request
6. Wait for completion
7. Review the generated report

**API Request**:

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"],
    "depth": "standard"
  }'
```

**Expected Results**:

- Request accepted within 5 seconds
- Analysis completes within 30-60 seconds
- Report contains requested frameworks
- PDF is downloadable and readable
- Executive summary is present

**What to Record**:

- API response time
- Total analysis time
- Report quality (content, formatting, charts)
- Confidence score
- Number of citations

---

### Scenario 3: Multi-Framework Analysis

**Objective**: Test generating all four frameworks simultaneously

**Steps**:

1. Submit analysis with all frameworks: ["porter", "swot", "pestel", "blue_ocean"]
2. Monitor progress (if available)
3. Wait for completion
4. Review each framework section in the PDF

**API Request**:

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "company": "Netflix",
    "industry": "Streaming Media",
    "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
    "depth": "standard"
  }'
```

**Expected Results**:

- All four frameworks are included
- Each framework has substantial content
- Frameworks are consistent with each other
- Visualizations are present where applicable
- Report structure is professional

**What to Record**:

- Completion time
- Quality of each framework
- Consistency across frameworks
- Presence of visualizations
- Overall report coherence

---

### Scenario 3B: Async Analysis Processing

**Objective**: Test asynchronous job processing for long-running analyses

**Steps**:

1. Submit analysis using `/analyze/async` endpoint
2. Receive job_id and status URL
3. Poll job status endpoint
4. Retrieve completed report when status is "completed"

**API Request**:

```bash
# Enqueue async job
curl -X POST "http://localhost:8080/analyze/async" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
    "depth": "deep"
  }'

# Response:
# {
#   "job_id": "550e8400-e29b-41d4-a716-446655440000",
#   "status": "pending",
#   "status_url": "/jobs/550e8400-e29b-41d4-a716-446655440000/status",
#   "estimated_completion": "2-5 minutes"
# }

# Poll job status
curl -X GET "http://localhost:8080/jobs/550e8400-e29b-41d4-a716-446655440000/status"

# List all jobs
curl -X GET "http://localhost:8080/jobs?status=completed" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Results**:

- Job is enqueued successfully
- Status updates correctly (pending → processing → completed)
- Report is accessible after completion
- Job listing filters work correctly

**What to Record**:

- Job enqueue time
- Status polling frequency
- Total processing time
- Error handling if job fails

---

### Scenario 4: Report Retrieval and Management

**Objective**: Test accessing previously generated reports

**Steps**:

1. Generate a report (from Scenario 2 or 3)
2. Note the report_id from response
3. Retrieve report using GET endpoint
4. If using frontend, check reports list
5. Download PDF from different sessions/devices

**API Request**:

```bash
# List all reports
curl -X GET "http://localhost:8080/reports" \
  -H "X-API-Key: YOUR_API_KEY"

# Get specific report
curl -X GET "http://localhost:8080/reports/{report_id}" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Results**:

- Reports list displays correctly
- Report metadata is accurate
- PDF download works
- Signed URLs expire appropriately
- Report history is maintained

**What to Record**:

- Ease of finding reports
- Report metadata accuracy
- Download reliability
- URL expiration behavior

---

### Scenario 5: Framework-Specific Testing

**Objective**: Test each framework individually for quality

**Test 5A: Porter's Five Forces**

- Submit analysis with only "porter" framework
- Verify all five forces are analyzed
- Check for competitive intensity scores
- Validate industry structure insights

**Test 5B: SWOT Analysis**

- Submit analysis with only "swot" framework
- Verify all four quadrants are populated
- Check prioritization of factors
- Validate internal vs external categorization

**Test 5C: PESTEL Analysis**

- Submit analysis with only "pestel" framework
- Verify all six factors are covered
- Check regional/industry specificity
- Validate macro-environment insights

**Test 5D: Blue Ocean Strategy**

- Submit analysis with only "blue_ocean" framework
- Verify value curve identification
- Check for strategic moves
- Validate strategy canvas visualization

**What to Record**:

- Framework completeness
- Quality of insights
- Presence of evidence/citations
- Visual quality (if applicable)

---

### Scenario 6: Edge Cases and Error Handling

**Objective**: Test system behavior with invalid or edge case inputs

**Test 6A: Missing Required Fields**

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": ""
  }'
```

- Expected: Clear error message, 400 status code

**Test 6B: Invalid Framework Names**

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "EV",
    "frameworks": ["invalid_framework"]
  }'
```

- Expected: Validation error, helpful message

**Test 6C: Private Company (Limited Data)**

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Local Small Business Inc",
    "industry": "Local Services",
    "frameworks": ["porter", "swot"]
  }'
```

- Expected: Graceful handling, proxy data usage, clear labeling

**Test 6D: Rate Limiting**

- Submit 11 requests rapidly (if limit is 10/hour)
- Expected: Rate limit error after 10th request

**Test 6E: Very Long Company Name**

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "A" * 500,
    "industry": "Test"
  }'
```

- Expected: Input validation, reasonable error

**What to Record**:

- Error message clarity
- HTTP status codes
- System stability
- User guidance quality

---

### Scenario 7: Performance Testing

**Objective**: Validate performance metrics

**Test 7A: API Response Time**

- Measure time from request submission to first response
- Target: <5 seconds
- Run 10 requests and calculate average

**Test 7B: End-to-End Analysis Time**

- Measure total time from submission to report completion
- Target: 30-60 seconds
- Test with different companies and framework combinations

**Test 7C: Concurrent Requests**

- Submit 5 analyses simultaneously
- Monitor system behavior
- Check for resource contention

**Test 7D: Large Report Generation**

- Generate report with all frameworks and "deep" depth
- Measure time and resource usage

**What to Record**:

- Response times (p50, p95, p99)
- Success rate
- Resource usage
- Error rates under load

---

### Scenario 8: Report Quality Assessment

**Objective**: Evaluate the quality and accuracy of generated reports

**Evaluation Criteria**:

1. **Content Quality**

   - Are insights relevant and accurate?
   - Is the analysis comprehensive?
   - Are claims supported by evidence?
   - Is the language professional?

2. **Framework Adherence**

   - Does Porter's analysis cover all five forces?
   - Does SWOT properly categorize factors?
   - Does PESTEL cover all six dimensions?
   - Does Blue Ocean identify value curves?

3. **Data Quality**

   - Are citations present and accessible?
   - Is data recent (within 12 months)?
   - Are sources credible?
   - Are confidence scores reasonable?

4. **Visual Quality**

   - Are charts clear and readable?
   - Do visualizations add value?
   - Is formatting professional?
   - Is PDF rendering consistent?

5. **Executive Summary**
   - Is it concise (1 page)?
   - Does it capture key insights?
   - Is it actionable?
   - Does it highlight risks?

**Test Companies**:

- Tesla (well-known, data-rich)
- Netflix (mature industry)
- A startup (limited data)
- A niche B2B company

**What to Record**:

- Quality score (1-10) for each criterion
- Specific examples of strengths/weaknesses
- Comparison to manual analysis (if possible)
- Client-readiness assessment

---

### Scenario 9: Frontend Dashboard Testing

**Objective**: Test the complete web interface and user experience

**Test 9A: Authentication & Registration Flow**

1. **Access Dashboard** (`http://localhost:3000`)

   - Verify redirect to login if not authenticated
   - Check login page loads correctly

2. **Registration Flow**

   - Click "Register" or navigate to `/register`
   - Fill in registration form (email, password, name)
   - Submit and verify email verification prompt
   - Check for validation errors (invalid email, weak password)
   - Verify successful registration redirects to login

3. **Login Flow**

   - Enter valid credentials
   - Verify successful login redirects to dashboard
   - Check session persistence (refresh page, should stay logged in)
   - Test logout functionality
   - Verify logout clears session and redirects to login

4. **Password Reset Flow**
   - Click "Forgot Password" link
   - Enter email address
   - Verify reset email sent message
   - Test password reset confirmation flow

**Test 9B: Dashboard Home Page** (`/`)

1. **Metrics Display**

   - Verify 4 metric cards display:
     - Total Reports Created (with trend indicator)
     - Active Jobs count
     - Reports This Month
     - Average Confidence Score
   - Check metrics update correctly
   - Verify loading states during data fetch

2. **Recent Reports Table**

   - Verify table displays last 5 reports
   - Check columns: Company, Industry, Frameworks, Status, Date
   - Test sorting functionality
   - Verify click on report navigates to detail page
   - Check empty state when no reports exist

3. **Quick Actions Section**

   - Verify 4 action cards:
     - Create Analysis
     - Browse Templates
     - View Reports
     - View Jobs
   - Test navigation to each section
   - Verify hover states and visual feedback

4. **Getting Started Guide**
   - Verify 3-step onboarding guide displays
   - Check guide is helpful for new users
   - Test responsive layout on mobile/tablet

**Test 9C: Analysis Creation Page** (`/analysis`)

1. **Tabbed Interface**

   - Verify two tabs: "Quick Analysis" and "Batch Analysis"
   - Test tab switching functionality
   - Verify form resets when switching tabs

2. **Quick Analysis (Synchronous)**

   - Fill in company name
   - Select industry (or use auto-detection)
   - Select frameworks (Porter, SWOT, PESTEL, Blue Ocean)
   - Choose analysis depth (standard/deep)
   - Submit and verify loading indicator
   - Check success message and auto-navigation to report
   - Test error handling (invalid input, API errors)

3. **Batch Analysis (Asynchronous)**

   - Fill in analysis form
   - Submit and verify job enqueued message
   - Check job_id is displayed
   - Verify redirect to jobs page or job status display
   - Test multiple batch submissions

4. **Framework Quick Reference**

   - Verify framework descriptions display
   - Check tooltips or help text for each framework
   - Test framework selector interactions

5. **Recent Analyses Tracking**
   - Verify recent analyses saved to localStorage
   - Check recent analyses display in dropdown or sidebar
   - Test clearing recent analyses

**Test 9D: Reports List Page** (`/reports`)

1. **DataTable Functionality**

   - Verify all reports display in table
   - Test pagination (if applicable)
   - Test sorting by each column
   - Test filtering by company, industry, status
   - Test search functionality
   - Verify row selection (if applicable)

2. **Report Actions**

   - Test "View" button navigates to report detail
   - Test "Download" button downloads PDF
   - Test "Share" button opens share dialog
   - Test "Delete" button with confirmation
   - Verify bulk actions (if applicable)

3. **Empty States**

   - Verify helpful message when no reports exist
   - Check "Create Analysis" CTA displays

4. **Responsive Design**
   - Test table on mobile (horizontal scroll or card view)
   - Verify filters work on small screens

**Test 9E: Report Detail Page** (`/reports/[id]`)

1. **Report Display**

   - Verify report metadata displays (company, industry, date, confidence)
   - Check framework sections render correctly
   - Verify executive summary displays
   - Test PDF viewer or download link
   - Check visualizations/charts display correctly

2. **Version History**

   - Verify version history sidebar or section
   - Test viewing different versions
   - Test version comparison feature
   - Test restoring previous version
   - Check version diff display

3. **Comments & Collaboration**

   - Test adding a comment
   - Verify comment thread displays
   - Test replying to comments
   - Test comment reactions (if applicable)
   - Test editing/deleting own comments
   - Verify real-time updates (if WebSocket implemented)

4. **Sharing Features**

   - Test "Share" button opens share dialog
   - Create share link with expiration
   - Test permission settings (view/edit)
   - Verify share analytics display (if applicable)
   - Test revoking share links

5. **Export Options**
   - Test PDF download
   - Test JSON export (if implemented)
   - Test Excel export (if implemented)
   - Test Word export (if implemented)

**Test 9F: Jobs Queue Page** (`/jobs`)

1. **Job List Display**

   - Verify all jobs display with status
   - Check job status indicators (pending, running, completed, failed)
   - Test filtering by status
   - Test sorting by date, status

2. **Job Status Monitoring**

   - Verify real-time status updates (polling or WebSocket)
   - Test job progress indicators
   - Check estimated completion time
   - Verify job cancellation (if applicable)

3. **Job Details**

   - Click job to view details
   - Verify job parameters display
   - Check error messages for failed jobs
   - Test retry functionality (if applicable)

4. **Job History**
   - Verify completed jobs archive
   - Test pagination for large job lists
   - Check job result links work

**Test 9G: Templates Page** (`/templates`)

1. **Template Library**

   - Verify template cards display
   - Test filtering by category, framework type, visibility
   - Test search functionality
   - Verify template preview or description

2. **Template Details**

   - Click template to view details
   - Verify template structure displays
   - Test "Use Template" button
   - Check template metadata (author, created date, usage count)

3. **Template Creation** (if authenticated)

   - Test creating custom template
   - Verify template form validation
   - Test saving template
   - Verify template appears in library

4. **Template Management**
   - Test editing own templates
   - Test deleting own templates
   - Verify template sharing settings

**Test 9H: Profile & Settings Page** (`/profile`)

1. **Profile Information**

   - Verify user profile displays
   - Test editing name, email
   - Verify email verification status
   - Test password change functionality

2. **API Key Management**

   - Verify API keys list displays
   - Test creating new API key
   - Test rotating API key
   - Test revoking API key
   - Verify key masking/security

3. **Notification Settings**

   - Test notification preferences
   - Verify email notification toggles
   - Test comment notification settings
   - Check notification center access

4. **Account Management**
   - Test account deletion (if applicable)
   - Verify data export (if applicable)
   - Check privacy settings

**Test 9I: Version Comparison Feature**

1. **Version Selection**

   - Navigate to report detail page
   - Open version history
   - Select two versions to compare
   - Verify comparison modal opens

2. **Comparison Display**

   - Verify side-by-side or diff view
   - Check framework changes highlighted
   - Test content changes display
   - Verify metrics changes shown
   - Test navigation between changes

3. **Version Actions**
   - Test restoring to previous version
   - Verify restore confirmation dialog
   - Check version branching (if applicable)
   - Test publishing version

**Test 9J: Comments & Notifications**

1. **Comment Threading**

   - Add comment to report
   - Reply to existing comment
   - Verify thread structure displays correctly
   - Test nested replies (if supported)

2. **Comment Notifications**

   - Verify notification appears for new comments
   - Test notification center access
   - Check notification settings
   - Test marking notifications as read

3. **Comment Interactions**
   - Test comment reactions (like, etc.)
   - Verify comment editing
   - Test comment deletion
   - Check comment timestamps and author info

**Test 9K: Navigation & Responsive Design**

1. **Navigation Menu**

   - Verify all menu items display
   - Test navigation to each page
   - Check active state highlighting
   - Test mobile hamburger menu
   - Verify user menu dropdown

2. **Responsive Design**

   - Test on desktop (1920x1080, 1366x768)
   - Test on tablet (768x1024)
   - Test on mobile (375x667, 414x896)
   - Verify all features work on mobile
   - Check touch interactions

3. **Browser Compatibility**
   - Test in Chrome
   - Test in Firefox
   - Test in Safari
   - Test in Edge
   - Verify feature parity across browsers

**What to Record**:

- UI clarity and intuitiveness
- Number of clicks to complete tasks
- Visual design quality
- Responsive behavior across devices
- Error message display and clarity
- Loading states and feedback
- Navigation flow efficiency
- Feature discoverability
- Accessibility (keyboard navigation, screen readers)
- Performance (page load times, interaction responsiveness)

---

### Scenario 10: API Integration Testing

**Objective**: Test API endpoints comprehensively

**Test 10A: Health Check**

```bash
curl http://localhost:8080/health
```

- Expected: Status "healthy", version info (0.3.0), cache/storage/database status
- Verify worker status is included (running, task_exists)
- Check all service availability indicators

**Test 10B: Authentication**

- Test with valid API key (via `X-API-Key` header or `?api_key=` query param)
- Test with invalid API key
- Test with missing API key (for optional endpoints)
- Verify error responses

**Test 10C: Analytics Endpoints**

```bash
curl -X GET "http://localhost:8080/metrics" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Verify metrics accuracy
- Check cache hit rate
- Validate execution time averages

**Test 10D: Template Endpoints**

```bash
# List templates
curl -X GET "http://localhost:8080/templates"

# Get specific template
curl -X GET "http://localhost:8080/templates/{template_id}"

# Create template (requires auth)
curl -X POST "http://localhost:8080/templates" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

- List templates with filters (category, framework_type, visibility)
- Get specific template details
- Create custom template (authenticated)
- Update/delete templates (authenticated)

**Test 10E: Sharing Endpoints**

```bash
# Create share link
curl -X POST "http://localhost:8080/sharing" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"report_id": "...", "expires_in_days": 7}'

# Get share by token
curl -X GET "http://localhost:8080/sharing/token/{token}"

# List shares for report
curl -X GET "http://localhost:8080/sharing/report/{report_id}" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Create share link with expiration
- Access shared report via token
- Verify permissions and access control
- Test link expiration

**Test 10F: Versioning Endpoints**

```bash
# Create version
curl -X POST "http://localhost:8080/versioning" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"report_id": "...", "notes": "..."}'

# Get version history
curl -X GET "http://localhost:8080/versioning/report/{report_id}" \
  -H "X-API-Key: YOUR_API_KEY"

# Compare versions
curl -X GET "http://localhost:8080/versioning/{from_id}/diff/{to_id}" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Create report versions
- View version history
- Compare versions
- Publish/rollback versions

**Test 10G: Comments Endpoints**

```bash
# Create comment
curl -X POST "http://localhost:8080/comments" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"report_id": "...", "content": "..."}'

# List comments
curl -X GET "http://localhost:8080/comments/report/{report_id}" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Create comments on reports
- List comments for a report
- Update/delete comments
- Add reactions to comments

**Test 10H: Community Endpoints**

```bash
# Create case study
curl -X POST "http://localhost:8080/community/case-studies" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'

# List case studies
curl -X GET "http://localhost:8080/community/case-studies?industry=Technology"

# Create best practice
curl -X POST "http://localhost:8080/community/best-practices" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

- Create and list case studies
- Filter by industry/framework
- Create and upvote/downvote best practices
- Publish case studies

**Test 10I: Visualization Endpoints**

```bash
# Generate Porter visualization
curl -X POST "http://localhost:8080/visualizations/porter" \
  -H "Content-Type: application/json" \
  -d '{...porter_data...}'

# Generate SWOT matrix
curl -X POST "http://localhost:8080/visualizations/swot" \
  -H "Content-Type: application/json" \
  -d '{...swot_data...}'
```

- Generate Porter's Five Forces visualization
- Generate SWOT matrix visualization
- Generate from report data

**Test 10J: API Key Management**

```bash
# Create API key
curl -X POST "http://localhost:8080/auth/api-keys" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "...", "description": "..."}'

# List API keys
curl -X GET "http://localhost:8080/auth/api-keys" \
  -H "X-API-Key: YOUR_API_KEY"

# Rotate API key
curl -X POST "http://localhost:8080/auth/api-keys/rotate" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"old_api_key": "...", "description": "..."}'

# Revoke API key
curl -X DELETE "http://localhost:8080/auth/api-keys/{key_hash_prefix}" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Create new API keys
- List all user API keys
- Rotate API keys
- Revoke API keys

**Test 10K: Notifications Endpoints**

```bash
# List notifications
curl -X GET "http://localhost:8080/notifications" \
  -H "X-API-Key: YOUR_API_KEY"

# Mark notification as read
curl -X POST "http://localhost:8080/notifications/{notification_id}/read" \
  -H "X-API-Key: YOUR_API_KEY"

# Mark all notifications as read
curl -X POST "http://localhost:8080/notifications/read-all" \
  -H "X-API-Key: YOUR_API_KEY"

# Delete notification
curl -X DELETE "http://localhost:8080/notifications/{notification_id}" \
  -H "X-API-Key: YOUR_API_KEY"

# Clear all notifications
curl -X POST "http://localhost:8080/notifications/clear-all" \
  -H "X-API-Key: YOUR_API_KEY"

# Get notification settings
curl -X GET "http://localhost:8080/notifications/settings" \
  -H "X-API-Key: YOUR_API_KEY"

# Update notification settings
curl -X PUT "http://localhost:8080/notifications/settings" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"in_app_enabled": true, "email_enabled": false, "email_frequency": "daily"}'
```

- List notifications for authenticated user
- Mark individual notifications as read
- Mark all notifications as read
- Delete individual notifications
- Clear all notifications
- Get and update notification preferences
- **Note**: Notifications feature is partially implemented (returns empty list for now)

**What to Record**:

- Endpoint functionality
- Response format consistency
- Error handling
- Documentation accuracy
- Authentication requirements

---

### Scenario 11: Export Formats Testing

**Objective**: Test different export formats

**Test 11A: PDF Export**

- Generate and download PDF
- Verify formatting
- Check charts render correctly
- Test print compatibility

**Test 11B: JSON Export**

```bash
curl -X GET "http://localhost:8080/reports/{report_id}?format=json" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Verify JSON structure and data completeness
- Check that all report metadata is included
- Validate JSON format is valid and parseable
- Verify framework_analysis data is present (if available)

**Test 11C: Excel Export** (Currently returns 501 Not Implemented)

```bash
curl -X GET "http://localhost:8080/reports/{report_id}?format=excel" \
  -H "X-API-Key: YOUR_API_KEY"
```

- **Note**: Currently returns 501 Not Implemented
- When implemented, verify data organization and formulas

**Test 11D: Word Export** (Currently returns 501 Not Implemented)

```bash
curl -X GET "http://localhost:8080/reports/{report_id}?format=word" \
  -H "X-API-Key: YOUR_API_KEY"
```

- **Note**: Currently returns 501 Not Implemented
- When implemented, verify formatting and editability

**What to Record**:

- Export success rate
- Format quality (for PDF and JSON)
- Data completeness
- File size appropriateness
- JSON structure validation
- Implementation status for Excel and Word formats (still 501 Not Implemented)

---

### Scenario 12: Data Source Reliability

**Objective**: Test integration with external data sources

**Test 12A: Tavily Research**

- Verify web research results
- Check citation quality
- Validate source diversity

**Test 12B: Google Trends**

- Verify trend data inclusion
- Check time range accuracy
- Validate regional data

**Test 12C: Financial Data (SEC/yfinance)**

- Verify financial metrics
- Check data recency
- Validate calculations

**Test 12D: Source Failures**

- Simulate API failures (if possible)
- Verify graceful degradation
- Check fallback mechanisms

**What to Record**:

- Data source reliability
- Citation accuracy
- Data freshness
- Error handling

---

## What to Observe

### During Testing

1. **User Behavior**

   - Where do users hesitate?
   - What questions do they ask?
   - What errors do they encounter?
   - How long do tasks take?

2. **System Behavior**

   - Response times
   - Error messages
   - Loading states
   - Progress indicators

3. **Content Quality**

   - Report accuracy
   - Framework completeness
   - Citation quality
   - Visual clarity

4. **Technical Issues**
   - Bugs or crashes
   - Performance problems
   - Integration failures
   - Data inconsistencies

### Metrics to Track

1. **Performance Metrics**

   - API response time (target: <5s)
   - Analysis completion time (target: 30-60s)
   - Page load time (target: <3s)
   - Error rate (target: <1%)

2. **Usability Metrics**

   - Time to first analysis
   - Number of clicks to complete task
   - Error recovery time
   - User satisfaction score

3. **Quality Metrics**

   - Framework completeness score
   - Citation count per report
   - Confidence score distribution
   - Data recency (target: ≥80% within 12 months)

4. **Business Metrics**
   - Reports generated per session
   - Framework selection patterns
   - Report download rate
   - User retention (if tracking)

---

## Reporting Findings

### Test Report Template

```markdown
# ConsultantOS User Testing Report

**Date**: [Date]
**Tester**: [Name]
**Version**: [Application Version]
**Environment**: [Local/Staging/Production]

## Executive Summary

[2-3 sentence overview of findings]

## Test Scenarios Completed

- [ ] Scenario 1: First-Time User Experience
- [ ] Scenario 2: Basic Analysis Generation
- [ ] Scenario 3: Multi-Framework Analysis
- [ ] Scenario 3B: Async Analysis Processing
- [ ] Scenario 4: Report Retrieval and Management
- [ ] Scenario 5: Framework-Specific Testing
- [ ] Scenario 6: Edge Cases and Error Handling
- [ ] Scenario 7: Performance Testing
- [ ] Scenario 8: Report Quality Assessment
- [ ] Scenario 9: Frontend Dashboard Testing
  - [ ] Test 9A: Authentication & Registration Flow
  - [ ] Test 9B: Dashboard Home Page
  - [ ] Test 9C: Analysis Creation Page
  - [ ] Test 9D: Reports List Page
  - [ ] Test 9E: Report Detail Page
  - [ ] Test 9F: Jobs Queue Page
  - [ ] Test 9G: Templates Page
  - [ ] Test 9H: Profile & Settings Page
  - [ ] Test 9I: Version Comparison Feature
  - [ ] Test 9J: Comments & Notifications
  - [ ] Test 9K: Navigation & Responsive Design
- [ ] Scenario 10: API Integration Testing
- [ ] Scenario 11: Export Formats Testing
- [ ] Scenario 12: Data Source Reliability
- [ ] Scenario 13: Frontend-Backend Integration Testing
- [ ] Scenario 14: Notifications Testing

## Critical Issues

### Issue #1: [Title]

- **Severity**: Critical/High/Medium/Low
- **Description**: [Detailed description]
- **Steps to Reproduce**: [Step-by-step]
- **Expected Behavior**: [What should happen]
- **Actual Behavior**: [What actually happened]
- **Screenshots/Logs**: [Attach evidence]
- **Impact**: [User impact]

## Performance Findings

- API Response Time: [Average, p95, p99]
- Analysis Completion Time: [Average, p95, p99]
- Error Rate: [Percentage]
- [Other metrics]

## Quality Assessment

### Report Quality Scores (1-10)

- Content Quality: [Score] - [Comments]
- Framework Adherence: [Score] - [Comments]
- Data Quality: [Score] - [Comments]
- Visual Quality: [Score] - [Comments]
- Executive Summary: [Score] - [Comments]

### Sample Report Analysis

[Detailed analysis of 1-2 sample reports]

## Usability Findings

- **Strengths**: [What works well]
- **Weaknesses**: [What needs improvement]
- **User Feedback**: [Direct quotes if available]
- **Recommendations**: [Actionable suggestions]

## Edge Cases Tested

[List edge cases and outcomes]

## Recommendations

### Immediate Actions

1. [Priority 1]
2. [Priority 2]

### Future Enhancements

1. [Enhancement 1]
2. [Enhancement 2]

## Appendix

- Test Data Used
- Test Environment Details
- Additional Notes
```

### Severity Classification

- **Critical**: System crash, data loss, security vulnerability
- **High**: Major feature broken, significant performance issue
- **Medium**: Feature works but with limitations, minor performance issue
- **Low**: Cosmetic issue, minor inconvenience

### Reporting Best Practices

1. **Be Specific**: Include exact steps, error messages, screenshots
2. **Be Objective**: Report what happened, not assumptions
3. **Prioritize**: Focus on critical and high-severity issues first
4. **Provide Context**: Include environment, version, test data
5. **Suggest Solutions**: Where possible, suggest fixes or workarounds

---

## Best Practices

### For Testers

1. **Test Realistically**

   - Use real-world scenarios
   - Test with actual consultant use cases
   - Don't just test happy paths

2. **Document Everything**

   - Take screenshots
   - Save API responses
   - Record timestamps
   - Note environment details

3. **Test Across Browsers/Devices**

   - Chrome, Firefox, Safari
   - Desktop and mobile (if applicable)
   - Different screen sizes

4. **Test Error Scenarios**

   - Invalid inputs
   - Network failures
   - Rate limiting
   - Missing data

5. **Validate Quality**
   - Review report content for accuracy
   - Check citations are accessible
   - Verify visualizations are clear
   - Assess professional appearance

### For Test Coordinators

1. **Prepare Test Environment**

   - Ensure all services are running
   - Verify API keys are configured
   - Prepare test data sets
   - Set up monitoring/logging

2. **Recruit Diverse Testers**

   - Different experience levels
   - Various industries
   - Different use cases

3. **Provide Clear Instructions**

   - Share this guide
   - Clarify objectives
   - Set expectations
   - Provide support

4. **Collect Structured Feedback**

   - Use consistent reporting format
   - Set deadlines for reports
   - Follow up on critical issues
   - Aggregate findings

5. **Iterate Based on Findings**
   - Prioritize fixes
   - Re-test after fixes
   - Track improvement
   - Update test scenarios

---

## Appendix

### A. Sample Test Data

**Companies for Testing**:

- Tesla (Electric Vehicles) - Well-known, data-rich
- Netflix (Streaming Media) - Mature industry
- Stripe (Fintech) - B2B, growing
- Local Restaurant Chain - Private, limited data

**Industries for Testing**:

- Technology/SaaS
- Healthcare
- Manufacturing
- Retail/E-commerce
- Professional Services

### B. API Endpoint Reference

**Core Endpoints**:

- `POST /analyze` - Generate analysis (synchronous)
- `POST /analyze/async` - Enqueue analysis job (asynchronous)
- `GET /reports` - List reports (with filters)
- `GET /reports/{report_id}` - Get specific report (with optional format parameter)
- `GET /health` - Health check
- `GET /metrics` - System metrics (requires auth)

**Job Management**:

- `GET /jobs/{job_id}/status` - Get job status
- `GET /jobs` - List jobs (with filters)

**User Management**:

- `POST /users/register` - Create account
- `POST /users/login` - Authenticate (returns `access_token`)
- `GET /users/profile` - Get profile (requires auth)
- `PUT /users/profile` - Update profile (requires auth)
- `POST /users/verify-email` - Verify email address
- `POST /users/password-reset/request` - Request password reset
- `POST /users/password-reset/confirm` - Confirm password reset
- `POST /users/change-password` - Change password (requires auth)

**Authentication & API Keys**:

- `POST /auth/api-keys` - Create API key (requires auth)
- `GET /auth/api-keys` - List API keys (requires auth)
- `POST /auth/api-keys/rotate` - Rotate API key (requires auth)
- `DELETE /auth/api-keys/{key_hash_prefix}` - Revoke API key (requires auth)
- `POST /auth/silent-auth` - Silent authentication check

**Templates**:

- `GET /templates` - List templates (with filters)
- `GET /templates/{template_id}` - Get specific template
- `POST /templates` - Create template (requires auth)
- `PUT /templates/{template_id}` - Update template (requires auth)
- `DELETE /templates/{template_id}` - Delete template (requires auth)

**Sharing**:

- `POST /sharing` - Create share link (requires auth)
- `GET /sharing/report/{report_id}` - List shares for report (requires auth)
- `GET /sharing/token/{token}` - Get share by token (public)
- `DELETE /sharing/{share_id}` - Revoke share (requires auth)

**Versioning**:

- `POST /versioning` - Create report version (requires auth)
- `GET /versioning/report/{report_id}` - Get version history (requires auth)
- `GET /versioning/{version_id}` - Get specific version (requires auth)
- `POST /versioning/{version_id}/publish` - Publish version (requires auth)
- `POST /versioning/{version_id}/rollback` - Rollback to version (requires auth)
- `GET /versioning/{from_id}/diff/{to_id}` - Compare versions (requires auth)
- `POST /versioning/{version_id}/branch` - Create branch (requires auth)

**Comments**:

- `POST /comments` - Create comment (requires auth)
- `GET /comments/report/{report_id}` - List comments for report (requires auth)
- `PUT /comments/{comment_id}` - Update comment (requires auth)
- `DELETE /comments/{comment_id}` - Delete comment (requires auth)
- `POST /comments/{comment_id}/react` - Add reaction (requires auth)

**Community**:

- `POST /community/case-studies` - Create case study (requires auth)
- `GET /community/case-studies` - List case studies (with filters)
- `GET /community/case-studies/{case_study_id}` - Get case study
- `PUT /community/case-studies/{case_study_id}` - Update case study (requires auth)
- `POST /community/case-studies/{case_study_id}/like` - Like case study (requires auth)
- `POST /community/case-studies/{case_study_id}/publish` - Publish case study (requires auth)
- `POST /community/best-practices` - Create best practice (requires auth)
- `GET /community/best-practices` - List best practices (with filters)
- `POST /community/best-practices/{practice_id}/upvote` - Upvote practice (requires auth)
- `POST /community/best-practices/{practice_id}/downvote` - Downvote practice (requires auth)

**Visualizations**:

- `POST /visualizations/porter` - Generate Porter's Five Forces chart
- `POST /visualizations/swot` - Generate SWOT matrix
- `POST /visualizations/porter/from-report` - Generate Porter chart from report
- `POST /visualizations/swot/from-report` - Generate SWOT chart from report

**Analytics**:

- `GET /analytics/shares/{share_id}` - Get share analytics (requires auth)
- `GET /analytics/reports/{report_id}` - Get report analytics (requires auth)

**Notifications**:

- `GET /notifications` - List notifications (requires auth)
- `POST /notifications/{notification_id}/read` - Mark notification as read (requires auth)
- `POST /notifications/read-all` - Mark all notifications as read (requires auth)
- `DELETE /notifications/{notification_id}` - Delete notification (requires auth)
- `POST /notifications/clear-all` - Clear all notifications (requires auth)
- `GET /notifications/settings` - Get notification settings (requires auth)
- `PUT /notifications/settings` - Update notification settings (requires auth)

### C. Common Issues and Solutions

**Issue**: API key not working

- **Solution**: Verify key is correctly set in header (`X-API-Key`) or query param (`?api_key=`)
- **Check**: Key format, expiration, permissions
- **Note**: Login endpoint returns `access_token` in response - use this as your API key

**Issue**: Analysis taking too long

- **Solution**: Check API rate limits, server resources
- **Check**: Network connectivity, external API status

**Issue**: Report quality is low

- **Solution**: Verify data sources are accessible
- **Check**: API keys for Tavily, Gemini, etc.

**Issue**: PDF not downloading

- **Solution**: Check storage service configuration
- **Check**: Signed URL expiration, permissions

### D. Quality Checklist

Use this checklist when reviewing reports:

- [ ] Executive summary is present and concise
- [ ] All requested frameworks are included
- [ ] Each framework has substantial content
- [ ] Citations are present and accessible
- [ ] Visualizations are clear and relevant
- [ ] Confidence scores are reasonable
- [ ] Data appears recent (within 12 months)
- [ ] Report formatting is professional
- [ ] No obvious errors or inconsistencies
- [ ] Content is relevant to company/industry

### E. Performance Benchmarks

**Target Metrics**:

- API Response: <5 seconds (p95)
- Analysis Completion: 30-60 seconds (p95)
- Error Rate: <1%
- Uptime: ≥99%

**Acceptable Ranges**:

- API Response: 1-10 seconds
- Analysis Completion: 20-90 seconds
- Error Rate: 0-2%
- Uptime: 95-100%

### F. Contact and Support

**For Technical Issues**:

- Check logs for any reported errors.
- Review API docs: `http://localhost:8080/docs`
- Check GitHub issues (if applicable)

**For Testing Questions**:

- Refer to this guide
- Review [Product Strategy & Technical Design](docs/PRODUCT_STRATEGY.md)
- Check [Implementation History](docs/IMPLEMENTATION_HISTORY.md)
- Review [API Documentation](API_Documentation.md)

---

### Scenario 14: Notifications Testing

**Objective**: Test notification system functionality

**Test 14A: Notification Listing**

1. Generate a report or create a comment on a shared report
2. List notifications via API
3. Verify notification structure (id, type, title, message, read status, link)
4. Check filtering by user_id (if authenticated)

**API Request**:

```bash
curl -X GET "http://localhost:8080/notifications" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Results**:

- Notifications list returns (may be empty if feature not fully implemented)
- Response includes count and notifications array
- Notifications have proper structure

**Test 14B: Notification Actions**

1. Mark a notification as read
2. Mark all notifications as read
3. Delete a notification
4. Clear all notifications

**API Requests**:

```bash
# Mark as read
curl -X POST "http://localhost:8080/notifications/{notification_id}/read" \
  -H "X-API-Key: YOUR_API_KEY"

# Mark all as read
curl -X POST "http://localhost:8080/notifications/read-all" \
  -H "X-API-Key: YOUR_API_KEY"

# Delete notification
curl -X DELETE "http://localhost:8080/notifications/{notification_id}" \
  -H "X-API-Key: YOUR_API_KEY"

# Clear all
curl -X POST "http://localhost:8080/notifications/clear-all" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Results**:

- Actions return success responses
- Read status updates correctly
- Notifications are deleted as expected

**Test 14C: Notification Settings**

1. Get current notification settings
2. Update notification preferences
3. Verify settings persist

**API Requests**:

```bash
# Get settings
curl -X GET "http://localhost:8080/notifications/settings" \
  -H "X-API-Key: YOUR_API_KEY"

# Update settings
curl -X PUT "http://localhost:8080/notifications/settings" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "in_app_enabled": true,
    "email_enabled": false,
    "email_frequency": "daily"
  }'
```

**Expected Results**:

- Settings are retrieved correctly
- Settings can be updated
- Settings persist across sessions

**What to Record**:

- Notification feature implementation status
- API response structure
- Action success rates
- Settings persistence
- Error handling for invalid operations

**Note**: The notifications feature is currently partially implemented. The endpoints exist and return appropriate responses, but notification storage and retrieval may not be fully functional yet. This is expected behavior for a feature in development.

---

### Scenario 13: Frontend-Backend Integration Testing

**Objective**: Verify seamless integration between frontend UI and backend API

**Test 13A: End-to-End Analysis Flow**

1. **Frontend to Backend**

   - Create analysis via frontend form (`/analysis`)
   - Verify API request sent correctly
   - Check request payload matches form inputs
   - Verify authentication header included (if logged in)

2. **Backend Response Handling**

   - Verify frontend handles success response
   - Check loading states during processing
   - Verify error handling for API failures
   - Test timeout handling for long-running analyses

3. **Real-time Updates**
   - For async jobs, verify status polling works
   - Check job status updates in UI
   - Verify completion triggers report display
   - Test error state display for failed jobs

**Test 13B: Data Synchronization**

1. **Report List Sync**

   - Create report via API
   - Verify appears in frontend reports list
   - Create report via frontend
   - Verify appears in API reports list
   - Test filtering/sorting consistency

2. **User Session Sync**

   - Login via API, verify frontend recognizes session
   - Login via frontend, verify API recognizes auth
   - Test logout clears both frontend and backend sessions

3. **State Management**
   - Verify localStorage syncs with backend
   - Test offline/online state handling
   - Check data refresh after network reconnection

**Test 13C: Error Handling Integration**

1. **API Error Display**

   - Trigger API error (invalid input, rate limit, etc.)
   - Verify frontend displays appropriate error message
   - Check error formatting is user-friendly
   - Test error recovery flows

2. **Network Error Handling**

   - Simulate network failure
   - Verify graceful error message
   - Test retry functionality
   - Check offline state handling

3. **Validation Consistency**
   - Test frontend validation matches backend
   - Verify error messages are consistent
   - Test edge cases handled on both sides

**Test 13D: Performance Integration**

1. **Loading States**

   - Verify loading indicators during API calls
   - Check skeleton screens for data loading
   - Test progress indicators for long operations
   - Verify no UI freezing during API calls

2. **Caching Behavior**

   - Verify frontend caches API responses appropriately
   - Test cache invalidation on updates
   - Check stale data handling
   - Verify optimistic updates (if implemented)

3. **Optimization**
   - Test lazy loading of data
   - Verify pagination reduces load
   - Check debouncing of search/filter inputs
   - Test request batching (if applicable)

**What to Record**:

- API request/response accuracy
- Error handling consistency
- Performance bottlenecks
- Data synchronization issues
- User experience during API calls
- Network error recovery

---

## Version History

- **v1.0** (January 2025): Initial user testing guide created
- **v1.1** (January 2025): Updated with consolidated documentation references and new features
- **v1.2** (January 2025): Updated with async job processing, new API endpoints (templates, sharing, versioning, comments, community, analytics, visualizations, auth), corrected authentication flow, and export format status
- **v1.3** (January 2025): Comprehensive frontend testing scenarios added (Scenario 9 expanded with 11 sub-tests covering all pages and features), new frontend-backend integration testing scenario (Scenario 13), enhanced navigation and responsive design testing
- **v1.4** (January 2025): Updated JSON export status (now implemented), added notifications endpoints and testing scenario (Scenario 14), updated health check to include worker status, corrected export format implementation status

---

**Last Updated**: January 2025  
**Current Version**: 0.3.0 (Backend API), 0.4.0 (Frontend)

**Note**: The backend API version is 0.3.0 (as shown in `/health` endpoint), though the FastAPI app metadata shows 0.1.0. JSON export is now implemented and returns report metadata. Excel and Word exports still return 501 Not Implemented and are planned for future releases. The notifications feature endpoints are available but the storage/retrieval functionality is partially implemented (returns empty lists for now). The frontend includes comprehensive pages for dashboard, analysis creation, reports management, jobs queue, templates, profile settings, and detailed report views with version comparison, comments, and sharing features.
