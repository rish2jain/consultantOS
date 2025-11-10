# Wargaming Simulator - Quick Start Guide

## Overview

The Wargaming Simulator provides Monte Carlo-based competitive scenario analysis with:
- **Probabilistic modeling** of uncertain competitive variables
- **Sensitivity analysis** to identify key drivers
- **AI-powered insights** for strategic recommendations
- **Interactive visualizations** for decision support

---

## API Endpoints

### Base URL
```
/wargaming
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/scenarios` | Create custom scenario |
| GET | `/scenarios` | List all scenarios |
| POST | `/scenarios/templates/{name}` | Create from template |
| POST | `/simulate` | Run Monte Carlo simulation |
| POST | `/compare` | Compare multiple scenarios |
| GET | `/visualizations/distribution/{id}` | Get histogram chart |
| GET | `/visualizations/tornado/{id}` | Get sensitivity chart |

---

## Quick Examples

### 1. Create Price War Scenario

```bash
curl -X POST "http://localhost:8080/wargaming/scenarios/templates/price_war" \
  -H "Content-Type: application/json" \
  -d '{
    "our_market_share": 0.25,
    "competitor_name": "AggressiveCorp"
  }'
```

**Templates Available:**
- `price_war` - Competitive pricing scenario
- `new_entrant` - Market disruption scenario
- `product_launch` - New product introduction
- `market_expansion` - Geographic expansion

### 2. Run Simulation

```bash
curl -X POST "http://localhost:8080/wargaming/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_id": "scenario_abc123",
    "num_iterations": 10000,
    "include_sensitivity": true
  }'
```

**Key Result Fields:**
- `expected_value` - Mean outcome
- `win_probability` - Probability of success
- `var_95` - Worst-case 5th percentile
- `sensitivity.rank_order` - Key drivers ranked

### 3. Custom Scenario

```python
from consultantos.models.wargaming import Distribution, WargameScenario

scenario = WargameScenario(
    name="Custom Analysis",
    description="Revenue impact of market conditions",
    variables={
        "market_growth": Distribution(
            type="normal",
            params={"mean": 0.15, "std": 0.05}
        ),
        "market_share": Distribution(
            type="triangular",
            params={"min": 0.20, "mode": 0.30, "max": 0.40}
        ),
        "base_revenue": Distribution(
            type="normal",
            params={"mean": 50_000_000, "std": 5_000_000}
        )
    },
    formula="base_revenue * (1 + market_growth) * market_share"
)
```

---

## Python SDK Usage

### Basic Simulation

```python
from consultantos.agents.wargaming_agent import WargamingAgent
from consultantos.simulation.scenario_builder import ScenarioBuilder

# Create scenario
builder = ScenarioBuilder()
scenario = builder.build_price_war_scenario(
    our_market_share=0.30,
    competitor_name="CompetitorX"
)

# Run simulation
agent = WargamingAgent(num_iterations=10000)
result = await agent.execute(
    scenario=scenario,
    include_sensitivity=True
)

# Analyze results
print(f"Expected Value: ${result.expected_value:,.0f}")
print(f"Win Probability: {result.win_probability:.1%}")
print(f"Key Driver: {result.sensitivity.rank_order[0]}")
```

### Compare Scenarios

```python
# Create multiple scenarios
scenario1 = builder.build_price_war_scenario(...)
scenario2 = builder.build_new_entrant_scenario(...)

# Compare
comparison = await agent.compare_scenarios(
    scenarios=[scenario1, scenario2],
    num_iterations=10000
)

# Best option
best_scenario, best_value = comparison.ranking[0]
print(f"Best strategy: {best_scenario} (${best_value:,.0f})")
```

---

## Distribution Reference

### Normal Distribution
```python
Distribution(
    type="normal",
    params={"mean": 100.0, "std": 15.0}
)
```
**Use for:** Revenue, costs, market size (symmetric uncertainty)

### Uniform Distribution
```python
Distribution(
    type="uniform",
    params={"min": 50.0, "max": 150.0}
)
```
**Use for:** Equal probability across range (no information)

### Triangular Distribution
```python
Distribution(
    type="triangular",
    params={"min": 50.0, "mode": 100.0, "max": 200.0}
)
```
**Use for:** Expert estimates (min, most likely, max scenarios)

### Beta Distribution
```python
Distribution(
    type="beta",
    params={"alpha": 2.0, "beta": 5.0, "scale": 1.0}
)
```
**Use for:** Percentages, probabilities (bounded 0-1)

### Lognormal Distribution
```python
Distribution(
    type="lognormal",
    params={"mean": 10.0, "std": 0.5}
)
```
**Use for:** Multiplicative processes, asset prices (positive skew)

---

## Interpreting Results

### Expected Value
- **Mean outcome** across all simulations
- Use for comparing scenarios
- May not represent most likely outcome (see median)

### Percentiles
- **P10**: Only 10% of outcomes worse
- **P50 (Median)**: Middle outcome
- **P90**: Only 10% of outcomes better

### Risk Metrics
- **VaR (95%)**: Worst case in 95% of scenarios
- **CVaR**: Average of worst 5% of cases
- **Volatility**: Standard deviation (outcome spread)

