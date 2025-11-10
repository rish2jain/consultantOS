"""
API endpoints for storytelling features.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import io

from consultantos.models.storytelling import (
    StorytellingRequest,
    StorytellingResult,
    PersonaAdaptationRequest,
    VisualizationEnhancementRequest,
    PresentationRequest,
    Narrative,
    Persona
)
from consultantos.agents.storytelling_agent import StorytellingAgent
from consultantos.auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/storytelling", tags=["storytelling"])


@router.post("/generate", response_model=StorytellingResult)
async def generate_storytelling(
    request: StorytellingRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user_optional)
) -> StorytellingResult:
    """
    Generate AI-powered narrative from analysis data.

    Creates persona-specific narratives with optional visualizations and presentation.

    **Args:**
    - `analysis_data`: Analysis results to create narrative from
    - `persona`: Target audience (executive, technical, sales, investor, analyst)
    - `narrative_types`: Types of narratives to generate (summary, trend, insight, etc.)
    - `include_visualizations`: Whether to enhance visualizations with annotations
    - `include_presentation`: Whether to generate PowerPoint slides
    - `tone_preference`: Optional tone override
    - `max_length_words`: Maximum narrative length (100-10000 words)
    - `focus_areas`: Specific topics to emphasize

    **Returns:**
    - Complete storytelling result with narrative, enhanced visualizations, and slides

    **Example:**
    ```json
    {
      "analysis_data": {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "insights": ["Growing market share", "Improving margins"],
        "charts": {
          "revenue_chart": {"type": "line", "data": [...]}
        }
      },
      "persona": "executive",
      "narrative_types": ["summary", "recommendation"],
      "include_visualizations": true,
      "include_presentation": true,
      "max_length_words": 1500,
      "focus_areas": ["ROI", "competitive advantage"]
    }
    ```
    """
    try:
        logger.info(f"Generating storytelling for {request.persona.value} persona")

        # Extract company from analysis data
        company = request.analysis_data.get("company", "Unknown Company")

        # Initialize agent
        agent = StorytellingAgent(timeout=120)

        # Generate storytelling
        result = await agent.execute(company=company, request=request)

        # Log for analytics (background task)
        background_tasks.add_task(
            _log_storytelling_generation,
            persona=request.persona,
            narrative_types=request.narrative_types,
            user=current_user
        )

        return result

    except Exception as e:
        logger.error(f"Storytelling generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate storytelling content: {str(e)}"
        )


@router.post("/adapt", response_model=Narrative)
async def adapt_narrative_for_persona(
    request: PersonaAdaptationRequest,
    current_user: str = Depends(get_current_user_optional)
) -> Narrative:
    """
    Adapt existing narrative for different persona.

    Re-writes content to match new audience's language, focus, and detail level.

    **Args:**
    - `original_narrative`: Original narrative to adapt
    - `target_persona`: New target audience
    - `preserve_data`: Keep same data references (recommended: true)
    - `adjust_tone`: Change tone to match persona (recommended: true)
    - `adjust_detail_level`: Change detail level (recommended: true)

    **Returns:**
    - Adapted narrative for new persona

    **Example:**
    ```json
    {
      "original_narrative": {...},
      "target_persona": "sales",
      "preserve_data": true,
      "adjust_tone": true,
      "adjust_detail_level": true
    }
    ```
    """
    try:
        logger.info(
            f"Adapting narrative from {request.original_narrative.generated_for_persona.value} "
            f"to {request.target_persona.value}"
        )

        # Initialize agent
        agent = StorytellingAgent()

        # Adapt narrative
        adapted = await agent.adapt_for_persona(
            original_narrative=request.original_narrative,
            target_persona=request.target_persona,
            preserve_data=request.preserve_data
        )

        return adapted

    except Exception as e:
        logger.error(f"Narrative adaptation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to adapt narrative: {str(e)}"
        )


@router.post("/enhance-viz", response_model=Dict[str, Any])
async def enhance_visualizations(
    request: VisualizationEnhancementRequest,
    current_user: str = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Add smart annotations to visualizations.

    Generates persona-specific annotations including callouts, trend lines, and highlights.

    **Args:**
    - `chart_ids`: List of chart IDs to annotate
    - `analysis_data`: Analysis context for annotations
    - `persona`: Target audience for annotation style
    - `annotation_types`: Types to generate (callout, arrow, highlight, trend_line)
    - `max_annotations_per_chart`: Maximum annotations per chart (1-10)

    **Returns:**
    - Dictionary of annotations by chart ID with metadata

    **Example:**
    ```json
    {
      "chart_ids": ["revenue_chart", "market_share_chart"],
      "analysis_data": {"company": "Tesla", "insights": [...]},
      "persona": "investor",
      "annotation_types": ["callout", "trend_line"],
      "max_annotations_per_chart": 5
    }
    ```
    """
    try:
        logger.info(f"Enhancing {len(request.chart_ids)} visualizations for {request.persona.value}")

        # Initialize agent
        agent = StorytellingAgent()

        # Enhance visualizations
        result = await agent.enhance_visualizations(request)

        return result

    except Exception as e:
        logger.error(f"Visualization enhancement failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance visualizations: {str(e)}"
        )


