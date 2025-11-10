# ConsultantOS - Architecture Diagrams & Visual Flows

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CONSULTANTOS PLATFORM                          │
└─────────────────────────────────────────────────────────────────────────┘

                              FRONTEND LAYER
                          (Next.js 14 + React)
                    ┌─────────────────────────────┐
                    │   Dashboard/Analysis/       │
                    │   Monitoring UI             │
                    │ (React Query + Tailwind)    │
                    └──────────────┬──────────────┘
                                   │
                    HTTP/REST (FastAPI)
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
    ┌───▼────┐              ┌─────▼─────┐          ┌─────────▼────┐
    │ /analyze│              │ /monitors │          │ /auth, /jobs │
    │ Endpoints              │ Endpoints  │          │ Other routes │
    └────┬────┘              └──────┬────┘          └──────┬───────┘
         │                         │                       │
         └──────────────┬──────────┴───────────────────────┘
                        │
              ┌─────────▼────────────┐
              │   MIDDLEWARE STACK   │
              │  CORS, Rate Limit,   │
              │  Auth, Error Handle  │
              └──────────┬───────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   ┌────▼────────────┐      ┌────────────▼────────┐
   │ ORCHESTRATOR    │      │ INTELLIGENCE MONITOR │
   │ 3-Phase         │      │ Change Detection     │
   │ Execution       │      │ Anomaly Detection    │
   │                 │      │ Alert Scoring        │
   └────┬────────────┘      └────────────┬────────┘
        │                                 │
        │         ┌───────────────────────┘
        │         │
    ┌───▼─────────▼────────────────────────────┐
    │        MULTI-AGENT SYSTEM                │
    ├──────────────────────────────────────────┤
    │ Phase 1 (Parallel):                      │
    │  • ResearchAgent     (Tavily web search) │
    │  • MarketAgent       (Google Trends)     │
    │  • FinancialAgent    (yfinance/Finnhub) │
    │                                          │
    │ Phase 2 (Sequential):                    │
    │  • FrameworkAgent    (Porter/SWOT/etc)   │
    │                                          │
    │ Phase 3 (Synthesis):                     │
    │  • SynthesisAgent    (Executive summary)  │
    └──────────────────────────────────────────┘
         │              │
         │         ┌────▼─────┐
         │         │BACKGROUND │
         │         │  WORKERS  │
         │         │           │
         │         │ Analysis  │
         │         │ Monitoring│
         │         └────┬──────┘
         │              │
    ┌────▼──────────────▼────────┐
    │      PERSISTENCE LAYER     │
    ├────────────────────────────┤
    │ • Firestore (documents)    │
    │ • Cloud Storage (PDFs)     │
    │ • Cache (disk + semantic)  │
    └────────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │   EXTERNAL DATA SOURCES       │
    ├──────────────────────────────┤
    │ • Tavily API (web search)    │
    │ • pytrends (Google Trends)   │
    │ • yfinance (stocks)          │
    │ • Finnhub (analyst data)     │
    │ • Alpha Vantage (technical)  │
    │ • Gemini API (LLM)           │
    └───────────────────────────────┘
