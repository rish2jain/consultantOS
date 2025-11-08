---
name: google-adk
description: Google Agent Development Kit (ADK) expert for building production-ready multi-agent AI systems with Gemini models, agent coordination, and tool integration
category: skill
---

# Google ADK (Agent Development Kit) Expert

Comprehensive guidance for building multi-agent AI systems using Google's Agent Development Kit with Gemini models.

## Overview

Google ADK is a framework for building and deploying AI agents that can coordinate, use tools, and maintain state across complex workflows. Perfect for Cloud Run hackathon projects requiring multi-agent systems.

## Installation & Setup

```bash
# Install Google ADK
pip install google-adk

# Install Gemini dependencies
pip install google-generativeai

# Set up API key
export GOOGLE_API_KEY="your-api-key-here"
```

## Core Concepts

### 1. Agents

Agents are specialized AI components with specific roles, instructions, and tools.

```python
from google.adk.agents import Agent

# Basic agent
research_agent = Agent(
    name="research_agent",
    model="gemini-2.5-flash",  # Recommended model
    instruction="""
    You are a business research specialist.
    Gather comprehensive information about companies using web search.
    Focus on: company overview, recent news, market position, products/services.
    """,
    tools=[web_search_tool],
    temperature=0.7
)
```

### 2. Tools

Tools give agents capabilities to interact with external systems.

```python
from google.genai.types import Tool, FunctionDeclaration

# Define tool schema
search_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
    ]
)

# Tool implementation
async def execute_search(query: str, max_results: int = 5):
    # Actual implementation
    results = await tavily.search(query, max_results=max_results)
    return results
```

### 3. Orchestrator

Orchestrator coordinates multiple agents and manages workflow execution.

```python
# Sequential workflow (agents run one after another)
orchestrator = adk.Orchestrator(
    agents=[research_agent, analysis_agent, synthesis_agent],
    workflow_type="sequential"
)

# Parallel workflow (agents run simultaneously)
orchestrator = adk.Orchestrator(
    agents=[data_agent_1, data_agent_2, data_agent_3],
    workflow_type="parallel"
)

# Execute workflow
result = await orchestrator.execute({
    "task": "Analyze Tesla's competitive position",
    "industry": "Electric Vehicles"
})
```

## Multi-Agent Patterns

### Pattern 1: Sequential Pipeline

Agents process information in stages, each building on previous results.

```python
# Research → Analysis → Synthesis
research_agent = adk.Agent(
    name="researcher",
    instruction="Gather raw data about the topic"
)

analysis_agent = adk.Agent(
    name="analyzer",
    instruction="Analyze the research data using frameworks"
)

synthesis_agent = adk.Agent(
    name="synthesizer",
    instruction="Create executive summary from analysis"
)

pipeline = adk.Orchestrator(
    agents=[research_agent, analysis_agent, synthesis_agent],
    workflow_type="sequential"
)
```

### Pattern 2: Parallel Execution

Multiple agents work simultaneously on independent tasks.

```python
# Market + Financial + Competitive analysis in parallel
market_agent = adk.Agent(name="market", instruction="Analyze market trends")
financial_agent = adk.Agent(name="financial", instruction="Analyze financials")
competitive_agent = adk.Agent(name="competitive", instruction="Analyze competition")

parallel_system = adk.Orchestrator(
    agents=[market_agent, financial_agent, competitive_agent],
    workflow_type="parallel"
)
```

### Pattern 3: Hierarchical (Supervisor + Workers)

A supervisor agent delegates to specialist agents.

```python
supervisor_agent = adk.Agent(
    name="supervisor",
    instruction="""
    You are a project manager coordinating specialist agents.
    Delegate tasks to: researcher, analyst, writer.
    Review outputs and ensure quality.
    """,
    tools=[delegate_tool]
)

# Workers
researcher = adk.Agent(name="researcher", instruction="Research specialist")
analyst = adk.Agent(name="analyst", instruction="Analysis specialist")
writer = adk.Agent(name="writer", instruction="Writing specialist")

hierarchy = adk.Orchestrator(
    supervisor=supervisor_agent,
    workers=[researcher, analyst, writer]
)
```

## Advanced Features

### State Management

```python
# Agent with stateful memory
stateful_agent = adk.Agent(
    name="stateful_agent",
    instruction="Remember previous interactions",
    memory_type="conversation",  # or "summary", "vector"
    max_memory_tokens=2000
)

# Access state
current_state = agent.get_state()
agent.update_state({"key": "value"})
```

