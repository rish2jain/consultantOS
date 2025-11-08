# ConsultantOS – Technical Design Document

## Product Overview

ConsultantOS is an AI-powered business analysis platform designed to automate and enhance strategic consulting workflows. Leveraging advanced orchestration (Google ADK), specialized agents, and state-of-the-art NLP, it delivers comprehensive company reports, strategic analysis, and actionable insights on demand. The system targets consultants, analysts, and business leaders who require rapid, data-driven intelligence, offering PDF reports, interactive visualizations, and scalable cloud-based delivery.

---

## Purpose

The primary goal of ConsultantOS is to streamline and augment the business consulting process by automating complex multi-agent analysis and report generation. Key problems addressed include:

- Reducing the time and cost required for thorough company, market, and strategic assessments.

- Improving consistency and accuracy in analytical frameworks (Porter’s Five Forces, SWOT, Blue Ocean).

- Enabling on-demand insights and actionable intelligence for business professionals.

**Example Scenario:** A strategy consultant needs a report on a public company for an upcoming pitch. With ConsultantOS, they initiate an analysis request and receive a detailed strategic report (including financials, market trends, and framework visualizations) within minutes—something that previously could take days.

---

## Target Audience

- **Management Consultants & Analysts:** Need comprehensive, up-to-date analysis and strategic frameworks.

- **Business Leaders & Executives:** Require quick insights for decision support and preparation.

- **Financial Advisors:** Demand secure, automated extraction and synthesis of market/company health.

- **Product Managers & Founders:** Leverage market analysis for product direction and investment pitches.

Pain Points Addressed:

- Manual, time-consuming research

- Siloed or incomplete data sources

- Lack of standardized deliverables

- Difficulty in visualizing and communicating complex analyses

Relevant Market Segments: Consulting firms, investment analysts, SMB executives, product strategy teams, due diligence functions.

---

## Expected Outcomes

- **Tangible Benefits:**

  - Reports generated in minutes instead of days

  - Consistent application of analytical frameworks

  - Data-driven, visualized insights

- **Intangible Benefits:**

  - Lowered consulting costs

  - Better, faster decision-making

  - Enhanced data security and compliance

**Key Metrics/KPIs**

| Metric                      | Target Value                     | Measurement Method                                                | Reporting Cadence       |
| --------------------------- | -------------------------------- | ----------------------------------------------------------------- | ----------------------- |
| **p95 Response Time**       | <60 seconds                      | Track end-to-end analysis completion time (95th percentile)       | Daily dashboard         |
| **p99 Response Time**       | <90 seconds                      | Track end-to-end analysis completion time (99th percentile)       | Daily dashboard         |
| **Throughput**              | 100 requests/minute              | Count successful analysis requests per minute                     | Real-time monitoring    |
| **Concurrent Users**        | 50 simultaneous analyses         | Track active job queue size                                       | Real-time monitoring    |
| **Error Rate**              | ≤1% per 1,000 runs               | Count failed analyses / total requests                            | Hourly alerts if >1%    |
| **Agent Success Rate**      | ≥95% per agent                   | Per-agent task-level success (successful tasks ÷ attempted tasks) | Daily report            |
| **Agent Completion Rate**   | ≥98% overall                     | End-to-end job-level success (all agents in workflow succeed)     | Daily report            |
| **Cache Hit Ratio**         | ≥40%                             | Count cache hits / total requests                                 | Daily dashboard         |
| **Cost per Analysis**       | <$0.50                           | Sum API costs (Tavily, Gemini, Trends) per analysis               | Weekly cost report      |
| **API Response Time (p95)** | <5 seconds                       | Track API endpoint response time (job submission)                 | Real-time monitoring    |
| **Data Freshness**          | ≥80% sources from last 12 months | Analyze source timestamps in research results                     | Weekly quality report   |
| **Framework Quality Score** | ≥6/10 (human rubric)             | Expert review panel scores                                        | Post-release validation |
| **Uptime SLA**              | ≥99% (v0.2.0), ≥99.9% (v1.0.0)   | Track service availability (health check failures)                | Monthly SLO report      |
| **Cold Start Latency**      | <3 seconds                       | Measure time from request to first agent execution                | Daily monitoring        |
| **PDF Generation Time**     | <10 seconds                      | Track ReportLab PDF creation duration                             | Daily report            |

**Measurement Infrastructure**:

