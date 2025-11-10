"""
Disruption Agent - Vulnerability assessment using Christensen's disruption theory

Purpose: Detect asymmetric competitive threats and disruption vulnerabilities using
Jobs-to-be-Done analysis, technology shift tracking, and business model innovation.

Integrates data from:
- Market Agent: Search trends, growth velocity, geographic patterns
- Financial Agent: Margin analysis, competitive metrics
- Research Agent: News, technology adoption, customer sentiment
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.disruption import (
    DisruptionAssessment,
    DisruptionThreat,
    VulnerabilityBreakdown,
    TechnologyTrend,
    CustomerJobMisalignment,
    BusinessModelShift,
    DisruptionScoreComponents
)

logger = logging.getLogger(__name__)


class DisruptionAgent(BaseAgent):
    """
    Disruption agent for vulnerability assessment using Christensen's frameworks.

    Capabilities:
    1. Incumbent Overserving Detection: High margins + feature bloat signals
    2. Asymmetric Threat Analysis: Small competitors growing >3x industry rate
    3. Technology Shift Momentum: Emerging tech adoption velocity
    4. Customer Job Misalignment: Pain points and JTBD gaps
    5. Business Model Innovation: Subscription vs license model shifts
    """

    def __init__(self, timeout: int = 120):
        super().__init__(
            name="disruption_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a disruption vulnerability expert trained in Clayton Christensen's frameworks:
        - Jobs-to-be-Done theory for customer need analysis
        - Asymmetric competition and low-end disruption patterns
        - Technology S-curves and adoption velocity
        - Business model innovation and value network shifts
        - Sustaining vs disruptive innovation classification

        Analyze disruption risk to identify:
        1. Overserving signals (high margins, feature bloat, customer frustration)
        2. Asymmetric threats (small competitors with different business models)
        3. Technology shifts (emerging tech adoption momentum)
        4. Customer job misalignments (unmet or poorly met needs)
        5. Business model innovations (new value capture mechanisms)
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> DisruptionAssessment:
        """
        Execute disruption vulnerability assessment.

        Args:
            input_data: Dictionary containing:
                - company: Company name (required)
                - industry: Industry sector (required)
                - market_data: Market trends from MarketAgent
                - financial_data: Financial snapshot from FinancialAgent
                - research_data: Company research from ResearchAgent
                - competitors: List of competitor data (optional)
                - historical_snapshots: Past analysis snapshots (optional)

        Returns:
            DisruptionAssessment with comprehensive vulnerability analysis

        Raises:
            ValueError: If required data is missing
            Exception: If analysis fails
        """
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")

        if not company or not industry:
            raise ValueError("Company and industry are required")

        # Extract integrated data
        market_data = input_data.get("market_data", {})
        financial_data = input_data.get("financial_data", {})
        research_data = input_data.get("research_data", {})
        competitors = input_data.get("competitors", [])
        historical_snapshots = input_data.get("historical_snapshots", [])

        logger.info(f"Starting disruption assessment for {company} in {industry}")

        # Calculate 5 vulnerability components (weighted scoring)
        overserving_score = self._calculate_overserving_score(
            financial_data, research_data, market_data
        )  # 30% weight

        asymmetric_threats, threat_velocity_score = self._calculate_asymmetric_threats(
            company, competitors, market_data, financial_data
        )  # 25% weight

        tech_trends, tech_momentum_score = self._calculate_technology_shifts(
            market_data, research_data, industry
        )  # 20% weight

        job_misalignments, job_misalignment_score = self._calculate_job_misalignment(
            research_data, market_data, company
        )  # 15% weight

        model_shifts, model_innovation_score = self._calculate_business_model_innovation(
            competitors, market_data, industry
        )  # 10% weight

        # Calculate overall disruption score (weighted sum)
        score_components = DisruptionScoreComponents(
            overserving_score=min(30, overserving_score * 0.30),
            threat_velocity_score=min(25, threat_velocity_score * 0.25),
            tech_momentum_score=min(20, tech_momentum_score * 0.20),
            job_misalignment_score=min(15, job_misalignment_score * 0.15),
            model_innovation_score=min(10, model_innovation_score * 0.10),
            total_score=0,  # Will be calculated
            weights_used={
                "overserving": 0.30,
                "threat_velocity": 0.25,
                "tech_momentum": 0.20,
                "job_misalignment": 0.15,
                "model_innovation": 0.10
            },
            calculation_notes="Weighted sum of 5 Christensen disruption indicators"
        )

        overall_risk = (
            score_components.overserving_score +
            score_components.threat_velocity_score +
            score_components.tech_momentum_score +
            score_components.job_misalignment_score +
            score_components.model_innovation_score
        )
        score_components.total_score = overall_risk

        # Calculate risk trend from historical data
        risk_trend = self._calculate_risk_trend(historical_snapshots, overall_risk)

        # Classify risk level
        risk_level = self._classify_risk_level(overall_risk)

        # Build vulnerability breakdown
        vulnerability_breakdown = VulnerabilityBreakdown(
            incumbent_overserving=overserving_score,
            asymmetric_threat_velocity=threat_velocity_score,
            technology_shift=tech_momentum_score,
            customer_job_misalignment=job_misalignment_score,
            business_model_innovation=model_innovation_score
        )

        # Use LLM to generate strategic recommendations and early warning signals
        recommendations, warning_signals = await self._generate_strategic_guidance(
            company=company,
            industry=industry,
            overall_risk=overall_risk,
            risk_level=risk_level,
            threats=asymmetric_threats,
            tech_trends=tech_trends,
            job_gaps=job_misalignments,
            model_shifts=model_shifts,
            vulnerability_breakdown=vulnerability_breakdown
        )

        # Calculate confidence based on data quality
        confidence_score = self._calculate_confidence(
            market_data, financial_data, research_data, competitors
        )

        # Build final assessment
        return DisruptionAssessment(
            company=company,
            industry=industry,
            overall_risk=overall_risk,
            risk_trend=risk_trend,
            risk_level=risk_level,
            primary_threats=asymmetric_threats[:5],  # Top 5 threats
            vulnerability_breakdown=vulnerability_breakdown,
            technology_trends=tech_trends[:10],  # Top 10 tech trends
            job_misalignments=job_misalignments[:5],  # Top 5 JTBD gaps
            model_shifts=model_shifts[:5],  # Top 5 model innovations
            strategic_recommendations=recommendations,
            early_warning_signals=warning_signals,
            confidence_score=confidence_score,
            data_sources=self._extract_sources(market_data, financial_data, research_data),
            generated_at=datetime.utcnow().isoformat()
        )

    def _calculate_overserving_score(
        self,
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> float:
        """
        Calculate incumbent overserving score (0-100).

        High margins + declining sentiment + feature bloat = overserving signal

        Indicators:
        - Profit margin vs industry average (>20% premium = risk)
        - Customer sentiment decline (negative trend)
        - Feature complexity mentions in research
        - Price premium vs market average
        """
        score = 0.0

        # 1. Margin analysis (40 points max)
        profit_margin = financial_data.get("profit_margin", 0)
        industry_avg_margin = market_data.get("industry_metrics", {}).get("avg_margin", 10)

        if profit_margin > industry_avg_margin * 1.5:  # 50% premium
            margin_excess = ((profit_margin - industry_avg_margin) / industry_avg_margin) * 100
            score += min(40, margin_excess / 2)  # Cap at 40 points

        # 2. Sentiment decline (30 points max)
        sentiment_trend = research_data.get("sentiment_analysis", {}).get("trend", "stable")
        sentiment_score = research_data.get("sentiment_analysis", {}).get("score", 0)

        if sentiment_trend == "declining" and sentiment_score < 0:
            score += min(30, abs(sentiment_score) * 10)

        # 3. Feature complexity signals (30 points max)
        description = research_data.get("description", "").lower()
        complexity_keywords = ["bloated", "complex", "too many features", "overwhelming", "complicated"]
        complexity_count = sum(1 for kw in complexity_keywords if kw in description)

        if complexity_count > 0:
            score += min(30, complexity_count * 10)

        logger.info(f"Overserving score: {score:.1f}/100 (margin premium, sentiment decline, complexity)")
        return min(100, score)

    def _calculate_asymmetric_threats(
        self,
        company: str,
        competitors: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any]
    ) -> tuple[List[DisruptionThreat], float]:
        """
        Identify asymmetric competitive threats (small, fast-growing competitors).

        Returns:
            (List of DisruptionThreat objects, overall threat score 0-100)

        Christensen pattern: Small competitors with different business models
        growing 3x+ faster than incumbents.
        """
        threats = []
        overall_score = 0.0

        company_growth = market_data.get("growth_trajectory", {}).get("rate", 0)
        industry_avg_growth = market_data.get("industry_metrics", {}).get("avg_growth", 5)

        for comp in competitors:
            comp_name = comp.get("name", "Unknown")
            comp_market = comp.get("market_data", {})
            comp_financial = comp.get("financial_data", {})
            comp_research = comp.get("research_data", {})

            comp_growth = comp_market.get("growth_trajectory", {}).get("rate", 0)
            comp_market_cap = comp_financial.get("market_cap", 0)
            company_market_cap = financial_data.get("market_cap", 1e9)

            # Asymmetric threat criteria
            is_smaller = comp_market_cap < (company_market_cap * 0.2)  # <20% size
            is_fast_growing = comp_growth > max(company_growth * 3, industry_avg_growth * 3)
            has_different_model = comp_research.get("business_model", "") != financial_data.get("business_model", "")

            if is_smaller and is_fast_growing:
                growth_velocity = comp_growth / max(industry_avg_growth, 1)
                disruption_score = min(100, growth_velocity * 10)

                if has_different_model:
                    disruption_score *= 1.3  # 30% boost for different business model

                # Extract customer jobs from research
                customer_jobs = self._extract_customer_jobs(comp_research)

                # Estimate timeline to impact (faster growth = shorter timeline)
                timeline_days = max(180, int(365 * (1 / max(growth_velocity, 0.1))))

                threat = DisruptionThreat(
                    threat_name=f"{comp_name} - Asymmetric Growth",
                    disruption_score=min(100, disruption_score),
                    growth_velocity=growth_velocity,
                    business_model=comp_research.get("business_model", "Unknown"),
                    customer_jobs=customer_jobs,
                    timeline_to_impact=timeline_days,
                    recommended_response=self._generate_threat_response(
                        comp_name, growth_velocity, has_different_model
                    ),
                    threat_indicators=[
                        f"Growth rate: {comp_growth:.1f}% (vs industry {industry_avg_growth:.1f}%)",
                        f"Velocity multiplier: {growth_velocity:.1f}x",
                        f"Market cap: ${comp_market_cap / 1e9:.2f}B (asymmetric size)",
                        f"Business model: {comp_research.get('business_model', 'Unknown')}"
                    ]
                )
                threats.append(threat)
                overall_score += disruption_score

        # Normalize overall score
        if threats:
            overall_score = min(100, overall_score / len(threats))
        else:
            overall_score = 10  # Low risk if no asymmetric threats detected

        # Sort by disruption score
        threats.sort(key=lambda t: t.disruption_score, reverse=True)

        logger.info(f"Identified {len(threats)} asymmetric threats, overall score: {overall_score:.1f}/100")
        return threats, overall_score

    def _calculate_technology_shifts(
        self,
        market_data: Dict[str, Any],
        research_data: Dict[str, Any],
        industry: str
    ) -> tuple[List[TechnologyTrend], float]:
        """
        Detect emerging technology trends and adoption momentum.

        Returns:
            (List of TechnologyTrend objects, overall tech shift score 0-100)

        Analyzes:
        - Keyword velocity in search trends
        - Competitive adoption rates
        - Technology maturity stage
        """
        tech_trends = []
        overall_score = 0.0

        # Extract technology keywords from research
        tech_keywords = self._extract_tech_keywords(research_data, industry)

        for tech_name, tech_data in tech_keywords.items():
            keyword_velocity = tech_data.get("search_velocity", 0)  # % change
            adoption_rate = tech_data.get("adoption_percentage", 0)
            maturity = tech_data.get("maturity_stage", "emerging")

            # Score based on velocity and adoption
            enabler_score = min(100, (abs(keyword_velocity) / 10) + (adoption_rate * 0.5))

            if keyword_velocity > 50:  # >50% growth in search volume
                trend = TechnologyTrend(
                    technology=tech_name,
                    keyword_velocity=keyword_velocity,
                    adoption_rate=adoption_rate,
                    enabler_score=enabler_score,
                    maturity_stage=maturity
                )
                tech_trends.append(trend)
                overall_score += enabler_score

        # Normalize overall score
        if tech_trends:
            overall_score = min(100, overall_score / len(tech_trends))
        else:
            overall_score = 20  # Moderate risk if no clear tech shifts

        # Sort by enabler score
        tech_trends.sort(key=lambda t: t.enabler_score, reverse=True)

        logger.info(f"Identified {len(tech_trends)} technology trends, overall score: {overall_score:.1f}/100")
        return tech_trends, overall_score

    def _calculate_job_misalignment(
        self,
        research_data: Dict[str, Any],
        market_data: Dict[str, Any],
        company: str
    ) -> tuple[List[CustomerJobMisalignment], float]:
        """
        Identify customer jobs-to-be-done misalignments.

        Returns:
            (List of CustomerJobMisalignment objects, overall misalignment score 0-100)

        Christensen JTBD: What job is the customer hiring the product to do?
        Misalignment = job poorly met or not met at all.
        """
        misalignments = []
        overall_score = 0.0

        # Extract "alternative to X" search patterns
        related_searches = market_data.get("related_searches", [])
        alternative_searches = [s for s in related_searches if "alternative" in s.lower() or "vs" in s.lower()]

        if alternative_searches:
            # High misalignment if customers searching for alternatives
            misalignment_score = min(100, len(alternative_searches) * 20)

            # Extract pain points from sentiment
            pain_points = self._extract_pain_points(research_data)

            # Estimate opportunity size (rough heuristic)
            market_size = market_data.get("industry_metrics", {}).get("market_size_usd", 1e9)
            opportunity_size = (market_size / 1e6) * (misalignment_score / 100)  # In millions

            misalignment = CustomerJobMisalignment(
                job_description=f"Core {company} use case alternatives",
                misalignment_score=misalignment_score,
                alternative_searches=alternative_searches[:10],
                pain_points=pain_points[:5],
                opportunity_size=opportunity_size
            )
            misalignments.append(misalignment)
            overall_score = misalignment_score

        else:
            overall_score = 15  # Low misalignment if no alternative searches

        logger.info(f"Identified {len(misalignments)} JTBD misalignments, overall score: {overall_score:.1f}/100")
        return misalignments, overall_score

    def _calculate_business_model_innovation(
        self,
        competitors: List[Dict[str, Any]],
        market_data: Dict[str, Any],
        industry: str
    ) -> tuple[List[BusinessModelShift], float]:
        """
        Detect business model innovation trends in the industry.

        Returns:
            (List of BusinessModelShift objects, overall innovation score 0-100)

        Tracks shifts: License → Subscription, Asset-heavy → Platform, etc.
        """
        model_shifts = []
        overall_score = 0.0

        # Track business model distribution across competitors
        model_counts = {}
        total_comps = len(competitors)

        for comp in competitors:
            model_type = comp.get("research_data", {}).get("business_model", "unknown")
            model_counts[model_type] = model_counts.get(model_type, 0) + 1

        # Identify emerging models (subscription, platform, marketplace)
        disruptive_models = ["subscription", "platform", "marketplace", "saas", "freemium"]

        for model_type in disruptive_models:
            if model_type in model_counts:
                adoption_pct = (model_counts[model_type] / max(total_comps, 1)) * 100

                if adoption_pct > 20:  # >20% adoption
                    # Estimate shift velocity (rough heuristic)
                    shift_velocity = adoption_pct  # % per year assumption

                    # Disruption potential based on value network change
                    disruption_potential = min(100, adoption_pct * 1.5)

                    shift = BusinessModelShift(
                        model_type=model_type.capitalize(),
                        shift_velocity=shift_velocity,
                        competitive_adoption=adoption_pct,
                        value_network_impact="high" if adoption_pct > 50 else "medium",
                        disruption_potential=disruption_potential
                    )
                    model_shifts.append(shift)
                    overall_score += disruption_potential

        # Normalize overall score
        if model_shifts:
            overall_score = min(100, overall_score / len(model_shifts))
        else:
            overall_score = 10  # Low risk if no model innovation

        # Sort by disruption potential
        model_shifts.sort(key=lambda m: m.disruption_potential, reverse=True)

        logger.info(f"Identified {len(model_shifts)} business model shifts, overall score: {overall_score:.1f}/100")
        return model_shifts, overall_score

    def _calculate_risk_trend(
        self,
        historical_snapshots: List[Dict[str, Any]],
        current_risk: float
    ) -> float:
        """Calculate 30-day risk delta from historical snapshots."""
        if not historical_snapshots or len(historical_snapshots) < 2:
            return 0.0

        # Get risk score from 30 days ago
        past_risk = historical_snapshots[-1].get("disruption_risk", current_risk)
        trend = current_risk - past_risk

        logger.info(f"Risk trend: {trend:+.1f} points (30-day delta)")
        return trend

    def _classify_risk_level(self, overall_risk: float) -> str:
        """Classify risk level based on overall score."""
        if overall_risk >= 75:
            return "critical"
        elif overall_risk >= 50:
            return "high"
        elif overall_risk >= 25:
            return "medium"
        else:
            return "low"

    async def _generate_strategic_guidance(
        self,
        company: str,
        industry: str,
        overall_risk: float,
        risk_level: str,
        threats: List[DisruptionThreat],
        tech_trends: List[TechnologyTrend],
        job_gaps: List[CustomerJobMisalignment],
        model_shifts: List[BusinessModelShift],
        vulnerability_breakdown: VulnerabilityBreakdown
    ) -> tuple[List[str], List[str]]:
        """
        Use LLM to generate strategic recommendations and early warning signals.

        Returns:
            (recommendations: List[str], warning_signals: List[str])
        """
        # Build context for LLM
        context = f"""
        Company: {company}
        Industry: {industry}
        Overall Disruption Risk: {overall_risk:.1f}/100 ({risk_level})

        Vulnerability Breakdown:
        - Incumbent Overserving: {vulnerability_breakdown.incumbent_overserving:.1f}/100
        - Asymmetric Threats: {vulnerability_breakdown.asymmetric_threat_velocity:.1f}/100
        - Technology Shifts: {vulnerability_breakdown.technology_shift:.1f}/100
        - Customer Job Misalignment: {vulnerability_breakdown.customer_job_misalignment:.1f}/100
        - Business Model Innovation: {vulnerability_breakdown.business_model_innovation:.1f}/100

        Top Threats:
        {self._format_threats(threats[:3])}

        Top Technology Trends:
        {self._format_tech_trends(tech_trends[:3])}

        Customer Job Gaps:
        {self._format_job_gaps(job_gaps[:2])}

        Business Model Shifts:
        {self._format_model_shifts(model_shifts[:2])}

        Based on this Christensen-framework disruption analysis, provide:
        1. 5 strategic recommendations for {company} to mitigate disruption risk
        2. 5 early warning signals to monitor for increasing vulnerability

        Focus on actionable, specific guidance grounded in the data.
        """

        try:
            # Use LLM to generate guidance
            response = await self.generate_structured_output(
                prompt=context,
                response_model=None  # Free-form text response
            )

            # Parse response (simple split for now)
            lines = response.split("\n") if isinstance(response, str) else []

            recommendations = []
            warning_signals = []
            current_section = None

            for line in lines:
                line = line.strip()
                if "recommendation" in line.lower():
                    current_section = "recommendations"
                elif "warning" in line.lower() or "signal" in line.lower():
                    current_section = "signals"
                elif line and line[0].isdigit() and "." in line:
                    # Numbered item
                    item = line.split(".", 1)[1].strip() if "." in line else line
                    if current_section == "recommendations":
                        recommendations.append(item)
                    elif current_section == "signals":
                        warning_signals.append(item)

            # Fallback to heuristic-based recommendations if LLM fails
            if not recommendations:
                recommendations = self._generate_fallback_recommendations(
                    overall_risk, vulnerability_breakdown, threats
                )

            if not warning_signals:
                warning_signals = self._generate_fallback_signals(
                    vulnerability_breakdown, threats, tech_trends
                )

            return recommendations[:5], warning_signals[:5]

        except Exception as e:
            logger.warning(f"LLM guidance generation failed: {e}, using fallback heuristics")
            recommendations = self._generate_fallback_recommendations(
                overall_risk, vulnerability_breakdown, threats
            )
            warning_signals = self._generate_fallback_signals(
                vulnerability_breakdown, threats, tech_trends
            )
            return recommendations[:5], warning_signals[:5]

    # Helper methods for data extraction and formatting

    def _extract_customer_jobs(self, research_data: Dict[str, Any]) -> List[str]:
        """Extract customer jobs from research data."""
        description = research_data.get("description", "")
        products = research_data.get("products", [])

        jobs = []
        if "enable" in description.lower() or "help" in description.lower():
            jobs.append(description[:100])

        for product in products[:3]:
            if isinstance(product, str):
                jobs.append(f"Job: Use {product}")

        return jobs if jobs else ["Customer need analysis required"]

    def _generate_threat_response(self, comp_name: str, velocity: float, different_model: bool) -> str:
        """Generate recommended response to asymmetric threat."""
        if velocity > 5:
            return f"URGENT: Monitor {comp_name} closely. Consider strategic investment or acquisition."
        elif different_model:
            return f"Investigate {comp_name}'s business model for potential defensive innovation."
        else:
            return f"Track {comp_name} growth trajectory. Assess competitive response options."

    def _extract_tech_keywords(self, research_data: Dict[str, Any], industry: str) -> Dict[str, Dict[str, Any]]:
        """Extract technology keywords from research with velocity metrics."""
        # Simplified: return predefined tech keywords for common industries
        tech_map = {
            "automotive": {
                "electric vehicles": {"search_velocity": 120, "adoption_percentage": 35, "maturity_stage": "growing"},
                "autonomous driving": {"search_velocity": 85, "adoption_percentage": 15, "maturity_stage": "emerging"},
            },
            "software": {
                "artificial intelligence": {"search_velocity": 200, "adoption_percentage": 60, "maturity_stage": "growing"},
                "blockchain": {"search_velocity": 40, "adoption_percentage": 25, "maturity_stage": "emerging"},
            },
            "retail": {
                "e-commerce": {"search_velocity": 75, "adoption_percentage": 80, "maturity_stage": "mature"},
                "augmented reality": {"search_velocity": 110, "adoption_percentage": 20, "maturity_stage": "emerging"},
            }
        }

        industry_lower = industry.lower()
        for key in tech_map:
            if key in industry_lower:
                return tech_map[key]

        return {}  # No tech trends detected

    def _extract_pain_points(self, research_data: Dict[str, Any]) -> List[str]:
        """Extract customer pain points from sentiment analysis."""
        sentiment_analysis = research_data.get("sentiment_analysis", {})
        negative_topics = sentiment_analysis.get("negative_topics", [])

        pain_points = []
        for topic in negative_topics[:5]:
            if isinstance(topic, str):
                pain_points.append(topic)

        return pain_points if pain_points else ["Sentiment analysis required"]

    def _format_threats(self, threats: List[DisruptionThreat]) -> str:
        """Format threats for LLM context."""
        if not threats:
            return "No significant asymmetric threats detected"

        lines = []
        for i, threat in enumerate(threats, 1):
            lines.append(
                f"{i}. {threat.threat_name} "
                f"(Score: {threat.disruption_score:.1f}, Velocity: {threat.growth_velocity:.1f}x)"
            )
        return "\n".join(lines)

    def _format_tech_trends(self, trends: List[TechnologyTrend]) -> str:
        """Format technology trends for LLM context."""
        if not trends:
            return "No significant technology shifts detected"

        lines = []
        for i, trend in enumerate(trends, 1):
            lines.append(
                f"{i}. {trend.technology} "
                f"(Velocity: +{trend.keyword_velocity:.0f}%, Adoption: {trend.adoption_rate:.0f}%)"
            )
        return "\n".join(lines)

    def _format_job_gaps(self, gaps: List[CustomerJobMisalignment]) -> str:
        """Format customer job gaps for LLM context."""
        if not gaps:
            return "No significant customer job misalignments detected"

        lines = []
        for i, gap in enumerate(gaps, 1):
            lines.append(
                f"{i}. {gap.job_description} "
                f"(Misalignment: {gap.misalignment_score:.1f}/100, Opportunity: ${gap.opportunity_size:.0f}M)"
            )
        return "\n".join(lines)

    def _format_model_shifts(self, shifts: List[BusinessModelShift]) -> str:
        """Format business model shifts for LLM context."""
        if not shifts:
            return "No significant business model innovations detected"

        lines = []
        for i, shift in enumerate(shifts, 1):
            lines.append(
                f"{i}. {shift.model_type} "
                f"(Adoption: {shift.competitive_adoption:.0f}%, Disruption Potential: {shift.disruption_potential:.1f}/100)"
            )
        return "\n".join(lines)

    def _generate_fallback_recommendations(
        self,
        overall_risk: float,
        vulnerability_breakdown: VulnerabilityBreakdown,
        threats: List[DisruptionThreat]
    ) -> List[str]:
        """Generate heuristic-based recommendations if LLM fails."""
        recommendations = []

        if vulnerability_breakdown.incumbent_overserving > 50:
            recommendations.append(
                "Address overserving: Simplify product offering and reduce pricing to prevent low-end disruption"
            )

        if vulnerability_breakdown.asymmetric_threat_velocity > 50:
            recommendations.append(
                f"Monitor asymmetric threats: Track {threats[0].threat_name if threats else 'fast-growing competitors'} "
                "and assess defensive innovation options"
            )

        if vulnerability_breakdown.technology_shift > 50:
            recommendations.append(
                "Accelerate technology adoption: Invest in emerging technologies to avoid technology disruption"
            )

        if vulnerability_breakdown.customer_job_misalignment > 50:
            recommendations.append(
                "Customer job realignment: Conduct JTBD research to identify and address unmet customer needs"
            )

        if vulnerability_breakdown.business_model_innovation > 50:
            recommendations.append(
                "Business model experimentation: Test alternative business models (subscription, platform) to counter disruption"
            )

        return recommendations if recommendations else ["Maintain competitive vigilance and monitor market trends"]

    def _generate_fallback_signals(
        self,
        vulnerability_breakdown: VulnerabilityBreakdown,
        threats: List[DisruptionThreat],
        tech_trends: List[TechnologyTrend]
    ) -> List[str]:
        """Generate heuristic-based early warning signals if LLM fails."""
        signals = []

        signals.append("Margin compression: >10% decline in profit margins vs previous quarter")

        if threats:
            signals.append(
                f"Competitor acceleration: {threats[0].threat_name if threats else 'Asymmetric competitors'} "
                "growth rate increasing >50%"
            )

        signals.append("Customer churn spike: >15% increase in churn rate month-over-month")

        if tech_trends:
            signals.append(
                f"Technology adoption lag: Competitors adopting {tech_trends[0].technology if tech_trends else 'new technologies'} "
                "faster than company"
            )

        signals.append("'Alternative to [Company]' search volume increasing >25%")

        return signals

    def _calculate_confidence(
        self,
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score based on data availability and quality."""
        confidence = 50.0  # Base confidence

        # Boost for data availability
        if market_data.get("growth_trajectory"):
            confidence += 10
        if financial_data.get("profit_margin"):
            confidence += 10
        if research_data.get("sentiment_analysis"):
            confidence += 10
        if len(competitors) >= 3:
            confidence += 10
        if market_data.get("related_searches"):
            confidence += 10

        return min(100, confidence)

    def _extract_sources(
        self,
        market_data: Dict[str, Any],
        financial_data: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> List[str]:
        """Extract data source URLs from agent outputs."""
        sources = []

        # Market sources
        if "sources" in market_data:
            sources.extend(market_data["sources"])

        # Financial sources
        if "sources" in financial_data:
            sources.extend(financial_data["sources"])

        # Research sources
        if "sources" in research_data:
            sources.extend(research_data["sources"])

        return list(set(sources))[:10]  # Dedupe and limit to 10
