# Business Intelligence Research Engine - Complete Design Document

**Project Name**: ConsultantOS - Business Intelligence Research Engine
**Version**: 2.0 (Post-Strategic Analysis)
**Date**: November 7, 2025
**Hackathon**: [Google Cloud Run Hackathon 2025](https://run.devpost.com/)
**Category**: AI Agents (Multi-Agent Systems)
**Deadline**: November 10, 2025 @ 5:00pm PST

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Strategic Foundation](#2-strategic-foundation)
3. [System Architecture](#3-system-architecture)
4. [Technical Design](#4-technical-design)
5. [Data Architecture](#5-data-architecture)
6. [Agent Design](#6-agent-design)
7. [Report Generation System](#7-report-generation-system)
8. [API Design](#8-api-design)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Security & Performance](#10-security--performance)
11. [Quality Assurance](#11-quality-assurance)
12. [Risk Mitigation](#12-risk-mitigation)

---

## 1. Executive Summary

### 1.1 Project Overview

**ConsultantOS** is a multi-agent AI system that enables independent strategy consultants to generate McKinsey-grade business framework analysis in 30 minutes instead of 32 hours. Built on Google Cloud Run with Google ADK (Agent Development Kit) orchestration.

### 1.2 Strategic Validation (Business Panel Consensus)

**✅ CONDITIONAL GO Decision** based on comprehensive framework analysis:

**Convergent Insights** (All 4 experts agree):

1. **Primary Market**: Independent consultants (ex-Big 4) are the beachhead (NOT VCs or strategy directors)
2. **Value Proposition**: Credibility > Cost (position as "McKinsey-grade frameworks" not "cheap alternative")
3. **Sustainable Moat**: Template library + consultant community (NOT just technology)

**Strategic Positioning**:

- **Porter (Competitive Strategy)**: Low-end disruption of $460K consulting market
- **Christensen (Innovation)**: Classic non-consumption opportunity (consultants can't afford McKinsey)
- **Drucker (Management)**: Business is "enabling consultants to compete with Big 4"
- **Meadows (Systems)**: Leverage paradigm shift ("AI-assisted = credible")

### 1.3 Core Metrics

**Hackathon Success** (3 days):

- 5 specialized agents coordinated via Google ADK
- 4 business frameworks implemented (Porter, SWOT, PESTEL, Blue Ocean)
- Professional PDF reports with visualizations
- Live Cloud Run deployment with <5 second response time

**Business Success** (12 months):

- Target: $150-200K ARR (255 paying customers @ $49/mo)
- Customer: Independent strategy consultants (ex-Big 4, $100K-300K billing)
- Proof: 10 consultants win client engagements using the tool

### 1.4 Key Differentiators

| Feature                      | ConsultantOS                | Perplexity   | ChatGPT Pro  | McKinsey      |
| ---------------------------- | --------------------------- | ------------ | ------------ | ------------- |
| **Multi-Framework Analysis** | ✅ Porter, SWOT, Blue Ocean | ❌ Generic   | ❌ Generic   | ✅ All        |
| **Professional Reports**     | ✅ PDF with charts          | ❌ Chat only | ❌ Chat only | ✅ Decks      |
| **Turnaround Time**          | ✅ 30 minutes               | ✅ 5 minutes | ✅ 5 minutes | ❌ 8-12 weeks |
| **Price**                    | ✅ $49/month                | $20/month    | $200/month   | $500K/project |
| **Quality Target**           | 60-80% McKinsey             | 50-60%       | 50-60%       | 90-100%       |

---

## 2. Strategic Foundation

### 2.1 Market Opportunity ($460K Pricing Gap)

```
┌────────────────┬─────────────────────┬──────────────────┐
│  AI Chatbots   │  ConsultantOS       │   Consulting     │
│   $80/month    │   $49-499/month     │   $500K/project  │
│   (Generic)    │   (Frameworks)      │   (Expert)       │
└────────────────┴─────────────────────┴──────────────────┘
        ↑                   ↑                    ↑
     Perplexity     MARKET GAP          McKinsey/BCG
     ChatGPT     (NO COMPETITOR)           Bain
```

**Market Size**:

- Business Intelligence: $47B (2025) → $116B (2033) at 10% CAGR
- Strategic Consulting: $35B (McKinsey + BCG + Bain combined)
- Independent Consultants: 50,000+ in US/UK markets

**Value Proposition**:

- **Time Savings**: 32 hours → 2 hours (95% reduction)
- **Cost Savings**: $500K → $49/month (99.99% reduction)
- **Quality Target**: 60-80% of McKinsey deliverable quality

### 2.2 Primary Customer: Independent Strategy Consultant

**Profile**:

- Background: Ex-Big 4 (McKinsey, BCG, Bain, Deloitte)
- Status: Solo or 2-5 person boutique firm
- Revenue: $100K-300K annual billing
- Pain: 60% of time on research vs advisory

**Jobs-to-be-Done** (Christensen Framework):

1. **PRIMARY**: "Help me look credible to clients with McKinsey-grade frameworks"
2. **SECONDARY**: "Save me 20 hours per engagement on framework application"
3. **TERTIARY**: "Reduce cost vs hiring junior analysts ($50K-80K/year)"

**Willingness to Pay**:

- **$49/month** = $588/year = 0.5-0.7% of revenue
- **ROI Calculation**: 1 client win @ $15K = 25x annual subscription
- **Validation**: Must interview 10 consultants, get 7/10 "definitely yes"

### 2.3 Competitive Positioning

**Blue Ocean Strategy (Four Actions Framework)**:

**Eliminate**:

- ❌ Manual research bottlenecks (32 hours → 2 hours)
- ❌ Consultant wait times ($500K McKinsey → instant delivery)

**Reduce**:

- 📉 Cost (99% reduction vs McKinsey)
- 📉 Turnaround time (95% reduction)

**Raise**:

- 📈 Analysis depth (multi-framework vs single ChatGPT response)
- 📈 Consistency (structured frameworks every time)
- 📈 Framework coverage (4-6 frameworks vs generic advice)

**Create**:

- ✨ Multi-framework synthesis (cross-framework insights)
- ✨ On-demand strategic analysis (no consulting engagement needed)
- ✨ Professional deliverables (PDF reports, not just chat)

### 2.4 Risk-Adjusted Assumptions

**Critical Assumptions** (Must Validate Pre-Hackathon):

| Assumption                                  | Current Evidence        | Validation Required                                     | Risk Level  |
| ------------------------------------------- | ----------------------- | ------------------------------------------------------- | ----------- |
| Can achieve 60%+ McKinsey quality           | ⚠️ None                 | Generate Netflix case study, compare to McKinsey report | 🔴 CRITICAL |
| Consultants will pay $49/mo                 | ⚠️ None                 | Interview 10 consultants, get willingness-to-pay        | 🔴 CRITICAL |
| Can build in 28 hours                       | ⚠️ 80% code reuse claim | Build vertical slice (Porter's 5 Forces) in 8 hours     | 🟡 HIGH     |
| Multi-framework analysis is defensible moat | ⚠️ Speculative          | Accept 6-12 month window, plan community moat           | 🟢 MEDIUM   |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Web UI / API Layer                        │
│              (FastAPI + Cloud Run Service)                  │
│   - Request validation, rate limiting, caching              │
│   - User authentication (post-hackathon)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         Google ADK (Multi-Agent Orchestrator)               │
│   - Task graph builder (parallel + sequential execution)   │
│   - State management across agents                         │
│   - Gemini Pro integration (bonus points)                  │
└─────┬──────────┬──────────┬──────────┬──────────┬──────────┘
      │          │          │          │          │
      ▼          ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Research │ │ Market  │ │Financial│ │Framework│ │Synthesis│
│ Agent   │ │Analyst  │ │ Analyst │ │ Analyst │ │ Agent   │
│(Tavily) │ │(Trends) │ │(SEC/yf) │ │(Gemini) │ │(Gemini) │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   ChromaDB    │
                    │ Vector Store  │
                    │ (Embeddings)  │
                    │ + Semantic    │
                    │   Caching     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Instructor  │
                    │  + Pydantic   │
                    │  (Structured  │
                    │   Validation) │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │Report Engine  │
                    │ - Plotly      │
                    │ - ReportLab   │
                    │ - Templates   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PDF Report   │
                    │ (Cloud Storage)│
                    └───────────────┘
```

### 3.2 Agent Coordination Workflow

```
User Query: "Analyze Tesla's competitive position in EV market"
            │
            ▼
    ┌───────────────┐
    │ Query Parser  │ → Decompose into agent-specific tasks
    └───────┬───────┘
            │
            ▼
    ┌───────────────────────────────────────┐
    │   Google ADK Task Graph Builder       │
    │   Creates parallel + sequential plan  │
    └───────┬───────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────┐
    │     PARALLEL EXECUTION (Phase 1)      │
    ├───────────────────────────────────────┤
    │ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
    │ │Research │ │ Market  │ │Financial│ │ ← Run in parallel
    │ │ Agent   │ │ Analyst │ │ Analyst │ │   (maximize speed)
    │ └────┬────┘ └────┬────┘ └────┬────┘ │
    └──────┼───────────┼───────────┼───────┘
           │           │           │
           └───────────┴───────────┘
                      │
                      ▼
           ┌────────────────────┐
           │  Data Aggregation  │ ← Combine results
           │  (ChromaDB Cache)  │   in vector store
           └──────────┬─────────┘
                      │
                      ▼
    ┌────────────────────────────────┐
    │  SEQUENTIAL EXECUTION (Phase 2)│
    ├────────────────────────────────┤
    │ ┌────────────────────┐        │
    │ │ Framework Analyst  │        │ ← Depends on Phase 1
    │ │ (Porter, SWOT, etc)│        │   data
    │ └──────────┬─────────┘        │
    │            │                   │
    │            ▼                   │
    │ ┌────────────────────┐        │
    │ │  Synthesis Agent   │        │ ← Depends on frameworks
    │ │ (Cross-framework)  │        │
    │ └──────────┬─────────┘        │
    └────────────┼──────────────────┘
                 │
                 ▼
      ┌────────────────────┐
      │  Report Generator  │
      │ (Plotly + ReportLab)│
      └──────────┬─────────┘
                 │
                 ▼
         Final PDF Report
```

### 3.3 Technology Stack

#### **Hackathon-Required (Must-Have)**

| Component        | Technology        | Status      | Justification                                  |
| ---------------- | ----------------- | ----------- | ---------------------------------------------- |
| **Orchestrator** | Google ADK        | ✅ Required | Hackathon requirement for AI Agents category   |
| **AI Model**     | Google Gemini Pro | ✅ Required | Bonus points (+0.4) for using Google AI models |
| **Deployment**   | Google Cloud Run  | ✅ Required | Hackathon platform requirement                 |
| **Runtime**      | Python 3.11       | ✅ Standard | Best Python support for AI libraries           |

#### **Core Infrastructure**

| Component              | Technology                   | Rationale                                     | Setup Time                      |
| ---------------------- | ---------------------------- | --------------------------------------------- | ------------------------------- |
| **Web Framework**      | FastAPI                      | Async support, auto docs, Cloud Run optimized | 30 min                          |
| **Structured Outputs** | Instructor + Pydantic        | Type-safe LLM outputs, validation             | 1 hour                          |
| **Vector Store**       | ChromaDB                     | Semantic caching, embeddings                  | 0 hours (already in SuperCoder) |
| **Data Processing**    | Pandas                       | Financial data manipulation                   | 0 hours (standard)              |
| **Report Generation**  | ReportLab + Plotly + kaleido | PDF + visualizations (kaleido for Plotly→PNG) | 2 hours                         |

#### **Data Sources (Open Source)**

| Source             | Library           | Purpose                       | Cost                           |
| ------------------ | ----------------- | ----------------------------- | ------------------------------ |
| **Web Research**   | Tavily API        | Company intelligence          | FREE tier (already integrated) |
| **Market Trends**  | pytrends          | Google Trends data            | FREE                           |
| **Financial Data** | yfinance + finviz | Stock data, financial metrics | FREE                           |
| **SEC Filings**    | edgartools        | Public company filings        | FREE                           |
| **Company Data**   | pandas_datareader | Unified financial data API    | FREE                           |

#### **Enhanced Libraries (Open Source Recommendations)**

| Library                   | Purpose                   | Priority  | Time Saved                      |
| ------------------------- | ------------------------- | --------- | ------------------------------- |
| **ReportLab**             | Native PDF generation     | 🔴 HIGH   | 1 hour (vs Playwright)          |
| **kaleido**               | Plotly chart rendering    | 🔴 HIGH   | 30 min (Plotly→PNG for PDF)     |
| **finviz**                | Additional financial data | 🔴 HIGH   | 1 hour (competitive analysis)   |
| **FastAPI-Cache**         | Endpoint caching          | 🔴 HIGH   | 30 min (simple decorators)      |
| **quantstats**            | Financial metrics         | 🟡 MEDIUM | 1 hour (pre-built calculations) |
| **sentence-transformers** | Better embeddings         | 🟡 MEDIUM | 1 hour (semantic caching)       |
| **structlog**             | Structured logging        | 🟢 LOW    | 30 min (production-ready logs)  |

**Total Time Savings from Open Source**: 5-6 hours (18-21% of 28-hour timeline)

---

## 4. Technical Design

### 4.1 Google ADK Integration

**Architecture Pattern**: Google ADK as primary orchestrator (hackathon requirement)

```python
# Core ADK Setup - CORRECT API STRUCTURE
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google import genai
import instructor
from instructor import patch

# Initialize Gemini client (bonus points requirement)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_client = genai.GenerativeModel(model="gemini-2.0-flash-exp")

# Patch client for structured outputs (Instructor integration)
structured_client = patch(gemini_client, mode=instructor.Mode.GEMINI_JSON)

# Define specialized agents using LlmAgent
research_agent = LlmAgent(
    name="research_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a business research specialist.
    Gather comprehensive company information using web search.
    Focus on: company overview, recent news, market position, products/services.
    """,
    tools=[tavily_search_tool]
)

market_analyst = LlmAgent(
    name="market_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a market trend analyst.
    Analyze market interest trends using Google Trends data.
    Identify: growth trends, seasonal patterns, regional interest, competitive dynamics.
    """,
    tools=[google_trends_tool]
)

financial_analyst = LlmAgent(
    name="financial_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a financial analyst.
    Analyze company financial performance using SEC filings and stock data.
    Focus on: revenue growth, profitability, cash flow, valuation metrics.
    """,
    tools=[sec_edgar_tool, yfinance_tool]
)

framework_analyst = LlmAgent(
    name="framework_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a strategic framework expert.
    Apply Porter's 5 Forces, SWOT, PESTEL, and Blue Ocean Strategy.
    Provide structured, evidence-based strategic analysis.
    """
)

synthesis_agent = LlmAgent(
    name="synthesis_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a synthesis specialist.
    Combine insights from research, market, financial, and framework analyses.
    Create executive summary with key insights and recommendations.
    """
)

# Phase 1: Parallel Data Gathering
parallel_phase = ParallelAgent(
    name="data_gathering_phase",
    description="Gather research, market, and financial data in parallel",
    sub_agents=[research_agent, market_analyst, financial_analyst]
)

# Phase 2: Sequential Analysis
sequential_phase = SequentialAgent(
    name="analysis_phase",
    description="Apply frameworks and synthesize insights sequentially",
    sub_agents=[framework_analyst, synthesis_agent]
)

# Combined orchestrator (manual coordination)
class AnalysisOrchestrator:
    """Orchestrates parallel → sequential workflow"""

    def __init__(self):
        self.parallel_phase = parallel_phase
        self.sequential_phase = sequential_phase

    async def execute(self, request: AnalysisRequest) -> StrategicReport:
        """Execute full analysis workflow"""
        # Phase 1: Parallel execution
        phase1_results = await self.parallel_phase.run(
            f"Analyze {request.company} - gather research, market trends, and financial data"
        )

        # Phase 2: Sequential execution (depends on Phase 1)
        phase2_results = await self.sequential_phase.run(
            f"Apply frameworks and synthesize: {phase1_results}"
        )

        return self._assemble_report(phase1_results, phase2_results)

orchestrator = AnalysisOrchestrator()
```

### 4.2 Workflow Execution Strategy

**Phase 1: Parallel Data Gathering** (agents run concurrently via ParallelAgent)

```python
from typing import Dict, Any
import asyncio
from google.adk.agents import ParallelAgent

async def execute_parallel_phase(company: str) -> Dict[str, Any]:
    """Execute research, market, and financial agents in parallel"""
    try:
        # ParallelAgent automatically runs sub-agents concurrently
        results = await parallel_phase.run(
            f"Analyze {company}: gather comprehensive research, market trends, and financial data"
        )

        # Parse results from parallel execution
        # ADK returns results as a structured response
        return {
            "research": results.get("research_agent", {}),
            "market": results.get("market_analyst", {}),
            "financial": results.get("financial_analyst", {})
        }
    except Exception as e:
        logger.error(f"Parallel phase failed: {str(e)}", exc_info=True)
        raise AnalysisError(f"Data gathering failed: {str(e)}")
```

**Phase 2: Sequential Analysis** (framework → synthesis via SequentialAgent)

```python
async def execute_sequential_phase(phase1_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute framework and synthesis agents sequentially"""
    try:
        # Step 1: Framework analysis (depends on Phase 1 data)
        framework_prompt = f"""
        Apply strategic frameworks to the following data:
        Research: {phase1_data.get('research', {})}
        Market: {phase1_data.get('market', {})}
        Financial: {phase1_data.get('financial', {})}

        Apply Porter's 5 Forces, SWOT, PESTEL, and Blue Ocean Strategy.
        """

        framework_results = await framework_analyst.run(framework_prompt)

        # Step 2: Synthesis (depends on framework results)
        synthesis_prompt = f"""
        Synthesize insights from:
        Research: {phase1_data.get('research', {})}
        Market: {phase1_data.get('market', {})}
        Financial: {phase1_data.get('financial', {})}
        Frameworks: {framework_results}

        Create executive summary with key findings and recommendations.
        """

        synthesis_results = await synthesis_agent.run(synthesis_prompt)

        return {
            "frameworks": framework_results,
            "synthesis": synthesis_results
        }
    except Exception as e:
        logger.error(f"Sequential phase failed: {str(e)}", exc_info=True)
        raise AnalysisError(f"Analysis phase failed: {str(e)}")
```

**Complete Workflow with Error Handling**

```python
async def execute_full_analysis(request: AnalysisRequest) -> StrategicReport:
    """Execute complete analysis workflow with error handling"""
    try:
        # Phase 1: Parallel data gathering
        phase1_data = await execute_parallel_phase(request.company)

        # Phase 2: Sequential analysis
        phase2_data = await execute_sequential_phase(phase1_data)

        # Assemble final report
        report = assemble_report(phase1_data, phase2_data)

        return report

    except AnalysisError as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise AnalysisError(f"Analysis failed unexpectedly: {str(e)}")
```

### 4.3 Fallback Strategy (If ADK Blocked)

**Risk Mitigation**: CrewAI as backup (only if ADK fails after 6 hours on Day 1)

```python
# ONLY use if Google ADK blocked (NOT primary plan)
from crewai import Agent, Task, Crew

# Simpler API than ADK (2-hour learning curve vs 6 hours)
research_agent = Agent(
    role='Research Specialist',
    goal='Gather company intelligence',
    tools=[tavily_tool]
)

analysis_agent = Agent(
    role='Strategic Analyst',
    goal='Apply business frameworks',
    tools=[]
)

crew = Crew(
    agents=[research_agent, analysis_agent],
    tasks=[research_task, analysis_task],
    process='sequential'
)

result = crew.kickoff()
```

**Decision Gate**: End of Day 1, Hour 6

- ✅ If ADK working → Continue
- ❌ If blocked → Pivot to CrewAI (lose ADK bonus points, but gain speed)

---

## 5. Data Architecture

### 5.1 Data Flow Pipeline

```
User Input → Query Parsing → Agent Execution → Data Aggregation → Framework Analysis → Synthesis → Report
```

**Detailed Data Flow**:

```python
# Step 1: Query Parsing
class QueryParser:
    def parse(self, query: str) -> AnalysisRequest:
        """
        Input: "Analyze Tesla's competitive position in EV market"
        Output: {
            company: "Tesla",
            ticker: "TSLA",
            industry: "Electric Vehicles",
            analysis_type: "competitive_positioning",
            frameworks: ["porter", "swot", "blue_ocean"]
        }
        """
        pass

# Step 2: Agent Task Decomposition
class TaskDecomposer:
    def decompose(self, request: AnalysisRequest) -> List[AgentTask]:
        """
        Parallel Phase:
        - Research Task: "Gather Tesla company intelligence"
        - Market Task: "Analyze EV market trends"
        - Financial Task: "Analyze TSLA stock and financials"

        Sequential Phase:
        - Framework Task: "Apply Porter/SWOT/Blue Ocean to data"
        - Synthesis Task: "Generate executive summary"
        """
        pass
```

### 5.2 Data Models (Pydantic Schemas)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ============================================================================
# INPUT MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    """User request for strategic analysis"""
    company: str = Field(..., description="Company name")
    industry: Optional[str] = Field(None, description="Industry sector")
    frameworks: List[str] = Field(
        default=["porter", "swot", "pestel", "blue_ocean"],
        description="Frameworks to apply"
    )
    depth: str = Field(default="standard", description="Analysis depth: quick/standard/deep")

# ============================================================================
# AGENT OUTPUT MODELS
# ============================================================================

class CompanyResearch(BaseModel):
    """Research agent output"""
    company_name: str
    description: str = Field(..., description="Company overview")
    products_services: List[str]
    target_market: str
    key_competitors: List[str]
    recent_news: List[str]
    sources: List[str] = Field(..., description="Citation URLs")

class MarketTrends(BaseModel):
    """Market analyst output"""
    search_interest_trend: str = Field(..., description="Growing/Stable/Declining")
    interest_data: dict = Field(..., description="Time series data")
    geographic_distribution: dict
    related_searches: List[str]
    competitive_comparison: dict = Field(..., description="Company vs competitors")

class FinancialSnapshot(BaseModel):
    """Financial analyst output"""
    ticker: str
    market_cap: Optional[float]
    revenue: Optional[float] = Field(None, description="Latest annual revenue")
    revenue_growth: Optional[float] = Field(None, description="YoY growth percentage")
    profit_margin: Optional[float]
    pe_ratio: Optional[float]
    key_metrics: dict = Field(..., description="Additional financial metrics")
    risk_assessment: str

# ============================================================================
# FRAMEWORK MODELS
# ============================================================================

class PortersFiveForces(BaseModel):
    """Porter's 5 Forces analysis"""
    supplier_power: float = Field(..., ge=1, le=5, description="1=weak, 5=strong")
    buyer_power: float = Field(..., ge=1, le=5)
    competitive_rivalry: float = Field(..., ge=1, le=5)
    threat_of_substitutes: float = Field(..., ge=1, le=5)
    threat_of_new_entrants: float = Field(..., ge=1, le=5)
    overall_intensity: str = Field(..., description="Low/Moderate/High")
    detailed_analysis: dict = Field(..., description="Per-force 2-3 sentence analysis")

class SWOTAnalysis(BaseModel):
    """SWOT analysis"""
    strengths: List[str] = Field(..., min_items=3, max_items=5)
    weaknesses: List[str] = Field(..., min_items=3, max_items=5)
    opportunities: List[str] = Field(..., min_items=3, max_items=5)
    threats: List[str] = Field(..., min_items=3, max_items=5)

class PESTELAnalysis(BaseModel):
    """PESTEL analysis"""
    political: List[str]
    economic: List[str]
    social: List[str]
    technological: List[str]
    environmental: List[str]
    legal: List[str]

class BlueOceanStrategy(BaseModel):
    """Blue Ocean Strategy (Four Actions Framework)"""
    eliminate: List[str] = Field(..., description="Factors to eliminate")
    reduce: List[str] = Field(..., description="Factors to reduce below industry")
    raise: List[str] = Field(..., description="Factors to raise above industry")
    create: List[str] = Field(..., description="New factors to create")

class FrameworkAnalysis(BaseModel):
    """Combined framework analysis output"""
    porter_five_forces: PortersFiveForces
    swot_analysis: SWOTAnalysis
    pestel_analysis: PESTELAnalysis
    blue_ocean_strategy: BlueOceanStrategy

# ============================================================================
# SYNTHESIS MODEL
# ============================================================================

class ExecutiveSummary(BaseModel):
    """Final synthesis output"""
    company_name: str
    industry: str
    analysis_date: datetime
    key_findings: List[str] = Field(..., min_items=3, max_items=5, description="Top insights")
    strategic_recommendation: str = Field(..., description="Primary recommendation")
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence")
    supporting_evidence: List[str]
    next_steps: List[str]

# ============================================================================
# FINAL REPORT MODEL
# ============================================================================

class StrategicReport(BaseModel):
    """Complete report structure"""
    executive_summary: ExecutiveSummary
    company_research: CompanyResearch
    market_trends: MarketTrends
    financial_snapshot: FinancialSnapshot
    framework_analysis: FrameworkAnalysis
    recommendations: List[str] = Field(..., min_items=3, description="Actionable recommendations")
    metadata: dict = Field(
        ...,
        description="Generation metadata: timestamp, agent versions, quality scores"
    )
```

### 5.3 Data Storage Strategy

**Caching Architecture** (Multi-Level):

```python
# Level 1: In-Memory Cache (Request-scoped)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_company_profile(ticker: str) -> dict:
    """Cache company data for duration of request"""
    return yfinance.Ticker(ticker).info

# Level 2: Persistent Disk Cache (1-24 hours)
from diskcache import Cache

cache = Cache('/tmp/consultantos_cache', size_limit=int(1e9))  # 1GB

@cache.memoize(expire=3600)  # 1 hour
async def cached_web_search(query: str):
    """Cache Tavily search results"""
    return await tavily.search(query)

@cache.memoize(expire=86400)  # 24 hours
async def cached_financial_data(ticker: str):
    """Cache financial data (doesn't change often)"""
    return yfinance.Ticker(ticker).info

# Level 3: Semantic Vector Cache (ChromaDB)
import chromadb

client = chromadb.Client()
collection = client.create_collection("analysis_cache")

async def semantic_search_cache(query: str, threshold: float = 0.9):
    """Search for similar past queries"""
    results = collection.query(
        query_texts=[query],
        n_results=1
    )

    if results and results['distances'][0][0] < (1 - threshold):
        # High similarity, return cached result
        return results['documents'][0]
    else:
        # Not cached, perform fresh analysis
        return None
```

---

## 6. Agent Design

### 6.1 Research Agent (Tavily Integration)

**Purpose**: Web search and information gathering

```python
from tavily import TavilyClient
import instructor
from pydantic import BaseModel

# Initialize Tavily (already integrated in SuperCoder)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Structured output model
class CompanyResearch(BaseModel):
    company_name: str
    description: str
    products_services: List[str]
    target_market: str
    key_competitors: List[str]
    recent_news: List[str]
    sources: List[str]

# Research agent with Instructor
research_agent = adk.Agent(
    name="research_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a business research specialist with expertise in:
    - Company intelligence gathering
    - Competitive landscape analysis
    - News monitoring and trend identification

    Task: Research {company} to understand:
    1. Company Overview: Business model, products/services, target market
    2. Competitive Landscape: Key competitors and differentiation
    3. Recent Developments: Latest news, product launches, strategic moves

    Use Tavily search tool to gather current, factual information.
    Cite all sources with URLs.
    """,
    tools=[tavily_search_tool],
    response_model=CompanyResearch
)

# Tool function
def tavily_search_tool(query: str) -> dict:
    """Execute Tavily web search"""
    response = tavily.search(
        query=query,
        max_results=10,
        search_depth="advanced"
    )
    return response

# Example execution
async def execute_research(company: str):
    result = await research_agent.execute(f"Research {company}")
    return result  # Returns validated CompanyResearch object
```

### 6.2 Market Analyst Agent (Google Trends)

**Purpose**: Market interest and trend analysis

```python
from pytrends.request import TrendReq
import pandas as pd

# Initialize Google Trends
pytrend = TrendReq(hl='en-US', tz=360)

class MarketTrends(BaseModel):
    search_interest_trend: str  # Growing/Stable/Declining
    interest_data: dict  # Time series
    geographic_distribution: dict
    related_searches: List[str]
    competitive_comparison: dict

# Google Trends tool
def google_trends_tool(keywords: List[str], timeframe: str = 'today 12-m'):
    """Analyze market trends using Google Trends"""
    # Build payload
    pytrend.build_payload(keywords, timeframe=timeframe)

    # Interest over time
    interest_data = pytrend.interest_over_time()

    # Regional interest
    regional = pytrend.interest_by_region()

    # Related queries
    related = pytrend.related_queries()

    return {
        "interest_over_time": interest_data.to_dict(),
        "regional_interest": regional.to_dict(),
        "related_queries": related
    }

# Market analyst agent
market_analyst = adk.Agent(
    name="market_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a market trend analyst.

    Analyze market interest trends using Google Trends data.

    Focus on:
    1. Search Interest Trend: Is interest growing, stable, or declining?
    2. Geographic Patterns: Where is interest concentrated?
    3. Related Topics: What related searches are trending?
    4. Competitive Dynamics: How does company compare to competitors?

    Provide data-driven insights with specific percentages and trends.
    """,
    tools=[google_trends_tool],
    response_model=MarketTrends
)
```

### 6.3 Financial Analyst Agent (SEC + yfinance)

**Purpose**: Company financial analysis

```python
import yfinance as yf
from edgar import Company

class FinancialSnapshot(BaseModel):
    ticker: str
    market_cap: Optional[float]
    revenue: Optional[float]
    revenue_growth: Optional[float]
    profit_margin: Optional[float]
    pe_ratio: Optional[float]
    key_metrics: dict
    risk_assessment: str

# SEC Edgar tool
def sec_edgar_tool(ticker: str):
    """Get SEC filings data"""
    company = Company(ticker)
    filings = company.get_filings(form="10-K", count=1)

    if filings:
        latest = filings[0]
        return {
            "filing_date": latest.filing_date,
            "financials": latest.financials if hasattr(latest, 'financials') else None,
            "business_description": latest.business if hasattr(latest, 'business') else None
        }
    return None

# yfinance tool
def yfinance_tool(ticker: str):
    """Get stock and financial data"""
    stock = yf.Ticker(ticker)
    info = stock.info

    # Historical data
    history = stock.history(period="1y")

    # Financial statements
    financials = stock.financials

    return {
        "company_info": info,
        "price_history": history.to_dict(),
        "financials": financials.to_dict() if financials is not None else None
    }

# Financial analyst agent
financial_analyst = adk.Agent(
    name="financial_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a financial analyst with expertise in:
    - Financial statement analysis
    - Valuation metrics interpretation
    - Risk assessment

    Analyze company financial performance:
    1. Growth Metrics: Revenue growth, profit margins
    2. Valuation: P/E ratio, market cap vs peers
    3. Financial Health: Cash flow, debt levels
    4. Risk Factors: From SEC filings

    Provide quantitative analysis with specific numbers and percentages.
    """,
    tools=[sec_edgar_tool, yfinance_tool],
    response_model=FinancialSnapshot
)
```

### 6.4 Framework Analyst Agent (Business Frameworks)

**Purpose**: Apply strategic business frameworks

```python
class FrameworkAnalysis(BaseModel):
    porter_five_forces: PortersFiveForces
    swot_analysis: SWOTAnalysis
    pestel_analysis: PESTELAnalysis
    blue_ocean_strategy: BlueOceanStrategy

# Framework-specific prompts
PORTER_PROMPT_TEMPLATE = """
Analyze {company_name} using Porter's Five Forces framework.

Based on the research data:
{research_data}

Evaluate each force on a 1-5 scale (1=weak, 5=strong):

**1. Supplier Power**:
- How many suppliers exist?
- How critical are supplier inputs?
- Can the company switch suppliers easily?
- Score (1-5): ___
- Analysis (2-3 sentences): ___

**2. Buyer Power**:
- How concentrated are customers?
- Do buyers have alternatives?
- Is price a key buying factor?
- Score (1-5): ___
- Analysis: ___

**3. Competitive Rivalry**:
- How many direct competitors?
- Market growth rate?
- Product differentiation level?
- Score (1-5): ___
- Analysis: ___

**4. Threat of Substitutes**:
- What alternative solutions exist?
- Switching costs for customers?
- Performance comparison?
- Score (1-5): ___
- Analysis: ___

**5. Threat of New Entrants**:
- Capital requirements to enter?
- Regulatory barriers?
- Brand loyalty/network effects?
- Score (1-5): ___
- Analysis: ___

Overall Competitive Intensity: [Low/Moderate/High]
"""

SWOT_PROMPT_TEMPLATE = """
Perform SWOT analysis for {company_name}.

Based on:
- Research: {research_data}
- Market: {market_data}
- Financial: {financial_data}

**Strengths** (Internal, positive):
- What does the company do exceptionally well?
- Unique resources or capabilities?
- Competitive advantages?
List 3-5 strengths with evidence.

**Weaknesses** (Internal, negative):
- What could be improved?
- Resource limitations?
- Areas where competitors are stronger?
List 3-5 weaknesses with evidence.

**Opportunities** (External, positive):
- Market trends to capitalize on?
- Emerging customer needs?
- Partnership/expansion possibilities?
List 3-5 opportunities with evidence.

**Threats** (External, negative):
- Competitive threats?
- Regulatory/economic risks?
- Technological disruption?
List 3-5 threats with evidence.
"""

# Framework analyst agent
framework_analyst = adk.Agent(
    name="framework_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a strategic framework expert trained in McKinsey/BCG methodologies.

    Apply rigorous business frameworks to company data:
    - Porter's Five Forces (competitive dynamics)
    - SWOT Analysis (internal/external factors)
    - PESTEL Analysis (macro environment)
    - Blue Ocean Strategy (value innovation)

    Requirements:
    1. Evidence-Based: Every claim must cite specific data
    2. Quantitative: Use scores, percentages, specific numbers
    3. Structured: Follow framework methodology precisely
    4. Actionable: Link analysis to strategic implications

    Output must be professional-grade suitable for client presentations.
    """,
    response_model=FrameworkAnalysis
)
```

### 6.5 Synthesis Agent (Cross-Framework Integration)

**Purpose**: Aggregate insights and create executive summary

```python
class ExecutiveSummary(BaseModel):
    company_name: str
    industry: str
    analysis_date: datetime
    key_findings: List[str]  # Top 3-5 insights
    strategic_recommendation: str
    confidence_score: float  # 0-1
    supporting_evidence: List[str]
    next_steps: List[str]

SYNTHESIS_PROMPT_TEMPLATE = """
Create executive summary synthesizing all analysis:

**Research Findings**: {research_summary}
**Market Trends**: {market_summary}
**Financial Performance**: {financial_summary}
**Porter's 5 Forces**: {porter_summary}
**SWOT**: {swot_summary}

Your task:
1. Identify 3-5 KEY FINDINGS across all frameworks
2. Provide ONE PRIMARY STRATEGIC RECOMMENDATION
3. List 3-5 SUPPORTING EVIDENCE points
4. Suggest 3 NEXT STEPS for the company

Requirements:
- **Integrate across frameworks**: Show how insights connect
- **Prioritize**: Focus on highest-impact insights
- **Actionable**: Recommendations must be implementable
- **Confident**: Assess your confidence level (0-1) based on data quality

Format as professional executive summary suitable for C-suite presentation.
"""

synthesis_agent = adk.Agent(
    name="synthesis_agent",
    model="gemini-2.0-flash-exp",
    instruction=SYNTHESIS_PROMPT_TEMPLATE,
    response_model=ExecutiveSummary
)
```

---

## 7. Report Generation System

### 7.1 Visualization Engine (Plotly)

```python
import plotly.graph_objects as go
import plotly.express as px

# Porter's 5 Forces Radar Chart
def create_porter_radar_figure(forces: PortersFiveForces) -> go.Figure:
    """Generate radar chart for Porter's 5 Forces - returns Figure object for PDF embedding"""
    fig = go.Figure(data=go.Scatterpolar(
        r=[
            forces.supplier_power,
            forces.buyer_power,
            forces.competitive_rivalry,
            forces.threat_of_substitutes,
            forces.threat_of_new_entrants
        ],
        theta=[
            'Supplier<br>Power',
            'Buyer<br>Power',
            'Competitive<br>Rivalry',
            'Threat of<br>Substitutes',
            'New Entrant<br>Threat'
        ],
        fill='toself',
        fillcolor='rgba(0, 123, 255, 0.3)',
        line=dict(color='rgba(0, 123, 255, 1)', width=2),
        marker=dict(size=8)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['Weak', '', 'Moderate', '', 'Strong']
            )
        ),
        title=dict(
            text="Porter's Five Forces Analysis",
            font=dict(size=18, family='Arial')
        ),
        showlegend=False,
        width=600,
        height=500
    )

    return fig  # Return Figure object for PDF embedding

def create_porter_radar_html(forces: PortersFiveForces) -> str:
    """Generate HTML version for web display"""
    fig = create_porter_radar_figure(forces)
    return fig.to_html(include_plotlyjs='cdn', div_id='porter_chart')

# SWOT Matrix Visualization
def create_swot_matrix(swot: SWOTAnalysis) -> str:
    """Generate 2x2 SWOT matrix"""
    fig = go.Figure()

    # Create quadrants
    fig.add_trace(go.Scatter(
        x=[0.25, 0.75, 0.25, 0.75],
        y=[0.75, 0.75, 0.25, 0.25],
        text=[
            '<b>STRENGTHS</b><br>' + '<br>• '.join(swot.strengths[:3]),
            '<b>WEAKNESSES</b><br>' + '<br>• '.join(swot.weaknesses[:3]),
            '<b>OPPORTUNITIES</b><br>' + '<br>• '.join(swot.opportunities[:3]),
            '<b>THREATS</b><br>' + '<br>• '.join(swot.threats[:3])
        ],
        mode='text',
        textposition='middle center',
        textfont=dict(size=11, family='Arial')
    ))

    # Add quadrant backgrounds
    fig.add_shape(type="rect", x0=0, x1=0.5, y0=0.5, y1=1,
                  fillcolor="rgba(144, 238, 144, 0.2)", line_width=0)
    fig.add_shape(type="rect", x0=0.5, x1=1, y0=0.5, y1=1,
                  fillcolor="rgba(255, 182, 193, 0.2)", line_width=0)
    fig.add_shape(type="rect", x0=0, x1=0.5, y0=0, y1=0.5,
                  fillcolor="rgba(173, 216, 230, 0.2)", line_width=0)
    fig.add_shape(type="rect", x0=0.5, x1=1, y0=0, y1=0.5,
                  fillcolor="rgba(255, 218, 185, 0.2)", line_width=0)

    # Add dividing lines
    fig.add_shape(type="line", x0=0.5, x1=0.5, y0=0, y1=1,
                  line=dict(color="black", width=2))
    fig.add_shape(type="line", x0=0, x1=1, y0=0.5, y1=0.5,
                  line=dict(color="black", width=2))

    fig.update_layout(
        title="SWOT Analysis Matrix",
        xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        width=700,
        height=600,
        showlegend=False
    )

    return fig.to_html(include_plotlyjs='cdn', div_id='swot_chart')

# Market Trend Line Chart
def create_trend_chart(trend_data: dict) -> str:
    """Generate market interest trend chart"""
    df = pd.DataFrame(trend_data)

    fig = px.line(
        df,
        x='date',
        y='value',
        title='Market Interest Over Time (Google Trends)',
        markers=True
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Search Interest (0-100)',
        hovermode='x unified',
        width=800,
        height=400
    )

    return fig.to_html(include_plotlyjs='cdn', div_id='trend_chart')
```

### 7.2 PDF Generation (ReportLab)

**Why ReportLab over Playwright**:

- ✅ Faster (native PDF, no browser launch)
- ✅ Smaller dependencies (~10MB vs ~300MB)
- ✅ More reliable (no browser crashes)
- ✅ Better control over layout

```python
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import tempfile

async def generate_pdf_report(report: StrategicReport) -> bytes:
    """Generate professional PDF report using ReportLab"""

    # Create temporary PDF file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_path = tmp.name

    # Create document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=12
    )

    # Build story (content)
    story = []

    # ===== COVER PAGE =====
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("STRATEGIC ANALYSIS REPORT", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        f"<b>{report.executive_summary.company_name}</b>",
        ParagraphStyle('CompanyName', parent=styles['Normal'], fontSize=18, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(
        f"{report.executive_summary.industry}",
        ParagraphStyle('Industry', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph(
        f"Generated by ConsultantOS<br/>{datetime.now().strftime('%B %d, %Y')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, textColor=colors.grey)
    ))
    story.append(PageBreak())

    # ===== EXECUTIVE SUMMARY =====
    story.append(Paragraph("Executive Summary", heading_style))

    # Key Findings
    story.append(Paragraph("<b>Key Findings:</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    for finding in report.executive_summary.key_findings:
        story.append(Paragraph(f"• {finding}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Strategic Recommendation
    story.append(Paragraph("<b>Strategic Recommendation:</b>", styles['Normal']))
    story.append(Paragraph(report.executive_summary.strategic_recommendation, styles['Normal']))
    story.append(Spacer(1, 12))

    # Confidence Score
    confidence_pct = f"{report.executive_summary.confidence_score * 100:.0f}%"
    story.append(Paragraph(f"<b>Analysis Confidence:</b> {confidence_pct}", styles['Normal']))
    story.append(PageBreak())

    # ===== PORTER'S 5 FORCES =====
    story.append(Paragraph("Porter's Five Forces Analysis", heading_style))

    # Generate and embed chart as image
    # Use kaleido for Plotly → PNG conversion (recommended for ReportLab)
    import plotly.io as pio
    import io

    porter_fig = create_porter_radar_figure(report.framework_analysis.porter_five_forces)

    # Convert Plotly figure to PNG bytes
    try:
        img_bytes = pio.to_image(porter_fig, format="png", width=600, height=500)
        img_buffer = io.BytesIO(img_bytes)

        # Add image to PDF
        from reportlab.platypus import Image
        porter_img = Image(img_buffer, width=5*inch, height=4*inch)
        story.append(porter_img)
    except Exception as e:
        logger.warning(f"Failed to render Porter chart: {e}. Falling back to table.")
        # Fallback to table format if chart rendering fails

    porter_data = [
        ['Force', 'Score', 'Assessment'],
        ['Supplier Power', f"{report.framework_analysis.porter_five_forces.supplier_power}/5", ''],
        ['Buyer Power', f"{report.framework_analysis.porter_five_forces.buyer_power}/5", ''],
        ['Competitive Rivalry', f"{report.framework_analysis.porter_five_forces.competitive_rivalry}/5", ''],
        ['Threat of Substitutes', f"{report.framework_analysis.porter_five_forces.threat_of_substitutes}/5", ''],
        ['Threat of New Entrants', f"{report.framework_analysis.porter_five_forces.threat_of_new_entrants}/5", '']
    ]

    porter_table = Table(porter_data, colWidths=[2.5*inch, 1*inch, 3*inch])
    porter_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(porter_table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        f"<b>Overall Competitive Intensity:</b> {report.framework_analysis.porter_five_forces.overall_intensity}",
        styles['Normal']
    ))
    story.append(PageBreak())

    # ===== SWOT ANALYSIS =====
    story.append(Paragraph("SWOT Analysis", heading_style))

    swot_data = [
        ['Strengths', 'Weaknesses'],
        [
            '<br/>'.join(['• ' + s for s in report.framework_analysis.swot_analysis.strengths]),
            '<br/>'.join(['• ' + w for w in report.framework_analysis.swot_analysis.weaknesses])
        ],
        ['Opportunities', 'Threats'],
        [
            '<br/>'.join(['• ' + o for o in report.framework_analysis.swot_analysis.opportunities]),
            '<br/>'.join(['• ' + t for t in report.framework_analysis.swot_analysis.threats])
        ]
    ]

    swot_table = Table(swot_data, colWidths=[3.25*inch, 3.25*inch])
    swot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('BACKGROUND', (0, 2), (-1, 2), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(swot_table)
    story.append(PageBreak())

    # ===== RECOMMENDATIONS =====
    story.append(Paragraph("Strategic Recommendations", heading_style))
    for i, rec in enumerate(report.recommendations, 1):
        story.append(Paragraph(f"<b>{i}.</b> {rec}", styles['Normal']))
        story.append(Spacer(1, 8))

    # Build PDF
    doc.build(story)

    # Read bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # Cleanup
    os.unlink(pdf_path)

    return pdf_bytes
```

### 7.3 Report Template (Alternative: Jinja2 + WeasyPrint)

**Fallback if ReportLab too complex**:

```python
from jinja2 import Template
from weasyprint import HTML

# HTML template
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Strategic Analysis: {{ company_name }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'Arial', sans-serif;
            color: #333;
            line-height: 1.6;
        }
        .cover {
            text-align: center;
            padding: 100px 0;
            page-break-after: always;
        }
        .cover h1 {
            font-size: 36px;
            color: #0066cc;
            margin-bottom: 20px;
        }
        .section {
            page-break-before: always;
            margin-bottom: 40px;
        }
        .section h2 {
            color: #0066cc;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
        }
        .key-findings {
            background: #f0f8ff;
            border-left: 4px solid #0066cc;
            padding: 15px;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th {
            background: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
        }
        td {
            padding: 10px;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover">
        <h1>Strategic Analysis Report</h1>
        <h2>{{ company_name }}</h2>
        <p>{{ industry }}</p>
        <p>{{ generated_date }}</p>
    </div>

    <!-- Executive Summary -->
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="key-findings">
            <h3>Key Findings</h3>
            <ul>
                {% for finding in key_findings %}
                <li>{{ finding }}</li>
                {% endfor %}
            </ul>
        </div>
        <p><strong>Strategic Recommendation:</strong> {{ recommendation }}</p>
        <p><strong>Confidence:</strong> {{ confidence }}%</p>
    </div>

    <!-- Porter's 5 Forces -->
    <div class="section">
        <h2>Porter's Five Forces Analysis</h2>
        {{ porter_chart | safe }}
        <table>
            <tr>
                <th>Force</th>
                <th>Score</th>
                <th>Assessment</th>
            </tr>
            <tr>
                <td>Supplier Power</td>
                <td>{{ porter.supplier_power }}/5</td>
                <td>{{ porter.detailed_analysis.supplier_power }}</td>
            </tr>
            <!-- ... more rows ... -->
        </table>
    </div>

    <!-- SWOT Analysis -->
    <div class="section">
        <h2>SWOT Analysis</h2>
        {{ swot_chart | safe }}
    </div>

    <!-- Recommendations -->
    <div class="section">
        <h2>Strategic Recommendations</h2>
        <ol>
            {% for rec in recommendations %}
            <li>{{ rec }}</li>
            {% endfor %}
        </ol>
    </div>
</body>
</html>
"""

async def generate_report_weasyprint(report: StrategicReport) -> bytes:
    """Generate PDF using Jinja2 + WeasyPrint (simpler than ReportLab)"""
    template = Template(REPORT_TEMPLATE)

    # Render HTML
    html_content = template.render(
        company_name=report.executive_summary.company_name,
        industry=report.executive_summary.industry,
        generated_date=report.executive_summary.analysis_date.strftime('%B %d, %Y'),
        key_findings=report.executive_summary.key_findings,
        recommendation=report.executive_summary.strategic_recommendation,
        confidence=f"{report.executive_summary.confidence_score * 100:.0f}",
        porter=report.framework_analysis.porter_five_forces,
        porter_chart=create_porter_radar(report.framework_analysis.porter_five_forces),
        swot_chart=create_swot_matrix(report.framework_analysis.swot_analysis),
        recommendations=report.recommendations
    )

    # Convert to PDF
    pdf = HTML(string=html_content).write_pdf()

    return pdf
```

---

## 8. API Design

### 8.1 FastAPI Application Structure

```python
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import logging

# Initialize FastAPI
app = FastAPI(
    title="ConsultantOS - Business Intelligence Research Engine",
    description="Multi-agent strategic analysis for independent consultants",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting - CORRECT SETUP
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup Cloud Logging
from google.cloud import logging as cloud_logging
import logging

logging_client = cloud_logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Custom exception classes
class AnalysisError(Exception):
    """Base exception for analysis failures"""
    pass

class AgentTimeoutError(AnalysisError):
    """Raised when agent execution times out"""
    pass

class PDFGenerationError(AnalysisError):
    """Raised when PDF generation fails"""
    pass

# Initialize cache (optional Redis backend)
@app.on_event("startup")
async def startup():
    # FastAPICache.init(RedisBackend(redis), prefix="consultantos-cache")
    logger.info("Application startup complete")
    logger.info("Rate limiter configured: 10 requests/hour per IP")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Main analysis endpoint with comprehensive error handling
@app.post("/analyze")
@limiter.limit("10/hour")  # 10 analyses per hour per user
async def analyze_company(
    request: Request,
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate strategic analysis report for a company

    Rate Limited: 10 requests/hour per IP
    Response Time: 30-60 seconds (may timeout for complex analyses)
    """
    start_time = datetime.now()
    report_id = None

    try:
        # Validate request
        if not analysis_request.company or len(analysis_request.company.strip()) == 0:
            raise HTTPException(status_code=400, detail="Company name is required")

        report_id = f"{analysis_request.company}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(
            "Analysis started",
            extra={
                "report_id": report_id,
                "company": analysis_request.company,
                "user_ip": request.client.host,
                "frameworks": analysis_request.frameworks,
                "depth": analysis_request.depth
            }
        )

        # Execute multi-agent workflow with timeout
        try:
            report = await asyncio.wait_for(
                orchestrator.execute(analysis_request),
                timeout=240.0  # 4 minutes timeout (Cloud Run allows 300s)
            )
        except asyncio.TimeoutError:
            logger.error(f"Analysis timeout for {analysis_request.company}")
            raise HTTPException(
                status_code=504,
                detail="Analysis timed out. Please try with a simpler query or contact support."
            )
        except AnalysisError as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

        # Generate PDF with error handling
        try:
            pdf_bytes = await generate_pdf_report(report)
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            # Return JSON response even if PDF fails
            return {
                "status": "partial_success",
                "report_id": report_id,
                "report_url": None,
                "error": "PDF generation failed, but analysis completed",
                "executive_summary": report.executive_summary.dict(),
                "confidence": report.executive_summary.confidence_score,
                "generated_at": datetime.now().isoformat()
            }

        # Store in Cloud Storage (background task with error handling)
        background_tasks.add_task(
            upload_to_storage_safe,
            report_id,
            pdf_bytes,
            analysis_request.company
        )

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()

        logger.info(
            "Analysis completed successfully",
            extra={
                "report_id": report_id,
                "company": analysis_request.company,
                "execution_time_seconds": execution_time,
                "confidence": report.executive_summary.confidence_score
            }
        )

        # Return structured report + PDF URL
        return {
            "status": "success",
            "report_id": report_id,
            "report_url": f"https://storage.googleapis.com/consultantos-reports/{report_id}.pdf",
            "executive_summary": report.executive_summary.dict(),
            "confidence": report.executive_summary.confidence_score,
            "generated_at": datetime.now().isoformat(),
            "execution_time_seconds": execution_time
        }

    except HTTPException:
        # Re-raise HTTP exceptions (rate limiting, validation errors)
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during analysis: {str(e)}",
            exc_info=True,
            extra={
                "report_id": report_id,
                "company": analysis_request.company if analysis_request else None
            }
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )

# Safe storage upload with error handling
async def upload_to_storage_safe(report_id: str, pdf_bytes: bytes, company: str):
    """Upload PDF to Cloud Storage with error handling"""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket("consultantos-reports")
        blob = bucket.blob(f"{report_id}.pdf")
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")
        logger.info(f"PDF uploaded successfully: {report_id}")
    except Exception as e:
        logger.error(f"Failed to upload PDF {report_id}: {str(e)}", exc_info=True)
        # Don't raise - background task failures shouldn't crash the app

# Get report by ID
@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Retrieve generated report"""
    # Check if report exists in Cloud Storage
    report_url = f"https://storage.googleapis.com/consultantos-reports/{report_id}.pdf"

    # In production, validate report exists before returning URL
    return {
        "report_id": report_id,
        "report_url": report_url,
        "status": "available"
    }
```

### 8.2 Request/Response Models

```python
# Request Model
class AnalysisRequest(BaseModel):
    company: str = Field(
        ...,
        description="Company name or ticker symbol",
        example="Tesla"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector (optional, will be auto-detected)",
        example="Electric Vehicles"
    )
    frameworks: List[str] = Field(
        default=["porter", "swot", "pestel", "blue_ocean"],
        description="Frameworks to apply",
        example=["porter", "swot"]
    )
    depth: str = Field(
        default="standard",
        description="Analysis depth",
        enum=["quick", "standard", "deep"]
    )

# Response Model
class AnalysisResponse(BaseModel):
    status: str = Field(..., description="Success/failure status")
    report_id: str = Field(..., description="Unique report identifier")
    report_url: str = Field(..., description="PDF report download URL")
    executive_summary: ExecutiveSummary
    confidence: float = Field(..., ge=0, le=1, description="Analysis confidence score")
    generated_at: str = Field(..., description="ISO 8601 timestamp")
```

---

## 9. Deployment Architecture

### 9.1 Cloud Run Configuration

```yaml
# cloud-run-config.yaml
service_name: consultantos-bi-engine
region: us-central1

resources:
  cpu: 2
  memory: 2Gi
  max_instances: 10
  min_instances: 0 # Scale to zero for cost savings

runtime:
  platform: python311
  timeout: 300s # 5 minutes for analysis

environment_variables:
  - TAVILY_API_KEY: ${TAVILY_API_KEY}
  - GEMINI_API_KEY: ${GEMINI_API_KEY}
  - ENVIRONMENT: production

secrets:
  - tavily-api-key:latest → TAVILY_API_KEY
  - gemini-api-key:latest → GEMINI_API_KEY

ingress: all
allow_unauthenticated: true # For hackathon demo (restrict post-hackathon)
```

### 9.2 Deployment Commands

```bash
# Build and deploy to Cloud Run (using buildpacks)
# Note: Ensure secrets exist in Secret Manager and service account has Secret Manager access
gcloud run deploy consultantos-bi-engine \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets GEMINI_API_KEY=projects/$(gcloud config get-value project)/secrets/gemini-api-key:latest,TAVILY_API_KEY=projects/$(gcloud config get-value project)/secrets/tavily-api-key:latest

# Check deployment status
gcloud run services describe consultantos-bi-engine --region us-central1

# View logs
gcloud run services logs read consultantos-bi-engine --region us-central1
```

### 9.3 Multiple Cloud Run Services (Bonus Points)

**Architecture**: Split into 2 services for +0.4 bonus points

```
Service 1: Analysis API
- Handles agent orchestration
- Fast response time
- Scales independently

Service 2: Report Generation
- Handles PDF generation
- Resource-intensive
- Separate scaling
```

```yaml
# Service 1: Analysis API
service: consultantos-analysis-api
resources:
  cpu: 2
  memory: 1Gi
timeout: 60s

# Service 2: Report Generator
service: consultantos-report-generator
resources:
  cpu: 1
  memory: 2Gi  # More memory for PDF generation
timeout: 300s
```

---

## 10. Security & Performance

### 10.1 API Security

```python
# Rate limiting (slowapi)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/hour")  # 10 analyses per hour per IP
async def analyze_company(request: Request, ...):
    pass

# API key authentication (post-hackathon)
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("VALID_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Input validation (Pydantic)
class AnalysisRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=100)
    # Pydantic automatically validates types, length, format
```

### 10.2 Secret Management

**Setup Instructions**:

```bash
# 1. Create secrets in Secret Manager
gcloud secrets create tavily-api-key --data-file=- <<< "your-tavily-key"
gcloud secrets create gemini-api-key --data-file=- <<< "your-gemini-key"

# 2. Grant Cloud Run service account access
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding tavily-api-key \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
```

**Cloud Run Configuration** (mount secrets as environment variables):

```yaml
# cloud-run-config.yaml
secrets:
  - name: TAVILY_API_KEY
    valueFrom:
      secretKeyRef:
        name: tavily-api-key
        key: latest
  - name: GEMINI_API_KEY
    valueFrom:
      secretKeyRef:
        name: gemini-api-key
        key: latest
```

**Application Code** (with fallback to environment variables):

```python
from google.cloud import secretmanager
import os
import logging

logger = logging.getLogger(__name__)

def get_secret(secret_id: str, default_env_var: str = None) -> str:
    """
    Retrieve secret from Google Secret Manager with fallback to environment variable.

    Args:
        secret_id: Secret name in Secret Manager
        default_env_var: Environment variable name as fallback

    Returns:
        Secret value as string
    """
    # Try Secret Manager first
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")

        if not project_id:
            raise ValueError("GCP_PROJECT_ID not set")

        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})
        secret_value = response.payload.data.decode('UTF-8')

        logger.info(f"Retrieved secret {secret_id} from Secret Manager")
        return secret_value

    except Exception as e:
        logger.warning(f"Failed to retrieve secret {secret_id} from Secret Manager: {e}")

        # Fallback to environment variable
        if default_env_var:
            env_value = os.getenv(default_env_var)
            if env_value:
                logger.info(f"Using environment variable {default_env_var} as fallback")
                return env_value

        # Final fallback: direct environment variable with secret_id name
        env_value = os.getenv(secret_id.upper().replace("-", "_"))
        if env_value:
            logger.info(f"Using environment variable {secret_id.upper().replace('-', '_')} as fallback")
            return env_value

        raise ValueError(f"Secret {secret_id} not found in Secret Manager or environment variables")

# Usage with error handling
try:
    TAVILY_API_KEY = get_secret("tavily-api-key", "TAVILY_API_KEY")
    GEMINI_API_KEY = get_secret("gemini-api-key", "GEMINI_API_KEY")
except ValueError as e:
    logger.error(f"Failed to load required secrets: {e}")
    raise
```

### 10.3 Monitoring & Observability

**Structured Logging Strategy**:

```python
import structlog
from google.cloud import logging as cloud_logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()  # JSON for Cloud Logging
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in application
logger.info(
    "analysis_started",
    report_id=report_id,
    company=company,
    frameworks=frameworks,
    user_ip=request.client.host
)

logger.error(
    "agent_failed",
    agent_name="research_agent",
    error=str(e),
    company=company,
    exc_info=True
)
```

**Key Metrics to Log**:

1. **Request Metrics**:

   - Request ID, company, frameworks requested
   - User IP (for rate limiting)
   - Request timestamp

2. **Agent Execution Metrics**:

   - Agent name and execution time
   - Success/failure status
   - Token usage (if available from Gemini API)
   - Error messages with stack traces

3. **Performance Metrics**:

   - Total analysis time
   - Phase 1 (parallel) duration
   - Phase 2 (sequential) duration
   - PDF generation time
   - Cache hit/miss rates

4. **Business Metrics**:
   - Analysis confidence scores
   - Framework completion rates
   - Error rates by agent type

**Cloud Logging Queries**:

```bash
# View all analysis requests
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.report_id:*" --limit 50

# Find failed analyses
gcloud logging read "resource.type=cloud_run_revision AND severity=ERROR" --limit 20

# Monitor agent performance
gcloud logging read "jsonPayload.agent_name:* AND jsonPayload.execution_time:*" --limit 50

# Track rate limiting
gcloud logging read "jsonPayload.rate_limit:*" --limit 20
```

**Error Alerting** (Post-Hackathon):

```python
# Set up error alerting via Cloud Monitoring
from google.cloud import monitoring_v3

def create_error_alert():
    """Create alert policy for high error rates"""
    client = monitoring_v3.AlertPolicyServiceClient()

    # Alert if error rate > 10% in 5 minutes
    policy = monitoring_v3.AlertPolicy(
        display_name="High Error Rate",
        conditions=[
            monitoring_v3.AlertPolicy.Condition(
                display_name="Error rate threshold",
                condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                    filter='resource.type="cloud_run_revision" AND severity="ERROR"',
                    comparison=monitoring_v3.ComparisonType.COMPARISON_GT,
                    threshold_value=0.1
                )
            )
        ]
    )

    client.create_alert_policy(name=f"projects/{PROJECT_ID}", alert_policy=policy)
```

### 10.4 Performance Optimization

**Caching Strategy**:

```python
from diskcache import Cache
import hashlib

cache = Cache('/tmp/consultantos_cache', size_limit=int(1e9))  # 1GB

def cache_key(company: str, frameworks: List[str]) -> str:
    """Generate cache key from request parameters"""
    key_string = f"{company}:{'|'.join(sorted(frameworks))}"
    return hashlib.md5(key_string.encode()).hexdigest()

@cache.memoize(expire=3600)  # 1 hour cache
async def cached_analysis(cache_key: str, request: AnalysisRequest):
    """Cache analysis results to avoid re-running for same company"""
    return await orchestrator.execute(request)

# Semantic caching (ChromaDB)
async def semantic_cache_lookup(company: str, threshold: float = 0.95):
    """Check if similar analysis exists in vector store"""
    results = chromadb_collection.query(
        query_texts=[f"strategic analysis for {company}"],
        n_results=1
    )

    if results['distances'][0][0] < (1 - threshold):
        # High similarity, return cached
        return results['documents'][0]
    return None
```

**Parallel Execution**:

```python
import asyncio

async def execute_parallel_agents(company: str):
    """Run independent agents in parallel"""
    results = await asyncio.gather(
        research_agent.execute(company),
        market_analyst.execute(company),
        financial_analyst.execute(company)
    )

    return {
        "research": results[0],
        "market": results[1],
        "financial": results[2]
    }
```

---

## 11. Quality Assurance

### 11.1 Testing Strategy

**Test Coverage Goals**:

- Unit tests: 70%+ coverage for core logic
- Integration tests: All agent workflows
- API tests: All endpoints with success and error cases
- PDF generation tests: Verify report structure and content

**Test Framework**: pytest with pytest-asyncio for async tests

```python
# tests/test_agents.py
import pytest
from unittest.mock import AsyncMock, patch
from consultantos.agents import research_agent, market_analyst

@pytest.mark.asyncio
async def test_research_agent_success():
    """Test research agent with valid company"""
    with patch('consultantos.agents.tavily_search') as mock_tavily:
        mock_tavily.return_value = {
            "results": [{"title": "Test", "url": "https://test.com"}]
        }

        result = await research_agent.run("Research Tesla")
        assert result is not None
        assert "company_name" in result

@pytest.mark.asyncio
async def test_research_agent_timeout():
    """Test research agent timeout handling"""
    with patch('consultantos.agents.tavily_search', side_effect=asyncio.TimeoutError):
        with pytest.raises(AgentTimeoutError):
            await research_agent.run("Research Tesla")

# tests/test_orchestrator.py
@pytest.mark.asyncio
async def test_parallel_phase_execution():
    """Test parallel agent execution"""
    request = AnalysisRequest(company="Tesla", frameworks=["porter"])

    with patch('consultantos.orchestrator.parallel_phase.run') as mock_parallel:
        mock_parallel.return_value = {
            "research_agent": {"company_name": "Tesla"},
            "market_analyst": {"trend": "growing"},
            "financial_analyst": {"revenue": 1000000}
        }

        result = await execute_parallel_phase("Tesla")
        assert "research" in result
        assert "market" in result
        assert "financial" in result

@pytest.mark.asyncio
async def test_full_workflow_integration():
    """Integration test for complete workflow"""
    request = AnalysisRequest(company="Netflix", frameworks=["porter", "swot"])

    # Mock all external APIs
    with patch('consultantos.agents.tavily_search'), \
         patch('consultantos.agents.google_trends'), \
         patch('consultantos.agents.yfinance'):

        report = await orchestrator.execute(request)
        assert report.executive_summary is not None
        assert report.framework_analysis is not None

# tests/test_api.py
from fastapi.testclient import TestClient
from consultantos.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_endpoint_success():
    """Test analysis endpoint with valid request"""
    response = client.post(
        "/analyze",
        json={
            "company": "Tesla",
            "frameworks": ["porter"],
            "depth": "standard"
        }
    )
    assert response.status_code == 200
    assert "report_id" in response.json()

def test_analyze_endpoint_rate_limit():
    """Test rate limiting"""
    # Make 11 requests (limit is 10/hour)
    for i in range(11):
        response = client.post(
            "/analyze",
            json={"company": f"Company{i}", "frameworks": ["porter"]}
        )

    assert response.status_code == 429  # Too Many Requests

def test_analyze_endpoint_validation():
    """Test request validation"""
    response = client.post(
        "/analyze",
        json={"company": "", "frameworks": []}  # Invalid
    )
    assert response.status_code == 422  # Validation Error

# tests/test_pdf_generation.py
@pytest.mark.asyncio
async def test_pdf_generation():
    """Test PDF report generation"""
    report = StrategicReport(
        executive_summary=ExecutiveSummary(...),
        framework_analysis=FrameworkAnalysis(...),
        # ... other fields
    )

    pdf_bytes = await generate_pdf_report(report)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")  # PDF magic bytes

@pytest.mark.asyncio
async def test_pdf_generation_chart_fallback():
    """Test PDF generation falls back to table if chart fails"""
    with patch('plotly.io.to_image', side_effect=Exception("Chart render failed")):
        report = StrategicReport(...)
        pdf_bytes = await generate_pdf_report(report)
        # Should still generate PDF with table instead of chart
        assert pdf_bytes is not None
```

**Running Tests**:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=consultantos --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run integration tests only
pytest tests/test_orchestrator.py -v -m integration
```

### 11.2 Pre-Hackathon Validation (CRITICAL)

**Quality Validation Test** (Must complete THIS WEEK):

```python
# Generate Netflix case study
async def quality_validation_test():
    """
    Generate Netflix competitive analysis
    Compare against published McKinsey/BCG reports
    Get ex-consultant review
    """
    company = "Netflix"

    # Generate report
    report = await orchestrator.execute(
        AnalysisRequest(
            company=company,
            frameworks=["porter", "swot", "blue_ocean"]
        )
    )

    # Manual review checklist:
    # 1. Porter's 5 Forces: Are scores (1-5) justified with evidence?
    # 2. SWOT: Are all 4 quadrants filled with 3-5 specific items?
    # 3. Blue Ocean: Do ERRC actions make strategic sense?
    # 4. Overall: Does analysis cite specific data points (not generic)?

    # Target: ≥6/10 quality rating from 3 ex-consultants
    return report

# Run validation
report = await quality_validation_test()
print(f"Quality Score: {report.executive_summary.confidence_score}")
```

**GO/NO-GO Gate**: If quality score <0.6, project is NOT viable.

### 11.2 Framework Quality Checklist

**Porter's 5 Forces**:

- [ ] Each force scored 1-5 with justification
- [ ] Specific evidence cited (not "competitors exist")
- [ ] Industry comparison included ("vs average industry")
- [ ] Overall intensity assessment matches scores

**SWOT Analysis**:

- [ ] 3-5 items per quadrant (not generic lists)
- [ ] Internal vs External categorization correct
- [ ] Positive vs Negative categorization correct
- [ ] Each item has supporting evidence

**Blue Ocean Strategy**:

- [ ] ERRC actions aligned with company strategy
- [ ] Cost/value implications explained
- [ ] Competitive comparison included

**Executive Summary**:

- [ ] 3-5 key findings (not 10+ bullet points)
- [ ] Primary recommendation clear and actionable
- [ ] Confidence score justified
- [ ] Next steps specific and time-bound

---

## 12. Risk Mitigation

### 12.1 Technical Risks

| Risk                          | Mitigation                                        | Status      |
| ----------------------------- | ------------------------------------------------- | ----------- |
| **Google ADK learning curve** | Allocate 4-6 hours Day 1, fallback to CrewAI      | ⚠️ CRITICAL |
| **LLM output quality <60%**   | Iterate prompts, validate with Netflix case study | ⚠️ CRITICAL |
| **API rate limits**           | Aggressive caching, semantic deduplication        | 🟡 MEDIUM   |
| **Cloud Run cold starts**     | Min instances=1 during demo, warmup requests      | 🟢 LOW      |
| **PDF generation slow**       | Use ReportLab (faster than Playwright)            | 🟢 LOW      |

### 12.2 Business Risks

| Risk                                       | Mitigation                            | Validation     |
| ------------------------------------------ | ------------------------------------- | -------------- |
| **Consultants won't pay $49/mo**           | Customer discovery: 10 interviews     | THIS WEEK      |
| **Quality below McKinsey standard**        | Netflix case study comparison         | THIS WEEK      |
| **Perplexity adds frameworks in 3 months** | Build community moat post-hackathon   | POST-HACKATHON |
| **Academic integrity backlash**            | Drop MBA student positioning entirely | IMMEDIATE      |

### 12.3 Decision Gates

**Pre-Hackathon Gate** (End of This Week):

- ✅ Quality validation: 6/10+ from ex-consultants
- ✅ Customer discovery: 7/10 consultants "definitely yes" at $49/mo
- ✅ Technical feasibility: Vertical slice (Porter's 5 Forces) in 8 hours

**Hackathon Gate** (End of Day 1):

- ✅ Google ADK working OR pivoted to CrewAI
- ✅ All 5 agents coordinating successfully
- ✅ Basic report generation functional

**Post-Hackathon Gate** (Month 3):

- ✅ 10 paying customers ($490 MRR)
- ✅ 1 case study: consultant won engagement using tool
- ✅ Quality score ≥0.7 from beta user feedback

---

## Appendices

### Appendix A: Open Source Libraries Reference

See `open_source_enhancements_analysis.md` for complete list of 47+ libraries.

**High Priority**:

- ReportLab (PDF generation)
- finviz (financial data)
- FastAPI-Cache (caching)
- quantstats (financial metrics)
- sentence-transformers (embeddings)

### Appendix B: Hackathon Requirements Checklist

- [x] Google ADK as primary orchestrator
- [x] Minimum 2 agents (we have 5)
- [x] Deploy to Cloud Run
- [x] Public GitHub repository
- [ ] Use Google AI models (Gemini Pro) - IN PROGRESS
- [ ] Multiple Cloud Run services (bonus) - OPTIONAL
- [ ] Blog post about build (bonus) - OPTIONAL
- [ ] Social media with #CloudRunHackathon (bonus) - OPTIONAL

### Appendix C: Business Panel Recommendations

**Primary Recommendation**: **CONDITIONAL GO**

**Conditions**:

1. Quality validation (Netflix case study ≥6/10)
2. Customer discovery (7/10 consultants willing to pay)
3. Technical feasibility (vertical slice in 8 hours)

**Strategic Focus**:

- **Beachhead**: Independent consultants ONLY (not VCs or strategy directors)
- **Value Prop**: Credibility > Cost ("McKinsey-grade frameworks" not "cheap alternative")
- **Moat**: Template library + community (post-hackathon)

**Post-Hackathon Path**:

- Months 1-3: 10 paying customers ($490 MRR)
- Months 4-6: 50 paying customers ($2,450 MRR)
- Months 7-12: 255+ paying customers ($12,500+ MRR = $150K+ ARR)

---

**Document Status**: ✅ Complete
**Last Updated**: November 7, 2025
**Next Review**: After pre-hackathon validation tests
**Owner**: Rish2Jain
**Stakeholders**: Hackathon judges, potential customers, development team

---

**END OF DESIGN DOCUMENT**
