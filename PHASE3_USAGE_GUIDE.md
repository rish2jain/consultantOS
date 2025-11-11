# Phase 3 Advanced Intelligence - Usage Guide

## Quick Start

### 1. Systems Agent - Feedback Loop Analysis

```python
from consultantos.agents import SystemsAgent
import asyncio

async def analyze_business_system():
    # Initialize agent
    agent = SystemsAgent(timeout=90)

    # Prepare time series data (monthly data for 2 years)
    input_data = {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "time_series_data": {
            "revenue": [1500, 1600, 1750, 1900, 2100, 2300, ...],  # 24 months
            "customer_satisfaction": [78, 79, 81, 83, 85, 87, ...],
            "market_share": [18, 19, 20, 22, 24, 26, ...],
            "brand_value": [45, 48, 52, 56, 61, 67, ...],
            "r_d_investment": [200, 210, 225, 240, 260, 280, ...],
        },
        "metric_names": ["revenue", "customer_satisfaction", "market_share",
                        "brand_value", "r_d_investment"]
    }

    # Execute analysis
    result = await agent.execute(input_data)

    if result["success"]:
        analysis = result["data"]
        narrative = result["narrative"]

        print(f"✅ System Analysis Complete")
        print(f"📊 Confidence: {analysis.confidence_score:.0f}%")
        print(f"🔄 Reinforcing Loops: {len(analysis.reinforcing_loops)}")
        print(f"⚖️ Balancing Loops: {len(analysis.balancing_loops)}")
        print(f"🎯 Leverage Points: {len(analysis.leverage_points)}")
        print(f"\n{narrative}")

        # Access specific insights
        if analysis.reinforcing_loops:
            dominant = next((l for l in analysis.reinforcing_loops if l.dominant), None)
            if dominant:
                print(f"\n🌟 Dominant Loop: {dominant.loop_name}")
                print(f"   Impact: {dominant.impact}")
                print(f"   Strength: {dominant.strength:.0f}/100")

        # Top leverage points
        print("\n🎯 Top 3 Leverage Points:")
        for i, lp in enumerate(analysis.leverage_points[:3], 1):
            print(f"{i}. {lp.leverage_name} (Level {lp.leverage_level})")
            print(f"   Impact: {lp.impact_potential:.0f}/100")
            print(f"   {lp.proposed_intervention}")
    else:
        print(f"❌ Analysis failed: {result['error']}")

# Run
asyncio.run(analyze_business_system())
```

### 2. Feedback Loop Detector - Direct Usage

```python
from consultantos.analysis.feedback_loops import FeedbackLoopDetector
import numpy as np

# Create detector
detector = FeedbackLoopDetector(
    min_correlation=0.5,  # Minimum correlation for causal links
    min_confidence=0.6     # Minimum confidence for loop detection
)

# Prepare time series data
n_months = 24
time_series_data = {
    "revenue": np.linspace(100, 200, n_months) + np.random.normal(0, 5, n_months),
    "satisfaction": np.linspace(70, 85, n_months) + np.random.normal(0, 2, n_months),
    "market_share": np.linspace(15, 25, n_months) + np.random.normal(0, 1, n_months),
}

metric_names = list(time_series_data.keys())

# Step 1: Detect causal links
causal_links = detector.detect_causal_links(time_series_data, metric_names)
print(f"Found {len(causal_links)} causal relationships")

for link in causal_links:
    print(f"  {link.from_element} → {link.to_element} "
          f"({link.polarity}, strength: {link.strength:.0f})")

# Step 2: Detect feedback loops
reinforcing, balancing = detector.detect_feedback_loops(causal_links, metric_names)
print(f"\nDetected {len(reinforcing)} reinforcing loops")
print(f"Detected {len(balancing)} balancing loops")

# Step 3: Identify leverage points
all_loops = reinforcing + balancing
leverage_points = detector.identify_leverage_points(all_loops, "MyCompany", "Tech")

print(f"\nTop 3 Leverage Points:")
for lp in leverage_points[:3]:
    roi = lp.impact_potential / max(lp.implementation_difficulty, 1)
    print(f"  - {lp.leverage_name}")
    print(f"    ROI: {roi:.2f}, Impact: {lp.impact_potential:.0f}/100")

# Complete analysis
full_analysis = detector.analyze_system(
    time_series_data,
    metric_names,
    "MyCompany",
    "Technology"
)

print(f"\n📊 System Archetype: {full_analysis.system_archetype}")
print(f"📈 Current Behavior: {full_analysis.current_behavior}")
print(f"⚠️ Structural Issues:")
for issue in full_analysis.structural_issues:
    print(f"  - {issue}")
```

