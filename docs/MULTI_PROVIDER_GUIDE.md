

# Multi-Provider LLM System Guide

ConsultantOS now supports multiple LLM providers with intelligent routing, automatic fallback, and cost optimization.

## Table of Contents

- [Overview](#overview)
- [Supported Providers](#supported-providers)
- [Configuration](#configuration)
- [Routing Strategies](#routing-strategies)
- [Cost Management](#cost-management)
- [Monitoring & Health](#monitoring--health)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)

## Overview

The multi-provider system provides:

- **Resilience**: Automatic fallback when providers fail
- **Cost Optimization**: Route requests to cheapest available provider
- **Capability Matching**: Route based on task requirements
- **Load Balancing**: Distribute load across providers
- **Cost Tracking**: Monitor spending by provider, agent, and user
- **Health Monitoring**: Track provider availability and performance

## Supported Providers

### Google Gemini (Default)

**Strengths**: Speed, cost-effectiveness, general-purpose analysis

**Best For**: High-volume requests, quick analysis, cost optimization

**Pricing**: ~$0.0007 per 1K tokens (blended)

**Configuration**:
```bash
GEMINI_API_KEY=your-gemini-key
```

### OpenAI GPT-4

**Strengths**: Complex analytical tasks, multi-step reasoning, accuracy

**Best For**: Deep analysis, strategic planning, complex reasoning

**Pricing**: ~$0.02 per 1K tokens (blended)

**Configuration**:
```bash
OPENAI_API_KEY=your-openai-key
```

### Anthropic Claude

**Strengths**: Creative writing, synthesis, nuanced analysis, long context

**Best For**: Executive summaries, creative content, synthesis

**Pricing**: ~$0.045 per 1K tokens (blended)

**Configuration**:
```bash
ANTHROPIC_API_KEY=your-anthropic-key
```

## Configuration

### Environment Variables

**Required**:
```bash
# Primary provider (at least one required)
GEMINI_API_KEY=your-gemini-key
```

**Optional**:
```bash
# Additional providers (for fallback/routing)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Provider Configuration
PRIMARY_LLM_PROVIDER=gemini  # Primary provider: gemini, openai, anthropic
ENABLE_LLM_FALLBACK=true     # Enable automatic fallback on failure
LLM_ROUTING_STRATEGY=fallback  # Routing strategy (see below)

# Cost Management
LLM_DAILY_BUDGET=10.0        # Daily budget in USD (optional)
LLM_MONTHLY_BUDGET=200.0     # Monthly budget in USD (optional)
```

### Configuration via API

Get current configuration:
```bash
GET /providers/configuration
```

Response:
```json
{
  "available_providers": ["gemini", "openai", "anthropic"],
  "primary_provider": "gemini",
  "enable_fallback": true,
  "routing_strategy": "fallback",
  "fallback_order": ["openai", "anthropic"],
  "budgets": {
    "daily": 10.0,
    "monthly": 200.0
  }
}
```

## Routing Strategies

### 1. Fallback (Default)

**Strategy**: Use primary provider, fallback to backups on failure

**Best For**: Maximum reliability with preferred provider

**Configuration**:
```bash
LLM_ROUTING_STRATEGY=fallback
PRIMARY_LLM_PROVIDER=gemini
```

**Behavior**:
1. Try primary provider (Gemini)
2. If fails → try first fallback (OpenAI)
3. If fails → try second fallback (Anthropic)
4. If all fail → raise exception

**Example**:
```python
# Automatically uses fallback strategy
result = await agent.generate_structured(
    prompt="Analyze Tesla",
    response_model=AnalysisResult
)
```

### 2. Cost-Based Routing

**Strategy**: Route to cheapest available provider

**Best For**: Cost optimization, high-volume workloads

**Configuration**:
```bash
LLM_ROUTING_STRATEGY=cost
```

**Behavior**:
- Calculates cost per provider
- Routes to cheapest healthy provider
- Fallback if cheapest fails

**Cost Ranking** (cheapest to most expensive):
1. Gemini: $0.0007/1K tokens
2. OpenAI: $0.02/1K tokens
3. Anthropic: $0.045/1K tokens

**Example**:
```python
# Automatically routes to cheapest provider
result = await agent.generate_structured(
    prompt="Analyze Tesla",
    response_model=AnalysisResult
)
# Will use Gemini (cheapest)
```

### 3. Capability-Based Routing

**Strategy**: Route based on task requirements

**Best For**: Optimizing quality for specific task types

**Configuration**:
```bash
LLM_ROUTING_STRATEGY=capability
```

**Task Type Mapping**:
- `creative` → Anthropic (Claude for creative writing)
- `synthesis` → Anthropic (Claude for executive summaries)
- `analytical` → OpenAI (GPT-4 for deep analysis)
- `reasoning` → OpenAI (GPT-4 for complex reasoning)
- `speed` → Gemini (Fast responses)
- `cost_effective` → Gemini (High volume)
- `general` → Gemini (Default)

**Agent Configuration**:
```python
# Research agent uses analytical routing
research_agent = ResearchAgent(
    name="research",
    task_type="analytical"  # Routes to OpenAI
)

# Synthesis agent uses creative routing
synthesis_agent = SynthesisAgent(
    name="synthesis",
    task_type="synthesis"  # Routes to Anthropic
)
```

**Example**:
```python
# Agent task type determines routing
# Research agent → OpenAI (analytical)
research_result = await research_agent.execute(data)

# Synthesis agent → Anthropic (creative)
summary_result = await synthesis_agent.execute(data)
```

### 4. Load Balancing

**Strategy**: Distribute load across healthy providers

**Best For**: High traffic, distributed workloads

**Configuration**:
```bash
LLM_ROUTING_STRATEGY=load_balance
```

**Behavior**:
- Tracks request count per provider
- Routes to provider with fewest requests
- Balances load across all providers

**Example**:
```python
# Requests distributed across providers
for i in range(10):
    result = await agent.generate_structured(
        prompt=f"Analyze company {i}",
        response_model=AnalysisResult
    )
# Requests spread across gemini, openai, anthropic
```

## Cost Management

### Setting Budgets

**Via Environment Variables**:
```bash
LLM_DAILY_BUDGET=10.0
LLM_MONTHLY_BUDGET=200.0
```

**Via Code**:
```python
from consultantos.llm.cost_tracker import cost_tracker

cost_tracker.set_daily_budget(10.0)  # $10/day
cost_tracker.set_monthly_budget(200.0)  # $200/month
```

### Budget Alerts

System automatically logs warnings when:
- Budget reaches 90% → Warning logged
- Budget exceeded → Error logged

**Check Current Spending**:
```bash
GET /providers/costs/summary
```

Response:
```json
{
  "daily_cost": 2.45,
  "monthly_cost": 48.30,
  "by_provider": {
    "gemini": 32.10,
    "openai": 14.20,
    "anthropic": 2.00
  },
  "by_agent": {
    "research": 20.50,
    "framework": 15.80,
    "synthesis": 12.00
  },
  "total_tokens": 156000,
  "total_requests": 342
}
```

### Cost Tracking

**Track by Provider**:
```bash
GET /providers/costs/stats
```

**Export Usage Report**:
```bash
GET /providers/costs/export?start_date=2024-01-01&end_date=2024-01-31
```

Response:
```json
{
  "period": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-01-31T23:59:59"
  },
  "summary": {
    "total_cost": 245.80,
    "total_tokens": 1250000,
    "total_requests": 2340,
    "average_cost_per_request": 0.105
  },
  "by_provider": {
    "gemini": 150.30,
    "openai": 85.50,
    "anthropic": 10.00
  },
  "by_user": {
    "user_1": 120.40,
    "user_2": 95.20,
    "user_3": 30.20
  }
}
```

## Monitoring & Health

### Provider Health Status

**Check Provider Health**:
```bash
GET /providers/health
```

Response:
```json
{
  "gemini": {
    "provider": "gemini",
    "is_healthy": true,
    "total_requests": 450,
    "failed_requests": 2,
    "failure_rate": 0.0044,
    "consecutive_failures": 0,
    "tokens_used": 125000,
    "estimated_cost": 87.50,
    "capabilities": {
      "strengths": ["speed", "cost_effective", "general_purpose"],
      "best_for": ["high_volume", "quick_analysis"],
      "max_context": 1048576
    }
  },
  "openai": {
    "provider": "openai",
    "is_healthy": true,
    "total_requests": 120,
    "failed_requests": 0,
    "failure_rate": 0.0,
    "consecutive_failures": 0,
    "tokens_used": 35000,
    "estimated_cost": 70.00,
    "capabilities": {
      "strengths": ["analytical", "reasoning", "complex_tasks"],
      "best_for": ["deep_analysis", "multi_step_reasoning"],
      "max_context": 128000
    }
  }
}
```

### Health Criteria

**Healthy Provider**:
- `is_healthy: true`
- `consecutive_failures < 3`
- Available for requests

**Unhealthy Provider**:
- `is_healthy: false`
- `consecutive_failures >= 3`
- Skipped for 5-minute cooldown
- Automatically retried after cooldown

**Reset Provider Health**:
```bash
POST /providers/health/gemini/reset
```

### Failure Handling

**Automatic Recovery**:
1. Provider fails → marked unhealthy after 3 consecutive failures
2. Skipped for 5-minute cooldown
3. Automatically retried after cooldown
4. Health reset on successful request

**Manual Recovery**:
```bash
# Reset provider health manually
POST /providers/health/{provider_name}/reset
```

## API Reference

### Provider Endpoints

#### GET /providers/health
Get health status for all providers.

**Response**: `Dict[str, ProviderHealthResponse]`

#### POST /providers/health/{provider_name}/reset
Reset health status for specific provider.

**Parameters**:
- `provider_name`: Provider to reset (gemini, openai, anthropic)

**Response**: Success message

#### GET /providers/costs/summary
Get cost summary (daily, monthly, by provider, by agent).

**Response**: `CostSummaryResponse`

#### GET /providers/costs/stats
Get detailed usage statistics.

**Query Parameters**:
- `start_date`: Optional start date (ISO format)
- `end_date`: Optional end date (ISO format)

**Response**: `UsageStatsResponse`

#### GET /providers/costs/export
Export comprehensive usage report.

**Query Parameters**:
- `start_date`: Optional start date
- `end_date`: Optional end date

**Response**: Detailed JSON report

#### GET /providers/configuration
Get current provider configuration.

**Response**: Configuration details

## Best Practices

### 1. Start with Fallback Strategy

```bash
PRIMARY_LLM_PROVIDER=gemini
ENABLE_LLM_FALLBACK=true
LLM_ROUTING_STRATEGY=fallback
```

**Why**: Maximum reliability while using preferred provider

### 2. Configure Multiple Providers

```bash
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

**Why**: Enables automatic failover and routing options

### 3. Set Cost Budgets

```bash
LLM_DAILY_BUDGET=10.0
LLM_MONTHLY_BUDGET=200.0
```

**Why**: Prevents unexpected spending, gets alerts at 90%

### 4. Use Capability Routing for Quality

**Framework Agent** (analytical):
```python
framework_agent = FrameworkAgent(
    name="framework",
    task_type="analytical"  # Routes to OpenAI
)
```

**Synthesis Agent** (creative):
```python
synthesis_agent = SynthesisAgent(
    name="synthesis",
    task_type="synthesis"  # Routes to Anthropic
)
```

**Why**: Matches provider strengths to task requirements

### 5. Use Cost Routing for High Volume

```bash
LLM_ROUTING_STRATEGY=cost
```

**Why**: Minimizes costs for large-scale operations

### 6. Monitor Health Regularly

```bash
# Check provider health
curl http://localhost:8080/providers/health

# Check costs
curl http://localhost:8080/providers/costs/summary
```

**Why**: Early detection of issues and cost overruns

### 7. Export Usage Reports

```bash
# Monthly report
curl "http://localhost:8080/providers/costs/export?start_date=2024-01-01&end_date=2024-01-31"
```

**Why**: Track spending trends, optimize usage

## Migration from Single Provider

### Before (Gemini Only)

```python
# Old BaseAgent (Gemini only)
class BaseAgent:
    def __init__(self, name, model="gemini-2.0-flash-exp"):
        self.client = genai.GenerativeModel(model)
        self.structured_client = instructor.from_gemini(self.client)
```

### After (Multi-Provider)

```python
# New BaseAgent (Multi-provider)
class BaseAgent:
    def __init__(self, name, task_type="analytical"):
        # Provider manager handles all providers
        self.llm = BaseAgent._provider_manager

    async def generate_structured(self, prompt, response_model):
        # Automatically uses configured routing strategy
        return await self.llm.generate(
            prompt, response_model
        )
```

### Migration Steps

1. **Add API Keys** (`.env`):
   ```bash
   OPENAI_API_KEY=your-key  # Optional
   ANTHROPIC_API_KEY=your-key  # Optional
   ```

2. **Configure Strategy** (`.env`):
   ```bash
   LLM_ROUTING_STRATEGY=fallback  # Start with fallback
   ```

3. **No Code Changes Required**:
   - Agents automatically use new system
   - Existing code continues working

4. **Monitor Performance**:
   ```bash
   GET /providers/health
   GET /providers/costs/summary
   ```

5. **Optimize Routing** (optional):
   ```bash
   # Try cost-based routing
   LLM_ROUTING_STRATEGY=cost

   # Or capability-based
   LLM_ROUTING_STRATEGY=capability
   ```

## Troubleshooting

### Provider Keeps Failing

**Check Health**:
```bash
GET /providers/health
```

**Reset Health**:
```bash
POST /providers/health/gemini/reset
```

**Verify API Key**:
```bash
# Check environment variable
echo $GEMINI_API_KEY
```

### High Costs

**Check Spending**:
```bash
GET /providers/costs/summary
```

**Set Budget**:
```bash
LLM_DAILY_BUDGET=10.0
```

**Switch to Cost Routing**:
```bash
LLM_ROUTING_STRATEGY=cost
```

### All Providers Failing

**Check Configuration**:
```bash
GET /providers/configuration
```

**Verify API Keys**:
```bash
# All providers
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

**Check Logs**:
```bash
# Look for provider errors
grep "provider.*failed" logs/app.log
```

## Advanced Usage

### Custom Routing Logic

```python
# Override routing for specific request
result = await provider_manager.route_by_capability(
    task_type="creative",
    prompt="Write executive summary",
    response_model=Summary
)
```

### Per-Request Provider Selection

```python
# Force specific provider
result = await provider_manager.providers["anthropic"].generate(
    prompt="Creative task",
    response_model=Response
)
```

### Cost Tracking Per User

```python
await cost_tracker.track_usage(
    provider="gemini",
    model="gemini-1.5-pro",
    tokens_used=1000,
    cost_per_1k_tokens=0.001,
    user_id="user_123",  # Track by user
    analysis_id="analysis_456"
)

# Get user costs
user_costs = await cost_tracker.get_cost_by_user()
```

## Summary

The multi-provider system provides:

✅ **Resilience**: Automatic fallback on provider failure
✅ **Cost Optimization**: Route to cheapest provider
✅ **Quality Optimization**: Match provider to task type
✅ **Load Distribution**: Balance across providers
✅ **Cost Tracking**: Monitor spending comprehensively
✅ **Health Monitoring**: Track provider availability

**Recommended Setup**:
```bash
# Primary provider
GEMINI_API_KEY=your-key

# Fallback providers
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Configuration
PRIMARY_LLM_PROVIDER=gemini
ENABLE_LLM_FALLBACK=true
LLM_ROUTING_STRATEGY=fallback

# Budgets
LLM_DAILY_BUDGET=10.0
LLM_MONTHLY_BUDGET=200.0
```

For questions or issues, see API documentation at `/docs` or contact support.
