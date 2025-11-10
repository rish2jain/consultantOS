"""
Research Agent - Gathers company intelligence using Tavily with NLP enrichment
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import CompanyResearch, EntityMention, SentimentScore, EntityRelationship
from consultantos.tools import tavily_search_tool
from consultantos.tools.nlp_tool import get_nlp_processor
from consultantos.utils.schemas import ResearchDataSchema, log_validation_metrics
import logging

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Research agent for gathering company information with NLP enrichment"""

    def __init__(self, timeout: int = 60, enable_nlp: bool = True):
        super().__init__(
            name="research_agent",
            timeout=timeout
        )
        self.enable_nlp = enable_nlp
        self._nlp_processor = None

        self.instruction = """
        You are a business research specialist with expertise in:
        - Company intelligence gathering
        - Competitive landscape analysis
        - News monitoring and trend identification

        Gather comprehensive information about companies using web search.
        Focus on: company overview, recent news, market position, products/services.
        Cite all sources with URLs.
        """

    @property
    def nlp_processor(self):
        """Lazy load NLP processor on first use"""
        if self.enable_nlp and self._nlp_processor is None:
            try:
                self._nlp_processor = get_nlp_processor()
                logger.info("NLP processor initialized for ResearchAgent")
            except Exception as e:
                logger.warning(f"Failed to initialize NLP processor: {e}. Continuing without NLP enrichment.")
                self.enable_nlp = False
        return self._nlp_processor
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> CompanyResearch:
        """
        Execute research task to gather comprehensive company intelligence.

        Uses Tavily web search to gather company information including overview,
        products/services, market position, competitors, and recent news.

        Args:
            input_data: Dictionary containing:
                - company: Name of the company to research
                - industry: (optional) Industry for context

        Returns:
            CompanyResearch object containing:
                - company_name: Official company name
                - description: 2-3 sentence company overview
                - products_services: List of products and services
                - target_market: Target market description
                - key_competitors: List of main competitors
                - recent_news: List of recent news items
                - sources: List of source URLs

        Raises:
            Exception: If search fails completely or LLM extraction fails
        """
        company = input_data.get("company", "")
        
        # Search for company information
        search_query = f"{company} company overview business model products services competitors"
        search_results = tavily_search_tool(search_query, max_results=10)
        
        # Check for errors in search results
        if search_results.get("error"):
            # Return partial result with error note
            error_data = {
                "company_name": company,
                "description": f"Research partially available for {company}. Some data sources unavailable.",
                "products_services": [],
                "target_market": "Unknown",
                "key_competitors": [],
                "recent_news": [],
                "sources": [r.get("url", "") for r in search_results.get("results", [])]
            }

            # Validate error data
            is_valid, error_msg, cleaned_error = ResearchDataSchema.validate_research_data(error_data)
            log_validation_metrics("research_error", is_valid, error_msg)

            return CompanyResearch(**cleaned_error)
        
        # Format research data for LLM
        research_context = self._format_search_results(search_results)
        
        # Use structured output to extract company research
        prompt = f"""
        {self.instruction}
        
        Research the following company: {company}
        
        Search Results:
        {research_context}
        
        Extract and structure the following information:
        1. Company name
        2. Description (2-3 sentences)
        3. Products/services (list)
        4. Target market
        5. Key competitors (list)
        6. Recent news (3-5 items)
        7. Sources (URLs from search results)
        """
        
        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=CompanyResearch
            )

            # Validate the result using Pandera
            result_dict = result.model_dump()
            is_valid, error_msg, cleaned_data = ResearchDataSchema.validate_research_data(result_dict)

            # Log validation metrics
            log_validation_metrics("research", is_valid, error_msg)

            if not is_valid:
                logger.warning(
                    f"Research data validation failed for {company}: {error_msg}. "
                    "Returning cleaned partial data."
                )

            # Enrich with NLP processing if enabled
            if self.enable_nlp:
                cleaned_data = self._enrich_with_nlp(cleaned_data, research_context)

            # Return validated and cleaned data
            return CompanyResearch(**cleaned_data)

        except Exception as e:
            # Fallback to basic structure if structured output fails
            fallback_data = {
                "company_name": company,
                "description": f"Research gathered for {company}",
                "products_services": [],
                "target_market": "Unknown",
                "key_competitors": [],
                "recent_news": [],
                "sources": [r.get("url", "") for r in search_results.get("results", [])]
            }

            # Validate fallback data
            is_valid, error_msg, cleaned_fallback = ResearchDataSchema.validate_research_data(fallback_data)
            log_validation_metrics("research_fallback", is_valid, error_msg)

            return CompanyResearch(**cleaned_fallback)
    
    def _format_search_results(self, search_results: Dict[str, Any]) -> str:
        """Format search results for LLM consumption"""
        formatted = []
        for result in search_results.get("results", []):
            formatted.append(f"Title: {result.get('title', '')}\nURL: {result.get('url', '')}\nContent: {result.get('content', '')[:500]}\n")
        return "\n".join(formatted)

    def _enrich_with_nlp(self, research_data: Dict[str, Any], research_context: str) -> Dict[str, Any]:
        """
        Enrich research data with NLP analysis.

        Args:
            research_data: Base research data dictionary
            research_context: Full research text for NLP processing

        Returns:
            Enhanced research data with NLP fields
        """
        if not self.nlp_processor:
            return research_data

        try:
            logger.info("Enriching research data with NLP analysis")

            # Extract entities from research context
            entities_raw = self.nlp_processor.entity_extraction(
                research_context,
                entity_types=['ORG', 'PERSON', 'GPE', 'DATE', 'PRODUCT', 'MONEY', 'PERCENT']
            )

            # Convert to EntityMention models
            entities = [
                EntityMention(
                    text=ent['text'],
                    label=ent['label'],
                    start=ent['start'],
                    end=ent['end']
                )
                for ent in entities_raw
            ]

            # Analyze sentiment
            sentiment_raw = self.nlp_processor.sentiment_analysis(research_context)
            sentiment = SentimentScore(
                polarity=sentiment_raw['polarity'],
                subjectivity=sentiment_raw['subjectivity'],
                classification=sentiment_raw['classification']
            )

            # Extract entity relationships
            relationships_raw = self.nlp_processor.relationship_extraction(
                research_context,
                max_distance=100
            )

            # Convert to EntityRelationship models
            relationships = [
                EntityRelationship(
                    entity1=rel['entity1'],
                    entity2=rel['entity2'],
                    distance=rel['distance'],
                    context=rel['context']
                )
                for rel in relationships_raw
            ]

            # Extract keywords
            keywords = self.nlp_processor.keyword_extraction(research_context, top_n=15)

            # Add NLP fields to research data
            research_data['entities'] = entities
            research_data['sentiment'] = sentiment
            research_data['entity_relationships'] = relationships
            research_data['keywords'] = keywords

            logger.info(
                f"NLP enrichment complete: {len(entities)} entities, "
                f"{len(relationships)} relationships, "
                f"sentiment={sentiment.classification}"
            )

        except Exception as e:
            logger.warning(f"NLP enrichment failed: {e}. Continuing without NLP data.")
            # Set empty NLP fields on failure
            research_data.setdefault('entities', [])
            research_data.setdefault('sentiment', None)
            research_data.setdefault('entity_relationships', [])
            research_data.setdefault('keywords', [])

        return research_data

