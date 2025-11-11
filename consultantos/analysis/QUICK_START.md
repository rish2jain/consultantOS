# Phase 1 Quick Wins - Quick Start Guide

Get started with strategic intelligence analysis in 5 minutes.

## Installation

The modules are already installed as part of ConsultantOS. No additional dependencies required.

## Basic Usage

### 1. Import the modules

```python
from consultantos.analysis import (
    analyze_triangulation_signals,
    analyze_geographic_opportunities,
    predict_financial_performance
)
```

### 2. Prepare your data

```python
# From existing agents
financial_snapshot = financial_agent.execute({"company": "Tesla", "ticker": "TSLA"})
market_trends = market_agent.execute({"company": "Tesla", "industry": "EV"})
news_sentiment = financial_snapshot.news_sentiment  # From FinancialAgent
```

### 3. Run analyses

```python
# Detect trading signals
signals = analyze_triangulation_signals(financial_snapshot, "Tesla")
print(f"Signal: {signals.overall_signal}")
print(f"Action: {signals.signals[0].recommended_action}")

# Find expansion opportunities
opportunities = analyze_geographic_opportunities(
    market_trends, "Tesla", "Electric Vehicles"
)
print(f"Top market: {opportunities.top_recommendation.region}")
print(f"ROI: {opportunities.top_recommendation.expected_roi}x")

# Predict earnings
prediction = predict_financial_performance(news_sentiment, financial_snapshot, "Tesla")
print(f"Forecast: {prediction.prediction.predicted_outcome}")
print(f"Confidence: {prediction.prediction.confidence:.0%}")
```

## Complete Example

```python
from consultantos.agents import FinancialAgent, MarketAgent
from consultantos.analysis import (
    analyze_triangulation_signals,
    analyze_geographic_opportunities,
    predict_financial_performance
)

async def analyze_company(company: str, ticker: str, industry: str):
    """Complete strategic analysis for a company"""
    
    # Fetch data from agents
    financial_agent = FinancialAgent()
    market_agent = MarketAgent()
    
    financial_data = await financial_agent.execute({
        "company": company,
        "ticker": ticker
    })
    
    market_data = await market_agent.execute({
        "company": company,
        "industry": industry
    })
    
    # Run strategic analyses
    signals = analyze_triangulation_signals(financial_data, company)
    opportunities = analyze_geographic_opportunities(market_data, company, industry)
    prediction = predict_financial_performance(
        financial_data.news_sentiment,
        financial_data,
        company
    )
    
    # Return strategic dashboard
    return {
        "company": company,
        "trading_signals": {
            "overall": signals.overall_signal,
            "top_signal": signals.signals[0] if signals.signals else None,
            "confidence": signals.signals[0].confidence_score if signals.signals else 0
        },
        "expansion_opportunities": {
            "top_market": opportunities.top_recommendation.region,
            "investment": opportunities.top_recommendation.estimated_investment,
            "roi": opportunities.top_recommendation.expected_roi,
            "payback_months": opportunities.top_recommendation.payback_period_months
        },
        "earnings_forecast": {
            "outcome": prediction.prediction.predicted_outcome,
            "confidence": prediction.prediction.confidence,
            "probabilities": {
                "beat": prediction.prediction.probability_beat,
                "meet": prediction.prediction.probability_meet,
                "miss": prediction.prediction.probability_miss
            }
        }
    }

# Run analysis
result = await analyze_company("Tesla", "TSLA", "Electric Vehicles")
print(result)
```

## Output Format

All modules return Pydantic models with structured data:

```python
# Triangulation Signals
{
    "company": "Tesla",
    "signals": [
        {
            "signal_type": "bearish_divergence",
            "probability": 0.72,
            "confidence_score": 0.85,
            "recommended_action": "CAUTION: Consider reducing exposure..."
        }
    ],
    "overall_signal": "bearish_divergence",
    "data_quality_score": 0.85
}

# Geographic Opportunities
{
    "company": "Tesla",
    "opportunities": [
        {
            "region": "Texas",
            "opportunity_index": 85.0,
            "expected_roi": 2.8,
            "estimated_investment": 510000000,
            "payback_period_months": 18
        }
    ]
}

# Sentiment Prediction
{
    "company": "Tesla",
    "prediction": {
        "predicted_outcome": "miss",
        "confidence": 0.68,
        "probability_beat": 0.15,
        "probability_meet": 0.40,
        "probability_miss": 0.45
    }
}
```

## Common Patterns

### Pattern 1: Alert on High-Confidence Signals

```python
signals = analyze_triangulation_signals(snapshot, company)

for signal in signals.signals:
    if signal.confidence_score > 0.75:
        send_alert(
            title=signal.title,
            message=signal.explanation,
            action=signal.recommended_action
        )
```

### Pattern 2: Budget-Constrained Expansion

```python
opportunities = analyze_geographic_opportunities(
    trends,
    company,
    industry,
    investment_budget=20_000_000  # $20M budget
)

# Returns only opportunities within budget
for opp in opportunities.opportunities:
    print(f"{opp.region}: ${opp.estimated_investment:,.0f} → {opp.expected_roi}x ROI")
```

### Pattern 3: Historical Correlation

```python
# With historical snapshots for better accuracy
prediction = predict_financial_performance(
    sentiment,
    snapshot,
    company,
    historical_snapshots=past_snapshots  # Improves accuracy by 30%
)

if prediction.prediction.correlation:
    print(f"Historical correlation: {prediction.prediction.correlation.correlation_strength:.2f}")
    print(f"Accuracy: {prediction.prediction.correlation.historical_accuracy:.0%}")
```

## Error Handling

All modules handle missing data gracefully:

```python
# Low data quality warning
if signals.data_quality_score < 0.5:
    logger.warning("Insufficient data for reliable analysis")

# No signals detected
if not signals.signals:
    logger.info("No divergence signals detected")

# Low confidence predictions
if prediction.prediction.confidence < 0.6:
    logger.warning("Low confidence prediction - validate before acting")
```

## Next Steps

- **API Integration**: See `USAGE_EXAMPLES.md` for API endpoint examples
- **Dashboard Integration**: Visualize results in real-time dashboard
- **Monitoring**: Integrate with continuous monitoring system
- **Backtesting**: Validate predictions against historical data

## Support

- Full documentation: `README.md`
- Usage examples: `USAGE_EXAMPLES.md`
- Technical details: Docstrings in each module
- Project guide: `CLAUDE.md` in root directory
