# ConsultantOS - Product Requirements Document (PRD)

### TL;DR

ConsultantOS enables independent strategy consultants to produce McKinsey-grade business framework analyses in 30 minutes instead of 32 hours. A multi-agent AI system on Google Cloud Run compiles real-time research into professional, client-ready PDF reports (Porter’s Five Forces, SWOT, PESTEL, Blue Ocean), with executive summaries and confidence scoring. Built for ex-Big 4 solo consultants and boutique firms seeking credible, affordable strategy deliverables at $49/month.

---

## Goals

### Business Goals

- Achieve $150–200K ARR within 12 months (≈255 paying consultants at $49/month).

- Validate 10+ customer case studies where ConsultantOS directly contributes to winning engagements.

- Deliver <5s API response time for job submission and status endpoints; 30–60s end-to-end analysis time.

- Maintain ≥99% service uptime in pilot phase with graceful degradation and recovery.

- Attain ≥60% perceived quality rating (vs. McKinsey baseline) from a panel of ex-consultants.

### User Goals

- Reduce research and synthesis time by 80–90% (from 32 hours to \~30 minutes).

- Generate comprehensive analyses across multiple frameworks in one run.

- Produce professional, client-ready PDF reports with charts and standardized layouts.

- Access real-time market, trend, and financial data with transparent sourcing and confidence scores.

- Store and retrieve past reports securely for reuse and iteration.

### Non-Goals

**Note**: The canonical naming convention for agents is defined in the Technical Design Document (Research Agent, Market Analyst, Financial Analyst, Framework Analyst, Synthesis Agent). This PRD uses the same naming to ensure consistency.

- Complex user authentication/authorization, payment processing, and full dashboard UI — **Status**: Deferred (see README.md for current implementation status)

- Template library beyond the four core frameworks — **Status**: Deferred (beyond MVP)

- Consultant community, collaboration features, or advanced workflow management — **Status**: Deferred (out of scope for hackathon)

**Current Implementation Status** (as of latest README.md):

- Dashboard UI — Completed (Phase 1) — See README.md for details
- User authentication — Completed — See README.md for details
- Report sharing & collaboration — Completed — See README.md for details
- Template library — Completed — See README.md for details

For authoritative feature status, refer to README.md which tracks implemented features and phases.

---

## User Stories

Persona: Independent Strategy Consultant (ex-Big 4; solo or 2–5 person boutique)

- As a consultant, I want to generate Porter’s Five Forces analysis in 30 minutes so that I can present credible insights to clients.

- As a consultant, I want professional PDF reports so that I can share deliverables directly with clients.

- As a consultant, I want multi-framework analysis (SWOT, PESTEL, Blue Ocean) so that I can provide comprehensive strategic insights.

- As a consultant, I want confidence scores and citations so that I can defend my recommendations.

- As a consultant, I want to pull recent trends and financials so that my analysis reflects current market dynamics.

Persona: Boutique Firm Owner/Principal

- As a principal, I want standardized report structure so that junior staff can deliver consistent outputs.

- As a principal, I want cloud-based report storage so that our team can retrieve and iterate on deliverables quickly.

- As a principal, I want predictable cost ($49/month) so that we can maintain margins without large overhead.

Persona: Engagement Manager

- As an engagement manager, I want an executive summary page so that clients can absorb insights in minutes.

- As an engagement manager, I want configurable frameworks per run so that I can tailor deliverables to client needs.

---

## Functional Requirements

- Multi-Agent Orchestration (Priority: P0)

  - Orchestration Engine: Coordinate five agents using Google ADK; manage task graph, retries, and timeouts.

  - Research Agent: Gather company intelligence using Tavily web search with deduplication, source ranking, and citation capture.

  - Status & Progress: Expose run status, per-agent progress, and logs.

