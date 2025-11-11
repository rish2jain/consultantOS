# Decision Intelligence Engine - Usage Guide

## Overview

The **DecisionIntelligenceEngine** transforms strategic framework analyses (Porter's Five Forces, SWOT, PESTEL, Blue Ocean Strategy) into actionable decision briefs with ROI models, prioritization, and implementation timelines.

## Key Features

### Framework Transformation
- **Porter's Five Forces** → Competitive positioning decisions
- **SWOT Analysis** → Exploitation/mitigation/pursuit/defense decisions
- **Blue Ocean Strategy** → Innovation and differentiation decisions
- **PESTEL Analysis** → Risk mitigation and opportunity capture

### Decision Models
Each decision includes:
- **2-4 Strategic Options** with detailed financial models
- **ROI Calculations**: Investment required, expected returns, payback periods
- **Risk Assessment**: Risk levels, mitigation strategies
- **Implementation Plans**: Timeline, phases, success metrics
- **Strategic Fit Scoring**: Alignment with company strategy (0-100)

### Prioritization Algorithm
```
Score = (Urgency × 0.4) + (Strategic Fit × 0.3) + (Success Probability × 0.2) + (ROI × 0.1)
```

## Basic Usage

### Step 1: Generate Framework Analysis

```python
from consultantos.agents import FrameworkAgent

# Run framework analysis first
framework_agent = FrameworkAgent()
framework_result = await framework_agent.execute({
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot", "blue_ocean"]
})

framework_analysis = framework_result  # FrameworkAnalysis object
```

### Step 2: Generate Decision Brief

```python
from consultantos.agents import DecisionIntelligenceEngine

# Initialize decision intelligence engine
decision_engine = DecisionIntelligenceEngine(timeout=120)

# Generate decision brief
decision_result = await decision_engine.execute({
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "framework_analysis": framework_analysis,
    "revenue": 81_000_000_000  # Optional: $81B annual revenue for ROI scaling
})

decision_brief = decision_result["data"]  # DecisionBrief object
```

### Step 3: Access Decision Brief

```python
# Top decisions (sorted by priority)
print(f"Total decisions: {decision_brief.decision_count}")
print(f"Critical decisions: {len(decision_brief.critical_decisions)}")
print(f"High priority decisions: {len(decision_brief.high_priority_decisions)}")

# Overall confidence
print(f"Confidence score: {decision_brief.confidence_score:.1f}%")

# Strategic themes
print(f"Strategic themes: {decision_brief.strategic_themes}")

# Resource conflicts
print(f"Resource conflicts: {decision_brief.resource_conflicts}")

# Top decision
top_decision = decision_brief.top_decision
print(f"\nTop Priority Decision: {top_decision.decision_question}")
print(f"Category: {top_decision.decision_category.value}")
print(f"Urgency: {top_decision.urgency.value}")
print(f"Stakes: {top_decision.stakes}")
```

## Detailed Decision Structure

### StrategicDecision Object

```python
decision = decision_brief.top_decision

# Decision metadata
print(f"ID: {decision.decision_id}")  # e.g., "DEC-PORTER-001"
print(f"Question: {decision.decision_question}")
print(f"Context: {decision.context}")
print(f"Stakes: {decision.stakes}")

# Urgency and category
print(f"Urgency: {decision.urgency.value}")  # CRITICAL/HIGH/MEDIUM/LOW
print(f"Category: {decision.decision_category.value}")  # market_entry, investment, etc.

# Framework source
print(f"Framework source: {decision.porter_analysis}")  # Framework-specific insights

# Options analysis
print(f"\nNumber of options: {len(decision.options)}")
for i, option in enumerate(decision.options, 1):
    print(f"\nOption {i}: {option.option_name}")
    print(f"  Investment: ${option.investment_required:,.0f}")
    print(f"  Annual Return: ${option.expected_annual_return:,.0f}")
    print(f"  ROI Multiple: {option.roi_multiple:.2f}x")
    print(f"  Payback: {option.payback_period_months} months")
    print(f"  Timeline: {option.timeline_days} days")
    print(f"  Success Probability: {option.success_probability:.1f}%")
    print(f"  Risk Level: {option.risk_level}")
    print(f"  Strategic Fit: {option.strategic_fit:.1f}/100")

# Recommended option
recommended = next(
    opt for opt in decision.options
    if opt.option_id == decision.recommended_option
)
print(f"\nRecommended: {recommended.option_name}")
print(f"Competitive advantage: {recommended.competitive_advantage}")

# Implementation details
print(f"\nImplementation steps:")
for step in recommended.implementation_steps:
    print(f"  - {step}")

# Risk assessment
print(f"\nRisks:")
for risk in recommended.risks:
    print(f"  - {risk}")

print(f"\nMitigation strategies:")
for strategy in recommended.mitigation_strategies:
    print(f"  - {strategy}")

# Success criteria
print(f"\nSuccess metrics:")
for metric in decision.success_metrics:
    print(f"  - {metric}")

# Key assumptions
print(f"\nKey assumptions:")
for assumption in decision.key_assumptions:
    print(f"  - {assumption}")
```

## Framework-Specific Decision Examples

### Porter's Five Forces Decisions

```python
# High supplier power (>3.5) → Supplier risk mitigation
# Decision categories: INVESTMENT
# Example options:
# 1. Vertical integration (acquire supplier capabilities)
# 2. Dual sourcing strategy (reduce dependency)
# 3. Long-term contracts with price caps

# High buyer power (>3.5) → Customer lock-in
# Decision categories: ORGANIZATIONAL
# Example options:
# 1. Build switching costs (platform lock-in)
# 2. Premium differentiation
# 3. Create ecosystem effects

# High rivalry (>4.0) → Differentiation
# Decision categories: PRODUCT_LAUNCH
# Example options:
# 1. Differentiation strategy
# 2. Cost leadership
# 3. Niche focus

# High substitutes (>3.5) → Innovation urgency
# Decision categories: TECHNOLOGY
# Example options:
# 1. Accelerated R&D
# 2. Ecosystem development
# 3. Price/value repositioning

# High entry threat (>3.5) → Moat building
# Decision categories: INVESTMENT
# Example options:
# 1. Scale advantages
# 2. IP and technology moats
# 3. Brand and loyalty programs
```

### SWOT Decisions

```python
# Strengths → Exploitation decisions
# Decision categories: MARKET_ENTRY
# Example options:
# 1. Geographic expansion
# 2. Premium pricing strategy
# 3. Adjacent market entry

# Weaknesses → Mitigation decisions
# Decision categories: ORGANIZATIONAL
# Example options:
# 1. Internal fix (process/tech/talent)
# 2. Strategic partnership or acquisition
# 3. Strategic repositioning

# Opportunities → Pursuit decisions
# Decision categories: GEOGRAPHIC_EXPANSION
# Example options:
# 1. Aggressive pursuit (first-mover)
# 2. Moderate approach (phased)
# 3. Cautious entry (pilot, learn, scale)

# Threats → Defense decisions
# Decision categories: INVESTMENT (CRITICAL urgency)
# Example options:
# 1. Proactive countermeasures
# 2. Defensive positioning
# 3. Strategic pivot
```

### Blue Ocean Strategy Decisions

```python
# Create factors → Innovation decisions
# Decision categories: PRODUCT_LAUNCH
# Example options:
# - Focus on unique value factors not offered by industry
# - Higher risk, transformational impact potential

# Raise factors → Investment decisions
# Decision categories: INVESTMENT
# Example options:
# - Significantly exceed industry standards
# - Premium pricing from superior value

# Eliminate factors → Cost optimization
# Decision categories: ORGANIZATIONAL
# Example options:
# - Remove factors customers don't value
# - Cost reduction while maintaining/growing revenue
```

## Integration Examples

### Example 1: Full Analysis Pipeline

```python
async def full_strategic_analysis(company: str, industry: str):
    """Complete strategic analysis with decision intelligence"""

    # Step 1: Framework analysis
    framework_agent = FrameworkAgent()
    framework_result = await framework_agent.execute({
        "company": company,
        "industry": industry,
        "frameworks": ["porter", "swot", "blue_ocean"]
    })

    # Step 2: Decision intelligence
    decision_engine = DecisionIntelligenceEngine()
    decision_result = await decision_engine.execute({
        "company": company,
        "industry": industry,
        "framework_analysis": framework_result,
        "revenue": 1_000_000_000  # Customize based on company size
    })

    decision_brief = decision_result["data"]

    # Step 3: Generate executive summary
    print(f"\n{'='*60}")
    print(f"DECISION INTELLIGENCE BRIEF: {company}")
    print(f"{'='*60}\n")

    print(f"Strategic Health: {decision_brief.confidence_score:.1f}%")
    print(f"Total Decisions: {decision_brief.decision_count}")
    print(f"  - Critical: {len(decision_brief.critical_decisions)}")
    print(f"  - High Priority: {len(decision_brief.high_priority_decisions)}")

    print(f"\nStrategic Themes:")
    for theme in decision_brief.strategic_themes:
        print(f"  • {theme}")

    if decision_brief.resource_conflicts:
        print(f"\nResource Conflicts:")
        for conflict in decision_brief.resource_conflicts:
            print(f"  ⚠️  {conflict}")

    # Step 4: Display top 3 decisions
    print(f"\n{'='*60}")
    print("TOP 3 PRIORITY DECISIONS")
    print(f"{'='*60}\n")

    all_decisions = (
        decision_brief.critical_decisions +
        decision_brief.high_priority_decisions
    )

    for i, decision in enumerate(all_decisions[:3], 1):
        print(f"\n{i}. {decision.decision_question}")
        print(f"   Category: {decision.decision_category.value}")
        print(f"   Urgency: {decision.urgency.value}")
        print(f"   Options: {len(decision.options)}")

        # Show recommended option ROI
        if decision.recommended_option:
            recommended = next(
                (opt for opt in decision.options
                 if opt.option_id == decision.recommended_option),
                None
            )
            if recommended:
                print(f"   Recommended: {recommended.option_name}")
                print(f"   ROI: {recommended.roi_multiple:.2f}x")
                print(f"   Payback: {recommended.payback_period_months} months")

    return decision_brief


# Usage
decision_brief = await full_strategic_analysis("Tesla", "Electric Vehicles")
```

### Example 2: Decision Comparison

```python
def compare_decision_options(decision: StrategicDecision):
    """Compare all options for a decision"""

    print(f"\nDECISION: {decision.decision_question}\n")
    print(f"{'Option':<30} {'Investment':<15} {'Return':<15} {'ROI':<10} {'Risk':<10}")
    print("-" * 80)

    for option in decision.options:
        print(
            f"{option.option_name:<30} "
            f"${option.investment_required/1e6:>6.1f}M      "
            f"${option.expected_annual_return/1e6:>6.1f}M      "
            f"{option.roi_multiple:>4.2f}x    "
            f"{option.risk_level:<10}"
        )

    # Highlight recommended
    if decision.recommended_option:
        recommended = next(
            opt for opt in decision.options
            if opt.option_id == decision.recommended_option
        )
        print(f"\n✅ RECOMMENDED: {recommended.option_name}")
        print(f"   Rationale: {recommended.competitive_advantage}")


# Usage
top_decision = decision_brief.top_decision
compare_decision_options(top_decision)
```

### Example 3: Portfolio ROI Analysis

```python
def analyze_decision_portfolio(decision_brief: DecisionBrief):
    """Analyze portfolio-level metrics"""

    all_decisions = (
        decision_brief.critical_decisions +
        decision_brief.high_priority_decisions
    )

    total_investment = 0
    total_return = 0

    print("\nPORTFOLIO ANALYSIS")
    print("=" * 60)

    for decision in all_decisions:
        if decision.recommended_option:
            recommended = next(
                (opt for opt in decision.options
                 if opt.option_id == decision.recommended_option),
                None
            )
            if recommended:
                total_investment += recommended.investment_required
                total_return += recommended.expected_annual_return

    portfolio_roi = total_return / total_investment if total_investment > 0 else 0

    print(f"Total Investment Required: ${total_investment/1e6:.1f}M")
    print(f"Expected Annual Return: ${total_return/1e6:.1f}M")
    print(f"Portfolio ROI: {portfolio_roi:.2f}x")
    print(f"Payback Period: ~{12/portfolio_roi:.0f} months")

    # Decision category breakdown
    print("\nDecision Breakdown by Category:")
    category_counts = {}
    for decision in all_decisions:
        cat = decision.decision_category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {cat.replace('_', ' ').title()}: {count}")


# Usage
analyze_decision_portfolio(decision_brief)
```

## Error Handling

```python
try:
    decision_result = await decision_engine.execute({
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "framework_analysis": framework_analysis
    })

    if decision_result["success"]:
        decision_brief = decision_result["data"]
        # Process decision brief
    else:
        print("Decision generation failed")

except ValueError as e:
    print(f"Invalid input: {e}")
except asyncio.TimeoutError:
    print("Decision generation timed out (exceeded 120 seconds)")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

### 1. Revenue Scaling
Provide accurate revenue for better ROI calculations:
```python
# For $81B company like Tesla
"revenue": 81_000_000_000

# For $5B mid-size company
"revenue": 5_000_000_000

# For $500M company
"revenue": 500_000_000
```

### 2. Framework Selection
Choose frameworks based on strategic needs:
```python
# For competitive positioning
"frameworks": ["porter", "blue_ocean"]

# For comprehensive analysis
"frameworks": ["porter", "swot", "pestel", "blue_ocean"]

# For internal focus
"frameworks": ["swot"]
```

### 3. Decision Filtering
Focus on most critical decisions:
```python
# Critical decisions only
critical_decisions = decision_brief.critical_decisions

# High urgency decisions (critical + high priority)
urgent_decisions = [
    d for d in all_decisions
    if d.urgency in [DecisionUrgency.CRITICAL, DecisionUrgency.HIGH]
]

# High ROI decisions
high_roi_decisions = [
    d for d in all_decisions
    if any(opt.roi_multiple > 2.0 for opt in d.options)
]
```

### 4. Time Management
Adjust timeout based on complexity:
```python
# Simple analysis (2-3 frameworks)
decision_engine = DecisionIntelligenceEngine(timeout=120)

# Complex analysis (all frameworks)
decision_engine = DecisionIntelligenceEngine(timeout=180)
```

## Model Reference

### DecisionUrgency Enum
- `CRITICAL`: Immediate action required (0-30 days)
- `HIGH`: Action needed within weeks (30-90 days)
- `MEDIUM`: Action needed within months (90-180 days)
- `LOW`: Strategic consideration (180+ days)

### DecisionCategory Enum
- `MARKET_ENTRY`: New market or segment entry
- `PRODUCT_LAUNCH`: New product/service launch
- `PRICING`: Pricing strategy changes
- `PARTNERSHIP`: Strategic partnerships
- `ACQUISITION`: M&A opportunities
- `DIVESTITURE`: Asset/business unit sales
- `INVESTMENT`: Capital investment decisions
- `ORGANIZATIONAL`: Organizational/operational changes
- `TECHNOLOGY`: Technology investments
- `GEOGRAPHIC_EXPANSION`: Geographic market expansion

## Performance Metrics

Expected execution time:
- **Simple analysis** (1-2 frameworks): 30-60 seconds
- **Standard analysis** (3 frameworks): 60-90 seconds
- **Comprehensive analysis** (4 frameworks): 90-120 seconds

Token usage:
- **Per decision**: ~2,000-2,500 tokens (LLM generation)
- **Total for 5 decisions**: ~10,000-12,500 tokens

## Troubleshooting

### Issue: Low confidence scores
**Solution**: Ensure framework analysis has rich, detailed data
```python
# Provide comprehensive framework analysis
# Ensure research, market, financial agents ran successfully
```

### Issue: Few decisions generated
**Solution**: Framework scores may not trigger thresholds
```python
# Check framework scores:
# - Porter forces should have some >3.5 scores
# - SWOT should have strengths/weaknesses/opportunities/threats
# - Blue Ocean should have create/raise/eliminate/reduce factors
```

### Issue: Timeout errors
**Solution**: Increase timeout or reduce frameworks
```python
# Increase timeout
decision_engine = DecisionIntelligenceEngine(timeout=180)

# Or reduce frameworks
"frameworks": ["porter", "swot"]  # Instead of all 4
```

## Next Steps

After generating decision brief:
1. **Review critical decisions** with executive team
2. **Validate ROI assumptions** with finance team
3. **Assess resource availability** for recommended options
4. **Create implementation roadmap** for top priorities
5. **Track decision outcomes** and update models based on results

## Support

For issues or questions:
- Check model validation errors in logs
- Review framework analysis quality
- Ensure all required fields are populated
- Verify revenue scaling is appropriate for company size
