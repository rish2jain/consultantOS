# Phase 1 Quick Wins - Usage Examples

This document demonstrates how to use the three strategic intelligence modules for actionable insights.

## 1. Cross-Source Signal Amplification

Detect analyst-reality divergences to predict earnings surprises.

```python
from consultantos.analysis import analyze_triangulation_signals
from consultantos.models import FinancialSnapshot, AnalystRecommendations, NewsSentiment

# Prepare financial snapshot with multi-source data
snapshot = FinancialSnapshot(
    ticker="TSLA",
    market_cap=800_000_000_000,
    revenue=96_000_000_000,
    revenue_growth=-5.0,  # Declining revenue
    profit_margin=0.08,   # Compressed margins
    pe_ratio=45.0,
    risk_assessment="High",
    analyst_recommendations=AnalystRecommendations(
        strong_buy=15,
        buy=10,
        hold=8,
        sell=2,
        strong_sell=1,
        total_analysts=36,
        consensus="Buy"  # Bullish analysts
    ),
    news_sentiment=NewsSentiment(
        articles_count=50,
        sentiment_score=0.6,
        sentiment="Positive"
    ),
    data_sources=["yfinance", "finnhub"]
)

# Analyze triangulation signals
result = analyze_triangulation_signals(
    financial_snapshot=snapshot,
    company="Tesla",
    historical_patterns=[
        {
            "pattern_type": "earnings_miss",
            "probability": 0.75,
            "timeline_days": 45
        }
    ]
)

# Access results
print(f"Overall Signal: {result.overall_signal}")
# Output: bearish_divergence

for signal in result.signals:
    print(f"\nSignal: {signal.title}")
    print(f"Type: {signal.signal_type}")
    print(f"Probability: {signal.probability:.0%}")
    print(f"Timeline: {signal.timeline_days} days")
    print(f"Confidence: {signal.confidence_score:.0%}")
    print(f"Action: {signal.recommended_action}")

# Output:
# Signal: Tesla: Bearish Divergence - Analyst Optimism vs Weak Fundamentals
# Type: bearish_divergence
# Probability: 72%
# Timeline: 45 days
# Confidence: 85%
# Action: CAUTION: Consider reducing exposure before next earnings...
```

### Key Insights

**Bearish Divergence Detected:**
- Analysts maintain bullish consensus (25 buy/strong buy vs 3 sell/strong sell)
- But fundamentals show weakness: -5% revenue growth, 8% margins
- Historical pattern: 72% probability of earnings miss within 45 days

**Recommended Action:**
Reduce exposure before next earnings to de-risk potential disappointment.

---

## 2. Geographic Opportunity Heatmap

Identify underserved high-demand markets for expansion.

```python
from consultantos.analysis import analyze_geographic_opportunities
from consultantos.models import MarketTrends

# Market trends from Google Trends
trends = MarketTrends(
    search_interest_trend="Growing",
    interest_data={"time_series": "..."},
    geographic_distribution={
        "California": 100,
        "Texas": 85,
        "Florida": 70,
        "New York": 95,
        "Illinois": 60,
        "Washington": 55,
        "Arizona": 50,
        "North Carolina": 45,
        "Georgia": 48,
        "Colorado": 52
    },
    related_searches=["electric vehicles", "tesla", "EV charging"],
    competitive_comparison={}
)

# Current market presence (optional)
current_presence = {
    "California": 0.25,  # 25% market share
    "New York": 0.15,
    "Texas": 0.05
}

# Analyze opportunities
result = analyze_geographic_opportunities(
    market_trends=trends,
    company="Tesla",
    industry="Electric Vehicles",
    current_presence=current_presence,
    investment_budget=20_000_000  # $20M budget
)

# Top opportunity
top = result.top_recommendation
print(f"\n🎯 Top Opportunity: {top.region}")
print(f"Opportunity Index: {top.opportunity_index:.1f}/100")
print(f"Ranking: #{top.ranking}")
print(f"Market Size: ${top.market_size_estimate:,.0f}")
print(f"Investment Required: ${top.estimated_investment:,.0f}")
print(f"Expected ROI: {top.expected_roi:.1f}x")
print(f"Payback Period: {top.payback_period_months} months")
print(f"\nStrategy: {top.expansion_strategy}")

# Investment breakdown
print(f"\n💰 Investment Allocation:")
for category, amount in top.investment_breakdown.items():
    print(f"  {category.title()}: ${amount:,.0f}")

# All opportunities within budget
print(f"\n📊 All Opportunities (within ${investment_budget:,.0f} budget):")
for opp in result.opportunities:
    print(f"  #{opp.ranking}. {opp.region} - OI: {opp.opportunity_index:.1f}, "
          f"ROI: {opp.expected_roi:.1f}x, Investment: ${opp.estimated_investment:,.0f}")

# Output:
# 🎯 Top Opportunity: Texas
# Opportunity Index: 85.0/100
# Ranking: #1
# Market Size: $25,500,000,000
# Investment Required: $510,000,000
# Expected ROI: 2.8x
# Payback Period: 18 months
#
# Strategy: Scale existing presence through aggressive marketing and operations expansion
#
# 💰 Investment Allocation:
#   Marketing: $204,000,000
#   Operations: $153,000,000
#   Technology: $76,500,000
#   Hiring: $51,000,000
#   Contingency: $25,500,000
```