- **Real-time**: Google Cloud Monitoring dashboards with 1-minute granularity
- **Daily**: Aggregated metrics exported to BigQuery for trend analysis
- **Weekly**: Cost and quality reports sent to stakeholders
- **Monthly**: SLO compliance and performance review

**Alerting Thresholds**:

| Metric                    | Target | Warning Threshold | Critical Threshold | Rationale                                                                                                     |
| ------------------------- | ------ | ----------------- | ------------------ | ------------------------------------------------------------------------------------------------------------- |
| **Error Rate**            | ≤1%    | >1.5%             | >2%                | Operational tolerance: <1% is acceptable noise; >1.5% indicates degradation; >2% requires immediate attention |
| **p95 Latency**           | <60s   | ≥60s              | ≥90s               | SLA target is <60s; ≥60s breaches SLA; ≥90s indicates severe performance issues                               |
| **p99 Latency**           | <90s   | ≥90s              | ≥120s              | p99 target is <90s; ≥90s breaches target; ≥120s indicates critical performance degradation                    |
| **Agent Success Rate**    | ≥95%   | <93%              | <90%               | Per-agent task success target ≥95%; <93% indicates degradation; <90% requires investigation                   |
| **Agent Completion Rate** | ≥98%   | <96%              | <94%               | End-to-end job success target ≥98%; <96% indicates workflow issues; <94% requires immediate attention         |
| **Cache Hit Ratio**       | ≥40%   | <30%              | <20%               | Target ≥40% for cost efficiency; <30% increases API costs; <20% indicates cache system failure                |
| **Cost per Analysis**     | <$0.50 | >$0.75            | >$1.00             | Target <$0.50 for profitability; >$0.75 reduces margins; >$1.00 indicates cost control failure                |
| **Uptime SLA**            | ≥99%   | <98%              | <97%               | Target ≥99% availability; <98% breaches SLA; <97% indicates critical service degradation                      |

---

## Design Details

### Component Overview

- **Application Layer:** FastAPI app deployed on Google Cloud Run, exposing REST endpoints.

- **Orchestration:** Google ADK (Agent Development Kit) manages agent workflows using LlmAgent, SequentialAgent, and ParallelAgent primitives.

- **Agents:**

  - Research Agent (Tavily search)

  - Market Analyst (Google Trends)

  - Financial Analyst (SEC API/yfinance)

  - Framework Analyst (LLM for strategy frameworks)

  - Synthesis Agent (LLM summarizer)

- **Vector Store:** ChromaDB for semantic storage and retrieval of research snippets and intermediate results.

- **Caching:** Three-tiered approach—in-memory, disk, ChromaDB.

- **Report Generation:** ReportLab for PDF, charts rendered via Plotly then converted by Kaleido.

- **Error Handling:** Graceful fallbacks, timeouts, and custom exception models.

- **Rate Limiting & Background Jobs:** slowapi for client-side rate limiting, FastAPI background tasks for asynchronous report rendering.

---

## Architectural Overview

### High-Level Architecture Diagram

```
   \[Client/UI\]
      |
  \[FastAPI app\]
      |
  \[Google ADK orchestrator\]
      |
-------------------------------------------------
|          |         |         |                |
Research   Market   Financial  Framework       Synthesis
 Agent     Analyst  Analyst    Analyst         Agent
(Tavily)  (Trends) (SEC/yf)   (LLM)           (LLM)
  |          |         |         |                |
      \[Intermediate Data Storage: ChromaDB\]
                          |
            \[ReportLab PDF Generation w/ Plotly\]
                          |
                    \[Google Cloud Storage\]

```

### Design Patterns & Principles

- Orchestration Pattern: Parallel and sequential flows for efficiency and logical dependencies

- Modular Agent Abstraction: Isolated, composable agents

- Repository Pattern: Data/query abstraction via ChromaDB

- Structured Logging & Monitoring

---

## Data Structures and Algorithms

### Key Data Models (Pydantic)

Caching Strategies

- **In-memory (Redis or local LRU)** for request/session-scoped data

- **Disk Cache** for intermediate results

- **ChromaDB (Semantic Vector Store):** Research/document retrieval and duplicate avoidance

Algorithms

- **Data Orchestration:** Parallel phase (gathering), sequential analysis (framework application)

- **Deduplication:** Vector similarity search before invoking costly API calls

- **Sequential/Parallel Flows:** Optimized for timeouts, dependency management, and fallback on slow/failed agents

---

## System Interfaces

### API Endpoints (FastAPI)

Standards & Protocols

- RESTful API conventions

- OpenAPI schema generation (FastAPI native)