### Win Probability
- Probability of positive outcome (> 0)
- Customize threshold in formula if needed

### Sensitivity Analysis
- **Rank Order**: Variables by impact on variance
- **Impact Score**: Percentage of variance explained
- Focus on top 2-3 drivers for risk management

---

## Best Practices

### Choosing Iterations

| Use Case | Iterations | Reason |
|----------|------------|--------|
| Quick test | 1,000-2,000 | Fast feedback |
| Standard analysis | 10,000 | Good accuracy |
| High stakes | 20,000-50,000 | Maximum precision |
| Presentation | 10,000 | Balance speed/quality |

### Distribution Selection

1. **Use triangular** when you have expert estimates (min/mode/max)
2. **Use normal** for well-understood symmetric variables
3. **Use uniform** when you have no information (conservative)
4. **Use lognormal** for multiplicative processes
5. **Use beta** for percentages/probabilities

### Formula Writing

✅ **Good:**
```python
"revenue * (1 - price_cut) * market_share"
```

❌ **Avoid:**
```python
"revenue / 0"  # Division by zero
"revenue ** 1000"  # Extreme operations
```

**Safe Operations:**
- Arithmetic: `+`, `-`, `*`, `/`
- Functions: `min()`, `max()`, `abs()`
- Comparisons: `>`, `<`, `>=`, `<=`

---

## Visualization Examples

### Distribution Chart
Shows probability distribution of outcomes with key statistics.

```python
from consultantos.visualizations.wargaming_charts import create_distribution_chart

fig = create_distribution_chart(result.simulation)
fig.write_html("distribution.html")
```

### Tornado Diagram
Shows which variables drive outcome variance.

```python
from consultantos.visualizations.wargaming_charts import create_tornado_diagram

fig = create_tornado_diagram(result.sensitivity, top_n=5)
fig.write_html("sensitivity.html")
```

### Risk-Return Chart
Compare scenarios on risk vs. return.

```python
from consultantos.visualizations.wargaming_charts import create_risk_heatmap

scenarios = {
    "Conservative": {"expected_return": 5M, "volatility": 1M},
    "Aggressive": {"expected_return": 10M, "volatility": 3M}
}

fig = create_risk_heatmap(scenarios)
fig.write_html("risk_return.html")
```

---

## Common Use Cases

### 1. Competitive Response Planning

**Scenario:** Competitor likely to cut prices

```python
scenario = WargameScenario(
    variables={
        "competitor_price_cut": Distribution(
            type="triangular",
            params={"min": 0.10, "mode": 0.20, "max": 0.30}
        ),
        "our_response": Distribution(
            type="triangular",
            params={"min": 0.05, "mode": 0.15, "max": 0.25}
        ),
        "market_elasticity": Distribution(
            type="normal",
            params={"mean": -2.0, "std": 0.5}
        )
    },
    formula="base_revenue * (1 - our_response) * (1 + market_elasticity * our_response)"
)
```

### 2. Market Entry Decision

**Scenario:** Should we enter new market?

```python
scenario = builder.build_new_entrant_scenario(
    market_size=100_000_000,
    entrant_name="Our Company"
)

result = await agent.execute(scenario)

# Decision rule
if result.win_probability > 0.70 and result.var_95 > -5_000_000:
    print("✅ Recommend market entry")
else:
    print("❌ Too risky - do not enter")
```

### 3. Product Launch ROI

**Scenario:** New product launch profitability

```python
scenario = builder.build_product_launch_scenario(
    investment=5_000_000
)

result = await agent.execute(scenario, include_sensitivity=True)

# Identify key drivers
top_driver = result.sensitivity.rank_order[0]
print(f"Focus on managing: {top_driver}")
```

---

## Troubleshooting

### Low Win Probability
- Review variable distributions (too pessimistic?)
- Check formula logic
- Consider best-case scenarios in triangular distributions

### High Variance
- Identify key drivers via sensitivity analysis
- Reduce uncertainty on top 2-3 variables
- Consider risk mitigation strategies

### Unexpected Results
- Validate formula with known values
- Check distribution parameters
- Review competitor action probabilities
- Run with fewer iterations for debugging

---

## Performance Tips

1. **Start small**: Test with 1,000 iterations before scaling
2. **Use sensitivity**: Identifies where to focus modeling effort
3. **Batch comparisons**: Compare scenarios in single call
4. **Cache results**: Store scenario results for reuse
5. **Parallel execution**: API handles concurrent requests

---

## Next Steps

1. **Explore templates** - Try each built-in scenario
2. **Build custom scenarios** - Model your specific situation
3. **Run comparisons** - Evaluate multiple strategies
4. **Visualize results** - Use charts for stakeholder communication
5. **Iterate rapidly** - Test assumptions with quick simulations

---

## Support

- **API Docs**: http://localhost:8080/docs
- **Examples**: See `WARGAMING_IMPLEMENTATION_SUMMARY.md`
- **Tests**: `tests/test_wargaming_agent.py` for code examples

**Implementation Date**: 2025-11-09
**Status**: Production Ready ✅
