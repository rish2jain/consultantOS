"""
Query intent classification for routing to specialized agents
"""
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AgentIntent(str, Enum):
    """Agent routing intents"""
    GENERAL = "general"  # Answer with RAG
    RESEARCH = "research"  # ResearchAgent - web research
    MARKET = "market"  # MarketAgent - trends and sentiment
    FINANCIAL = "financial"  # FinancialAgent - financial data
    FORECASTING = "forecasting"  # ForecastingAgent - predictions
    SOCIAL_MEDIA = "social_media"  # SocialMediaAgent - social sentiment
    DARK_DATA = "dark_data"  # DarkDataAgent - internal data
    FRAMEWORK = "framework"  # FrameworkAgent - strategic frameworks
    SYNTHESIS = "synthesis"  # SynthesisAgent - comprehensive analysis


class QueryClassifier:
    """Classify user query intent for agent routing"""

    # Intent keywords for classification
    INTENT_KEYWORDS = {
        AgentIntent.RESEARCH: [
            "research", "investigate", "find information", "web search",
            "latest news", "recent developments", "what happened"
        ],
        AgentIntent.MARKET: [
            "market trends", "market analysis", "industry trends",
            "market share", "competition", "competitors",
            "market sentiment", "consumer sentiment"
        ],
        AgentIntent.FINANCIAL: [
            "financial", "revenue", "earnings", "profit", "stock price",
            "financial performance", "balance sheet", "income statement",
            "cash flow", "valuation", "pe ratio", "market cap"
        ],
        AgentIntent.FORECASTING: [
            "forecast", "predict", "projection", "future",
            "next quarter", "next year", "trend prediction",
            "growth forecast", "revenue forecast"
        ],
        AgentIntent.SOCIAL_MEDIA: [
            "social media", "twitter", "sentiment", "mentions",
            "brand perception", "social sentiment", "online buzz",
            "social listening"
        ],
        AgentIntent.DARK_DATA: [
            "email", "slack", "internal", "dark data",
            "company documents", "internal communications",
            "employee feedback"
        ],
        AgentIntent.FRAMEWORK: [
            "porter", "swot", "pestel", "five forces",
            "blue ocean", "strategic analysis", "framework analysis",
            "competitive strategy", "strategic framework"
        ],
        AgentIntent.SYNTHESIS: [
            "comprehensive analysis", "full analysis", "complete report",
            "executive summary", "overall assessment",
            "synthesize", "consolidate"
        ]
    }

    def __init__(self):
        """Initialize query classifier"""
        pass

    def classify(self, query: str) -> AgentIntent:
        """
        Classify user query to determine routing intent

        Args:
            query: User query text

        Returns:
            AgentIntent enum value
        """
        if not query or not query.strip():
            logger.warning("Empty query provided for classification")
            return AgentIntent.GENERAL

        query_lower = query.lower()

        # Score each intent based on keyword matches
        intent_scores: Dict[AgentIntent, int] = {intent: 0 for intent in AgentIntent}

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    intent_scores[intent] += 1

        # Find intent with highest score
        max_score = max(intent_scores.values())

        if max_score == 0:
            # No keywords matched - use general RAG
            logger.debug(f"Query classified as GENERAL (no keyword matches): {query[:100]}")
            return AgentIntent.GENERAL

        # Get intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])[0]

        logger.debug(f"Query classified as {best_intent.value} (score: {max_score}): {query[:100]}")
        return best_intent

    def get_routing_metadata(self, query: str) -> Dict[str, Any]:
        """
        Get detailed routing metadata for a query

        Args:
            query: User query text

        Returns:
            Dict with intent, confidence, and matched keywords
        """
        intent = self.classify(query)
        query_lower = query.lower()

        # Find matched keywords
        matched_keywords = []
        if intent in self.INTENT_KEYWORDS:
            for keyword in self.INTENT_KEYWORDS[intent]:
                if keyword in query_lower:
                    matched_keywords.append(keyword)

        # Calculate simple confidence score
        confidence = min(len(matched_keywords) * 0.2, 1.0) if matched_keywords else 0.0

        return {
            "intent": intent.value,
            "confidence": confidence,
            "matched_keywords": matched_keywords,
            "route_to_agent": intent != AgentIntent.GENERAL
        }
