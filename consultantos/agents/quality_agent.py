"""
Quality Assurance Agent - Reviews analysis outputs for quality
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import StrategicReport
from pydantic import BaseModel


class QualityReview(BaseModel):
    """Quality review results"""
    quality_score: float  # 0-100
    specificity_score: float  # 0-100
    evidence_score: float  # 0-100
    depth_score: float  # 0-100
    actionability_score: float  # 0-100
    consistency_score: float  # 0-100
    issues: list[str]
    suggestions: list[str]
    overall_assessment: str


class QualityAgent(BaseAgent):
    """Quality assurance agent for reviewing analysis outputs"""
    
    def __init__(self):
        super().__init__(
            name="quality_agent",
            model="gemini-pro",  # Use more capable model for quality review
            timeout=90  # Longer timeout for quality analysis
        )
        self.instruction = """
        You are a quality assurance specialist reviewing strategic analysis reports.
        
        Evaluate the report for:
        1. Specificity - Are statements specific and data-driven? Avoid vague or generic content.
        2. Evidence - Are claims backed by citations and data points?
        3. Depth - Does analysis go beyond surface-level observations?
        4. Actionability - Are recommendations clear and implementable?
        5. Consistency - Are insights consistent across frameworks?
        
        Flag generic or template-y content.
        Provide quality score (0-100) and improvement suggestions.
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> QualityReview:
        """
        Review report quality
        
        Args:
            input_data: Dictionary containing 'report' (StrategicReport)
        
        Returns:
            QualityReview with scores and feedback
        """
        report = input_data.get("report")
        
        if not report:
            return QualityReview(
                quality_score=0.0,
                specificity_score=0.0,
                evidence_score=0.0,
                depth_score=0.0,
                actionability_score=0.0,
                consistency_score=0.0,
                issues=["No report provided for review"],
                suggestions=["Provide a valid report"],
                overall_assessment="Cannot review - no report provided"
            )
        
        # Format report for review
        report_summary = self._format_report_for_review(report)
        
        prompt = f"""
        {self.instruction}
        
        Review the following strategic analysis report:
        
        {report_summary}
        
        Evaluate and provide:
        1. Quality score (0-100) - Overall quality
        2. Specificity score (0-100) - How specific and data-driven
        3. Evidence score (0-100) - How well claims are supported
        4. Depth score (0-100) - How deep the analysis goes
        5. Actionability score (0-100) - How actionable recommendations are
        6. Consistency score (0-100) - Consistency across frameworks
        7. Issues - List of specific problems found
        8. Suggestions - List of improvement suggestions
        9. Overall assessment - Brief summary
        """
        
        try:
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=QualityReview,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return result
        except Exception as e:
            # Fallback - return neutral scores
            return QualityReview(
                quality_score=50.0,
                specificity_score=50.0,
                evidence_score=50.0,
                depth_score=50.0,
                actionability_score=50.0,
                consistency_score=50.0,
                issues=[f"Quality review failed: {str(e)}"],
                suggestions=["Manual review recommended"],
                overall_assessment="Quality review could not be completed automatically"
            )
    
    def _format_report_for_review(self, report: StrategicReport) -> str:
        """Format report for quality review"""
        summary = report.executive_summary
        
        sections = []
        sections.append(f"Company: {summary.company_name}")
        sections.append(f"Industry: {summary.industry}")
        sections.append(f"Key Findings: {', '.join(summary.key_findings[:5])}")
        sections.append(f"Strategic Recommendation: {summary.strategic_recommendation}")
        sections.append(f"Confidence Score: {summary.confidence_score}")
        
        if report.framework_analysis:
            if report.framework_analysis.porter_five_forces:
                sections.append("Porter's Five Forces: Included")
            if report.framework_analysis.swot_analysis:
                sections.append("SWOT Analysis: Included")
            if report.framework_analysis.pestel_analysis:
                sections.append("PESTEL Analysis: Included")
            if report.framework_analysis.blue_ocean_strategy:
                sections.append("Blue Ocean Strategy: Included")
        
        if report.recommendations:
            sections.append(f"Recommendations: {len(report.recommendations)} provided")
        
        return "\n".join(sections)