```

---

## 2. Agent Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ USER REQUEST: POST /analyze or /monitors                        │
│ {company: "Tesla", frameworks: ["porter", "swot"], depth: ...}  │
└────────────────────────┬────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │  INPUT VALIDATION   │
              │ & Sanitization      │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  CACHE LOOKUP       │
              │ (Disk + Semantic)   │◄─────────┐
              └──────────┬──────────┘          │
                    NO  │  YES (HIT)          │
                        ▼                     │
         ┌──────────────────────────┐         │
         │   PHASE 1: PARALLEL      │         │
         │   DATA GATHERING (60s)   │         │
         │                          │         │
         │  ┌──────────────────┐    │         │
         │  │ ResearchAgent    │    │         │
         │  │ (Tavily search)  │    │         │
         │  └──────┬───────────┘    │         │
         │         │                 │         │
         │  ┌──────▼───────────┐    │         │
         │  │ MarketAgent      │    │         │
         │  │ (Google Trends)  │    │         │
         │  └──────┬───────────┘    │         │
         │         │                 │         │
         │  ┌──────▼───────────┐    │         │
         │  │ FinancialAgent   │    │         │
         │  │ (yfinance/Finnhub)   │         │
         │  └──────┬───────────┘    │         │
         │         │                 │         │
         └────────┬┴─────────────────┘         │
                  │                            │
         ┌────────▼────────────┐              │
         │ asyncio.gather()    │              │
         │ - errors trapped    │              │
         │ - timeouts handled  │              │
         │ - continue if 1-2   │              │
         │   agents fail       │              │
         └────────┬────────────┘              │
                  │                            │
         ┌────────▼─────────────────┐         │
         │  PHASE 2: SEQUENTIAL     │         │
         │  FRAMEWORK ANALYSIS      │         │
         │                          │         │
         │  ┌──────────────────┐    │         │
         │  │ FrameworkAgent   │    │         │
         │  │ • Porter's 5F    │    │         │
         │  │ • SWOT           │    │         │
         │  │ • PESTEL         │    │         │
         │  │ • Blue Ocean     │    │         │
         │  │ (20s timeout)    │    │         │
         │  └──────┬───────────┘    │         │
         └────────┬┴────────────────┘         │
                  │                            │
         ┌────────▼─────────────────┐         │
         │  PHASE 3: SYNTHESIS      │         │
         │                          │         │
         │  ┌──────────────────┐    │         │
         │  │ SynthesisAgent   │    │         │
         │  │ Executive Summary│    │         │
         │  │ Confidence Score │    │         │
         │  │ Next Steps       │    │         │
         │  └──────┬───────────┘    │         │
         └────────┬┴────────────────┘         │
                  │                            │
         ┌────────▼──────────────────┐        │
         │ REPORT ASSEMBLY           │        │
         │ - Combine all components  │        │
         │ - Adjust confidence       │        │
         │ - Add metadata            │        │
         │ - Return StrategicReport  │        │
         └────────┬───────────────────┘       │
                  │                            │
         ┌────────▼──────────────────┐        │
         │ CACHE STORAGE             │        │
         │ (Disk + Semantic)         │────────┘
         └────────┬───────────────────┘
                  │
         ┌────────▼──────────────────┐
         │ RESPONSE TO CLIENT        │
         │ - JSON Report             │
         │ - Optional PDF            │
         │ - Signed URLs             │
         └───────────────────────────┘
```

---

## 3. Monitoring & Change Detection Flow

