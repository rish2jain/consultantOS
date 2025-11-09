# Multi-Provider LLM Quick Reference

## Environment Variables

```bash
# Required (at least one)
GEMINI_API_KEY=your-key

# Optional (for fallback/routing)
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Configuration
PRIMARY_LLM_PROVIDER=gemini          # gemini | openai | anthropic
ENABLE_LLM_FALLBACK=true             # true | false
LLM_ROUTING_STRATEGY=fallback        # fallback | cost | capability | load_balance

# Budget Limits (optional)
LLM_DAILY_BUDGET=10.0               # USD per day
LLM_MONTHLY_BUDGET=200.0            # USD per month
```

## Routing Strategies

| Strategy | Use Case | Behavior |
|----------|----------|----------|
| `fallback` | Maximum reliability | Primary → fallback on failure |
| `cost` | Cost optimization | Route to cheapest provider |
| `capability` | Quality optimization | Match task to provider strength |
| `load_balance` | High traffic | Distribute across providers |

## Provider Characteristics

| Provider | Cost/1K | Strengths | Best For |
|----------|---------|-----------|----------|
| Gemini | $0.0007 | Speed, cost | High volume, quick analysis |
| OpenAI | $0.02 | Analytical, reasoning | Deep analysis, complex tasks |
| Anthropic | $0.045 | Creative, synthesis | Summaries, creative content |

## API Endpoints

```bash
# Health Status
GET /providers/health

# Cost Summary
GET /providers/costs/summary

# Detailed Stats
GET /providers/costs/stats?start_date=2024-01-01

# Export Report
GET /providers/costs/export

# Configuration
GET /providers/configuration

# Reset Provider Health
POST /providers/health/{provider}/reset
```

## Code Examples

### Using in Agents

```python
# Agents automatically use configured strategy
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            task_type="analytical"  # For capability routing
        )

    async def analyze(self, data):
        result = await self.generate_structured(
            prompt=f"Analyze {data}",
            response_model=AnalysisResult
        )
        return result
```

### Manual Provider Selection

```python
# Override routing for specific request
from consultantos.agents.base_agent import BaseAgent

pm = BaseAgent._provider_manager

# Force specific provider
result = await pm.providers["anthropic"].generate(
    prompt="Creative task",
    response_model=Response
)

# Use capability routing
result = await pm.route_by_capability(
    task_type="creative",
    prompt="Write summary",
    response_model=Summary
)
```

### Cost Tracking

```python
from consultantos.llm.cost_tracker import cost_tracker

# Set budgets
cost_tracker.set_daily_budget(10.0)
cost_tracker.set_monthly_budget(200.0)

# Get current costs
daily = await cost_tracker.get_daily_cost()
monthly = await cost_tracker.get_monthly_cost()

# Breakdown by provider
by_provider = await cost_tracker.get_cost_by_provider()
```

## Health Monitoring

```bash
# Check status
curl http://localhost:8080/providers/health

# Example response
{
  "gemini": {
    "is_healthy": true,
    "total_requests": 450,
    "failure_rate": 0.004,
    "tokens_used": 125000,
    "estimated_cost": 87.50
  }
}
```

## Troubleshooting

### Provider Failing
```bash
# Check health
curl http://localhost:8080/providers/health

# Reset if needed
curl -X POST http://localhost:8080/providers/health/gemini/reset
```

### High Costs
```bash
# Check spending
curl http://localhost:8080/providers/costs/summary

# Switch to cost routing
export LLM_ROUTING_STRATEGY=cost
```

### All Providers Down
```bash
# Verify API keys
echo $GEMINI_API_KEY
echo $OPENAI_API_KEY

# Check logs
grep "provider.*failed" logs/app.log
```

## Best Practices

1. **Start with Fallback**: Most reliable, uses preferred provider
2. **Add Multiple Providers**: Enable automatic failover
3. **Set Budgets**: Prevent unexpected costs
4. **Monitor Health**: Check `/providers/health` regularly
5. **Use Capability Routing**: Match tasks to provider strengths
6. **Export Reports**: Monthly cost analysis

## Migration Checklist

- [ ] Add OpenAI and Anthropic API keys
- [ ] Set `LLM_ROUTING_STRATEGY=fallback`
- [ ] Configure daily/monthly budgets
- [ ] Test with `GET /providers/health`
- [ ] Monitor costs with `GET /providers/costs/summary`
- [ ] Optimize routing strategy based on usage

## Quick Start

```bash
# 1. Add API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Configure
export LLM_ROUTING_STRATEGY=fallback
export LLM_DAILY_BUDGET=10.0

# 3. Start server
python main.py

# 4. Check health
curl http://localhost:8080/providers/health

# 5. Monitor costs
curl http://localhost:8080/providers/costs/summary
```

## Support

- **Full Guide**: `docs/MULTI_PROVIDER_GUIDE.md`
- **API Docs**: `http://localhost:8080/docs`
- **Implementation**: `MULTI_PROVIDER_IMPLEMENTATION.md`
