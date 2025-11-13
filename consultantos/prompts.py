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

Social media signals:
{social_media_summary}

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

**ENHANCED ANALYSIS** (for detailed_analysis field):
For each force, provide:
- Barriers to entry (if applicable): specific barriers like capital requirements, regulations
- Recent competitors: any new entrants in last 2 years
- Switching costs: cost to switch suppliers/buyers
- Substitute technologies: emerging alternatives
- Competitive intensity indicators: battle zones, differentiation opportunities
- Strategic implications: 2-3 specific action items derived from this force
"""

SWOT_PROMPT_TEMPLATE = """
Perform SWOT analysis for {company_name}.

Based on:
- Research: {research_summary}
- Market: {market_summary}
- Financial: {financial_summary}
- Social Media: {social_media_summary}

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

**ENHANCED ANALYSIS** (for actionable strategies):
For each SWOT element, consider:
- Importance score (1-10): How critical is this element?
- Strategic implications: How to leverage strengths, address weaknesses, pursue opportunities, monitor threats
- Timeline: When should this be addressed? (immediate/short-term/medium-term/long-term)
- Impact level: High/Medium/Low impact on business

**STRATEGIC COMBINATIONS**:
- S+O: How can strengths be used to pursue opportunities?
- W+T: How can weaknesses be addressed to counter threats?
"""

PESTEL_PROMPT_TEMPLATE = """
Analyze macro environment for {company_name} using PESTEL framework.

Based on available data:
- Research: {research_summary}
- Market: {market_summary}
- Financial: {financial_summary}
- Social Media: {social_media_summary}

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

**ENHANCED ANALYSIS**:
For each PESTEL factor, also provide:
- Current state: Today's landscape
- Trend direction: Is this moving favorable or unfavorable?
- Timeline: How soon will changes matter? (immediate/6-12 months/12-24 months)
- Early warning signals: What to watch for
- Adaptation required: Specific adjustments needed
- Competitive advantage: How to turn threats into opportunities
- Risk score (0-10): Quantified risk level
"""

BLUE_OCEAN_PROMPT_TEMPLATE = """
Apply Blue Ocean Strategy's Four Actions Framework to {company_name}.

Industry: {industry}
Current competitors: {competitors}

Based on data:
- Research: {research_summary}
- Market: {market_summary}
- Financial: {financial_summary}
- Social Media: {social_media_summary}

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

**ENHANCED ANALYSIS**:
For each action, also provide:
- Implementation complexity: Low/Medium/High
- Timeline: When to implement (immediate/short-term/medium-term/long-term)
- Cost savings: If applicable, estimated savings
- Customer value: If applicable, value proposition created
- Strategic profile: Current vs future positioning
- Uncontested market space: Target customer segments for value innovation
- Risk assessment: Cannibalization risks, resource requirements
"""

SYNTHESIS_PROMPT_TEMPLATE = """
Create evidence-based executive summary synthesizing all analysis:

**Research Findings**: {research_summary}
**Market Trends**: {market_summary}
**Financial Performance**: {financial_summary}
**Social Media Signals**: {social_media_summary}
**Porter's 5 Forces**: {porter_summary}
**SWOT**: {swot_summary}

## CRITICAL EVIDENCE REQUIREMENTS

**For Market Position**:
- Provide SPECIFIC metric (market share %, revenue rank, user base)
- Include comparison to competitors or industry average
- State the time period and source

**For Each Key Finding**:
1. State the specific insight (min 30 words)
2. Confidence level (0-1) based on data quality
3. At least 2 supporting metrics with actual values/percentages
4. Which frameworks support this finding
5. Strategic implication (what action this drives)

**For Primary Recommendation**:
- Specific action to take (not generic "improve operations")
- Priority level with justification
- At least 2 rationale points with evidence
- Expected impact with quantified metric
- Implementation timeline (specific months/quarters)
- Resources required (budget range, team size, etc.)
- 2+ success metrics (KPIs with target values)
- At least 1 risk with likelihood (0-1) and impact (1-10)

**For Secondary Recommendations** (at least 2):
- Same structure as primary but can be more concise
- Must be distinct from primary recommendation

**For Data Quality Assessment**:
Rate each source 0-1:
- Research: Based on completeness of company info
- Market: Based on trend data availability
- Financial: Based on metrics coverage
- Frameworks: Based on analysis depth
- Social Media: Based on sentiment and engagement data