- OAuth2/JWT for future authentication integration

### Third-Party & Internal Modules

- **Tavily:** Company/market web search

- **Google Trends:** Market data extraction

- **SEC API, yfinance:** Financial/stock data

- **ChromaDB:** Semantic caching/retrieval

- **ReportLab, Plotly, Kaleido:** PDF and chart generation

---

## User Interfaces

**Core UI Components (for web/mobile frontends not in MVP, but planned):**

- Company Analysis Submission Form

- Request Status / Results Dashboard

- Download Link for Reports

- Trend/Framework Visualizations

**Alignment with User Needs**

- Streamlined, minimalistic interface for submitting requests

- Inline status notifiers for long-running background tasks

- Download and republishing functionality for PDF outputs

---

## Hardware Interfaces

- **Google Cloud Run:** No direct hardware management; autoscaling containerized runtime.

- **Optional Local Development:** CPU/memory specs matching Cloud Run constraints (2 CPU, 2Gi RAM) for parity.

- **No device-specific I/O:** All interaction over HTTP(S) endpoints and service APIs.

---

## Testing Plan

### Test Strategies

- **Unit Testing:** For each specialized agent, PDF/report functions, and data models.

- **Integration Testing:** Simulated end-to-end runs (API–agents–report).

- **API Testing:** Entire endpoints suite, rate limiting, error handling (using TestClient).

- **Edge Cases:** Network/API failures, malformed input, timeouts, and cache misses.

### Testing Tools

- **pytest:** Main Python test runner

- **pytest-asyncio:** For async agent tasks and workflows

- **FastAPI TestClient:** REST endpoint testing

- **Coverage.py:** Enforce/monitor code coverage

- **CI:** GitHub Actions for continuous integration and test automation

### Testing Environments

- **Local Development:** Docker Compose with all dependencies, env mirrors Cloud Run

- **Staging Cloud Run:** Identical to production config, used for integration tests

- **Test Data:** Synthetic and real-world sanitized company data

### Test Cases (Samples)

### Reporting and Metrics

- **Test Metrics:** Pass/fail, duration, code coverage, performance regression

- **Reporting:** CI pipeline output, summarized in dashboards (GitHub Actions, Codecov.io)

- **Alerting:** Slack/email webhook alerts on failures in main/master

---

## Deployment Plan

### Deployment Environment

- **Google Cloud Run:** Containerized app

  - 2 vCPU, 2Gi RAM, 300s request timeout

  - Scale-to-zero for cost efficiency; max 10 concurrent instances

- **Google Secret Manager:** Secrets for API keys, tokens

- **Environment Variables:** Securely manage configs and secrets (auto-injected by deployment scripts)

- **High Availability:** Multi-region support in Cloud Run, health checks, auto-restart

### Deployment Tools

- **Terraform:** (Optional) Infra provisioning

- **Docker:** Container build and local dev matching Cloud Run

- **gcloud CLI:** Deployment automation

- **GitHub Actions:** CI/CD pipelines, push-to-deploy

### Deployment Steps

1. **Build Container:** `docker build -t consultantos:latest .`

2. **Push Image:** `docker push gcr.io/<project>/consultantos:latest`

3. **Deploy to Cloud Run:**

`gcloud run deploy consultantos --image gcr.io/<project>/consultantos:latest --cpu=2 --memory=2Gi --timeout=300 --max-instances=10 --set-secrets ...`

4. **Configure Env & Secret Manager:** Ensure all runtime secrets are linked.

5. **Run Smoke Test:** Invoke `/health` and sample `/analyze` request.

6. **Monitor Logs:** Tail logs via Google Cloud Console or Stackdriver.

7. **Rollback (if needed):**

`gcloud run revisions list && gcloud run services update-traffic consultantos --to-revisions=<prev>`

### Post-Deployment Verification

- **Health Check:** `/health` endpoint

- **Functionality Test:** /analyze and /reports/{id} for real and mock data

- **Secrets Validation:** Ensure all keys correctly injected

- **Performance:** Response time benchmarks

- **Monitoring:** Structured logs; Stackdriver, Google Error Reporting

### Continuous Deployment

- **CI/CD:** All commits to main trigger test and deployment jobs via GitHub Actions

- **Automation:** Scripts push images, update secrets, and validate deployment

- **Benefits:** Quicker iterations, reduced manual steps, continuous security scanning

---

## Google ADK Integration

### API Structure

- Orchestrator uses `ParallelAgent` for phase 1 (Research, Market, Financial data)

