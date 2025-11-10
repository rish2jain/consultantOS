"""
Actionable Recommendations Engine

Transforms analysis findings into prioritized, specific action items with:
- Timeline assignments
- Owner/responsibility
- Success metrics
- Resource requirements
- Risk assessment
"""
from typing import Dict, Any, List, Optional
from consultantos.models.enhanced_reports import (
    ActionItem,
    ActionableRecommendations,
    PriorityLevel,
    Timeline,
    ImpactLevel,
    RecommendationGroup
)
from consultantos.models import StrategicReport, FrameworkAnalysis
import logging

logger = logging.getLogger(__name__)


class RecommendationsEngine:
    """Generates actionable recommendations from analysis"""
    
    def __init__(self):
        self.instruction = """
        Transform strategic analysis findings into specific, prioritized action items.
        Each recommendation must include:
        - Clear title and description
        - Priority level (Critical/High/Medium/Low)
        - Timeline (Immediate/Short-term/Medium-term/Long-term)
        - Expected outcome
        - Success metrics/KPIs
        - Resource requirements
        - Potential risks
        """
    
    def generate_recommendations(
        self,
        report: StrategicReport,
        enhanced_frameworks: Optional[Dict[str, Any]] = None
    ) -> ActionableRecommendations:
        """
        Generate actionable recommendations from analysis report.
        
        Args:
            report: StrategicReport with analysis findings
            enhanced_frameworks: Optional enhanced framework analysis
            
        Returns:
            ActionableRecommendations with prioritized action items
        """
        recommendations = ActionableRecommendations()
        
        # Extract findings from executive summary
        key_findings = report.executive_summary.key_findings
        strategic_rec = report.executive_summary.strategic_recommendation
        
        # Generate actions from key findings
        for finding in key_findings:
            actions = self._findings_to_actions(finding, report)
            recommendations.immediate_actions.extend(actions.get("immediate", []))
            recommendations.short_term_actions.extend(actions.get("short_term", []))
            recommendations.medium_term_actions.extend(actions.get("medium_term", []))
            recommendations.long_term_actions.extend(actions.get("long_term", []))
        
        # Generate actions from strategic recommendation
        strategic_actions = self._strategic_recommendation_to_actions(strategic_rec, report)
        recommendations.immediate_actions.extend(strategic_actions.get("immediate", []))
        recommendations.short_term_actions.extend(strategic_actions.get("short_term", []))
        
        # Generate actions from framework analysis
        if report.framework_analysis:
            framework_actions = self._framework_to_actions(report.framework_analysis)
            recommendations.immediate_actions.extend(framework_actions.get("immediate", []))
            recommendations.short_term_actions.extend(framework_actions.get("short_term", []))
            recommendations.medium_term_actions.extend(framework_actions.get("medium_term", []))
            recommendations.long_term_actions.extend(framework_actions.get("long_term", []))
        
        # Identify critical actions (high priority + immediate timeline)
        recommendations.critical_actions = [
            action for action in recommendations.immediate_actions
            if action.priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]
        ]
        
        # Group by owner
        recommendations.grouped_by_owner = self._group_by_owner(recommendations)
        
        return recommendations
    
    def _findings_to_actions(self, finding: str, report: StrategicReport) -> Dict[str, List[ActionItem]]:
        """Convert a finding into actionable items"""
        actions = {
            "immediate": [],
            "short_term": [],
            "medium_term": [],
            "long_term": []
        }
        
        # Determine priority based on finding content
        priority = self._determine_priority(finding)
        impact = self._determine_impact(finding)
        
        # Create immediate action for high-priority findings
        if priority in [PriorityLevel.CRITICAL, PriorityLevel.HIGH]:
            actions["immediate"].append(ActionItem(
                title=f"Address: {finding[:50]}",
                description=f"Immediate action required based on finding: {finding}",
                priority=priority,
                timeline=Timeline.IMMEDIATE,
                expected_outcome=f"Mitigate risk or capitalize on opportunity identified in: {finding}",
                success_metrics=[
                    "Action plan created within 2 weeks",
                    "Stakeholder alignment achieved",
                    "Initial progress within 30 days"
                ],
                resource_requirements="Medium",
                potential_impact=impact,
                related_findings=[finding]
            ))
        
        # Create short-term follow-up
        actions["short_term"].append(ActionItem(
            title=f"Implement strategy for: {finding[:50]}",
            description=f"Develop and execute strategy addressing: {finding}",
            priority=PriorityLevel.MEDIUM if priority == PriorityLevel.CRITICAL else PriorityLevel.LOW,
            timeline=Timeline.SHORT_TERM,
            expected_outcome=f"Measurable progress on addressing: {finding}",
            success_metrics=[
                "Strategy document completed",
                "Resources allocated",
                "Milestone achieved within 6 months"
            ],
            resource_requirements="Medium",
            potential_impact=impact,
            related_findings=[finding]
        ))
        
        return actions
    
    def _strategic_recommendation_to_actions(
        self,
        recommendation: str,
        report: StrategicReport
    ) -> Dict[str, List[ActionItem]]:
        """Convert strategic recommendation into actionable items"""
        actions = {
            "immediate": [],
            "short_term": [],
            "medium_term": [],
            "long_term": []
        }
        
        # Break down strategic recommendation into phases
        actions["immediate"].append(ActionItem(
            title="Initiate Strategic Recommendation",
            description=f"Begin implementation of: {recommendation}",
            priority=PriorityLevel.HIGH,
            timeline=Timeline.IMMEDIATE,
            owner="Executive Team",
            expected_outcome="Strategic initiative launched",
            success_metrics=[
                "Project charter approved",
                "Team assigned",
                "Budget allocated"
            ],
            resource_requirements="High",
            potential_impact=ImpactLevel.HIGH,
            related_findings=[recommendation]
        ))
        
        actions["short_term"].append(ActionItem(
            title="Execute Strategic Recommendation",
            description=f"Implement: {recommendation}",
            priority=PriorityLevel.HIGH,
            timeline=Timeline.SHORT_TERM,
            owner="Project Team",
            expected_outcome=f"Measurable progress on: {recommendation}",
            success_metrics=[
                "Key milestones achieved",
                "Stakeholder buy-in secured",
                "Initial results visible"
            ],
            resource_requirements="High",
            potential_impact=ImpactLevel.HIGH,
            related_findings=[recommendation]
        ))
        
        return actions
    
    def _framework_to_actions(
        self,
        framework_analysis: FrameworkAnalysis
    ) -> Dict[str, List[ActionItem]]:
        """Generate actions from framework analysis"""
        actions = {
            "immediate": [],
            "short_term": [],
            "medium_term": [],
            "long_term": []
        }
        
        # Porter's Five Forces actions
        if framework_analysis.porter_five_forces:
            porter = framework_analysis.porter_five_forces
            # Check if overall_intensity is not None/empty before calling .lower()
            if porter.overall_intensity:
                intensity = porter.overall_intensity.lower()
                
                if "high" in intensity:
                    actions["immediate"].append(ActionItem(
                        title="Address High Competitive Intensity",
                        description=f"Industry shows {intensity} competitive intensity. Develop differentiation strategy.",
                        priority=PriorityLevel.HIGH,
                        timeline=Timeline.IMMEDIATE,
                        owner="Strategy Team",
                        expected_outcome="Competitive positioning strategy defined",
                        success_metrics=[
                            "Competitive analysis completed",
                            "Differentiation plan created",
                            "Market positioning updated"
                        ],
                        resource_requirements="Medium",
                        potential_impact=ImpactLevel.HIGH,
                        related_findings=[f"Porter's analysis: {intensity} intensity"]
                    ))
        
        # SWOT actions
        if framework_analysis.swot_analysis:
            swot = framework_analysis.swot_analysis
            
            # Address top weaknesses
            if swot.weaknesses:
                top_weakness = swot.weaknesses[0]
                actions["short_term"].append(ActionItem(
                    title=f"Mitigate Weakness: {top_weakness[:50]}",
                    description=f"Address identified weakness: {top_weakness}",
                    priority=PriorityLevel.MEDIUM,
                    timeline=Timeline.SHORT_TERM,
                    owner="Operations Team",
                    expected_outcome=f"Weakness addressed: {top_weakness}",
                    success_metrics=[
                        "Improvement plan created",
                        "Resources allocated",
                        "Progress measured"
                    ],
                    resource_requirements="Medium",
                    potential_impact=ImpactLevel.MEDIUM,
                    related_findings=[f"SWOT weakness: {top_weakness}"]
                ))
            
            # Pursue top opportunities
            if swot.opportunities:
                top_opportunity = swot.opportunities[0]
                actions["short_term"].append(ActionItem(
                    title=f"Pursue Opportunity: {top_opportunity[:50]}",
                    description=f"Capitalize on opportunity: {top_opportunity}",
                    priority=PriorityLevel.HIGH,
                    timeline=Timeline.SHORT_TERM,
                    owner="Business Development",
                    expected_outcome=f"Progress on opportunity: {top_opportunity}",
                    success_metrics=[
                        "Opportunity assessment completed",
                        "Go/no-go decision made",
                        "Initial investment committed"
                    ],
                    resource_requirements="Medium",
                    potential_impact=ImpactLevel.HIGH,
                    related_findings=[f"SWOT opportunity: {top_opportunity}"]
                ))
        
        # Blue Ocean actions
        if framework_analysis.blue_ocean_strategy:
            blue_ocean = framework_analysis.blue_ocean_strategy
            
            if blue_ocean.create:
                actions["medium_term"].append(ActionItem(
                    title="Explore Blue Ocean Innovation",
                    description="Investigate new value propositions from Blue Ocean analysis",
                    priority=PriorityLevel.MEDIUM,
                    timeline=Timeline.MEDIUM_TERM,
                    owner="Innovation Team",
                    expected_outcome="New market space identified",
                    success_metrics=[
                        "Market research completed",
                        "Value proposition validated",
                        "Pilot program launched"
                    ],
                    resource_requirements="High",
                    potential_impact=ImpactLevel.HIGH,
                    related_findings=["Blue Ocean Strategy analysis"]
                ))
        
        return actions
    
    def _determine_priority(self, finding: str) -> PriorityLevel:
        """Determine priority level from finding text"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["critical", "urgent", "immediate", "threat", "risk"]):
            return PriorityLevel.CRITICAL
        elif any(word in finding_lower for word in ["important", "significant", "major"]):
            return PriorityLevel.HIGH
        elif any(word in finding_lower for word in ["consider", "evaluate", "assess"]):
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
    
    def _determine_impact(self, finding: str) -> ImpactLevel:
        """Determine impact level from finding text"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["high", "significant", "major", "critical"]):
            return ImpactLevel.HIGH
        elif any(word in finding_lower for word in ["moderate", "medium", "some"]):
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _group_by_owner(self, recommendations: ActionableRecommendations) -> Dict[str, List[ActionItem]]:
        """Group actions by owner/responsible party"""
        grouped = {}
        
        all_actions = (
            recommendations.immediate_actions +
            recommendations.short_term_actions +
            recommendations.medium_term_actions +
            recommendations.long_term_actions
        )
        
        for action in all_actions:
            owner = action.owner or "Unassigned"
            if owner not in grouped:
                grouped[owner] = []
            grouped[owner].append(action)
        
        return grouped

