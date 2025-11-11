# ConsultantOS: Comprehensive Architecture Analysis

## Executive Summary

ConsultantOS is a **Comprehensive Competitive Intelligence Platform** that orchestrates multiple specialized AI agents to provide comprehensive business intelligence. The platform has evolved from a simple report generator to a full-featured intelligence platform with advanced analytics, conversational AI, and strategic planning capabilities.

**Key Capabilities:**
- **Core Analysis**: 5 specialized agents (Research, Market, Financial, Framework, Synthesis)
- **Advanced Analytics**: Forecasting, Wargaming, Social Media Analysis, Dark Data Extraction
- **Conversational AI**: RAG-based chat with intelligent query routing
- **Strategic Intelligence**: Comprehensive competitive intelligence dashboards
- **Report Generation**: PDF, Excel, Word exports with interactive visualizations

---

## 1. AGENT ORCHESTRATION FLOW

### 1.1 Architecture Overview

```
User Request
    ↓
[API Layer] (/analyze, /monitors/*)
    ↓
[AnalysisOrchestrator] - 3-Phase Execution
    ├── Phase 1: Parallel Data Gathering (60s timeout per agent)
    │   ├── ResearchAgent (Tavily web search)
    │   ├── MarketAgent (Google Trends via pytrends)
    │   └── FinancialAgent (yfinance + Finnhub + Alpha Vantage)
    │
    ├── Phase 2: Sequential Analysis (with graceful degradation)
    │   └── FrameworkAgent (Porter, SWOT, PESTEL, Blue Ocean)
    │
    └── Phase 3: Synthesis (Executive Summary)
        └── SynthesisAgent (LLM-powered summarization)
    ↓
[Cache Layer] - Semantic + Disk Cache
    ↓
[Report Assembly] - StrategicReport object
    ↓
[PDF Generation] (Optional) or [Dashboard Display]
```

### 1.2 BaseAgent Pattern

All agents inherit from `BaseAgent` providing:
- **Gemini + Instructor Setup**: Structured LLM outputs using Pydantic models
- **Timeout Handling**: Per-agent 60s timeout with asyncio.wait_for()
- **Error Logging**: Context-aware logging with Sentry integration
- **Performance Tracking**: Execution time measurement and breadcrumb tracking

```python
class BaseAgent(ABC):
    async def execute(input_data):
        # Wraps _execute_internal() with:
        # - timeout enforcement
        # - Sentry transaction tracking
        # - Performance metrics
        # - Error handling & context
        
    @abstractmethod
    async def _execute_internal(input_data):
        # Implemented by each agent
```

### 1.3 Core Agent Implementations

The platform includes 5 core agents plus multiple advanced agents:

#### ResearchAgent
- **Purpose**: Gather company intelligence using web search
- **Input**: Company name, industry context
- **Output**: `CompanyResearch` with NLP enrichment
- **Tools Used**: Tavily API (advanced search depth)
- **Features**:
  - Entity extraction (named entities)
  - Sentiment analysis
  - Entity relationship detection
  - Keyword extraction

#### MarketAgent  
- **Purpose**: Analyze market trends and consumer interest
- **Input**: Company name, industry
- **Output**: `MarketTrends` with comparative analysis
- **Tools Used**: pytrends (Google Trends)
- **Features**:
  - Search interest trends (Growing/Stable/Declining)
  - Geographic distribution
  - Related searches
  - Competitor comparison

#### FinancialAgent
- **Purpose**: Extract financial metrics and analyst sentiment
- **Input**: Company ticker, industry
- **Output**: `FinancialSnapshot` with multi-source validation
- **Tools Used**: 
  - yfinance (primary market data)
  - Finnhub (analyst recommendations, news sentiment)
  - Alpha Vantage (technical indicators)
- **Features**:
  - Cross-source validation (yfinance vs Finnhub)
  - Analyst consensus scores
  - News sentiment analysis
  - Technical indicators

#### FrameworkAgent
- **Purpose**: Apply strategic business frameworks
- **Input**: Company context + Phase 1 data (optional)
- **Output**: `FrameworkAnalysis` with framework-specific models
- **Frameworks Supported**:
  - Porter's Five Forces (competitive dynamics)
  - SWOT Analysis (strengths/weaknesses/opportunities/threats)
  - PESTEL Analysis (macro-environmental factors)
  - Blue Ocean Strategy (value innovation)
