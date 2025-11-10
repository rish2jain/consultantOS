"""
Tests for narrative generator with AI-powered content creation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from consultantos.storytelling.narrative_generator import NarrativeGenerator
from consultantos.models.storytelling import (
    Narrative,
    NarrativeSection,
    NarrativeType,
    Persona
)


@pytest.fixture
def narrative_generator():
    """Create narrative generator instance."""
    return NarrativeGenerator()


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing."""
    return {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "insights": [
            "Market share growing 15% YoY",
            "Profit margins improving to 25%",
            "Strong brand loyalty"
        ],
        "trends": {
            "revenue_growth": 0.35,
            "market_expansion": "global"
        },
        "charts": {
            "revenue_chart": {
                "type": "line",
                "data": [
                    {"year": 2020, "value": 31500},
                    {"year": 2021, "value": 53800},
                    {"year": 2022, "value": 81462},
                    {"year": 2023, "value": 96773}
                ]
            }
        }
    }


@pytest.mark.asyncio
async def test_generate_narrative_executive_persona(narrative_generator, sample_analysis_data):
    """Test narrative generation for executive persona."""
    with patch.object(narrative_generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
        # Mock response
        mock_narrative = Narrative(
            title="Tesla Strategic Analysis",
            subtitle="Executive Summary",
            sections=[
                NarrativeSection(
                    heading="Market Position",
                    content="Tesla maintains strong competitive advantage with 15% YoY growth.",
                    key_points=["Market leader", "Strong growth"]
                )
            ],
            key_insights=["Growing market share", "Improving margins"],
            recommendations=["Expand production capacity", "Invest in new markets"],
            tone="professional",
            length_words=250,
            confidence_score=0.85,
            generated_for_persona=Persona.EXECUTIVE
        )
        mock_create.return_value = mock_narrative

        # Generate narrative
        result = await narrative_generator.generate_narrative(
            data=sample_analysis_data,
            persona=Persona.EXECUTIVE,
            narrative_type=NarrativeType.SUMMARY,
            max_length_words=500
        )

        # Assertions
        assert result.title is not None
        assert result.generated_for_persona == Persona.EXECUTIVE
        assert len(result.sections) > 0
        assert len(result.key_insights) > 0
        assert result.confidence_score > 0
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_narrative_technical_persona(narrative_generator, sample_analysis_data):
    """Test narrative generation for technical persona."""
    with patch.object(narrative_generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
        mock_narrative = Narrative(
            title="Tesla Technical Analysis",
            sections=[
                NarrativeSection(
                    heading="Methodology",
                    content="Analysis conducted using time-series forecasting with 95% confidence intervals.",
                    key_points=["Statistical significance", "Data quality validated"]
                )
            ],
            key_insights=["Significant growth trend", "High data confidence"],
            recommendations=["Monitor key metrics", "Validate assumptions"],
            tone="analytical",
            length_words=800,
            confidence_score=0.9,
            generated_for_persona=Persona.TECHNICAL
        )
        mock_create.return_value = mock_narrative

        result = await narrative_generator.generate_narrative(
            data=sample_analysis_data,
            persona=Persona.TECHNICAL,
            narrative_type=NarrativeType.TREND
        )

        assert result.generated_for_persona == Persona.TECHNICAL
        assert "methodology" in result.sections[0].heading.lower() or "technical" in result.title.lower()
        assert result.length_words > 500  # Technical should be more detailed


@pytest.mark.asyncio
async def test_adapt_narrative_for_persona(narrative_generator):
    """Test adapting narrative from one persona to another."""
    # Original narrative for executives
    original = Narrative(
        title="Strategic Overview",
        subtitle="Executive Summary",
        sections=[
            NarrativeSection(
                heading="Business Impact",
                content="ROI increased by 35% with strategic market positioning.",
                key_points=["Strong ROI", "Market leadership"]
            )
        ],
        key_insights=["Excellent financial performance"],
        recommendations=["Continue expansion"],
        tone="professional",
        length_words=200,
        confidence_score=0.8,
        generated_for_persona=Persona.EXECUTIVE
    )

    with patch.object(narrative_generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
        # Mock adapted narrative for sales
        adapted_mock = Narrative(
            title="Customer Value Proposition",
            sections=[
                NarrativeSection(
                    heading="Competitive Advantages",
                    content="Our solution delivers 35% better ROI for customers through strategic positioning.",
                    key_points=["Customer ROI", "Competitive wins"]
                )
            ],
            key_insights=["Strong customer value delivery"],
            recommendations=["Emphasize ROI in sales conversations"],
            tone="persuasive",
            length_words=200,
            confidence_score=0.75,
            generated_for_persona=Persona.SALES
        )
        mock_create.return_value = adapted_mock

        # Adapt for sales persona
        result = await narrative_generator.adapt_narrative_for_persona(
            original_narrative=original,
            target_persona=Persona.SALES,
            preserve_data=True
        )

        assert result.generated_for_persona == Persona.SALES
        assert "customer" in result.title.lower() or "sales" in str(result.sections).lower()
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_key_insights(narrative_generator, sample_analysis_data):
    """Test extracting key insights from data."""
    with patch.object(narrative_generator.client.chat.completions, 'create', new_callable=MagicMock) as mock_create:
        # Mock response with insights
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '["Market share growing rapidly", "Profit margins improving", "Strong competitive position"]'
        mock_create.return_value = mock_response

        result = await narrative_generator.generate_key_insights(
            data=sample_analysis_data,
            persona=Persona.INVESTOR,
            max_insights=5
        )

        assert isinstance(result, list)
        assert len(result) <= 5
        assert all(isinstance(insight, str) for insight in result)


@pytest.mark.asyncio
async def test_fallback_narrative_on_error(narrative_generator, sample_analysis_data):
    """Test fallback narrative generation when AI fails."""
    with patch.object(narrative_generator.client.messages, 'create', side_effect=Exception("API Error")):
        result = await narrative_generator.generate_narrative(
            data=sample_analysis_data,
            persona=Persona.ANALYST,
            narrative_type=NarrativeType.SUMMARY
        )

        # Should return fallback narrative
        assert result.title is not None
        assert result.generated_for_persona == Persona.ANALYST
        assert len(result.sections) > 0
        assert result.confidence_score < 1.0  # Lower confidence for fallback


def test_prepare_data_summary(narrative_generator, sample_analysis_data):
    """Test data summary preparation."""
    summary = narrative_generator._prepare_data_summary(sample_analysis_data)

    assert isinstance(summary, str)
    assert "Tesla" in summary
    assert len(summary) > 0
    assert len(summary) <= 3000  # Respects max length


def test_format_sections_for_prompt(narrative_generator):
    """Test section formatting for prompts."""
    sections = [
        NarrativeSection(
            heading="Section 1",
            content="Content for section 1 " * 100,  # Long content
            key_points=["Point 1"]
        ),
        NarrativeSection(
            heading="Section 2",
            content="Content for section 2",
            key_points=["Point 2"]
        )
    ]

    formatted = narrative_generator._format_sections_for_prompt(sections)

    assert "Section 1" in formatted
    assert "Section 2" in formatted
    assert len(formatted) < len(sections[0].content) + len(sections[1].content)  # Truncated


@pytest.mark.asyncio
async def test_narrative_types_all_supported(narrative_generator, sample_analysis_data):
    """Test that all narrative types can be generated."""
    narrative_types = [
        NarrativeType.SUMMARY,
        NarrativeType.TREND,
        NarrativeType.INSIGHT,
        NarrativeType.RECOMMENDATION,
        NarrativeType.COMPARISON,
        NarrativeType.FORECAST
    ]

    for narrative_type in narrative_types:
        with patch.object(narrative_generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = Narrative(
                title=f"{narrative_type.value} Analysis",
                sections=[NarrativeSection(heading="Test", content="Test content")],
                key_insights=["Test insight"],
                recommendations=["Test recommendation"],
                tone="professional",
                length_words=100,
                confidence_score=0.8,
                generated_for_persona=Persona.ANALYST
            )

            result = await narrative_generator.generate_narrative(
                data=sample_analysis_data,
                persona=Persona.ANALYST,
                narrative_type=narrative_type
            )

            assert result is not None
            assert result.title is not None


@pytest.mark.asyncio
async def test_focus_areas_included_in_prompt(narrative_generator, sample_analysis_data):
    """Test that focus areas are included in generation prompt."""
    focus_areas = ["ROI", "Market share", "Competitive advantage"]

    with patch.object(narrative_generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = Narrative(
            title="Test",
            sections=[NarrativeSection(heading="Test", content="Test")],
            key_insights=[],
            recommendations=[],
            tone="professional",
            length_words=100,
            confidence_score=0.8,
            generated_for_persona=Persona.EXECUTIVE
        )

        await narrative_generator.generate_narrative(
            data=sample_analysis_data,
            persona=Persona.EXECUTIVE,
            narrative_type=NarrativeType.SUMMARY,
            focus_areas=focus_areas
        )

        # Check that prompt includes focus areas
        call_args = mock_create.call_args
        prompt = call_args[1]['messages'][0]['content']
        assert all(area in prompt for area in focus_areas)


def test_extract_basic_insights_fallback(narrative_generator):
    """Test fallback insight extraction."""
    data_with_insights = {
        "insights": ["Insight 1", "Insight 2", "Insight 3"],
        "key_findings": ["Finding 1", "Finding 2"]
    }

    result = narrative_generator._extract_basic_insights(data_with_insights, max_insights=3)

    assert len(result) <= 3
    assert "Insight 1" in result or "Finding 1" in result


def test_manual_adaptation_fallback(narrative_generator):
    """Test manual adaptation when AI adaptation fails."""
    original = Narrative(
        title="Original",
        sections=[NarrativeSection(heading="Test", content="Test")],
        key_insights=["Insight"],
        recommendations=["Rec"],
        tone="professional",
        length_words=100,
        confidence_score=0.9,
        generated_for_persona=Persona.EXECUTIVE
    )

    result = narrative_generator._manual_adaptation(original, Persona.TECHNICAL)

    assert result.generated_for_persona == Persona.TECHNICAL
    assert result.title == original.title
    assert result.confidence_score < original.confidence_score  # Reduced confidence
