# ConsultantOS - User Testing Guide (Hackathon Demo)

**Version**: 1.0.0-hackathon
**Last Updated**: 2025-11-08
**Status**: Demo-Ready

## Overview

This guide provides testing scenarios for ConsultantOS hackathon demonstration. The focus is on core multi-agent analysis features that are currently enabled and working.

### What's Enabled for Testing ✅

- Multi-agent strategic analysis (5 agents)
- Business framework analysis (Porter, SWOT, PESTEL, Blue Ocean)
- Async job processing
- PDF report generation
- Multiple export formats (PDF, JSON)
- Health checks and monitoring
- User registration and authentication
- API key management

### What's Disabled for Hackathon ⚠️

The following features exist in the codebase but are disabled for demo simplicity:

- Dashboard endpoints
- Continuous monitoring
- Team collaboration
- Knowledge base
- Custom frameworks
- Saved searches
- Email digests

## Quick Setup

### Prerequisites

1. **Backend Setup**

   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Set API keys
   export GEMINI_API_KEY="your-gemini-key"
   export TAVILY_API_KEY="your-tavily-key"

   # Start server
   python main.py
   ```

2. **Access Points**
   - API: http://localhost:8080
   - Swagger UI: http://localhost:8080/docs
   - ReDoc: http://localhost:8080/redoc

### Test Account Setup

```bash
# Register test user
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@consultantos.com",
    "password": "SecurePass123!",
    "name": "Test User"
  }'

# Login and get API key
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@consultantos.com",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from login response for subsequent requests.

## Core Test Scenarios

### Scenario 1: Basic Analysis Generation ⏱️ 30 seconds

**Objective**: Generate a strategic analysis with 2 frameworks

**Steps**:

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

**Expected Results**:

- ✅ API responds within 5 seconds
- ✅ Analysis completes in 20-40 seconds
- ✅ Response includes:
  - `report_id`
  - `confidence_score` (0.0-1.0)
  - Framework analyses (Porter's Five Forces, SWOT)
  - Executive summary
  - PDF download URL

**What to Record**:

- Total time from request to completion
- Confidence score
- Quality of framework analysis
- Presence of data citations

---

### Scenario 2: Comprehensive Multi-Framework Analysis ⏱️ 60 seconds

**Objective**: Test all 4 frameworks simultaneously

**Steps**:

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "OpenAI",
    "industry": "Artificial Intelligence",
    "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
    "analysis_depth": "deep"
  }'
```

**Expected Results**:

- ✅ All 4 frameworks included
- ✅ Each framework has substantial content:
  - **Porter**: All 5 forces analyzed
  - **SWOT**: All 4 quadrants populated
  - **PESTEL**: All 6 factors covered
  - **Blue Ocean**: Value innovation opportunities identified
- ✅ Executive summary synthesizes all frameworks
- ✅ Completion time 50-90 seconds

**What to Record**:

- Framework completeness (each framework scored 1-10)
- Cross-framework consistency
- Data recency (% of citations within 12 months)
- Professional report formatting

---

### Scenario 3: Async Job Processing ⏱️ 5 minutes

**Objective**: Test asynchronous job queue for long-running analyses

**Steps**:

1. **Enqueue Job**

   ```bash
   curl -X POST "http://localhost:8080/analyze/async" \
     -H "Content-Type: application/json" \
     -d '{
       "company": "SpaceX",
       "industry": "Aerospace",
       "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
       "analysis_depth": "deep"
     }'
   ```

   Expected response:

   ```json
   {
     "job_id": "550e8400-...",
     "status": "pending",
     "status_url": "/jobs/550e8400-.../status"
   }
   ```

2. **Check Job Status**

   ```bash
   # Poll status (repeat until completed)
   curl "http://localhost:8080/jobs/{job_id}/status"
   ```

   Status progression:

   - `pending` → `processing` → `completed` or `failed`

3. **Retrieve Completed Report**
   ```bash
   # Once status is "completed"
   curl "http://localhost:8080/reports/{report_id}"
   ```

**Expected Results**:

- ✅ Job enqueued immediately (< 1 second)
- ✅ Status updates correctly
- ✅ Job completes within 2-5 minutes
- ✅ Report accessible after completion

**What to Record**:

- Time from enqueue to completion
- Status polling frequency needed
- Error handling if job fails

---

### Scenario 4: Export Formats Testing ⏱️ 10 seconds

**Objective**: Test different report export formats

**Test 4A: PDF Export**

```bash
curl "http://localhost:8080/reports/{report_id}/pdf" -o report.pdf
```

Expected:

- ✅ Professional PDF formatting
- ✅ Charts and visualizations render correctly
- ✅ Clickable table of contents
- ✅ Citations included

**Test 4B: JSON Export**

```bash
curl "http://localhost:8080/reports/{report_id}/export?format=json" -o report.json
```

Expected:

- ✅ Valid JSON structure
- ✅ All metadata included
- ✅ Framework data properly structured

**Test 4C: Excel Export**

```bash
curl "http://localhost:8080/reports/{report_id}/export?format=excel" -o report.xlsx
```

Expected:

- ✅ Data organized in worksheets
- ✅ Framework data in separate sheets
- ✅ Charts included

**Test 4D: Word Export**

```bash
curl "http://localhost:8080/reports/{report_id}/export?format=word" -o report.docx
```

Expected:

- ✅ Editable document format
- ✅ Professional formatting preserved
- ✅ Charts embedded

**What to Record**:

- Export success rate for each format
- File sizes
- Data completeness
- Visual quality (PDF charts)

---

### Scenario 5: Health and Monitoring ⏱️ 2 seconds

**Objective**: Verify system health endpoints

**Steps**:

```bash
# Health check
curl "http://localhost:8080/health"