- **Features**:
  - Evidence-based analysis
  - Quantitative scoring
  - Graceful degradation (works with partial Phase 1 data)

#### SynthesisAgent
- **Purpose**: Create executive summary from all analysis
- **Input**: Outputs from all Phase 1 + Phase 2 agents
- **Output**: `ExecutiveSummary` with strategic recommendations
- **Features**:
  - Confidence scoring
  - Prioritized next steps
  - Risk/opportunity assessment

### 1.4 Advanced Agent Implementations

#### ForecastingAgent
- **Purpose**: Multi-scenario financial forecasting using Monte Carlo simulation
- **Input**: Company financial data, historical metrics
- **Output**: `ForecastResult` with multiple scenarios (optimistic, base, pessimistic)
- **Tools Used**: NumPy, SciPy for statistical analysis
- **Features**:
  - Monte Carlo simulation (1000+ iterations)
  - Statistical validation with confidence intervals
  - Multiple scenario modeling
  - P-value and confidence interval calculations

#### WargamingAgent
- **Purpose**: Competitive scenario planning and simulation
- **Input**: Company context, competitive scenario definition
- **Output**: `WargamingResult` with win probability and risk assessment
- **Tools Used**: NumPy, SciPy for Monte Carlo simulation
- **Features**:
  - Monte Carlo simulation for competitive scenarios
  - Win probability calculations
  - Risk assessment
  - Statistical validation

#### SocialMediaAgent
- **Purpose**: Social media sentiment analysis and trend tracking
- **Input**: Company name, keywords, platforms
- **Output**: `SocialMediaInsights` with sentiment scores and trends
- **Tools Used**: Reddit (PRAW), Twitter (Tweepy), Grok API (via laozhang.ai)
- **Features**:
  - Reddit sentiment analysis
  - Twitter sentiment tracking
  - Trend identification
  - Influencer detection
  - Real-time sentiment monitoring

#### DarkDataAgent
- **Purpose**: Extract insights from unstructured data sources
- **Input**: Unstructured documents, emails, files
- **Output**: `DarkDataInsights` with extracted intelligence
- **Tools Used**: NLP libraries (spaCy, TextBlob)
- **Features**:
  - Email parsing and analysis
  - Document extraction
  - Hidden insights discovery
  - Entity extraction from unstructured sources

#### ConversationalAgent
- **Purpose**: RAG-based conversational AI with intelligent query routing
- **Input**: User query, company context, conversation history
- **Output**: `ConversationalResponse` with AI response and sources
- **Tools Used**: ChromaDB for vector storage, RAG retrieval
- **Features**:
  - RAG-based retrieval from historical reports
  - Intelligent routing to specialized agents
  - Conversation history management
  - Source citation and transparency

### 1.5 Orchestrator Pattern

**AnalysisOrchestrator** manages:

1. **Cache Lookup** (semantic + disk)
2. **Phase 1 Execution**: 
   - Parallel task execution via `asyncio.gather()`
   - Individual error handling in `_safe_execute_agent()`
   - Graceful degradation: continues if 1-2 agents fail
   - Failure only if ALL agents fail
3. **Phase 2 Execution**:
   - Sequential processing (depends on Phase 1 data)
   - Handles missing data with warnings
4. **Phase 3 Execution**:
   - Synthesis uses both Phase 1 and Phase 2 outputs
5. **Report Assembly**:
   - Confidence score adjustment (reduce 10% per failed agent, min 0.3)
   - Metadata tracking (frameworks requested, depth, partial_results flag)
   - Error collection and reporting
6. **Cache Storage**: Semantic cache stores for future hits

---

## 2. DATA FLOW PATTERNS

### 2.1 Request Flow

