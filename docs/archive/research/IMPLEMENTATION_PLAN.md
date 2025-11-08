# ConsultantOS - Complete Implementation Plan

**Project Name**: Business Intelligence Research Engine (ConsultantOS)
**Version**: 2.0 (Strategic Alignment)
**Date**: November 7, 2025
**Hackathon Deadline**: November 10, 2025 @ 5:00pm PST
**Total Timeline**: 3 days (28 hours estimated) + Pre-hackathon validation

---

## Table of Contents

1. [Pre-Hackathon Validation (THIS WEEK - CRITICAL)](#1-pre-hackathon-validation-this-week---critical)
2. [Day 1: Foundation (8 hours)](#2-day-1-foundation-8-hours)
3. [Day 2: Multi-Agent System (10 hours)](#3-day-2-multi-agent-system-10-hours)
4. [Day 3: Reports & Deployment (10 hours)](#4-day-3-reports--deployment-10-hours)
5. [Post-Hackathon Roadmap (12 months)](#5-post-hackathon-roadmap-12-months)
6. [Risk Mitigation Strategies](#6-risk-mitigation-strategies)
7. [Success Metrics & Decision Gates](#7-success-metrics--decision-gates)

---

## 1. Pre-Hackathon Validation (THIS WEEK - CRITICAL)

**Timeline**: November 7-8, 2025 (2 days before hackathon)
**Status**: 🔴 BLOCKING - Must complete before hackathon GO/NO-GO decision

### 1.1 Quality Validation Test (8 hours)

**Objective**: Prove we can achieve 60%+ McKinsey quality

#### Task 1.1.1: Generate Netflix Case Study (3 hours)

```bash
# Setup
cd /Users/rish2jain/Documents/GitHub/SuperCoder/SuperCoder
python supercoder.py

# Prompt
"Generate strategic analysis for Netflix using Porter's 5 Forces and SWOT analysis"
```

**Deliverables**:

- [ ] Porter's 5 Forces analysis with 1-5 scores
- [ ] SWOT analysis with 3-5 items per quadrant
- [ ] Executive summary with key findings
- [ ] All analysis backed by specific evidence (not generic)

**Quality Checklist**:

- [ ] Porter scores justified with industry data
- [ ] SWOT items specific (not "strong brand" but "97M US subscribers, 40% market share")
- [ ] Analysis cites numbers (revenue, growth, market share)
- [ ] Reads like consultant report (not ChatGPT generic output)

#### Task 1.1.2: Benchmark Against McKinsey (2 hours)

```bash
# Research McKinsey reports on Netflix
# Compare structure, depth, evidence quality
```

**Find**:

- [ ] Published McKinsey/BCG analysis on Netflix or streaming industry
- [ ] Compare framework application (Porter, SWOT structure)
- [ ] Identify quality gaps (what's missing in our output?)

**Target**: Our analysis should have ≥60% of McKinsey depth and specificity

#### Task 1.1.3: Ex-Consultant Review (3 hours)

**Recruitment**:

- [ ] Find 3 ex-Big 4 consultants (LinkedIn, network)
- [ ] Send Netflix report + review rubric
- [ ] Request 30-min feedback call

**Review Rubric** (1-10 scale):

```
Framework Application (3 points):
- Are frameworks applied correctly? (methodology)
- Are scores/categorizations justified?

Evidence Quality (3 points):
- Are claims backed by specific data?
- Are sources credible and cited?

Professional Polish (2 points):
- Would you show this to a client?
- Formatting and clarity?

Strategic Value (2 points):
- Are insights actionable?
- Would this help win business?
```

**Success Criterion**: Average score ≥6/10 from 3 reviewers

**GO/NO-GO Gate**: If <6/10 → Project is NOT viable, pivot to different hackathon idea

---

### 1.2 Customer Discovery (12 hours)

**Objective**: Validate consultants will pay $49/mo

#### Task 1.2.1: Recruit 10 Independent Consultants (4 hours)

**Target Profile**:

- Ex-Big 4 (McKinsey, BCG, Bain, Deloitte)
- Now independent or boutique firm (solo or 2-5 people)
- Revenue: $100K-300K annual billing
- Geography: US/UK (English-language markets)

**Outreach Channels**:

```bash
# LinkedIn Search
"Independent strategy consultant" + "Ex-McKinsey"
"Strategy consultant" + "Freelance"
"Business strategy consultant" + location:United States

# Filters
- Current company: "Self-employed" or "Independent"
- Past company: McKinsey, BCG, Bain, Deloitte
- Industry: Management Consulting

# Message Template
Subject: Quick feedback on AI tool for strategy consultants?

Hi [Name],

I'm building an AI tool that helps independent consultants generate
McKinsey-grade framework analysis (Porter's 5 Forces, SWOT, Blue Ocean)
in 30 minutes instead of 2 days.

Would you be open to a 15-minute call this week to share feedback?
I'll show you a demo and get your thoughts on pricing/features.

[Your Name]
```

**Target**: 10 scheduled calls by end of November 7

#### Task 1.2.2: Customer Discovery Interviews (6 hours)

**Interview Script** (15 minutes each):

```markdown
# Introduction (2 min)

"I'm building ConsultantOS - an AI tool that generates strategic
framework analysis for consultants. Can I show you a quick demo?"

# Demo (5 min)

[Screen share Netflix case study]
"Here's what it generates: Porter's 5 Forces, SWOT, executive summary.
Takes 30 minutes vs 20-40 hours of manual research."

# Discovery Questions (6 min)

1. "How much time do you currently spend on framework application per engagement?"
   [Listen for: 20-40 hours → our tool saves this]

2. "What frameworks do you use most often?"
   [Listen for: Porter, SWOT, Blue Ocean → prioritize these]

3. "What's your biggest pain point when creating strategic deliverables?"
   [Listen for: time, credibility, consistency]

4. "If this tool saved you 20 hours per engagement, what would you pay per month?"
   [Listen for: $49-99 range]

5. "On a scale of 1-10, how likely would you be to use this?"
   [Target: ≥7/10]

6. "What would make this a MUST-HAVE vs nice-to-have?"
   [Listen for: quality, templates, credibility]

# Close (2 min)

"Would you be interested in beta testing when we launch in 2 weeks?"
[Get email if yes]
```

**Data Collection**:
| Consultant | Time Savings | WTP ($/mo) | Likelihood (1-10) | Beta Interest? |
|------------|-------------|------------|-------------------|----------------|
| 1 | | | | |
| 2 | | | | |
| ... | | | | |

#### Task 1.2.3: Synthesize Findings (2 hours)

**Analysis**:

- [ ] What % say they'd pay $49/mo? (Target: 70%+ = 7/10)
- [ ] What's median likelihood score? (Target: ≥7/10)
- [ ] What's #1 feature request?
- [ ] What's #1 concern/objection?

**GO/NO-GO Gate**: If <7/10 "definitely/probably yes" → Willingness-to-pay NOT validated

---

### 1.3 Technical Feasibility (8 hours)

**Objective**: Validate 80% code reuse and 28-hour build timeline

#### Task 1.3.1: Environment Setup (1 hour)

```bash
# Clone SuperCoder
cd ~/Documents/GitHub/SuperCoder/SuperCoder

# Create hackathon branch
git checkout -b hackathon/consultantos

# Install dependencies
pip install -e ".[dev]"
pip install google-genai-adk instructor pydantic

# Test imports
python -c "from orchestrator.core.orchestrator import MultiAgentOrchestrator; print('✓')"
python -c "from orchestrator.research.research_engine import ResearchEngine; print('✓')"
python -c "import instructor; print('✓')"
```

**Deliverables**:

- [ ] SuperCoder running locally
- [ ] All dependencies installed
- [ ] Test imports successful

#### Task 1.3.2: Build Vertical Slice - Porter's 5 Forces (6 hours)

**Goal**: End-to-end Porter's 5 Forces analysis in ≤6 hours (proves 28-hour timeline viable)

```python
# File: consultantos/vertical_slice.py

from pydantic import BaseModel, Field
import instructor
from google import genai

# Data model
class PortersFiveForces(BaseModel):
    supplier_power: float = Field(..., ge=1, le=5)
    buyer_power: float = Field(..., ge=1, le=5)
    competitive_rivalry: float = Field(..., ge=1, le=5)
    threat_of_substitutes: float = Field(..., ge=1, le=5)
    threat_of_new_entrants: float = Field(..., ge=1, le=5)
    overall_intensity: str

# Instructor setup
client = instructor.from_gemini(
    client=genai.GenerativeModel(model="gemini-2.0-flash-exp")
)

# Prompt template
PORTER_PROMPT = """
Analyze {company} using Porter's Five Forces framework.

Research data:
{research_data}

Evaluate each force on 1-5 scale (1=weak, 5=strong):
[Include framework questions]

Provide scores and justifications.
"""

# Execute
async def analyze_porter(company: str):
    # 1. Research (use Tavily from SuperCoder)
    research = await tavily.search(f"{company} competitive analysis")

    # 2. Framework analysis (Instructor + Gemini)
    analysis = client.chat.completions.create(
        model="gemini-2.0-flash-exp",
        response_model=PortersFiveForces,
        messages=[{
            "role": "user",
            "content": PORTER_PROMPT.format(
                company=company,
                research_data=research
            )
        }]
    )

    return analysis

# Test
result = await analyze_porter("Netflix")
print(result)
```

**Timeline Breakdown**:

- Hour 1: Setup Instructor + Pydantic models (30 min) + Test Gemini API (30 min)
- Hour 2: Write Porter prompt template + test with Netflix
- Hour 3: Integrate Tavily from SuperCoder + data flow
- Hour 4: Add validation + error handling
- Hour 5: Generate test report + manual review
- Hour 6: Refine prompts for quality

**Success Criterion**: Working Porter's 5 Forces analysis in ≤6 hours

**GO/NO-GO Gate**: If takes >8 hours → 28-hour timeline is unrealistic

#### Task 1.3.3: Code Reuse Audit (1 hour)

**Map SuperCoder → ConsultantOS reuse**:

| Component           | SuperCoder Path                             | Reuse % | Effort |
| ------------------- | ------------------------------------------- | ------- | ------ |
| Tavily Integration  | `orchestrator/adapters/tavily_adapter.py`   | 100%    | Copy   |
| Gemini Integration  | `orchestrator/adapters/gemini_adapter.py`   | 80%     | Adapt  |
| ChromaDB            | `orchestrator/intelligence/vector_store.py` | 100%    | Copy   |
| Instructor Patterns | (new)                                       | 0%      | Build  |
| Report Templates    | (new)                                       | 0%      | Build  |

**Deliverables**:

- [ ] List of SuperCoder components to reuse (with file paths)
- [ ] Estimated effort for each component (copy/adapt/build)
- [ ] Validated 80% reuse claim

---

### 1.4 Pre-Hackathon Decision Gate

**Decision Matrix**:

| Criterion      | Target     | Actual | Pass? |
| -------------- | ---------- | ------ | ----- |
| Quality Score  | ≥6/10      | \_\_\_ | ⬜    |
| Customer WTP   | 7/10 "yes" | \_\_\_ | ⬜    |
| Vertical Slice | ≤6 hours   | \_\_\_ | ⬜    |

**Decision**:

- ✅ **3/3 Pass → FULL GO** for hackathon
- ⚠️ **2/3 Pass → CAUTIOUS GO** (adjust scope, lower expectations)
- ❌ **0-1/3 Pass → NO-GO** (pivot to different project)

**Adjustment Strategies** (if 2/3 pass):

- Quality low → Reduce framework count (Porter + SWOT only)
- WTP unclear → Lower price to $29, focus on speed over quality
- Timeline risk → Cut PESTEL and Blue Ocean, focus on Porter + SWOT

---

## 2. Day 1: Foundation (8 hours)

**Date**: Friday, November 8, 2025
**Goals**: Google ADK working, data APIs integrated, basic agent coordination

### 2.0 Pre-Hackathon Checklist (BEFORE Day 1) ⚠️ CRITICAL

**Status**: 🔴 MUST COMPLETE BEFORE DAY 1 - Prevents Day 1 delays

**Objective**: Validate all credentials, dependencies, and basic API connectivity to ensure Day 1 focuses on orchestration and integration rather than auth/debugging.

#### Credential Validation (30 minutes)

**Checklist**:

- [ ] **Tavily API Key**: Verify key is valid and test basic search call

  ```bash
  curl -X POST "https://api.tavily.com/search" \
    -H "Content-Type: application/json" \
    -d '{"api_key": "YOUR_KEY", "query": "Tesla", "search_depth": "basic"}'
  ```

  Expected: JSON response with search results

- [ ] **Gemini/Instructor API Key**: Verify Gemini API access and test Instructor integration

  ```python
  import instructor
  from google import genai
  client = instructor.from_gemini(
    client=genai.GenerativeModel(model="gemini-2.0-flash-exp")
  )
  # Test basic structured extraction
  ```

  Expected: No import errors, basic test succeeds

- [ ] **SEC/yfinance Access**: Test basic data retrieval (no API key required)

  ```python
  import yfinance as yf
  stock = yf.Ticker("TSLA")
  print(stock.info['marketCap'])  # Should return number
  ```

  Expected: Market cap data retrieved

- [ ] **Google Trends/pytrends**: Test basic trend query
  ```python
  from pytrends.request import TrendReq
  pytrend = TrendReq()
  pytrend.build_payload(["Tesla"])
  data = pytrend.interest_over_time()
  print(len(data))  # Should return data points
  ```
  Expected: Trend data retrieved (note: rate limit 400/hour)

**Success Criterion**: All 4 credential/data sources validated with successful sample calls

#### Dependency Validation (30 minutes)

**Checklist**:

- [ ] **Python Environment**: Python 3.10+ installed and accessible

  ```bash
  python --version  # Should be 3.10+
  ```

- [ ] **Core Dependencies**: Install and verify imports

  ```bash
  pip install google-genai-adk instructor pydantic edgartools yfinance pytrends finviz pandas_datareader
  python -c "from google.genai import adk; print('✓ ADK')"
  python -c "import instructor; print('✓ Instructor')"
  python -c "import yfinance as yf; print('✓ yfinance')"
  python -c "from pytrends.request import TrendReq; print('✓ pytrends')"
  ```

- [ ] **Google Cloud Setup**: gcloud CLI installed and authenticated (for Cloud Run deployment)
  ```bash
  gcloud --version
  gcloud auth list  # Should show authenticated account
  ```

**Success Criterion**: All dependencies install without errors, basic imports succeed

#### Data API Smoke Tests (30 minutes)

**Parallel Testing** (run all simultaneously):

- [ ] **Tavily**: Search for "Netflix competitive analysis" → Verify 5+ results with URLs
- [ ] **yfinance**: Get Tesla financials → Verify revenue, market cap, P/E ratio
- [ ] **SEC EDGAR**: Get latest 10-K filing for TSLA → Verify filing text retrieved
- [ ] **Google Trends**: Query "electric vehicles" → Verify interest over time data

**Success Criterion**: All 4 APIs return valid data (no errors, reasonable response times)

**Decision Gate**: If any credential/dependency fails → Fix BEFORE Day 1 starts. Do not proceed to Day 1 until all checks pass.

---

### 2.1 Google ADK Setup (4 hours hard limit + 2-hour contingency) ⚠️ CRITICAL PATH

**Status**: 🔴 HIGHEST PRIORITY - Hackathon requirement
**Time Allocation**: Hard 4-hour window for ADK work, with clear 2-hour contingency block reserved for troubleshooting

**Note**: Credential and dependency validation completed in Pre-Hackathon Checklist (Section 2.0), ensuring Day 1 focuses on orchestration and integration.

#### Hour 1-2: Install and Learn ADK

```bash
# Install Google ADK
pip install google-genai-adk

# Test basic functionality
python -c "from google.genai import adk; print('✓')"

# Review examples
git clone https://github.com/google/adk
cd adk/examples
# Study: basic_agent.py, multi_agent.py, tools_example.py
```

**Learning Tasks**:

- [ ] Understand Agent class (name, model, instruction, tools, response_model)
- [ ] Understand Orchestrator class (agents, workflow_type)
- [ ] Test basic agent execution
- [ ] Test tool integration pattern

**Example Test**:

```python
from google.genai import adk

# Create simple agent
agent = adk.Agent(
    name="test_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a helpful assistant."
)

# Test execution
response = agent.execute("What is 2+2?")
print(response)  # Should return "4"
```

#### Hour 3-4: Build 2-Agent Prototype

```python
# File: consultantos/adk_prototype.py

from google.genai import adk

# Agent 1: Research (using validated Tavily from pre-hackathon checklist)
research_agent = adk.Agent(
    name="research_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a business research specialist. Summarize company information.",
    tools=[tavily_search_tool]  # Pre-validated in Section 2.0
)

# Agent 2: Analysis
analysis_agent = adk.Agent(
    name="analysis_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a strategic analyst. Apply Porter's 5 Forces framework.",
    response_model=PortersFiveForces
)

# Orchestrator
orchestrator = adk.Orchestrator(
    agents=[research_agent, analysis_agent],
    workflow_type="sequential"  # Research → Analysis
)

# Execute
result = orchestrator.execute("Analyze Netflix competitive position")
print(result)
```

**Deliverables**:

- [ ] 2 agents (research + analysis) working
- [ ] Sequential coordination (research → analysis)
- [ ] Tool integration (Tavily search - pre-validated)
- [ ] Structured output (Pydantic model)

**Decision Gate** (End of Hour 4):

- ✅ **ADK working** → Continue with ADK, proceed to Section 2.2
- ⚠️ **Partially working** → Use 2-hour contingency block (Hours 5-6) for troubleshooting
- ❌ **Still blocked after Hour 6** → PIVOT to CrewAI fallback (see below)

**Contingency Block (Hours 5-6)**: Reserved for ADK troubleshooting only

- Debug agent execution errors
- Fix tool integration issues
- Resolve orchestrator workflow problems
- If still blocked → Execute CrewAI fallback

**Fallback Trigger**: If ADK not working after 6 total hours → PIVOT immediately

#### Fallback: CrewAI (IF ADK blocked)

```python
# Only if ADK fails after 6 hours
from crewai import Agent, Task, Crew

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

**Trade-off**: Lose ADK bonus points (-0.4), but gain 4 hours of development time

---

### 2.2 Data APIs Integration (1-2 hours)

**Note**: Basic API connectivity validated in Pre-Hackathon Checklist (Section 2.0). This section focuses on integration with ADK agents.

#### Hour 5-6 (or Hour 7-8 if ADK contingency used): Financial Data Integration

```bash
# Install libraries
pip install edgartools yfinance pytrends finviz pandas_datareader

# Test each library
python -c "from edgar import Company; print('✓ edgartools')"
python -c "import yfinance as yf; print('✓ yfinance')"
python -c "from pytrends.request import TrendReq; print('✓ pytrends')"
python -c "from finviz.screener import Screener; print('✓ finviz')"
```

**Test Scripts**:

```python
# File: consultantos/test_data_apis.py

# Test 1: SEC Edgar
from edgar import Company

tesla = Company("TSLA")
filings = tesla.get_filings(form="10-K", count=1)
print(f"✓ SEC Edgar: {len(filings)} filings found")

# Test 2: yfinance
import yfinance as yf

stock = yf.Ticker("TSLA")
print(f"✓ yfinance: Market cap ${stock.info['marketCap']:,}")

# Test 3: Google Trends
from pytrends.request import TrendReq

pytrend = TrendReq()
pytrend.build_payload(["Tesla", "electric vehicles"])
data = pytrend.interest_over_time()
print(f"✓ Google Trends: {len(data)} data points")

# Test 4: finviz
from finviz.screener import Screener

filters = ['exch_nasd']
stock_list = Screener(filters=filters, table='Overview')
print(f"✓ finviz: {len(stock_list)} stocks screened")
```

**Deliverables**:

- [ ] All 4 data APIs working (SEC, yfinance, Trends, finviz)
- [ ] Sample data retrieved for Tesla
- [ ] Error handling for API failures
- [ ] Rate limiting awareness (Trends: 400/hour, SEC: 10/sec)

---

### 2.3 Instructor + Pydantic Setup (1 hour)

**Note**: Instructor/Gemini integration validated in Pre-Hackathon Checklist. This section focuses on agent integration.

#### Hour 7 (or Hour 9 if ADK contingency used): Structured Outputs

```python
# File: consultantos/models.py

from pydantic import BaseModel, Field
from typing import List, Optional
import instructor
from google import genai

# Define data models (copy from design doc)
class CompanyResearch(BaseModel):
    company_name: str
    description: str
    products_services: List[str]
    key_competitors: List[str]
    sources: List[str]

class PortersFiveForces(BaseModel):
    supplier_power: float = Field(..., ge=1, le=5)
    buyer_power: float = Field(..., ge=1, le=5)
    competitive_rivalry: float = Field(..., ge=1, le=5)
    threat_of_substitutes: float = Field(..., ge=1, le=5)
    threat_of_new_entrants: float = Field(..., ge=1, le=5)
    overall_intensity: str

# Patch Gemini with Instructor
client = instructor.from_gemini(
    client=genai.GenerativeModel(model="gemini-2.0-flash-exp")
)

# Test structured extraction
analysis = client.chat.completions.create(
    model="gemini-2.0-flash-exp",
    response_model=PortersFiveForces,
    messages=[{
        "role": "user",
        "content": "Analyze Tesla using Porter's 5 Forces. Score each 1-5."
    }]
)

print(analysis)  # Returns validated PortersFiveForces object
assert 1 <= analysis.supplier_power <= 5  # Validation check
```

**Deliverables**:

- [ ] All Pydantic models defined (from design doc)
- [ ] Instructor patching Gemini client
- [ ] Test structured extraction working
- [ ] Validation errors handled

---

### 2.4 Basic Multi-Agent Flow (1 hour)

#### Hour 8 (or Hour 10 if ADK contingency used): End-to-End Test

```python
# File: consultantos/day1_demo.py

async def day1_demo(company: str):
    """End-to-end test of Day 1 work"""

    # Step 1: Research agent (Tavily)
    research = await research_agent.execute(f"Research {company}")

    # Step 2: Market analyst (Google Trends)
    market = await market_analyst.execute(f"Analyze {company} trends")

    # Step 3: Financial analyst (yfinance + SEC)
    financial = await financial_analyst.execute(f"Analyze {company} financials")

    # Step 4: Framework analyst (Gemini + Instructor)
    frameworks = await framework_analyst.execute({
        "company": company,
        "research": research,
        "market": market,
        "financial": financial
    })

    return {
        "company": company,
        "research": research,
        "market": market,
        "financial": financial,
        "frameworks": frameworks
    }

# Test
result = await day1_demo("Tesla")
print(result['frameworks'].porter_five_forces)
```

**Deliverables**:

- [ ] 4 agents coordinating successfully
- [ ] Data flowing between agents
- [ ] Structured Porter's 5 Forces output
- [ ] Demo working end-to-end

---

### 2.5 Day 1 Exit Criteria

**Checklist**:

- [ ] Pre-hackathon checklist completed (credentials, dependencies validated)
- [ ] Google ADK working (or pivoted to CrewAI after 6-hour limit)
- [ ] All data APIs integrated (SEC, yfinance, Trends - connectivity pre-validated)
- [ ] Structured outputs validated (Instructor + Pydantic - integration pre-validated)
- [ ] 2-4 agents coordinating successfully
- [ ] Porter's 5 Forces analysis generated

**Status Check**:

- ✅ **All criteria met** → On track for Day 2
- ⚠️ **1-2 missing** → Allocate extra time Day 2 morning
- ❌ **3+ missing** → Major timeline risk, reassess scope

**Time Tracking**:

- **Target**: 8 hours total
- **ADK Critical Path**: 4 hours (hard limit) + 2-hour contingency = 6 hours max
- **Buffer**: 2 hours reserved for ADK troubleshooting
- **If ADK works in 4 hours**: Proceed normally, buffer available for other tasks
- **If ADK needs contingency**: Use Hours 5-6, adjust remaining tasks accordingly

---

## 3. Day 2: Multi-Agent System (10 hours)

**Date**: Saturday, November 9, 2025
**Goals**: 5-agent system, all frameworks, high-quality prompts

### 3.1 Full Multi-Agent System (3 hours)

#### Hour 1-3: Build All 5 Agents

```python
# File: consultantos/agents.py

from google.genai import adk
from consultantos.models import *
from consultantos.tools import *

# Agent 1: Research Agent (Tavily)
research_agent = adk.Agent(
    name="research_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a business research specialist with expertise in:
    - Company intelligence gathering
    - Competitive landscape analysis
    - News monitoring and trend identification

    Gather comprehensive information about companies using web search.
    Focus on: company overview, recent news, market position, products/services.
    Cite all sources with URLs.
    """,
    tools=[tavily_search_tool],
    response_model=CompanyResearch
)

# Agent 2: Market Analyst (Google Trends)
market_analyst = adk.Agent(
    name="market_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a market trend analyst.
    Analyze market interest trends using Google Trends data.
    Identify: growth trends, seasonal patterns, regional interest, competitive dynamics.
    """,
    tools=[google_trends_tool],
    response_model=MarketTrends
)

# Agent 3: Financial Analyst (SEC + yfinance)
financial_analyst = adk.Agent(
    name="financial_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a financial analyst with expertise in:
    - Financial statement analysis
    - Valuation metrics interpretation
    - Risk assessment

    Analyze company financial performance using SEC filings and stock data.
    Focus on: revenue growth, profitability, cash flow, valuation metrics.
    """,
    tools=[sec_edgar_tool, yfinance_tool],
    response_model=FinancialSnapshot
)

# Agent 4: Framework Analyst (Business Frameworks)
framework_analyst = adk.Agent(
    name="framework_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a strategic framework expert trained in McKinsey/BCG methodologies.

    Apply rigorous business frameworks:
    - Porter's Five Forces (competitive dynamics)
    - SWOT Analysis (internal/external factors)
    - PESTEL Analysis (macro environment)
    - Blue Ocean Strategy (value innovation)

    Requirements:
    - Evidence-Based: Every claim must cite specific data
    - Quantitative: Use scores, percentages, specific numbers
    - Structured: Follow framework methodology precisely
    - Actionable: Link analysis to strategic implications
    """,
    response_model=FrameworkAnalysis
)

# Agent 5: Synthesis Agent (Cross-Framework Integration)
synthesis_agent = adk.Agent(
    name="synthesis_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a synthesis specialist.
    Combine insights from research, market, financial, and framework analyses.
    Create executive summary with key insights and recommendations.

    Requirements:
    - Integrate across frameworks: Show how insights connect
    - Prioritize: Focus on highest-impact insights
    - Actionable: Recommendations must be implementable
    - Confident: Assess your confidence level (0-1) based on data quality
    """,
    response_model=ExecutiveSummary
)

# Orchestrator (Hybrid workflow: Parallel Phase 1 → Sequential Phase 2)
orchestrator = adk.Orchestrator(
    agents=[
        research_agent,
        market_analyst,
        financial_analyst,
        framework_analyst,
        synthesis_agent
    ],
    workflow_type="hybrid"  # Custom: parallel + sequential
)
```

**Deliverables**:

- [ ] All 5 agents defined with instructions
- [ ] Tools integrated (Tavily, Trends, SEC, yfinance)
- [ ] Response models attached
- [ ] Orchestrator configured

---

### 3.2 Business Framework Prompts (6 hours) ⚠️ CRITICAL FOR QUALITY

**Status**: 🔴 HIGHEST PRIORITY for quality

#### Hour 4-6: Porter's 5 Forces Prompt Engineering

**Goal**: Produce non-generic, evidence-based Porter analysis

**Iteration Plan**: 3 refinement cycles, each 20-30 minutes

- **Cycle 1** (20 min): Initial prompt + test on Netflix
- **Cycle 2** (20 min): Refine based on quality gaps, test on Tesla
- **Cycle 3** (20 min): Final refinement, test on Airbnb
- **Buffer** (30 min): Additional iteration if quality <6/10

**Baseline Template**: Use pre-hackathon Netflix case study (Section 1.1.1) as baseline prompt template to speed convergence. Include validated Netflix analysis as few-shot example.

**Pivot Condition**: If quality <6/10 after 4 hours total (including iterations), execute fallback:

- **Fallback Strategy**: Focus on Porter + SWOT only (reduce scope)
- **Time Reallocation**: Reduce PESTEL and Blue Ocean time to improve Porter/SWOT quality
- **Decision Point**: End of Hour 6, assess quality score

```python
# File: consultantos/prompts/porter_template.py

PORTER_PROMPT = """
Analyze {company_name} in the {industry} industry using Porter's Five Forces framework.

Based on research data:
{research_summary}

Market data:
{market_summary}

Financial data:
{financial_summary}

Evaluate each force on a 1-5 scale (1=weak, 5=strong):

**1. SUPPLIER POWER** (1-5 score)

Analysis Questions:
- How many suppliers does {company_name} depend on?
- Can {company_name} easily switch suppliers?
- What % of costs come from key suppliers?
- Are supplier inputs commoditized or specialized?

Your Task:
- Score (1-5): ___
- Evidence: [Cite specific data from research]
- Industry Comparison: How does this compare to industry average?
- Strategic Implication: What does this mean for {company_name}?

**2. BUYER POWER** (1-5 score)

Analysis Questions:
- How concentrated are {company_name}'s customers?
- Do customers have alternative options?
- What are switching costs for customers?
- Is price a key buying factor?

Your Task:
- Score (1-5): ___
- Evidence: [Cite specific data]
- Industry Comparison: vs industry average
- Strategic Implication: Impact on pricing power?

**3. COMPETITIVE RIVALRY** (1-5 score)

Analysis Questions:
- How many direct competitors?
- Market growth rate (growing markets = less rivalry)?
- Product differentiation level?
- Exit barriers (hard to leave = more rivalry)?

Your Task:
- Score (1-5): ___
- Evidence: [Cite competitor data, market share]
- Industry Comparison: vs average industry
- Strategic Implication: Margin pressure?

**4. THREAT OF SUBSTITUTES** (1-5 score)

Analysis Questions:
- What alternative solutions exist?
- Switching costs for customers to substitutes?
- Performance/price comparison to substitutes?
- Substitute adoption trends?

Your Task:
- Score (1-5): ___
- Evidence: [Cite substitute data]
- Industry Comparison: vs industry average
- Strategic Implication: Disruption risk?

**5. THREAT OF NEW ENTRANTS** (1-5 score)

Analysis Questions:
- Capital requirements to enter industry?
- Regulatory barriers (licenses, approvals)?
- Brand loyalty / network effects?
- Economies of scale advantages?

Your Task:
- Score (1-5): ___
- Evidence: [Cite barrier data]
- Industry Comparison: vs industry average
- Strategic Implication: Market share risk?

**OVERALL COMPETITIVE INTENSITY**
Based on the 5 forces, assess overall intensity:
- Low (average score 1-2.5): Favorable industry structure
- Moderate (average score 2.5-3.5): Mixed competitive dynamics
- High (average score 3.5-5): Intense competition, margin pressure

Average Score: ___
Overall Intensity: [Low/Moderate/High]
Key Insight: [1 sentence summarizing competitive dynamics]

**CRITICAL REQUIREMENTS**:
1. Every score must cite specific evidence (not "moderate competition exists")
2. Use numbers: market share %, growth rates, number of competitors
3. Compare to industry average (is this force stronger/weaker than typical?)
4. Link to strategic implications (so what? why does this matter?)

Example of GOOD analysis:
"Supplier Power: 4/5 (High)
Evidence: Tesla depends on single supplier (TSMC) for AI chips, representing 15% of COGS.
Industry Comparison: Most automakers have 3-5 chip suppliers (lower power).
Implication: Supply chain vulnerability if TSMC has production issues."

Example of BAD analysis:
"Supplier Power: 3/5 (Moderate)
Evidence: Tesla has some supplier concentration.
Implication: Moderate impact."
"""

# Few-shot example (from Netflix case study validation)
PORTER_EXAMPLE = """
[Include your validated Netflix Porter analysis as few-shot example]
"""

# Final prompt
def create_porter_prompt(company: str, industry: str, research: dict, market: dict, financial: dict):
    return PORTER_PROMPT.format(
        company_name=company,
        industry=industry,
        research_summary=summarize(research),
        market_summary=summarize(market),
        financial_summary=summarize(financial)
    ) + "\n\nExample of high-quality analysis:\n" + PORTER_EXAMPLE
```

**Quality Checklist**:

- [ ] Prompt includes specific questions for each force
- [ ] Requires evidence citation (not generic statements)
- [ ] Asks for industry comparison (contextualize scores)
- [ ] Links to strategic implications (so what?)
- [ ] Includes few-shot example (Netflix case study from pre-hackathon validation)

**Explicit Iteration Process** (3 cycles, 20-30 min each):

**Cycle 1** (20 min):

1. Start with baseline template (Netflix case study prompt)
2. Test prompt on Netflix (use pre-hackathon case study for comparison)
3. Manual review: Compare output to pre-hackathon quality (target: ≥6/10)
4. Identify gaps: Generic statements? Missing evidence? Weak scores?

**Cycle 2** (20 min):

1. Refine prompt based on Cycle 1 gaps
2. Test on Tesla (new company, different industry)
3. Manual review: Is output specific? Evidence-based?
4. Compare to Cycle 1: Quality improved?

**Cycle 3** (20 min):

1. Final refinement incorporating Cycle 2 learnings
2. Test on Airbnb (third company for validation)
3. Manual review: Quality ≥6/10?
4. If yes → Proceed. If no → Execute pivot condition (see below)

**Pivot Condition** (triggered if quality <6/10 after 4 hours):

- **Condition**: Quality score <6/10 after 3 iteration cycles + buffer
- **Action**: Reduce scope to Porter + SWOT only
- **Time Reallocation**:
  - Porter: 2 hours (already spent)
  - SWOT: 2 hours (focused effort)
  - PESTEL: Defer to post-hackathon
  - Blue Ocean: Defer to post-hackathon
- **Rationale**: Better to have 2 high-quality frameworks than 4 mediocre ones

**Fallback Quality Target**: If pivoting, aim for Porter + SWOT quality ≥7/10 (higher bar with reduced scope)

#### Hour 7-9: SWOT + PESTEL + Blue Ocean Prompts

**Similar process for each framework**:

```python
# SWOT Prompt Template
SWOT_PROMPT = """
Perform SWOT analysis for {company_name}.

Based on:
- Research: {research_summary}
- Market: {market_summary}
- Financial: {financial_summary}

**STRENGTHS** (Internal, Positive)
Identify 3-5 strengths with SPECIFIC EVIDENCE:

1. [Strength]: [Evidence with numbers]
   Example: "97M US subscribers (40% streaming market share) vs Netflix 75M"
   NOT: "Strong brand presence"

2. [Strength]: [Evidence]
...

**WEAKNESSES** (Internal, Negative)
Identify 3-5 weaknesses with SPECIFIC EVIDENCE:

1. [Weakness]: [Evidence with numbers]
   Example: "$15B debt (3.2x EBITDA) vs industry average 1.8x"
   NOT: "High debt levels"

[Continue for Opportunities and Threats]

**CRITICAL**: Every item must include specific numbers, percentages, or comparisons.
"""

# PESTEL Prompt Template
PESTEL_PROMPT = """
Analyze macro environment for {company_name} using PESTEL framework.

**POLITICAL**: Government policies, regulations, trade
**ECONOMIC**: GDP, inflation, interest rates, consumer spending
**SOCIAL**: Demographics, cultural trends, consumer behavior
**TECHNOLOGICAL**: Innovation, automation, digital transformation
**ENVIRONMENTAL**: Sustainability, climate, resource availability
**LEGAL**: Laws, compliance, intellectual property

For each category, identify 2-3 factors with:
- Factor description
- Impact on {company_name} (Positive/Negative/Neutral)
- Magnitude (Low/Medium/High)
- Evidence/Data
"""

# Blue Ocean Prompt Template
BLUE_OCEAN_PROMPT = """
Apply Blue Ocean Strategy's Four Actions Framework to {company_name}.

Industry: {industry}
Current competitors: {competitors}

**ELIMINATE**: Which industry factors should be eliminated?
(Factors the industry competes on but add no value)

**REDUCE**: Which factors should be reduced below industry standard?
(Over-designed features, unnecessary costs)

**RAISE**: Which factors should be raised above industry standard?
(Differentiation opportunities)

**CREATE**: Which new factors should be created?
(Never offered by industry before)

For each action:
- Specific factor (not generic)
- Rationale (cost savings OR customer value)
- Estimated impact (Low/Medium/High)
- Example: "ELIMINATE: Physical retail stores (Reduce overhead by $50M/year, customers prefer online)"
"""
```

**Deliverables**:

- [ ] High-quality prompt for each framework (Porter, SWOT, PESTEL, Blue Ocean)
- [ ] Few-shot examples included
- [ ] Evidence requirements specified
- [ ] Test outputs reviewed and refined

---

### 3.3 Google Trends Integration (1 hour)

#### Hour 10: Market Analyst Tool

```python
# File: consultantos/tools/google_trends_tool.py

from pytrends.request import TrendReq
import pandas as pd

class GoogleTrendsTool:
    def __init__(self):
        self.pytrend = TrendReq(hl='en-US', tz=360)

    def analyze_trends(self, keywords: List[str], timeframe: str = 'today 12-m'):
        """Analyze market trends for keywords"""

        # Build payload
        self.pytrend.build_payload(keywords, timeframe=timeframe)

        # Interest over time
        interest_data = self.pytrend.interest_over_time()

        # Regional interest
        regional = self.pytrend.interest_by_region()

        # Related queries
        related = self.pytrend.related_queries()

        # Determine trend direction
        if not interest_data.empty:
            recent_avg = interest_data[keywords[0]][-3:].mean()
            earlier_avg = interest_data[keywords[0]][:3].mean()

            if recent_avg > earlier_avg * 1.2:
                trend = "Growing"
            elif recent_avg < earlier_avg * 0.8:
                trend = "Declining"
            else:
                trend = "Stable"
        else:
            trend = "Unknown"

        return {
            "search_interest_trend": trend,
            "interest_data": interest_data.to_dict() if not interest_data.empty else {},
            "regional_interest": regional.to_dict(),
            "related_queries": related,
            "keywords_analyzed": keywords
        }

# Integration with ADK agent
def google_trends_tool(keywords: List[str]):
    """Tool function for ADK agent"""
    tool = GoogleTrendsTool()
    return tool.analyze_trends(keywords)

# Test
result = google_trends_tool(["Tesla", "electric vehicles"])
print(result['search_interest_trend'])  # "Growing" / "Stable" / "Declining"
```

**Deliverables**:

- [ ] Google Trends tool working
- [ ] Market analyst agent integrated
- [ ] Trend direction detection logic
- [ ] Test data retrieved

---

### 3.4 Day 2 Exit Criteria

**Checklist**:

- [ ] All 5 agents working (research, market, financial, framework, synthesis)
- [ ] High-quality prompts for all frameworks (Porter, SWOT, PESTEL, Blue Ocean)
- [ ] Google Trends integration complete
- [ ] Report data structure defined (Pydantic models)
- [ ] End-to-end test produces complete analysis

**Quality Gate**:

- [ ] Manual review of Tesla analysis
- [ ] Quality score ≥6/10 (based on pre-hackathon rubric)
- [ ] All frameworks populated with specific evidence

**Status Check**:

- ✅ **All criteria + quality met** → Excellent, on track for Day 3
- ⚠️ **Criteria met, quality 5-6/10** → Acceptable, refine prompts Day 3 morning
- ❌ **Quality <5/10** → Major quality risk, reassess prompt strategy

---

## 4. Day 3: Reports & Deployment (10 hours)

**Date**: Sunday, November 10, 2025 (DEADLINE DAY)
**Goals**: Professional PDFs, Cloud Run deployment, demo ready

### 4.1 Plotly Visualizations (2 hours)

#### Hour 1-2: Create Charts

```python
# File: consultantos/visualizations/charts.py

import plotly.graph_objects as go
import plotly.express as px

def create_porter_radar(forces: PortersFiveForces) -> str:
    """Generate radar chart for Porter's 5 Forces"""
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
        title="Porter's Five Forces Analysis",
        showlegend=False,
        width=600,
        height=500
    )

    return fig.to_html(include_plotlyjs='cdn', div_id='porter_chart')

def create_swot_matrix(swot: SWOTAnalysis) -> str:
    """Generate 2x2 SWOT matrix"""
    # [Implementation from design doc]
    pass

def create_trend_chart(trend_data: dict) -> str:
    """Generate market interest trend chart"""
    # [Implementation from design doc]
    pass
```

**Deliverables**:

- [ ] Porter's 5 Forces radar chart
- [ ] SWOT 2x2 matrix
- [ ] Market trend line chart
- [ ] All charts render in HTML

---

### 4.2 PDF Generation (2 hours)

#### Hour 3-4: ReportLab Implementation

**Decision**: Use ReportLab (faster, more reliable than Playwright)

```bash
# Install
pip install reportlab

# Test
python -c "from reportlab.pdfgen import canvas; print('✓')"
```

```python
# File: consultantos/reports/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile

async def generate_pdf_report(report: StrategicReport) -> bytes:
    """Generate professional PDF report using ReportLab"""

    # [Implementation from design doc - complete code in design doc]

    # Key sections:
    # 1. Cover page
    # 2. Executive summary
    # 3. Porter's 5 Forces (with table)
    # 4. SWOT matrix
    # 5. PESTEL analysis
    # 6. Blue Ocean strategy
    # 7. Recommendations

    return pdf_bytes
```

**Deliverables**:

- [ ] PDF generator function working
- [ ] All sections included (cover, summary, frameworks)
- [ ] Professional formatting (colors, fonts, spacing)
- [ ] Charts embedded (or table representation)
- [ ] Test PDF generated for Tesla

**Fallback**: If ReportLab too complex, use WeasyPrint (HTML → PDF)

---

### 4.3 Cloud Run Deployment (2 hours)

#### Hour 5-6: Deploy to Cloud Run

```bash
# File: requirements.txt
google-genai-adk
instructor
pydantic
google-generativeai
edgartools
yfinance
pytrends
finviz
pandas_datareader
plotly
reportlab
chromadb
fastapi
uvicorn
slowapi
google-cloud-logging
google-cloud-secret-manager

# File: main.py
# [FastAPI app from design doc]

# Deploy
gcloud run deploy consultantos-bi-engine \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"

# Test deployment
curl https://consultantos-bi-engine-xxx.run.app/health

# Test analysis endpoint
curl -X POST https://consultantos-bi-engine-xxx.run.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "Tesla", "frameworks": ["porter", "swot"]}'
```

**Deliverables**:

- [ ] FastAPI app working locally
- [ ] Deployed to Cloud Run successfully
- [ ] Public URL accessible
- [ ] Health check endpoint responding
- [ ] Analysis endpoint working (30-60 sec response)

---

### 4.4 Caching + Rate Limiting (1 hour)

#### Hour 7: Performance Optimization

```python
# File: consultantos/api/caching.py

from diskcache import Cache
import hashlib

cache = Cache('/tmp/consultantos_cache', size_limit=int(1e9))

def cache_key(company: str, frameworks: List[str]) -> str:
    key_string = f"{company}:{'|'.join(sorted(frameworks))}"
    return hashlib.md5(key_string.encode()).hexdigest()

@cache.memoize(expire=3600)  # 1 hour
async def cached_analysis(key: str, request: AnalysisRequest):
    return await orchestrator.execute(request)

# Rate limiting
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/hour")
async def analyze_company(request: Request, ...):
    pass
```

**Deliverables**:

- [ ] Disk cache working (1-hour TTL)
- [ ] Rate limiting configured (10/hour)
- [ ] Cache hit test (same company twice = instant 2nd response)

---

### 4.5 Demo Preparation (5 hours)

#### Hour 8-9: Pre-Generate Example Reports

**Generate 3 example reports**:

```python
# Generate demo reports
companies = ["Tesla", "Netflix", "Airbnb"]

for company in companies:
    report = await orchestrator.execute(
        AnalysisRequest(company=company)
    )

    pdf = await generate_pdf_report(report)

    # Save locally
    with open(f"demo_reports/{company}_analysis.pdf", "wb") as f:
        f.write(pdf)

    print(f"✓ Generated {company} report")
```

**Deliverables**:

- [ ] 3 high-quality demo reports (Tesla, Netflix, Airbnb)
- [ ] Manual review: Quality ≥6/10 each
- [ ] PDFs formatted professionally
- [ ] Reports uploaded to Cloud Storage (for demo)

#### Hour 9: Create Demo Video (3 minutes max)

**Video Script**:

```
0:00-0:30 - Problem
"Independent consultants need McKinsey-grade strategic analysis,
but can't afford $500K consulting fees or spend 40 hours per engagement."

0:30-1:00 - Solution
"ConsultantOS is a multi-agent AI system that generates business framework
analysis in 30 minutes. 5 specialized agents coordinate via Google ADK."

1:00-2:00 - Live Demo
[Screen recording]
1. Enter "Tesla" in web UI
2. Show agents working (research → market → financial → frameworks → synthesis)
3. Download PDF report
4. Open PDF, scroll through Porter's 5 Forces, SWOT, recommendations

2:00-2:30 - Technical Highlights
"Built on Google Cloud Run with Google ADK orchestration.
5 agents. Gemini Pro models. Auto-scaling. 30-second response time."

2:30-3:00 - Business Case
"$47B business intelligence market. $460K pricing gap.
Target: Independent consultants at $49/month.
Post-hackathon: $150K ARR path validated."

[End with Try It Out URL]
```

**Deliverables**:

- [ ] 3-minute demo video recorded
- [ ] Uploaded to YouTube (unlisted)
- [ ] Video link ready for submission

#### Hour 10: Write Submission Materials

**Project Description** (500 words):

```markdown
# ConsultantOS - Business Intelligence Research Engine

## Problem

Independent strategy consultants face a dilemma: clients expect McKinsey-grade
strategic analysis (Porter's 5 Forces, SWOT, Blue Ocean Strategy), but consultants
can't afford $500K McKinsey fees or spend 40 hours per engagement on framework
application.

## Solution

ConsultantOS is a multi-agent AI system that generates professional business
framework analysis in 30 minutes instead of 40 hours. Five specialized agents
coordinate via Google ADK:

1. **Research Agent**: Gathers company intelligence using Tavily web search
2. **Market Analyst**: Analyzes trends using Google Trends
3. **Financial Analyst**: Processes SEC filings and stock data
4. **Framework Analyst**: Applies Porter's 5 Forces, SWOT, PESTEL, Blue Ocean
5. **Synthesis Agent**: Creates executive summary with recommendations

## Technical Implementation

- **Google ADK**: Multi-agent orchestration (hackathon requirement)
- **Google Gemini Pro**: All 5 agents powered by Gemini (bonus points)
- **Google Cloud Run**: Serverless auto-scaling deployment
- **Structured Outputs**: Instructor + Pydantic for type-safe LLM responses
- **Data Sources**: Tavily, Google Trends, SEC Edgar, yfinance (all open source)
- **Report Generation**: ReportLab for professional PDF outputs

## Architecture Highlights

Hybrid workflow: Parallel Phase 1 (research + market + financial agents run
concurrently) → Sequential Phase 2 (framework analysis depends on Phase 1 data
→ synthesis depends on frameworks).

Caching strategy: 3-level caching (in-memory, disk, semantic vector) for
sub-second repeat queries.

Rate limiting: 10 analyses/hour per user to manage API costs.

## Business Opportunity

- **Market**: $47B business intelligence market growing 10% annually
- **Pricing Gap**: $460K (McKinsey consulting) vs $80/month (ChatGPT) = opportunity
- **Target Customer**: 50,000+ independent consultants (ex-Big 4) in US/UK
- **Pricing**: $49/month (validated with 10 customer interviews)
- **Post-Hackathon Path**: $150K ARR in 12 months (255 paying customers)

## Differentiation

Unlike Perplexity or ChatGPT (generic analysis), ConsultantOS applies rigorous
business frameworks with evidence-based scores. Unlike McKinsey ($500K, 8 weeks),
ConsultantOS delivers in 30 minutes at $49/month.

## Try It Out

[Cloud Run URL]: https://consultantos-bi-engine-xxx.run.app

[Demo Video]: [YouTube link]
[GitHub]: [Repository link]
```

**Deliverables**:

- [ ] Project description written (500 words)
- [ ] Architecture diagram created (visual)
- [ ] Try It Out link tested (Cloud Run URL)
- [ ] GitHub repository public (with README)
- [ ] All submission materials ready

---

### 4.6 Day 3 Exit Criteria

**Submission Checklist**:

- [ ] Cloud Run service deployed and working
- [ ] 3-minute demo video recorded
- [ ] 3 example reports generated (Tesla, Netflix, Airbnb)
- [ ] Project description written
- [ ] Architecture diagram created
- [ ] Public GitHub repository
- [ ] All submission materials uploaded to Devpost

**Hackathon Success Metrics**:

- [ ] 5 agents coordinating successfully
- [ ] Professional PDF reports generated
- [ ] <60 second response time
- [ ] Quality score ≥6/10 (from pre-hackathon validation)

---

## 5. Post-Hackathon Roadmap (12 Months)

### 5.1 Month 1-3: Validation Phase

**Goal**: 10 paying customers @ $49/mo ($490 MRR)

**Week 1-2: Launch Free Beta**

- [ ] Email 50 consultants from pre-hackathon interviews
- [ ] Post on LinkedIn, r/consulting, consultant communities
- [ ] Onboard 50 beta users
- [ ] Track usage: Who uses for real client work?

**Week 3-8: Customer Discovery**

- [ ] Interview 10 beta users weekly
- [ ] Ask: "Did you use this for a real engagement?"
- [ ] Track: Did consultant win the engagement?
- [ ] Refine prompts based on feedback

**Week 9-12: Convert to Paid**

- [ ] End free beta, convert to $49/mo
- [ ] Target: 40% conversion (20 paying customers)
- [ ] Reality check: 50 beta → 20% usage (10) → 50% conversion = 5 paying
- [ ] Adjust as needed

**Milestone**: 1 case study of consultant winning client engagement using tool

---

### 5.2 Month 4-6: Community Phase

**Goal**: 50 paying customers ($2,450 MRR)

**Month 4: Launch Template Library**

- [ ] Consultants can submit their best reports
- [ ] Build shared case study library
- [ ] Network effects begin (R2 reinforcing loop)

**Month 5: Referral Program**

- [ ] Existing customer refers new → 1 month free
- [ ] Target: 2x referrals per customer
- [ ] Activate R1 reinforcing loop (consultant adoption spiral)

**Month 6: Content Marketing**

- [ ] Case study blog posts (consultant testimonials)
- [ ] SEO: "McKinsey frameworks", "strategy consulting tools"
- [ ] LinkedIn thought leadership

**Metrics**: 30% month-over-month growth

---

### 5.3 Month 7-9: Scaling Phase

**Goal**: 150 paying customers ($7,350 MRR)

**Month 7: UK Expansion**

- [ ] Target UK independent consultants
- [ ] Same playbook as US launch

**Month 8: Professional Tier Launch**

- [ ] $149/mo tier (100 reports, all frameworks, priority support)
- [ ] Target: Small consulting teams (2-3 people)

**Month 9: Content Marketing Acceleration**

- [ ] SEO ranking for key terms
- [ ] Partnerships with consulting communities

**Metrics**: 40% month-over-month growth

---

### 5.4 Month 10-12: Premium Phase

**Goal**: 255+ paying customers ($12,500 MRR = $150K ARR)

**Month 10: VC Tier Launch**

- [ ] $199/mo tier for junior VCs / angel investors
- [ ] Use case: Deal memo generation

**Month 11: Annual Plans**

- [ ] $490/year (15% discount vs monthly)
- [ ] Target: 10-15% take annual

**Month 12: Enterprise Consideration**

- [ ] $499/mo tier for boutique consulting firms
- [ ] White-labeling, custom frameworks
- [ ] Evaluate demand before building

**Final Metric**: $201K ARR (34% above $150K target)

---

## 6. Risk Mitigation Strategies

### 6.1 Technical Risks

#### Risk: Google ADK Learning Curve Too Steep

**Probability**: 40%
**Impact**: HIGH (blocks core functionality)
**Mitigation**:

- Allocate 4-6 hours Day 1 (not 2 hours)
- Join Google ADK Discord community
- Review all ADK examples on GitHub
- Have CrewAI code ready as fallback

**Decision Gate**: End of Day 1, Hour 6

- ✅ ADK working → Continue
- ❌ Blocked → Pivot to CrewAI (lose bonus points, gain speed)

#### Risk: LLM Output Quality <60% McKinsey

**Probability**: 50%
**Impact**: HIGH (judges notice, customers reject)
**Mitigation**:

- Iterate on prompts (6 hours allocated Day 2)
- Include few-shot examples (Netflix case study)
- Add quality validation agent (reviews outputs)
- Chain-of-thought prompting for depth

**Decision Gate**: End of Day 2

- ✅ Quality ≥6/10 → Good
- ⚠️ Quality 5-6/10 → Acceptable for hackathon, improve post-launch
- ❌ Quality <5/10 → Position as "AI-powered first draft" (lower expectations)

#### Risk: API Rate Limits Exhausted

**Probability**: 60%
**Impact**: MEDIUM (degraded functionality)
**Mitigation**:

- Aggressive caching (1-hour disk cache)
- Semantic deduplication (ChromaDB similarity check)
- Pre-generate demo reports (avoid live API calls)
- Upgrade to paid API tiers if needed ($20-50 total)

**Fallback**: Use cached demo data for hackathon presentation

---

### 6.2 Business Risks

#### Risk: Consultants Won't Pay $49/mo

**Probability**: 30% (IF customer discovery done)
**Impact**: CRITICAL (no revenue)
**Mitigation**:

- Pre-hackathon: Interview 10 consultants (validate WTP)
- Show ROI calculator (1 client win = 25x annual subscription)
- Offer 30-day free trial (prove value first)

**Fallback Pricing**:

- Test $29/mo (lower friction)
- Test usage-based (pay per report)
- Test annual only ($490/year upfront)

#### Risk: Perplexity Adds Frameworks in 3 Months

**Probability**: 50% (technology is commoditizable)
**Impact**: HIGH (competitive threat)
**Mitigation**:

- Build community moat (template library + consultant network)
- Focus on execution quality (better prompts, better UX)
- First-mover advantage (6-12 month window)

**Long-term Strategy**: Network effects > technology

---

## 7. Success Metrics & Decision Gates

### 7.1 Pre-Hackathon Gate (End of This Week)

**Decision Matrix**:

| Metric        | Target     | Pass Threshold            | Status |
| ------------- | ---------- | ------------------------- | ------ |
| Quality Score | ≥6/10      | 3 ex-consultants average  | ⬜     |
| Customer WTP  | 7/10 "yes" | 70% willing to pay $49/mo | ⬜     |
| Build Time    | ≤6 hours   | Vertical slice working    | ⬜     |

**Decisions**:

- ✅ **3/3 Pass** → FULL GO for hackathon
- ⚠️ **2/3 Pass** → CAUTIOUS GO (adjust scope)
- ❌ **0-1/3 Pass** → NO-GO (pivot to different project)

---

### 7.2 Hackathon Gates

**Day 1 Gate (End of Friday)**:

- [ ] Google ADK working (or CrewAI fallback executed)
- [ ] All data APIs tested (4/4)
- [ ] 2-4 agents coordinating
- [ ] Vertical slice (Porter's 5 Forces) complete

**Day 2 Gate (End of Saturday)**:

- [ ] All 5 agents working
- [ ] All 4 frameworks implemented (Porter, SWOT, PESTEL, Blue Ocean)
- [ ] Quality ≥6/10 on manual review
- [ ] End-to-end test produces full report

**Day 3 Gate (Submission Time)**:

- [ ] Cloud Run deployed and accessible
- [ ] 3 demo reports generated (quality validated)
- [ ] 3-minute demo video uploaded
- [ ] All submission materials complete

---

### 7.3 Post-Hackathon Gates

**Month 3 Gate**:

- [ ] 10 paying customers ($490 MRR)
- [ ] 1 case study: consultant won engagement using tool
- [ ] Quality score ≥7/10 from beta users
- [ ] Decision: Continue or pivot?

**Month 6 Gate**:

- [ ] 50 paying customers ($2,450 MRR)
- [ ] 30% month-over-month growth sustained
- [ ] 2x referrals per customer (network effects)
- [ ] Decision: Raise funding or bootstrap?

**Month 12 Gate**:

- [ ] $150K+ ARR (255+ customers)
- [ ] Profitable unit economics (LTV > 3x CAC)
- [ ] Template library active (community moat)
- [ ] Decision: Scale to $1M ARR or strategic exit?

---

## Summary Timeline

### Pre-Hackathon (Nov 7-8)

- [ ] Quality validation (Netflix case study)
- [ ] Customer discovery (10 consultants)
- [ ] Technical feasibility (vertical slice)

### Day 1 (Nov 8, 8 hours)

- [ ] Google ADK setup (4-6 hours)
- [ ] Data APIs integration (2 hours)
- [ ] Vertical slice complete (Porter's 5 Forces)

### Day 2 (Nov 9, 10 hours)

- [ ] 5-agent system (3 hours)
- [ ] Framework prompts (6 hours)
- [ ] Google Trends integration (1 hour)

### Day 3 (Nov 10, 10 hours)

- [ ] Visualizations (2 hours)
- [ ] PDF generation (2 hours)
- [ ] Cloud Run deployment (2 hours)
- [ ] Caching + rate limiting (1 hour)
- [ ] Demo preparation (3 hours)

### Post-Hackathon (12 months)

- Month 1-3: Validation (10 customers)
- Month 4-6: Community (50 customers)
- Month 7-9: Scaling (150 customers)
- Month 10-12: Premium (255+ customers, $150K ARR)

---

**Document Status**: ✅ Complete
**Last Updated**: November 7, 2025
**Next Action**: Execute Pre-Hackathon Validation (THIS WEEK)
**Owner**: Rish2Jain

---

**END OF IMPLEMENTATION PLAN**
