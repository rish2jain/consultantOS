# ConsultantOS - Multi-Agent Business Intelligence Engine

**Version**: 1.0.0-hackathon
**Status**: ✅ Demo-Ready
**Platform**: Google Cloud Run + FastAPI + Gemini AI

Generate McKinsey-grade strategic business analyses in 30 seconds instead of 32 hours using specialized AI agents. Purpose-built for hackathon demonstration of multi-agent orchestration and business intelligence automation.

## What It Does

ConsultantOS orchestrates 5 specialized AI agents to produce professional strategic analyses with:
- **Porter's Five Forces** competitive analysis
- **SWOT Analysis** (Strengths, Weaknesses, Opportunities, Threats)
- **PESTEL Analysis** (Political, Economic, Social, Technological, Environmental, Legal)
- **Blue Ocean Strategy** framework
- **Executive Summary** with strategic recommendations

All backed by real-time data from web research, market trends, and financial sources.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Keys
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
export TAVILY_API_KEY="your-tavily-api-key-here"
```

Get API keys:
- **Gemini**: https://makersuite.google.com/app/apikey
- **Tavily**: https://app.tavily.com

### 3. Start Server
```bash
# Option 1: Direct launch
python main.py

# Option 2: Uvicorn with reload
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Test It
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

**Response**: Complete strategic analysis in JSON format in ~30 seconds.

### 5. View API Docs
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Core Features

### ✅ Multi-Agent Analysis Orchestration
- **5 Specialized Agents**: Research, Market, Financial, Framework, Synthesis
- **Parallel + Sequential Execution**: Optimized for speed
- **Graceful Degradation**: Returns partial results if agents fail
- **Confidence Scoring**: Adjusts based on available data quality

### ✅ Real-Time Data Integration
- **Web Research**: Tavily search API for competitive intelligence
- **Market Trends**: Google Trends for market dynamics
- **Financial Data**: yfinance for stock/financial metrics
- **SEC Filings**: EDGAR integration for public company data

### ✅ Professional Report Generation
- **PDF Export**: Publication-ready strategic reports
- **Excel Export**: Data tables and analysis breakdowns
- **Word Export**: Editable document format
- **Plotly Charts**: Data visualizations in reports

### ✅ Async Job Processing
- **Background Jobs**: Queue long-running analyses
- **Job Status Tracking**: Monitor progress via API
- **Cloud Tasks Ready**: Designed for Google Cloud Tasks integration

### ✅ Production-Ready Infrastructure
- **FastAPI**: Modern async Python web framework
- **Rate Limiting**: 10 requests/hour per IP (configurable)
- **CORS Security**: Configurable origin restrictions
- **Health Checks**: Kubernetes-style probes (ready, live, startup)
- **Structured Logging**: JSON-formatted logs for observability
- **Multi-Level Caching**: Disk + semantic caching for performance

## Architecture

### Agent Workflow

```
┌─────────────────────────────────────────────────────┐
│                 Analysis Orchestrator                │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌───▼────┐     ┌───▼────┐
    │ Research│     │ Market │     │Financial│
    │  Agent  │     │ Agent  │     │  Agent │
    └────┬────┘     └───┬────┘     └───┬────┘
         │              │              │
         └──────────────┼──────────────┘
                        │
                   ┌────▼────┐
                   │Framework│
                   │  Agent  │
                   └────┬────┘
                        │
                   ┌────▼────┐
                   │Synthesis│
                   │  Agent  │
                   └─────────┘
```

**Phase 1 (Parallel)**: Research, Market, and Financial agents run concurrently
**Phase 2 (Sequential)**: Framework agent applies business frameworks to gathered data
**Phase 3**: Synthesis agent creates executive summary

### Technology Stack

**Backend**:
- FastAPI (Python 3.11+)
- Google Gemini 1.5 Flash (via Instructor)
- Pydantic V2 for data validation
- Tavily, Google Trends, yfinance, SEC EDGAR APIs

**Reports**:
- ReportLab (PDF generation)
- Plotly (data visualizations)
- python-docx (Word export)
- openpyxl (Excel export)

**Infrastructure**:
- Google Cloud Run (serverless deployment)
- Firestore (optional, in-memory fallback)
- Cloud Storage (optional, local fallback)
- Cloud Tasks (async job processing)

## API Usage

### Synchronous Analysis
For quick analyses (< 60 seconds):

```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "OpenAI",
    "industry": "Artificial Intelligence",
    "frameworks": ["porter", "swot", "pestel"],
    "analysis_depth": "standard"
  }'
```

### Asynchronous Analysis
For comprehensive analyses or multiple frameworks:

```bash
# Queue job
JOB_RESPONSE=$(curl -X POST "http://localhost:8080/analyze/async" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "SpaceX",
    "industry": "Aerospace",
    "frameworks": ["porter", "swot", "pestel", "blue_ocean"],
    "analysis_depth": "deep"
  }')

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')

# Check status
curl "http://localhost:8080/jobs/$JOB_ID/status"
```

### Export Reports

```bash
# Get report ID from analysis response
REPORT_ID="<report_id>"

# PDF
curl "http://localhost:8080/reports/$REPORT_ID/pdf" -o report.pdf

# Excel
curl "http://localhost:8080/reports/$REPORT_ID/export?format=excel" -o report.xlsx

# Word
curl "http://localhost:8080/reports/$REPORT_ID/export?format=word" -o report.docx

# JSON
curl "http://localhost:8080/reports/$REPORT_ID/export?format=json" -o report.json
```

