"""
Tests for storytelling agent.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from consultantos.agents.storytelling_agent import StorytellingAgent
from consultantos.models.storytelling import (
    StorytellingRequest,
    StorytellingResult,
    Narrative,
    NarrativeSection,
    NarrativeType,
    Persona,
    Slide
)


@pytest.fixture
def agent():
    """Create storytelling agent."""
    return StorytellingAgent(timeout=60)


@pytest.fixture
def sample_request():
    """Sample storytelling request."""
    return StorytellingRequest(
        analysis_data={
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "insights": ["Growing market share", "Improving margins"],
            "charts": {
                "revenue_chart": {"type": "line", "data": []},
                "market_chart": {"type": "bar", "data": []}
            }
        },
        persona=Persona.EXECUTIVE,
        narrative_types=[NarrativeType.SUMMARY],
        include_visualizations=True,
        include_presentation=False,
        max_length_words=1000
    )


@pytest.mark.asyncio
async def test_execute_generates_storytelling(agent, sample_request):
    """Test that agent executes and generates storytelling result."""
    with patch.object(agent.narrative_generator, 'generate_narrative', new_callable=AsyncMock) as mock_gen:
        # Mock narrative
        mock_gen.return_value = Narrative(
            title="Tesla Analysis",
            sections=[NarrativeSection(heading="Overview", content="Content")],
            key_insights=["Insight 1"],
            recommendations=["Rec 1"],
            tone="professional",
            length_words=500,
            confidence_score=0.85,
            generated_for_persona=Persona.EXECUTIVE
        )

        with patch.object(agent.viz_enhancer, 'enhance_visualizations', new_callable=AsyncMock) as mock_viz:
            mock_viz.return_value = {
                "revenue_chart": [],
                "market_chart": []
            }

            result = await agent.execute("Tesla", sample_request)

            assert isinstance(result, StorytellingResult)
            assert result.narrative.title == "Tesla Analysis"
            assert result.persona == Persona.EXECUTIVE
            assert len(result.enhanced_visualizations) == 2
            assert result.generation_time_seconds > 0


@pytest.mark.asyncio
async def test_execute_with_presentation(agent, sample_request):
    """Test storytelling with presentation generation."""
    sample_request.include_presentation = True

    with patch.object(agent.narrative_generator, 'generate_narrative', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = Narrative(
            title="Test",
            sections=[NarrativeSection(heading="Test", content="Test")],
            key_insights=[],
            recommendations=[],
            tone="professional",
            length_words=100,
            confidence_score=0.8,
            generated_for_persona=Persona.EXECUTIVE
        )

        with patch.object(agent.viz_enhancer, 'enhance_visualizations', new_callable=AsyncMock):
            with patch.object(agent.presentation_generator, 'generate_presentation', new_callable=AsyncMock) as mock_pres:
                mock_pres.return_value = (
                    MagicMock(),  # Presentation object
                    [Slide(slide_number=1, layout="title", title="Title", content=[])]
                )

                result = await agent.execute("Tesla", sample_request)

                assert len(result.presentation_slides) > 0
                assert "pptx" in result.export_formats


@pytest.mark.asyncio
async def test_execute_multiple_narrative_types(agent, sample_request):
    """Test generating multiple narrative types."""
    sample_request.narrative_types = [NarrativeType.SUMMARY, NarrativeType.RECOMMENDATION]

    with patch.object(agent.narrative_generator, 'generate_narrative', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = Narrative(
            title="Test",
            sections=[NarrativeSection(heading="Test", content="Test")],
            key_insights=[],
            recommendations=[],
            tone="professional",
            length_words=100,
            confidence_score=0.8,
            generated_for_persona=Persona.EXECUTIVE
        )

        with patch.object(agent.viz_enhancer, 'enhance_visualizations', new_callable=AsyncMock):
            result = await agent.execute("Tesla", sample_request)

            # Should call generate_narrative twice
            assert mock_gen.call_count == 2
            assert result.narrative is not None


@pytest.mark.asyncio
async def test_adapt_for_persona(agent):
    """Test persona adaptation."""
    original = Narrative(
        title="Executive Summary",
        sections=[NarrativeSection(heading="ROI", content="35% ROI increase")],
        key_insights=["Strong ROI"],
        recommendations=["Continue strategy"],
        tone="professional",
        length_words=200,
        confidence_score=0.9,
        generated_for_persona=Persona.EXECUTIVE
    )

    with patch.object(agent.narrative_generator, 'adapt_narrative_for_persona', new_callable=AsyncMock) as mock_adapt:
        mock_adapt.return_value = Narrative(
            title="Customer Value",
            sections=[NarrativeSection(heading="Benefits", content="35% better customer ROI")],
            key_insights=["Strong customer value"],
            recommendations=["Emphasize in sales"],
            tone="persuasive",
            length_words=200,
            confidence_score=0.85,
            generated_for_persona=Persona.SALES
        )

        result = await agent.adapt_for_persona(original, Persona.SALES)

        assert result.generated_for_persona == Persona.SALES
        mock_adapt.assert_called_once()


@pytest.mark.asyncio
async def test_enhance_visualizations(agent):
    """Test visualization enhancement."""
    from consultantos.models.storytelling import VisualizationEnhancementRequest

    request = VisualizationEnhancementRequest(
        chart_ids=["chart1", "chart2"],
        analysis_data={"company": "Tesla"},
        persona=Persona.INVESTOR,
        max_annotations_per_chart=5
    )

    with patch.object(agent.viz_enhancer, 'enhance_visualizations', new_callable=AsyncMock) as mock_enhance:
        mock_enhance.return_value = {
            "chart1": [MagicMock()],
            "chart2": [MagicMock(), MagicMock()]
        }

        result = await agent.enhance_visualizations(request)

        assert result["chart_count"] == 2
        assert result["total_annotations"] == 3
        mock_enhance.assert_called_once()


@pytest.mark.asyncio
async def test_generate_presentation(agent):
    """Test presentation generation."""
    from consultantos.models.storytelling import PresentationRequest

    narrative = Narrative(
        title="Test Presentation",
        sections=[NarrativeSection(heading="Slide 1", content="Content")],
        key_insights=["Insight"],
        recommendations=["Rec"],
        tone="professional",
        length_words=500,
        confidence_score=0.8,
        generated_for_persona=Persona.EXECUTIVE
    )

    request = PresentationRequest(
        narrative=narrative,
        max_slides=10,
        template="professional"
    )

    with patch.object(agent.presentation_generator, 'generate_presentation', new_callable=AsyncMock) as mock_pres:
        mock_pres.return_value = (
            MagicMock(),
            [
                Slide(slide_number=1, layout="title", title="Title", content=[]),
                Slide(slide_number=2, layout="title_content", title="Content", content=["Point 1"])
            ]
        )

        result = await agent.generate_presentation(request)

        assert result["slide_count"] == 2
        assert result["template"] == "professional"


def test_extract_chart_ids(agent):
    """Test chart ID extraction from analysis data."""
    # Dict format
    data1 = {"charts": {"chart1": {}, "chart2": {}}}
    ids1 = agent._extract_chart_ids(data1)
    assert "chart1" in ids1
    assert "chart2" in ids1

    # List format
    data2 = {"charts": [{"id": "chart_a"}, {"id": "chart_b"}]}
    ids2 = agent._extract_chart_ids(data2)
    assert "chart_a" in ids2
    assert "chart_b" in ids2

    # Visualizations
    data3 = {"visualizations": [{"id": "viz1"}, {"id": "viz2"}]}
    ids3 = agent._extract_chart_ids(data3)
    assert "viz1" in ids3

    # No charts - should generate defaults
    data4 = {"company": "Tesla"}
    ids4 = agent._extract_chart_ids(data4)
    assert len(ids4) > 0  # Default IDs


def test_determine_export_formats(agent, sample_request):
    """Test export format determination."""
    # Without presentation
    sample_request.include_presentation = False
    formats1 = agent._determine_export_formats(sample_request)
    assert "json" in formats1
    assert "pdf" in formats1
    assert "docx" in formats1
    assert "pptx" not in formats1

    # With presentation
    sample_request.include_presentation = True
    formats2 = agent._determine_export_formats(sample_request)
    assert "pptx" in formats2


@pytest.mark.asyncio
async def test_execute_internal(agent):
    """Test internal execution method."""
    request = StorytellingRequest(
        analysis_data={"company": "Tesla"},
        persona=Persona.ANALYST,
        narrative_types=[NarrativeType.SUMMARY]
    )

    with patch.object(agent, 'execute', new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = StorytellingResult(
            narrative=Narrative(
                title="Test",
                sections=[],
                key_insights=[],
                recommendations=[],
                tone="professional",
                length_words=100,
                confidence_score=0.8,
                generated_for_persona=Persona.ANALYST
            ),
            persona=Persona.ANALYST,
            enhanced_visualizations=[],
            presentation_slides=[],
            export_formats=["json"],
            generation_time_seconds=1.0,
            metadata={}
        )

        result = await agent._execute_internal(
            company="Tesla",
            industry="EV",
            request=request
        )

        assert result.persona == Persona.ANALYST
        mock_execute.assert_called_once()


@pytest.mark.asyncio
async def test_execute_without_visualizations(agent, sample_request):
    """Test execution without visualization enhancement."""
    sample_request.include_visualizations = False

    with patch.object(agent.narrative_generator, 'generate_narrative', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = Narrative(
            title="Test",
            sections=[],
            key_insights=[],
            recommendations=[],
            tone="professional",
            length_words=100,
            confidence_score=0.8,
            generated_for_persona=Persona.EXECUTIVE
        )

        result = await agent.execute("Tesla", sample_request)

        assert len(result.enhanced_visualizations) == 0


@pytest.mark.asyncio
async def test_execute_with_focus_areas(agent, sample_request):
    """Test execution with specific focus areas."""
    sample_request.focus_areas = ["ROI", "Market Share", "Competitive Advantage"]

    with patch.object(agent.narrative_generator, 'generate_narrative', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = Narrative(
            title="Test",
            sections=[],
            key_insights=[],
            recommendations=[],
            tone="professional",
            length_words=100,
            confidence_score=0.8,
            generated_for_persona=Persona.EXECUTIVE
        )

        with patch.object(agent.viz_enhancer, 'enhance_visualizations', new_callable=AsyncMock):
            await agent.execute("Tesla", sample_request)

            # Check that focus areas were passed
            call_args = mock_gen.call_args
            assert call_args[1]['focus_areas'] == sample_request.focus_areas


@pytest.mark.asyncio
async def test_error_handling(agent, sample_request):
    """Test error handling in agent execution."""
    with patch.object(agent.narrative_generator, 'generate_narrative', side_effect=Exception("Generation failed")):
        with pytest.raises(Exception) as exc_info:
            await agent.execute("Tesla", sample_request)

        assert "Generation failed" in str(exc_info.value)


def test_agent_initialization():
    """Test agent initialization."""
    agent = StorytellingAgent(timeout=180)

    assert agent.name == "storytelling"
    assert agent.timeout == 180
    assert agent.narrative_generator is not None
    assert agent.viz_enhancer is not None
    assert agent.presentation_generator is not None
