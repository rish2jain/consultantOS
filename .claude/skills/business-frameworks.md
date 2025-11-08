---
name: business-frameworks
description: Strategic business framework expert for Porter's 5 Forces, SWOT, Blue Ocean Strategy, Business Model Canvas, and competitive analysis with prompt templates and implementation patterns
category: skill
---

# Business Frameworks Expert

Expert implementation of strategic business frameworks for AI-powered business intelligence systems.

## Overview

Strategic frameworks provide structured approaches to analyzing companies, industries, and competitive dynamics. This skill provides battle-tested prompts, validation schemas, and implementation patterns for automated framework analysis.

## Core Frameworks

### 1. Porter's Five Forces

Analyzes industry structure and competitive intensity through five key forces.

#### Pydantic Schema

```python
from pydantic import BaseModel, Field
from typing import Dict

class PortersFiveForces(BaseModel):
    """Porter's Five Forces Analysis"""

    supplier_power: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Supplier bargaining power (1=weak, 5=strong)"
    )
    buyer_power: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Buyer bargaining power (1=weak, 5=strong)"
    )
    competitive_rivalry: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Intensity of competitive rivalry (1=weak, 5=strong)"
    )
    threat_of_substitutes: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Threat from substitute products (1=weak, 5=strong)"
    )
    threat_of_new_entrants: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Threat from new market entrants (1=weak, 5=strong)"
    )

    force_analyses: Dict[str, str] = Field(
        ...,
        description="Detailed 2-3 sentence analysis for each force"
    )

    overall_intensity: str = Field(
        ...,
        description="Overall competitive intensity: Low, Moderate, or High"
    )

    competitive_advantages: list[str] = Field(
        default_factory=list,
        description="Key competitive advantages identified"
    )

    strategic_recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable strategic recommendations"
    )
```

#### Prompt Template

```python
PORTER_PROMPT_TEMPLATE = """
Analyze {company_name} in the {industry} industry using Porter's Five Forces framework.

Context Data:
{context_data}

For each force, provide:
1. Score (1-5): 1=weak force, 5=strong force
2. Evidence: Specific data points supporting the score
3. Analysis: 2-3 sentences explaining the competitive dynamics

**1. SUPPLIER POWER**
Evaluate:
- Number and concentration of suppliers
- Uniqueness of supplier products/services
- Switching costs for the company
- Forward integration potential of suppliers
- Importance of volume to suppliers

Score: _/5
Evidence: [Specific examples]
Analysis: [Explanation with data]

**2. BUYER POWER**
Evaluate:
- Number and concentration of customers
- Volume of purchases by individual buyers
- Availability of substitute products
- Buyer price sensitivity
- Buyer information availability

Score: _/5
Evidence: [Specific examples]
Analysis: [Explanation with data]

**3. COMPETITIVE RIVALRY**
Evaluate:
- Number and diversity of competitors
- Industry growth rate
- Product/service differentiation
- Switching costs for customers
- Exit barriers

Score: _/5
Evidence: [Specific examples]
Analysis: [Explanation with data]

**4. THREAT OF SUBSTITUTES**
Evaluate:
- Availability of substitute products/services
- Relative price-performance of substitutes
- Switching costs to substitutes
- Buyer propensity to substitute

Score: _/5
Evidence: [Specific examples]
Analysis: [Explanation with data]

**5. THREAT OF NEW ENTRANTS**
Evaluate:
- Capital requirements
- Economies of scale
- Brand loyalty and switching costs
- Regulatory barriers
- Access to distribution channels
- Technology and patents

Score: _/5
Evidence: [Specific examples]
Analysis: [Explanation with data]

**OVERALL ASSESSMENT**
Based on all five forces, assess:
- Overall competitive intensity: Low / Moderate / High
- Key competitive advantages for {company_name}
- Strategic recommendations (3-5 specific actions)

Use this structure and provide detailed, evidence-based analysis.
"""
```

### 2. SWOT Analysis

Identifies internal Strengths/Weaknesses and external Opportunities/Threats.

#### Pydantic Schema