```
┌────────────────────────────────────────────────────────┐
│ USER CREATES MONITOR: POST /monitors                    │
│ {company: "Tesla", config: {...}}                      │
└─────────────────────────┬────────────────────────────────┘
                          │
                ┌─────────▼────────┐
                │ MONITOR CREATION │
                │                  │
                │ • Validate inputs│
                │ • Run baseline   │
                │   analysis       │
                │ • Store snapshot │
                │ • Schedule checks│
                └─────────┬────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
    ┌──────▼──────┐         ┌────────────▼─────────┐
    │ DASHBOARD   │         │ BACKGROUND WORKER    │
    │ - Monitor   │         │ MonitoringWorker     │
    │   list      │         │                      │
    │ - Status    │         │ Check interval:      │
    │   indicators│         │ hourly/daily/weekly/ │
    │ - Recent    │         │ monthly              │
    │   alerts    │         │                      │
    └─────────────┘         └────────────┬─────────┘
                                         │
                  ┌──────────────────────┴──────────────────┐
                  │  SCHEDULED MONITOR CHECKS               │
                  │                                         │
                  │  For each active monitor:               │
                  │                                         │
       ┌──────────▼────────────────────────────┐            │
       │  1. RUN NEW ANALYSIS                  │            │
       │     (via AnalysisOrchestrator)        │            │
       │  → StrategicReport                    │            │
       └──────────┬────────────────────────────┘            │
                  │                                          │
       ┌──────────▼────────────────────────────┐            │
       │  2. COMPARE SNAPSHOTS                 │            │
       │     (SnapshotAggregator)              │            │
       │  → Previous vs Current metrics        │            │
       │  → Detect metric changes              │            │
       │  → Calculate change confidence        │            │
       └──────────┬────────────────────────────┘            │
                  │                                          │
       ┌──────────▼────────────────────────────┐            │
       │  3. ANOMALY DETECTION                 │            │
       │     (AnomalyDetector + Prophet)       │            │
       │  → Time-series analysis               │            │
       │  → Detect unusual patterns            │            │
       │  → 4 types: point/contextual/         │            │
       │    trend_reversal/volatility_spike    │            │
       └──────────┬────────────────────────────┘            │
                  │                                          │
       ┌──────────▼────────────────────────────┐            │
       │  4. ALERT SCORING                     │            │
       │     (AlertScorer)                     │            │
       │  → Priority (0-10)                    │            │
       │  → Urgency (critical/high/med/low)    │            │
       │  → Deduplication (hash-based)         │            │
       │  → Throttling (1h/4h/24h windows)     │            │
       │  → Max 5 alerts/day                   │            │
       └──────────┬────────────────────────────┘            │
                  │                                          │
         ┌────────▼────────┐                                │
         │ IF should_notify│                                │
         └────────┬────────┘                                │
                  │                                          │
      ┌───────────┼───────────────────────────┐            │
      │           │                           │             │
   ┌──▼──┐  ┌────▼────┐  ┌──────┐  ┌────────▼──┐          │
   │Email│  │ Slack   │  │In-App│  │ Webhook  │          │
   │ SMTP│  │ Webhook │  │Store │  │ Callback │          │
   └─────┘  └─────────┘  └──────┘  └──────────┘          │
      │           │           │           │                │
      └───────────┼───────────┴───────────┘                │
                  │                                          │
          ┌───────▼──────────┐                             │
          │ ALERT CREATED    │                             │
          │ - Store in DB    │                             │
          │ - Log & track    │                             │
          │ - Notify user    │                             │
          └───────┬──────────┘                             │
                  │                                          │
          ┌───────▼──────────┐                             │
          │ STORE SNAPSHOT   │                             │
          │ - Compress >1KB  │                             │
          │ - Batch compress │                             │
          │ - Index by date  │                             │
          └──────────────────┘                             │
                  │                                          │
                  └──────────────────────────────────────────┘
```

---

## 4. Data Model Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                     PYDANTIC MODELS                         │
└─────────────────────────────────────────────────────────────┘

INPUT
  └─ AnalysisRequest
      ├─ company: str
      ├─ industry: Optional[str]
      ├─ frameworks: List[str]
      └─ depth: str

PHASE 1 OUTPUTS (Parallel)
  ├─ CompanyResearch (ResearchAgent)
  │   ├─ company_name, description, products_services
  │   ├─ target_market, key_competitors, recent_news
  │   └─ NLP fields: entities, sentiment, keywords
  │
  ├─ MarketTrends (MarketAgent)
  │   ├─ search_interest_trend
  │   ├─ geographic_distribution
  │   └─ competitive_comparison
  │
  └─ FinancialSnapshot (FinancialAgent)
      ├─ ticker, market_cap, revenue, profit_margin
      ├─ analyst_recommendations, news_sentiment
      └─ data_source_validation[]

PHASE 2 OUTPUTS (Sequential)
  └─ FrameworkAnalysis (FrameworkAgent)
      ├─ porter_five_forces
      ├─ swot_analysis
      ├─ pestel_analysis
      └─ blue_ocean_strategy

PHASE 3 OUTPUTS (Synthesis)
  └─ ExecutiveSummary (SynthesisAgent)
      ├─ overview: str
      ├─ key_insights: List[str]
      ├─ risks: List[str]
      ├─ opportunities: List[str]
      ├─ next_steps: List[str]
      └─ confidence_score: float

COMPOSITE OUTPUT
  └─ StrategicReport
      ├─ executive_summary: ExecutiveSummary
      ├─ company_research: CompanyResearch
      ├─ market_trends: MarketTrends
      ├─ financial_snapshot: FinancialSnapshot
      ├─ framework_analysis: FrameworkAnalysis
      ├─ recommendations: List[str]
      └─ metadata: Dict