```
HTTP Request: POST /analyze
    ↓
[AnalysisRequestValidator] - validates & sanitizes
    ├── company: str (required)
    ├── industry: str (optional, auto-detect)
    ├── frameworks: List[str] (default: all 4)
    └── depth: str (quick/standard/deep)
    ↓
[AnalysisOrchestrator.execute()] 
    ├── Cache check → return if hit
    ├── Phase 1 → CompanyResearch, MarketTrends, FinancialSnapshot
    ├── Phase 2 → FrameworkAnalysis
    ├── Phase 3 → ExecutiveSummary
    ↓
[StrategicReport] - assembled object
    ├── executive_summary: ExecutiveSummary
    ├── company_research: CompanyResearch
    ├── market_trends: MarketTrends
    ├── financial_snapshot: FinancialSnapshot
    ├── framework_analysis: FrameworkAnalysis
    ├── recommendations: List[str]
    └── metadata: Dict
    ↓
[Response to client]
    - Sync: /analyze → return StrategicReport + optional PDF
    - Async: /analyze/async → return job_id, process in background
```

### 2.2 Monitoring Flow (NEW)

```
User creates Monitor (POST /monitors)
    ↓
[IntelligenceMonitor.create_monitor()]
    ├── Validate company/industry
    ├── Check for duplicate active monitor
    ├── Create Monitor object with MonitoringConfig
    ├── Run initial baseline analysis (via orchestrator)
    ├── Store baseline snapshot in Firestore
    └── Schedule background checks
    ↓
[MonitoringWorker] (background/scheduled)
    ├── Check interval: hourly/daily/weekly/monthly
    ├── For each active monitor:
    │   ├── Run new analysis
    │   ├── Compare with previous snapshot
    │   ├── Detect changes (via SnapshotAggregator)
    │   ├── Run anomaly detection (via AnomalyDetector)
    │   ├── Score alerts (via AlertScorer)
    │   └── Create Alert if threshold exceeded
    └── Store snapshot, changes, alerts in Firestore
    ↓
[Alert Distribution]
    ├── In-app notifications (in Firestore)
    ├── Email notifications (via EmailService)
    ├── Slack notifications (via SlackChannel)
    └── Webhook callbacks (via WebhookChannel)
    ↓
[User Dashboard]
    ├── Real-time alert feed
    ├── Monitor status indicators
    ├── Change timeline visualization
    └── Manual trigger options
```

### 2.3 Pydantic Model Hierarchy

**Input Models:**
- `AnalysisRequest` - user request with frameworks/depth

**Agent Output Models:**
- `CompanyResearch` - research_agent output
- `MarketTrends` - market_agent output  
- `FinancialSnapshot` - financial_agent output
- `FrameworkAnalysis` - framework_agent output
- `ExecutiveSummary` - synthesis_agent output

**Composite Models:**
- `StrategicReport` - final assembled report

**Monitoring Models:**
- `Monitor` - continuous monitoring instance
- `MonitoringConfig` - configuration options
- `Alert` - detected change alert
- `Change` - individual change detected
- `MonitorAnalysisSnapshot` - time-series snapshot for comparison

---

## 3. EXTERNAL INTEGRATIONS

### 3.1 Data Sources

| Tool | Purpose | Agent | Integration |
|------|---------|-------|-------------|
| **Tavily** | Web search | ResearchAgent | `tavily_search_tool()` - circuit breaker + retry |
| **Google Trends** | Consumer trends | MarketAgent | `pytrends` library |
| **yfinance** | Stock/financial data | FinancialAgent | Direct library calls |
| **Finnhub** | Analyst data | FinancialAgent | `finnhub_tool()` - with caching |
| **Alpha Vantage** | Technical indicators | FinancialAgent | `alpha_vantage_tool()` - optional |
| **Reddit (PRAW)** | Social media | SocialMediaAgent | Reddit API wrapper |
| **Twitter (Tweepy)** | Social media | SocialMediaAgent | Twitter API v2 client |
| **Grok (laozhang.ai)** | Sentiment analysis | SocialMediaAgent | Grok API integration |
| **ChromaDB** | Vector storage | ConversationalAgent | RAG retrieval |
| **NumPy/SciPy** | Statistical analysis | ForecastingAgent, WargamingAgent | Monte Carlo simulation |

### 3.2 Tool Patterns

**Circuit Breaker Pattern:**
```python
_tavily_circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60,      # Attempt recovery after 60s
    name="tavily_api"
)
```

**Retry Logic:**
- Max 3 retries with exponential backoff
- Delay: 1s → 2s → 4s
- Circuit breaker integration