**UNACCEPTABLE GENERIC STATEMENTS TO AVOID**:
❌ "Strong market position" → ✅ "#2 in market with 28% share"
❌ "Growing revenue" → ✅ "Revenue grew 45% YoY to $1.2B"
❌ "Competitive threats exist" → ✅ "3 new entrants captured 12% share in 6 months"
❌ "Improve operations" → ✅ "Reduce fulfillment time by 2 days using automated warehouses"
❌ "Monitor competition" → ✅ "Track competitor pricing weekly, respond within 48 hours"

**Confidence Score Calculation**:
- 0.8-1.0: All data sources robust, consistent findings, high specificity
- 0.6-0.79: Most data available, some specifics, minor gaps
- 0.4-0.59: Moderate data, mixed specificity, notable gaps
- 0.2-0.39: Limited data, mostly generic, significant gaps
- 0.0-0.19: Minimal data, highly speculative

Format as data-driven executive briefing with evidence for every claim.
"""


# ============================================================================
# FEEDBACK-BASED LEARNING SYSTEM
# ============================================================================

def get_feedback_enhanced_prompt(base_prompt: str, framework: str, feedback_data: dict = None) -> str:
    """
    Enhance base prompt with feedback-based learning examples.
    
    Args:
        base_prompt: Original framework prompt template
        framework: Framework name (porter, swot, pestel, blue_ocean)
        feedback_data: Dict with 'negative_examples' and 'positive_examples' keys
        
    Returns:
        Enhanced prompt with learning examples
    """
    if not feedback_data:
        return base_prompt
    
    enhancements = []
    
    # Add negative examples (common errors to avoid)
    negative_examples = feedback_data.get('negative_examples', [])
    if negative_examples:
        neg_section = "\n**AVOID THESE COMMON ERRORS** (Based on user corrections):\n"
        for i, example in enumerate(negative_examples[:5], 1):  # Top 5
            neg_section += f"{i}. ❌ **{example['category'].upper()}**: {example['explanation']}\n"
            neg_section += f"   Bad: \"{example['original'][:100]}...\"\n"
            neg_section += f"   Better: \"{example['corrected'][:100]}...\"\n\n"
        enhancements.append(neg_section)
    
    # Add positive examples (high-quality insights)
    positive_examples = feedback_data.get('positive_examples', [])
    if positive_examples:
        pos_section = "\n**EXCELLENT INSIGHT EXAMPLES** (Highly rated by users):\n"
        for i, example in enumerate(positive_examples[:3], 1):  # Top 3
            pos_section += f"{i}. ✅ **Rating: {example['rating']}/5**\n"
            pos_section += f"   \"{example['text']}\"\n\n"
        enhancements.append(pos_section)
    
    # Add pattern-based recommendations
    recommendations = feedback_data.get('recommendations', [])
    if recommendations:
        rec_section = "\n**QUALITY GUIDELINES** (From feedback analysis):\n"
        for rec in recommendations[:5]:
            rec_section += f"• {rec}\n"
        enhancements.append(rec_section)
    
    # Combine base prompt with enhancements
    if enhancements:
        enhanced = base_prompt + "\n\n" + "".join(enhancements)
        return enhanced
    
    return base_prompt


# Negative examples template - populated by FeedbackProcessor
NEGATIVE_EXAMPLES_SECTION = """
**AVOID THESE COMMON ERRORS** (Based on user corrections):
{corrections_summary}

These are real mistakes identified by users in previous analyses.
Learn from these patterns and ensure your analysis avoids similar issues.
"""

# Positive examples template - populated by FeedbackProcessor
POSITIVE_EXAMPLES_SECTION = """
**EXCELLENT INSIGHT EXAMPLES** (Highly rated by users):
{high_rated_examples}

These insights received 4.5-5 star ratings. Use them as quality benchmarks.
Notice the specificity, evidence-based reasoning, and strategic relevance.
"""

# Quality guidelines template - populated by FeedbackProcessor
QUALITY_GUIDELINES_SECTION = """
**QUALITY GUIDELINES** (From feedback analysis):
{quality_guidelines}

