"""
AI-powered narrative generator for creating compelling data stories.
"""
import json
import logging
from typing import Dict, Any, List, Optional
import instructor
import google.generativeai as genai

from consultantos.models.storytelling import (
    Narrative,
    NarrativeSection,
    NarrativeType,
    Persona,
    PersonaAdaptationRequest
)
from consultantos.storytelling.personas import (
    get_persona_prompt_guidance,
    adapt_content_for_persona,
    get_persona_traits
)
from consultantos.config import settings

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """
    Generates AI-powered narratives from analysis data.
    Adapts content based on target persona and narrative type.
    """

    def __init__(self):
        """Initialize narrative generator with Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        gemini_model = genai.GenerativeModel(
            model_name=settings.gemini_model or "gemini-2.5-flash"  # Updated: gemini-1.5-flash-002 is no longer available
        )
        self.client = instructor.from_gemini(
            client=gemini_model,
            mode=instructor.Mode.GEMINI_JSON,
        )
        self.model = settings.gemini_model or "gemini-2.5-flash"  # Updated: gemini-1.5-flash-002 is no longer available

    async def generate_narrative(
        self,
        data: Dict[str, Any],
        persona: Persona,
        narrative_type: NarrativeType = NarrativeType.SUMMARY,
        focus_areas: Optional[List[str]] = None,
        max_length_words: int = 1500,
        tone: Optional[str] = None
    ) -> Narrative:
        """
        Generate a narrative from analysis data tailored to specific persona.

        Args:
            data: Analysis results and insights
            persona: Target audience persona
            narrative_type: Type of narrative to generate
            focus_areas: Specific topics to emphasize
            max_length_words: Maximum word count
            tone: Tone preference (overrides persona default)

        Returns:
            Generated narrative with sections and insights
        """
        logger.info(f"Generating {narrative_type.value} narrative for {persona.value} persona")

        # Get persona guidance
        persona_guidance = get_persona_prompt_guidance(persona)
        persona_traits = get_persona_traits(persona)

        # Prepare data summary
        data_summary = self._prepare_data_summary(data)

        # Build prompt
        prompt = self._build_narrative_prompt(
            data_summary=data_summary,
            persona=persona,
            narrative_type=narrative_type,
            persona_guidance=persona_guidance,
            focus_areas=focus_areas or persona_traits["focus"][:3],
            max_length_words=max_length_words,
            tone=tone or persona_traits["tone"]
        )

        try:
            # Generate narrative using Gemini
            response = self.client.messages.create(
                model=self.model,
                response_model=Narrative,
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Set persona and metadata
            response.generated_for_persona = persona
            response.source_data_summary = data_summary[:500]  # Store summary

            logger.info(f"Generated narrative with {len(response.sections)} sections, {response.length_words} words")
            return response

        except Exception as e:
            logger.error(f"Failed to generate narrative: {str(e)}")
            # Return fallback narrative
            return self._create_fallback_narrative(data, persona, narrative_type)

    async def adapt_narrative_for_persona(
        self,
        original_narrative: Narrative,
        target_persona: Persona,
        preserve_data: bool = True
    ) -> Narrative:
        """
        Adapt an existing narrative for a different persona.

        Args:
            original_narrative: Original narrative content
            target_persona: New target audience persona
            preserve_data: Keep the same data references

        Returns:
            Adapted narrative for new persona
        """
        logger.info(f"Adapting narrative from {original_narrative.generated_for_persona.value} to {target_persona.value}")

        # Get adaptation guidance
        adaptation_guidance = adapt_content_for_persona(
            original_content=original_narrative.title,
            original_persona=original_narrative.generated_for_persona,
            target_persona=target_persona
        )

        # Get target persona traits
        target_traits = get_persona_traits(target_persona)

        # Build adaptation prompt
        prompt = f"""
{adaptation_guidance}

ORIGINAL NARRATIVE:
Title: {original_narrative.title}
{original_narrative.subtitle or ""}

Key Insights:
{chr(10).join([f"- {insight}" for insight in original_narrative.key_insights])}

Sections:
{self._format_sections_for_prompt(original_narrative.sections)}

TASK: Rewrite this narrative for {target_persona.value} audience following the style changes above.

