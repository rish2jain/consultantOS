"""
Systems Agent for system dynamics and feedback loop analysis.

Integrates feedback loop detection, leverage point identification, and
momentum tracking for comprehensive system intelligence.
"""
import logging
from typing import Dict, Any, List
import asyncio

from consultantos.agents.base_agent import BaseAgent
from consultantos.models.systems import SystemDynamicsAnalysis
from consultantos.analysis.feedback_loops import FeedbackLoopDetector

logger = logging.getLogger(__name__)


class SystemsAgent(BaseAgent):
    """
    Agent for system dynamics analysis.

    Analyzes feedback loops, causal relationships, and leverage points
    to provide strategic insights about business systems.
    """

    def __init__(self, timeout: int = 90):
        """
        Initialize Systems Agent.

        Args:
            timeout: Per-agent timeout in seconds (default: 90s for complex analysis)
        """
        super().__init__(name="SystemsAgent", timeout=timeout)
        self.loop_detector = FeedbackLoopDetector(
            min_correlation=0.5,
            min_confidence=0.6
        )

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute system dynamics analysis.

        Args:
            input_data: Must contain:
                - company: str
                - industry: str
                - time_series_data: Dict[str, List[float]] - metric_name -> values
                - metric_names: List[str] - names of metrics

        Returns:
            Dict containing:
                - success: bool
                - data: SystemDynamicsAnalysis or None
                - error: str if success is False
        """
        try:
            # Extract required inputs
            company = input_data.get("company")
            industry = input_data.get("industry")
            time_series_data = input_data.get("time_series_data", {})
            metric_names = input_data.get("metric_names", [])

            if not company or not industry:
                return {
                    "success": False,
                    "data": None,
                    "error": "Company and industry are required"
                }

            if not time_series_data or not metric_names:
                return {
                    "success": False,
                    "data": None,
                    "error": "Time series data and metric names are required"
                }

            logger.info(f"Starting system dynamics analysis for {company}")

            # Perform analysis in thread pool (CPU-intensive)
            analysis = await asyncio.to_thread(
                self.loop_detector.analyze_system,
                time_series_data,
                metric_names,
                company,
                industry
            )

            logger.info(
                f"System dynamics analysis complete: "
                f"{len(analysis.reinforcing_loops)} reinforcing loops, "
                f"{len(analysis.balancing_loops)} balancing loops, "
                f"{len(analysis.leverage_points)} leverage points"
            )

            # Generate narrative summary using LLM
            narrative = await self._generate_narrative(analysis)

            return {
                "success": True,
                "data": analysis,
                "narrative": narrative,
                "error": None
            }

        except Exception as e:
            logger.error(f"SystemsAgent failed: {e}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _generate_narrative(
        self,
        analysis: SystemDynamicsAnalysis
    ) -> str:
        """
        Generate human-readable narrative from system dynamics analysis.

        Args:
            analysis: System dynamics analysis result

        Returns:
            Narrative summary string
        """
        try:
            # Build prompt for LLM
            prompt = self._build_narrative_prompt(analysis)

            # Use Gemini to generate narrative
            from pydantic import BaseModel

            class SystemsNarrative(BaseModel):
                """Narrative summary of system dynamics"""
                executive_summary: str
                key_insights: List[str]
                strategic_implications: str
                recommended_interventions: List[str]

            result = await self.generate_structured(
                prompt=prompt,
                response_model=SystemsNarrative,
                temperature=0.7,
                max_tokens=2000
            )

            # Format narrative
            narrative = f"""
**SYSTEM DYNAMICS ANALYSIS**

**Executive Summary:**
{result.executive_summary}

**Key Insights:**
{chr(10).join(f"- {insight}" for insight in result.key_insights)}

**Strategic Implications:**
{result.strategic_implications}

**Recommended Interventions:**
{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(result.recommended_interventions))}
            """.strip()

            return narrative

        except Exception as e:
            logger.warning(f"Narrative generation failed: {e}")
            return self._build_fallback_narrative(analysis)

    def _build_narrative_prompt(self, analysis: SystemDynamicsAnalysis) -> str:
        """Build prompt for LLM narrative generation"""
        # Summarize loops
        reinforcing_summary = "\n".join([
            f"- {loop.loop_name}: {loop.impact} (strength: {loop.strength:.0f}/100)"
            for loop in analysis.reinforcing_loops[:3]
        ])

        balancing_summary = "\n".join([
            f"- {loop.loop_name}: {loop.impact} (strength: {loop.strength:.0f}/100)"
            for loop in analysis.balancing_loops[:3]
        ])

        # Summarize leverage points
        leverage_summary = "\n".join([
            f"- {lp.leverage_name} (Level {lp.leverage_level}): {lp.proposed_intervention}"
            for lp in analysis.leverage_points[:3]
        ])

        prompt = f"""
You are a systems thinking expert analyzing {analysis.company} in the {analysis.industry} industry.

**DETECTED SYSTEM STRUCTURE:**

Reinforcing Loops (amplifying cycles):
{reinforcing_summary or "None detected"}

Balancing Loops (stabilizing forces):
{balancing_summary or "None detected"}

Dominant Pattern: {analysis.system_archetype or "Unknown"}
Current Behavior: {analysis.current_behavior}

**LEVERAGE POINTS (Meadows' Hierarchy):**
{leverage_summary or "None identified"}

**STRUCTURAL ISSUES:**
{chr(10).join(f"- {issue}" for issue in analysis.structural_issues)}

**YOUR TASK:**
Provide a strategic analysis that:
1. Explains the system dynamics in business terms (avoid jargon)
2. Identifies key insights about how the system behaves
3. Explains strategic implications for {analysis.company}
4. Recommends 3-5 specific interventions based on leverage points

Focus on actionable insights and practical recommendations.
        """.strip()

        return prompt

    def _build_fallback_narrative(self, analysis: SystemDynamicsAnalysis) -> str:
        """Build fallback narrative without LLM"""
        narrative_parts = [
            f"**SYSTEM DYNAMICS ANALYSIS - {analysis.company}**",
            "",
            f"**System Archetype:** {analysis.system_archetype or 'Unknown'}",
            f"**Dominant Loop:** {analysis.dominant_loop or 'None'}",
            f"**Confidence:** {analysis.confidence_score:.0f}%",
            "",
            "**Reinforcing Loops:**"
        ]

        for loop in analysis.reinforcing_loops[:3]:
            narrative_parts.append(f"- {loop.loop_name} (strength: {loop.strength:.0f}/100)")

        narrative_parts.append("")
        narrative_parts.append("**Balancing Loops:**")

        for loop in analysis.balancing_loops[:3]:
            narrative_parts.append(f"- {loop.loop_name} (strength: {loop.strength:.0f}/100)")

        narrative_parts.append("")
        narrative_parts.append("**Top Leverage Points:**")

        for i, lp in enumerate(analysis.leverage_points[:3], 1):
            narrative_parts.append(
                f"{i}. {lp.leverage_name} (Level {lp.leverage_level}): "
                f"{lp.proposed_intervention}"
            )

        narrative_parts.append("")
        narrative_parts.append("**Structural Issues:**")
        narrative_parts.extend(f"- {issue}" for issue in analysis.structural_issues)

        narrative_parts.append("")
        narrative_parts.append("**Fundamental Solutions:**")
        narrative_parts.extend(f"- {sol}" for sol in analysis.fundamental_solutions)

        return "\n".join(narrative_parts)