MONITORING MODELS
  ├─ Monitor
  │   ├─ id, user_id, company, industry
  │   ├─ config: MonitoringConfig
  │   ├─ status: MonitorStatus
  │   └─ created_at, last_check, next_check
  │
  ├─ Alert
  │   ├─ id, monitor_id, title, summary
  │   ├─ confidence: float
  │   ├─ changes_detected: List[Change]
  │   └─ created_at, read, user_feedback
  │
  ├─ Change
  │   ├─ change_type: ChangeType
  │   ├─ title, description
  │   ├─ confidence, source_urls
  │   └─ previous_value, current_value
  │
  ├─ MonitorAnalysisSnapshot
  │   ├─ monitor_id, created_at
  │   ├─ analysis_result: Dict
  │   ├─ compressed: bool
  │   └─ compression_ratio: float
  │
  └─ AnomalyScore
      ├─ metric_name, anomaly_type
      ├─ severity, confidence
      ├─ forecast_value, actual_value
      └─ statistical_details: Dict
```

---

## 5. Cache Strategy

```
┌─────────────────────────────────────────────────────┐
│           MULTI-LEVEL CACHING STRATEGY              │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────▼───────────┐
        │  LAYER 3: IN-MEMORY  │
        │  (No persistence)    │
        │ • Alert dedup        │
        │ • Ticker cache       │
        │ • Recent alerts (5m) │
        └──────────┬───────────┘
                   │
        ┌──────────▼──────────────────┐
        │  LAYER 2: SEMANTIC CACHE    │
        │  (ChromaDB)                 │
        │ • /tmp/consultantos_chroma  │
        │ • Embedding similarity      │
        │ • Dedup similar queries     │
        │ • TTL: 24 hours             │
        │ • Hit rate: ~30%            │
        └──────────┬───────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  LAYER 1: DISK CACHE        │
        │  (diskcache, persistent)    │
        │ • /tmp/consultantos_cache   │
        │ • Size limit: 1GB           │
        │ • TTL: 3600s (1 hour)       │
        │ • Hit rate: ~60-70%         │
        │ • Survives restarts         │
        └──────────┬───────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  CACHE KEY GENERATION       │
        │                             │
        │  MD5(company:frameworks:    │
        │      industry)              │
        │                             │
        │  Example:                   │
        │  "tesla:porter:swot:ev"     │
        │  → 5f3k2a1b9c8d7e...       │
        └──────────┬───────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  CACHE HIT PROCESS          │
        │                             │
        │  1. Check in-memory         │
        │  2. Check disk (0.5s)       │
        │  3. Check semantic (1s)     │
        │  4. Return if found         │
        │  5. Otherwise: full exec    │
        └──────────────────────────────┘
```

---

## 6. Error Recovery & Resilience

```
┌─────────────────────────────────────────────────────┐
│         ERROR HANDLING & GRACEFUL DEGRADATION       │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────▼──────────────────┐
        │  PHASE 1: PARALLEL AGENTS   │
        │                             │
        │  3 agents running:          │
        │  ResearchAgent              │
        │  MarketAgent                │
        │  FinancialAgent             │
        └──────────┬───────────────────┘
                   │
       ┌───────────┼───────────────┐
       │           │               │
    ┌──▼──┐    ┌───▼───┐    ┌─────▼──┐
    │FAIL?│    │FAIL?  │    │FAIL?   │
    └──┬──┘    └───┬───┘    └────┬───┘
       │           │             │
    NO│    NO│    NO│
       │      │      │
       │      │      └──────────┐
       │      └───────────────┐ │
       │                      │ │
       │  ┌──────────────────┐│ │
       │  │ ALL AGENTS OK?   ││ │
       │  │ YES → Continue   ││ │
       │  └────────────┬─────┘│ │
       │               │      │ │
       │               ▼      │ │
       │         ┌─────────┐  │ │
       │         │CONTINUE │  │ │
       │         │PHASE 2  │  │ │
       │         └─────────┘  │ │
       │                      │ │
       │     ┌────────────────┘ │
       │     │                  │
       │  ┌──▼──────────────────▼──┐
       │  │1-2 AGENTS FAILED?      │
       │  │YES → Use partial data  │
       │  │• Log warning           │
       │  │• Continue with Phase 2 │
       │  └──┬─────────────────────┘
       │     │
       │  ┌──▼───────────────────┐
       │  │CONFIDENCE PENALTY     │
       │  │• Base: 0.7 (70%)      │
       │  │• Per failure: -10%    │
       │  │• Minimum: 0.3 (30%)   │
       │  └──┬──────────────────┘
       │     │
       └─────┤
             │
       ┌─────▼───────────────────┐
       │ ALL AGENTS FAILED?      │
       │ YES → RAISE EXCEPTION   │
       │ "Cannot proceed"        │
       └─────────────────────────┘