```python
class SWOTAnalysis(BaseModel):
    """SWOT Analysis Schema"""

    strengths: list[str] = Field(
        ...,
        min_items=3,
        max_items=7,
        description="Internal positive factors"
    )
    weaknesses: list[str] = Field(
        ...,
        min_items=3,
        max_items=7,
        description="Internal negative factors"
    )
    opportunities: list[str] = Field(
        ...,
        min_items=3,
        max_items=7,
        description="External positive factors"
    )
    threats: list[str] = Field(
        ...,
        min_items=3,
        max_items=7,
        description="External negative factors"
    )

    strategic_fit: str = Field(
        ...,
        description="How to leverage strengths and opportunities while mitigating weaknesses and threats"
    )

    priority_actions: list[str] = Field(
        ...,
        description="Top 3-5 priority actions based on SWOT"
    )
```

#### Prompt Template

```python
SWOT_PROMPT_TEMPLATE = """
Perform comprehensive SWOT analysis for {company_name}.

Research Data:
{research_data}

Financial Data:
{financial_data}

Market Data:
{market_data}

Provide 3-7 items per quadrant, prioritized by importance.

**STRENGTHS (Internal, Positive)**
What does {company_name} do exceptionally well?
- Unique resources or capabilities
- Competitive advantages (cost, quality, brand, technology)
- Strong financial position
- Skilled workforce or leadership
- Proprietary technology or IP

Examples with evidence:
1. [Strength]: [Supporting data/evidence]
2. ...

**WEAKNESSES (Internal, Negative)**
What could {company_name} improve?
- Resource limitations (financial, human, technological)
- Operational inefficiencies
- Product/service gaps
- Areas where competitors are stronger
- Organizational or cultural challenges

Examples with evidence:
1. [Weakness]: [Supporting data/evidence]
2. ...

**OPPORTUNITIES (External, Positive)**
What external trends can {company_name} capitalize on?
- Market growth trends
- Emerging customer needs or segments
- Technological advancements
- Regulatory/policy changes favoring the company
- Partnership or acquisition possibilities
- Geographic expansion

Examples with evidence:
1. [Opportunity]: [Supporting data/evidence]
2. ...

**THREATS (External, Negative)**
What external challenges does {company_name} face?
- Competitive threats (new entrants, aggressive competitors)
- Market decline or saturation
- Regulatory or economic risks
- Technological disruption
- Changing customer preferences
- Supply chain vulnerabilities

Examples with evidence:
1. [Threat]: [Supporting data/evidence]
2. ...

**STRATEGIC FIT**
How can {company_name}:
- Use strengths to capitalize on opportunities? (SO strategies)
- Use strengths to mitigate threats? (ST strategies)
- Overcome weaknesses to pursue opportunities? (WO strategies)
- Minimize weaknesses and avoid threats? (WT strategies)

**PRIORITY ACTIONS**
Based on SWOT, identify 3-5 highest priority strategic actions.
"""
```

### 3. Blue Ocean Strategy

Four Actions Framework (ERRC) for creating uncontested market space.

#### Pydantic Schema

```python
class BlueOceanStrategy(BaseModel):
    """Blue Ocean Strategy Analysis"""

    eliminate: list[str] = Field(
        ...,
        description="Factors to eliminate that industry takes for granted"
    )
    reduce: list[str] = Field(
        ...,
        description="Factors to reduce below industry standard"
    )
    raise_factors: list[str] = Field(
        ...,
        description="Factors to raise above industry standard",
        alias="raise"
    )
    create: list[str] = Field(
        ...,
        description="Factors to create that industry never offered"
    )

    value_curve_shift: str = Field(
        ...,
        description="How these actions reshape the value curve"
    )

    blue_ocean_opportunities: list[str] = Field(
        ...,
        description="Specific blue ocean opportunities identified"
    )

    class Config:
        populate_by_name = True
```

#### Prompt Template

