# ConsultantOS - Product Strategy & Technical Design

**Last Updated**: January 2025  
**Status**: Consolidated from multiple documents

---

## Table of Contents

1. [Product Vision](#product-vision)
2. [Product Requirements Document (PRD)](#product-requirements-document-prd)
3. [Go-to-Market Strategy](#go-to-market-strategy)
4. [Release Plan](#release-plan)
5. [Technical Design](#technical-design)
6. [Architecture](#architecture)

---

## Product Vision

### Mission

Enable every independent strategy consultant to compete with Big 4 firms by providing McKinsey-grade framework analysis at affordable prices. Democratize access to professional strategic consulting tools.

### Value Proposition

Reduce strategic analysis time from 32 hours to 30 minutes while maintaining 60-80% of McKinsey deliverable quality. Empower consultants to focus on high-value advisory, not repetitive or time-consuming research.

### Market Opportunity

**Pricing Gap**: $460K between AI chatbots ($80/month) and full-scale consulting engagements ($500K/project)

**Market Size**:
- Business Intelligence Market: $47 billion (2025 projection)
- Strategic Consulting Market: $35 billion globally
- Independent Consultant Population: 50,000+ professionals in US/UK markets

**Target Customer**: Independent strategy consultants (ex-Big 4, solo or 2-5 person boutique firms)

**Pricing**: $49/month (validated with customer discovery)

---

## Product Requirements Document (PRD)

### Goals

**Business Goals**:
- Achieve $150–200K ARR within 12 months (≈255 paying consultants at $49/month)
- Validate 10+ customer case studies where ConsultantOS directly contributes to winning engagements
- Deliver <5s API response time for job submission; 30–60s end-to-end analysis time
- Maintain ≥99% service uptime in pilot phase
- Attain ≥60% perceived quality rating (vs. McKinsey baseline) from ex-consultants

**User Goals**:
- Reduce research and synthesis time by 80–90% (from 32 hours to ~30 minutes)
- Generate comprehensive analyses across multiple frameworks in one run
- Produce professional, client-ready PDF reports with charts and standardized layouts
- Access real-time market, trend, and financial data with transparent sourcing

### Functional Requirements

**Multi-Agent Orchestration** (Priority: P0):
- Orchestration Engine: Coordinate five agents using Google ADK
- Status & Progress: Expose run status, per-agent progress, and logs

**Framework Analysis** (Priority: P0):
- Porter's Five Forces Engine
- SWOT Engine
- PESTEL Engine
- Blue Ocean Engine

**Data Ingestion & Evidence** (Priority: P0):
- Web Research: Tavily-powered search with deduplication and citation capture
- Market & Trend Data: Google Trends ingestion
- Financial Data: SEC EDGAR and yfinance pull for public comparables
- Data Validation: Confidence scoring based on recency, corroboration, and source quality

**Reporting & Visualization** (Priority: P0):
- PDF Composition: ReportLab-based generation with consulting-grade layout
- Charts & Figures: Plotly visualizations
- Executive Summary: One-page brief with key insights, risks, and next steps
- Citations Appendix: Structured references with URLs/timestamps

**Platform & API** (Priority: P0):
- FastAPI Backend: Endpoints for job submission, status, and download
- Cloud Run Deployment: Containerized, autoscaling, scale-to-zero

### Success Metrics

**User-Centric Metrics**:
- Time Savings: Median analysis completion time ≤30 minutes
- Quality Perception: ≥60% "McKinsey-comparable" rating
- Adoption: ≥255 active subscribers within 12 months

**Business Metrics**:
- ARR: $150–200K within 12 months at $49 per month pricing
- Retention: ≥80% month-2 retention; churn ≤5% monthly
- Gross Margin: ≥80% after infra and API costs

**Technical Metrics**:
- Performance: <5s API acknowledgement; 30–60s end-to-end analysis SLA
- Reliability: ≥99% uptime; error rate ≤1% per 1,000 runs
- Data Freshness: ≥80% sources from the last 12 months

---

## Go-to-Market Strategy

### Market Positioning

**Core Value Proposition**:
- Time Efficiency: Reduce analysis time from 32 hours to 2 hours (95% reduction)
- Cost Effectiveness: $500K traditional consulting cost reduced to $49/month (99.99% reduction)
- Quality Assurance: 60-80% of McKinsey deliverable quality through proven frameworks
- Professional Positioning: "McKinsey-grade frameworks" rather than "cheap alternative"

### Pricing Strategy

**Starter Tier: $49/month**:
- Target: Individual consultants
- ROI Justification: Single client win at $15K = 25x annual subscription value
- Represents 0.5-0.7% of typical consultant annual revenue ($100K-300K)

**Future Pricing Tiers**:
- Premium Tier: $99/month (enhanced features, priority support)
- Enterprise Tier: $499/month (unlimited access, white-label capabilities)

### Customer Acquisition Strategy

**Phase 1: Direct Outreach (Months 1-3)**:
- Target: 10 Paying Customers
- Direct LinkedIn outreach to ex-Big 4 consultants
- Personalized messaging highlighting relevant experience
- One-on-one demo calls and consultations

**Phase 2: Content-Driven Growth (Months 4-6)**:
- Target: 50 Total Customers
- Case study publication and promotion
- Thought leadership content distribution
- Consultant community engagement
- Referral program launch

**Phase 3: Scale and Partnerships (Months 7-12)**:
- Target: 255+ Total Customers
- Partner channel development
- API integration launches
- Consultant community advocacy
- Expanded content marketing

### Success Metrics

**Month 3 Targets**:
- 10 paying customers acquired
- $490 Monthly Recurring Revenue (MRR)
- 1 detailed customer case study published

**Month 6 Targets**:
- 50 total paying customers
- $2,450 Monthly Recurring Revenue
- 5 published customer case studies
- Customer acquisition cost below $200

**Month 12 Targets**:
- 255+ paying customers
- $12,500+ Monthly Recurring Revenue
- $150,000+ Annual Recurring Revenue
- Average customer lifetime value above $1,000

---

## Release Plan

### Version Roadmap

**v0.1.0 (Hackathon MVP)**:
- 5 agents (Research, Market, Financial, Framework, Synthesis)
- 4 frameworks (Porter, SWOT, PESTEL, Blue Ocean)
- PDF report generation with basic styling
- Google Cloud Run deployment

**v0.2.0 (Month 1)**:
- Robust error handling and request timeout management
- Monitoring dashboard (latency, errors, cost)
- Performance optimizations (caching, batching)

**v0.3.0 (Months 2–3)**:
- User authentication and account management
- Basic dashboard (recent reports, run history)
- Report library with versioning and search
- API key issuance and management

**v0.4.0 (Months 4–6)**:
- Template library with custom framework templates
- Consultant community features
- API improvements (pagination, webhooks)

**v1.0.0 (Months 7–12)**:
- Team collaboration (shared workspaces, roles/permissions)
- White-label report theming and branding
- Advanced analytics
- Enterprise-grade security controls and SOC 2 readiness

### Release Criteria

**v0.1.0**:
- All 5 agents functional with 4 frameworks
- PDF generation produces complete, readable reports
- Deployed on Cloud Run; demo endpoint publicly accessible
- Median response-to-first-token <5s; full standard analysis <60s

**v0.2.0**:
- 99% uptime (monthly), p95 standard analysis <60s
- 70%+ automated test coverage across critical paths
- Monitoring dashboard with error budget tracking

**v1.0.0**:
- 99.9% uptime (quarterly), documented SLOs
- Enterprise security controls (RBAC, encryption, audit logs)
- SOC 2 readiness: policies, controls, and evidence management

---

## Technical Design

### System Architecture

```
[Client/UI] 
    ↓
[FastAPI app] 
    ↓
[Google ADK orchestrator]
    ↓
┌─────────────────────────────────┐
│ Phase 1: Parallel Execution    │
│ - Research Agent (Tavily)       │
│ - Market Analyst (Trends)       │
│ - Financial Analyst (SEC/yf)   │
└─────────────┬───────────────────┘
              ↓
┌─────────────────────────────────┐
│ Phase 2: Sequential Execution   │
│ - Framework Agent (4 frameworks)│
│ - Synthesis Agent (summary)     │
└─────────────┬───────────────────┘
              ↓
[ReportLab PDF Generation w/ Plotly]
              ↓
[Google Cloud Storage]
```

### Technology Stack

**Core Infrastructure**:
- **Web Framework**: FastAPI (async support, auto docs)
- **Orchestration**: Google ADK (Agent Development Kit)
- **AI Model**: Google Gemini Pro
- **Structured Outputs**: Instructor + Pydantic
- **Vector Store**: ChromaDB for semantic caching
- **Report Generation**: ReportLab + Plotly + kaleido
- **Deployment**: Google Cloud Run

**Data Sources**:
- **Web Research**: Tavily API
- **Market Trends**: Google Trends (pytrends)
- **Financial Data**: SEC EDGAR (edgartools) + yfinance
- **Company Data**: finviz, pandas-datareader

### Agent Design

**Research Agent**:
- Purpose: Aggregate latest web and wiki info
- Tool Integration: Tavily API
- Output: CompanyResearch model

**Market Analyst**:
- Purpose: Analyze real-time searches & sentiment
- Tool Integration: Google Trends API (pytrends)
- Output: MarketTrends model

**Financial Analyst**:
- Purpose: Extract and summarize company financials
- Tool Integration: SEC EDGAR API, yfinance
- Output: FinancialSnapshot model

**Framework Analyst**:
- Purpose: Apply strategic frameworks (Porter's, SWOT, PESTEL, Blue Ocean)
- Tool Integration: LLM (Gemini), vector cache for context
- Output: FrameworkAnalysis model

**Synthesis Agent**:
- Purpose: Craft executive summary, recommendations
- Tool Integration: LLM with prior stage data/context
- Output: ExecutiveSummary model

### Data Models

**Key Pydantic Models**:
- `AnalysisRequest`: User request for strategic analysis
- `CompanyResearch`: Research agent output
- `MarketTrends`: Market analyst output
- `FinancialSnapshot`: Financial analyst output
- `PortersFiveForces`: Porter's 5 Forces analysis
- `SWOTAnalysis`: SWOT analysis
- `PESTELAnalysis`: PESTEL analysis
- `BlueOceanStrategy`: Blue Ocean Strategy analysis
- `ExecutiveSummary`: Final synthesis output
- `StrategicReport`: Complete report structure

### API Design

**Core Endpoints**:
- `POST /analyze`: Generate strategic analysis report
- `GET /health`: Health check endpoint
- `GET /reports/{report_id}`: Retrieve a generated report
- `GET /reports`: List reports with filters
- `GET /metrics`: System metrics

**Features**:
- Rate Limiting: slowapi, 10/minute/IP
- Background Tasks: Report build async, client polls for completion
- Comprehensive Error Handling: Custom exception types, 422/429/503 for various errors

### Deployment Architecture

**Cloud Run Configuration**:
- 2 vCPU, 2Gi RAM, 300s request timeout
- Scale-to-zero for cost efficiency; max 10 concurrent instances
- Google Secret Manager: Secrets for API keys, tokens
- High Availability: Multi-region support, health checks, auto-restart

**Deployment Tools**:
- Docker: Container build and local dev matching Cloud Run
- gcloud CLI: Deployment automation
- GitHub Actions: CI/CD pipelines, push-to-deploy

### Security & Performance

**API Security**:
- Input validation (Pydantic)
- Rate limiting (slowapi)
- API key authentication (post-hackathon)

**Secret Management**:
- Primary: Google Secret Manager
- Fallback: Environment variables with secure permissions

**Performance Optimizations**:
- Multi-tiered caching (in-memory, disk, ChromaDB)
- Parallel agent design
- Pre-rendered assets for PDF/visualizations

**Monitoring**:
- Structured logging (timestamp, trace ID)
- Google Cloud Monitoring
- Error alerts

---

## Architecture

### High-Level Architecture

```
   [Client/UI] 
      |
  [FastAPI app] 
      |
  [Google ADK orchestrator]
      |
-------------------------------------------------
|          |         |         |                |
Research   Market   Financial  Framework       Synthesis
 Agent     Analyst  Analyst    Analyst         Agent
(Tavily)  (Trends) (SEC/yf)   (LLM)           (LLM)
  |          |         |         |                |
      [Intermediate Data Storage: ChromaDB]
                          |
            [ReportLab PDF Generation w/ Plotly]
                          |
                    [Google Cloud Storage]
```

### Design Patterns

- **Orchestration Pattern**: Parallel and sequential flows for efficiency
- **Modular Agent Abstraction**: Isolated, composable agents
- **Repository Pattern**: Data/query abstraction via ChromaDB
- **Structured Logging & Monitoring**

### Caching Strategy

**Multi-Level Caching**:
- **In-memory (LRU)**: Request/session-scoped data
- **Disk Cache**: Intermediate results (1GB limit, 1-hour TTL)
- **ChromaDB (Semantic Vector Store)**: Research/document retrieval and duplicate avoidance

### Testing Strategy

**Test Coverage Goals**:
- Unit tests: 70%+ coverage for core logic
- Integration tests: All agent workflows
- API tests: All endpoints with success and error cases
- PDF generation tests: Verify report structure and content

**Testing Tools**:
- pytest: Main Python test runner
- pytest-asyncio: For async agent tasks and workflows
- FastAPI TestClient: REST endpoint testing
- Coverage.py: Enforce/monitor code coverage

---

## Risk Mitigation

### Technical Risks

- **ADK Learning Curve**: Mitigation: Offer CrewAI fallback and detailed onboarding
- **LLM Quality Variability**: Mitigation: Deploy validation gates, supervised output, client feedback loops
- **API Rate Limits**: Mitigation: Aggressive caching, retry with exponential backoff

### Business Risks

- **Customer Willingness to Pay**: Mitigation: Conduct continuous discovery interviews, highlight ROI
- **Competitive Response**: Mitigation: Build moat via unique template library and active consultant community

---

**Document Status**: Consolidated from PRD.md, Product_Strategy_Document.md, Go_to_Market_Plan.md, Release_Plan.md, Technical_Design_Document.md, and Research documents.

