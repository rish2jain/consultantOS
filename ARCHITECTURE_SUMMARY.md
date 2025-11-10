# ConsultantOS Architecture - Executive Summary

## Project Overview

**ConsultantOS** is a Continuous Competitive Intelligence Platform that provides real-time monitoring and strategic analysis of companies and markets. It evolved from a batch-oriented report generator to a continuous intelligence system with a dashboard-first user experience.

## Core Innovation

The platform shifts from:
- **Traditional**: One-time reports on demand (32 hours → 30 minutes)
- **Modern**: Continuous monitoring with real-time dashboards and smart alerts

---

## Architecture at a Glance

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React, Tailwind CSS | User interface & monitoring dashboard |
| **Backend** | FastAPI, Python 3.11+ | REST API & business logic |
| **Agents** | 5 specialized agents with Gemini | Multi-source intelligence gathering |
| **Database** | Google Firestore | Document-based persistence |
| **Storage** | Google Cloud Storage | PDF report hosting (signed URLs) |
| **Cache** | diskcache + ChromaDB | Multi-level intelligent caching |
| **LLM** | Google Gemini API | Structured outputs via Instructor |
| **Monitoring** | Sentry + Prometheus | Observability & error tracking |
| **Jobs** | asyncio + Celery (optional) | Background job processing |

---

## Key Components

### 1. Agent-Based Intelligence System

**5 Specialized Agents (Multi-Agent Orchestration):**

```
Phase 1: PARALLEL DATA GATHERING (60s timeout each)
├── ResearchAgent → Web search (Tavily) → CompanyResearch
├── MarketAgent → Consumer trends (Google Trends) → MarketTrends
└── FinancialAgent → Financial metrics → FinancialSnapshot

Phase 2: SEQUENTIAL ANALYSIS
└── FrameworkAgent → Business frameworks → FrameworkAnalysis
    (Porter, SWOT, PESTEL, Blue Ocean)

Phase 3: SYNTHESIS
└── SynthesisAgent → Executive summary → ExecutiveSummary
```

**Key Features:**
- Graceful degradation: works with 1-3 agents succeeding (adjust confidence)
- Timeout enforcement: per-agent 60s limit
- Error handling: Sentry integration, breadcrumbs, tagging
- Performance tracking: execution time metrics

### 2. Continuous Intelligence Monitoring

**New capability: Real-time change detection**

```
Monitor Created → Baseline Analysis → Scheduled Checks (hourly/daily/weekly)
                                              ↓
                                    Run new analysis
                                              ↓
                                    Compare snapshots
                                              ↓
                                    Detect changes
                                              ↓
                                    Anomaly detection (Prophet)
                                              ↓
                                    Priority scoring (0-10)
                                              ↓
                                    Throttling & deduplication
                                              ↓
                                    Multi-channel alerts
                                    (Email/Slack/Webhook/In-App)
```

**Components:**
- `IntelligenceMonitor`: Core orchestration
- `SnapshotAggregator`: Change detection
- `AnomalyDetector`: Time-series analysis (Facebook Prophet)
- `AlertScorer`: Priority & throttling
- `TimeSeriesOptimizer`: Data compression (60% reduction)

### 3. Multi-Level Caching

```
Layer 3: IN-MEMORY
- Alert dedup, ticker cache (5m TTL)

Layer 2: SEMANTIC CACHE (ChromaDB)
- Embedding similarity, dedup (24h TTL)
- Hit rate: ~30%

Layer 1: DISK CACHE (diskcache)
- Persistent, 1GB limit (3600s TTL)
- Hit rate: ~60-70%
```

### 4. API Architecture

**20+ endpoints organized by feature:**

```
Core Analysis:     /analyze, /analyze/async, /jobs/{id}
Monitoring:        /monitors (CRUD), /monitors/{id}/alerts
Authentication:    /auth/register, /auth/login, /auth/api-keys
Analytics:         /analytics/summary, /trends, /query
User Management:   /profile, /preferences
Additional:        /templates, /sharing, /feedback, /comments
```

**Middleware Stack:**
- CORS, GZip compression, session management
- Rate limiting (slowapi, configurable)
- Request logging with structured context
- Sentry error tracking

### 5. Frontend Architecture

**Next.js 14 with modern React patterns:**

```
Pages:
- Dashboard (/dashboard) → Main monitoring interface
- Analysis (/analysis) → One-off analysis form
- Reports (/reports) → Report history & viewer
- Templates (/templates) → Saved analysis templates

Key Components:
- Navigation (top nav)
- DataTable (reusable, sortable, paginated)
- Chart (Plotly visualization)
- Monitor card & alert feed
- Modal, button, card, alert components

State Management:
- React Query for server state
- Component-level state (useState)
- Custom hooks (useKeyboardShortcuts, useWebSocket)
```