```python
BLUE_OCEAN_PROMPT_TEMPLATE = """
Apply Blue Ocean Strategy's Four Actions Framework (ERRC) to {company_name}.

Industry: {industry}
Current competitors: {competitors}
Industry standards: {industry_standards}

The Four Actions Framework challenges industry logic to create blue oceans.

**ELIMINATE**
Which factors that the industry takes for granted should be eliminated?

Think about:
- Industry standards that add cost but little value
- Features customers don't actually use
- Competitive practices that are wasteful

For each factor:
- Factor name
- Why it should be eliminated
- Cost savings potential: Low / Medium / High
- Customer value impact: Negative / Neutral / Positive

Examples:
1. [Factor]: [Rationale] | Cost savings: [Level] | Value impact: [Impact]

**REDUCE**
Which factors should be reduced well below the industry standard?

Think about:
- Over-engineered features
- Excessive service levels
- Costly differentiation with limited value

For each factor:
- Factor name
- Target reduction level (e.g., "Reduce by 50%")
- Cost savings potential: Low / Medium / High
- Customer value impact: Acceptable / Negligible

Examples:
1. [Factor]: [Reduction target] | Cost savings: [Level] | Value impact: [Impact]

**RAISE**
Which factors should be raised well above the industry standard?

Think about:
- Under-delivered customer needs
- Emerging value drivers
- Differentiation opportunities

For each factor:
- Factor name
- Target increase level (e.g., "Raise to premium level")
- Cost increase: Low / Medium / High
- Customer value creation: Medium / High / Very High

Examples:
1. [Factor]: [Increase target] | Cost: [Level] | Value creation: [Level]

**CREATE**
Which factors should be created that the industry has never offered?

Think about:
- Unmet customer needs
- New sources of value
- Game-changing innovations

For each factor:
- Factor name
- What makes it unique
- Investment required: Low / Medium / High
- Market potential: Low / Medium / High / Breakthrough

Examples:
1. [Factor]: [Unique value] | Investment: [Level] | Potential: [Level]

**VALUE CURVE SHIFT**
Describe how these four actions would reshape the industry value curve and create a blue ocean.

**BLUE OCEAN OPPORTUNITIES**
Identify 3-5 specific blue ocean strategies {company_name} could pursue.
"""
```

### 4. Business Model Canvas

Nine building blocks of business model design.

#### Pydantic Schema

```python
class BusinessModelCanvas(BaseModel):
    """Business Model Canvas"""

    customer_segments: list[str] = Field(
        ...,
        description="Distinct groups of customers"
    )
    value_propositions: list[str] = Field(
        ...,
        description="Bundle of products/services creating value"
    )
    channels: list[str] = Field(
        ...,
        description="How company reaches customers"
    )
    customer_relationships: list[str] = Field(
        ...,
        description="Types of relationships with customer segments"
    )
    revenue_streams: list[str] = Field(
        ...,
        description="How company generates revenue"
    )
    key_resources: list[str] = Field(
        ...,
        description="Most important assets required"
    )
    key_activities: list[str] = Field(
        ...,
        description="Most important actions for success"
    )
    key_partnerships: list[str] = Field(
        ...,
        description="Network of suppliers and partners"
    )
    cost_structure: list[str] = Field(
        ...,
        description="Most important costs in business model"
    )

    business_model_strengths: list[str] = Field(
        default_factory=list,
        description="Strengths of current business model"
    )
    business_model_risks: list[str] = Field(
        default_factory=list,
        description="Risks or vulnerabilities in business model"
    )
```

## Framework Selection Logic

```python
def select_frameworks(analysis_type: str, industry: str) -> list[str]:
    """Select appropriate frameworks based on analysis type"""

    framework_map = {
        "competitive_analysis": [
            "porter_five_forces",
            "swot",
            "competitive_matrix"
        ],
        "strategic_planning": [
            "swot",
            "business_model_canvas",
            "blue_ocean"
        ],
        "market_entry": [
            "porter_five_forces",
            "blue_ocean",
            "market_segmentation"
        ],
        "innovation_strategy": [
            "blue_ocean",
            "business_model_canvas",
            "swot"
        ],
        "investment_due_diligence": [
            "porter_five_forces",
            "swot",
            "financial_analysis"
        ]
    }

    return framework_map.get(analysis_type, ["porter_five_forces", "swot"])
```

## Quality Validation