These guidelines emerged from analyzing thousands of user feedback submissions.
Following these will significantly improve insight quality and user satisfaction.
"""


def build_corrections_summary(corrections: list) -> str:
    """
    Build formatted summary of common corrections.
    
    Args:
        corrections: List of InsightCorrection objects
        
    Returns:
        Formatted string for prompt injection
    """
    if not corrections:
        return "No corrections data available yet."
    
    summary_lines = []
    for i, correction in enumerate(corrections[:5], 1):  # Top 5 most common
        summary_lines.append(
            f"{i}. ❌ **{correction.error_category.value.upper()}** in {correction.section.upper()}:\n"
            f"   Problem: {correction.original_text[:150]}...\n"
            f"   Fix: {correction.corrected_text[:150]}...\n"
            f"   Lesson: {correction.explanation}\n"
        )
    
    return "\n".join(summary_lines)


def build_positive_examples(ratings: list) -> str:
    """
    Build formatted summary of high-rated insights.
    
    Args:
        ratings: List of InsightRating objects with high scores
        
    Returns:
        Formatted string for prompt injection
    """
    if not ratings:
        return "No high-rated examples available yet."
    
    examples = []
    for i, rating in enumerate(ratings[:3], 1):  # Top 3
        framework = rating.insight_id.split("_")[1] if "_" in rating.insight_id else "unknown"
        examples.append(
            f"{i}. ✅ **{framework.upper()}** - {rating.rating}/5 stars\n"
            f"   \"{rating.feedback_text}\"\n"
        )
    
    return "\n".join(examples)


def build_quality_guidelines(patterns: list) -> str:
    """
    Build quality guidelines from learning patterns.
    
    Args:
        patterns: List of LearningPattern objects
        
    Returns:
        Formatted string for prompt injection
    """
    if not patterns:
        return "• Provide specific, evidence-based insights\n• Include quantitative data where possible\n• Focus on strategic implications"
    
    guidelines = []
    
    # Categorize patterns by type
    factual_patterns = [p for p in patterns if "factual" in p.description.lower()]
    depth_patterns = [p for p in patterns if "depth" in p.description.lower()]
    relevance_patterns = [p for p in patterns if "relevance" in p.description.lower()]
    
    if factual_patterns:
        guidelines.append("• **Factual Accuracy**: Verify all data points against source material. Cross-check numerical claims.")
    
    if depth_patterns:
        guidelines.append("• **Analysis Depth**: Provide 3-4 supporting points for each major insight. Don't just state facts—explain implications.")
    
    if relevance_patterns:
        guidelines.append("• **Strategic Relevance**: Focus on insights that directly impact business strategy. Avoid tangential observations.")
    
    # Add general best practices
    guidelines.extend([
        "• **Specificity**: Use concrete examples and metrics rather than vague statements",
        "• **Comparisons**: Benchmark against competitors and industry averages",
        "• **Actionability**: Connect insights to strategic decisions or actions"
    ])
    
    return "\n".join(guidelines)


# Framework-specific enhancement functions
async def get_enhanced_porter_prompt(company: str, industry: str, research: str, market: str, financial: str, feedback_processor=None) -> str:
    """Get Porter's Five Forces prompt enhanced with feedback learning"""
    base_prompt = PORTER_PROMPT_TEMPLATE.format(
        company_name=company,
        industry=industry,
        research_summary=research,
        market_summary=market,
        financial_summary=financial
    )
    
    if not feedback_processor:
        return base_prompt
    
    # Get feedback-based improvements
    improvements = await feedback_processor.improve_prompts(framework="porter")
    
    return get_feedback_enhanced_prompt(base_prompt, "porter", improvements)


async def get_enhanced_swot_prompt(company: str, research: str, market: str, financial: str, feedback_processor=None) -> str:
    """Get SWOT prompt enhanced with feedback learning"""
    base_prompt = SWOT_PROMPT_TEMPLATE.format(
        company_name=company,
        research_summary=research,
        market_summary=market,
        financial_summary=financial
    )
    
    if not feedback_processor:
        return base_prompt
    
    improvements = await feedback_processor.improve_prompts(framework="swot")
    
    return get_feedback_enhanced_prompt(base_prompt, "swot", improvements)


async def get_enhanced_pestel_prompt(company: str, feedback_processor=None) -> str:
    """Get PESTEL prompt enhanced with feedback learning"""
    base_prompt = PESTEL_PROMPT_TEMPLATE.format(company_name=company)
    
    if not feedback_processor:
        return base_prompt
    
    improvements = await feedback_processor.improve_prompts(framework="pestel")
    
    return get_feedback_enhanced_prompt(base_prompt, "pestel", improvements)


async def get_enhanced_blue_ocean_prompt(company: str, industry: str, competitors: str, feedback_processor=None) -> str:
    """Get Blue Ocean prompt enhanced with feedback learning"""
    base_prompt = BLUE_OCEAN_PROMPT_TEMPLATE.format(
        company_name=company,
        industry=industry,
        competitors=competitors
    )
    
    if not feedback_processor:
        return base_prompt
    
    improvements = await feedback_processor.improve_prompts(framework="blue_ocean")
    
    return get_feedback_enhanced_prompt(base_prompt, "blue_ocean", improvements)