---

## Data Flow Summary

### Analysis Request (Sync)

```
POST /analyze
    ↓
Validate & sanitize
    ↓
Check cache (disk/semantic)
    ↓ Cache HIT → Return immediately
    ↓ Cache MISS → Continue
    ↓
Phase 1: asyncio.gather() [3 agents in parallel]
    ├─ ResearchAgent (Tavily) → 20-60s
    ├─ MarketAgent (Trends) → 10-30s
    └─ FinancialAgent (APIs) → 20-50s
    ↓
Phase 2: Framework agent (sequential)
    └─ FrameworkAgent → 10-20s
    ↓
Phase 3: Synthesis agent
    └─ SynthesisAgent → 5-10s
    ↓
Assemble report + adjust confidence
    ↓
Store in cache (disk + semantic)
    ↓
Return StrategicReport JSON
Optional: Generate + upload PDF
    ↓
200 OK: {report, pdf_url, confidence}

Total Latency: 45-90s (Phase 1 timeout)
```

### Monitoring Check (Background)

```
Scheduled trigger (hourly/daily/weekly)
    ↓
Get active monitors for user
    ↓
For each monitor:
    ├─ Run analysis (full 3-phase)
    ├─ Compare with previous snapshot
    ├─ Run anomaly detection (Prophet)
    ├─ Score alert priority (0-10)
    ├─ Check dedup/throttling
    └─ If should_notify:
        ├─ Send email (SMTP)
        ├─ Send Slack (webhook)
        ├─ Send webhook (custom)
        └─ Store in-app alert
    ↓
Store new snapshot (compressed)
    ↓
Mark monitor as checked
    ↓
Schedule next check
```

---

## Design Patterns Used

| Pattern | Usage | Example |
|---------|-------|---------|
| **Agent** | Specialized task performers | 5 agent subclasses |
| **Orchestrator** | Multi-step workflow coordination | AnalysisOrchestrator |
| **Circuit Breaker** | Fault tolerance | Tavily API wrapper |
| **Graceful Degradation** | Partial results on failure | Continue with 1-2 agents |
| **Dependency Injection** | Loose coupling | get_orchestrator(), get_db_service() |
| **Repository** | Data abstraction | DatabaseService |
| **Factory** | Lazy initialization | get_tavily_client() |
| **Decorator** | Cross-cutting concerns | @cached_analysis(), @track_operation() |
| **Observer** | Change detection | Alert notifications on changes |
| **Strategy** | Configurable behavior | Different monitoring frequencies |

---

## External Integrations

### Data Sources

| Source | Agent | Use Case | Resilience |
|--------|-------|----------|-----------|
| **Tavily API** | Research | Web search | Circuit breaker + 3 retries |
| **Google Trends** | Market | Consumer interest | Try/except, fallback to empty |
| **yfinance** | Financial | Stock data | Direct, with error handling |
| **Finnhub** | Financial | Analyst data | Disk cache + rate limiting |
| **Alpha Vantage** | Financial | Technical indicators | Optional, graceful skip |

### AI/LLM

- **Google Gemini 1.5 Flash** for:
  - Structured analysis (via Instructor)
  - Framework application
  - Executive summary generation
  - NLP enrichment (entity extraction, sentiment)

---

## Performance Characteristics

### Concurrency Model

- **Phase 1**: 3 agents run in parallel (asyncio.gather)
- **Phase 2-3**: Sequential (data dependent)
- **Monitors**: Max 5 concurrent checks
- **Caching**: Reduces repeated analyses by 60-70%

### Latency Profile

| Operation | Time | Bottleneck |
|-----------|------|-----------|
| Cache hit | 50ms | Disk I/O |
| Phase 1 | 30-60s | External API calls |
| Phase 2 | 10-20s | Gemini token generation |
| Phase 3 | 5-10s | Synthesis |
| **Total** | **45-90s** | **Phase 1 timeout** |

### Database Optimization

- **Compression**: Snapshots >1KB → zlib, saves 60% storage
- **Indexing**: Composite indexes on (user_id, status), (monitor_id, created_at)
- **Partitioning**: By monitor_id for scalability
- **TTL**: Automatic cleanup of old snapshots

---

## Deployment Model

### Backend: Google Cloud Run

```
Service: consultantos
Region: us-central1
Memory: 2Gi
CPU: 2
Timeout: 300s
Auto-scaling: 0-100 instances
Cold start: ~10s
```

### Frontend: Vercel

```
Framework: Next.js 14
Build: npm run build
Deploy: vercel deploy
Env: NEXT_PUBLIC_API_URL
```

### Infrastructure

- **Database**: Google Firestore (managed)
- **Storage**: Google Cloud Storage (signed URLs)
- **Queue**: Cloud Tasks or Celery + Redis
- **Observability**: Sentry (error tracking) + Prometheus (metrics)

