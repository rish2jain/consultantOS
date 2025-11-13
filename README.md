# ConsultantOS - Continuous Competitive Intelligence Platform

**Transform from one-time reports to continuous intelligence monitoring**

Multi-agent AI platform that continuously monitors companies and industries, detects material changes, and delivers real-time competitive intelligence. Get McKinsey-grade strategic analyses updated automatically instead of manual report generation.

## Core Features

### Continuous Intelligence Monitoring
- **Dashboard-First Experience**: Real-time monitoring dashboard with live updates
- **Automated Change Detection**: Track competitors, market trends, and strategic shifts
- **Smart Alerts**: Only notify on material changes above confidence thresholds
- **Multiple Monitors**: Track 100+ companies simultaneously per user
- **Flexible Scheduling**: Hourly, daily, weekly, or monthly checks
- **User Feedback Loop**: Learn from alert relevance to improve quality

### Strategic Analysis Engine
- **5 Specialized Agents**: Research, Market, Financial, Framework, and Synthesis agents
- **4 Business Frameworks**: Porter's Five Forces, SWOT, PESTEL, and Blue Ocean Strategy
- **Real-time Data**: Integrates with Tavily, Google Trends, SEC EDGAR, and yfinance
- **Change Detection**: Competitive forces, market trends, financial metrics, strategic shifts

### Dashboard & Collaboration
- **Live Dashboard**: Real-time status of all monitors and alerts
- **Alert Management**: Mark as read, provide feedback, track actions taken
- **Export Options**: PDF reports available on-demand (no longer default)
- **Report Sharing**: Link-based sharing with permissions and expiration
- **Template Library**: Custom framework templates and best practices

### Platform Infrastructure
- **Background Workers**: Automated scheduled monitoring checks
- **Async Processing**: Non-blocking job queue for analyses
- **Multi-level Caching**: Disk + semantic caching for performance
- **Cloud Run Deployment**: Serverless, auto-scaling deployment on Google Cloud

## Live Demo

**🌐 Production Dashboard**: https://consultantos-frontend-187550875653.us-central1.run.app
**📚 API Documentation**: https://consultantos-api-187550875653.us-central1.run.app/docs

Try the live system now - no installation required!

---

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

**Quick Deploy (Automated):**
```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# Run deployment script
./scripts/deploy.sh
```

**Manual Deployment:**
See [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) for comprehensive deployment guide including:
- Backend API deployment
- Frontend dashboard deployment
- Security configuration
- Monitoring setup
- Cost optimization

**Quick Start (Backend Only):**
```bash
gcloud run deploy consultantos-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"
```

## API Usage

### Continuous Monitoring (Primary Use Case)

**Create a Monitor** (recommended approach):
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
      "alert_threshold": 0.7,
      "notification_channels": ["email", "in_app"]
    }
  }'
```

**List Your Monitors**:
```bash
curl "http://localhost:8080/monitors" \
  -H "X-API-Key: your_api_key"
```

**Get Monitor Alerts**:
```bash
curl "http://localhost:8080/monitors/{monitor_id}/alerts" \
  -H "X-API-Key: your_api_key"
```

**Trigger Manual Check**:
```bash
curl -X POST "http://localhost:8080/monitors/{monitor_id}/check" \
  -H "X-API-Key: your_api_key"
```

**Mark Alert as Read**:
```bash
curl -X POST "http://localhost:8080/monitors/alerts/{alert_id}/read" \
  -H "X-API-Key: your_api_key"
```

**Provide Alert Feedback** (improves future alerts):
```bash
curl -X POST "http://localhost:8080/monitors/alerts/{alert_id}/feedback" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "feedback": "helpful",
    "action_taken": "scheduled_deep_dive",
    "notes": "Detected competitor pricing change early"
  }'
```

### One-Time Analysis (Legacy Mode)

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

### Core Documentation
- **[Setup Guide](SETUP.md)** - Detailed setup and installation instructions
- **[API Documentation](API_Documentation.md)** - Complete API reference and examples
- **[Architecture](ARCHITECTURE.md)** - Comprehensive system architecture
- **[Deployment Plan](DEPLOYMENT_PLAN.md)** - ⭐ **Complete Cloud Run deployment guide**
- **[Deployment Quick Start](DEPLOYMENT_QUICK_START.md)** - Quick deployment reference

### Additional Resources
- **[Documentation Index](docs/DOCUMENTATION_INDEX.md)** - 📚 **Complete index of all documentation**
- **[Frontend Architecture](FRONTEND_ARCHITECTURE.md)** - Frontend tech stack and architecture
- **[Frontend Deployment](frontend/DEPLOYMENT.md)** - Frontend-specific deployment guide
- **[Frontend Dashboard](frontend/README.md)** - Dashboard setup and features
- **[Decision Intelligence Usage](DECISION_INTELLIGENCE_USAGE.md)** - Decision Intelligence Engine guide
- **[Product Strategy](docs/PRODUCT_STRATEGY.md)** - Product vision, requirements, and technical architecture
- **[Best Practices](best_practices.md)** - Coding guidelines and project standards

## License

MIT