### 3. Momentum Tracking Engine

```python
from consultantos.analysis.momentum_tracking import MomentumTrackingEngine

# Create engine
engine = MomentumTrackingEngine(smoothing_window=3)

# Prepare metrics data by component
metrics_data = {
    "market": {
        "search_volume": [100, 110, 125, 140, 160, 185, 215, 250, 290, 335, 385, 445],
        "brand_awareness": [50, 52, 55, 59, 64, 70, 77, 85, 94, 104, 115, 127],
    },
    "financial": {
        "revenue": [1000, 1100, 1250, 1400, 1600, 1850, 2150, 2500, 2900, 3350, 3850, 4400],
        "gross_margin": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
    },
    "strategic": {
        "partnerships": [5, 6, 7, 8, 10, 12, 15, 18, 22, 27, 33, 40],
        "product_launches": [2, 2, 3, 3, 4, 5, 6, 7, 8, 10, 12, 14],
    },
    "execution": {
        "delivery_speed": [30, 28, 26, 24, 22, 20, 18, 17, 16, 15, 14, 13],  # Lower is better
        "quality_score": [80, 81, 83, 85, 87, 89, 91, 93, 95, 96, 97, 98],
    },
    "talent": {
        "employee_nps": [60, 62, 65, 68, 72, 76, 80, 84, 88, 91, 94, 96],
        "retention_rate": [85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96],
    }
}

# Analyze momentum
analysis = engine.analyze_momentum(
    company="RocketCo",
    industry="SaaS",
    metrics_data=metrics_data
)

print(f"🚀 Current Momentum: {analysis.current_momentum:.1f}/100")
print(f"📈 Trend: {analysis.momentum_trend}")
print(f"🎯 Confidence: {analysis.confidence_score:.0f}%")

print(f"\n💪 Strongest Contributors:")
for contributor in analysis.strongest_contributors[:3]:
    print(f"  - {contributor}")

print(f"\n⚠️ Drag Factors:")
for drag in analysis.drag_factors:
    print(f"  - {drag}")

print(f"\n🔮 Projections:")
print(f"  30-day: {analysis.projected_momentum_30d:.1f}/100")
print(f"  90-day: {analysis.projected_momentum_90d:.1f}/100")
print(f"  Inflection Risk: {analysis.inflection_point_risk:.0f}%")

print(f"\n🎯 Acceleration Opportunities:")
for opp in analysis.acceleration_opportunities:
    print(f"  - {opp}")
```

### 4. Single Metric Momentum Analysis

```python
from consultantos.analysis.momentum_tracking import MomentumTrackingEngine

engine = MomentumTrackingEngine()

# Analyze single metric
revenue_series = [1000, 1100, 1250, 1400, 1600, 1850, 2150, 2500, 2900, 3350, 3850, 4400]

metric = engine.analyze_metric_momentum(
    metric_name="monthly_revenue",
    time_series=revenue_series,
    metric_type="financial"
)

print(f"📊 Metric: {metric.metric_name}")
print(f"   Current: ${metric.current_value:,.0f}")
print(f"   Previous: ${metric.previous_value:,.0f}")
print(f"   Velocity: {metric.velocity:.2f} (growth rate)")
print(f"   Acceleration: {metric.acceleration:.2f} (growth rate change)")
print(f"   Flywheel Contribution: {metric.contribution_to_flywheel:.0f}/100")

# Calculate derivatives manually
velocity, acceleration = engine.calculate_velocity_and_acceleration(
    revenue_series,
    "monthly_revenue"
)
print(f"\n📈 First Derivative (Velocity): {velocity:.2f}")
print(f"📊 Second Derivative (Acceleration): {acceleration:.2f}")

# Detect inflection points
inflections = engine.detect_inflection_points(revenue_series, "monthly_revenue")
if inflections:
    print(f"\n⚡ Inflection Points Detected:")
    for idx, change_type in inflections:
        print(f"   Month {idx}: {change_type}")
```

## Advanced Usage

### Custom Correlation Thresholds

```python
# Stricter detection
strict_detector = FeedbackLoopDetector(
    min_correlation=0.7,  # Higher threshold
    min_confidence=0.8
)

# More lenient detection
lenient_detector = FeedbackLoopDetector(
    min_correlation=0.3,  # Lower threshold
    min_confidence=0.5
)
```