---

## Security Architecture

### Authentication

- API Key (header `X-API-Key` or query param)
- JWT for user sessions
- Optional for public endpoints

### Data Protection

- Input sanitization (XSS prevention)
- Pydantic validation (type safety)
- Signed URLs for PDF downloads (1-hour expiration)
- Private Cloud Storage buckets
- HTTPS enforced in production

### Rate Limiting

- Per-IP: 10 req/hour (configurable)
- Could add: per-user quotas, per-API-key limits

---

## Monitoring & Observability

### Logging

- Structured logging via `logging` module
- Context tracking: company, user_id, report_id
- Levels: DEBUG, INFO, WARNING, ERROR

### Metrics

- **Prometheus**: Request counts, latencies, error rates
- **Custom**: Analyses/hour, monitor success rate, confidence distribution
- **Sentry**: Transaction tracking, performance, error grouping

### Tracing

- Sentry transactions for agent execution
- Breadcrumbs for execution milestones
- Tagged context (agent name, company, error type)

---

## Strengths & Weaknesses

### Strengths ✓

1. **Scalable Multi-Agent**: Independent agents with timeout + graceful degradation
2. **Intelligent Caching**: Multi-level (disk + semantic) reduces API costs
3. **Continuous Intelligence**: Real-time monitoring with anomaly detection
4. **Error Resilient**: Circuit breakers, retries, partial results
5. **Modular Design**: Clear separation (agents, tools, orchestrator, API)
6. **Cloud Native**: Serverless-ready, GCP-integrated, auto-scaling
7. **Well Observable**: Sentry, Prometheus, structured logging
8. **Type Safe**: Pydantic models throughout

### Weaknesses & Improvements ✗

1. **Agent Timeout Coupling**: All agents same 60s timeout (should be per-agent)
2. **Cache Invalidation**: No explicit TTL-based invalidation strategy
3. **No Gemini Circuit Breaker**: Only Tavily has circuit breaker
4. **Rate Limiting**: Per-IP only, no per-user quotas
5. **Monitoring Backpressure**: No queue depth limits
6. **Event Sourcing**: No complete audit trail of all actions
7. **Distributed Tracing**: No OpenTelemetry integration
8. **Multi-Region**: Currently single region (us-central1)

---

## Getting Started

### Local Development

```bash
# Backend
pip install -r requirements.txt
export GEMINI_API_KEY=...
export TAVILY_API_KEY=...
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

### API Testing

```bash
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

---

## File Organization

```
consultantos/
├── agents/              # 5 specialized agents
├── orchestrator/        # Multi-agent coordination
├── monitoring/          # Intelligence monitoring system
├── api/                 # 20+ FastAPI endpoints
├── models/              # Pydantic data models
├── tools/               # External tool integrations
├── database.py          # Firestore abstraction
├── cache.py             # Multi-level caching
├── storage.py           # Cloud Storage integration
├── config.py            # Settings management
├── auth.py              # Authentication
└── prompts.py           # LLM prompts

frontend/
├── app/
│   ├── page.tsx         # Home
│   ├── dashboard/       # Main monitoring UI
│   ├── analysis/        # Analysis form
│   ├── reports/         # Report history
│   ├── components/      # 70+ reusable components
│   ├── hooks/           # Custom React hooks
│   └── api/             # Client-side API
└── next.config.js
```

---

## Key Metrics for Success

### Performance KPIs

- Analysis latency: < 90s
- Cache hit rate: > 60%
- Uptime: > 99.9%
- Error rate: < 1%

### Business KPIs

- Monitors created: N/month
- Alerts generated: N/day
- User retention: X%
- API usage: N/month

### Data Quality

- Confidence score: > 0.7 (70%)
- Change detection accuracy: > 85%
- False positive rate: < 10%
- User feedback incorporation: Monthly

---

## Next Steps / Roadmap

1. **Multi-Region Deployment**: Reduce latency globally
2. **Advanced ML**: User feedback loop to improve change detection
3. **Custom Agents**: Allow users to create custom analysis agents
4. **Webhooks**: User-defined webhooks for alerts
5. **API Rate Quotas**: Per-user pricing tiers
6. **White-Label**: Embed monitoring in other platforms
7. **Mobile App**: Native iOS/Android for alerts
8. **Integrations**: Zapier, Make, Power Automate

---

## Documentation

For more details, see:
- `ARCHITECTURE.md` - Comprehensive 15-section architecture
- `ARCHITECTURE_DIAGRAMS.md` - Visual flows and diagrams
- `CLAUDE.md` - Project guidelines and commands

---

**Generated**: November 9, 2025
**Analysis Scope**: Very thorough (30+ files examined)
**Coverage**: All 7 focus areas (agents, API, monitoring, models, tools, database, frontend)

