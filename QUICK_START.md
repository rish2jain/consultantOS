# ConsultantOS - Quick Start Guide

## ✅ Application Status

The application is **ready to run**! All core components have been implemented:

- ✅ 5 Agents (Research, Market, Financial, Framework, Synthesis)
- ✅ 4 Frameworks (Porter's 5 Forces, SWOT, PESTEL, Blue Ocean)
- ✅ PDF Report Generation
- ✅ FastAPI Backend with comprehensive API
- ✅ User Authentication & Management
- ✅ Dashboard UI (Next.js/React)
- ✅ Report Sharing & Collaboration
- ✅ Template Library
- ✅ Report Versioning
- ✅ Comments & Community Features
- ✅ Async Job Processing
- ✅ Rate Limiting & Error Handling
- ✅ Comprehensive Monitoring & Analytics

## 🚀 Running the Application

### Start the Server

```bash
python main.py
```

The API will be available at:

- **API**: `http://localhost:8080`
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### Test the Health Endpoint

```bash
curl http://localhost:8080/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "0.3.0",
  "timestamp": "2025-01-XX...",
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

### Run an Analysis

**Option 1: Synchronous** (quick analyses, waits for completion):

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

**Option 2: Asynchronous** (recommended for complex analyses):

```bash
# Enqueue job
curl -X POST "http://localhost:8080/analyze/async" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot", "pestel", "blue_ocean"]
  }'

# Check job status (use job_id from response)
curl "http://localhost:8080/jobs/{job_id}/status"

# Get report when completed
curl "http://localhost:8080/reports/{report_id}"
```

### User Registration & Authentication (Optional)

For authenticated features (report history, sharing, etc.):

```bash
# Register a new user
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
  }'

# Login to get API key
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Use API key in subsequent requests
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_..." \
  -d '{
    "company": "Tesla",
    "frameworks": ["porter", "swot"]
  }'
```

## 📋 API Endpoints

### POST /analyze

Generate strategic analysis report

**Request:**

```json
{
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
  "depth": "standard"
}
```

**Response:**

```json
{
  "status": "success",
  "report_id": "Tesla_20250101...",
  "report_url": "https://storage.googleapis.com/...",
  "executive_summary": {...},
  "confidence": 0.85,
  "execution_time_seconds": 45.2
}
```

### GET /health

Health check endpoint

### GET /reports/{report_id}

Retrieve a generated report

### POST /analyze/async

Enqueue analysis job for asynchronous processing (recommended for long-running analyses)

### GET /jobs/{job_id}/status

Check status of async job

### POST /users/register

Register a new user account

### POST /users/login

Authenticate and get API key

## 🔑 Required API Keys

Make sure these are set in your environment:

- `TAVILY_API_KEY` - For web research (get at [tavily.com](https://tavily.com))
- `GEMINI_API_KEY` - For AI analysis (get at [Google AI Studio](https://makersuite.google.com/app/apikey))

**Note**: The application uses lazy initialization, so API keys are checked when the first request comes in. You can start the server without keys, but analysis requests will fail until keys are configured.

## 🐛 Troubleshooting

### API Keys Not Found

If you get "GEMINI_API_KEY not found":

- Export in current shell: `export GEMINI_API_KEY=your_key`
- Or create `.env` file with keys
- The app uses lazy initialization, so keys are checked when first request comes in

### Import Errors

- Run: `pip install -r requirements.txt`
- Some packages may need `--no-deps` flag if httpx has issues

### Port Already in Use

- Change port in `main.py`: `uvicorn.run(..., port=8081)`
- Or kill existing process: `lsof -ti:8080 | xargs kill`

## 📊 Architecture

```
Request → FastAPI → Orchestrator
                    ├─ Phase 1 (Parallel)
                    │  ├─ Research Agent (Tavily)
                    │  ├─ Market Agent (Trends)
                    │  └─ Financial Agent (SEC/yfinance)
                    │
                    ├─ Phase 2 (Sequential)
                    │  ├─ Framework Agent (4 frameworks)
                    │  └─ Synthesis Agent (Executive Summary)
                    │
                    └─ PDF Generation (ReportLab + Plotly)
```

## 🎯 Next Steps

1. **Test with a real company**: Try analyzing Tesla, Netflix, or another well-known company
2. **Review PDF output**: Check the generated reports for quality and completeness
3. **Try the Dashboard**: Start the frontend and explore the UI features
4. **Explore API Features**: Test sharing, versioning, comments, and templates
5. **Deploy to Cloud Run**: Use the provided Dockerfile and cloudbuild.yaml
6. **Set up Monitoring**: Configure Cloud Logging and error tracking

## 🔧 Advanced Features

### Report Sharing

```bash
# Create a shareable link
curl -X POST "http://localhost:8080/sharing" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_live_..." \
  -d '{
    "report_id": "Tesla_20240101120000",
    "permission": "view",
    "expires_at": "2024-02-01T12:00:00"
  }'
```

### Export Formats

```bash
# Export as JSON
curl "http://localhost:8080/reports/{report_id}/export?format=json"

# Export as Excel
curl "http://localhost:8080/reports/{report_id}/export?format=excel"

# Export as Word
curl "http://localhost:8080/reports/{report_id}/export?format=word"
```

### View Metrics

```bash
# Get system metrics (requires authentication)
curl "http://localhost:8080/metrics" \
  -H "X-API-Key: sk_live_..."
```

## 🎨 Frontend Dashboard

The application includes a Next.js dashboard for managing reports and viewing analytics:

```bash
cd frontend
npm install
npm run dev
```

Access dashboard at: `http://localhost:3000`

**Features**:

- User authentication (login/registration)
- Report history and management
- Usage statistics and analytics
- API key management
- Report sharing and collaboration

## 📚 Documentation

- **[API Documentation](API_Documentation.md)** - Complete API reference
- **[Setup Guide](SETUP.md)** - Detailed setup instructions
- **[User Testing Guide](USER_TESTING_GUIDE.md)** - Testing procedures
- **[Product Strategy & Technical Design](docs/PRODUCT_STRATEGY.md)** - Product vision and architecture
- **[Implementation History](docs/IMPLEMENTATION_HISTORY.md)** - Development history
- **Interactive API Docs**: `http://localhost:8080/docs` (Swagger UI) or `/redoc` (ReDoc)