### Custom Smoothing Window

```python
# Aggressive smoothing (reduce noise)
smooth_engine = MomentumTrackingEngine(smoothing_window=5)

# Minimal smoothing (more responsive)
responsive_engine = MomentumTrackingEngine(smoothing_window=2)
```

### Accessing Individual Loop Details

```python
analysis = detector.analyze_system(data, metrics, company, industry)

# Examine reinforcing loops (virtuous/vicious cycles)
for loop in analysis.reinforcing_loops:
    print(f"\n🔄 {loop.loop_name} ({loop.loop_id})")
    print(f"   Strength: {loop.strength:.0f}/100")
    print(f"   Dominant: {'Yes' if loop.dominant else 'No'}")
    print(f"   Elements: {' → '.join(loop.elements)}")
    print(f"   Impact: {loop.impact}")
    print(f"   Current State: {loop.current_state}")

    print(f"   Intervention Points:")
    for intervention in loop.intervention_points:
        print(f"     - {intervention}")

# Examine leverage points by level (Meadows' hierarchy)
leverage_by_level = {}
for lp in analysis.leverage_points:
    level = lp.leverage_level
    if level not in leverage_by_level:
        leverage_by_level[level] = []
    leverage_by_level[level].append(lp)

for level in sorted(leverage_by_level.keys()):
    print(f"\n🎯 Level {level} Leverage Points:")
    for lp in leverage_by_level[level]:
        print(f"   - {lp.leverage_name}")
        print(f"     Impact: {lp.impact_potential:.0f}, Difficulty: {lp.implementation_difficulty:.0f}")
```

### Component-Wise Momentum Breakdown

```python
analysis = engine.analyze_momentum(company, industry, metrics_data)

# Get metrics by component
market_metrics = [m for m in analysis.key_metrics if "search" in m.metric_name.lower() or "brand" in m.metric_name.lower()]
financial_metrics = [m for m in analysis.key_metrics if "revenue" in m.metric_name.lower() or "margin" in m.metric_name.lower()]

print("📊 Market Momentum Breakdown:")
for metric in market_metrics:
    print(f"  {metric.metric_name}: {metric.contribution_to_flywheel:.0f}/100")
    print(f"    Velocity: {metric.velocity:.2f}, Acceleration: {metric.acceleration:.2f}")

# Identify accelerating vs decelerating metrics
accelerating = [m for m in analysis.key_metrics if m.acceleration > 0]
decelerating = [m for m in analysis.key_metrics if m.acceleration < 0]

print(f"\n✅ Accelerating Metrics ({len(accelerating)}):")
for m in accelerating:
    print(f"  - {m.metric_name}")

print(f"\n⚠️ Decelerating Metrics ({len(decelerating)}):")
for m in decelerating:
    print(f"  - {m.metric_name}")
```

## Data Preparation Tips

### Time Series Requirements

```python
# Minimum requirements
min_data_points = 3  # For basic analysis
recommended_data_points = 12  # 1 year monthly
ideal_data_points = 24  # 2 years monthly

# Data should be regularly spaced
# Use monthly, quarterly, or weekly intervals
# Avoid mixing time scales

# Example: Monthly data
import pandas as pd

df = pd.DataFrame({
    'month': pd.date_range('2023-01-01', periods=24, freq='M'),
    'revenue': [...],  # 24 values
    'customers': [...],  # 24 values
})

time_series_data = {
    'revenue': df['revenue'].tolist(),
    'customers': df['customers'].tolist(),
}
```

### Handling Missing Data

```python
import numpy as np

# Option 1: Interpolation
from scipy.interpolate import interp1d

x = np.arange(len(series_with_gaps))
mask = ~np.isnan(series_with_gaps)
f = interp1d(x[mask], series_with_gaps[mask], kind='linear', fill_value='extrapolate')
filled_series = f(x)

# Option 2: Forward fill
import pandas as pd
series_filled = pd.Series(series_with_gaps).fillna(method='ffill').tolist()

# Option 3: Remove metrics with too many gaps
def filter_valid_metrics(time_series_data, max_missing_pct=0.2):
    valid_metrics = {}
    for metric, values in time_series_data.items():
        missing_pct = sum(1 for v in values if v is None or np.isnan(v)) / len(values)
        if missing_pct <= max_missing_pct:
            valid_metrics[metric] = values
    return valid_metrics
```