**Caching:**
- Finnhub tool uses disk cache (diskcache)
- TTL-based expiration
- Optional semantic dedup via ChromaDB

### 3.3 LLM Integration

**Gemini Integration:**
```python
genai.configure(api_key=settings.gemini_api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash-002")
client = instructor.from_gemini(gemini_model)

# Structured outputs via Instructor
response = await client.create(
    messages=[{"role": "user", "content": prompt}],
    response_model=TargetPydanticModel,
    temperature=0.7,
    max_output_tokens=4000
)
```

---

## 4. MONITORING & INTELLIGENCE SYSTEM

### 4.1 Core Components

#### IntelligenceMonitor
```python
class IntelligenceMonitor:
    def __init__(orchestrator, db_service, cache_service):
        self.orchestrator = orchestrator
        self.timeseries_optimizer = TimeSeriesOptimizer(...)
        self.snapshot_aggregator = SnapshotAggregator(...)
        self.anomaly_detector = AnomalyDetector(...)
        self.alert_scorer = AlertScorer(...)
```

**Key Methods:**
- `create_monitor()` - Initialize new monitor with baseline
- `check_monitor()` - Run analysis & detect changes
- `get_alerts()` - Retrieve alert history
- `provide_feedback()` - User feedback for ML improvement

#### TimeSeriesOptimizer
- Compresses snapshots >1KB using zlib
- Batch storage optimization (compress every 10 snapshots)
- 5-minute cache TTL for recent data
- Reduces database storage by ~60%

#### SnapshotAggregator
- Compares consecutive snapshots
- Detects metric changes (financial, market, research)
- Calculates change confidence
- Supports multi-period aggregation (hourly/daily/weekly)

#### AnomalyDetector
- Facebook Prophet for time-series forecasting
- Detects 4 anomaly types:
  - **POINT**: Single unusual value
  - **CONTEXTUAL**: Unusual in context (time/seasonality)
  - **TREND_REVERSAL**: Direction change
  - **VOLATILITY_SPIKE**: Sudden variance increase
- Confidence scoring
- Statistical details (z-score, p-value)

#### AlertScorer
- Priority scoring (0-10 scale)
- Urgency levels: critical/high/medium/low
- Deduplication (hash-based)
- Throttling windows:
  - Critical: 1 hour
  - Default: 4 hours
  - Low priority: 24 hours
- Max alerts per monitor per day: 5

### 4.2 Change Detection

**Change Types:**
- COMPETITIVE_LANDSCAPE
- MARKET_TREND
- FINANCIAL_METRIC
- STRATEGIC_SHIFT
- REGULATORY
- TECHNOLOGY
- LEADERSHIP

**Change Model:**
```python
class Change(BaseModel):
    change_type: ChangeType
    title: str
    description: str
    confidence: float (0-1)
    source_urls: List[str]
    detected_at: datetime
    previous_value: Optional[str]
    current_value: Optional[str]
```

### 4.3 Notification System

**Multi-Channel Architecture:**
```
Alert Generated
    ├── [AlertScorer] → Priority & Throttling
    ├── [InMemory Dedup Cache]
    ├── If shouldNotify:
    │   ├── → [EmailService] (SMTP)
    │   ├── → [SlackChannel] (Webhook)
    │   ├── → [WebhookChannel] (Custom endpoints)
    │   └── → [InAppChannel] (Firestore + API)
    └── Store in database
```

**Channels:**
1. **Email**: SMTP-based, includes summary + links
2. **Slack**: Webhook integration, formatted messages
3. **Webhook**: Custom user webhooks with retry logic
4. **In-App**: Stored in Firestore, real-time via WebSocket

### 4.4 Background Workers

#### AnalysisWorker
- Processes `/analyze/async` jobs
- Updates JobQueue status (PENDING → PROCESSING → COMPLETED/FAILED)
- Generates PDF reports
- Uploads to Cloud Storage with signed URLs

#### MonitoringWorker
- Scheduled monitor checks
- Configurable interval (hourly/daily/weekly/monthly)
- Celery integration for distributed execution
- Fallback to direct execution if Celery unavailable
- Concurrent check limit (default: 5)

---

## 5. DATABASE & STORAGE PATTERNS

### 5.1 Firestore Database Schema

