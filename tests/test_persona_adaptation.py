"""
Tests for persona-specific content adaptation.
"""
import pytest
from consultantos.storytelling.personas import (
    PERSONA_TRAITS,
    get_persona_traits,
    get_persona_prompt_guidance,
    adapt_content_for_persona,
    get_visualization_preferences,
    should_include_detail
)
from consultantos.models.storytelling import Persona


def test_all_personas_have_traits():
    """Test that all personas have complete trait definitions."""
    required_keys = [
        "focus", "detail_level", "preferred_viz", "language",
        "tone", "avoid", "prioritize", "typical_questions", "content_structure"
    ]

    for persona in Persona:
        traits = PERSONA_TRAITS[persona]
        for key in required_keys:
            assert key in traits, f"Persona {persona} missing trait: {key}"

        # Verify content structure
        assert "intro_length" in traits["content_structure"]
        assert "use_bullets" in traits["content_structure"]
        assert "include_recommendations" in traits["content_structure"]
        assert "max_paragraphs_per_section" in traits["content_structure"]


def test_get_persona_traits():
    """Test retrieving persona traits."""
    # Valid persona
    traits = get_persona_traits(Persona.EXECUTIVE)
    assert traits is not None
    assert "focus" in traits
    assert "ROI" in str(traits["focus"])

    # Technical persona
    tech_traits = get_persona_traits(Persona.TECHNICAL)
    assert "methodology" in str(tech_traits["focus"]).lower()
    assert tech_traits["detail_level"] == "detailed"


def test_executive_persona_characteristics():
    """Test executive persona has appropriate characteristics."""
    traits = get_persona_traits(Persona.EXECUTIVE)

    assert traits["detail_level"] == "high-level"
    assert "ROI" in str(traits["focus"])
    assert "technical jargon" in traits["avoid"]
    assert traits["content_structure"]["use_bullets"] is True
    assert traits["content_structure"]["max_paragraphs_per_section"] <= 3


def test_technical_persona_characteristics():
    """Test technical persona has appropriate characteristics."""
    traits = get_persona_traits(Persona.TECHNICAL)

    assert traits["detail_level"] == "detailed"
    assert "methodology" in str(traits["focus"]).lower()
    assert "oversimplification" in traits["avoid"]
    assert traits["content_structure"]["max_paragraphs_per_section"] >= 4


def test_sales_persona_characteristics():
    """Test sales persona has appropriate characteristics."""
    traits = get_persona_traits(Persona.SALES)

    assert "customer" in str(traits["focus"]).lower()
    assert "value proposition" in str(traits["focus"]).lower()
    assert "technical complexity" in traits["avoid"]
    assert traits["tone"] == "persuasive and practical"


def test_investor_persona_characteristics():
    """Test investor persona has appropriate characteristics."""
    traits = get_persona_traits(Persona.INVESTOR)

    assert "financial" in str(traits["focus"]).lower()
    assert "growth" in str(traits["focus"]).lower()
    assert "hype" in traits["avoid"]
    assert traits["language"] == "financial metrics"


def test_analyst_persona_characteristics():
    """Test analyst persona has appropriate characteristics."""
    traits = get_persona_traits(Persona.ANALYST)

    assert "comprehensive" in str(traits["focus"]).lower()
    assert "frameworks" in str(traits["focus"]).lower()
    assert "bias" in traits["avoid"]
    assert traits["content_structure"]["include_recommendations"] is True


def test_get_persona_prompt_guidance():
    """Test prompt guidance generation for personas."""
    guidance = get_persona_prompt_guidance(Persona.EXECUTIVE)

    assert "EXECUTIVE" in guidance
    assert "FOCUS ON" in guidance
    assert "AVOID" in guidance
    assert "STYLE" in guidance
    assert "STRUCTURE" in guidance

    # Check persona-specific content
    assert "ROI" in guidance or "strategic" in guidance.lower()
    assert "technical jargon" in guidance


def test_prompt_guidance_all_personas():
    """Test that prompt guidance can be generated for all personas."""
    for persona in Persona:
        guidance = get_persona_prompt_guidance(persona)

        assert len(guidance) > 100  # Substantial guidance
        assert persona.value.upper() in guidance
        assert "FOCUS ON" in guidance
        assert "AVOID" in guidance


def test_adapt_content_for_persona():
    """Test content adaptation guidance generation."""
    adaptation = adapt_content_for_persona(
        original_content="Strategic analysis for executives",
        original_persona=Persona.EXECUTIVE,
        target_persona=Persona.TECHNICAL
    )

    assert "EXECUTIVE" in adaptation.lower()
    assert "TECHNICAL" in adaptation.lower()
    assert "ORIGINAL FOCUS" in adaptation
    assert "NEW FOCUS" in adaptation
    assert "STYLE CHANGES" in adaptation


def test_adaptation_guidance_focus_changes():
    """Test that adaptation guidance highlights focus changes."""
    # Executive to Sales
    exec_to_sales = adapt_content_for_persona(
        original_content="Test",
        original_persona=Persona.EXECUTIVE,
        target_persona=Persona.SALES
    )

    assert "customer" in exec_to_sales.lower() or "value" in exec_to_sales.lower()

    # Technical to Investor
    tech_to_investor = adapt_content_for_persona(
        original_content="Test",
        original_persona=Persona.TECHNICAL,
        target_persona=Persona.INVESTOR
    )

    assert "financial" in tech_to_investor.lower() or "growth" in tech_to_investor.lower()


