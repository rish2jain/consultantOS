"""
Persona system for audience-specific content adaptation.
"""
from typing import Dict, List, Any
from consultantos.models.storytelling import Persona


# Persona characteristics and preferences
PERSONA_TRAITS: Dict[Persona, Dict[str, Any]] = {
    Persona.EXECUTIVE: {
        "focus": [
            "ROI and financial impact",
            "Strategic implications",
            "Competitive advantage",
            "Risk mitigation",
            "Growth opportunities"
        ],
        "detail_level": "high-level",
        "preferred_viz": ["executive dashboard", "key metrics cards", "trend lines", "comparison charts"],
        "language": "business outcomes",
        "tone": "professional and concise",
        "avoid": ["technical jargon", "implementation details", "granular data"],
        "prioritize": ["bottom line", "market position", "strategic decisions"],
        "typical_questions": [
            "What's the ROI?",
            "How does this impact our competitive position?",
            "What are the risks?",
            "What's the strategic recommendation?"
        ],
        "content_structure": {
            "intro_length": "brief",
            "use_bullets": True,
            "include_recommendations": True,
            "max_paragraphs_per_section": 2
        }
    },

    Persona.TECHNICAL: {
        "focus": [
            "Methodology and approach",
            "Data accuracy and sources",
            "Technical implementation",
            "Algorithm details",
            "Statistical significance"
        ],
        "detail_level": "detailed",
        "preferred_viz": ["detailed charts", "data tables", "correlation matrices", "distribution plots"],
        "language": "technical precision",
        "tone": "analytical and thorough",
        "avoid": ["oversimplification", "vague claims", "missing citations"],
        "prioritize": ["data quality", "reproducibility", "technical accuracy"],
        "typical_questions": [
            "What's the methodology?",
            "What are the data sources?",
            "What's the confidence interval?",
            "How was this calculated?"
        ],
        "content_structure": {
            "intro_length": "comprehensive",
            "use_bullets": False,
            "include_recommendations": False,
            "max_paragraphs_per_section": 5
        }
    },

    Persona.SALES: {
        "focus": [
            "Customer benefits",
            "Market opportunities",
            "Competitive differentiation",
            "Value proposition",
            "Deal enablement"
        ],
        "detail_level": "moderate",
        "preferred_viz": ["comparison charts", "opportunity maps", "customer segments", "win/loss analysis"],
        "language": "customer value",
        "tone": "persuasive and practical",
        "avoid": ["technical complexity", "academic language", "abstract concepts"],
        "prioritize": ["customer pain points", "competitive wins", "tangible benefits"],
        "typical_questions": [
            "How does this help close deals?",
            "What's our competitive advantage?",
            "What do customers care about?",
            "What's the value proposition?"
        ],
        "content_structure": {
            "intro_length": "moderate",
            "use_bullets": True,
            "include_recommendations": True,
            "max_paragraphs_per_section": 3
        }
    },

    Persona.INVESTOR: {
        "focus": [
            "Financial performance",
            "Growth trajectory",
            "Market size and opportunity",
            "Risk factors",
            "Valuation drivers"
        ],
        "detail_level": "moderate",
        "preferred_viz": ["financial charts", "growth curves", "market sizing", "cohort analysis"],
        "language": "financial metrics",
        "tone": "data-driven and objective",
        "avoid": ["hype", "unsubstantiated claims", "missing financial context"],
        "prioritize": ["unit economics", "market dynamics", "scalability", "exit potential"],
        "typical_questions": [
            "What's the TAM/SAM?",
            "What are the unit economics?",
            "What's the growth rate?",
            "What are the key risks?"
        ],
        "content_structure": {
            "intro_length": "moderate",
            "use_bullets": True,
            "include_recommendations": True,
            "max_paragraphs_per_section": 3
        }
    },

    Persona.ANALYST: {
        "focus": [
            "Comprehensive analysis",
            "Industry trends",
            "Framework application",
            "Comparative insights",
            "Actionable recommendations"
        ],
        "detail_level": "detailed",
        "preferred_viz": ["all chart types", "frameworks diagrams", "trend analysis", "segmentation"],
        "language": "analytical frameworks",
        "tone": "balanced and thorough",
        "avoid": ["bias", "incomplete analysis", "missing context"],
        "prioritize": ["holistic view", "framework rigor", "actionable insights"],
        "typical_questions": [
            "What frameworks were applied?",
            "What are the key trends?",
            "How does this compare to benchmarks?",
            "What are the implications?"
        ],
        "content_structure": {
            "intro_length": "comprehensive",
            "use_bullets": True,
            "include_recommendations": True,
            "max_paragraphs_per_section": 4
        }
    }
}