**Collections:**
- `users` - User accounts
- `reports` - Report metadata & results
- `monitors` - Monitor configurations
- `monitor_snapshots` - Time-series data (compressed)
- `alerts` - Alert instances
- `alert_feedback` - User feedback on alerts
- `api_keys` - API key management

**Example - Monitor Document:**
```json
{
  "id": "uuid",
  "user_id": "user_uuid",
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "config": {
    "frequency": "daily",
    "frameworks": ["porter", "swot"],
    "alert_threshold": 0.7,
    "notification_channels": ["email", "slack"]
  },
  "status": "active",
  "created_at": "2024-11-09T...",
  "last_check": "2024-11-09T...",
  "total_alerts": 42,
  "error_count": 2
}
```

### 5.2 Cloud Storage (GCS)

**Bucket: `consultantos-reports`**
- PDF reports: `{report_id}.pdf`
- Private by default (access via signed URLs)
- 1-hour expiration on signed URLs
- Metadata: report_id, uploaded_at, content_type

### 5.3 Caching Strategy (Multi-Level)

**Level 1: Disk Cache (diskcache)**
- Persistent across restarts
- Location: `/tmp/consultantos_cache`
- Size limit: 1GB
- TTL: configurable (default: 3600s)

**Level 2: Semantic Vector Cache (ChromaDB)**
- Embedding-based deduplication
- Location: `/tmp/consultantos_chroma`
- Collection: `analysis_cache`
- For similar query clustering

**Level 3: In-Memory**
- Alert dedup cache (recent alerts)
- Ticker resolution cache

---

## 6. API STRUCTURE

### 6.1 Route Organization

**Core Endpoints:**
```
POST   /analyze              # Sync analysis
POST   /analyze/async        # Async analysis (returns job_id)
POST   /integration/comprehensive-analysis  # Full-featured analysis
GET    /jobs/{job_id}       # Job status
GET    /reports/{report_id} # Report retrieval
```

**Advanced Analytics Endpoints:**
```
POST   /forecasting/multi-scenario  # Multi-scenario forecasting
POST   /wargaming/simulate          # Competitive scenario simulation
POST   /wargaming/scenarios         # Create scenario
GET    /wargaming/scenarios         # List scenarios
GET    /social-media/insights       # Social media analysis
POST   /dark-data/extract          # Dark data extraction
POST   /conversational/chat         # Conversational AI
GET    /api/strategic-intelligence/{company}  # Strategic intelligence
```

**Monitoring Endpoints:**
```
POST   /monitors             # Create monitor
GET    /monitors             # List monitors
GET    /monitors/{id}        # Get monitor
PATCH  /monitors/{id}        # Update config
DELETE /monitors/{id}        # Delete/pause
GET    /monitors/{id}/alerts # Get alerts
POST   /monitors/{id}/check  # Manual trigger
POST   /monitors/{id}/feedback # Alert feedback
```

**User/Auth Endpoints:**
```
POST   /auth/register        # User registration
POST   /auth/login           # User login
POST   /auth/api-keys        # API key management
GET    /profile              # User profile
```

**Analytics Endpoints:**
```
GET    /analytics/summary    # Dashboard statistics
GET    /analytics/trends     # Historical trends
POST   /analytics/query      # Custom analytics
```

### 6.2 Middleware Stack

```
CORSMiddleware (origins configurable)
GZipMiddleware (compression for large responses)
SessionMiddleware (session management)
RateLimiter (slowapi - default 10 req/hour/IP)
RequestLogging (structured logging)
ErrorHandler (HTTPException → JSON)
```

### 6.3 Authentication

**Patterns:**
1. **API Key** (X-API-Key header or ?api_key=)
2. **JWT** (for user sessions)
3. **Optional** (some endpoints public)

**DatabaseService Methods:**
- `get_api_key()` - validate API key
- `create_api_key()` - generate new key
- `check_password()` - password validation

---

## 7. FRONTEND ARCHITECTURE

### 7.1 Tech Stack
- **Framework**: Next.js 14 (app directory)
- **Styling**: Tailwind CSS
- **State**: React Query (@tanstack/react-query)
- **UI Components**: Custom (Card, Button, Modal, DataTable, etc.)
- **Charts**: Plotly (PlotlyChart component)
- **Icons**: lucide-react

