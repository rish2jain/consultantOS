# ConsultantOS - User Testing Guide

## Table of Contents

1. [Overview](#overview)
2. [Pre-Testing Setup](#pre-testing-setup)
3. [Test Scenarios](#test-scenarios)
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

2. **Frontend Dashboard** (if testing UI)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Required Environment Variables**

   ```bash
   export TAVILY_API_KEY=your_tavily_key
   export GEMINI_API_KEY=your_gemini_key
   ```

4. **API Access**
   - API Base URL: `http://localhost:8080`
   - Swagger UI: `http://localhost:8080/docs`
   - Frontend: `http://localhost:3000` (if applicable)

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

3. **Save API Key** for subsequent requests

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

**Objective**: Test the web interface (if available)

**Test 9A: Login Flow**

1. Access dashboard URL
2. Enter credentials
3. Verify successful login
4. Check session persistence

**Test 9B: Dashboard Display**

1. Verify metrics cards display correctly
2. Check reports table loads
3. Verify status indicators
4. Test responsive design

**Test 9C: Report Generation via UI**

1. Find "Create Analysis" button/form
2. Fill in required fields
3. Submit and monitor progress
4. Download completed report

**Test 9D: Navigation**

1. Test all menu items
2. Verify breadcrumbs (if present)
3. Check back button behavior
4. Test logout functionality

**What to Record**:

- UI clarity and intuitiveness
- Number of clicks to complete tasks
- Visual design quality
- Responsive behavior
- Error message display

---

### Scenario 10: API Integration Testing

**Objective**: Test API endpoints comprehensively

**Test 10A: Health Check**

```bash
curl http://localhost:8080/health
```

- Expected: Status "healthy", version info

**Test 10B: Authentication**

- Test with valid API key
- Test with invalid API key
- Test with missing API key
- Verify error responses

**Test 10C: Analytics Endpoints**

```bash
curl -X GET "http://localhost:8080/metrics" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Verify metrics accuracy
- Check cache hit rate
- Validate execution time averages

**Test 10D: Template Endpoints** (if available)

- List templates
- Get specific template
- Create custom template
- Update template

**Test 10E: Sharing Endpoints** (if available)

- Create share link
- Access shared report
- Verify permissions
- Test link expiration

**What to Record**:

- Endpoint functionality
- Response format consistency
- Error handling
- Documentation accuracy

---

### Scenario 11: Export Formats Testing

**Objective**: Test different export formats

**Test 11A: PDF Export**

- Generate and download PDF
- Verify formatting
- Check charts render correctly
- Test print compatibility

**Test 11B: JSON Export** (if available)

```bash
curl -X GET "http://localhost:8080/reports/{report_id}/export?format=json" \
  -H "X-API-Key: YOUR_API_KEY"
```

- Verify JSON structure
- Check data completeness

**Test 11C: Excel Export** (if available)

- Download Excel file
- Verify data organization
- Check formulas (if any)

**Test 11D: Word Export** (if available)

- Download Word document
- Verify formatting
- Check editability

**What to Record**:

- Export success rate
- Format quality
- Data completeness
- File size appropriateness

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
- [ ] ... (list all completed)

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

- `POST /analyze` - Generate analysis
- `GET /reports` - List reports
- `GET /reports/{report_id}` - Get specific report
- `GET /health` - Health check
- `GET /metrics` - System metrics

**User Management**:

- `POST /users/register` - Create account
- `POST /users/login` - Authenticate
- `GET /users/profile` - Get profile

**Additional Endpoints**:

- `GET /templates` - List templates
- `POST /sharing` - Create share link
- `GET /community/case-studies` - Browse case studies

### C. Common Issues and Solutions

**Issue**: API key not working

- **Solution**: Verify key is correctly set in header or query param
- **Check**: Key format, expiration, permissions

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

- Check logs: `consultantos/monitoring.py`
- Review API docs: `http://localhost:8080/docs`
- Check GitHub issues (if applicable)

**For Testing Questions**:

- Refer to this guide
- Review [Product Strategy & Technical Design](docs/PRODUCT_STRATEGY.md)
- Check [Implementation History](docs/IMPLEMENTATION_HISTORY.md)
- Review [API Documentation](API_Documentation.md)

---

## Version History

- **v1.0** (January 2025): Initial user testing guide created
- **v1.1** (January 2025): Updated with consolidated documentation references and new features

---

**Last Updated**: January 2025  
**Current Version**: 0.3.0 (Backend), 0.4.0 (Frontend)
