"""
Storytelling agent for AI-generated narratives and persona adaptation.
"""
import time
import logging
from typing import Dict, Any, Optional

from consultantos.agents.base_agent import BaseAgent
from consultantos.models.storytelling import (
    StorytellingResult,
    StorytellingRequest,
    Narrative,
    Persona,
    NarrativeType,
    PersonaAdaptationRequest,
    VisualizationEnhancementRequest,
    PresentationRequest
)
from consultantos.storytelling.narrative_generator import NarrativeGenerator
from consultantos.storytelling.viz_enhancer import VisualizationEnhancer
from consultantos.storytelling.presentation_generator import PresentationGenerator

logger = logging.getLogger(__name__)


class StorytellingAgent(BaseAgent):
    """
    Agent for generating data-driven narratives with persona adaptation.

    Orchestrates:
    - AI narrative generation from analysis data
    - Persona-based content adaptation
    - Visualization enhancement with annotations
    - Presentation slide generation
    """

    def __init__(self, timeout: int = 120):
        """
        Initialize storytelling agent.

        Args:
            timeout: Agent timeout in seconds (default: 120s for AI generation)
        """
        super().__init__(name="storytelling", timeout=timeout)

        # Initialize components
        self.narrative_generator = NarrativeGenerator()
        self.viz_enhancer = VisualizationEnhancer()
        self.presentation_generator = PresentationGenerator()

    async def execute(
        self,
        company: str,
        request: StorytellingRequest
    ) -> StorytellingResult:
        """
        Execute storytelling generation.

        Args:
            company: Company being analyzed
            request: Storytelling generation request

        Returns:
            Complete storytelling result with narrative and visualizations
        """
        start_time = time.time()
        logger.info(f"Generating storytelling content for {company} ({request.persona.value} persona)")

        try:
            # Step 1: Generate narrative(s)
            narratives = []
            for narrative_type in request.narrative_types:
                narrative = await self.narrative_generator.generate_narrative(
                    data=request.analysis_data,
                    persona=request.persona,
                    narrative_type=narrative_type,
                    focus_areas=request.focus_areas,
                    max_length_words=request.max_length_words,
                    tone=request.tone_preference
                )
                narratives.append(narrative)

            # Use the primary narrative (first one)
            primary_narrative = narratives[0]

            # Step 2: Enhance visualizations (if requested)
            enhanced_viz = []
            if request.include_visualizations:
                # Extract chart IDs from analysis data
                chart_ids = self._extract_chart_ids(request.analysis_data)

                if chart_ids:
                    annotations = await self.viz_enhancer.enhance_visualizations(
                        chart_ids=chart_ids,
                        analysis_data=request.analysis_data,
                        persona=request.persona,
                        max_annotations_per_chart=3
                    )
                    enhanced_viz = list(annotations.keys())

            # Step 3: Generate presentation (if requested)
            presentation_slides = []
            if request.include_presentation:
                prs, slides = await self.presentation_generator.generate_presentation(
                    narrative=primary_narrative,
                    max_slides=10,
                    template="professional",
                    include_charts=bool(enhanced_viz)
                )
                presentation_slides = slides

            # Build result
            result = StorytellingResult(
                narrative=primary_narrative,
                persona=request.persona,
                enhanced_visualizations=enhanced_viz,
                presentation_slides=presentation_slides,
                export_formats=self._determine_export_formats(request),
                generation_time_seconds=time.time() - start_time,
                metadata={
                    "company": company,
                    "narrative_types": [nt.value for nt in request.narrative_types],
                    "focus_areas": request.focus_areas,
                    "num_sections": len(primary_narrative.sections),
                    "num_insights": len(primary_narrative.key_insights),
                    "num_recommendations": len(primary_narrative.recommendations)
                }
            )

            logger.info(
                f"Generated storytelling content in {result.generation_time_seconds:.2f}s: "
                f"{len(result.narrative.sections)} sections, {len(result.enhanced_visualizations)} charts"
            )

            return result

        except Exception as e:
            logger.error(f"Storytelling generation failed: {str(e)}")
            raise

    async def adapt_for_persona(
        self,
        original_narrative: Narrative,
        target_persona: Persona,
        preserve_data: bool = True
    ) -> Narrative:
        """
        Adapt existing narrative for different persona.

        Args:
            original_narrative: Original narrative content
            target_persona: New target audience
            preserve_data: Keep same data references

        Returns:
            Adapted narrative
        """
        logger.info(
            f"Adapting narrative from {original_narrative.generated_for_persona.value} "
            f"to {target_persona.value}"
        )

        try:
            adapted = await self.narrative_generator.adapt_narrative_for_persona(
                original_narrative=original_narrative,
                target_persona=target_persona,
                preserve_data=preserve_data
            )

            return adapted

        except Exception as e:
            logger.error(f"Persona adaptation failed: {str(e)}")
            raise

    async def enhance_visualizations(
        self,
        request: VisualizationEnhancementRequest
    ) -> Dict[str, Any]:
        """
        Add annotations to visualizations.

        Args:
            request: Visualization enhancement request

        Returns:
            Dictionary of chart annotations
        """
        logger.info(f"Enhancing {len(request.chart_ids)} visualizations")

        try:
            annotations = await self.viz_enhancer.enhance_visualizations(
                chart_ids=request.chart_ids,
                analysis_data=request.analysis_data,
                persona=request.persona,
                annotation_types=request.annotation_types,
                max_annotations_per_chart=request.max_annotations_per_chart
            )

            return {
                "annotations": annotations,
                "chart_count": len(request.chart_ids),
                "total_annotations": sum(len(anns) for anns in annotations.values())
            }

        except Exception as e:
            logger.error(f"Visualization enhancement failed: {str(e)}")
            raise

    async def generate_presentation(
        self,
        request: PresentationRequest
    ) -> Dict[str, Any]:
        """
        Generate presentation slides.

        Args:
            request: Presentation generation request

        Returns:
            Presentation metadata
        """
        logger.info(f"Generating presentation with max {request.max_slides} slides")

        try:
            prs, slides = await self.presentation_generator.generate_presentation(
                narrative=request.narrative,
                max_slides=request.max_slides,
                template=request.template,
                brand_colors=request.brand_colors,
                include_charts=request.include_charts
            )

            return {
                "presentation": prs,
                "slides": slides,
                "slide_count": len(slides),
                "template": request.template
            }

        except Exception as e:
            logger.error(f"Presentation generation failed: {str(e)}")
            raise

    def _extract_chart_ids(self, analysis_data: Dict[str, Any]) -> list[str]:
        """Extract chart IDs from analysis data."""
        chart_ids = []

        # Check common locations for chart references
        if "charts" in analysis_data:
            if isinstance(analysis_data["charts"], dict):
                chart_ids.extend(analysis_data["charts"].keys())
            elif isinstance(analysis_data["charts"], list):
                chart_ids.extend([
                    c.get("id", f"chart_{i}")
                    for i, c in enumerate(analysis_data["charts"])
                ])

        # Check in visualizations
        if "visualizations" in analysis_data:
            if isinstance(analysis_data["visualizations"], list):
                chart_ids.extend([
                    v.get("id", f"viz_{i}")
                    for i, v in enumerate(analysis_data["visualizations"])
                ])

        # Generate default IDs if none found
        if not chart_ids:
            chart_ids = [f"chart_{i}" for i in range(3)]

        return chart_ids

    def _determine_export_formats(self, request: StorytellingRequest) -> list[str]:
        """Determine available export formats based on request."""
        formats = ["json"]  # Always available

        if request.include_presentation:
            formats.append("pptx")

        # PDF export from narrative
        formats.append("pdf")

        # Word document
        formats.append("docx")

        return formats

    async def _execute_internal(
        self,
        company: str,
        industry: str,
        **kwargs
    ) -> StorytellingResult:
        """
        Internal execution method required by BaseAgent.

        Args:
            company: Company name
            industry: Industry
            **kwargs: Additional parameters including request

        Returns:
            Storytelling result
        """
        # Extract request from kwargs or create default
        request = kwargs.get("request")
        if not request:
            # Create default request
            request = StorytellingRequest(
                analysis_data=kwargs.get("analysis_data", {}),
                persona=kwargs.get("persona", Persona.ANALYST),
                narrative_types=[NarrativeType.SUMMARY]
            )

        return await self.execute(company, request)