### 7.2 Page Structure

```
frontend/app/
├── page.tsx              # Home/landing
├── layout.tsx            # Root layout with Navigation
├── globals.css           # Tailwind styles
├── providers.tsx         # React Query setup
├── dashboard/
│   ├── page.tsx         # Monitor dashboard (main feature)
│   └── [id]/
│       └── page.tsx     # Monitor detail view
├── analysis/
│   └── page.tsx         # One-off analysis form
├── reports/
│   ├── page.tsx         # Report history
│   └── [id]/
│       └── page.tsx     # Report viewer
├── templates/
│   └── page.tsx         # Saved templates
├── jobs/
│   └── page.tsx         # Job queue status
├── components/
│   ├── Navigation.tsx    # Top nav bar
│   ├── AnalysisRequestForm.tsx
│   ├── MonitoringDashboard.tsx
│   ├── DataTable.tsx     # Reusable table component
│   ├── PlotlyChart.tsx
│   └── [other 60+ components]
├── hooks/
│   ├── useKeyboardShortcuts.ts
│   └── useWebSocket.ts
└── api/
    └── notifications.ts  # Client-side API handler
```

### 7.3 Key Components

**Navigation Component:**
- Top nav with logo
- Links to main sections
- User menu (profile, logout)
- Search bar (quick analysis)

**Dashboard Page:**
- Monitor list with status indicators
- Recent alerts feed
- Statistics cards (total, active, unread)
- New monitor button
- Filter/sort options

**AnalysisRequestForm:**
- Company/industry inputs
- Framework multi-select
- Depth selector (quick/standard/deep)
- Submit button
- Results display area

**DataTable Component:**
- Sortable columns
- Pagination
- Filtering
- Row selection
- Export options

### 7.4 API Integration Pattern

```typescript
// Client uses React Query
useQuery({
  queryKey: ['monitors'],
  queryFn: async () => {
    const response = await fetch('/monitors', {
      headers: { 'X-API-Key': apiKey }
    });
    return response.json();
  },
  refetchInterval: 30000  // Poll every 30s
});
```

---

## 8. KEY DESIGN PATTERNS

### 8.1 Agent Pattern
- Base class with common infrastructure
- Subclasses implement specific logic
- Timeout management per agent
- Error handling & monitoring

### 8.2 Orchestrator Pattern
- Coordinates multi-step workflows
- Manages phase dependencies
- Graceful degradation
- Cache integration

### 8.3 Circuit Breaker Pattern
- Prevents cascading failures
- Failure threshold + recovery timeout
- Used for external API calls (Tavily)

### 8.4 Decorator Pattern
- `@cached_analysis()` - caching decorator
- `@asyncio.timeout()` - timeout handling
- `@track_operation()` - Sentry monitoring

### 8.5 Dependency Injection
- `get_orchestrator()` - singleton orchestrator
- `get_database_service()` - database abstraction
- `get_cache_service()` - cache abstraction

### 8.6 Repository Pattern
- `DatabaseService` abstracts Firestore
- Methods: get, create, update, delete
- In-memory fallback for dev/testing

### 8.7 Factory Pattern
- `get_tavily_client()` - lazy client initialization
- `_get_chroma_collection()` - ChromaDB initialization
- Prevents unnecessary instantiation

---

## 9. ERROR HANDLING & RESILIENCE

### 9.1 Graceful Degradation

**Phase 1 Execution:**
- If 1-2 agents fail: continue with partial results
- If all 3 agents fail: raise exception
- Adjust confidence score: -10% per failure (min 0.3)

**Phase 2 Execution:**
- Framework agent returns empty analysis if Phase 1 data missing
- Logs warnings for missing data

**Phase 3 Execution:**
- Synthesis agent always completes
- May use reduced context

### 9.2 Error Tracking (Sentry)

**Breadcrumbs:**
- Agent start/completion
- Cache hits/misses
- API calls
- User actions

**Transactions:**
- Agent execution duration
- Orchestration timeline
- Phase completion

**Tags:**
- `agent_name`: which agent
- `error_type`: timeout, validation, API error
- `company`: for context

### 9.3 Validation

**Input Validation:**
- `AnalysisRequestValidator` - schema validation
- Pydantic models - type checking
- Sanitization - XSS prevention

