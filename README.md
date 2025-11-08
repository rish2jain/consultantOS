# ConsultantOS - Business Intelligence Research Engine

Multi-agent AI system for generating McKinsey-grade business framework analyses in 30 minutes instead of 32 hours.

## Features

- **5 Specialized Agents**: Research, Market, Financial, Framework, and Synthesis agents
- **4 Business Frameworks**: Porter's Five Forces, SWOT, PESTEL, and Blue Ocean Strategy
- **Professional PDF Reports**: Auto-generated reports with charts and visualizations
- **Real-time Data**: Integrates with Tavily, Google Trends, SEC EDGAR, and yfinance
- **User Dashboard**: Next.js/React dashboard for report management and analytics
- **Report Sharing**: Link-based sharing with permissions and expiration
- **Template Library**: Custom framework templates and best practices
- **Report Versioning**: Track changes, compare versions, and rollback
- **Comments & Collaboration**: Comment threads and reactions on reports
- **Community Features**: Case study library and best practices sharing
- **Async Processing**: Background job queue for long-running analyses
- **Cloud Run Deployment**: Serverless, auto-scaling deployment on Google Cloud

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export TAVILY_API_KEY=your_tavily_key
export GEMINI_API_KEY=your_gemini_key
```

3. Run the API:
```bash
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080
```

4. Access API docs:
```
http://localhost:8080/docs
```

### Deploy to Cloud Run

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

## API Usage

### Analyze a Company

**Synchronous** (for quick analyses):
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot", "pestel", "blue_ocean"]
  }'
```

**Asynchronous** (recommended for complex analyses):
```bash
# Enqueue job
curl -X POST "http://localhost:8080/analyze/async" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'

# Check status
curl "http://localhost:8080/jobs/{job_id}/status"
```

### Health Check

```bash
curl http://localhost:8080/health
```

### User Registration & Authentication

```bash
# Register
curl -X POST "http://localhost:8080/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "name": "John Doe"
  }'

# Login (get API key)
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

## Architecture

- **Orchestrator**: Coordinates 5 agents using parallel and sequential workflows
- **Phase 1 (Parallel)**: Research, Market, and Financial agents run concurrently
- **Phase 2 (Sequential)**: Framework analysis depends on Phase 1 data
- **Phase 3**: Synthesis agent creates executive summary
- **Caching**: Multi-level caching (in-memory, disk, semantic) for performance
- **Error Handling**: Retry logic, circuit breakers, and graceful degradation
- **Monitoring**: Comprehensive metrics, logging, and observability

## Project Structure

```
consultantos/
├── agents/          # Agent implementations (Research, Market, Financial, Framework, Synthesis)
├── api/             # FastAPI endpoints (main, user, template, sharing, versioning, comments, community, analytics)
├── models/          # Pydantic data models
├── tools/           # Data source integrations (Tavily, Trends, SEC, yfinance)
├── orchestrator/    # Multi-agent coordination
├── reports/         # PDF generation and exports (JSON, Excel, Word)
├── visualizations/  # Chart generation (Plotly)
├── utils/           # Utilities (retry, circuit breaker, validators, sanitize)
├── jobs/            # Async job processing queue
├── services/        # Services (email notifications)
├── cache.py         # Multi-level caching (disk + semantic)
├── storage.py       # Cloud Storage integration
├── database.py      # Firestore database layer
├── auth.py          # API key authentication
├── monitoring.py    # Logging and metrics
└── config.py        # Configuration management

frontend/
├── app/             # Next.js 14 app directory
├── components/      # React components
└── public/          # Static assets
```

## Frontend Dashboard

The application includes a modern Next.js dashboard for managing reports and viewing analytics:

```bash
cd frontend
npm install
npm run dev
```

Access at: `http://localhost:3000`

**Dashboard Features**:
- User authentication and registration
- Report history with filtering and search
- Usage statistics and performance metrics
- API key management
- Report sharing and collaboration
- Comments and version history
- Template library browser
- Community case studies

See [Frontend README](frontend/README.md) for more details.

## Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get started quickly
- **[Setup Guide](SETUP.md)** - Detailed setup instructions
- **[API Documentation](API_Documentation.md)** - Complete API reference and examples
- **[User Testing Guide](USER_TESTING_GUIDE.md)** - Testing procedures and scenarios
- **[Product Strategy & Technical Design](docs/PRODUCT_STRATEGY.md)** - Product vision, requirements, and technical architecture
- **[Implementation History](docs/IMPLEMENTATION_HISTORY.md)** - Development history and enhancement tracking
- **[Frontend Dashboard](frontend/README.md)** - Dashboard setup and features

## License

MIT