```

---

## 7. Frontend Component Hierarchy

```
┌─────────────────────────────────────────────────────┐
│              NEXT.JS 14 COMPONENT TREE               │
└──────────────────┬──────────────────────────────────┘
                   │
           ┌───────▼────────┐
           │  Root Layout   │
           │ (Global CSS)   │
           │ (Navigation)   │
           └───────┬────────┘
                   │
        ┌──────────┼───────────────────────┐
        │          │                       │
     ┌──▼──┐   ┌───▼────┐         ┌────────▼─┐
     │Page │   │Analysis│         │Templates │
     │(/)  │   │(/analy)│         │(/templat)│
     └──────   └───────┘         └──────────┘
        │
     ┌──▼───────────┐
     │ Dashboard    │
     │ (/dashboard) │
     │              │
     │ ┌─────────┐  │
     │ │Monitors │  │
     │ │  List   │  │
     │ └────┬────┘  │
     │      │       │
     │ ┌────▼────┐  │
     │ │ Alerts  │  │
     │ │  Feed   │  │
     │ └────┬────┘  │
     │      │       │
     │ ┌────▼────┐  │
     │ │Stats    │  │
     │ │Cards    │  │
     │ └─────────┘  │
     └──────────────┘

Components (Reusable):
  ├─ Navigation (top bar)
  ├─ DataTable (sortable/paginated)
  ├─ Card (layout wrapper)
  ├─ Button (primary/secondary)
  ├─ Modal (dialog)
  ├─ Tabs (tabbed navigation)
  ├─ PlotlyChart (data visualization)
  ├─ Alert (notifications)
  └─ Spinner (loading state)

Hooks (Custom):
  ├─ useKeyboardShortcuts (kbd events)
  ├─ useWebSocket (real-time updates)
  └─ useQuery (React Query integration)
```

---

## 8. Database Schema (Firestore)

```
┌────────────────────────────────────────────────────┐
│              FIRESTORE COLLECTIONS                 │
└────────────────────────────────────────────────────┘

users/
  └─ {user_id}
      ├─ email: string
      ├─ password_hash: string
      ├─ created_at: timestamp
      └─ subscription_tier: string

monitors/
  └─ {monitor_id}
      ├─ user_id: string
      ├─ company: string
      ├─ industry: string
      ├─ config: object
      │   ├─ frequency: enum
      │   ├─ frameworks: array
      │   ├─ alert_threshold: number
      │   └─ notification_channels: array
      ├─ status: enum (active/paused/deleted/error)
      ├─ created_at: timestamp
      ├─ last_check: timestamp
      ├─ next_check: timestamp
      ├─ total_alerts: number
      └─ error_count: number

monitor_snapshots/
  └─ {snapshot_id}
      ├─ monitor_id: string
      ├─ created_at: timestamp
      ├─ analysis_result: object (compressed)
      ├─ compressed: boolean
      └─ compression_ratio: number

alerts/
  └─ {alert_id}
      ├─ monitor_id: string
      ├─ user_id: string
      ├─ title: string
      ├─ summary: string
      ├─ confidence: number
      ├─ changes_detected: array
      │   └─ Change objects
      ├─ created_at: timestamp
      ├─ read: boolean
      ├─ read_at: timestamp
      └─ user_feedback: string

alert_feedback/
  └─ {feedback_id}
      ├─ alert_id: string
      ├─ user_id: string
      ├─ is_accurate: boolean
      ├─ feedback: string
      └─ created_at: timestamp

reports/
  └─ {report_id}
      ├─ user_id: string
      ├─ company: string
      ├─ industry: string
      ├─ frameworks: array
      ├─ status: enum (completed/failed/processing)
      ├─ confidence_score: number
      ├─ execution_time_seconds: number
      ├─ pdf_url: string (signed URL)
      ├─ created_at: timestamp
      └─ error_message: string

api_keys/
  └─ {key_hash}
      ├─ user_id: string
      ├─ description: string
      ├─ created_at: timestamp
      ├─ last_used: timestamp
      ├─ usage_count: number
      └─ active: boolean