- Framework Analysis (Priority: P0)

  - Porter’s Five Forces Engine: Produce industry structure analysis with evidence and scores.

  - SWOT Engine: Synthesize internal/external factors with prioritization.

  - PESTEL Engine: Analyze macro forces with region/industry filters.

  - Blue Ocean Engine: Identify value curves and strategic moves; visualize strategy canvas.

- Data Ingestion & Evidence (Priority: P0)

  - Web Research: Tavily-powered search with deduplication, source ranking, and citation capture.

  - Market & Trend Data: Google Trends ingestion with time window selection.

  - Financial Data: SEC EDGAR and yfinance pull for public comparables; private-company proxies.

  - Data Validation: Confidence scoring based on recency, corroboration, and source quality.

- Reporting & Visualization (Priority: P0)

  - PDF Composition: ReportLab-based generation with brand-neutral, consulting-grade layout.

  - Charts & Figures: Plotly visualizations (industry forces, trends, strategy canvas).

  - Executive Summary: One-page brief with key insights, risks, and next steps.

  - Citations Appendix: Structured references with URLs/timestamps.

- Storage & Retrieval (Priority: P0)

  - Cloud Storage: Save PDFs and metadata with signed URL retrieval.

  - Report Index: Search by client, industry, date, and framework.

- Platform & API (Priority: P0)

  - FastAPI Backend: Endpoints for job submission, status, and download.

  - Cloud Run Deployment: Containerized, autoscaling, scale-to-zero for cost-efficiency.

- Performance, Observability & Reliability (Priority: P0)

  - Performance Budgets: <5s API response to enqueue; 30–60s total analysis SLA.

  - Monitoring: Request tracing, structured logs, latency/error dashboards.

  - Graceful Errors: User-friendly messages and retry guidance.

- Security & Access Control (Priority: P0)

  - API Keys: Key-based access with rate limiting.

  - Secrets Management: Use Secret Manager for external API credentials.

  - Data Isolation: Tenant-safe storage and signed URL expiry.

- Optional Enhancements (Priority: P1, Post-hackathon)

  - Gemini Pro Integration: Enhanced reasoning and summarization.

  - Quality Tuning: Framework-specific prompting and evaluator loops.

  - Lightweight Web UI: Minimal form to replace API-only workflow.

---

## User Experience

**Entry Point & First-Time User Experience**

- Discovery: Consultants reach a simple landing page with product overview and call-to-action to “Generate Report,” or use a documented API.

- Onboarding: No login in hackathon phase. Users enter project details in a minimal form (client/industry/region/competitors/objectives), select frameworks, and provide an email for delivery (optional).

- Guidance: Inline examples, field validations, and a short “What you’ll get” preview with SLA.

**Core Experience**

- Step 1: Define Scope

  - User enters client name, industry, geography, competitors, and timeframe; selects frameworks (default: all four).

  - Validation ensures required fields; suggest NAICS/industry tags when ambiguous.

  - Show estimated run time and token usage (informational).

- Step 2: Submit Generation

  - User submits; API responds in <5s with Run ID and status endpoint.

  - UI displays progress per agent (Research Agent, Market Analyst, Financial Analyst, Framework Analyst, Synthesis Agent).

- Step 3: Data Gathering

  - Research Agent queries Tavily; Market Analyst and Financial Analyst pull Google Trends and SEC/yfinance.

  - Conflicts flagged; stale or low-quality sources deprioritized.

- Step 4: Framework Synthesis

  - Analyst agent composes framework-specific sections with evidence and confidence scores.

  - Consistency checks: Align insights across frameworks; resolve contradictions with rationale.

- Step 5: Visualization & Layout

  - Plotly generates charts (forces radar, trend lines, strategy canvas).

  - ReportLab compiles sections into a consulting-grade PDF with TOC, headers, footers, and page numbers.

- Step 6: Delivery

  - Completion view shows executive summary, confidence overview, and download link (signed URL).

  - Email (optional) with link and run metadata.

- Step 7: Retrieval

  - Report index lists previous runs by client and date; users can duplicate a run with tweaks.