### Error Handling

```python
from google.genai.errors import AgentError, ToolExecutionError

try:
    result = await orchestrator.execute(task)
except ToolExecutionError as e:
    print(f"Tool failed: {e.tool_name} - {e.message}")
    # Retry or fallback
except AgentError as e:
    print(f"Agent failed: {e.agent_name} - {e.message}")
    # Handle agent failure
```

### Streaming Responses

```python
# Stream agent output in real-time
async for chunk in agent.stream(prompt):
    print(chunk.text, end="", flush=True)
```

## Integration with Instructor for Structured Outputs

Combine ADK with Instructor for validated outputs.

```python
import instructor
from pydantic import BaseModel
from google import genai

# Define output schema
class PortersFiveForces(BaseModel):
    supplier_power: float  # 1-5
    buyer_power: float
    competitive_rivalry: float
    threat_of_substitutes: float
    threat_of_new_entrants: float
    analysis: str

# Patch Gemini client
client = instructor.from_gemini(
    client=genai.GenerativeModel(model="gemini-2.5-flash")
)

# Create agent without response_model (not supported by Agent)
from google.adk.agents import Agent
framework_agent = Agent(
    name="framework_analyst",
    model="gemini-2.5-flash",
    instruction="Apply Porter's 5 Forces framework"
)

# Execute agent and validate output post-execution
raw_output = await framework_agent.execute(task)
# Parse and validate using Pydantic model
analysis = PortersFiveForces.model_validate(raw_output)
print(f"Supplier Power: {analysis.supplier_power}/5")
```

## Business Intelligence Multi-Agent System

Complete example for hackathon project:

```python
from google.genai import adk
import instructor
from pydantic import BaseModel

# Data models
class CompanyResearch(BaseModel):
    name: str
    industry: str
    key_facts: list[str]
    competitors: list[str]

class MarketTrends(BaseModel):
    trend_direction: str  # "Growing", "Stable", "Declining"
    interest_score: float
    regional_data: dict

class FinancialSnapshot(BaseModel):
    revenue: float
    growth_rate: float
    market_cap: float
    key_metrics: dict

class PorterAnalysis(BaseModel):
    forces: dict
    overall_intensity: str

class StrategicReport(BaseModel):
    executive_summary: str
    research: CompanyResearch
    market: MarketTrends
    financial: FinancialSnapshot
    porter: PorterAnalysis
    recommendations: list[str]

# Agent 1: Research
research_agent = adk.Agent(
    name="research_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    Research the company thoroughly.
    Gather: company overview, recent news, market position, products.
    Use web search tool to find current information.
    """,
    tools=[web_search_tool],
    response_model=CompanyResearch
)

# Agent 2: Market Analyst
market_agent = adk.Agent(
    name="market_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    Analyze market trends using Google Trends data.
    Identify: trend direction, interest patterns, regional dynamics.
    """,
    tools=[google_trends_tool],
    response_model=MarketTrends
)

# Agent 3: Financial Analyst
financial_agent = adk.Agent(
    name="financial_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    Analyze company financials using SEC filings and stock data.
    Calculate: revenue, growth, margins, valuation metrics.
    """,
    tools=[sec_edgar_tool, yfinance_tool],
    response_model=FinancialSnapshot
)

# Agent 4: Framework Analyst
framework_agent = adk.Agent(
    name="framework_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    Apply Porter's 5 Forces framework to company data.
    Score each force 1-5 with evidence.
    """,
    response_model=PorterAnalysis
)

# Agent 5: Synthesis Agent
synthesis_agent = adk.Agent(
    name="synthesis_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    Synthesize all agent outputs into executive summary.
    Create actionable strategic recommendations.
    """,
    response_model=StrategicReport
)

# Orchestrator
bi_orchestrator = adk.Orchestrator(
    agents=[
        research_agent,
        market_agent,
        financial_agent,
        framework_agent,
        synthesis_agent
    ],
    workflow_type="mixed",  # Parallel data gathering, sequential analysis
    execution_plan={
        "parallel": [research_agent, market_agent, financial_agent],
        "sequential": [framework_agent, synthesis_agent]
    }
)

# Execute
async def analyze_company(company: str, industry: str):
    result = await bi_orchestrator.execute({
        "company": company,
        "industry": industry
    })

    return result  # StrategicReport with all analyses
```