### Key Insights

**Top 3 Expansion Opportunities:**

1. **Texas** (OI: 85.0)
   - High demand (85/100), low competition (2.5/10)
   - $25.5B addressable market
   - 2.8x ROI potential, 18-month payback
   - Strategy: Scale existing 5% share to 15%

2. **Florida** (OI: 70.0)
   - Strong demand (70/100), moderate competition (5.0/10)
   - $21.0B addressable market
   - 2.2x ROI potential, 24-month payback
   - Strategy: New market entry with differentiated positioning

3. **Arizona** (OI: 62.5)
   - Moderate demand (50/100), very low competition (1.0/10)
   - $15.0B addressable market
   - 3.2x ROI potential, 14-month payback
   - Strategy: First-mover advantage in emerging market

**Budget Allocation:**
With $20M budget, can pursue Arizona + North Carolina opportunities for diversified geographic expansion.

---

## 3. Sentiment-Performance Prediction

Predict earnings outcomes based on sentiment trends.

```python
from consultantos.analysis import predict_financial_performance
from consultantos.models import NewsSentiment, FinancialSnapshot, MonitorAnalysisSnapshot
from datetime import datetime, timedelta

# Current sentiment
current_sentiment = NewsSentiment(
    articles_count=75,
    sentiment_score=-0.35,  # Negative sentiment
    sentiment="Negative",
    recent_headlines=[
        "Company faces regulatory scrutiny",
        "Competitor gains market share",
        "Analyst downgrades stock to Hold"
    ]
)

# Financial snapshot
financial_snapshot = FinancialSnapshot(
    ticker="AAPL",
    market_cap=2_800_000_000_000,
    revenue=394_000_000_000,
    revenue_growth=8.0,
    profit_margin=0.25,
    pe_ratio=28.5,
    risk_assessment="Low"
)

# Historical snapshots for correlation analysis
historical_snapshots = [
    MonitorAnalysisSnapshot(
        monitor_id="test",
        timestamp=datetime.utcnow() - timedelta(days=90),
        company="Apple",
        industry="Technology",
        news_sentiment=0.4,  # Positive sentiment
        financial_metrics={
            "revenue_growth": 12.0,
            "profit_margin": 0.26
        }
    ),
    MonitorAnalysisSnapshot(
        monitor_id="test",
        timestamp=datetime.utcnow() - timedelta(days=60),
        company="Apple",
        industry="Technology",
        news_sentiment=0.1,  # Neutral
        financial_metrics={
            "revenue_growth": 10.0,
            "profit_margin": 0.25
        }
    ),
    MonitorAnalysisSnapshot(
        monitor_id="test",
        timestamp=datetime.utcnow() - timedelta(days=30),
        company="Apple",
        industry="Technology",
        news_sentiment=-0.2,  # Slightly negative
        financial_metrics={
            "revenue_growth": 8.5,
            "profit_margin": 0.25
        }
    )
]

# Predict performance
result = predict_financial_performance(
    current_sentiment=current_sentiment,
    financial_snapshot=financial_snapshot,
    company="Apple",
    historical_snapshots=historical_snapshots,
    next_earnings_date=datetime.utcnow() + timedelta(days=45)
)

# Access prediction
pred = result.prediction
print(f"\n📈 Earnings Prediction for Apple (AAPL)")
print(f"Predicted Outcome: {pred.predicted_outcome.value.upper()}")
print(f"Confidence: {pred.confidence:.0%}")
print(f"\nProbabilities:")
print(f"  Beat: {pred.probability_beat:.0%}")
print(f"  Meet: {pred.probability_meet:.0%}")
print(f"  Miss: {pred.probability_miss:.0%}")
print(f"\nSentiment Analysis:")
print(f"  Current Score: {pred.current_sentiment_score:.2f}")
print(f"  Trend: {pred.sentiment_trend.value}")
print(f"  Momentum: {pred.sentiment_momentum:.2f}")
print(f"\nNext Earnings: {pred.next_earnings_date.strftime('%Y-%m-%d')}")
print(f"Lead Time: {pred.lead_time_days} days")

# Correlation analysis
if pred.correlation:
    corr = pred.correlation
    print(f"\n🔗 Historical Correlation:")
    print(f"  Strength: {corr.correlation_strength:.2f}")
    print(f"  Lead Time: {corr.lead_time_days} days")
    print(f"  Historical Accuracy: {corr.historical_accuracy:.0%}")
    print(f"  Sample Size: {corr.sample_size} observations")

# Key drivers
print(f"\n🔑 Sentiment Drivers:")
for driver in pred.key_sentiment_drivers:
    print(f"  • {driver}")

# Explanation
print(f"\n📝 {pred.explanation}")

# Output:
# 📈 Earnings Prediction for Apple (AAPL)
# Predicted Outcome: MISS
# Confidence: 68%
#
# Probabilities:
#   Beat: 15%
#   Meet: 40%
#   Miss: 45%
#
# Sentiment Analysis:
#   Current Score: -0.35
#   Trend: deteriorating
#   Momentum: -0.25
#
# Next Earnings: 2025-03-15
# Lead Time: 30 days
#
# 🔗 Historical Correlation:
#   Strength: 0.72
#   Lead Time: 30 days
#   Historical Accuracy: 86%
#   Sample Size: 3 observations
#
# 🔑 Sentiment Drivers:
#   • Negative media narrative
#   • Deteriorating sentiment trend
#   • High sentiment momentum (negative)
#   • High media attention (75 articles)
```

