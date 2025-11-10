"""
Risk and Opportunity Scoring Service

Generates quantified risk and opportunity assessments with:
- Risk heatmaps (likelihood vs impact)
- Opportunity prioritization (impact vs effort)
- Early warning indicators
- Mitigation strategies
"""
from typing import Dict, Any, List, Optional
from consultantos.models import StrategicReport, FrameworkAnalysis
from consultantos.models.enhanced_reports import (
    RiskItem,
    OpportunityItem,
    RiskOpportunityMatrix,
    ImpactLevel,
    PriorityLevel
)
import logging

logger = logging.getLogger(__name__)


class RiskOpportunityScorer:
    """Scores risks and opportunities from analysis"""
    
    def generate_risk_opportunity_matrix(
        self,
        report: StrategicReport
    ) -> RiskOpportunityMatrix:
        """
        Generate risk and opportunity assessment matrix.
        
        Args:
            report: Strategic report with analysis
            
        Returns:
            RiskOpportunityMatrix with scored risks and opportunities
        """
        risks = []
        opportunities = []
        
        # Extract risks from findings and frameworks
        risks.extend(self._extract_risks_from_findings(report.executive_summary.key_findings))
        risks.extend(self._extract_risks_from_frameworks(report.framework_analysis))
        
        # Extract opportunities from findings and frameworks
        opportunities.extend(self._extract_opportunities_from_findings(report.executive_summary.key_findings))
        opportunities.extend(self._extract_opportunities_from_frameworks(report.framework_analysis))
        
        # Build risk heatmap
        risk_heatmap = self._build_risk_heatmap(risks)
        
        # Prioritize opportunities
        opportunity_prioritization = self._prioritize_opportunities(opportunities)
        
        return RiskOpportunityMatrix(
            risks=risks,
            opportunities=opportunities,
            risk_heatmap=risk_heatmap,
            opportunity_prioritization=opportunity_prioritization
        )
    
    def _extract_risks_from_findings(self, findings: List[str]) -> List[RiskItem]:
        """Extract risk items from key findings"""
        risks = []
        
        for finding in findings:
            finding_lower = finding.lower()
            
            # Identify risk-related findings
            if any(word in finding_lower for word in ["risk", "threat", "challenge", "concern", "vulnerability"]):
                likelihood = self._assess_likelihood(finding)
                impact = self._assess_impact(finding)
                risk_score = likelihood * (3.0 if impact == ImpactLevel.HIGH else 2.0 if impact == ImpactLevel.MEDIUM else 1.0)
                
                risks.append(RiskItem(
                    title=f"Risk: {finding[:60]}",
                    description=finding,
                    likelihood=likelihood,
                    impact=impact,
                    risk_score=min(risk_score, 10.0),
                    mitigation_strategies=self._generate_mitigation_strategies(finding),
                    early_warning_indicators=self._generate_warning_indicators(finding),
                    related_factors=[finding]
                ))
        
        return risks
    
    def _extract_risks_from_frameworks(self, framework_analysis: Optional[FrameworkAnalysis]) -> List[RiskItem]:
        """Extract risks from framework analysis"""
        risks = []
        
        if not framework_analysis:
            return risks
        
        # Porter's Five Forces risks
        if framework_analysis.porter_five_forces:
            porter = framework_analysis.porter_five_forces
            
            # Check if overall_intensity is not None/empty before calling .lower()
            if porter.overall_intensity and porter.overall_intensity.lower() in ["high", "very high"]:
                risks.append(RiskItem(
                    title="High Competitive Intensity Risk",
                    description=f"Industry shows {porter.overall_intensity} competitive intensity",
                    likelihood=8.0,
                    impact=ImpactLevel.HIGH,
                    risk_score=8.0,
                    mitigation_strategies=[
                        "Develop strong differentiation strategy",
                        "Build customer loyalty programs",
                        "Invest in innovation"
                    ],
                    early_warning_indicators=[
                        "Price wars breaking out",
                        "New aggressive competitors entering",
                        "Market share declining"
                    ],
                    related_factors=["Porter's Five Forces analysis"]
                ))
        
        # SWOT threats
        if framework_analysis.swot_analysis:
            for threat in framework_analysis.swot_analysis.threats:
                risks.append(RiskItem(
                    title=f"Threat: {threat[:50]}",
                    description=threat,
                    likelihood=7.0,
                    impact=ImpactLevel.MEDIUM,
                    risk_score=7.0,
                    mitigation_strategies=self._generate_mitigation_strategies(threat),
                    early_warning_indicators=self._generate_warning_indicators(threat),
                    related_factors=[f"SWOT threat: {threat}"]
                ))
        
        return risks
    
    def _extract_opportunities_from_findings(self, findings: List[str]) -> List[OpportunityItem]:
        """Extract opportunity items from key findings"""
        opportunities = []
        
        for finding in findings:
            finding_lower = finding.lower()
            
            # Identify opportunity-related findings
            if any(word in finding_lower for word in ["opportunity", "growth", "potential", "advantage", "benefit"]):
                impact_potential = self._assess_opportunity_impact(finding)
                feasibility = self._assess_feasibility(finding)
                priority_score = (impact_potential + feasibility) / 2.0
                
                opportunities.append(OpportunityItem(
                    title=f"Opportunity: {finding[:60]}",
                    description=finding,
                    impact_potential=impact_potential,
                    feasibility=feasibility,
                    timeline_to_value=self._estimate_timeline(finding),
                    resource_requirements=self._estimate_resources(finding),
                    strategic_fit=75.0,  # Default, can be enhanced
                    competitive_advantage_strength=7.0,  # Default
                    priority_score=priority_score
                ))
        
        return opportunities
    
    def _extract_opportunities_from_frameworks(self, framework_analysis: Optional[FrameworkAnalysis]) -> List[OpportunityItem]:
        """Extract opportunities from framework analysis"""
        opportunities = []
        
        if not framework_analysis:
            return opportunities
        
        # SWOT opportunities
        if framework_analysis.swot_analysis:
            for opp in framework_analysis.swot_analysis.opportunities:
                opportunities.append(OpportunityItem(
                    title=f"Opportunity: {opp[:60]}",
                    description=opp,
                    impact_potential=8.0,
                    feasibility=7.0,
                    timeline_to_value=12,
                    resource_requirements="Medium",
                    strategic_fit=80.0,
                    competitive_advantage_strength=7.5,
                    priority_score=7.5
                ))
        
        # Blue Ocean opportunities
        if framework_analysis.blue_ocean_strategy:
            blue_ocean = framework_analysis.blue_ocean_strategy
            
            for create_action in blue_ocean.create:
                opportunities.append(OpportunityItem(
                    title=f"Blue Ocean: {create_action[:60]}",
                    description=f"Create new value through: {create_action}",
                    impact_potential=9.0,
                    feasibility=6.0,  # Innovation is harder
                    timeline_to_value=18,
                    resource_requirements="High",
                    strategic_fit=85.0,
                    competitive_advantage_strength=9.0,
                    priority_score=7.5
                ))
        
        return opportunities
    
    def _build_risk_heatmap(self, risks: List[RiskItem]) -> Dict[str, Dict[str, float]]:
        """Build risk heatmap (likelihood vs impact)"""
        heatmap = {
            "high_likelihood_high_impact": [],
            "high_likelihood_medium_impact": [],
            "high_likelihood_low_impact": [],
            "medium_likelihood_high_impact": [],
            "medium_likelihood_medium_impact": [],
            "medium_likelihood_low_impact": [],
            "low_likelihood_high_impact": [],
            "low_likelihood_medium_impact": [],
            "low_likelihood_low_impact": []
        }
        
        for risk in risks:
            likelihood_cat = "high" if risk.likelihood >= 7 else "medium" if risk.likelihood >= 4 else "low"
            impact_cat = risk.impact.value
            
            key = f"{likelihood_cat}_likelihood_{impact_cat}_impact"
            if key in heatmap:
                if isinstance(heatmap[key], list):
                    heatmap[key].append({
                        "title": risk.title,
                        "risk_score": risk.risk_score
                    })
                else:
                    heatmap[key] = [{
                        "title": risk.title,
                        "risk_score": risk.risk_score
                    }]
        
        return heatmap
    
    def _prioritize_opportunities(self, opportunities: List[OpportunityItem]) -> List[Dict[str, Any]]:
        """Prioritize opportunities by impact vs effort"""
        # Sort by priority score (impact × feasibility)
        sorted_opps = sorted(opportunities, key=lambda x: x.priority_score, reverse=True)
        
        return [
            {
                "rank": i + 1,
                "title": opp.title,
                "impact_potential": opp.impact_potential,
                "feasibility": opp.feasibility,
                "priority_score": opp.priority_score,
                "timeline": opp.timeline_to_value,
                "resource_requirements": opp.resource_requirements
            }
            for i, opp in enumerate(sorted_opps)
        ]
    
    # Helper methods
    
    def _assess_likelihood(self, finding: str) -> float:
        """Assess likelihood of risk materializing (0-10)"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["imminent", "immediate", "now", "current"]):
            return 9.0
        elif any(word in finding_lower for word in ["likely", "probable", "expected"]):
            return 7.0
        elif any(word in finding_lower for word in ["possible", "potential", "may"]):
            return 5.0
        else:
            return 3.0
    
    def _assess_impact(self, finding: str) -> ImpactLevel:
        """Assess impact level"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["critical", "severe", "major", "significant"]):
            return ImpactLevel.HIGH
        elif any(word in finding_lower for word in ["moderate", "medium", "some"]):
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _assess_opportunity_impact(self, finding: str) -> float:
        """Assess opportunity impact potential (1-10)"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["major", "significant", "huge", "transformative"]):
            return 9.0
        elif any(word in finding_lower for word in ["substantial", "important", "notable"]):
            return 7.0
        elif any(word in finding_lower for word in ["moderate", "some", "potential"]):
            return 5.0
        else:
            return 3.0
    
    def _assess_feasibility(self, finding: str) -> float:
        """Assess feasibility of opportunity (1-10)"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["easy", "quick", "simple", "straightforward"]):
            return 8.0
        elif any(word in finding_lower for word in ["feasible", "achievable", "realistic"]):
            return 6.0
        elif any(word in finding_lower for word in ["challenging", "complex", "difficult"]):
            return 4.0
        else:
            return 5.0
    
    def _estimate_timeline(self, finding: str) -> int:
        """Estimate timeline to value in months"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["quick", "immediate", "soon", "fast"]):
            return 3
        elif any(word in finding_lower for word in ["short", "months"]):
            return 6
        elif any(word in finding_lower for word in ["medium", "year"]):
            return 12
        else:
            return 18
    
    def _estimate_resources(self, finding: str) -> str:
        """Estimate resource requirements"""
        finding_lower = finding.lower()
        
        if any(word in finding_lower for word in ["major", "significant", "large", "substantial"]):
            return "High"
        elif any(word in finding_lower for word in ["moderate", "medium", "some"]):
            return "Medium"
        else:
            return "Low"
    
    def _generate_mitigation_strategies(self, risk: str) -> List[str]:
        """Generate mitigation strategies for a risk"""
        return [
            f"Develop contingency plan for {risk[:50]}",
            f"Monitor early warning indicators",
            f"Build resilience to {risk[:50]} impact"
        ]
    
    def _generate_warning_indicators(self, risk: str) -> List[str]:
        """Generate early warning indicators"""
        return [
            f"Monitor market signals related to {risk[:50]}",
            f"Track industry trends",
            f"Watch for regulatory changes"
        ]