def test_get_visualization_preferences():
    """Test visualization preference retrieval."""
    # Executive preferences
    exec_prefs = get_visualization_preferences(Persona.EXECUTIVE)
    assert "executive dashboard" in exec_prefs or "key metrics" in str(exec_prefs).lower()

    # Technical preferences
    tech_prefs = get_visualization_preferences(Persona.TECHNICAL)
    assert "data tables" in str(tech_prefs).lower() or "detailed" in str(tech_prefs).lower()

    # Analyst preferences
    analyst_prefs = get_visualization_preferences(Persona.ANALYST)
    assert "all chart types" in str(analyst_prefs).lower() or "frameworks" in str(analyst_prefs).lower()


def test_should_include_detail():
    """Test detail inclusion logic for personas."""
    # Methodology details
    assert should_include_detail(Persona.TECHNICAL, "methodology") is True
    assert should_include_detail(Persona.ANALYST, "methodology") is True
    assert should_include_detail(Persona.EXECUTIVE, "methodology") is False
    assert should_include_detail(Persona.SALES, "methodology") is False

    # Financial details
    assert should_include_detail(Persona.EXECUTIVE, "financial_details") is True
    assert should_include_detail(Persona.INVESTOR, "financial_details") is True
    assert should_include_detail(Persona.TECHNICAL, "financial_details") is False

    # Technical specs
    assert should_include_detail(Persona.TECHNICAL, "technical_specs") is True
    assert should_include_detail(Persona.EXECUTIVE, "technical_specs") is False
    assert should_include_detail(Persona.SALES, "technical_specs") is False

    # Customer stories
    assert should_include_detail(Persona.SALES, "customer_stories") is True
    assert should_include_detail(Persona.EXECUTIVE, "customer_stories") is True
    assert should_include_detail(Persona.TECHNICAL, "customer_stories") is False

    # Market sizing
    assert should_include_detail(Persona.INVESTOR, "market_sizing") is True
    assert should_include_detail(Persona.ANALYST, "market_sizing") is True
    assert should_include_detail(Persona.TECHNICAL, "market_sizing") is False


def test_detail_inclusion_consistency():
    """Test that detail inclusion is consistent with persona traits."""
    for persona in Persona:
        traits = get_persona_traits(persona)

        # Technical details should align with detail level
        if traits["detail_level"] == "detailed":
            # Detailed personas should include methodology
            include_methodology = should_include_detail(persona, "methodology")
            # This is a heuristic, not strict requirement
            assert include_methodology or persona == Persona.INVESTOR  # Investor focuses on financial


def test_persona_differentiation():
    """Test that personas are clearly differentiated."""
    # Get traits for all personas
    all_traits = {persona: get_persona_traits(persona) for persona in Persona}

    # Check that focus areas are different
    focus_sets = [set(str(traits["focus"])) for traits in all_traits.values()]

    # At least some differentiation in focus
    assert len(set(map(frozenset, focus_sets))) > 1

    # Check that avoided topics are different
    avoid_sets = [set(traits["avoid"]) for traits in all_traits.values()]
    assert len(set(map(frozenset, avoid_sets))) > 1


def test_content_structure_variations():
    """Test that content structures vary by persona."""
    structures = {
        persona: get_persona_traits(persona)["content_structure"]
        for persona in Persona
    }

    # Detail levels should vary
    max_paragraphs = [s["max_paragraphs_per_section"] for s in structures.values()]
    assert max(max_paragraphs) > min(max_paragraphs)

    # Intro lengths should vary
    intro_lengths = [s["intro_length"] for s in structures.values()]
    assert len(set(intro_lengths)) > 1


def test_prompt_guidance_length():
    """Test that prompt guidance is substantial for all personas."""
    for persona in Persona:
        guidance = get_persona_prompt_guidance(persona)

        # Should be detailed enough to be useful
        assert len(guidance) > 200
        assert guidance.count('\n') > 10  # Multiple sections


def test_persona_traits_completeness():
    """Test that all required traits are present and valid."""
    for persona in Persona:
        traits = get_persona_traits(persona)

        # List fields should have content
        assert len(traits["focus"]) >= 3
        assert len(traits["avoid"]) >= 2
        assert len(traits["prioritize"]) >= 2
        assert len(traits["typical_questions"]) >= 2
        assert len(traits["preferred_viz"]) >= 2

        # String fields should be non-empty
        assert len(traits["detail_level"]) > 0
        assert len(traits["language"]) > 0
        assert len(traits["tone"]) > 0

        # Content structure should be valid
        cs = traits["content_structure"]
        assert cs["intro_length"] in ["brief", "moderate", "comprehensive"]
        assert isinstance(cs["use_bullets"], bool)
        assert isinstance(cs["include_recommendations"], bool)
        assert 1 <= cs["max_paragraphs_per_section"] <= 10


@pytest.mark.parametrize("original_persona,target_persona", [
    (Persona.EXECUTIVE, Persona.TECHNICAL),
    (Persona.EXECUTIVE, Persona.SALES),
    (Persona.TECHNICAL, Persona.EXECUTIVE),
    (Persona.SALES, Persona.INVESTOR),
    (Persona.INVESTOR, Persona.ANALYST)
])
def test_all_persona_adaptations(original_persona, target_persona):
    """Test that adaptations can be generated for all persona pairs."""
    adaptation = adapt_content_for_persona(
        original_content="Test content",
        original_persona=original_persona,
        target_persona=target_persona
    )

    assert original_persona.value in adaptation.lower()
    assert target_persona.value in adaptation.lower()
    assert len(adaptation) > 100  # Substantial guidance