### Metric Naming Best Practices

```python
# Good metric names (descriptive, consistent)
good_names = {
    "monthly_revenue": [...],
    "customer_satisfaction_nps": [...],
    "market_share_percentage": [...],
    "brand_awareness_score": [...],
    "employee_retention_rate": [...],
}

# Avoid
bad_names = {
    "rev": [...],  # Too short
    "metric_1": [...],  # Not descriptive
    "Customer Satisfaction Score (NPS)": [...],  # Inconsistent formatting
}
```

## Performance Optimization

### Large Datasets

```python
# For many metrics (>20), consider batching
def analyze_in_batches(all_metrics_data, batch_size=15):
    results = []
    metric_names = list(all_metrics_data.keys())

    for i in range(0, len(metric_names), batch_size):
        batch_names = metric_names[i:i+batch_size]
        batch_data = {k: all_metrics_data[k] for k in batch_names}

        analysis = detector.analyze_system(
            batch_data,
            batch_names,
            company,
            industry
        )
        results.append(analysis)

    return results

# For long time series (>60 points), consider sampling
def sample_time_series(time_series, target_points=24):
    if len(time_series) <= target_points:
        return time_series

    # Take every nth point
    step = len(time_series) // target_points
    return time_series[::step][:target_points]
```

### Async Execution

```python
import asyncio

async def parallel_analysis():
    # Run multiple analyses in parallel
    systems_task = systems_agent.execute(systems_input)
    momentum_task = asyncio.to_thread(
        momentum_engine.analyze_momentum,
        company, industry, metrics_data
    )

    systems_result, momentum_result = await asyncio.gather(
        systems_task,
        momentum_task
    )

    return systems_result, momentum_result

# Run
systems, momentum = asyncio.run(parallel_analysis())
```

## Troubleshooting

### Issue: No Causal Links Detected

**Cause**: Correlations too weak or data too noisy

**Solution**:
```python
# Lower correlation threshold
detector = FeedbackLoopDetector(min_correlation=0.3)

# Increase data points
# Use longer time series (24+ months instead of 12)

# Check for data issues
for metric, values in time_series_data.items():
    print(f"{metric}: mean={np.mean(values):.2f}, std={np.std(values):.2f}")
```

### Issue: No Feedback Loops Found

**Cause**: Not enough interconnected metrics

**Solution**:
```python
# Add more related metrics
# Ensure metrics that should be related are included
# Example: revenue + customer_satisfaction + brand_value (creates loop)

# Check causal links first
links = detector.detect_causal_links(data, metrics)
print(f"Found {len(links)} causal links")
# Need at least 3-4 links to form a loop
```

### Issue: Low Momentum Scores

**Cause**: Metrics declining or flat growth

**Solution**:
```python
# Check individual metric contributions
for metric in analysis.key_metrics:
    print(f"{metric.metric_name}: {metric.contribution_to_flywheel:.0f}/100")
    print(f"  Velocity: {metric.velocity:.2f}")
    print(f"  Acceleration: {metric.acceleration:.2f}")

# Focus on improving metrics with negative acceleration
```

### Issue: Agent Timeout

**Cause**: Too many metrics or complex analysis

**Solution**:
```python
# Increase timeout
agent = SystemsAgent(timeout=180)  # 3 minutes

# Reduce data complexity
# Use fewer metrics (<15) or shorter time series (<36 months)

# Use detector directly for more control
analysis = detector.analyze_system(data, metrics, company, industry)
```

## Best Practices

1. **Data Quality**: Ensure consistent, clean time series data
2. **Time Scale**: Use monthly data for 12-24 months (ideal)
3. **Metric Selection**: Include 8-15 related business metrics
4. **Correlation Threshold**: Start with 0.5, adjust based on results
5. **Validation**: Always check confidence scores
6. **Interpretation**: Consider system archetype and structural issues
7. **Action**: Focus on high-leverage, low-difficulty interventions
8. **Monitoring**: Track momentum trends over time
9. **Iteration**: Refine based on feedback and outcomes

## Resources

- **Source Code**: `consultantos/agents/systems_agent.py`, `consultantos/analysis/`
- **Tests**: `tests/test_phase3_intelligence.py`
- **Models**: `consultantos/models/systems.py`, `consultantos/models/momentum.py`
- **Summary**: `PHASE3_IMPLEMENTATION_SUMMARY.md`
