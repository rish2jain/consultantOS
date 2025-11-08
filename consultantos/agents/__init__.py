"""
Agent implementations for ConsultantOS
"""
from .research_agent import ResearchAgent
from .market_agent import MarketAgent
from .financial_agent import FinancialAgent
from .framework_agent import FrameworkAgent
from .synthesis_agent import SynthesisAgent
from .quality_agent import QualityAgent, QualityReview

__all__ = [
    "ResearchAgent",
    "MarketAgent",
    "FinancialAgent",
    "FrameworkAgent",
    "SynthesisAgent",
    "QualityAgent",
    "QualityReview",
]