# Readiness check
curl "http://localhost:8080/health/ready"

# Liveness check
curl "http://localhost:8080/health/live"
```

**Expected Results**:

- ✅ Health check returns `{"status": "healthy"}`
- ✅ Readiness check indicates services ready
- ✅ Liveness check confirms API is responsive
- ✅ Response time < 1 second

**What to Record**:

- Service availability status
- Response times
- Any warnings in health check

---

### Scenario 6: Edge Cases and Error Handling

**Test 6A: Missing Required Fields**

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company": ""}'
```

Expected: `400 Bad Request` with clear error message

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

Expected: `422 Validation Error` listing valid frameworks

**Test 6C: Private Company (Limited Data)**

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Local Small Business",
    "industry": "Services",
    "frameworks": ["swot"]
  }'
```

Expected:

- ✅ Graceful handling with proxy/industry data
- ✅ Lower confidence score
- ✅ Clear labeling of data limitations

**Test 6D: Rate Limiting**

Submit 11 requests rapidly (default limit: 10/hour):

Expected: 11th request returns `429 Too Many Requests`

**What to Record**:

- Error message clarity
- HTTP status code correctness
- Helpful guidance for users
- System stability during errors

---

### Scenario 7: Performance Testing

**Test 7A: Response Time Benchmarks**

Run 10 analyses and measure:

- API response time (request to first byte)
- Analysis completion time (total duration)
- Success rate

Target metrics:

- API response: < 5 seconds (p95)
- Completion: 30-60 seconds (p50)
- Success rate: ≥ 99%

**Test 7B: Concurrent Requests**

Submit 3-5 analyses simultaneously:

```bash
# In parallel terminals or script
for i in {1..5}; do
  curl -X POST "http://localhost:8080/analyze/async" \
    -H "Content-Type: application/json" \
    -d "{\"company\": \"Company$i\", \"industry\": \"Tech\", \"frameworks\": [\"swot\"]}" &
done
wait
```

Expected:

- ✅ All requests accepted
- ✅ Jobs processed in parallel
- ✅ No failures due to concurrency

**What to Record**:

- p50, p95, p99 response times
- Success vs failure rate
- Resource usage (if observable)
- Degradation under load

---

### Scenario 8: User Authentication Flow

**Test 8A: Password Validation**

Try registering with weak passwords:

```bash
# Weak password (should fail)
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "weak",
    "name": "Test"
  }'
```

Expected:

- ❌ `400 Bad Request`
- Error message listing password requirements:
  - Minimum 8 characters
  - Uppercase letter
  - Lowercase letter
  - Digit
  - Special character

**Test 8B: Email Verification**

```bash
# Register
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "verify@example.com",
    "password": "SecurePass123!",
    "name": "Test User"
  }'

# Response includes verification_token
# Verify email
curl -X POST "http://localhost:8080/users/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"token": "verification_token_here"}'
```

**Test 8C: Password Reset**

```bash
# Request reset
curl -X POST "http://localhost:8080/users/password-reset/request" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@consultantos.com"}'

# Confirm reset (with token from email)
curl -X POST "http://localhost:8080/users/password-reset/confirm" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "reset_token_here",
    "new_password": "NewSecure123!"
  }'
```

**What to Record**:

- Password validation works correctly
- Email verification flow
- Password reset functionality
- Error messages clarity

---

## Quality Assessment Checklist

Use this checklist when reviewing generated reports:

### Content Quality (Score 1-10)

- [ ] Insights are relevant and accurate
- [ ] Analysis is comprehensive
- [ ] Claims supported by evidence
- [ ] Professional language
- [ ] No obvious errors

### Framework Adherence (Score 1-10)

- [ ] Porter's: All 5 forces analyzed
- [ ] SWOT: All 4 quadrants populated
- [ ] PESTEL: All 6 dimensions covered
- [ ] Blue Ocean: Value curves identified

### Data Quality (Score 1-10)

- [ ] Citations present and accessible
- [ ] Data recent (within 12 months)
- [ ] Sources credible
- [ ] Confidence scores reasonable

### Visual Quality (Score 1-10)

- [ ] Charts clear and readable
- [ ] Visualizations add value
- [ ] Formatting professional
- [ ] PDF rendering consistent

### Executive Summary (Score 1-10)

- [ ] Concise (1 page or less)
- [ ] Captures key insights
- [ ] Actionable recommendations
- [ ] Highlights risks and opportunities

**Overall Quality Score**: \_\_\_ / 50

---

## Test Report Template

```markdown
# ConsultantOS Hackathon Test Report

