"""
Enhanced Report Builder

Builds multi-layered strategic reports with:
- Executive summary layer (1 page)
- Detailed analysis layer
- Supporting appendices
- Actionable recommendations
- Risk/opportunity scoring
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from consultantos.models import StrategicReport
from consultantos.models.enhanced_reports import (
    EnhancedStrategicReport,
    ExecutiveSummaryLayer,
    DetailedAnalysisLayer,
    SupportingAppendices,
    ActionableRecommendations,
    RiskOpportunityMatrix,
    CompetitiveIntelligence,
    ScenarioPlanning,
    ConfidenceLevel
)
from consultantos.reports.recommendations_engine import RecommendationsEngine
from consultantos.reports.risk_opportunity_scorer import RiskOpportunityScorer
from consultantos.reports.enhancement_service import FrameworkEnhancementService
import logging

logger = logging.getLogger(__name__)


class EnhancedReportBuilder:
    """Builds enhanced multi-layered strategic reports"""
    
    def __init__(self):
        self.recommendations_engine = RecommendationsEngine()
        self.risk_opportunity_scorer = RiskOpportunityScorer()
        self.enhancement_service = FrameworkEnhancementService()
    
    async def build_enhanced_report(
        self,
        report: StrategicReport,
        include_competitive_intelligence: bool = False,
        include_scenario_planning: bool = False
    ) -> EnhancedStrategicReport:
        """
        Build enhanced multi-layered strategic report.
        
        Args:
            report: Base strategic report
            include_competitive_intelligence: Whether to include competitive intelligence
            include_scenario_planning: Whether to include scenario planning
            
        Returns:
            EnhancedStrategicReport with all layers
        """
        # Enhance framework analysis
        enhanced_frameworks = await self.enhancement_service.enhance_framework_analysis(
            report.framework_analysis,
            report
        )
        
        # Generate actionable recommendations
        recommendations = self.recommendations_engine.generate_recommendations(
            report,
            enhanced_frameworks
        )
        
        # Generate risk/opportunity matrix
        risk_opportunity_matrix = self.risk_opportunity_scorer.generate_risk_opportunity_matrix(
            report
        )
        
        # Build executive summary layer
        executive_summary_layer = self._build_executive_summary_layer(report, enhanced_frameworks)
        
        # Build detailed analysis layer
        detailed_analysis_layer = self._build_detailed_analysis_layer(
            report,
            enhanced_frameworks,
            recommendations,
            risk_opportunity_matrix
        )
        
        # Build supporting appendices
        supporting_appendices = self._build_supporting_appendices(report, enhanced_frameworks)
        
        # Build competitive intelligence (optional)
        competitive_intelligence = None
        if include_competitive_intelligence:
            competitive_intelligence = self._build_competitive_intelligence(report)
        
        # Build scenario planning (optional)
        scenario_planning = None
        if include_scenario_planning:
            scenario_planning = self._build_scenario_planning(report, enhanced_frameworks)
        
        # Build confidence indicators
        confidence_indicators = self._build_confidence_indicators(report, enhanced_frameworks)
        
        # Build quality metrics
        quality_metrics = self._build_quality_metrics(report, enhanced_frameworks)
        
        return EnhancedStrategicReport(
            executive_summary_layer=executive_summary_layer,
            detailed_analysis_layer=detailed_analysis_layer,
            supporting_appendices=supporting_appendices,
            actionable_recommendations=recommendations,
            risk_opportunity_matrix=risk_opportunity_matrix,
            competitive_intelligence=competitive_intelligence,
            scenario_planning=scenario_planning,
            confidence_indicators=confidence_indicators,
            quality_metrics=quality_metrics,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "report_id": report.metadata.get("report_id", "unknown"),
                "version": "enhanced_v1"
            }
        )
    
    def _build_executive_summary_layer(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any]
    ) -> ExecutiveSummaryLayer:
        """Build 1-page executive summary"""
        
        # Company overview
        company_overview = {
            "name": report.executive_summary.company_name,
            "industry": report.executive_summary.industry,
            "description": report.company_research.description[:200] if report.company_research else "N/A",
            "key_metrics": {
                "market_cap": report.financial_snapshot.market_cap,
                "revenue": report.financial_snapshot.revenue,
                "revenue_growth": report.financial_snapshot.revenue_growth
            }
        }
        
        # Analysis scope
        frameworks_used = []
        if report.framework_analysis.porter_five_forces:
            frameworks_used.append("Porter's Five Forces")
        if report.framework_analysis.swot_analysis:
            frameworks_used.append("SWOT")
        if report.framework_analysis.pestel_analysis:
            frameworks_used.append("PESTEL")
        if report.framework_analysis.blue_ocean_strategy:
            frameworks_used.append("Blue Ocean Strategy")
        
        analysis_scope = f"Comprehensive strategic analysis of {report.executive_summary.company_name} " \
                         f"in the {report.executive_summary.industry} industry using " \
                         f"{', '.join(frameworks_used)} frameworks."
        
        # Methodology note
        methodology_note = f"Analysis confidence: {report.executive_summary.confidence_score:.0%}. " \
                          f"Based on research data, market trends, financial analysis, and strategic frameworks. " \
                          f"Data sources include web research, market trends, and financial data."
        
        # Visual dashboard data
        visual_dashboard = {
            "confidence_score": report.executive_summary.confidence_score,
            "frameworks_applied": len(frameworks_used),
            "key_metrics": company_overview["key_metrics"]
        }
        
        # Safely get recommendations list (handle None or missing attribute)
        safe_recs = getattr(report, "recommendations", None) or []
        if not isinstance(safe_recs, list):
            safe_recs = []
        strategic_recommendations = safe_recs[:5]  # Top 5
        
        return ExecutiveSummaryLayer(
            company_overview=company_overview,
            analysis_date=report.executive_summary.analysis_date,
            analysis_scope=analysis_scope,
            key_findings=report.executive_summary.key_findings,
            strategic_recommendations=strategic_recommendations,
            confidence_score=report.executive_summary.confidence_score,
            methodology_note=methodology_note,
            next_steps=report.executive_summary.next_steps,
            visual_dashboard=visual_dashboard
        )
    
    def _build_detailed_analysis_layer(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any],
        recommendations: ActionableRecommendations,
        risk_opportunity_matrix: RiskOpportunityMatrix
    ) -> DetailedAnalysisLayer:
        """Build detailed analysis layer"""
        
        # Framework breakdowns
        framework_breakdowns = {
            "porter": enhanced_frameworks.get("porter"),
            "swot": enhanced_frameworks.get("swot"),
            "pestel": enhanced_frameworks.get("pestel"),
            "blue_ocean": enhanced_frameworks.get("blue_ocean")
        }
        
        # Supporting data
        supporting_data = {
            "research": {
                "company_name": report.company_research.company_name,
                "description": report.company_research.description,
                "competitors": report.company_research.key_competitors,
                "sources": report.company_research.sources
            },
            "market": {
                "trend": report.market_trends.search_interest_trend if report.market_trends else None
            },
            "financial": {
                "revenue": report.financial_snapshot.revenue if report.financial_snapshot else None,
                "market_cap": report.financial_snapshot.market_cap if report.financial_snapshot else None,
                "risk_assessment": report.financial_snapshot.risk_assessment if report.financial_snapshot else None
            }
        }
        
        # Cross-framework insights
        cross_framework_insights = self._generate_cross_framework_insights(
            report,
            enhanced_frameworks
        )
        
        return DetailedAnalysisLayer(
            framework_breakdowns=framework_breakdowns,
            supporting_data=supporting_data,
            cross_framework_insights=cross_framework_insights,
            risk_assessments={
                "risks": [r.dict() for r in risk_opportunity_matrix.risks[:5]],
                "risk_heatmap": risk_opportunity_matrix.risk_heatmap
            },
            opportunities={
                "opportunities": [o.dict() for o in risk_opportunity_matrix.opportunities[:5]],
                "prioritization": risk_opportunity_matrix.opportunity_prioritization
            }
        )
    
    def _build_supporting_appendices(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any]
    ) -> SupportingAppendices:
        """Build supporting appendices"""
        
        # Data sources
        data_sources = []
        if report.company_research:
            data_sources.append({
                "type": "Research",
                "sources": report.company_research.sources,
                "description": "Web research via Tavily API"
            })
        if report.market_trends:
            data_sources.append({
                "type": "Market Trends",
                "description": "Google Trends data"
            })
        if report.financial_snapshot:
            data_sources.append({
                "type": "Financial Data",
                "description": "SEC EDGAR and yfinance data"
            })
        
        # Detailed metrics
        detailed_metrics = {
            "confidence_score": report.executive_summary.confidence_score,
            "frameworks_applied": len([k for k in enhanced_frameworks.keys() if enhanced_frameworks[k]]),
            "data_completeness": self._assess_data_completeness(report)
        }
        
        # Frameworks applied
        frameworks_applied = []
        if report.framework_analysis.porter_five_forces:
            frameworks_applied.append("Porter's Five Forces")
        if report.framework_analysis.swot_analysis:
            frameworks_applied.append("SWOT Analysis")
        if report.framework_analysis.pestel_analysis:
            frameworks_applied.append("PESTEL Analysis")
        if report.framework_analysis.blue_ocean_strategy:
            frameworks_applied.append("Blue Ocean Strategy")
        
        return SupportingAppendices(
            data_sources=data_sources,
            detailed_metrics=detailed_metrics,
            frameworks_applied=frameworks_applied
        )
    
    def _build_competitive_intelligence(self, report: StrategicReport) -> CompetitiveIntelligence:
        """Build competitive intelligence section"""
        # This would integrate with competitive intelligence tools
        # For now, use data from research
        competitors = report.company_research.key_competitors if report.company_research else []
        
        competitor_matrix = [
            {
                "competitor_name": comp,
                "key_strengths": [],
                "key_weaknesses": [],
                "recent_movements": []
            }
            for comp in competitors[:5]  # Top 5 competitors
        ]
        
        return CompetitiveIntelligence(
            competitor_matrix=competitor_matrix,
            market_share_visualization={},
            pricing_analysis={},
            feature_comparison={},
            recent_news=[]
        )
    
    def _build_scenario_planning(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any]
    ) -> ScenarioPlanning:
        """Build scenario planning section"""
        from consultantos.models.enhanced_reports import Scenario
        
        # This would use AI to generate scenarios
        # For now, create basic scenarios
        optimistic = Scenario(
            name="Optimistic",
            probability=0.3,
            description="Best-case industry trajectory with positive outcomes",
            key_assumptions=["Favorable market conditions", "Successful strategy execution"],
            financial_projections={"growth": "+15%"}
        )
        
        base = Scenario(
            name="Base Case",
            probability=0.5,
            description="Most likely industry evolution",
            key_assumptions=["Moderate market conditions", "Average execution"],
            financial_projections={"growth": "+5%"}
        )
        
        pessimistic = Scenario(
            name="Pessimistic",
            probability=0.2,
            description="Industry headwinds and challenges",
            key_assumptions=["Challenging market conditions", "Execution difficulties"],
            financial_projections={"growth": "-10%"}
        )
        
        return ScenarioPlanning(
            optimistic_scenario=optimistic,
            base_scenario=base,
            pessimistic_scenario=pessimistic,
            scenario_comparison={}
        )
    
    def _build_confidence_indicators(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any]
    ) -> Dict[str, ConfidenceLevel]:
        """Build confidence indicators for each finding"""
        indicators = {}
        
        # Overall confidence
        if report.executive_summary.confidence_score >= 0.8:
            indicators["overall"] = ConfidenceLevel.HIGH
        elif report.executive_summary.confidence_score >= 0.6:
            indicators["overall"] = ConfidenceLevel.MEDIUM
        else:
            indicators["overall"] = ConfidenceLevel.LOW
        
        # Framework-specific confidence
        for framework_name in enhanced_frameworks.keys():
            indicators[framework_name] = ConfidenceLevel.MEDIUM
        
        return indicators
    
    def _build_quality_metrics(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build quality metrics"""
        return {
            "data_completeness": self._assess_data_completeness(report),
            "analysis_depth": len(enhanced_frameworks),
            "external_research": report.company_research is not None,
            "real_time_data": report.market_trends is not None,
            "assumptions_documented": True
        }
    
    def _generate_cross_framework_insights(
        self,
        report: StrategicReport,
        enhanced_frameworks: Dict[str, Any]
    ) -> List[str]:
        """Generate insights that connect across frameworks"""
        insights = []
        
        # Example: Connect Porter's intensity with SWOT threats
        if enhanced_frameworks.get("porter") and enhanced_frameworks.get("swot"):
            insights.append(
                "High competitive intensity from Porter's analysis aligns with external threats "
                "identified in SWOT, suggesting need for defensive strategy."
            )
        
        # Example: Connect opportunities across frameworks
        if enhanced_frameworks.get("swot") and enhanced_frameworks.get("blue_ocean"):
            insights.append(
                "SWOT opportunities can be pursued through Blue Ocean value innovation strategies."
            )
        
        return insights
    
    def _assess_data_completeness(self, report: StrategicReport) -> float:
        """Assess data completeness score (0-1)"""
        completeness = 0.0
        
        if report.company_research:
            completeness += 0.3
        if report.market_trends:
            completeness += 0.2
        if report.financial_snapshot:
            completeness += 0.3
        if report.framework_analysis:
            completeness += 0.2
        
        return min(completeness, 1.0)