**Output Validation:**
- Pydantic model validation
- Schema validation via Pandera
- Confidence score validation (0-1)

---

## 10. PERFORMANCE & SCALABILITY

### 10.1 Concurrency

**Parallel Execution:**
- Phase 1: 3 agents run simultaneously
- Max concurrent monitors: configurable (default: 5)
- asyncio.gather() for orchestration

**Threading:**
- Database client: singleton with thread-local access
- Cache: double-checked locking pattern
- No global state mutations

### 10.2 Caching Impact

**Disk Cache:**
- 1GB size limit
- TTL: 3600s (1 hour)
- Hit rate: ~60-70% for repeated analyses

**Semantic Cache:**
- ChromaDB for embedding similarity
- Reduces API calls
- Deduplicates similar queries

### 10.3 Database Optimization

**Compression:**
- Snapshots: zlib compression >1KB
- Batch compression every 10 snapshots
- 60% storage reduction

**Indexing:**
- Firestore composite indexes
- Monitor queries by user_id + status
- Alert queries by monitor_id + created_at

### 10.4 Latency Profile

| Operation | Latency | Bottleneck |
|-----------|---------|-----------|
| Cache hit | 50ms | Disk I/O |
| Phase 1 | 30-60s | API calls (Tavily, yfinance) |
| Phase 2 | 10-20s | LLM token generation |
| Phase 3 | 5-10s | LLM synthesis |
| Total | 45-90s | Phase 1 timeout |

---

## 11. MONITORING & OBSERVABILITY

### 11.1 Logging

**Structured Logging:**
```python
logger.info(
    "analysis_completed",
    extra={
        "report_id": "uuid",
        "company": "Tesla",
        "execution_time": 45.2,
        "frameworks": ["porter", "swot"]
    }
)
```

**Log Levels:**
- DEBUG: Detailed execution
- INFO: Operation milestones
- WARNING: Degraded execution, retries
- ERROR: Failures, exceptions

### 11.2 Metrics

**Prometheus Metrics:**
- Request count by endpoint
- Execution time histograms
- Error count by type
- Cache hit/miss rate
- Agent execution times

**Custom Metrics:**
- Analyses per hour
- Monitor check success rate
- Alert generation rate
- Confidence score distribution

### 11.3 Tracing

**Sentry Integration:**
- Transaction tracking (agent execution)
- Performance monitoring
- Error grouping
- Release tracking

---

## 12. SECURITY CONSIDERATIONS

### 12.1 API Key Management

**Storage:**
- Hashed in Firestore (bcrypt or similar)
- Never logged in plaintext
- Rotate via admin dashboard

**Usage:**
- Rate limiting per key
- Usage tracking
- Audit trail of API calls

### 12.2 Data Protection

**Input Sanitization:**
- `sanitize_string()` - XSS prevention
- Input validation via Pydantic
- SQL injection prevention (Firestore)

**Output Security:**
- No secrets in error messages
- Signed URLs for PDF downloads (1-hour expiration)
- Private Cloud Storage buckets

### 12.3 CORS & Session

**CORS Configuration:**
- Whitelisted origins (configurable)
- Credentials allowed
- Methods: GET, POST, PATCH, DELETE

**Sessions:**
- SessionMiddleware for session tracking
- Cookie-based or token-based
- HTTPS enforced in production

---

## 13. DEPLOYMENT ARCHITECTURE

### 13.1 Cloud Run (GCP)

```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=...,TAVILY_API_KEY=..."
```

**Configuration:**
- 2 CPU, 2Gi RAM per instance
- 300s timeout (for long analyses)
- Auto-scaling (0-100 instances)
- Cold start: ~10s

### 13.2 Background Processing

**Option A: Cloud Tasks (Simple)**
- Queue-based job processing
- Direct integration with Cloud Run

**Option B: Celery + Redis (Scalable)**
- Distributed task queue
- Priority-based execution
- Retry logic with exponential backoff
- Dead letter queue for failed tasks

### 13.3 Frontend Deployment