Indexes:
  ├─ monitors: (user_id, status)
  ├─ monitor_snapshots: (monitor_id, created_at DESC)
  ├─ alerts: (monitor_id, created_at DESC)
  ├─ alerts: (user_id, read, created_at DESC)
  └─ reports: (user_id, created_at DESC)
```

---

## 9. Agent State Machine

```
┌────────────────────────────────────────┐
│         AGENT EXECUTION LIFECYCLE       │
└────────────────────┬───────────────────┘
                     │
          ┌──────────▼──────────┐
          │  INITIALIZED        │
          │  (BaseAgent.__init__)│
          │                     │
          │ • Gemini configured │
          │ • Instructor setup  │
          │ • Timeout ready     │
          │ • Sentry ready      │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────────┐
          │  EXECUTING             │
          │  (execute() called)    │
          │                        │
          │ • Sentry transaction   │
          │ • Breadcrumb: start    │
          │ • Call _execute_       │
          │   internal()           │
          └──────────┬─────────────┘
                     │
             ┌───────┴────────┐
             │                │
        ┌────▼─────┐    ┌─────▼────┐
        │TIMEOUT?  │    │EXCEPTION?│
        │YES       │    │YES       │
        └────┬─────┘    └─────┬────┘
             │                │
        ┌────▼──────────┐  ┌──▼────────┐
        │TimeoutError   │  │Exception  │
        │ • Log error   │  │ • Log     │
        │ • Breadcrumb  │  │ • Sentry  │
        │ • Sentry tag  │  │ • Re-raise│
        └────┬──────────┘  └──┬────────┘
             │                │
             └────┬───────────┘
                  │
        ┌─────────▼───────────┐
        │  SUCCESS            │
        │  (returned result)  │
        │                     │
        │ • Measure time      │
        │ • Breadcrumb: done  │
        │ • Return result     │
        └─────────┬───────────┘
                  │
        ┌─────────▼───────────┐
        │  COMPLETED          │
        │  (Sentry transaction│
        │   ends)             │
        └─────────────────────┘
```

---

## 10. Request/Response Flow

```
┌──────────────────────────────────────────┐
│  HTTP REQUEST: POST /analyze              │
│  Headers: Content-Type, X-API-Key         │
│  Body: {company, industry, frameworks...} │
└──────────────────────┬────────────────────┘
                       │
            ┌──────────▼──────────┐
            │  MIDDLEWARE STACK   │
            │                     │
            │ • CORS check        │
            │ • Rate limit check  │
            │ • Auth validation   │
            │ • Request logging   │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  INPUT VALIDATION   │
            │                     │
            │ • Schema check      │
            │ • Sanitization      │
            │ • Type casting      │
            │ • Pydantic model    │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  ORCHESTRATOR       │
            │  execute()          │
            │                     │
            │ [3-Phase execution] │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │ StrategicReport     │
            │ assembly            │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────────┐
            │ OPTIONAL: PDF          │
            │ generation             │
            │ (background or sync)   │
            └──────────┬─────────────┘
                       │
            ┌──────────▼──────────────┐
            │ JSON Response           │
            │ {                       │
            │   "report": {...},      │
            │   "pdf_url": "...",     │
            │   "confidence": 0.85    │
            │ }                       │
            └──────────┬──────────────┘
                       │
            ┌──────────▼──────────────┐
            │ HTTP Response (200 OK)  │
            │ Content-Type: JSON      │
            │ GZIP: compressed        │
            └───────────────────────────┘
```

---

## Summary: Data Flow Architecture

```
REQUEST → VALIDATION → ORCHESTRATOR → ANALYSIS → REPORT → RESPONSE
            ↓
         Cache Miss?
            ↓
      Phase 1 (PARALLEL)
      Research | Market | Financial
            ↓
      Phase 2 (SEQUENTIAL)
      Framework Analysis
            ↓
      Phase 3 (SYNTHESIS)
      Executive Summary
            ↓
      CONFIDENCE ADJUSTMENT
      (based on errors)
            ↓
      CACHE STORAGE
            ↓
      PDF GENERATION (optional)
            ↓
      RESPONSE TO CLIENT
```