**Advanced Features & Edge Cases**

- Private Companies: If SEC/yfinance data missing, use industry averages and nearest public comps; label proxies clearly.

- Thin Information Markets: If limited data, reduce scope and increase qualitative analysis; surface risks prominently.

- Rate Limits/Source Failures: Fallback to cached data; retry with exponential backoff; partial results annotated.

- Overbroad Prompts: Framework Analyst narrows scope and prompts user to confirm.

- Long Runs: If exceeding SLA, deliver partial report with flagged sections and follow-up completion.

**UI/UX Highlights**

- Consulting-grade typography, clean hierarchy, and high-contrast color palette for readability in print and screen.

- One-page executive summary; consistent section headers; click-through TOC in PDF.

- Charts labeled with sources and timestamps; legend clarity at 100% zoom and in print.

- Accessibility: Alt text for images/charts in PDF metadata; avoid color-only encoding.

- Internationalization-ready numeric/currency formatting; explicit date ranges and time zones.

- Clear disclaimers on data recency, proxies, and confidence scores.

---

## Narrative

Aisha, an ex-McKinsey consultant running a two-person boutique, has a new prospect in industrial IoT. The client expects a sharp point of view across industry structure, macro forces, competitive dynamics, and strategic whitespace—on a shoestring budget and a 48-hour deadline. Historically, Aisha would spend all night assembling sources, wrangling spreadsheets, and aligning slides into a client-ready narrative.

With ConsultantOS, she enters the client’s segment, geography, and top competitors, selects Porter’s Five Forces, SWOT, PESTEL, and Blue Ocean, and hits Generate. The planner coordinates five specialized agents. One scours the web for high-signal sources, another pulls trendlines and public comps, and a third synthesizes findings into clean frameworks with evidence and confidence scores. Visuals and layout are auto-generated into a professional PDF with an executive summary and citations. In under 30 minutes, Aisha downloads a crisp report that she can share as-is.

The client meeting shifts from data gathering to decision-making. Aisha leads with a confident narrative grounded in timely data and transparent sourcing. The client appreciates the speed, rigor, and professional packaging—ultimately awarding the engagement. Aisha protects margins with a $49/month tool, redeploys saved hours to advisory work, and scales her firm’s capacity without hiring.

---

## Success Metrics

- Hackathon Outcomes: 5 agents orchestrated, 4 frameworks implemented, PDF reports generated, <5s API response.

### User-Centric Metrics

- Time Savings: Median analysis completion time ≤30 minutes (95th percentile ≤45 minutes).

- Quality Perception: ≥60% “McKinsey-comparable” rating from a panel of ex-consultants.

- Adoption: ≥255 active subscribers within 12 months; ≥30% monthly active usage per seat.

- Outcome: ≥10 documented cases where ConsultantOS helped win or expand engagements.

### Business Metrics

- ARR: $150–200K within 12 months at $49 per month pricing.

- Retention: ≥80% month-2 retention; churn ≤5% monthly.

- Gross Margin: ≥80% after infra and API costs.

### Technical Metrics

- Performance: <5s API acknowledgement; 30–60s end-to-end analysis SLA.

- Reliability: ≥99% uptime; error rate ≤1% per 1,000 runs.

- Data Freshness: ≥80% sources from the last 12 months for time-sensitive topics.

### Tracking Plan

- Events: Run Created, Frameworks Selected, Data Sources Queried, Agent Completed, Report Generated, Download Clicked, Retrieval Opened, Error Encountered.

- Properties: Industry, Region, Competitor Count, Run Duration, Confidence Score Distribution, Source Count.

- System Metrics: Latency per agent, success/failure codes, retry counts, cold starts, API quota usage.

---

## Technical Considerations

### Technical Needs

