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
from .decision_intelligence import DecisionIntelligenceEngine

# Phase 2: Advanced agents (with graceful degradation)
_advanced_agents = {}

# Phase 2 Critical Agents - Positioning & Disruption
try:
    from .positioning_agent import PositioningAgent
    _advanced_agents['PositioningAgent'] = PositioningAgent
except (ImportError, Exception) as e:
    logger.warning(f"PositioningAgent unavailable: {e}")
    PositioningAgent = None

try:
    from .disruption_agent import DisruptionAgent
    _advanced_agents['DisruptionAgent'] = DisruptionAgent
except (ImportError, Exception) as e:
    logger.warning(f"DisruptionAgent unavailable: {e}")
    DisruptionAgent = None

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
except (ImportError, Exception) as e:
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
    "DecisionIntelligenceEngine",
]

# Dashboard agents (conditional) - import individually to prevent one blocking others
try:
    from .dashboard_analytics_agent import DashboardAnalyticsAgent
    _advanced_agents['DashboardAnalyticsAgent'] = DashboardAnalyticsAgent
    __all__.append("DashboardAnalyticsAgent")
except (ImportError, Exception) as e:
    logger.warning(f"DashboardAnalyticsAgent unavailable: {e}")
    DashboardAnalyticsAgent = None

try:
    from .dashboard_data_agent import DashboardDataAgent
    _advanced_agents['DashboardDataAgent'] = DashboardDataAgent
    __all__.append("DashboardDataAgent")
except (ImportError, Exception) as e:
    logger.warning(f"DashboardDataAgent unavailable: {e}")
    DashboardDataAgent = None

try:
    from .report_management_agent import ReportManagementAgent
    _advanced_agents['ReportManagementAgent'] = ReportManagementAgent
    __all__.append("ReportManagementAgent")
except (ImportError, Exception) as e:
    logger.warning(f"ReportManagementAgent unavailable: {e}")
    ReportManagementAgent = None

try:
    from .job_management_agent import JobManagementAgent
    _advanced_agents['JobManagementAgent'] = JobManagementAgent
    __all__.append("JobManagementAgent")
except (ImportError, Exception) as e:
    logger.warning(f"JobManagementAgent unavailable: {e}")
    JobManagementAgent = None

# Phase 2 & 3 agents (conditional) - import individually to prevent one blocking others
try:
    from .notification_agent import NotificationAgent
    _advanced_agents['NotificationAgent'] = NotificationAgent
    __all__.append("NotificationAgent")
except (ImportError, Exception) as e:
    logger.warning(f"NotificationAgent unavailable: {e}")
    NotificationAgent = None

try:
    from .version_control_agent import VersionControlAgent
    _advanced_agents['VersionControlAgent'] = VersionControlAgent
    __all__.append("VersionControlAgent")
except (ImportError, Exception) as e:
    logger.warning(f"VersionControlAgent unavailable: {e}")
    VersionControlAgent = None

try:
    from .template_agent import TemplateAgent
    _advanced_agents['TemplateAgent'] = TemplateAgent
    __all__.append("TemplateAgent")
except (ImportError, Exception) as e:
    logger.warning(f"TemplateAgent unavailable: {e}")
    TemplateAgent = None

try:
    from .visualization_agent import VisualizationAgent
    _advanced_agents['VisualizationAgent'] = VisualizationAgent
    __all__.append("VisualizationAgent")
except (ImportError, Exception) as e:
    logger.warning(f"VisualizationAgent unavailable: {e}")
    VisualizationAgent = None

try:
    from .alert_feedback_agent import AlertFeedbackAgent
    _advanced_agents['AlertFeedbackAgent'] = AlertFeedbackAgent
    __all__.append("AlertFeedbackAgent")
except (ImportError, Exception) as e:
    logger.warning(f"AlertFeedbackAgent unavailable: {e}")
    AlertFeedbackAgent = None

# Phase 3: Advanced Intelligence Agents
try:
    from .systems_agent import SystemsAgent
    _advanced_agents['SystemsAgent'] = SystemsAgent
    __all__.append("SystemsAgent")
except (ImportError, Exception) as e:
    logger.warning(f"SystemsAgent unavailable: {e}")
    SystemsAgent = None


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
        "QualityAgent",
        "DecisionIntelligenceEngine"
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
                      "FrameworkAgent", "SynthesisAgent", "QualityAgent",
                      "DecisionIntelligenceEngine"]:
        return True
    return agent_name in _advanced_agents