```python
from typing import Any

def validate_framework_output(
    framework_type: str,
    output: Any,
    min_quality_score: float = 0.7
) -> tuple[bool, float, list[str]]:
    """Validate framework analysis quality"""

    issues = []
    quality_score = 1.0

    if framework_type == "porter_five_forces":
        # Check scores are in range
        for force in ["supplier_power", "buyer_power", "competitive_rivalry",
                      "threat_of_substitutes", "threat_of_new_entrants"]:
            score = getattr(output, force)
            if not (1.0 <= score <= 5.0):
                issues.append(f"{force} score out of range: {score}")
                quality_score -= 0.2

        # Check analysis depth
        for force, analysis in output.force_analyses.items():
            if len(analysis.split()) < 20:
                issues.append(f"{force} analysis too brief")
                quality_score -= 0.1

        # Check evidence
        if not any(char.isdigit() for char in str(output.force_analyses)):
            issues.append("No quantitative evidence found")
            quality_score -= 0.15

    elif framework_type == "swot":
        # Check balance
        quadrants = {
            "strengths": len(output.strengths),
            "weaknesses": len(output.weaknesses),
            "opportunities": len(output.opportunities),
            "threats": len(output.threats)
        }

        # Each quadrant should have 3-7 items
        for quadrant, count in quadrants.items():
            if count < 3:
                issues.append(f"{quadrant} has too few items: {count}")
                quality_score -= 0.1
            elif count > 7:
                issues.append(f"{quadrant} has too many items: {count}")
                quality_score -= 0.05

        # Check specificity
        generic_terms = ["good", "bad", "strong", "weak", "better"]
        for items in [output.strengths, output.weaknesses,
                      output.opportunities, output.threats]:
            for item in items:
                if any(term in item.lower() for term in generic_terms):
                    quality_score -= 0.02

    return (quality_score >= min_quality_score, quality_score, issues)
```

## Visualization Helpers

```python
import plotly.graph_objects as go

def create_porter_radar(forces: PortersFiveForces) -> str:
    """Create Porter's 5 Forces radar chart"""

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
            'Threat of<br>New Entrants'
        ],
        fill='toself',
        fillcolor='rgba(0, 123, 255, 0.3)',
        line=dict(color='rgba(0, 123, 255, 1)', width=2)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['1<br>Weak', '2', '3', '4', '5<br>Strong']
            )
        ),
        title={
            'text': "Porter's Five Forces Analysis",
            'font': {'size': 20, 'color': '#333'}
        },
        showlegend=False,
        height=500,
        width=600
    ))

    return fig.to_html(include_plotlyjs='cdn')


def create_swot_matrix(swot: SWOTAnalysis) -> str:
    """Create SWOT matrix visualization"""

    # Create 2x2 grid
    fig = go.Figure()

    # Define quadrants
    quadrants = [
        {
            "x": 0.25, "y": 0.75,
            "title": "STRENGTHS",
            "items": swot.strengths,
            "color": "#4CAF50"
        },
        {
            "x": 0.75, "y": 0.75,
            "title": "WEAKNESSES",
            "items": swot.weaknesses,
            "color": "#FF9800"
        },
        {
            "x": 0.25, "y": 0.25,
            "title": "OPPORTUNITIES",
            "items": swot.opportunities,
            "color": "#2196F3"
        },
        {
            "x": 0.75, "y": 0.25,
            "title": "THREATS",
            "items": swot.threats,
            "color": "#F44336"
        }
    ]

    for quad in quadrants:
        # Format items (show first 3)
        items_text = "<br>".join([f"• {item[:50]}..."
                                  for item in quad["items"][:3]])

        fig.add_trace(go.Scatter(
            x=[quad["x"]],
            y=[quad["y"]],
            text=[f"<b>{quad['title']}</b><br><br>{items_text}"],
            mode='text',
            textposition='middle center',
            textfont=dict(size=10, color=quad["color"]),
            showlegend=False
        ))

    fig.update_layout(
        title="SWOT Analysis Matrix",
        xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        shapes=[
            # Vertical line
            dict(type="line", x0=0.5, x1=0.5, y0=0, y1=1,
                 line=dict(color="gray", width=2)),
            # Horizontal line
            dict(type="line", x0=0, x1=1, y0=0.5, y1=0.5,
                 line=dict(color="gray", width=2))
        ],
        height=500,
        width=700
    )

    return fig.to_html(include_plotlyjs='cdn')
```

