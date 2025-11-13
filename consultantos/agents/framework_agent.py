"""
Framework Agent - Applies business frameworks (Porter, SWOT, PESTEL, Blue Ocean)
"""
import logging
import traceback
from typing import Dict, Any, List
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import FrameworkAnalysis
from consultantos.models.evidence_models import (
    EnhancedPortersFiveForces,
    EnhancedSWOTAnalysis,
    EnhancedPESTELAnalysis,
    EnhancedBlueOceanStrategy,
    InsightValidator
)
from consultantos.prompts import (
    PORTER_PROMPT_TEMPLATE,
    SWOT_PROMPT_TEMPLATE,
    PESTEL_PROMPT_TEMPLATE,
    BLUE_OCEAN_PROMPT_TEMPLATE
)

logger = logging.getLogger(__name__)


class FrameworkAgent(BaseAgent):
    """Framework analyst agent for applying strategic frameworks"""
    
    def __init__(self):
        super().__init__(
            name="framework_analyst"
        )
        self.instruction = """
        You are a strategic framework expert trained in strategic consulting methodologies.

        Apply rigorous business frameworks:
        - Porter's Five Forces (competitive dynamics)
        - SWOT Analysis (internal/external factors)
        - PESTEL Analysis (macro environment)
        - Blue Ocean Strategy (value innovation)

        Requirements:
        - Evidence-Based: Every claim must cite specific data
        - Quantitative: Use scores, percentages, specific numbers
        - Structured: Follow framework methodology precisely
        - Actionable: Link analysis to strategic implications
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> FrameworkAnalysis:
        """
        Execute strategic framework analysis using selected business frameworks.

        Applies rigorous professional-grade frameworks to analyze competitive
        positioning and strategic options. Each framework provides unique insights:
        - Porter's Five Forces: Industry competitive dynamics
        - SWOT: Internal strengths/weaknesses, external opportunities/threats
        - PESTEL: Macro-environmental factors
        - Blue Ocean: Value innovation opportunities

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - industry: Industry context
                - frameworks: List of frameworks to apply (default: all 4)
                - research: CompanyResearch from research agent (optional)
                - market: MarketTrends from market agent (optional)
                - financial: FinancialSnapshot from financial agent (optional)

        Returns:
            FrameworkAnalysis object containing:
                - porter_five_forces: Porter's analysis (if requested)
                - swot_analysis: SWOT analysis (if requested)
                - pestel_analysis: PESTEL analysis (if requested)
                - blue_ocean_strategy: Blue Ocean analysis (if requested)

        Raises:
            Exception: If framework application fails

        Note:
            Gracefully handles missing data from previous phases by noting
            gaps in the analysis rather than failing completely.
        """
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")
        frameworks = input_data.get("frameworks", ["porter", "swot", "pestel", "blue_ocean"])
        
        # Get context from previous agents
        research = input_data.get("research", {})
        market = input_data.get("market", {})
        financial = input_data.get("financial", {})
        social_media = input_data.get("social_media", {})

        # Format context summaries
        research_summary = self._format_research(research)
        market_summary = self._format_market(market)
        financial_summary = self._format_financial(financial)
        social_media_summary = self._format_social_media(social_media)
        
        framework_results = FrameworkAnalysis()
        
        # Apply requested frameworks
        if "porter" in frameworks:
            framework_results.porter_five_forces = await self._analyze_porter(
                company, industry, research_summary, market_summary, financial_summary, social_media_summary
            )

        if "swot" in frameworks:
            framework_results.swot_analysis = await self._analyze_swot(
                company, research_summary, market_summary, financial_summary, social_media_summary
            )

        if "pestel" in frameworks:
            framework_results.pestel_analysis = await self._analyze_pestel(
                company, research_summary, market_summary, financial_summary, social_media_summary
            )

        if "blue_ocean" in frameworks:
            competitors = research.get("key_competitors", []) if isinstance(research, dict) else []
            framework_results.blue_ocean_strategy = await self._analyze_blue_ocean(
                company, industry, competitors, research_summary, market_summary, financial_summary, social_media_summary
            )
        
        return framework_results
    
    async def _analyze_porter(self, company: str, industry: str, research: str, market: str, financial: str, social_media: str) -> EnhancedPortersFiveForces:
        """Analyze using Porter's 5 Forces with required evidence"""
        prompt = PORTER_PROMPT_TEMPLATE.format(
            company_name=company,
            industry=industry or "Unknown",
            research_summary=research,
            market_summary=market,
            financial_summary=financial,
            social_media_summary=social_media
        )

        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=EnhancedPortersFiveForces
            )
            return result
        except Exception as e:
            # Log detailed error information
            logger.error(
                f"Porter's Five Forces analysis failed for company={company}, industry={industry}",
                exc_info=True,
                extra={
                    "company": company,
                    "industry": industry,
                    "framework": "porter",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            # Import evidence models for fallback
            from consultantos.models.evidence_models import PorterForceDetail, MetricEvidence

            # Fallback with minimal valid data
            default_metric = MetricEvidence(
                metric_name="Data Collection Required",
                value="Pending",
                unit="N/A"
            )

            default_force = PorterForceDetail(
                force_name="Analysis Pending",
                score=3.0,
                key_factors=["Data collection in progress", "Review recommended"],
                metrics=[default_metric],
                competitive_implication="Further analysis required for strategic insights"
            )

            return EnhancedPortersFiveForces(
                supplier_power=default_force,
                buyer_power=default_force,
                competitive_rivalry=default_force,
                threat_of_substitutes=default_force,
                threat_of_new_entrants=default_force,
                overall_intensity="Moderate",
                strategic_position="Analysis pending - insufficient data",
                key_battlegrounds=["Market position unclear", "Competitive dynamics under review"]
            )
    
    async def _analyze_swot(self, company: str, research: str, market: str, financial: str, social_media: str) -> EnhancedSWOTAnalysis:
        """Analyze using SWOT with required evidence"""
        prompt = SWOT_PROMPT_TEMPLATE.format(
            company_name=company,
            research_summary=research,
            market_summary=market,
            financial_summary=financial,
            social_media_summary=social_media
        )

        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=EnhancedSWOTAnalysis
            )
            return result
        except Exception as e:
            # Log detailed error information
            logger.error(
                f"SWOT analysis failed for company={company}",
                exc_info=True,
                extra={
                    "company": company,
                    "framework": "swot",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                    "research_summary_length": len(research) if research else 0,
                    "market_summary_length": len(market) if market else 0,
                    "financial_summary_length": len(financial) if financial else 0
                }
            )
            # Import evidence models for fallback
            from consultantos.models.evidence_models import SWOTItem, MetricEvidence

            # Create default evidence
            default_evidence = MetricEvidence(
                metric_name="Data Required",
                value="Pending",
                unit="N/A"
            )

            # Create default SWOT items with evidence
            default_item = lambda statement: SWOTItem(
                statement=statement,
                evidence=default_evidence,
                impact="Analysis pending - data collection required"
            )

            # Return valid enhanced SWOT with minimum requirements
            return EnhancedSWOTAnalysis(
                strengths=[
                    default_item("Market position under analysis"),
                    default_item("Competitive advantages being assessed"),
                    default_item("Core competencies under review")
                ],
                weaknesses=[
                    default_item("Operational gaps being identified"),
                    default_item("Resource constraints under evaluation"),
                    default_item("Market vulnerabilities being assessed")
                ],
                opportunities=[
                    default_item("Growth potential being analyzed"),
                    default_item("Market trends under review"),
                    default_item("Strategic options being evaluated")
                ],
                threats=[
                    default_item("Competitive pressures being monitored"),
                    default_item("Market risks under assessment"),
                    default_item("Regulatory challenges being reviewed")
                ],
                strategic_options=["Comprehensive analysis required", "Strategic planning pending"]
            )
    
    async def _analyze_pestel(self, company: str, research: str, market: str, financial: str, social_media: str) -> EnhancedPESTELAnalysis:
        """Analyze using PESTEL with trend data and impact assessment"""
        prompt = PESTEL_PROMPT_TEMPLATE.format(
            company_name=company,
            research_summary=research,
            market_summary=market,
            financial_summary=financial,
            social_media_summary=social_media
        )

        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=EnhancedPESTELAnalysis
            )
            return result
        except Exception as e:
            # Log detailed error information
            logger.error(
                f"PESTEL analysis failed for company={company}",
                exc_info=True,
                extra={
                    "company": company,
                    "framework": "pestel",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            # Import evidence models for fallback
            from consultantos.models.evidence_models import PESTELFactor, TrendData

            # Create default trend
            default_trend = TrendData(
                trend_name="Analysis pending",
                direction="Stable",
                impact="Data collection required for assessment"
            )

            # Create default factor
            def create_default_factor(area: str) -> PESTELFactor:
                return PESTELFactor(
                    factor=f"{area} factors under analysis",
                    current_state="Current data being collected",
                    trend=default_trend,
                    impact_on_company="Impact assessment pending data collection",
                    time_horizon="1yr"
                )

            # Return valid enhanced PESTEL with minimum requirements
            return EnhancedPESTELAnalysis(
                political=[create_default_factor("Regulatory"), create_default_factor("Government policy")],
                economic=[create_default_factor("Market conditions"), create_default_factor("Economic growth")],
                social=[create_default_factor("Demographics"), create_default_factor("Consumer behavior")],
                technological=[create_default_factor("Innovation"), create_default_factor("Digital transformation")],
                environmental=[create_default_factor("Sustainability")],
                legal=[create_default_factor("Compliance")],
                critical_factors=["Data collection required", "Analysis pending", "Review recommended"]
            )
    
    async def _analyze_blue_ocean(self, company: str, industry: str, competitors: List[str],
                                  research: str, market: str, financial: str, social_media: str) -> EnhancedBlueOceanStrategy:
        """Analyze using Blue Ocean Strategy with value innovation metrics"""
        prompt = BLUE_OCEAN_PROMPT_TEMPLATE.format(
            company_name=company,
            industry=industry or "Unknown",
            competitors=", ".join(competitors) if competitors else "Unknown",
            research_summary=research,
            market_summary=market,
            financial_summary=financial,
            social_media_summary=social_media
        )
        
        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=EnhancedBlueOceanStrategy
            )
            return result
        except Exception as e:
            # Log detailed error information
            logger.error(
                f"Blue Ocean Strategy analysis failed for company={company}, industry={industry}",
                exc_info=True,
                extra={
                    "company": company,
                    "industry": industry,
                    "framework": "blue_ocean",
                    "competitors_count": len(competitors) if competitors else 0,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
            )
            # Import evidence models for fallback
            from consultantos.models.evidence_models import BlueOceanAction

            # Create default action
            def create_default_action(action_text: str) -> BlueOceanAction:
                return BlueOceanAction(
                    action=action_text,
                    rationale="Analysis pending - data collection required",
                    implementation_cost="Medium"
                )

            # Return valid enhanced Blue Ocean with minimum requirements
            return EnhancedBlueOceanStrategy(
                eliminate=[
                    create_default_action("Non-essential features under review"),
                    create_default_action("Cost centers being evaluated")
                ],
                reduce=[
                    create_default_action("Operational complexity being assessed"),
                    create_default_action("Resource allocation under analysis")
                ],
                raise_factors=[
                    create_default_action("Customer value drivers being identified"),
                    create_default_action("Differentiation opportunities under review")
                ],
                create=[
                    create_default_action("Innovation potential being explored"),
                    create_default_action("New market opportunities under assessment")
                ],
                value_innovation="Value innovation strategy pending comprehensive analysis",
                target_segment="Target market definition requires further research",
                differentiation_score=5.0
            )
    
    def _format_research(self, research: Any) -> str:
        """Format research data - preserving ALL collected intelligence"""
        if not isinstance(research, dict):
            return str(research)

        sections = [
            f"Company: {research.get('company_name', 'Unknown')}",
            f"Description: {research.get('description', 'N/A')}",
            f"\n📦 Products/Services: {', '.join(research.get('products_services', [])) or 'Not found'}",
            f"🎯 Target Market: {research.get('target_market', 'Unknown')}",
            f"⚔️ Key Competitors: {', '.join(research.get('key_competitors', [])) or 'Not found'}",
        ]

        # Include recent news with details
        if research.get('recent_news'):
            sections.append("\n📰 Recent News & Developments:")
            for item in research.get('recent_news', [])[:10]:
                sections.append(f"  • {item}")

        # Include NLP-enriched entities if available
        if research.get('entities'):
            entities_by_type = {}
            for ent in research.get('entities', [])[:30]:
                if isinstance(ent, dict):
                    label = ent.get('label', 'OTHER')
                    text = ent.get('text', '')
                    entities_by_type.setdefault(label, []).append(text)

            if entities_by_type:
                sections.append("\n🔍 Key Entities Detected:")
                for label, texts in entities_by_type.items():
                    sections.append(f"  {label}: {', '.join(texts[:10])}")

        # Include sentiment analysis if available
        if research.get('sentiment'):
            sentiment = research['sentiment']
            if isinstance(sentiment, dict):
                sections.append(f"\n💭 Market Sentiment: {sentiment.get('classification', 'Unknown')} (Score: {sentiment.get('polarity', 0):.2f})")

        # Include keywords/topics if available
        if research.get('keywords'):
            sections.append(f"🔑 Key Topics: {', '.join(research.get('keywords', [])[:15])}")

        # Include relationships if available
        if research.get('relationships'):
            sections.append("\n🔗 Business Relationships:")
            for rel in research.get('relationships', [])[:10]:
                if isinstance(rel, str):
                    sections.append(f"  • {rel}")

        # Include market position if available
        if research.get('market_position'):
            sections.append(f"\n📊 Market Position: {research.get('market_position')}")

        # Include funding information if available
        if research.get('funding'):
            sections.append(f"💰 Funding: {research.get('funding')}")

        return "\n".join(sections)
    
    def _format_market(self, market: Any) -> str:
        """Format market data - preserving ALL trend intelligence"""
        if not isinstance(market, dict):
            return str(market)

        sections = [
            f"📈 Search Interest Trend: {market.get('search_interest_trend', 'Unknown')}",
        ]

        # Include detailed time series data if available
        if market.get('interest_over_time'):
            sections.append("\n⏱️ Interest Over Time (Recent Data Points):")
            time_data = market.get('interest_over_time', [])
            if isinstance(time_data, list):
                for point in time_data[-10:]:  # Last 10 data points
                    if isinstance(point, dict):
                        sections.append(f"  • {point.get('date', '')}: {point.get('value', 0)}")

        # Include regional interest breakdown
        if market.get('interest_by_region'):
            sections.append("\n🌍 Regional Interest (Top Markets):")
            regions = market.get('interest_by_region', {})
            if isinstance(regions, dict):
                sorted_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:10]
                for region, score in sorted_regions:
                    sections.append(f"  • {region}: {score}")

        # Include related queries
        if market.get('related_queries'):
            sections.append("\n🔍 Related Search Queries:")
            for query in market.get('related_queries', [])[:15]:
                if isinstance(query, dict):
                    sections.append(f"  • {query.get('query', '')}: {query.get('value', '')}")
                else:
                    sections.append(f"  • {query}")

        # Include rising/breakout topics
        if market.get('rising_topics'):
            sections.append("\n🚀 Rising/Breakout Topics:")
            for topic in market.get('rising_topics', [])[:10]:
                if isinstance(topic, dict):
                    sections.append(f"  • {topic.get('topic', '')}: +{topic.get('growth', '')}%")
                else:
                    sections.append(f"  • {topic}")

        # Include competitor comparison if available
        if market.get('vs_competitors'):
            sections.append("\n⚔️ Search Volume vs Competitors:")
            for comp, data in market.get('vs_competitors', {}).items()[:5]:
                sections.append(f"  • {comp}: {data}")

        # Include seasonality patterns
        if market.get('seasonality'):
            sections.append(f"\n📊 Seasonality Pattern: {market.get('seasonality')}")

        # Include market size/TAM if available
        if market.get('market_size'):
            sections.append(f"\n💰 Market Size/TAM: {market.get('market_size')}")

        # Include growth rate
        if market.get('growth_rate'):
            sections.append(f"📈 Market Growth Rate: {market.get('growth_rate')}")

        return "\n".join(sections)
    
    def _format_financial(self, financial: Any) -> str:
        """Format financial data - preserving ALL financial metrics"""
        if not isinstance(financial, dict):
            return str(financial)

        sections = []

        # Core financial metrics
        if financial.get('revenue'):
            sections.append(f"💰 Revenue: {financial.get('revenue')}")
        if financial.get('market_cap'):
            sections.append(f"📊 Market Cap: {financial.get('market_cap')}")

        # Growth metrics
        if financial.get('revenue_growth'):
            sections.append(f"📈 Revenue Growth: {financial.get('revenue_growth')}")
        if financial.get('earnings_growth'):
            sections.append(f"📈 Earnings Growth: {financial.get('earnings_growth')}")

        # Profitability metrics
        if financial.get('profit_margin'):
            sections.append(f"💵 Profit Margin: {financial.get('profit_margin')}")
        if financial.get('operating_margin'):
            sections.append(f"⚙️ Operating Margin: {financial.get('operating_margin')}")
        if financial.get('gross_margin'):
            sections.append(f"📊 Gross Margin: {financial.get('gross_margin')}")

        # Valuation metrics
        if financial.get('pe_ratio'):
            sections.append(f"📈 P/E Ratio: {financial.get('pe_ratio')}")
        if financial.get('peg_ratio'):
            sections.append(f"📊 PEG Ratio: {financial.get('peg_ratio')}")
        if financial.get('price_to_book'):
            sections.append(f"📚 Price/Book: {financial.get('price_to_book')}")
        if financial.get('ev_to_ebitda'):
            sections.append(f"💹 EV/EBITDA: {financial.get('ev_to_ebitda')}")

        # Balance sheet metrics
        if financial.get('total_cash'):
            sections.append(f"💵 Total Cash: {financial.get('total_cash')}")
        if financial.get('total_debt'):
            sections.append(f"💳 Total Debt: {financial.get('total_debt')}")
        if financial.get('debt_to_equity'):
            sections.append(f"⚖️ Debt/Equity: {financial.get('debt_to_equity')}")
        if financial.get('current_ratio'):
            sections.append(f"💧 Current Ratio: {financial.get('current_ratio')}")

        # Cash flow metrics
        if financial.get('operating_cash_flow'):
            sections.append(f"💸 Operating Cash Flow: {financial.get('operating_cash_flow')}")
        if financial.get('free_cash_flow'):
            sections.append(f"💰 Free Cash Flow: {financial.get('free_cash_flow')}")
        if financial.get('cash_flow_margin'):
            sections.append(f"📊 Cash Flow Margin: {financial.get('cash_flow_margin')}")

        # Efficiency metrics
        if financial.get('roe'):
            sections.append(f"📈 ROE: {financial.get('roe')}")
        if financial.get('roa'):
            sections.append(f"📊 ROA: {financial.get('roa')}")
        if financial.get('roic'):
            sections.append(f"💹 ROIC: {financial.get('roic')}")

        # Stock performance
        if financial.get('stock_price'):
            sections.append(f"\n📈 Stock Price: {financial.get('stock_price')}")
        if financial.get('52_week_high'):
            sections.append(f"⬆️ 52-Week High: {financial.get('52_week_high')}")
        if financial.get('52_week_low'):
            sections.append(f"⬇️ 52-Week Low: {financial.get('52_week_low')}")
        if financial.get('ytd_return'):
            sections.append(f"📊 YTD Return: {financial.get('ytd_return')}")

        # Analyst ratings if available
        if financial.get('analyst_rating'):
            sections.append(f"\n🎯 Analyst Rating: {financial.get('analyst_rating')}")
        if financial.get('price_target'):
            sections.append(f"🎯 Price Target: {financial.get('price_target')}")

        # Competitive financial comparison if available
        if financial.get('vs_industry_avg'):
            sections.append("\n⚔️ vs Industry Average:")
            for metric, value in financial.get('vs_industry_avg', {}).items()[:10]:
                sections.append(f"  • {metric}: {value}")

        return "\n".join(sections) if sections else "Financial data not available"

    def _format_social_media(self, social_media: Any) -> str:
        """Format social media data - extracting ALL Twitter/Reddit intelligence"""
        if not social_media or not isinstance(social_media, dict):
            return "Social media data not available"

        # Check if we have data from social media agent
        if social_media.get('success') == False or not social_media.get('data'):
            return "Social media monitoring not available"

        data = social_media.get('data', {})
        sections = ["📱 Social Media Intelligence:"]

        # Overall sentiment
        if hasattr(data, 'overall_sentiment'):
            sentiment_score = data.overall_sentiment
            sentiment_label = getattr(data, 'sentiment_label', 'neutral')
            sections.append(f"\n🎭 Overall Sentiment: {sentiment_label} (Score: {sentiment_score:.2f})")

        # Crisis alerts
        if hasattr(data, 'crisis_alerts') and data.crisis_alerts:
            sections.append("\n🚨 Crisis Alerts:")
            for alert in data.crisis_alerts[:3]:
                sections.append(f"  • [{alert.severity}] {alert.description}")
                if alert.affected_keywords:
                    sections.append(f"    Keywords: {', '.join(alert.affected_keywords[:3])}")

        # Trending topics
        if hasattr(data, 'trending_topics') and data.trending_topics:
            sections.append("\n🔥 Trending Topics:")
            for topic in data.trending_topics[:5]:
                sections.append(f"  • {topic.topic} (Mentions: {topic.mention_count}, Sentiment: {topic.sentiment_score:.2f})")

        # Top influencers
        if hasattr(data, 'top_influencers') and data.top_influencers:
            sections.append("\n👥 Key Influencers:")
            for influencer in data.top_influencers[:5]:
                verified = "✓" if influencer.verified else ""
                sections.append(f"  • @{influencer.username}{verified} ({influencer.followers_count:,} followers)")
                if influencer.description:
                    sections.append(f"    {influencer.description[:100]}")

        # Competitor mentions
        if hasattr(data, 'competitor_mentions') and data.competitor_mentions:
            sections.append("\n⚔️ Competitor Mentions:")
            for comp_name, comp_data in data.competitor_mentions.items():
                if hasattr(comp_data, 'mention_count'):
                    sections.append(f"  • {comp_name}: {comp_data.mention_count} mentions (Sentiment: {comp_data.sentiment_score:.2f})")
                    if hasattr(comp_data, 'share_of_voice'):
                        sections.append(f"    Share of Voice: {comp_data.share_of_voice}%")

        # Platform metrics
        if hasattr(data, 'metrics') and data.metrics:
            metrics = data.metrics
            if isinstance(metrics, dict):
                sections.append("\n📊 Engagement Metrics:")
                if metrics.get('total_mentions'):
                    sections.append(f"  • Total Mentions: {metrics['total_mentions']}")
                if metrics.get('engagement_rate'):
                    sections.append(f"  • Engagement Rate: {metrics['engagement_rate']:.2f}")
                if metrics.get('reach'):
                    sections.append(f"  • Estimated Reach: {metrics['reach']:,}")
                if metrics.get('sentiment_breakdown'):
                    breakdown = metrics['sentiment_breakdown']
                    sections.append(f"  • Sentiment Breakdown: {breakdown}")
                if metrics.get('key_themes'):
                    sections.append(f"  • Key Themes: {', '.join(metrics['key_themes'][:5])}")

        # Reddit-specific insights if available
        if hasattr(data, 'reddit_insights'):
            reddit = data.reddit_insights
            sections.append("\n🟠 Reddit Community Insights:")
            if hasattr(reddit, 'overall_sentiment'):
                sections.append(f"  • Reddit Sentiment: {reddit.overall_sentiment:.2f}")
            if hasattr(reddit, 'top_discussions'):
                sections.append("  • Top Discussions:")
                for post in reddit.top_discussions[:3]:
                    sections.append(f"    - {post.title[:100]} ({post.score} upvotes, {post.num_comments} comments)")
            if hasattr(reddit, 'community_sentiment'):
                sections.append("  • Community Sentiment by Subreddit:")
                for sub, score in reddit.community_sentiment.items()[:5]:
                    sections.append(f"    - r/{sub}: {score:.2f}")

        # Time period
        if hasattr(data, 'time_period') and data.time_period:
            period = data.time_period
            sections.append(f"\n⏰ Analysis Period: {period.get('start', 'N/A')} to {period.get('end', 'N/A')}")

        # Summary if available
        if hasattr(data, 'metrics') and isinstance(data.metrics, dict) and data.metrics.get('summary'):
            sections.append(f"\n📝 Summary: {data.metrics['summary']}")

        return "\n".join(sections)

