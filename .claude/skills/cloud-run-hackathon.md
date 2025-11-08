---
name: cloud-run-hackathon
description: Google Cloud Run Hackathon assistant for building and deploying AI agent applications with Google ADK, focusing on multi-agent coordination, business intelligence, and serverless deployment
category: skill
---

# Cloud Run Hackathon Assistant

Expert guidance for building and submitting applications to the Google Cloud Run Hackathon (run.devpost.com).

## Hackathon Context

**Deadline**: November 10, 2025 at 5:00 PM PST
**Total Prizes**: $50,000 in cash + Google Cloud credits
**Focus**: Serverless applications built with Cloud Run

### Three Categories

1. **AI Studio Category**: Use AI Studio to generate code and deploy
2. **AI Agents Category** ⭐ (Multi-agent apps with Google ADK, minimum 2 agents)
3. **GPU Category**: Use Nvidia L4 GPUs on Cloud Run for ML models

### Judging Criteria

- **Technical Implementation**: 40% (code quality, Cloud Run utilization, scalability)
- **Demo & Presentation**: 40% (problem clarity, solution effectiveness, documentation)
- **Innovation & Creativity**: 20% (originality, problem significance)

### Bonus Points

- Using Google AI models (Gemini, Gemma, Veo)
- Multiple Cloud Run services (front + back end)
- Publishing content about the build (blog, video)
- Social media posts with #CloudRunHackathon

## Project: Business Intelligence Research Engine

### Strategic Positioning

**Market Gap**: $460K pricing gap between AI chatbots ($80/month) and strategic consulting ($500K/project)

**Value Proposition**: Multi-framework strategic analysis in 30 minutes instead of 8 weeks

**Target Users**:
- Independent strategy consultants ($200-500/month WTP)
- VC investors ($500-1K/month WTP)
- MBA students ($20-40/month WTP)
- Strategy directors at mid-market companies
- Product managers needing competitive intelligence

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Web UI / API                          │
│              (FastAPI + Cloud Run Service)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Google ADK (Multi-Agent Orchestrator)          │
│        Coordinates specialized agents, manages state        │
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
                    Final PDF Report
```

## Core Technology Stack

### Must-Have Foundation (12 Core Tools)

| Tool | Purpose | Cost | Already Have? |
|------|---------|------|---------------|
| **Google ADK** | Multi-agent orchestration | FREE | ❌ |
| **Instructor + Pydantic** | Structured LLM outputs | FREE | ❌ |
| **Tavily API** | Web research | FREE tier | ✅ |
| **SEC Edgar API** | Company filings | FREE | ❌ |
| **yfinance** | Financial data | FREE | ❌ |
| **pytrends** | Market trends | FREE | ❌ |
| **ChromaDB** | Vector storage | FREE | ✅ |
| **Playwright** | PDF generation | FREE | ✅ |
| **Plotly** | Visualizations | FREE | ❌ |
| **Cloud Buildpacks** | Deployment | FREE | ❌ |
| **Cloud Tasks** | Async processing | FREE tier | ❌ |
| **slowapi** | Rate limiting | FREE | ❌ |

## Google ADK Integration

### Basic Agent Setup

```python
from google.genai import adk

# Create specialized agent
research_agent = adk.Agent(
    name="research_agent",
    model="gemini-2.0-flash-exp",
    instruction="You are a business research specialist...",
    tools=[tavily_search_tool]
)

# Multi-agent orchestrator
orchestrator = adk.Orchestrator(
    agents=[research_agent, market_analyst, financial_analyst],
    workflow_type="sequential"  # or "parallel"
)

# Execute
result = await orchestrator.execute(task_data)
```

### Agent Specializations

1. **Research Agent** (Tavily): Web search and information gathering
2. **Market Analyst** (Google Trends): Market interest and trend analysis
3. **Financial Analyst** (SEC + yfinance): Company financial analysis
4. **Framework Analyst** (Gemini): Strategic framework application
5. **Synthesis Agent** (Gemini): Cross-agent result aggregation

## Business Frameworks Implementation

### Porter's Five Forces

```python
PORTER_PROMPT = """
Analyze {company_name} using Porter's Five Forces framework.

Evaluate each force on a 1-5 scale (1=weak, 5=strong):

1. **Supplier Power**: Dependencies, switching costs
2. **Buyer Power**: Customer concentration, alternatives
3. **Competitive Rivalry**: Number of competitors, differentiation
4. **Threat of Substitutes**: Alternative solutions, performance
5. **Threat of New Entrants**: Barriers, capital requirements

Provide score, analysis, and evidence for each force.
"""
```

### SWOT Analysis

```python
SWOT_PROMPT = """
Perform SWOT analysis for {company_name}.

**Strengths** (Internal, positive): Unique capabilities, advantages
**Weaknesses** (Internal, negative): Limitations, areas to improve
**Opportunities** (External, positive): Market trends, expansion
**Threats** (External, negative): Competition, risks

Provide 3-5 items per quadrant with evidence.
"""
```

### Blue Ocean Strategy

```python
BLUE_OCEAN_PROMPT = """
Apply Blue Ocean Strategy's Four Actions Framework:

**Eliminate**: Factors to eliminate
**Reduce**: Factors to reduce below industry standard
**Raise**: Factors to raise above industry standard
**Create**: Factors to create that industry never offered

Identify specific factors with rationale and impact.
"""
```

## Cloud Run Deployment

### Deployment Command

```bash
gcloud run deploy bi-research-engine \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars TAVILY_API_KEY=${TAVILY_API_KEY}
```

### FastAPI Application

```python
from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI(title="Business Intelligence Research Engine")
limiter = Limiter(key_func=get_remote_address)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_company(request: Request, company: str):
    # Execute multi-agent analysis
    result = await orchestrator.execute({"company": company})

    # Generate report
    pdf_bytes = await generate_report(result)

    return {"status": "success", "report_url": report_url}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Report Generation Pipeline