**Vercel (Recommended)**
```bash
npm run build
vercel deploy
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- Auth tokens (if needed)

---

## 14. DATA CONSISTENCY & TRANSACTIONS

### 14.1 Snapshot Lifecycle

```
New Monitor Created
    ├── Run initial analysis
    ├── Store snapshot in Firestore
    ├── Index by created_at
    └── Ready for comparisons

Scheduled Check
    ├── Run new analysis
    ├── Compare with previous snapshot
    ├── Detect changes
    ├── Store new snapshot
    └── Generate alerts if needed
```

### 14.2 Alert Deduplication

**Hash-Based:**
```python
alert_hash = hashlib.md5(
    f"{monitor_id}:{change_type}:{metric_name}".encode()
).hexdigest()
```

**Throttling:**
- Critical (8.0+): 1h window
- Default: 4h window
- Low (<2.0): 24h window

---

## 15. EXTENSION POINTS

### 15.1 Custom Agents

Add new agent by:
1. Subclass `BaseAgent`
2. Implement `_execute_internal()`
3. Return Pydantic model
4. Add to orchestrator phase

### 15.2 Custom Frameworks

Extend `FrameworkAgent`:
1. Add prompt template in `prompts.py`
2. Define Pydantic response model
3. Update framework validation
4. Add to UI framework selector

### 15.3 Custom Notification Channels

Create channel by:
1. Subclass `BaseChannel`
2. Implement `send()`
3. Register in `AlertingService`
4. Add to notification preferences

### 15.4 Custom Metrics

Add to monitoring:
1. Define metric collection logic
2. Implement Prometheus export
3. Add dashboard visualization
4. Configure alerting rules

---

## SUMMARY TABLE

| Layer | Component | Technology | Key Pattern |
|-------|-----------|-----------|------------|
| **Agents** | 10+ specialized agents | Python + Gemini | Orchestrator + Base class |
| **Orchestration** | AnalysisOrchestrator | asyncio + Pydantic | 3-phase execution + cache |
| **Advanced Analytics** | Forecasting, Wargaming | NumPy + SciPy | Monte Carlo simulation |
| **Conversational AI** | RAG-based chat | ChromaDB + Gemini | Vector retrieval + routing |
| **Social Media** | Sentiment analysis | Reddit + Twitter + Grok | Multi-platform aggregation |
| **Monitoring** | IntelligenceMonitor | Prophet + scoring | Change detection + alerts |
| **Database** | Firestore | Google Cloud | Document-based + indexing |
| **Cache** | Disk + Semantic | diskcache + ChromaDB | Multi-level + TTL |
| **Storage** | Cloud Storage | Google Cloud | Signed URLs + compression |
| **API** | FastAPI | Python | Router + middleware |
| **Frontend** | Next.js 14 | React + Tailwind | Component-based + React Query |
| **Jobs** | Job queue + workers | Async + Celery | Queue pattern + retries |
| **Observability** | Sentry + Prometheus | Observability stack | Transactions + metrics |

---

## ARCHITECTURE STRENGTHS

1. **Scalable Multi-Agent**: Independent agents with timeout + graceful degradation
2. **Advanced Analytics**: Monte Carlo simulation, statistical validation, multi-scenario forecasting
3. **Intelligent Caching**: Multi-level cache reduces API calls significantly
4. **Conversational AI**: RAG-based retrieval with intelligent query routing
5. **Real-time Monitoring**: Continuous intelligence with smart alerting
6. **Error Resilience**: Circuit breakers, retries, partial result handling
7. **Modular Design**: Clear separation of concerns (agents, tools, orchestrator, API)
8. **Observable**: Comprehensive logging, Sentry integration, Prometheus metrics
9. **Cloud Native**: GCP-integrated, scalable, serverless-ready
10. **Comprehensive Intelligence**: Social media, dark data, wargaming, forecasting capabilities

---

## ARCHITECTURE WEAKNESSES & IMPROVEMENTS

1. **Agent Timeout Coupling**: All agents have same 60s timeout (could be per-agent)
2. **Cache Invalidation**: No explicit TTL-based cache invalidation
3. **No Circuit Breaker on Gemini**: Only Tavily has circuit breaker
4. **Limited Rate Limiting**: Per-IP rate limiting, no per-user quotas
5. **Monitoring Backpressure**: No queue depth limits for monitoring checks
6. **Blockchain/Event Sourcing**: No event log for audit trail

---