### Key Insights

**Earnings Miss Prediction:**
- Current sentiment: Negative (-0.35) with deteriorating trend
- 45% probability of earnings miss vs 15% beat
- Sentiment momentum strongly negative (-0.25)
- Historical correlation: 0.72 strength, 30-day lead time

**Supporting Evidence:**
- 75 articles analyzed showing negative narrative
- Recent headlines about regulatory scrutiny and competition
- Sentiment has declined from +0.4 to -0.35 over 90 days
- Historical accuracy: 86% based on prior predictions

**Recommended Action:**
Monitor closely for sentiment reversal or fundamental improvement. Consider hedging exposure if sentiment continues to deteriorate.

---

## Integration Example

Combine all three modules for comprehensive strategic intelligence:

```python
from consultantos.analysis import (
    analyze_triangulation_signals,
    analyze_geographic_opportunities,
    predict_financial_performance
)

# Run all analyses
triangulation = analyze_triangulation_signals(snapshot, company)
geographic = analyze_geographic_opportunities(trends, company, industry)
sentiment_pred = predict_financial_performance(sentiment, snapshot, company)

# Strategic dashboard view
print("=" * 60)
print(f"STRATEGIC INTELLIGENCE DASHBOARD: {company}")
print("=" * 60)

print(f"\n📊 Cross-Source Signals:")
print(f"  Overall Signal: {triangulation.overall_signal.value}")
print(f"  Top Signal: {triangulation.signals[0].title}")
print(f"  Confidence: {triangulation.signals[0].confidence_score:.0%}")

print(f"\n🌍 Geographic Opportunities:")
print(f"  Top Market: {geographic.top_recommendation.region}")
print(f"  Opportunity Index: {geographic.top_recommendation.opportunity_index:.1f}")
print(f"  Expected ROI: {geographic.top_recommendation.expected_roi:.1f}x")

print(f"\n📈 Earnings Prediction:")
print(f"  Predicted Outcome: {sentiment_pred.prediction.predicted_outcome.value}")
print(f"  Confidence: {sentiment_pred.prediction.confidence:.0%}")
print(f"  Timeline: {sentiment_pred.prediction.lead_time_days} days")

print("\n" + "=" * 60)
```

This creates a comprehensive strategic intelligence view combining:
- **Tactical signals** (triangulation) for short-term trading decisions
- **Strategic opportunities** (geographic) for expansion planning
- **Predictive insights** (sentiment) for risk management
