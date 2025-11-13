"""
Synthesis Agent - Creates executive summary and recommendations
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.evidence_models import EnhancedExecutiveSummary, InsightValidator
from consultantos.prompts import SYNTHESIS_PROMPT_TEMPLATE
import structlog
logger = structlog.get_logger(__name__)


class SynthesisAgent(BaseAgent):
    """Synthesis agent for creating executive summary"""
    
    def __init__(self, timeout: int = 90):
        super().__init__(
            name="synthesis_agent",
            timeout=timeout  # Increased from default 60s to 90s to prevent timeouts
        )
        self.instruction = """
        You are a synthesis specialist.
        Combine insights from research, market, financial, and framework analyses.
        Create executive summary with key insights and recommendations.
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> EnhancedExecutiveSummary:
        """
        Execute synthesis to create executive summary and strategic recommendations.

        Combines insights from all previous analysis phases (research, market,
        financial, frameworks) into a cohesive executive summary with actionable
        recommendations.

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - industry: Industry context
                - research: CompanyResearch results (optional)
                - market: MarketTrends results (optional)
                - financial: FinancialSnapshot results (optional)
                - frameworks: FrameworkAnalysis results (optional)

        Returns:
            EnhancedExecutiveSummary object containing:
                - market_position: Current market position with metrics
                - competitive_advantage: Core differentiation
                - key_findings: Top 3-5 strategic insights with evidence
                - primary_recommendation: Main strategic recommendation
                - secondary_recommendations: Additional recommendations
                - confidence_score: 0-1 confidence in analysis quality
                - data_quality_assessment: Quality scores by data source
                - critical_assumptions: Key assumptions made

        Raises:
            Exception: If synthesis fails or all input analyses are missing

        Note:
            Confidence score is adjusted based on completeness of input data.
            Missing phases result in lower confidence but synthesis still proceeds.
        """
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")
        
        # Get all analysis results
        research = input_data.get("research", {})
        market = input_data.get("market", {})
        financial = input_data.get("financial", {})
        social_media = input_data.get("social_media", {})
        frameworks = input_data.get("frameworks", {})

        # Format summaries
        research_summary = self._format_research(research)
        market_summary = self._format_market(market)
        financial_summary = self._format_financial(financial)
        social_media_summary = self._format_social_media(social_media)
        porter_summary = self._format_porter(frameworks.get("porter_five_forces") if isinstance(frameworks, dict) else {})
        swot_summary = self._format_swot(frameworks.get("swot_analysis") if isinstance(frameworks, dict) else {})

        prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            research_summary=research_summary,
            market_summary=market_summary,
            financial_summary=financial_summary,
            social_media_summary=social_media_summary,
            porter_summary=porter_summary,
            swot_summary=swot_summary
        )
        
        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=EnhancedExecutiveSummary
            )
            # Ensure company name and industry are set
            result.company_name = company
            result.industry = industry or "Unknown"

            # Validate quality of insights
            quality_report = InsightValidator.generate_quality_report(result)
            if quality_report['overall_quality'] < 0.6:
                logger.warning(
                    f"Low quality synthesis detected (score: {quality_report['overall_quality']:.2f})",
                    issues=quality_report.get('issues', [])
                )
                # Optionally retry once with more specific prompt
                enhanced_prompt = prompt + "\n\nCRITICAL: Previous response was too generic. Provide SPECIFIC metrics, percentages, and evidence for EVERY claim."
                result = await self.generate_structured(
                    prompt=enhanced_prompt,
                    response_model=EnhancedExecutiveSummary
                )
                result.company_name = company
                result.industry = industry or "Unknown"
            
            # Calculate data completeness and adjust confidence if needed
            data_completeness = self._calculate_data_completeness(research, market, financial, frameworks, social_media)
            # If LLM gave a very low score but we have good data, adjust upward
            if result.confidence_score < 0.5 and data_completeness >= 0.7:
                # Adjust confidence: take average of LLM score and data completeness, but cap at 0.85
                adjusted_confidence = min(0.85, (result.confidence_score + data_completeness) / 2)
                logger.info(
                    f"Adjusting confidence from {result.confidence_score:.2f} to {adjusted_confidence:.2f} "
                    f"based on data completeness {data_completeness:.2f}"
                )
                result.confidence_score = adjusted_confidence
            # If LLM gave a high score but we have poor data, adjust downward slightly
            elif result.confidence_score > 0.8 and data_completeness < 0.5:
                adjusted_confidence = max(0.5, result.confidence_score * data_completeness)
                logger.info(
                    f"Adjusting confidence from {result.confidence_score:.2f} to {adjusted_confidence:.2f} "
                    f"based on data completeness {data_completeness:.2f}"
                )
                result.confidence_score = adjusted_confidence
            
            return result
        except Exception as e:
            # Log exception with full context and stacktrace
            error_type = type(e).__name__
            logger.error(
                "synthesis_agent_execution_failed",
                company=company,
                industry=industry or "Unknown",
                error_type=error_type,
                error_message=str(e),
                exc_info=True  # Includes full stacktrace
            )
            
            # Determine if this is a critical error that should be re-raised
            # Critical errors: network issues, authentication failures, model errors
            critical_error_types = (
                ConnectionError,
                TimeoutError,
                PermissionError,
            )
            
            # Check if it's a critical error by type or message content
            # Use a single lowercased message variable to avoid repeated calls
            error_message_lower = str(e).lower()
            is_critical = (
                isinstance(e, critical_error_types) or
                ("api" in error_message_lower and ("key" in error_message_lower or "auth" in error_message_lower)) or
                ("model" in error_message_lower and ("not found" in error_message_lower or "invalid" in error_message_lower))
            )
            
            if is_critical:
                # Re-raise critical errors so they can be handled upstream
                logger.error(
                    "synthesis_agent_critical_error_re_raising",
                    company=company,
                    industry=industry or "Unknown",
                    error_type=error_type,
                    error_message=str(e)
                )
                raise
            
            # For non-critical errors (e.g., parsing issues, validation errors), return fallback
            logger.warning(
                "synthesis_agent_using_fallback",
                company=company,
                industry=industry or "Unknown",
                error_type=error_type,
                error_message=str(e)
            )
            
            # Import evidence models for fallback
            from consultantos.models.evidence_models import (
                MetricEvidence, KeyFinding, StrategicRecommendation, RiskAssessment
            )
            from datetime import datetime

            # Create minimal valid evidence objects
            default_metric = MetricEvidence(
                metric_name="Data Collection Required",
                value="Pending",
                unit="N/A"
            )

            default_risk = RiskAssessment(
                risk_factor="Incomplete analysis",
                likelihood=0.5,
                impact_score=5.0,
                mitigation="Complete data collection and rerun analysis",
                evidence="Analysis failed due to processing error"
            )

            default_finding = KeyFinding(
                finding="Analysis partially completed - review required",
                confidence=0.3,
                supporting_data=[default_metric, default_metric],
                source_frameworks=["Initial assessment"],
                strategic_implication="Further analysis needed for strategic decisions"
            )

            default_recommendation = StrategicRecommendation(
                recommendation="Complete comprehensive analysis",
                priority="High",
                rationale=["Data collection incomplete", "Framework analysis required"],
                expected_impact=default_metric,
                implementation_timeline="Immediate",
                resources_required="Analyst time and data access",
                success_metrics=["Complete data collection", "All frameworks analyzed"],
                risks=[default_risk]
            )

            # Return valid enhanced executive summary with fallback data
            return EnhancedExecutiveSummary(
                company_name=company,
                industry=industry or "Unknown",
                analysis_date=datetime.now(),
                market_position=default_metric,
                competitive_advantage="Competitive position requires comprehensive analysis to determine",
                key_findings=[default_finding, default_finding, default_finding],
                primary_recommendation=default_recommendation,
                secondary_recommendations=[default_recommendation, default_recommendation],
                confidence_score=0.3,
                data_quality_assessment={
                    "research": 0.1,
                    "market": 0.1,
                    "financial": 0.1,
                    "frameworks": 0.1
                },
                critical_assumptions=["Limited data available", "Analysis requires completion"]
            )
    
    def _format_research(self, research: Any) -> str:
        """Format research summary - preserving key intelligence"""
        if not isinstance(research, dict):
            return str(research)

        sections = [
            f"Company: {research.get('company_name', 'Unknown')}",
            f"Description: {research.get('description', 'N/A')}",
            f"Products: {', '.join(research.get('products_services', [])[:5]) or 'N/A'}",
            f"Competitors: {', '.join(research.get('key_competitors', [])[:5]) or 'N/A'}",
            f"Target Market: {research.get('target_market', 'N/A')}",
        ]

        if research.get('recent_news'):
            sections.append(f"Recent Developments: {len(research.get('recent_news', []))} news items")

        if research.get('sentiment'):
            sentiment = research['sentiment']
            if isinstance(sentiment, dict):
                sections.append(f"Market Sentiment: {sentiment.get('classification', 'Unknown')}")

        return "\n".join(sections)

    def _format_market(self, market: Any) -> str:
        """Format market summary - preserving trend insights"""
        if not isinstance(market, dict):
            return str(market)

        sections = [f"Search Trend: {market.get('search_interest_trend', 'Unknown')}"]

        if market.get('growth_rate'):
            sections.append(f"Growth Rate: {market.get('growth_rate')}")

        if market.get('rising_topics'):
            sections.append(f"Rising Topics: {len(market.get('rising_topics', []))} identified")

        if market.get('vs_competitors'):
            sections.append(f"Competitive Position: Tracked against {len(market.get('vs_competitors', {}))} competitors")

        if market.get('seasonality'):
            sections.append(f"Seasonality: {market.get('seasonality')}")

        return "\n".join(sections)

    def _format_financial(self, financial: Any) -> str:
        """Format financial summary - preserving key metrics"""
        if not isinstance(financial, dict):
            return str(financial)

        sections = []
        key_metrics = [
            ('Revenue', 'revenue'),
            ('Market Cap', 'market_cap'),
            ('Revenue Growth', 'revenue_growth'),
            ('Profit Margin', 'profit_margin'),
            ('P/E Ratio', 'pe_ratio'),
            ('Free Cash Flow', 'free_cash_flow'),
            ('ROE', 'roe')
        ]

        for label, key in key_metrics:
            if financial.get(key):
                sections.append(f"{label}: {financial.get(key)}")

        return "\n".join(sections) if sections else "Limited financial data available"

    def _format_porter(self, porter: Any) -> str:
        """Format Porter's 5 Forces summary - preserving actual analysis"""
        if not isinstance(porter, dict):
            return str(porter)

        sections = [f"Overall Competitive Intensity: {porter.get('overall_intensity', 'Unknown')}"]

        forces = [
            ('Supplier Power', 'supplier_power'),
            ('Buyer Power', 'buyer_power'),
            ('Threat of Substitutes', 'threat_of_substitutes'),
            ('Threat of New Entrants', 'threat_of_new_entrants'),
            ('Competitive Rivalry', 'competitive_rivalry')
        ]

        for label, key in forces:
            if porter.get(key):
                score = porter[key]
                sections.append(f"• {label}: {score}/5")

        if porter.get('detailed_analysis'):
            sections.append(f"Detailed Insights: {len(porter.get('detailed_analysis', {}))} force analyses")

        return "\n".join(sections)

    def _format_swot(self, swot: Any) -> str:
        """Format SWOT summary - INCLUDING ACTUAL CONTENT"""
        if not isinstance(swot, dict):
            return str(swot)

        sections = ["SWOT Analysis:"]

        # Include actual strengths, not just count!
        if swot.get('strengths'):
            sections.append(f"\nStrengths ({len(swot['strengths'])}):")
            for strength in swot['strengths'][:3]:  # Top 3
                sections.append(f"  • {strength}")

        # Include actual weaknesses
        if swot.get('weaknesses'):
            sections.append(f"\nWeaknesses ({len(swot['weaknesses'])}):")
            for weakness in swot['weaknesses'][:3]:  # Top 3
                sections.append(f"  • {weakness}")

        # Include actual opportunities
        if swot.get('opportunities'):
            sections.append(f"\nOpportunities ({len(swot['opportunities'])}):")
            for opp in swot['opportunities'][:3]:  # Top 3
                sections.append(f"  • {opp}")

        # Include actual threats
        if swot.get('threats'):
            sections.append(f"\nThreats ({len(swot['threats'])}):")
            for threat in swot['threats'][:3]:  # Top 3
                sections.append(f"  • {threat}")

        return "\n".join(sections)

    def _format_social_media(self, social_media: Any) -> str:
        """Format social media data for synthesis - extracting key signals"""
        if not social_media or not isinstance(social_media, dict):
            return "Social media monitoring not available"

        # Check if we have data from social media agent
        if social_media.get('success') == False or not social_media.get('data'):
            return "Social media data collection failed"

        data = social_media.get('data', {})
        sections = ["Social Media Signals:"]

        # Overall sentiment
        if hasattr(data, 'overall_sentiment'):
            sentiment_score = data.overall_sentiment
            sentiment_label = getattr(data, 'sentiment_label', 'neutral')
            sections.append(f"• Sentiment: {sentiment_label} ({sentiment_score:.2f})")

        # Crisis alerts (important for synthesis)
        if hasattr(data, 'crisis_alerts') and data.crisis_alerts:
            sections.append(f"• Crisis Alerts: {len(data.crisis_alerts)} detected")
            for alert in data.crisis_alerts[:2]:
                sections.append(f"  - {alert.severity}: {alert.description}")

        # Trending topics
        if hasattr(data, 'trending_topics') and data.trending_topics:
            topics_list = [topic.topic for topic in data.trending_topics[:3]]
            sections.append(f"• Trending: {', '.join(topics_list)}")

        # Key influencers count
        if hasattr(data, 'top_influencers') and data.top_influencers:
            sections.append(f"• Key Influencers: {len(data.top_influencers)} identified")
            total_followers = sum(inf.followers_count for inf in data.top_influencers[:5])
            sections.append(f"  Combined reach: {total_followers:,} followers")

        # Competitor sentiment comparison
        if hasattr(data, 'competitor_mentions') and data.competitor_mentions:
            sections.append(f"• Competitor tracking: {len(data.competitor_mentions)} competitors monitored")

        # Engagement metrics summary
        if hasattr(data, 'metrics') and isinstance(data.metrics, dict):
            metrics = data.metrics
            if metrics.get('engagement_rate'):
                sections.append(f"• Engagement Rate: {metrics['engagement_rate']:.1f}")
            if metrics.get('reach'):
                sections.append(f"• Estimated Reach: {metrics['reach']:,}")

        return "\n".join(sections)

    def _calculate_data_completeness(
        self,
        research: Any,
        market: Any,
        financial: Any,
        frameworks: Any,
        social_media: Any = None
    ) -> float:
        """
        Calculate data completeness score (0-1) based on available data sources.
        
        Args:
            research: Research data
            market: Market trends data
            financial: Financial data
            frameworks: Framework analysis data
        
        Returns:
            Completeness score between 0 and 1
        """
        score = 0.0
        total_weight = 0.0
        
        # Research data (weight: 0.25)
        if research and isinstance(research, dict) and research.get('description'):
            score += 0.25
        total_weight += 0.25
        
        # Market data (weight: 0.20)
        if market and isinstance(market, dict) and market.get('search_interest_trend'):
            score += 0.20
        total_weight += 0.20
        
        # Financial data (weight: 0.25)
        if financial and isinstance(financial, dict):
            # Check if we have meaningful financial data
            has_financial = any([
                financial.get('revenue'),
                financial.get('market_cap'),
                financial.get('revenue_growth'),
                financial.get('profit_margin')
            ])
            if has_financial:
                score += 0.25
        total_weight += 0.25
        
        # Framework data (weight: 0.25)
        if frameworks:
            if isinstance(frameworks, dict):
                # Check for Porter's 5 Forces
                porter = frameworks.get('porter_five_forces') or frameworks.get('porter')
                if porter and isinstance(porter, dict) and porter.get('overall_intensity'):
                    score += 0.125
                # Check for SWOT
                swot = frameworks.get('swot_analysis') or frameworks.get('swot')
                if swot and isinstance(swot, dict) and (swot.get('strengths') or swot.get('weaknesses')):
                    score += 0.125
            else:
                # If frameworks is not empty, give partial credit
                score += 0.125
        total_weight += 0.25

        # Social media data (weight: 0.15)
        if social_media:
            if isinstance(social_media, dict) and social_media.get('success') and social_media.get('data'):
                data = social_media.get('data', {})
                # Check for meaningful social media signals
                has_social = any([
                    hasattr(data, 'overall_sentiment'),
                    hasattr(data, 'trending_topics'),
                    hasattr(data, 'top_influencers'),
                    hasattr(data, 'crisis_alerts')
                ])
                if has_social:
                    score += 0.15
        total_weight += 0.15

        # Normalize to 0-1 range
        if total_weight > 0:
            return min(1.0, score / total_weight)
        return 0.0