Requirements:
- Maintain factual accuracy
- {"Preserve all data references and numbers" if preserve_data else "Adjust data presentation as needed"}
- Adjust language and focus for {target_persona.value}
- Target length: {len(original_narrative.sections) * 200}-{len(original_narrative.sections) * 300} words
- Tone: {target_traits["tone"]}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                response_model=Narrative,
                max_tokens=8000,
                messages=[{"role": "user", "content": prompt}]
            )

            response.generated_for_persona = target_persona
            return response

        except Exception as e:
            logger.error(f"Failed to adapt narrative: {str(e)}")
            # Return modified copy
            return self._manual_adaptation(original_narrative, target_persona)

    async def generate_key_insights(
        self,
        data: Dict[str, Any],
        persona: Persona,
        max_insights: int = 5
    ) -> List[str]:
        """
        Extract key insights from data tailored to persona.

        Args:
            data: Analysis data
            persona: Target audience
            max_insights: Maximum number of insights

        Returns:
            List of key insight statements
        """
        persona_traits = get_persona_traits(persona)
        data_summary = self._prepare_data_summary(data)

        prompt = f"""
Extract the top {max_insights} most important insights from this analysis for {persona.value} audience.

Data:
{data_summary}

Focus on:
{chr(10).join([f"- {focus}" for focus in persona_traits["focus"][:5]])}

Requirements:
- Each insight should be a clear, standalone statement
- Use {persona_traits["language"]} language
- Include specific numbers or trends when available
- Prioritize {", ".join(persona_traits["prioritize"])}

Return only a JSON array of insight strings.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse insights from response
            insights_text = response.choices[0].message.content
            insights = json.loads(insights_text)

            return insights[:max_insights]

        except Exception as e:
            logger.error(f"Failed to generate insights: {str(e)}")
            return self._extract_basic_insights(data, max_insights)

    def _build_narrative_prompt(
        self,
        data_summary: str,
        persona: Persona,
        narrative_type: NarrativeType,
        persona_guidance: str,
        focus_areas: List[str],
        max_length_words: int,
        tone: str
    ) -> str:
        """Build comprehensive prompt for narrative generation."""

        type_guidance = {
            NarrativeType.SUMMARY: "Provide an executive summary highlighting the most important findings and recommendations.",
            NarrativeType.TREND: "Analyze key trends and patterns, explaining their significance and trajectory.",
            NarrativeType.INSIGHT: "Explain a specific key insight in depth, including context, implications, and evidence.",
            NarrativeType.RECOMMENDATION: "Present actionable recommendations with clear rationale and expected outcomes.",
            NarrativeType.COMPARISON: "Compare different options, scenarios, or competitors with objective analysis.",
            NarrativeType.FORECAST: "Predict future developments based on current data and trends."
        }

        prompt = f"""
Generate a {narrative_type.value} narrative from the following analysis data.

{persona_guidance}

DATA TO ANALYZE:
{data_summary}

NARRATIVE TYPE: {narrative_type.value}
{type_guidance[narrative_type]}

FOCUS AREAS:
{chr(10).join([f"- {area}" for area in focus_areas])}

REQUIREMENTS:
- Target length: {max_length_words} words (±10%)
- Tone: {tone}
- Create 3-5 sections with clear headings
- Each section should:
  * Have a descriptive heading
  * Contain 2-4 paragraphs or 3-6 bullet points
  * Reference specific data points
  * Include key insights

- Generate 3-5 key insights (one-sentence takeaways)
- Provide 2-4 actionable recommendations
- Use concrete numbers and trends from the data
- Maintain professional, evidence-based approach

STRUCTURE:
1. Compelling title
2. Optional subtitle
3. 3-5 narrative sections
4. Key insights list
5. Recommendations list
"""

        return prompt

    def _prepare_data_summary(self, data: Dict[str, Any], max_length: int = 3000) -> str:
        """Prepare a concise summary of analysis data for prompt."""
        try:
            # Convert data to formatted string
            formatted_data = json.dumps(data, indent=2, default=str)

            # Truncate if too long
            if len(formatted_data) > max_length:
                formatted_data = formatted_data[:max_length] + "\n... (truncated)"

            return formatted_data

        except Exception as e:
            logger.warning(f"Failed to format data: {str(e)}")
            return str(data)[:max_length]

    def _format_sections_for_prompt(self, sections: List[NarrativeSection]) -> str:
        """Format narrative sections for inclusion in prompt."""
        formatted = []
        for i, section in enumerate(sections, 1):
            formatted.append(f"\nSection {i}: {section.heading}")
            formatted.append(section.content[:500])  # Truncate long content

        return "\n".join(formatted)

    def _create_fallback_narrative(
        self,
        data: Dict[str, Any],
        persona: Persona,
        narrative_type: NarrativeType
    ) -> Narrative:
        """Create a basic fallback narrative when AI generation fails."""
        return Narrative(
            title=f"{narrative_type.value.title()} Analysis",
            subtitle="Automated Analysis Summary",
            sections=[
                NarrativeSection(
                    heading="Overview",
                    content=f"This {narrative_type.value} provides insights from the analysis data.",
                    supporting_data={},
                    key_points=["Analysis completed successfully"]
                )
            ],
            key_insights=["Analysis data available for review"],
            recommendations=["Review detailed data for further insights"],
            tone="professional",
            length_words=50,
            confidence_score=0.5,
            generated_for_persona=persona
        )

    def _manual_adaptation(
        self,
        original: Narrative,
        target_persona: Persona
    ) -> Narrative:
        """Manually adapt narrative when AI adaptation fails."""
        # Simple copy with persona change
        adapted = original.model_copy(deep=True)
        adapted.generated_for_persona = target_persona
        adapted.confidence_score = original.confidence_score * 0.8  # Reduce confidence

        return adapted

    def _extract_basic_insights(
        self,
        data: Dict[str, Any],
        max_insights: int
    ) -> List[str]:
        """Extract basic insights when AI extraction fails."""
        insights = []

        # Try to extract from common data structures
        if isinstance(data, dict):
            if "insights" in data:
                insights.extend(data["insights"][:max_insights])
            if "key_findings" in data:
                insights.extend(data["key_findings"][:max_insights])
            if "summary" in data:
                insights.append(data["summary"])

        # Generic fallback
        if not insights:
            insights = ["Analysis completed with available data"]

        return insights[:max_insights]