## Deployment

### Google Cloud Run

```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"
```

### Docker

```bash
# Build
docker build -t consultantos .

# Run
docker run -p 8080:8080 \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  -e TAVILY_API_KEY=$TAVILY_API_KEY \
  consultantos
```

## Configuration

### Environment Variables

**Required**:
- `GEMINI_API_KEY` - Google Gemini API key
- `TAVILY_API_KEY` - Tavily search API key

**Optional**:
- `LOG_LEVEL` - Logging level (default: INFO)
- `RATE_LIMIT_PER_HOUR` - Rate limit per IP (default: 10)
- `CACHE_TTL_SECONDS` - Cache TTL (default: 86400)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `GCP_PROJECT_ID` - Google Cloud project ID (for Firestore/Storage)
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account JSON path

### Gemini Models

Default model: `gemini-1.5-flash-002`

Configure via `GEMINI_MODEL` environment variable:
- `gemini-1.5-flash-002` - Fast, cost-effective (recommended)
- `gemini-1.5-pro-002` - Higher quality, slower
- `gemini-1.0-pro` - Legacy model

## Project Structure

```
consultantos/
├── agents/              # 5 specialized agents
│   ├── base_agent.py       # Base agent with Gemini integration
│   ├── research_agent.py   # Web research via Tavily
│   ├── market_agent.py     # Market trends via Google Trends
│   ├── financial_agent.py  # Financial data via yfinance/SEC
│   ├── framework_agent.py  # Strategic framework analysis
│   └── synthesis_agent.py  # Executive summary generation
├── api/                 # FastAPI endpoints
│   ├── main.py             # Main application and routes
│   ├── jobs_endpoints.py   # Job processing endpoints
│   ├── health_endpoints.py # Health check endpoints
│   └── [user/template/etc] # Additional feature endpoints
├── orchestrator/        # Multi-agent coordination
│   └── orchestrator.py     # Analysis orchestration logic
├── reports/             # Report generation
│   ├── pdf_generator.py    # PDF report creation
│   └── exports.py          # JSON/Excel/Word exports
├── visualizations/      # Chart generation
│   └── __init__.py         # Plotly chart creators
├── tools/               # Data source integrations
│   ├── tavily_tool.py      # Tavily search wrapper
│   ├── trends_tool.py      # Google Trends wrapper
│   └── financial_tool.py   # yfinance/EDGAR wrapper
├── jobs/                # Async job queue
│   ├── queue.py            # Job queue management
│   └── worker.py           # Background worker
├── utils/               # Utilities
│   ├── validators.py       # Input validation
│   ├── sanitize.py         # Input sanitization
│   ├── circuit_breaker.py  # Circuit breaker pattern
│   └── retry.py            # Retry logic
├── models.py            # Pydantic data models
├── cache.py             # Multi-level caching
├── database.py          # Firestore integration
├── storage.py           # Cloud Storage integration
├── monitoring.py        # Logging and metrics
└── config.py            # Configuration management
```

## Performance

### Speed Comparison
- **Manual consultant**: 32 hours (2 working days)
- **ConsultantOS**: 30 seconds average
- **Speedup**: ~3,840x faster

### Analysis Times
- **Simple** (1-2 frameworks): 15-30 seconds
- **Standard** (3-4 frameworks): 30-60 seconds
- **Deep** (5+ frameworks): 60-120 seconds

### Quality
- McKinsey-grade strategic framework analysis
- Evidence-based recommendations from real data
- Multi-source data synthesis and cross-validation
- Professional PDF formatting with visualizations

## Documentation

- **[Hackathon Guide](HACKATHON_GUIDE.md)** - Complete demo setup and usage
- **[Quick Start](QUICK_START.md)** - Streamlined getting started
- **[Setup Guide](SETUP.md)** - Detailed installation and configuration
- **[API Documentation](API_Documentation.md)** - Full API reference
- **[CLAUDE.md](CLAUDE.md)** - Claude Code development guidance

### Feature Guides (Archived)
The following guides describe features that exist in the codebase but are disabled for the hackathon demo:
- Continuous monitoring system
- Team collaboration features
- Knowledge base integration
- Custom framework builder
- Live dashboards

See `docs/archive/` for implementation reports and historical documentation.

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=consultantos --cov-report=html

# Specific test file
pytest tests/test_agents.py -v
```

## Troubleshooting

### Import Errors
All import errors have been fixed in v1.0.0-hackathon. If you encounter issues:
```bash
git pull origin master
pip install -r requirements.txt --upgrade
```

### API Keys Not Working
```bash
# Verify keys are set
echo $GEMINI_API_KEY
echo $TAVILY_API_KEY

# Test Gemini directly
python -c "import google.generativeai as genai; genai.configure(api_key='$GEMINI_API_KEY'); print('✅ Gemini OK')"
```

### Port Already in Use
```bash
# Find process on port 8080
lsof -ti:8080

# Kill process
kill -9 $(lsof -ti:8080)
```

## License

MIT

## Support

For issues, questions, or contributions, see the GitHub repository or contact the development team.

---

**Built with** ❤️ **for hackathon demonstration of multi-agent AI systems**