**Date**: [Date]
**Tester**: [Name]
**Version**: 1.0.0-hackathon
**Environment**: Local/Cloud Run

## Summary

[2-3 sentences summarizing findings]

## Scenarios Tested

- [x] Scenario 1: Basic Analysis
- [x] Scenario 2: Multi-Framework Analysis
- [x] Scenario 3: Async Jobs
- [x] Scenario 4: Export Formats
- [x] Scenario 5: Health Checks
- [x] Scenario 6: Error Handling
- [x] Scenario 7: Performance
- [x] Scenario 8: Authentication

## Performance Metrics

| Metric              | Target | Actual   | Status |
| ------------------- | ------ | -------- | ------ |
| API Response (p95)  | < 5s   | \_\_\_   | ✅/❌  |
| Analysis Time (p50) | 30-60s | \_\_\_   | ✅/❌  |
| Success Rate        | ≥ 99%  | \_\_\_ % | ✅/❌  |
| Error Rate          | < 1%   | \_\_\_ % | ✅/❌  |

## Quality Scores

| Report | Company | Quality | Notes |
| ------ | ------- | ------- | ----- |
| 1      | Tesla   | \_\_/50 |       |
| 2      | OpenAI  | \_\_/50 |       |
| 3      | SpaceX  | \_\_/50 |       |

## Issues Found

### Critical

- [Issue description]

### High

- [Issue description]

### Medium

- [Issue description]

### Low

- [Issue description]

## Recommendations

1. [Priority recommendation]
2. [Priority recommendation]
3. [Enhancement]

## Appendix

- Test data used
- Environment details
- Additional observations
```

---

## Sample Test Companies

Use these for consistent testing:

1. **Tesla** (Electric Vehicles)

   - Well-known, data-rich
   - Good for baseline quality

2. **OpenAI** (Artificial Intelligence)

   - Recent company, active news
   - Tests data recency

3. **SpaceX** (Aerospace)

   - Private company
   - Tests limited data handling

4. **Netflix** (Streaming Media)

   - Mature industry
   - Tests comprehensive analysis

5. **Small Local Business** (Services)
   - Limited public data
   - Tests proxy data usage

---

## Troubleshooting

### Issue: API Won't Start

```bash
# Check environment variables
echo $GEMINI_API_KEY
echo $TAVILY_API_KEY

# Check port availability
lsof -i :8080

# View startup logs
python main.py
```

### Issue: Import Errors

```bash
# Ensure on master branch
git checkout master
git pull

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Issue: Analysis Fails

- Check API keys are valid
- Verify network connectivity
- Check rate limits not exceeded
- Review error message in response

### Issue: Low Quality Reports

- Verify data sources accessible
- Check confidence scores
- Review framework completeness
- Validate citations are working

---

## Performance Benchmarks

### Target Metrics (Hackathon Demo)

| Metric                  | Target | Acceptable | Poor   |
| ----------------------- | ------ | ---------- | ------ |
| API Response            | < 5s   | 5-10s      | > 10s  |
| Analysis (2 frameworks) | 20-40s | 40-60s     | > 60s  |
| Analysis (4 frameworks) | 50-90s | 90-120s    | > 120s |
| Success Rate            | ≥ 99%  | 95-99%     | < 95%  |
| Error Rate              | < 1%   | 1-3%       | > 3%   |

### Comparison to Manual Work

| Task           | Manual    | ConsultantOS | Speedup |
| -------------- | --------- | ------------ | ------- |
| Basic Analysis | 8 hours   | 30 seconds   | 960x    |
| Comprehensive  | 32 hours  | 60 seconds   | 1,920x  |
| Multi-Company  | 160 hours | 5 minutes    | 1,920x  |

---

## Success Criteria

For hackathon demonstration, the system should:

✅ **Functional**

- Generate analyses successfully ≥ 95% of the time
- Complete analyses within target time ranges
- Export reports in multiple formats

✅ **Quality**

- Average quality score ≥ 35/50
- Framework completeness ≥ 90%
- Data recency ≥ 70% within 12 months

✅ **Performance**

- API response < 10 seconds (p95)
- Analysis completion within 2x target times
- Handle 3-5 concurrent requests

✅ **Reliability**

- Graceful error handling
- Clear error messages
- No crashes or data loss

---

## Additional Resources

- **[HACKATHON_GUIDE.md](HACKATHON_GUIDE.md)** - Complete demo setup
- **[README.md](README.md)** - Project overview
- **[API Documentation](API_Documentation.md)** - Full API reference
- **Swagger UI**: http://localhost:8080/docs

---

**Version**: 1.0.0-hackathon
**Last Updated**: 2025-11-08
**Status**: Ready for hackathon demonstration testing