@router.post("/presentation")
async def generate_presentation(
    request: PresentationRequest,
    current_user: str = Depends(get_current_user_optional)
) -> StreamingResponse:
    """
    Generate PowerPoint presentation from narrative.

    Creates branded slide deck with narrative content and visualizations.

    **Args:**
    - `narrative`: Narrative content to convert to slides
    - `max_slides`: Maximum number of slides (3-50)
    - `include_charts`: Include chart placeholders
    - `template`: Presentation template (professional, modern, minimal, corporate)
    - `brand_colors`: Optional custom brand colors

    **Returns:**
    - PowerPoint file (PPTX format)

    **Example:**
    ```json
    {
      "narrative": {...},
      "max_slides": 10,
      "include_charts": true,
      "template": "professional",
      "brand_colors": {
        "primary": "#1976D2",
        "secondary": "#424242",
        "accent": "#F44336"
      }
    }
    ```
    """
    try:
        logger.info(f"Generating presentation with {request.max_slides} slides")

        # Initialize agent
        agent = StorytellingAgent()

        # Generate presentation
        result = await agent.generate_presentation(request)
        prs = result["presentation"]

        # Save to bytes buffer
        buffer = io.BytesIO()
        prs.save(buffer)
        buffer.seek(0)

        # Return as streaming response
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": "attachment; filename=presentation.pptx"
            }
        )

    except Exception as e:
        logger.error(f"Presentation generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate presentation: {str(e)}"
        )


@router.get("/personas")
async def get_available_personas() -> Dict[str, Any]:
    """
    Get available personas with their characteristics.

    Returns all supported personas and their focus areas, language, and preferences.

    **Returns:**
    - Dictionary of personas with traits and preferences

    **Example Response:**
    ```json
    {
      "executive": {
        "focus": ["ROI", "strategic impact", "competitive advantage"],
        "detail_level": "high-level",
        "language": "business outcomes"
      },
      "technical": {...}
    }
    ```
    """
    from consultantos.storytelling.personas import PERSONA_TRAITS

    return {
        persona.value: {
            "focus": traits["focus"],
            "detail_level": traits["detail_level"],
            "language": traits["language"],
            "tone": traits["tone"],
            "preferred_viz": traits["preferred_viz"]
        }
        for persona, traits in PERSONA_TRAITS.items()
    }


@router.get("/narrative-types")
async def get_narrative_types() -> Dict[str, str]:
    """
    Get available narrative types.

    Returns all supported narrative types with descriptions.

    **Returns:**
    - Dictionary of narrative types

    **Example Response:**
    ```json
    {
      "summary": "Executive summary of key findings",
      "trend": "Trend analysis and patterns",
      "insight": "Deep dive into specific insight",
      "recommendation": "Actionable recommendations"
    }
    ```
    """
    from consultantos.models.storytelling import NarrativeType

    return {
        "summary": "Executive summary highlighting most important findings and recommendations",
        "trend": "Analysis of key trends and patterns with significance and trajectory",
        "insight": "Specific key insight explained in depth with context and implications",
        "recommendation": "Actionable recommendations with clear rationale and expected outcomes",
        "comparison": "Comparison of different options, scenarios, or competitors",
        "forecast": "Future predictions based on current data and trends"
    }


async def _log_storytelling_generation(
    persona: Persona,
    narrative_types: list,
    user: str
) -> None:
    """Background task to log storytelling generation for analytics."""
    try:
        logger.info(
            f"Storytelling generated - User: {user}, Persona: {persona.value}, "
            f"Types: {[nt.value for nt in narrative_types]}"
        )
        # Could add to analytics database here

    except Exception as e:
        logger.warning(f"Failed to log storytelling generation: {str(e)}")
