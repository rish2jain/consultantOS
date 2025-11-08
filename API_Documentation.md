# ConsultantOS - API Documentation

**Version**: 0.3.0  
**Base URL**: `http://localhost:8080` (development) or your Cloud Run URL (production)  
**API Documentation**: Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [Report Management](#report-management)
4. [User Management](#user-management)
5. [Templates](#templates)
6. [Sharing & Collaboration](#sharing--collaboration)
7. [Versioning](#versioning)
8. [Comments](#comments)
9. [Community](#community)
10. [Analytics](#analytics)
11. [Job Queue](#job-queue)
12. [Error Handling](#error-handling)
13. [Rate Limiting](#rate-limiting)

---

## Authentication

### API Key Authentication

Most endpoints support optional API key authentication via:

- **Header**: `X-API-Key: your_api_key_here`
- **Query Parameter**: `?api_key=your_api_key_here`

**Note**: Some endpoints require authentication, while others are optional. Check individual endpoint documentation.

### Get API Key

```bash
POST /auth/api-keys
```

Create a new API key (requires authentication).

**Response**:
```json
{
  "api_key": "sk_live_...",
  "description": "My API Key",
  "created_at": "2024-01-01T12:00:00"
}
```

### List API Keys

```bash
GET /auth/api-keys
```

List all API keys for the authenticated user.

---

## Core Endpoints

### Generate Analysis

```bash
POST /analyze
```

Generate strategic analysis report for a company.

**Authentication**: Optional  
**Rate Limit**: 10 requests/hour per IP

**Request Body**:
```json
{
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
  "depth": "standard"
}
```

**Parameters**:
- `company` (string, required): Company name or ticker symbol
- `industry` (string, optional): Industry sector (auto-detected if not provided)
- `frameworks` (array, optional): List of frameworks to apply. Options: `porter`, `swot`, `pestel`, `blue_ocean`. Default: all frameworks
- `depth` (string, optional): Analysis depth. Options: `quick`, `standard`, `deep`. Default: `standard`

**Response**:
```json
{
  "status": "success",
  "report_id": "Tesla_20240101120000",
  "report_url": "https://storage.googleapis.com/...",
  "executive_summary": {
    "company_name": "Tesla",
    "industry": "Electric Vehicles",
    "key_findings": [
      "Strong competitive position in EV market",
      "High supplier power due to vertical integration"
    ],
    "strategic_recommendation": "Focus on international expansion...",
    "confidence_score": 0.85
  },
  "execution_time_seconds": 45.2
}
```

**Response Time**: 30-60 seconds (may timeout for complex analyses)

### Generate Analysis (Async)

```bash
POST /analyze/async
```

Enqueue analysis job for asynchronous processing.

**Authentication**: Optional  
**Rate Limit**: 10 requests/hour per IP

**Request Body**: Same as `/analyze`

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "status_url": "/jobs/550e8400-e29b-41d4-a716-446655440000/status",
  "estimated_completion": "2-5 minutes"
}
```

### Health Check

```bash
GET /health
```

Check system health status.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "timestamp": "2024-01-01T12:00:00",
  "cache": {
    "disk_cache_initialized": true,
    "semantic_cache_available": true
  },
  "storage": {
    "available": true
  },
  "database": {
    "available": true,
    "type": "firestore"
  }
}
```

### System Metrics

```bash
GET /metrics
```

Get system performance metrics.

**Authentication**: Required

**Response**:
```json
{
  "metrics": {
    "total_requests": 1250,
    "cache_hits": 450,
    "cache_misses": 800,
    "average_execution_time": 42.3,
    "error_rate": 0.02
  },
  "summary": {
    "api_success_rates": {
      "tavily": 98.5,
      "yfinance": 99.2
    },
    "circuit_breaker_states": {
      "tavily_api": "closed"
    },
    "job_queue_status": {
      "pending": 5,
      "processing": 2
    },
    "total_api_cost": 0.045,
    "active_users": 12
  }
}
```

---

## Report Management

### Get Report

```bash
GET /reports/{report_id}
```

Retrieve a generated report by ID.

**Authentication**: Optional (required for private reports)

**Response**:
```json
{
  "report_id": "Tesla_20240101120000",
  "report_url": "https://storage.googleapis.com/...",
  "metadata": {
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"],
    "created_at": "2024-01-01T12:00:00",
    "execution_time_seconds": 45.2,
    "confidence_score": 0.85
  },
  "status": "completed"
}
```

### List Reports

```bash
GET /reports
```

List all reports with optional filtering.

**Authentication**: Required

**Query Parameters**:
- `company` (string, optional): Filter by company name
- `industry` (string, optional): Filter by industry
- `status` (string, optional): Filter by status (`pending`, `completed`, `failed`)
- `limit` (integer, optional): Maximum number of results (default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response**:
```json
{
  "reports": [
    {
      "report_id": "Tesla_20240101120000",
      "company": "Tesla",
      "industry": "Electric Vehicles",
      "created_at": "2024-01-01T12:00:00",
      "status": "completed"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

### Export Report

```bash
GET /reports/{report_id}/export
```

Export report in different formats.

**Authentication**: Optional

**Query Parameters**:
- `format` (string, required): Export format. Options: `json`, `excel`, `word`, `pdf` (default)

**Response**: File download (content-type varies by format)

---

## User Management

### Register User

```bash
POST /users/register
```

Create a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "name": "John Doe"
}
```

**Response**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "message": "Registration successful. Please check your email for verification."
}
```

### Login

```bash
POST /users/login
```

Authenticate user and get API key.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response**:
```json
{
  "api_key": "sk_live_...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

### Get User Profile

```bash
GET /users/profile
```

Get authenticated user's profile.

**Authentication**: Required

**Response**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "email_verified": true,
  "created_at": "2024-01-01T12:00:00"
}
```

### Update User Profile

```bash
PUT /users/profile
```

Update authenticated user's profile.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "John Smith",
  "email": "newemail@example.com"
}
```

---

## Templates

### List Templates

```bash
GET /templates
```

List available templates.

**Query Parameters**:
- `category` (string, optional): Filter by category
- `framework_type` (string, optional): Filter by framework type
- `visibility` (string, optional): Filter by visibility (`public`, `private`, `shared`)
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20)

### Get Template

```bash
GET /templates/{template_id}
```

Get template details.

### Create Template

```bash
POST /templates
```

Create a new template.

**Authentication**: Required

**Request Body**:
```json
{
  "name": "Custom Porter Analysis",
  "description": "Custom Porter's 5 Forces template",
  "category": "porter",
  "framework_type": "porter",
  "content": {...},
  "visibility": "private"
}
```

### Update Template

```bash
PUT /templates/{template_id}
```

Update an existing template.

**Authentication**: Required (must own template)

### Delete Template

```bash
DELETE /templates/{template_id}
```

Delete a template.

**Authentication**: Required (must own template)

---

## Sharing & Collaboration

### Create Share

```bash
POST /sharing
```

Create a shareable link for a report.

**Authentication**: Required

**Request Body**:
```json
{
  "report_id": "Tesla_20240101120000",
  "permission": "view",
  "expires_at": "2024-02-01T12:00:00"
}
```

**Response**:
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "token": "abc123...",
  "share_url": "https://app.consultantos.com/sharing/abc123...",
  "permission": "view",
  "expires_at": "2024-02-01T12:00:00"
}
```

### Get Share

```bash
GET /sharing/token/{token}
```

Get share details by token (public access).

### List Shares

```bash
GET /sharing/report/{report_id}
```

List all shares for a report.

**Authentication**: Required (must own report)

### Revoke Share

```bash
DELETE /sharing/{share_id}
```

Revoke a share.

**Authentication**: Required (must own share)

---

## Versioning

### Create Version

```bash
POST /versions
```

Create a new version of a report.

**Authentication**: Required

**Request Body**:
```json
{
  "report_id": "Tesla_20240101120000",
  "change_summary": "Updated Porter analysis with latest market data"
}
```

### Get Version History

```bash
GET /versions/report/{report_id}
```

Get version history for a report.

**Authentication**: Required (must own report)

### Get Version

```bash
GET /versions/{version_id}
```

Get specific version details.

### Compare Versions

```bash
GET /versions/{from_id}/diff/{to_id}
```

Compare two versions and get diff.

**Authentication**: Required

### Rollback to Version

```bash
POST /versions/{version_id}/rollback
```

Create a new version from an old version (rollback).

**Authentication**: Required

---

## Comments

### Create Comment

```bash
POST /comments
```

Add a comment to a report.

**Authentication**: Required

**Request Body**:
```json
{
  "report_id": "Tesla_20240101120000",
  "content": "Great analysis! Consider adding more data on supplier relationships.",
  "parent_comment_id": null
}
```

### List Comments

```bash
GET /comments/report/{report_id}
```

Get all comments for a report.

**Authentication**: Optional

### Update Comment

```bash
PUT /comments/{comment_id}
```

Update a comment.

**Authentication**: Required (must own comment)

### Delete Comment

```bash
DELETE /comments/{comment_id}
```

Delete a comment.

**Authentication**: Required (must own comment)

### Add Reaction

```bash
POST /comments/{comment_id}/react
```

Add a reaction to a comment.

**Authentication**: Required

**Request Body**:
```json
{
  "reaction": "👍"
}
```

---

## Community

### Create Case Study

```bash
POST /community/case-studies
```

Publish a case study.

**Authentication**: Required

**Request Body**:
```json
{
  "title": "How ConsultantOS Helped Win a $500K Engagement",
  "description": "Case study description...",
  "industry": "Technology",
  "framework": "porter",
  "content": {...}
}
```

### List Case Studies

```bash
GET /community/case-studies
```

List published case studies.

**Query Parameters**:
- `industry` (string, optional): Filter by industry
- `framework` (string, optional): Filter by framework
- `category` (string, optional): Filter by category
- `status` (string, optional): Filter by status (`draft`, `published`)
- `page` (integer, optional): Page number
- `page_size` (integer, optional): Items per page

### Get Case Study

```bash
GET /community/case-studies/{id}
```

Get case study details.

### Like Case Study

```bash
POST /community/case-studies/{id}/like
```

Like a case study.

**Authentication**: Required

### Create Best Practice

```bash
POST /community/best-practices
```

Share a best practice.

**Authentication**: Required

### List Best Practices

```bash
GET /community/best-practices
```

List best practices.

### Vote on Best Practice

```bash
POST /community/best-practices/{id}/upvote
POST /community/best-practices/{id}/downvote
```

Vote on a best practice.

**Authentication**: Required

---

## Analytics

### Get Share Analytics

```bash
GET /analytics/shares/{share_id}
```

Get analytics for a specific share.

**Authentication**: Required (must own share)

**Response**:
```json
{
  "share_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_accesses": 45,
  "unique_visitors": 12,
  "accesses_by_date": {...},
  "last_accessed": "2024-01-15T10:30:00"
}
```

### Get Report Analytics

```bash
GET /analytics/reports/{report_id}
```

Get analytics for a report (aggregates all shares).

**Authentication**: Required (must own report)

**Response**:
```json
{
  "report_id": "Tesla_20240101120000",
  "total_shares": 3,
  "total_accesses": 125,
  "unique_visitors": 45,
  "comment_count": 8,
  "share_breakdown": {...}
}
```

---

## Job Queue

### Get Job Status

```bash
GET /jobs/{job_id}/status
```

Get status of an async job.

**Authentication**: Optional

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "report_id": "Tesla_20240101120000",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:01:30",
  "progress": 100
}
```

**Status Values**: `pending`, `processing`, `completed`, `failed`

### List Jobs

```bash
GET /jobs
```

List jobs with optional filtering.

**Authentication**: Required

**Query Parameters**:
- `status` (string, optional): Filter by status
- `limit` (integer, optional): Maximum results (default: 50)

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `AUTHENTICATION_REQUIRED`: API key required
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `PERMISSION_DENIED`: Insufficient permissions
- `ANALYSIS_FAILED`: Analysis generation failed
- `TIMEOUT`: Request timed out

---

## Rate Limiting

### Limits

- **Default**: 10 requests/hour per IP address
- **Authenticated Users**: Higher limits based on tier
- **Rate Limit Headers**: Included in all responses

### Rate Limit Headers

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 5
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response:

```json
{
  "detail": "Rate limit exceeded: 10 requests per hour",
  "retry_after": 3600
}
```

Wait for the `retry_after` seconds before making another request.

---

## Examples

### Complete Workflow Example

```bash
# 1. Register a user
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
  }'

# 2. Login to get API key
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# 3. Generate analysis (async)
curl -X POST "http://localhost:8080/analyze/async" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_..." \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'

# 4. Check job status
curl "http://localhost:8080/jobs/{job_id}/status" \
  -H "X-API-Key: sk_live_..."

# 5. Get report when completed
curl "http://localhost:8080/reports/{report_id}" \
  -H "X-API-Key: sk_live_..."

# 6. Share report
curl -X POST "http://localhost:8080/sharing" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_..." \
  -d '{
    "report_id": "Tesla_20240101120000",
    "permission": "view"
  }'
```

---

## Interactive Documentation

For interactive API documentation with "Try it out" functionality:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

Both provide:
- Complete endpoint documentation
- Request/response schemas
- Authentication testing
- Direct API calls from the browser

---

## Additional Resources

- **Interactive API Docs**: Visit `/docs` (Swagger UI) or `/redoc` (ReDoc) when the server is running
- **Frontend Dashboard**: See [frontend/README.md](../frontend/README.md) for dashboard setup
- **Product Documentation**: See [docs/PRODUCT_STRATEGY.md](docs/PRODUCT_STRATEGY.md) for product vision and architecture
- **Implementation History**: See [docs/IMPLEMENTATION_HISTORY.md](docs/IMPLEMENTATION_HISTORY.md) for development history

---

**Last Updated**: January 2025  
**API Version**: 0.3.0  
**Backend Version**: 0.3.0  
**Frontend Version**: 0.4.0