def get_persona_traits(persona: Persona) -> Dict[str, Any]:
    """
    Get the traits and preferences for a specific persona.

    Args:
        persona: Target audience persona

    Returns:
        Dictionary of persona traits and preferences
    """
    return PERSONA_TRAITS.get(persona, PERSONA_TRAITS[Persona.ANALYST])


def get_persona_prompt_guidance(persona: Persona) -> str:
    """
    Generate prompt guidance for AI narrative generation based on persona.

    Args:
        persona: Target audience persona

    Returns:
        String with guidance for content generation
    """
    traits = get_persona_traits(persona)

    focus_items = "\n".join([f"- {item}" for item in traits["focus"]])
    avoid_items = "\n".join([f"- {item}" for item in traits["avoid"]])

    guidance = f"""
Content for {persona.value.upper()} persona:

FOCUS ON:
{focus_items}

AVOID:
{avoid_items}

STYLE:
- Language: {traits["language"]}
- Tone: {traits["tone"]}
- Detail level: {traits["detail_level"]}

STRUCTURE:
- Introduction: {traits["content_structure"]["intro_length"]}
- Use bullet points: {traits["content_structure"]["use_bullets"]}
- Max paragraphs per section: {traits["content_structure"]["max_paragraphs_per_section"]}
- Include recommendations: {traits["content_structure"]["include_recommendations"]}

PREFERRED VISUALIZATIONS:
{", ".join(traits["preferred_viz"])}
"""

    return guidance


def adapt_content_for_persona(
    original_content: str,
    original_persona: Persona,
    target_persona: Persona
) -> str:
    """
    Generate guidance for adapting content from one persona to another.

    Args:
        original_content: Original narrative content
        original_persona: Original target persona
        target_persona: New target persona

    Returns:
        Guidance string for content adaptation
    """
    original_traits = get_persona_traits(original_persona)
    target_traits = get_persona_traits(target_persona)

    adaptation = f"""
Adapt this content from {original_persona.value} to {target_persona.value} audience:

ORIGINAL FOCUS: {", ".join(original_traits["focus"][:3])}
NEW FOCUS: {", ".join(target_traits["focus"][:3])}

STYLE CHANGES:
- Language: {original_traits["language"]} → {target_traits["language"]}
- Detail level: {original_traits["detail_level"]} → {target_traits["detail_level"]}
- Tone: {original_traits["tone"]} → {target_traits["tone"]}

CONTENT ADJUSTMENTS:
1. Re-emphasize content around: {", ".join(target_traits["prioritize"])}
2. Remove or minimize: {", ".join(target_traits["avoid"])}
3. Adjust structure for {target_traits["content_structure"]["intro_length"]} introduction
4. {"Add" if target_traits["content_structure"]["include_recommendations"] else "Remove"} recommendations section
"""

    return adaptation


def get_visualization_preferences(persona: Persona) -> List[str]:
    """
    Get preferred visualization types for a persona.

    Args:
        persona: Target audience persona

    Returns:
        List of preferred visualization types
    """
    traits = get_persona_traits(persona)
    return traits["preferred_viz"]


def should_include_detail(persona: Persona, detail_type: str) -> bool:
    """
    Determine if a specific detail type should be included for a persona.

    Args:
        persona: Target audience persona
        detail_type: Type of detail (e.g., "methodology", "technical_specs", "financial_details")

    Returns:
        Boolean indicating whether to include the detail
    """
    traits = get_persona_traits(persona)

    # Map detail types to personas that want them
    detail_mapping = {
        "methodology": [Persona.TECHNICAL, Persona.ANALYST],
        "technical_specs": [Persona.TECHNICAL],
        "financial_details": [Persona.EXECUTIVE, Persona.INVESTOR, Persona.ANALYST],
        "implementation_details": [Persona.TECHNICAL],
        "customer_stories": [Persona.SALES, Persona.EXECUTIVE],
        "market_sizing": [Persona.INVESTOR, Persona.ANALYST],
        "competitive_comparison": [Persona.SALES, Persona.EXECUTIVE, Persona.ANALYST],
        "statistical_significance": [Persona.TECHNICAL, Persona.ANALYST]
    }

    return persona in detail_mapping.get(detail_type, [])
