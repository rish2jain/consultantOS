"""
Prompt templates for framework analysis
"""

PORTER_PROMPT_TEMPLATE = """
Analyze {company_name} in the {industry} industry using Porter's Five Forces framework.

Based on research data:
{research_summary}

Market data:
{market_summary}

Financial data:
{financial_summary}

Evaluate each force on a 1-5 scale (1=weak, 5=strong):

**1. SUPPLIER POWER** (1-5 score)
- How many suppliers does {company_name} depend on?
- Can {company_name} easily switch suppliers?
- What % of costs come from key suppliers?
- Are supplier inputs commoditized or specialized?

**2. BUYER POWER** (1-5 score)
- How concentrated are {company_name}'s customers?
- Do customers have alternative options?
- What are switching costs for customers?
- Is price a key buying factor?

**3. COMPETITIVE RIVALRY** (1-5 score)
- How many direct competitors?
- Market growth rate (growing markets = less rivalry)?
- Product differentiation level?
- Exit barriers (hard to leave = more rivalry)?

**4. THREAT OF SUBSTITUTES** (1-5 score)
- What alternative solutions exist?
- Switching costs for customers to substitutes?
- Performance/price comparison to substitutes?
- Substitute adoption trends?

**5. THREAT OF NEW ENTRANTS** (1-5 score)
- Capital requirements to enter industry?
- Regulatory barriers (licenses, approvals)?
- Brand loyalty / network effects?
- Economies of scale advantages?

**OVERALL COMPETITIVE INTENSITY**
Based on the 5 forces, assess overall intensity:
- Low (average score 1-2.5): Favorable industry structure
- Moderate (average score 2.5-3.5): Mixed competitive dynamics
- High (average score 3.5-5): Intense competition, margin pressure

**CRITICAL REQUIREMENTS**:
1. Every score must cite specific evidence (not "moderate competition exists")
2. Use numbers: market share %, growth rates, number of competitors
3. Compare to industry average (is this force stronger/weaker than typical?)
4. Link to strategic implications (so what? why does this matter?)
"""

SWOT_PROMPT_TEMPLATE = """
Perform SWOT analysis for {company_name}.

Based on:
- Research: {research_summary}
- Market: {market_summary}
- Financial: {financial_summary}

**STRENGTHS** (Internal, Positive)
Identify 3-5 strengths with SPECIFIC EVIDENCE:
- What does the company do exceptionally well?
- Unique resources or capabilities?
- Competitive advantages?
Example format: "97M US subscribers (40% streaming market share) vs Netflix 75M"
NOT: "Strong brand presence"

**WEAKNESSES** (Internal, Negative)
Identify 3-5 weaknesses with SPECIFIC EVIDENCE:
- What could be improved?
- Resource limitations?
- Areas where competitors are stronger?
Example format: "$15B debt (3.2x EBITDA) vs industry average 1.8x"
NOT: "High debt levels"

**OPPORTUNITIES** (External, Positive)
Identify 3-5 opportunities with SPECIFIC EVIDENCE:
- Market trends to capitalize on?
- Emerging customer needs?
- Partnership/expansion possibilities?

**THREATS** (External, Negative)
Identify 3-5 threats with SPECIFIC EVIDENCE:
- Competitive threats?
- Regulatory/economic risks?
- Technological disruption?

**CRITICAL**: Every item must include specific numbers, percentages, or comparisons.
"""

PESTEL_PROMPT_TEMPLATE = """
Analyze macro environment for {company_name} using PESTEL framework.

**POLITICAL**: Government policies, regulations, trade
**ECONOMIC**: GDP, inflation, interest rates, consumer spending
**SOCIAL**: Demographics, cultural trends, consumer behavior
**TECHNOLOGICAL**: Innovation, automation, digital transformation
**ENVIRONMENTAL**: Sustainability, climate, resource availability
**LEGAL**: Laws, compliance, intellectual property

For each category, identify 2-3 factors with:
- Factor description
- Impact on {company_name} (Positive/Negative/Neutral)
- Magnitude (Low/Medium/High)
- Evidence/Data
"""

BLUE_OCEAN_PROMPT_TEMPLATE = """
Apply Blue Ocean Strategy's Four Actions Framework to {company_name}.

Industry: {industry}
Current competitors: {competitors}

**ELIMINATE**: Which industry factors should be eliminated?
(Factors the industry competes on but add no value)

**REDUCE**: Which factors should be reduced below industry standard?
(Over-designed features, unnecessary costs)

**RAISE**: Which factors should be raised above industry standard?
(Differentiation opportunities)

**CREATE**: Which new factors should be created?
(Never offered by industry before)

For each action:
- Specific factor (not generic)
- Rationale (cost savings OR customer value)
- Estimated impact (Low/Medium/High)
Example: "ELIMINATE: Physical retail stores (Reduce overhead by $50M/year, customers prefer online)"
"""

SYNTHESIS_PROMPT_TEMPLATE = """
Create executive summary synthesizing all analysis:

**Research Findings**: {research_summary}
**Market Trends**: {market_summary}
**Financial Performance**: {financial_summary}
**Porter's 5 Forces**: {porter_summary}
**SWOT**: {swot_summary}

Your task:
1. Identify 3-5 KEY FINDINGS across all frameworks
2. Provide ONE PRIMARY STRATEGIC RECOMMENDATION
3. List 3-5 SUPPORTING EVIDENCE points
4. Suggest 3 NEXT STEPS for the company

Requirements:
- **Integrate across frameworks**: Show how insights connect
- **Prioritize**: Focus on highest-impact insights
- **Actionable**: Recommendations must be implementable
- **Confident**: Assess your confidence level (0-1) based on data quality

Format as professional executive summary suitable for C-suite presentation.
"""

