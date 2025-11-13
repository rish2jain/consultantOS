"""
Visualization enhancer for adding smart annotations and highlights to charts.
"""
import logging
from typing import Dict, Any, List, Optional
import instructor
import google.generativeai as genai

from consultantos.models.storytelling import (
    ChartAnnotation,
    Persona,
    VisualizationEnhancementRequest
)
from consultantos.storytelling.personas import get_persona_traits
from consultantos.config import settings

logger = logging.getLogger(__name__)


class AnnotationSuggestion:
    """Suggested annotation for a chart."""
    chart_id: str
    annotation_type: str
    position: Dict[str, float]
    text: str
    importance: int


class VisualizationEnhancer:
    """
    Enhances visualizations with intelligent annotations and highlights.
    Adapts annotation style and content based on target persona.
    """

    def __init__(self):
        """Initialize visualization enhancer."""
        genai.configure(api_key=settings.gemini_api_key)
        gemini_model = genai.GenerativeModel(
            model_name=settings.gemini_model or "gemini-2.5-flash"  # Updated: gemini-1.5-flash-002 is no longer available
        )
        self.client = instructor.from_gemini(
            client=gemini_model,
            mode=instructor.Mode.GEMINI_JSON,
        )
        self.model = settings.gemini_model or "gemini-2.5-flash"  # Updated: gemini-1.5-flash-002 is no longer available

    async def enhance_visualizations(
        self,
        chart_ids: List[str],
        analysis_data: Dict[str, Any],
        persona: Persona,
        annotation_types: Optional[List[str]] = None,
        max_annotations_per_chart: int = 5
    ) -> Dict[str, List[ChartAnnotation]]:
        """
        Generate smart annotations for visualizations.

        Args:
            chart_ids: List of chart IDs to annotate
            analysis_data: Analysis data providing context
            persona: Target audience persona
            annotation_types: Types to generate (callout, arrow, highlight, trend_line)
            max_annotations_per_chart: Maximum annotations per chart

        Returns:
            Dictionary mapping chart IDs to annotation lists
        """
        logger.info(f"Enhancing {len(chart_ids)} visualizations for {persona.value} persona")

        annotations_by_chart = {}

        for chart_id in chart_ids:
            try:
                annotations = await self._generate_chart_annotations(
                    chart_id=chart_id,
                    analysis_data=analysis_data,
                    persona=persona,
                    annotation_types=annotation_types or ["callout", "trend_line", "highlight"],
                    max_annotations=max_annotations_per_chart
                )
                annotations_by_chart[chart_id] = annotations

            except Exception as e:
                logger.error(f"Failed to generate annotations for {chart_id}: {str(e)}")
                annotations_by_chart[chart_id] = []

        return annotations_by_chart

    async def _generate_chart_annotations(
        self,
        chart_id: str,
        analysis_data: Dict[str, Any],
        persona: Persona,
        annotation_types: List[str],
        max_annotations: int
    ) -> List[ChartAnnotation]:
        """Generate annotations for a specific chart."""
        persona_traits = get_persona_traits(persona)

        # Build prompt for annotation generation
        prompt = f"""
Generate smart annotations for chart "{chart_id}" for {persona.value} audience.

CHART CONTEXT:
{self._get_chart_context(chart_id, analysis_data)}

ANNOTATION TYPES TO USE:
{", ".join(annotation_types)}

PERSONA FOCUS:
{", ".join(persona_traits["focus"][:3])}

REQUIREMENTS:
- Generate up to {max_annotations} annotations
- Prioritize most important insights
- Use {persona_traits["language"]} language
- Annotation types available:
  * callout: Text pointing to important data point
  * arrow: Directional indicator for trends
  * highlight: Emphasize specific area or value
  * trend_line: Show overall direction

For each annotation provide:
- Type (from above)
- Text (brief, {persona.value}-relevant)
- Importance (1-5, 5 = most important)
- Approximate position (if known)

Return as JSON array of annotation objects.
"""

        try:
            # In a real implementation, this would use the Gemini API
            # For now, create rule-based annotations
            annotations = self._create_rule_based_annotations(
                chart_id=chart_id,
                analysis_data=analysis_data,
                persona=persona,
                annotation_types=annotation_types,
                max_annotations=max_annotations
            )

            return annotations

        except Exception as e:
            logger.error(f"Failed to generate annotations: {str(e)}")
            return []

    def _get_chart_context(self, chart_id: str, analysis_data: Dict[str, Any]) -> str:
        """Extract relevant context for a chart from analysis data."""
        context_parts = []

        # Look for chart-specific data
        if "charts" in analysis_data and chart_id in analysis_data["charts"]:
            chart_data = analysis_data["charts"][chart_id]
            context_parts.append(f"Chart type: {chart_data.get('type', 'unknown')}")
            context_parts.append(f"Data points: {len(chart_data.get('data', []))}")

        # Look for related insights
        if "insights" in analysis_data:
            for insight in analysis_data["insights"]:
                if chart_id in str(insight):
                    context_parts.append(f"Insight: {insight}")

        return "\n".join(context_parts) if context_parts else "No specific context available"

    def _create_rule_based_annotations(
        self,
        chart_id: str,
        analysis_data: Dict[str, Any],
        persona: Persona,
        annotation_types: List[str],
        max_annotations: int
    ) -> List[ChartAnnotation]:
        """
        Create annotations using rule-based logic as fallback.
        In production, this would be AI-generated.
        """
        annotations = []
        persona_traits = get_persona_traits(persona)

        # Extract chart data
        chart_data = self._extract_chart_data(chart_id, analysis_data)

        if not chart_data:
            return annotations

        # Generate annotations based on data patterns
        if "callout" in annotation_types and len(annotations) < max_annotations:
            # Highlight max value
            max_annotation = self._create_max_value_annotation(
                chart_id, chart_data, persona_traits
            )
            if max_annotation:
                annotations.append(max_annotation)

        if "trend_line" in annotation_types and len(annotations) < max_annotations:
            # Add trend indicator
            trend_annotation = self._create_trend_annotation(
                chart_id, chart_data, persona_traits
            )
            if trend_annotation:
                annotations.append(trend_annotation)

        if "highlight" in annotation_types and len(annotations) < max_annotations:
            # Highlight significant changes
            change_annotation = self._create_change_annotation(
                chart_id, chart_data, persona_traits
            )
            if change_annotation:
                annotations.append(change_annotation)

        return annotations[:max_annotations]

    def _extract_chart_data(
        self,
        chart_id: str,
        analysis_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract data for a specific chart."""
        if "charts" in analysis_data and chart_id in analysis_data["charts"]:
            return analysis_data["charts"][chart_id]

        # Try to find in nested structures
        for key, value in analysis_data.items():
            if isinstance(value, dict) and chart_id in value:
                return value[chart_id]

        return None

    def _create_max_value_annotation(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        persona_traits: Dict[str, Any]
    ) -> Optional[ChartAnnotation]:
        """Create annotation for maximum value."""
        try:
            data_points = chart_data.get("data", [])
            if not data_points:
                return None

            # Find max value
            max_val = max(data_points, key=lambda x: x.get("value", 0))

            # Persona-specific messaging
            if "ROI" in persona_traits["focus"][0]:
                text = f"Peak: ${max_val.get('value', 0):,.0f}"
            else:
                text = f"Highest: {max_val.get('value', 0)}"

            return ChartAnnotation(
                chart_id=chart_id,
                annotation_type="callout",
                text=text,
                importance=5,
                color="#4CAF50"
            )

        except Exception as e:
            logger.warning(f"Failed to create max value annotation: {str(e)}")
            return None

    def _create_trend_annotation(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        persona_traits: Dict[str, Any]
    ) -> Optional[ChartAnnotation]:
        """Create annotation for trend direction."""
        try:
            data_points = chart_data.get("data", [])
            if len(data_points) < 2:
                return None

            # Calculate trend
            first_val = data_points[0].get("value", 0)
            last_val = data_points[-1].get("value", 0)
            change_pct = ((last_val - first_val) / first_val * 100) if first_val != 0 else 0

            # Determine direction and message
            if change_pct > 5:
                direction = "↗"
                color = "#4CAF50"
                text = f"Growing {abs(change_pct):.1f}%"
            elif change_pct < -5:
                direction = "↘"
                color = "#F44336"
                text = f"Declining {abs(change_pct):.1f}%"
            else:
                direction = "→"
                color = "#FFC107"
                text = "Stable trend"

            return ChartAnnotation(
                chart_id=chart_id,
                annotation_type="trend_line",
                text=f"{direction} {text}",
                importance=4,
                color=color
            )

        except Exception as e:
            logger.warning(f"Failed to create trend annotation: {str(e)}")
            return None

    def _create_change_annotation(
        self,
        chart_id: str,
        chart_data: Dict[str, Any],
        persona_traits: Dict[str, Any]
    ) -> Optional[ChartAnnotation]:
        """Create annotation for significant changes."""
        try:
            data_points = chart_data.get("data", [])
            if len(data_points) < 2:
                return None

            # Find largest change
            max_change = 0
            max_change_idx = 0

            for i in range(1, len(data_points)):
                prev_val = data_points[i - 1].get("value", 0)
                curr_val = data_points[i].get("value", 0)

                if prev_val != 0:
                    change = abs((curr_val - prev_val) / prev_val)
                    if change > max_change:
                        max_change = change
                        max_change_idx = i

            if max_change > 0.1:  # 10% change threshold
                return ChartAnnotation(
                    chart_id=chart_id,
                    annotation_type="highlight",
                    text=f"Significant shift: {max_change * 100:.0f}%",
                    importance=4,
                    color="#FF9800"
                )

        except Exception as e:
            logger.warning(f"Failed to create change annotation: {str(e)}")
            return None

    async def add_persona_specific_highlights(
        self,
        chart_id: str,
        persona: Persona,
        data: Dict[str, Any]
    ) -> List[ChartAnnotation]:
        """
        Add highlights specifically relevant to a persona's interests.

        Args:
            chart_id: Chart to annotate
            persona: Target audience
            data: Chart and analysis data

        Returns:
            List of persona-specific annotations
        """
        persona_traits = get_persona_traits(persona)
        highlights = []

        # Persona-specific annotation logic
        if persona == Persona.EXECUTIVE:
            # Focus on ROI, strategic impact
            highlights.extend(self._create_executive_highlights(chart_id, data))

        elif persona == Persona.TECHNICAL:
            # Focus on methodology, accuracy
            highlights.extend(self._create_technical_highlights(chart_id, data))

        elif persona == Persona.SALES:
            # Focus on customer value, competitive wins
            highlights.extend(self._create_sales_highlights(chart_id, data))

        elif persona == Persona.INVESTOR:
            # Focus on growth, market opportunity
            highlights.extend(self._create_investor_highlights(chart_id, data))

        return highlights

    def _create_executive_highlights(
        self,
        chart_id: str,
        data: Dict[str, Any]
    ) -> List[ChartAnnotation]:
        """Create executive-focused highlights."""
        return [
            ChartAnnotation(
                chart_id=chart_id,
                annotation_type="callout",
                text="Strategic opportunity",
                importance=5,
                color="#9C27B0"
            )
        ]

    def _create_technical_highlights(
        self,
        chart_id: str,
        data: Dict[str, Any]
    ) -> List[ChartAnnotation]:
        """Create technical-focused highlights."""
        return [
            ChartAnnotation(
                chart_id=chart_id,
                annotation_type="callout",
                text="95% confidence",
                importance=3,
                color="#2196F3"
            )
        ]

    def _create_sales_highlights(
        self,
        chart_id: str,
        data: Dict[str, Any]
    ) -> List[ChartAnnotation]:
        """Create sales-focused highlights."""
        return [
            ChartAnnotation(
                chart_id=chart_id,
                annotation_type="callout",
                text="Customer pain point",
                importance=5,
                color="#FF5722"
            )
        ]

    def _create_investor_highlights(
        self,
        chart_id: str,
        data: Dict[str, Any]
    ) -> List[ChartAnnotation]:
        """Create investor-focused highlights."""
        return [
            ChartAnnotation(
                chart_id=chart_id,
                annotation_type="callout",
                text="Market opportunity",
                importance=5,
                color="#00BCD4"
            )
        ]
