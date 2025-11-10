"""
Decision Intelligence Engine for ConsultantOS

Transforms framework analyses (Porter, SWOT, PESTEL, Blue Ocean) into
actionable decision briefs with ROI models, prioritization, and timelines.

Architecture:
    - Inherits from BaseAgent for consistent Gemini + Instructor setup
    - Processes FrameworkAnalysis → DecisionBrief transformation
    - Uses structured outputs for reproducible decision generation
    - Implements sophisticated prioritization algorithms

Key Features:
    - ROI calculation for strategic options
    - Multi-criteria prioritization (impact × urgency × confidence)
    - Framework-specific transformation logic
    - Portfolio-level financial modeling
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import (
    FrameworkAnalysis,
    PortersFiveForces,
    SWOTAnalysis,
    BlueOceanStrategy,
    PESTELAnalysis
)
from consultantos.models.decisions import (
    DecisionBrief,
    StrategicDecision,
    DecisionOption,
    DecisionUrgency,
    DecisionCategory
)

logger = logging.getLogger(__name__)


class DecisionIntelligenceEngine(BaseAgent):
    """
    Transform framework analyses into actionable decision briefs

    This agent converts strategic frameworks (Porter's 5 Forces, SWOT, PESTEL,
    Blue Ocean) into prioritized, executable decisions with detailed ROI models,
    implementation plans, and risk assessments.

    Transformation Logic:
        Porter's 5 Forces → Competitive positioning decisions
        SWOT → Exploitation/mitigation/pursuit/defense decisions
        Blue Ocean → Innovation and differentiation decisions
        PESTEL → Risk mitigation and opportunity capture decisions

    Prioritization:
        Score = (Impact × 0.4) + (Urgency × 0.3) + (Strategic Fit × 0.2) + (ROI × 0.1)
    """

    def __init__(self, timeout: int = 120):
        """
        Initialize Decision Intelligence Engine

        Args:
            timeout: Agent execution timeout in seconds (default: 120s for complex analysis)
        """
        super().__init__(
            name="decision_intelligence_engine",
            timeout=timeout
        )
        self.instruction = """
        You are an elite strategy consultant specializing in decision intelligence.

        Your role is to transform strategic frameworks into executive-ready decisions:
        - Convert framework insights into specific, actionable decisions
        - Build detailed ROI models for each strategic option
        - Assess risks and create mitigation strategies
        - Prioritize based on impact, urgency, and strategic fit
        - Provide clear implementation roadmaps

        Standards:
        - Every decision must have 2-4 viable options with financial models
        - ROI calculations must be evidence-based and conservative
        - Implementation timelines must be realistic (30-730 days)
        - Risk assessments must be comprehensive with mitigation plans
        - Recommendations must be clear and defensible
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute decision intelligence transformation

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - industry: Industry context
                - framework_analysis: FrameworkAnalysis object with Porter/SWOT/Blue Ocean/PESTEL
                - revenue: Optional annual revenue for scaling ROI calculations (default: $1B)

        Returns:
            Dict containing:
                - success: bool
                - data: DecisionBrief object with prioritized decisions

        Raises:
            ValueError: If framework_analysis is missing
            Exception: If decision generation fails
        """
        company = input_data.get("company", "Unknown Company")
        industry = input_data.get("industry", "Unknown Industry")
        framework_analysis: FrameworkAnalysis = input_data.get("framework_analysis")
        revenue = input_data.get("revenue", 1_000_000_000)  # Default $1B for scaling

        if not framework_analysis:
            raise ValueError("framework_analysis is required for decision intelligence")

        logger.info(
            f"Generating decision brief for {company}",
            extra={"company": company, "industry": industry}
        )

        # Generate decisions from each framework
        all_decisions: List[StrategicDecision] = []

        if framework_analysis.porter_five_forces:
            porter_decisions = await self._porter_to_decisions(
                framework_analysis.porter_five_forces,
                company,
                industry,
                revenue
            )
            all_decisions.extend(porter_decisions)

        if framework_analysis.swot_analysis:
            swot_decisions = await self._swot_to_decisions(
                framework_analysis.swot_analysis,
                company,
                industry,
                revenue
            )
            all_decisions.extend(swot_decisions)

        if framework_analysis.blue_ocean_strategy:
            blue_ocean_decisions = await self._blue_ocean_to_decisions(
                framework_analysis.blue_ocean_strategy,
                company,
                industry,
                revenue
            )
            all_decisions.extend(blue_ocean_decisions)

        # Prioritize all decisions
        prioritized_decisions = self._prioritize_decisions(all_decisions)

        # Split into critical and high priority
        critical_decisions = [d for d in prioritized_decisions if d.urgency == DecisionUrgency.CRITICAL]
        high_priority_decisions = [d for d in prioritized_decisions if d.urgency == DecisionUrgency.HIGH]

        # Calculate strategic themes
        strategic_themes = self._extract_strategic_themes(prioritized_decisions)

        # Calculate overall confidence
        avg_confidence = sum(
            sum(opt.success_probability for opt in d.options) / len(d.options) if d.options else 50.0
            for d in prioritized_decisions
        ) / len(prioritized_decisions) if prioritized_decisions else 50.0

        # Generate decision brief
        decision_brief = DecisionBrief(
            company=company,
            generated_at=datetime.utcnow().isoformat(),
            critical_decisions=critical_decisions[:3],  # Top 3 critical
            high_priority_decisions=high_priority_decisions[:5],  # Top 5 high priority
            top_decision=prioritized_decisions[0] if prioritized_decisions else None,
            decision_count=len(prioritized_decisions),
            strategic_themes=strategic_themes,
            resource_conflicts=self._identify_resource_conflicts(prioritized_decisions),
            confidence_score=avg_confidence
        )

        logger.info(
            f"Generated {len(prioritized_decisions)} decisions for {company}",
            extra={
                "company": company,
                "decision_count": len(prioritized_decisions),
                "critical_count": len(critical_decisions),
                "avg_confidence": avg_confidence
            }
        )

        return {
            "success": True,
            "data": decision_brief
        }

    async def _porter_to_decisions(
        self,
        porter: PortersFiveForces,
        company: str,
        industry: str,
        revenue: float
    ) -> List[StrategicDecision]:
        """
        Transform Porter's Five Forces into strategic decisions

        Decision Logic:
            - High supplier power (>3.5) → Supplier risk mitigation
            - High buyer power (>3.5) → Customer lock-in strategies
            - High rivalry (>4.0) → Differentiation or cost leadership
            - High substitutes (>3.5) → Innovation urgency
            - High entry threat (>3.5) → Competitive moat building

        Args:
            porter: PortersFiveForces analysis
            company: Company name
            industry: Industry context
            revenue: Annual revenue for ROI scaling

        Returns:
            List of StrategicDecision objects from Porter analysis
        """
        decisions: List[StrategicDecision] = []

        # High supplier power → Supplier risk mitigation
        if porter.supplier_power >= 3.5:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Supplier Power Score: {porter.supplier_power}/5.0 (High)
            Annual Revenue: ${revenue:,.0f}

            Generate a strategic decision for mitigating high supplier power.

            Decision Question: "How should we reduce dependency on powerful suppliers?"
            Context: Suppliers have strong pricing power and control over key inputs
            Stakes: Supply chain risk, margin compression, operational disruption

            Provide 3 strategic options:
            1. Vertical integration (acquire/build supplier capabilities)
            2. Dual sourcing strategy (reduce dependency on single suppliers)
            3. Long-term contracts with price caps

            For EACH option, provide:
            - Investment required (% of revenue, then convert to USD)
            - Expected annual savings (cost reduction or margin protection)
            - ROI multiple (return / investment)
            - Payback period in months
            - Implementation timeline in days (90-365)
            - Success probability (0-100%)
            - Risk level (Low/Medium/High)
            - 2-3 key risks
            - 2-3 mitigation strategies
            - 3-5 implementation steps
            - Strategic fit score (0-100)
            - Competitive advantage gained

            Be specific and realistic based on {industry} industry dynamics.
            Use conservative estimates. All financial figures must be numeric (not strings).
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            # Override specific fields for consistency
            decision.decision_id = f"DEC-PORTER-001"
            decision.decision_category = DecisionCategory.INVESTMENT
            decision.urgency = DecisionUrgency.HIGH
            decision.porter_analysis = f"High supplier power ({porter.supplier_power}/5.0) creates supply chain risk and margin pressure"

            decisions.append(decision)

        # High buyer power → Customer retention/lock-in
        if porter.buyer_power >= 3.5:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Buyer Power Score: {porter.buyer_power}/5.0 (High)
            Annual Revenue: ${revenue:,.0f}

            Generate a strategic decision for addressing high buyer power.

            Decision Question: "How do we build customer switching costs and reduce churn?"
            Context: Customers have strong bargaining power and many alternatives
            Stakes: Price erosion, customer churn, margin compression

            Provide 3 strategic options:
            1. Build switching costs (platform lock-in, deep integrations)
            2. Premium differentiation (justify price premium with unique value)
            3. Create ecosystem effects (network value, community)

            Follow same detailed requirements as previous decisions.
            Focus on customer lifetime value improvement and churn reduction.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-PORTER-002"
            decision.decision_category = DecisionCategory.ORGANIZATIONAL
            decision.urgency = DecisionUrgency.HIGH
            decision.porter_analysis = f"High buyer power ({porter.buyer_power}/5.0) threatens pricing power and customer retention"

            decisions.append(decision)

        # High competitive rivalry → Differentiation
        if porter.competitive_rivalry >= 4.0:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Competitive Rivalry Score: {porter.competitive_rivalry}/5.0 (Intense)
            Annual Revenue: ${revenue:,.0f}

            Generate a strategic decision for intense competitive rivalry.

            Decision Question: "How do we differentiate and escape commoditization?"
            Context: Intense competition eroding margins and forcing price competition
            Stakes: Market share, profitability, long-term viability

            Provide 3 strategic options:
            1. Differentiation strategy (unique value proposition, premium positioning)
            2. Cost leadership (operational efficiency, scale advantages)
            3. Niche focus (underserved segment, specialized offering)

            Show market share impact, margin improvements, and competitive positioning gains.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-PORTER-003"
            decision.decision_category = DecisionCategory.PRODUCT_LAUNCH
            decision.urgency = DecisionUrgency.CRITICAL
            decision.porter_analysis = f"Intense competitive rivalry ({porter.competitive_rivalry}/5.0) requires strategic differentiation"

            decisions.append(decision)

        # High threat of substitutes → Innovation
        if porter.threat_of_substitutes >= 3.5:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Threat of Substitutes Score: {porter.threat_of_substitutes}/5.0 (High)
            Annual Revenue: ${revenue:,.0f}

            Generate a strategic decision to address substitute threats.

            Decision Question: "How do we defend against substitute products/services?"
            Context: Alternative solutions threatening market share and pricing power
            Stakes: Market relevance, revenue erosion, obsolescence risk

            Provide 3 strategic options:
            1. Accelerated innovation (R&D investment, new features, next-gen products)
            2. Ecosystem development (make switching to substitutes costly)
            3. Price/value repositioning (compete on total value, not just price)

            Focus on protecting market share and maintaining pricing power.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-PORTER-004"
            decision.decision_category = DecisionCategory.TECHNOLOGY
            decision.urgency = DecisionUrgency.HIGH
            decision.porter_analysis = f"High threat of substitutes ({porter.threat_of_substitutes}/5.0) demands innovation to maintain relevance"

            decisions.append(decision)

        # High entry threat → Moat building
        if porter.threat_of_new_entrants >= 3.5:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Threat of New Entrants Score: {porter.threat_of_new_entrants}/5.0 (High)
            Annual Revenue: ${revenue:,.0f}

            Generate a strategic decision to build competitive moats.

            Decision Question: "How do we create barriers to entry and protect market position?"
            Context: Low entry barriers making market vulnerable to new competitors
            Stakes: Market share dilution, price pressure, competitive advantage erosion

            Provide 3 strategic options:
            1. Scale advantages (economies of scale, network effects, data moats)
            2. IP and technology moats (patents, proprietary technology, trade secrets)
            3. Brand and customer loyalty (brand equity, switching costs, community)

            Show how each moat increases entry barriers and protects margins.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-PORTER-005"
            decision.decision_category = DecisionCategory.INVESTMENT
            decision.urgency = DecisionUrgency.MEDIUM
            decision.porter_analysis = f"High threat of new entrants ({porter.threat_of_new_entrants}/5.0) requires building defensible moats"

            decisions.append(decision)

        return decisions

    async def _swot_to_decisions(
        self,
        swot: SWOTAnalysis,
        company: str,
        industry: str,
        revenue: float
    ) -> List[StrategicDecision]:
        """
        Transform SWOT into strategic decisions

        Decision Logic:
            - Strengths → Exploitation decisions (double down, expand)
            - Weaknesses → Mitigation decisions (fix or manage)
            - Opportunities → Pursuit decisions (with investment models)
            - Threats → Defense decisions (with timeline urgency)

        Args:
            swot: SWOTAnalysis object
            company: Company name
            industry: Industry context
            revenue: Annual revenue for scaling

        Returns:
            List of StrategicDecision objects from SWOT
        """
        decisions: List[StrategicDecision] = []

        # Top strength → Exploitation decision
        if swot.strengths:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Top Strength: {swot.strengths[0]}
            Revenue: ${revenue:,.0f}

            Generate a decision to EXPLOIT this core strength.

            Decision Question: "How should we capitalize on our key strength to accelerate growth?"
            Context: We have a proven competitive advantage that can be amplified
            Stakes: Growth acceleration, market leadership, margin expansion

            Provide 3 exploitation options:
            1. Market expansion (new geographies, new segments leveraging this strength)
            2. Premium pricing strategy (monetize strength through higher prices)
            3. Adjacent market entry (use strength to enter related markets)

            Show revenue growth potential, market share gains, and competitive advantages.
            All options should leverage the identified strength directly.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-SWOT-101"
            decision.decision_category = DecisionCategory.MARKET_ENTRY
            decision.urgency = DecisionUrgency.HIGH

            decisions.append(decision)

        # Critical weakness → Mitigation decision
        if swot.weaknesses:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Critical Weakness: {swot.weaknesses[0]}
            Revenue: ${revenue:,.0f}

            Generate a decision to MITIGATE this critical weakness.

            Decision Question: "How do we address our key weakness to reduce competitive vulnerability?"
            Context: This weakness is being exploited by competitors or limiting growth
            Stakes: Competitive disadvantage, operational risk, margin erosion

            Provide 3 mitigation options:
            1. Internal fix (process improvement, technology upgrade, talent acquisition)
            2. Strategic partnership or acquisition (fill gap externally)
            3. Strategic repositioning (accept weakness, focus on differentiators)

            Show risk reduction, efficiency gains, and competitive positioning improvements.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-SWOT-102"
            decision.decision_category = DecisionCategory.ORGANIZATIONAL
            decision.urgency = DecisionUrgency.HIGH

            decisions.append(decision)

        # Top opportunity → Pursuit decision
        if swot.opportunities:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Top Opportunity: {swot.opportunities[0]}
            Revenue: ${revenue:,.0f}

            Generate a decision to PURSUE this market opportunity.

            Decision Question: "How should we capture this market opportunity?"
            Context: Emerging market opportunity with growth potential
            Stakes: Market leadership, first-mover advantage, growth trajectory

            Provide 3 pursuit approaches:
            1. Aggressive pursuit (fast investment, first-mover advantage)
            2. Moderate approach (balanced risk/reward, phased rollout)
            3. Cautious entry (pilot, learn, then scale)

            Show expected market share capture, revenue potential, and timing advantages.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-SWOT-103"
            decision.decision_category = DecisionCategory.GEOGRAPHIC_EXPANSION
            decision.urgency = DecisionUrgency.HIGH

            decisions.append(decision)

        # Major threat → Defense decision
        if swot.threats:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Major Threat: {swot.threats[0]}
            Revenue: ${revenue:,.0f}

            Generate a decision to DEFEND against this strategic threat.

            Decision Question: "How do we protect our business from this emerging threat?"
            Context: External threat with potential to disrupt business or erode position
            Stakes: Market share protection, revenue defense, business continuity

            Provide 3 defensive options:
            1. Proactive countermeasures (address threat head-on)
            2. Defensive positioning (fortify existing position)
            3. Strategic pivot (shift business model to avoid threat)

            Emphasize urgency and downside protection.
            Show ROI in terms of revenue/market share preservation.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-SWOT-104"
            decision.decision_category = DecisionCategory.INVESTMENT
            decision.urgency = DecisionUrgency.CRITICAL  # Threats are urgent

            decisions.append(decision)

        return decisions

    async def _blue_ocean_to_decisions(
        self,
        blue_ocean: BlueOceanStrategy,
        company: str,
        industry: str,
        revenue: float
    ) -> List[StrategicDecision]:
        """
        Transform Blue Ocean Strategy into innovation decisions

        Decision Logic:
            - Create factors → Innovation decisions (new value)
            - Raise factors → Investment decisions (superior value)
            - Eliminate factors → Cost optimization decisions
            - Reduce factors → Efficiency decisions

        Args:
            blue_ocean: BlueOceanStrategy object
            company: Company name
            industry: Industry context
            revenue: Annual revenue

        Returns:
            List of StrategicDecision objects from Blue Ocean
        """
        decisions: List[StrategicDecision] = []

        # Create factors → Innovation decision (highest priority)
        if blue_ocean.create:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            New Value Factors to CREATE: {', '.join(blue_ocean.create)}
            Revenue: ${revenue:,.0f}

            Generate a decision to CREATE new value innovation.

            Decision Question: "What new value factors should we introduce to create uncontested market space?"
            Context: Blue ocean opportunity to create differentiation no competitor offers
            Stakes: Market leadership, premium pricing, sustained competitive advantage

            Provide 3 innovation options focusing on different CREATE factors:
            - Each option should introduce unique factors not offered by industry
            - Expected customer willingness to pay for new value
            - Time to market and competitive lead time
            - Technology or capability investments needed

            This is blue ocean territory - show ROI from uncontested market space.
            Higher risk but transformational impact potential.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.8,  # Higher temperature for innovation
                max_tokens=2500
            )

            decision.decision_id = f"DEC-BLUEOCEAN-201"
            decision.decision_category = DecisionCategory.PRODUCT_LAUNCH
            decision.urgency = DecisionUrgency.HIGH

            decisions.append(decision)

        # Raise factors → Strategic investment decision
        if blue_ocean.raise_factors:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Factors to RAISE: {', '.join(blue_ocean.raise_factors)}
            Revenue: ${revenue:,.0f}

            Generate a decision to RAISE key competitive factors.

            Decision Question: "Which factors should we raise well above industry standard?"
            Context: Opportunity to achieve differentiation through superior execution
            Stakes: Premium positioning, market share gains, brand elevation

            Provide 3 investment options:
            - Investment to significantly exceed industry standards on these factors
            - Premium pricing potential from superior value
            - Market share gains from best-in-class execution
            - Brand positioning improvements

            Show ROI from differentiation and premium pricing power.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-BLUEOCEAN-202"
            decision.decision_category = DecisionCategory.INVESTMENT
            decision.urgency = DecisionUrgency.MEDIUM

            decisions.append(decision)

        # Eliminate factors → Cost optimization decision
        if blue_ocean.eliminate:
            prompt = f"""
            Company: {company}
            Industry: {industry}
            Factors to ELIMINATE: {', '.join(blue_ocean.eliminate)}
            Revenue: ${revenue:,.0f}

            Generate a decision to ELIMINATE industry-standard factors.

            Decision Question: "Which industry-standard factors should we completely eliminate?"
            Context: Opportunity to reduce costs by removing factors customers don't value
            Stakes: Cost structure optimization, strategic repositioning

            Provide 3 elimination strategies:
            - Cost savings from removing these factors
            - Customer segments who won't miss eliminated factors (target these)
            - Operational simplification benefits
            - Competitive repositioning and messaging

            Show ROI from cost reduction while maintaining or growing revenue.
            Lower risk with clear cost savings.
            """

            decision = await self.generate_structured(
                prompt=prompt,
                response_model=StrategicDecision,
                temperature=0.7,
                max_tokens=2500
            )

            decision.decision_id = f"DEC-BLUEOCEAN-203"
            decision.decision_category = DecisionCategory.ORGANIZATIONAL
            decision.urgency = DecisionUrgency.MEDIUM

            decisions.append(decision)

        return decisions

    def _prioritize_decisions(
        self,
        decisions: List[StrategicDecision]
    ) -> List[StrategicDecision]:
        """
        Prioritize decisions using multi-criteria scoring

        Scoring Formula:
            Score = (Urgency × 0.4) + (Avg Strategic Fit × 0.3) + (Avg Success Prob × 0.2) + (Avg ROI × 0.1)

        Where:
            - Urgency: CRITICAL=100, HIGH=75, MEDIUM=50, LOW=25
            - Strategic Fit: Average across options (0-100)
            - Success Probability: Average across options (0-100)
            - ROI: Average ROI multiple normalized to 0-100 scale

        Args:
            decisions: List of StrategicDecision objects

        Returns:
            Sorted list (highest priority first)
        """

        def calculate_priority_score(decision: StrategicDecision) -> float:
            """Calculate priority score for a single decision"""

            # Urgency score (0-100)
            urgency_map = {
                DecisionUrgency.CRITICAL: 100.0,
                DecisionUrgency.HIGH: 75.0,
                DecisionUrgency.MEDIUM: 50.0,
                DecisionUrgency.LOW: 25.0
            }
            urgency_score = urgency_map.get(decision.urgency, 50.0)

            # Average strategic fit across options
            strategic_fit_scores = [opt.strategic_fit for opt in decision.options if hasattr(opt, 'strategic_fit')]
            avg_strategic_fit = sum(strategic_fit_scores) / len(strategic_fit_scores) if strategic_fit_scores else 50.0

            # Average success probability
            success_probs = [opt.success_probability for opt in decision.options]
            avg_success_prob = sum(success_probs) / len(success_probs) if success_probs else 50.0

            # Average ROI (normalize to 0-100, cap at 10x)
            roi_multiples = [min(opt.roi_multiple, 10.0) for opt in decision.options if hasattr(opt, 'roi_multiple')]
            avg_roi = (sum(roi_multiples) / len(roi_multiples) * 10) if roi_multiples else 50.0

            # Weighted combination
            priority = (
                urgency_score * 0.4 +
                avg_strategic_fit * 0.3 +
                avg_success_prob * 0.2 +
                avg_roi * 0.1
            )

            return priority

        # Calculate scores and sort
        decision_scores = [
            (decision, calculate_priority_score(decision))
            for decision in decisions
        ]
        decision_scores.sort(key=lambda x: x[1], reverse=True)

        return [decision for decision, score in decision_scores]

    def _extract_strategic_themes(
        self,
        decisions: List[StrategicDecision]
    ) -> List[str]:
        """
        Extract common strategic themes from decisions

        Args:
            decisions: List of strategic decisions

        Returns:
            List of 3-5 strategic themes
        """
        themes = []

        # Count decision categories
        category_counts = {}
        for decision in decisions:
            cat = decision.decision_category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Top 3 categories become themes
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_categories[:3]:
            themes.append(f"{cat.replace('_', ' ').title()} ({count} decisions)")

        # Add urgency theme if many critical decisions
        critical_count = sum(1 for d in decisions if d.urgency == DecisionUrgency.CRITICAL)
        if critical_count >= 2:
            themes.append(f"Urgent action required ({critical_count} critical decisions)")

        return themes[:5]  # Max 5 themes

    def _identify_resource_conflicts(
        self,
        decisions: List[StrategicDecision]
    ) -> List[str]:
        """
        Identify potential resource conflicts between decisions

        Args:
            decisions: List of strategic decisions

        Returns:
            List of identified resource conflicts
        """
        conflicts = []

        # Check for high investment requirements
        high_investment_decisions = [
            d for d in decisions
            if any(opt.implementation_cost == "high" for opt in d.options)
        ]

        if len(high_investment_decisions) >= 3:
            conflicts.append(
                f"Capital allocation: {len(high_investment_decisions)} decisions require high investment"
            )

        # Check for technology decisions
        tech_decisions = [
            d for d in decisions
            if d.decision_category == DecisionCategory.TECHNOLOGY
        ]

        if len(tech_decisions) >= 2:
            conflicts.append(
                f"Engineering resources: {len(tech_decisions)} technology initiatives competing for talent"
            )

        # Check for simultaneous critical decisions
        critical_decisions = [d for d in decisions if d.urgency == DecisionUrgency.CRITICAL]

        if len(critical_decisions) >= 3:
            conflicts.append(
                f"Executive attention: {len(critical_decisions)} critical decisions requiring immediate focus"
            )

        return conflicts[:5]  # Max 5 conflicts