- Results passed to `SequentialAgent` for phase 2 (Framework Analysis → Synthesis)

- Every agent conforms to `LlmAgent` interface

- Error handling via timeouts, retry with exponential backoff, and fallback mechanisms

### Workflow

**Phase 1: Parallel Data Gathering**

- Research Agent (Tavily): General web/company search

- Market Analyst (Google Trends): Trending topics, sentiment

- Financial Analyst (SEC/yfinance): Financial metrics

**Phase 2: Sequential Framework Analysis**

- Framework Analyst applies 2–4 frameworks depending on request

- Synthesis Agent generates executive summaries and action recommendations

### Error & Timeout Handling

- Set explicit timeouts (60s agent limit)

- Fallback: If ADK workflow fails, revert to CrewAI agent orchestration

- Store partial results—avoid re-querying APIs if phase 1 succeeds but phase 2 fails

---

## Agent Design

### Research Agent (Tavily)

- **Purpose:** Aggregate latest web and wiki info

- **Tool Integration:** Tavily API

- **Prompts/Instructions:** “Find recent credible sources on \[Company\], focus on news, business profile, innovations.”

- **Model Output:** CompanyResearch

### Market Analyst (Google Trends)

- **Purpose:** Analyze real-time searches & sentiment

- **Tool Integration:** Google Trends API (pytrends)

- **Prompts/Instructions:** “Summarize emerging market/trend data for \[Company/Industry\].”

- **Model Output:** MarketTrends

### Financial Analyst (SEC/yfinance)

- **Purpose:** Extract and summarize company financials

- **Tool Integration:** SEC EDGAR API, yfinance

- **Prompts/Instructions:** “Provide a snapshot of revenue, profit, key ratios for the last 12 quarters.”

- **Model Output:** FinancialSnapshot

### Framework Analyst (LLM)

- **Purpose:** Apply strategic frameworks (Porter’s, SWOT, PESTEL, Blue Ocean)

- **Tool Integration:** LLM (OpenAI/Gemini), vector cache for context

- **Prompts/Instructions:** “Generate a detailed \[Selected Framework\] analysis using supplied data.”

- **Model Output:** FrameworkAnalysis

### Synthesis Agent (LLM)

- **Purpose:** Craft executive summary, recommendations

- **Tool Integration:** LLM with prior stage data/context

- **Instructions:** “Summarize the analysis and deliver key actionable insights.”

- **Model Output:** ExecutiveSummary

---

## Report Generation System

- **PDF Backbone:** ReportLab

- **Charts:** Plotly figures (radar/Pie/Bar/Line), exported as PNG using Kaleido and embedded in PDF

- **Report Structure:**

  1. Cover Page (Title, Summary)

  2. Company Profile (from Research)

  3. Market Trends (charts/tables)

  4. Financial Snapshot (tables/plots)

  5. Framework Analyses (custom visualizations)

  6. Executive Summary & Recommendations

- **Visualization Functions:**

  - Porter’s: Radar chart

  - SWOT: Matrix with quadrant icons

  - Trends: Line/area chart

  - Financials: Multipanel bar/line

- **Fallbacks:** If chart generation fails, include tables/textual summaries; if PDF fails, return HTML fallback

---

## API Design

### Endpoints

### Features

- **Rate Limiting:** slowapi, 10/minute/IP

- **Background Tasks:** Report build async, client polls for completion

- **Comprehensive Error Handling:** Custom exception types, 422/429/503 for various errors

---

## Security & Performance

- **API Security:** Input validation, rate limiting, planned OAuth

- **Secret Management:** Primary—Google Secret Manager; fallback—env vars with secure permissions

- **Performance Optimizations:**

  - Multi-tiered caching

  - Parallel agent design

  - Pre-rendered assets for PDF/visualizations

- **Monitoring:** Structured logging (timestamp, trace ID), Google Cloud Monitoring, error alerts

- **Data Access Controls:** Principle of least privilege for deployed services/secrets

---

## Testing Strategy

- **Framework:** pytest, pytest-asyncio for async agent flows

- **Coverage:** 70%+ unit/integration target

- **API & Edge Testing:** FastAPI TestClient for endpoints, input fuzzing, and timed tests

- **Automation:** CI pipeline for all tests before merge/deployment

---

## Risk Mitigation

---

**This document defines the baseline technical design for ConsultantOS. All future enhancements, integration points, and security improvements will build upon this foundation to ensure fast, reliable, and intelligent consulting at scale.**
