"""
Agent implementations for ConsultantOS

Includes core agents (Phase 1) and advanced agents (Phase 2) with graceful
degradation for agents with missing dependencies.
"""
import logging

logger = logging.getLogger(__name__)

# Phase 1: Core agents (always available)
from .research_agent import ResearchAgent
from .market_agent import MarketAgent
from .financial_agent import FinancialAgent
from .framework_agent import FrameworkAgent
from .synthesis_agent import SynthesisAgent
from .quality_agent import QualityAgent, QualityReview

# Phase 2: Advanced agents (with graceful degradation)
_advanced_agents = {}

# Conversational Agent
try:
    from .conversational_agent import ConversationalAgent
    _advanced_agents['ConversationalAgent'] = ConversationalAgent
except ImportError as e:
    logger.warning(f"ConversationalAgent unavailable: {e}")
    ConversationalAgent = None

# Enhanced Forecasting Agent
try:
    from .forecasting_agent import EnhancedForecastingAgent
    _advanced_agents['EnhancedForecastingAgent'] = EnhancedForecastingAgent
except ImportError as e:
    logger.warning(f"EnhancedForecastingAgent unavailable: {e}")
    EnhancedForecastingAgent = None

# Dark Data Agent
try:
    from .dark_data_agent import DarkDataAgent
    _advanced_agents['DarkDataAgent'] = DarkDataAgent
except ImportError as e:
    logger.warning(f"DarkDataAgent unavailable: {e}")
    DarkDataAgent = None

# Social Media Agent
try:
    from .social_media_agent import SocialMediaAgent
    _advanced_agents['SocialMediaAgent'] = SocialMediaAgent
except ImportError as e:
    logger.warning(f"SocialMediaAgent unavailable: {e}")
    SocialMediaAgent = None

# Wargaming Agent
try:
    from .wargaming_agent import WargamingAgent
    _advanced_agents['WargamingAgent'] = WargamingAgent
except ImportError as e:
    logger.warning(f"WargamingAgent unavailable: {e}")
    WargamingAgent = None

# Analytics Builder Agent
try:
    from .analytics_builder_agent import AnalyticsBuilderAgent
    _advanced_agents['AnalyticsBuilderAgent'] = AnalyticsBuilderAgent
except ImportError as e:
    logger.warning(f"AnalyticsBuilderAgent unavailable: {e}")
    AnalyticsBuilderAgent = None

# Storytelling Agent
try:
    from .storytelling_agent import StorytellingAgent
    _advanced_agents['StorytellingAgent'] = StorytellingAgent
except ImportError as e:
    logger.warning(f"StorytellingAgent unavailable: {e}")
    StorytellingAgent = None

# Core exports (always available)
__all__ = [
    "ResearchAgent",
    "MarketAgent",
    "FinancialAgent",
    "FrameworkAgent",
    "SynthesisAgent",
    "QualityAgent",
    "QualityReview",
]

# Advanced exports (conditional)
__all__.extend(_advanced_agents.keys())


def get_available_agents():
    """
    Get list of available agent names.

    Returns:
        Dict with 'core' and 'advanced' agent lists
    """
    core_agents = [
        "ResearchAgent",
        "MarketAgent",
        "FinancialAgent",
        "FrameworkAgent",
        "SynthesisAgent",
        "QualityAgent"
    ]

    return {
        "core": core_agents,
        "advanced": list(_advanced_agents.keys()),
        "all": core_agents + list(_advanced_agents.keys())
    }


def is_agent_available(agent_name: str) -> bool:
    """
    Check if a specific agent is available.

    Args:
        agent_name: Name of the agent class

    Returns:
        True if agent is available, False otherwise
    """
    if agent_name in ["ResearchAgent", "MarketAgent", "FinancialAgent",
                      "FrameworkAgent", "SynthesisAgent", "QualityAgent"]:
        return True
    return agent_name in _advanced_agents