## Cloud Run Deployment

### Dockerfile for ADK

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### FastAPI Integration

```python
from fastapi import FastAPI, BackgroundTasks
from google.genai import adk

app = FastAPI()

# Initialize orchestrator
orchestrator = bi_orchestrator  # from above

@app.post("/analyze")
async def analyze_endpoint(
    company: str,
    industry: str,
    background_tasks: BackgroundTasks
):
    # Execute async
    result = await orchestrator.execute({
        "company": company,
        "industry": industry
    })

    return {"status": "success", "report": result.dict()}

@app.get("/health")
async def health():
    return {"status": "healthy", "agents": len(orchestrator.agents)}
```

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should have one clear purpose
- **Clear Instructions**: Be specific about agent's role and expected outputs
- **Tool Selection**: Only give agents tools they actually need

### 2. Prompt Engineering

```python
# BAD: Vague instruction
instruction = "Analyze the company"

# GOOD: Specific instruction with structure
instruction = """
You are a financial analyst specializing in public companies.

Your task:
1. Gather financial data from SEC filings
2. Calculate key metrics (revenue growth, margins, P/E ratio)
3. Compare to industry benchmarks
4. Identify strengths and weaknesses

Output format:
- Metric: Value (comparison to industry)
- Analysis: 2-3 sentences explaining significance
"""
```

### 3. Error Recovery

```python
# Implement retry logic
async def execute_with_retry(agent, task, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await agent.execute(task)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Cost Optimization

```python
# Use cheaper models for simple tasks
simple_agent = adk.Agent(
    model="gemini-2.0-flash-exp",  # Faster, cheaper
    instruction="Extract key facts"
)

# Use pro models for complex reasoning
complex_agent = adk.Agent(
    model="gemini-pro",  # More capable
    instruction="Apply complex strategic frameworks"
)
```

### 5. Testing

```python
import pytest

@pytest.mark.asyncio
async def test_research_agent():
    agent = research_agent
    result = await agent.execute({
        "company": "Tesla",
        "industry": "Electric Vehicles"
    })

    assert result.name == "Tesla"
    assert len(result.key_facts) > 0
    assert len(result.competitors) > 0
```

## Troubleshooting

### Common Issues

**1. Agent Not Using Tools**

```python
# Ensure tool is properly configured
tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="search",  # Clear name
            description="Search the web for information",  # Detailed description
            parameters={"type": "object", "properties": {...}}
        )
    ]
)

# Make sure agent instruction mentions the tool
instruction = "Use the search tool to find information about..."
```

**2. Inconsistent Outputs**

```python
# Use Pydantic for validation
from pydantic import BaseModel, Field

class ValidatedOutput(BaseModel):
    name: str = Field(..., min_length=1)
    score: float = Field(..., ge=1.0, le=5.0)

agent = adk.Agent(response_model=ValidatedOutput)
```

**3. Performance Issues**

```python
# Implement caching
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_agent_execute(company: str):
    return await agent.execute({"company": company})
```

## Resources

- **Documentation**: https://github.com/google/adk
- **Examples**: https://github.com/google/adk/tree/main/examples
- **Gemini API**: https://ai.google.dev/
- **Community**: Google ADK Discord

## Integration with SuperCoder

ADK agents can be integrated with SuperCoder's orchestration system:

```python
from orchestrator.core.orchestrator import MultiAgentOrchestrator
from google.genai import adk

# Wrap ADK agent as SuperCoder agent
class ADKAgentAdapter:
    def __init__(self, adk_agent):
        self.agent = adk_agent

    async def execute(self, task: str, context: dict) -> dict:
        result = await self.agent.execute(context)
        return {
            "success": True,
            "output": result,
            "confidence": 0.85
        }

# Use in SuperCoder orchestrator
orchestrator = MultiAgentOrchestrator()
orchestrator.add_agent("adk_research", ADKAgentAdapter(research_agent))
```

## Hackathon-Specific Tips

1. **Start Simple**: Begin with 2 agents, expand to 5
2. **Test Early**: Verify ADK setup on Day 1 Hour 1
3. **Fallback Plan**: Have CrewAI ready if ADK blocked
4. **Demo Focus**: Show agent coordination visually
5. **Documentation**: Document agent roles clearly for judges