- Architecture

  - Cloud Run service hosting FastAPI for job submission, status, and retrieval.

  - Google ADK-based orchestrator coordinating five agents (Research Agent, Market Analyst, Financial Analyst, Framework Analyst, Synthesis Agent).

  - Asynchronous task execution with parallel agent steps and shared context store.

- Data Models

  - Report: id, client, industry, region, frameworks, created_at, status, confidence_summary, pdf_url.

  - Evidence: source_url, title, publisher, date, snippet, reliability_score.

  - FrameworkSection: type (Porter, SWOT, PESTEL, Blue Ocean), content, visuals, citations.

- Reporting

  - ReportLab for layout; Plotly for charts embedded as vector or high-res raster.

### Integration Points

- Research: Tavily web search API (with source ranking and dedupe).

- Trends: Google Trends for relative interest over time by region/keyword.

- Financials: SEC EDGAR filings; yfinance for market data.

- Reasoning: Optional Gemini Pro integration for synthesis and summarization.

- Secrets: Secret Manager for all third-party API keys.

### Data Storage & Privacy

- Storage: PDFs and artifacts in cloud object storage with signed URLs; minimal metadata in a managed NoSQL store.

- Privacy: Only user-provided project data and public-source evidence; no sharing across tenants.

- Security: At-rest encryption; in-transit TLS; least-privilege IAM; audit logs for access to storage.

- Retention: Configurable retention (e.g., 90 days by default) with purge endpoint.

- Compliance: Clear disclaimers for informational use; respect robots.txt and source terms where applicable.

### Scalability & Performance

- Autoscaling: 0–10 instances with scale-to-zero for cost control; concurrency tuned for parallel agent tasks.

- Caching: Query/result caching for repeated runs; ETag-based validation for static sources.

- Cold Starts: Minimize image size; keep warm via scheduled pings during peak windows.

- Parallelism: Fan-out for data and research agents; fan-in with timeouts for synthesis.

### Potential Challenges

- Source Reliability: Mitigate hallucinations with strict citation requirements and confidence scoring.

- Private Company Data: Use proxy comps and industry averages with clear labeling.

- Rate Limits: Backoff, pooling, and staggered queries; cache recent pulls.

- PDF Fidelity: Ensure consistent cross-platform rendering; embed fonts and fallbacks.

- Legal/IP: Honor content usage terms; avoid scraping behind paywalls.

---

## Milestones & Sequencing

### Project Estimate

- Small: 1–2 weeks for MVP and initial hardening.

### Team Size & Composition

- Small Team (2 people)

  - Full-Stack/ML Engineer: Orchestration, data integrations, PDF/visualization, Cloud Run ops.

  - Product Designer/PM: UX flow (minimal form), prompt design, quality evaluation, docs.

### Suggested Phases

- P0: Hackathon MVP (3–5 days)

  - Key Deliverables:

    - Engineer: Cloud Run + FastAPI service; ADK orchestrator with 5 agents; integrations (Tavily, Google Trends, SEC/yfinance); four frameworks; ReportLab + Plotly PDF; API keys and rate limiting; status endpoint; <5s enqueue.

    - PM/Designer: Minimal input form (or Postman collection); prompt patterns; report template; success metrics dashboard.

  - Dependencies: API keys, Secret Manager, base container image, sample prompts and industries.

- P1: Hardening & Pilot (5–7 days)

  - Key Deliverables:

    - Engineer: Monitoring dashboards, structured logging, retries/timeouts, caching, signed URLs, storage index, confidence scoring refinements.

    - PM/Designer: QA rubric with ex-consultants, documentation, sample reports, onboarding guide.

  - Dependencies: Access to reviewer panel, initial pilot users, infra quotas.

- P2: Early Beta Enhancements (5 days)

  - Key Deliverables:

    - Engineer: Optional Gemini Pro synthesis path; improved Blue Ocean visuals; partial results handling; retention controls.

    - PM/Designer: Pricing page draft, case studies, success tracking framework.

  - Dependencies: Gemini access, budget for API usage tests.

---