## Best Practices

### 1. Provide Rich Context

```python
# BAD: Minimal context
prompt = PORTER_PROMPT_TEMPLATE.format(
    company_name="Tesla",
    industry="Automotive",
    context_data="Tesla makes electric cars"
)

# GOOD: Rich, specific context
context_data = f"""
Company: Tesla Inc (TSLA)
Industry: Electric Vehicles / Automotive

Financial Metrics:
- Revenue: $96.8B (2023), +19% YoY
- Market Cap: $800B
- Gross Margin: 18.2%

Market Position:
- EV Market Share: 20% globally, 50%+ in US
- Production: 1.8M vehicles (2023)
- Key Models: Model 3, Y, S, X, Cybertruck

Competitors:
- Traditional: GM, Ford, VW, Toyota
- EV Pure-plays: Rivian, Lucid, NIO
- Chinese: BYD, XPeng, Li Auto

Recent Developments:
- Gigafactory expansion in Texas, Berlin
- Price cuts in Q1 2024 to maintain market share
- Full Self-Driving rollout ongoing
"""

prompt = PORTER_PROMPT_TEMPLATE.format(
    company_name="Tesla",
    industry="Electric Vehicles",
    context_data=context_data
)
```

### 2. Chain Frameworks Sequentially

```python
async def comprehensive_analysis(company: str, industry: str):
    # 1. Porter's 5 Forces (industry structure)
    porter = await framework_agent.execute_porter(company, industry)

    # 2. SWOT (company-specific strengths/weaknesses)
    swot = await framework_agent.execute_swot(
        company,
        industry,
        porter_context=porter  # Use Porter findings
    )

    # 3. Blue Ocean (strategic opportunities)
    blue_ocean = await framework_agent.execute_blue_ocean(
        company,
        industry,
        competitive_context=porter,  # Use Porter findings
        strengths=swot.strengths  # Use SWOT strengths
    )

    return {
        "porter": porter,
        "swot": swot,
        "blue_ocean": blue_ocean
    }
```

### 3. Validate and Iterate

```python
async def execute_with_validation(
    framework_type: str,
    prompt: str,
    max_iterations: int = 3
):
    for iteration in range(max_iterations):
        result = await agent.execute(prompt)

        is_valid, quality_score, issues = validate_framework_output(
            framework_type,
            result
        )

        if is_valid:
            return result

        # Refine prompt with issues
        prompt = f"{prompt}\n\nPrevious attempt had issues: {issues}\nPlease address these."

    return result  # Return best attempt
```

## Integration Example

Complete integration with Google ADK:

```python
from google.genai import adk
import instructor
from pydantic import BaseModel

# Framework analyst agent
framework_agent = adk.Agent(
    name="framework_analyst",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are a strategic framework expert.
    Apply business frameworks with precision and evidence.
    Provide structured, actionable analysis.
    """,
    temperature=0.7
)

async def analyze_with_frameworks(
    company: str,
    industry: str,
    context_data: str
):
    # Porter's 5 Forces
    porter_prompt = PORTER_PROMPT_TEMPLATE.format(
        company_name=company,
        industry=industry,
        context_data=context_data
    )

    porter_analysis = await framework_agent.execute(
        porter_prompt,
        response_model=PortersFiveForces
    )

    # SWOT Analysis
    swot_prompt = SWOT_PROMPT_TEMPLATE.format(
        company_name=company,
        research_data=context_data,
        financial_data="...",
        market_data="..."
    )

    swot_analysis = await framework_agent.execute(
        swot_prompt,
        response_model=SWOTAnalysis
    )

    # Validate
    porter_valid, porter_score, porter_issues = validate_framework_output(
        "porter_five_forces",
        porter_analysis
    )

    swot_valid, swot_score, swot_issues = validate_framework_output(
        "swot",
        swot_analysis
    )

    return {
        "porter": {
            "analysis": porter_analysis,
            "quality_score": porter_score,
            "issues": porter_issues
        },
        "swot": {
            "analysis": swot_analysis,
            "quality_score": swot_score,
            "issues": swot_issues
        }
    }
```

This skill provides production-ready implementation of strategic business frameworks for AI-powered analysis systems.
