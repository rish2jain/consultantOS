"""
Framework Enhancement Service

Enhances base framework analysis with:
- Detailed metrics and scoring
- Strategic implications
- Risk/opportunity assessments
- Competitive intelligence
- Actionable insights
"""
from typing import Dict, Any, Optional, List
from consultantos.models import (
    StrategicReport,
    FrameworkAnalysis,
    PortersFiveForces,
    SWOTAnalysis,
    PESTELAnalysis,
    BlueOceanStrategy
)
from consultantos.models.enhanced_reports import (
    EnhancedPortersFiveForces,
    EnhancedSWOTAnalysis,
    EnhancedPESTELAnalysis,
    EnhancedBlueOceanStrategy,
    PorterForceDetail,
    SWOTElement,
    PESTELFactor,
    BlueOceanAction,
    Timeline,
    ImpactLevel,
    ConfidenceLevel
)
from consultantos.agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class FrameworkEnhancementService:
    """Enhances framework analysis with detailed metrics and insights"""
    
    def __init__(self, enhancement_agent: Optional[BaseAgent] = None):
        """
        Initialize enhancement service.
        
        Args:
            enhancement_agent: Optional agent for AI-powered enhancements
        """
        self.enhancement_agent = enhancement_agent
    
    async def enhance_framework_analysis(
        self,
        framework_analysis: FrameworkAnalysis,
        report: StrategicReport
    ) -> Dict[str, Any]:
        """
        Enhance framework analysis with detailed metrics.
        
        Args:
            framework_analysis: Base framework analysis
            report: Full strategic report for context
            
        Returns:
            Dictionary with enhanced framework outputs
        """
        enhanced = {}
        
        if framework_analysis.porter_five_forces:
            enhanced["porter"] = await self._enhance_porter(
                framework_analysis.porter_five_forces,
                report
            )
        
        if framework_analysis.swot_analysis:
            enhanced["swot"] = await self._enhance_swot(
                framework_analysis.swot_analysis,
                report
            )
        
        if framework_analysis.pestel_analysis:
            enhanced["pestel"] = await self._enhance_pestel(
                framework_analysis.pestel_analysis,
                report
            )
        
        if framework_analysis.blue_ocean_strategy:
            enhanced["blue_ocean"] = await self._enhance_blue_ocean(
                framework_analysis.blue_ocean_strategy,
                report
            )
        
        return enhanced
    
    async def _enhance_porter(
        self,
        porter: PortersFiveForces,
        report: StrategicReport
    ) -> EnhancedPortersFiveForces:
        """Enhance Porter's Five Forces with detailed metrics"""
        
        # Calculate industry attractiveness score
        avg_score = (
            porter.supplier_power +
            porter.buyer_power +
            porter.competitive_rivalry +
            porter.threat_of_substitutes +
            porter.threat_of_new_entrants
        ) / 5.0
        
        # Lower average = more attractive (inverse relationship)
        attractiveness_score = (5.0 - avg_score) * 20  # Scale to 0-100
        
        # Create detailed force analyses
        supplier_detail = PorterForceDetail(
            score=porter.supplier_power,
            assessment=porter.detailed_analysis.get("supplier_power", "Analysis pending"),
            strategic_implications=self._generate_strategic_implications(
                "supplier", porter.supplier_power
            ),
            risk_score=self._score_to_risk(porter.supplier_power),
            opportunity_score=self._score_to_opportunity(porter.supplier_power)
        )
        
        buyer_detail = PorterForceDetail(
            score=porter.buyer_power,
            assessment=porter.detailed_analysis.get("buyer_power", "Analysis pending"),
            strategic_implications=self._generate_strategic_implications(
                "buyer", porter.buyer_power
            ),
            risk_score=self._score_to_risk(porter.buyer_power),
            opportunity_score=self._score_to_opportunity(porter.buyer_power)
        )
        
        rivalry_detail = PorterForceDetail(
            score=porter.competitive_rivalry,
            assessment=porter.detailed_analysis.get("competitive_rivalry", "Analysis pending"),
            strategic_implications=self._generate_strategic_implications(
                "rivalry", porter.competitive_rivalry
            ),
            risk_score=self._score_to_risk(porter.competitive_rivalry),
            opportunity_score=self._score_to_opportunity(porter.competitive_rivalry)
        )
        
        substitutes_detail = PorterForceDetail(
            score=porter.threat_of_substitutes,
            assessment=porter.detailed_analysis.get("threat_of_substitutes", "Analysis pending"),
            strategic_implications=self._generate_strategic_implications(
                "substitutes", porter.threat_of_substitutes
            ),
            risk_score=self._score_to_risk(porter.threat_of_substitutes),
            opportunity_score=self._score_to_opportunity(porter.threat_of_substitutes)
        )
        
        entrants_detail = PorterForceDetail(
            score=porter.threat_of_new_entrants,
            assessment=porter.detailed_analysis.get("threat_of_new_entrants", "Analysis pending"),
            strategic_implications=self._generate_strategic_implications(
                "entrants", porter.threat_of_new_entrants
            ),
            risk_score=self._score_to_risk(porter.threat_of_new_entrants),
            opportunity_score=self._score_to_opportunity(porter.threat_of_new_entrants)
        )
        
        # Build risk-opportunity matrix
        risk_opp_matrix = {
            "supplier_power": {
                "risk": self._score_to_risk(porter.supplier_power),
                "opportunity": self._score_to_opportunity(porter.supplier_power)
            },
            "buyer_power": {
                "risk": self._score_to_risk(porter.buyer_power),
                "opportunity": self._score_to_opportunity(porter.buyer_power)
            },
            "competitive_rivalry": {
                "risk": self._score_to_risk(porter.competitive_rivalry),
                "opportunity": self._score_to_opportunity(porter.competitive_rivalry)
            },
            "threat_of_substitutes": {
                "risk": self._score_to_risk(porter.threat_of_substitutes),
                "opportunity": self._score_to_opportunity(porter.threat_of_substitutes)
            },
            "threat_of_new_entrants": {
                "risk": self._score_to_risk(porter.threat_of_new_entrants),
                "opportunity": self._score_to_opportunity(porter.threat_of_new_entrants)
            }
        }
        
        # Generate cross-force strategic implications
        strategic_implications = self._generate_cross_force_implications(porter)
        
        return EnhancedPortersFiveForces(
            supplier_power=supplier_detail,
            buyer_power=buyer_detail,
            competitive_rivalry=rivalry_detail,
            threat_of_substitutes=substitutes_detail,
            threat_of_new_entrants=entrants_detail,
            overall_intensity=porter.overall_intensity,
            industry_attractiveness_score=attractiveness_score,
            risk_opportunity_matrix=risk_opp_matrix,
            strategic_implications=strategic_implications
        )
    
    async def _enhance_swot(
        self,
        swot: SWOTAnalysis,
        report: StrategicReport
    ) -> EnhancedSWOTAnalysis:
        """Enhance SWOT analysis with actionable strategies"""
        
        # Convert to enhanced SWOT elements
        strengths = [
            SWOTElement(
                description=s,
                importance_score=self._calculate_importance(s),
                impact_level=self._determine_impact_level(s),
                confidence=ConfidenceLevel.MEDIUM
            )
            for s in swot.strengths
        ]
        
        weaknesses = [
            SWOTElement(
                description=w,
                importance_score=self._calculate_importance(w),
                impact_level=self._determine_impact_level(w),
                confidence=ConfidenceLevel.MEDIUM
            )
            for w in swot.weaknesses
        ]
        
        opportunities = [
            SWOTElement(
                description=o,
                importance_score=self._calculate_importance(o),
                impact_level=self._determine_impact_level(o),
                confidence=ConfidenceLevel.MEDIUM,
                timeline=self._determine_timeline(o)
            )
            for o in swot.opportunities
        ]
        
        threats = [
            SWOTElement(
                description=t,
                importance_score=self._calculate_importance(t),
                impact_level=self._determine_impact_level(t),
                confidence=ConfidenceLevel.MEDIUM,
                timeline=self._determine_timeline(t)
            )
            for t in swot.threats
        ]
        
        # Generate actionable strategies
        strengths_to_leverage = {
            s.description: self._generate_leverage_strategies(s.description)
            for s in strengths
        }
        
        weaknesses_to_address = {
            w.description: {
                "mitigation_strategies": self._generate_mitigation_strategies(w.description),
                "timeline": Timeline.SHORT_TERM,
                "priority": "medium"
            }
            for w in weaknesses
        }
        
        opportunities_to_pursue = {
            o.description: {
                "impact": o.impact_level.value,
                "feasibility": "medium",
                "timeline": o.timeline.value if o.timeline else "short_term"
            }
            for o in opportunities
        }
        
        threats_to_monitor = {
            t.description: {
                "early_warning_indicators": self._generate_warning_indicators(t.description),
                "contingency_plans": self._generate_contingency_plans(t.description)
            }
            for t in threats
        }
        
        # Generate strategic combinations (S+O, W+T)
        strategic_combinations = self._generate_strategic_combinations(
            strengths, weaknesses, opportunities, threats
        )
        
        # Generate roadmap
        roadmap = self._generate_swot_roadmap(
            strengths, weaknesses, opportunities, threats
        )
        
        return EnhancedSWOTAnalysis(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            strengths_to_leverage=strengths_to_leverage,
            weaknesses_to_address=weaknesses_to_address,
            opportunities_to_pursue=opportunities_to_pursue,
            threats_to_monitor=threats_to_monitor,
            strategic_combinations=strategic_combinations,
            roadmap=roadmap
        )
    
    async def _enhance_pestel(
        self,
        pestel: PESTELAnalysis,
        report: StrategicReport
    ) -> EnhancedPESTELAnalysis:
        """Enhance PESTEL analysis with trend analysis"""
        
        political = [
            PESTELFactor(
                factor=factor,
                current_state="Current state analysis",
                trend_direction="Stable",
                timeline="12-24 months",
                impact_level=ImpactLevel.MEDIUM,
                risk_score=5.0
            )
            for factor in pestel.political
        ]
        
        economic = [
            PESTELFactor(
                factor=factor,
                current_state="Current state analysis",
                trend_direction="Stable",
                timeline="6-12 months",
                impact_level=ImpactLevel.MEDIUM,
                risk_score=5.0
            )
            for factor in pestel.economic
        ]
        
        social = [
            PESTELFactor(
                factor=factor,
                current_state="Current state analysis",
                trend_direction="Stable",
                timeline="12-18 months",
                impact_level=ImpactLevel.MEDIUM,
                risk_score=5.0
            )
            for factor in pestel.social
        ]
        
        technological = [
            PESTELFactor(
                factor=factor,
                current_state="Current state analysis",
                trend_direction="Rapid change",
                timeline="6-12 months",
                impact_level=ImpactLevel.HIGH,
                risk_score=6.0
            )
            for factor in pestel.technological
        ]
        
        environmental = [
            PESTELFactor(
                factor=factor,
                current_state="Current state analysis",
                trend_direction="Increasing importance",
                timeline="12-24 months",
                impact_level=ImpactLevel.MEDIUM,
                risk_score=5.0
            )
            for factor in pestel.environmental
        ]
        
        legal = [
            PESTELFactor(
                factor=factor,
                current_state="Current state analysis",
                trend_direction="Stable",
                timeline="12-24 months",
                impact_level=ImpactLevel.MEDIUM,
                risk_score=5.0
            )
            for factor in pestel.legal
        ]
        
        # Calculate overall risk score
        all_factors = political + economic + social + technological + environmental + legal
        overall_risk = sum(f.risk_score for f in all_factors) / len(all_factors) if all_factors else 5.0
        
        return EnhancedPESTELAnalysis(
            political=political,
            economic=economic,
            social=social,
            technological=technological,
            environmental=environmental,
            legal=legal,
            overall_risk_score=overall_risk
        )
    
    async def _enhance_blue_ocean(
        self,
        blue_ocean: BlueOceanStrategy,
        report: StrategicReport
    ) -> EnhancedBlueOceanStrategy:
        """Enhance Blue Ocean Strategy with implementation details"""
        
        eliminate = [
            BlueOceanAction(
                action=action,
                rationale="Reduce costs and focus on value-adding factors",
                estimated_impact=ImpactLevel.MEDIUM,
                implementation_complexity="Medium",
                timeline=Timeline.SHORT_TERM
            )
            for action in blue_ocean.eliminate
        ]
        
        reduce = [
            BlueOceanAction(
                action=action,
                rationale="Optimize resource allocation",
                estimated_impact=ImpactLevel.MEDIUM,
                implementation_complexity="Low",
                timeline=Timeline.SHORT_TERM
            )
            for action in blue_ocean.reduce
        ]
        
        raise_factors = [
            BlueOceanAction(
                action=action,
                rationale="Create differentiation and competitive advantage",
                estimated_impact=ImpactLevel.HIGH,
                implementation_complexity="High",
                timeline=Timeline.MEDIUM_TERM
            )
            for action in blue_ocean.raise_factors
        ]
        
        create = [
            BlueOceanAction(
                action=action,
                rationale="Open new market space and create value innovation",
                estimated_impact=ImpactLevel.HIGH,
                implementation_complexity="High",
                timeline=Timeline.MEDIUM_TERM
            )
            for action in blue_ocean.create
        ]
        
        return EnhancedBlueOceanStrategy(
            eliminate=eliminate,
            reduce=reduce,
            raise_factors=raise_factors,
            create=create,
            value_innovation=[action.action for action in create],
            implementation_roadmap=self._generate_blue_ocean_roadmap(
                eliminate, reduce, raise_factors, create
            )
        )
    
    # Helper methods
    
    def _generate_strategic_implications(self, force_type: str, score: float) -> List[str]:
        """Generate strategic implications from force score"""
        implications = []
        
        if score >= 4.0:
            implications.append(f"High {force_type} force requires defensive strategy")
            implications.append(f"Consider building barriers or switching costs")
        elif score <= 2.0:
            implications.append(f"Low {force_type} force presents opportunity")
            implications.append(f"Leverage favorable position for competitive advantage")
        else:
            implications.append(f"Moderate {force_type} force - monitor closely")
        
        return implications
    
    def _score_to_risk(self, score: float) -> float:
        """Convert Porter score to risk score (higher score = higher risk)"""
        return score * 2.0  # Scale 1-5 to 2-10
    
    def _score_to_opportunity(self, score: float) -> float:
        """Convert Porter score to opportunity score (lower score = higher opportunity)"""
        return (5.0 - score) * 2.0  # Inverse relationship
    
    def _generate_cross_force_implications(self, porter: PortersFiveForces) -> List[str]:
        """Generate strategic implications across all forces"""
        implications = []
        
        avg_score = (
            porter.supplier_power +
            porter.buyer_power +
            porter.competitive_rivalry +
            porter.threat_of_substitutes +
            porter.threat_of_new_entrants
        ) / 5.0
        
        if avg_score >= 4.0:
            implications.append("Industry structure is challenging - focus on differentiation")
            implications.append("Consider vertical integration to reduce supplier/buyer power")
        elif avg_score <= 2.0:
            implications.append("Favorable industry structure - capitalize on opportunities")
            implications.append("Invest in growth and market expansion")
        else:
            implications.append("Mixed competitive dynamics - selective strategy required")
        
        return implications
    
    def _calculate_importance(self, element: str) -> float:
        """Calculate importance score for SWOT element"""
        # Simple heuristic - can be enhanced with AI
        if any(word in element.lower() for word in ["critical", "major", "significant", "key"]):
            return 9.0
        elif any(word in element.lower() for word in ["important", "notable"]):
            return 7.0
        else:
            return 5.0
    
    def _determine_impact_level(self, element: str) -> ImpactLevel:
        """Determine impact level from element text"""
        element_lower = element.lower()
        if any(word in element_lower for word in ["high", "major", "significant", "critical"]):
            return ImpactLevel.HIGH
        elif any(word in element_lower for word in ["moderate", "medium", "some"]):
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW
    
    def _determine_timeline(self, element: str) -> Optional[Timeline]:
        """Determine timeline from element text"""
        element_lower = element.lower()
        if any(word in element_lower for word in ["immediate", "urgent", "now"]):
            return Timeline.IMMEDIATE
        elif any(word in element_lower for word in ["short", "soon", "months"]):
            return Timeline.SHORT_TERM
        elif any(word in element_lower for word in ["medium", "year"]):
            return Timeline.MEDIUM_TERM
        else:
            return Timeline.LONG_TERM
    
    def _generate_leverage_strategies(self, strength: str) -> List[str]:
        """Generate strategies to leverage a strength"""
        return [
            f"Use {strength} to differentiate from competitors",
            f"Build marketing campaigns around {strength}",
            f"Expand {strength} to new markets or segments"
        ]
    
    def _generate_mitigation_strategies(self, weakness: str) -> List[str]:
        """Generate strategies to address a weakness"""
        return [
            f"Develop action plan to address {weakness}",
            f"Allocate resources to improve {weakness}",
            f"Monitor progress on {weakness} mitigation"
        ]
    
    def _generate_warning_indicators(self, threat: str) -> List[str]:
        """Generate early warning indicators for a threat"""
        return [
            f"Monitor market signals related to {threat}",
            f"Track competitor actions in {threat} area",
            f"Watch for regulatory changes affecting {threat}"
        ]
    
    def _generate_contingency_plans(self, threat: str) -> List[str]:
        """Generate contingency plans for a threat"""
        return [
            f"Develop response plan for {threat}",
            f"Identify alternative strategies if {threat} materializes",
            f"Build resilience to {threat} impact"
        ]
    
    def _generate_strategic_combinations(
        self,
        strengths: List[SWOTElement],
        weaknesses: List[SWOTElement],
        opportunities: List[SWOTElement],
        threats: List[SWOTElement]
    ) -> List[Dict[str, Any]]:
        """Generate S+O and W+T strategic combinations"""
        combinations = []
        
        # S+O combinations (use strengths to pursue opportunities)
        for strength in strengths[:2]:  # Top 2 strengths
            for opportunity in opportunities[:2]:  # Top 2 opportunities
                combinations.append({
                    "type": "S+O",
                    "strength": strength.description,
                    "opportunity": opportunity.description,
                    "strategy": f"Leverage {strength.description} to pursue {opportunity.description}"
                })
        
        # W+T mitigations (address weaknesses to counter threats)
        for weakness in weaknesses[:2]:  # Top 2 weaknesses
            for threat in threats[:2]:  # Top 2 threats
                combinations.append({
                    "type": "W+T",
                    "weakness": weakness.description,
                    "threat": threat.description,
                    "strategy": f"Address {weakness.description} to mitigate {threat.description}"
                })
        
        return combinations
    
    def _generate_swot_roadmap(
        self,
        strengths: List[SWOTElement],
        weaknesses: List[SWOTElement],
        opportunities: List[SWOTElement],
        threats: List[SWOTElement]
    ) -> List[Dict[str, Any]]:
        """Generate timeline roadmap for SWOT factors"""
        roadmap = []
        
        # Immediate: Address critical threats and pursue quick wins
        roadmap.append({
            "timeline": "0-3 months",
            "focus": "Critical threats and quick-win opportunities",
            "actions": [t.description for t in threats[:2]] + [o.description for o in opportunities[:1]]
        })
        
        # Short-term: Address weaknesses, leverage strengths
        roadmap.append({
            "timeline": "3-12 months",
            "focus": "Weakness mitigation and strength leverage",
            "actions": [w.description for w in weaknesses[:2]] + [s.description for s in strengths[:2]]
        })
        
        # Medium-term: Strategic opportunities
        roadmap.append({
            "timeline": "12-24 months",
            "focus": "Long-term opportunities and strategic positioning",
            "actions": [o.description for o in opportunities[1:]]
        })
        
        return roadmap
    
    def _generate_blue_ocean_roadmap(
        self,
        eliminate: List[BlueOceanAction],
        reduce: List[BlueOceanAction],
        raise_factors: List[BlueOceanAction],
        create: List[BlueOceanAction]
    ) -> List[Dict[str, Any]]:
        """Generate implementation roadmap for Blue Ocean strategy"""
        roadmap = []
        
        # Phase 1: Eliminate and Reduce (quick wins)
        roadmap.append({
            "phase": 1,
            "timeline": "0-6 months",
            "actions": [a.action for a in eliminate[:2]] + [a.action for a in reduce[:2]],
            "focus": "Cost reduction and efficiency"
        })
        
        # Phase 2: Raise (differentiation
        roadmap.append({
            "phase": 2,
            "timeline": "6-18 months",
            "actions": [a.action for a in raise_factors[:2]],
            "focus": "Value creation and differentiation"
        })
        
        # Phase 3: Create (innovation)
        roadmap.append({
            "phase": 3,
            "timeline": "18-36 months",
            "actions": [a.action for a in create],
            "focus": "Market creation and value innovation"
        })
        
        return roadmap