### Plotly Visualizations

```python
import plotly.graph_objects as go

def create_porter_radar(forces):
    fig = go.Figure(data=go.Scatterpolar(
        r=[forces.supplier_power, forces.buyer_power,
           forces.competitive_rivalry, forces.threat_of_substitutes,
           forces.threat_of_new_entrants],
        theta=['Supplier Power', 'Buyer Power', 'Competitive Rivalry',
               'Threat of Substitutes', 'New Entrants'],
        fill='toself'
    ))
    return fig.to_html(include_plotlyjs='cdn')
```

### PDF Generation with Playwright

```python
from playwright.async_api import async_playwright

async def generate_pdf_report(html_content: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)

        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "1cm", "right": "1cm", "bottom": "1cm", "left": "1cm"}
        )

        await browser.close()
        return pdf_bytes
```

## 3-Day Implementation Timeline

### Day 1: Foundation (8 hours) - Friday, Nov 8

- **Hour 1-2**: Google ADK setup and basic agent testing ⚠️ CRITICAL
- **Hour 3-4**: Data APIs integration (SEC, yfinance, pytrends)
- **Hour 5-6**: Instructor + Pydantic structured outputs
- **Hour 7-8**: Basic 2-agent coordination test

### Day 2: Multi-Agent Analysis (10 hours) - Saturday, Nov 9

- **Hour 1-3**: Full 5-agent system with ADK
- **Hour 4-6**: Business framework prompt engineering ⚠️ CRITICAL
- **Hour 7-8**: Google Trends integration
- **Hour 9-10**: Report data structure

### Day 3: Reports + Deployment (10 hours) - Sunday, Nov 10

- **Hour 1-2**: Plotly visualizations
- **Hour 3-4**: HTML templates + PDF generation
- **Hour 5-6**: Cloud Run deployment
- **Hour 7-8**: Caching + rate limiting
- **Hour 9-10**: Demo preparation and submission

## Critical Success Factors

### Technical Requirements

✅ Multi-agent system demonstrating coordination
✅ Real business frameworks applied (Porter, SWOT)
✅ Professional PDF reports generated
✅ Deployed to Cloud Run (public URL)
✅ 5-minute demo video recorded

### Risk Mitigation

1. **ADK Learning Curve**: Allocate 4-6 hours, fallback to CrewAI if blocked
2. **LLM Quality**: Iterate on prompts, use few-shot examples
3. **API Rate Limits**: Aggressive caching, rate limiting users

### Demo Strategy

**5-Minute Pitch Structure**:
1. Hook (30s): $500K vs 30 minutes problem
2. Problem (30s): $460K market gap
3. Solution (1min): 5-agent architecture
4. Live Demo (2min): Tesla/Rivian analysis
5. Business Case (30s): Market size, pricing
6. Close (30s): Cloud Run showcase

## Submission Checklist

- [ ] 3-minute demo video (upload to YouTube)
- [ ] GitHub repository (public)
- [ ] README with architecture diagram
- [ ] Try It Out link (Cloud Run URL)
- [ ] Architecture diagram (image file)
- [ ] Project description (500 words)
- [ ] Blog post about building (bonus points)
- [ ] Social media post with #CloudRunHackathon

## Usage Guidelines

When using this skill, Claude will:

1. **Prioritize hackathon requirements**: Focus on ADK, Cloud Run, and judging criteria
2. **Apply business frameworks**: Use Porter, SWOT, Blue Ocean for strategic analysis
3. **Optimize for timeline**: 3-day sprint with clear priorities
4. **Mitigate risks**: Identify blockers early, have fallback plans
5. **Focus on demo**: Everything should support compelling 5-minute pitch

## Integration with SuperCoder

This project leverages SuperCoder's existing infrastructure:
- **Multi-agent orchestration**: 80% code reuse
- **Tavily integration**: Already working
- **ChromaDB**: Vector storage ready
- **Playwright**: Familiar from testing
- **Research engine**: Deep research capabilities

Total code reuse: ~80% from SuperCoder foundation

## Post-Hackathon Path

**Phase 1**: MVP (3 days) - Win hackathon
**Phase 2**: Beta (2-4 weeks) - 10-20 users
**Phase 3**: Launch (2-3 months) - $10K MRR
**Phase 4**: Scale (6-12 months) - $100K+ MRR

Target: $150K ARR in 12 months with validated user personas
