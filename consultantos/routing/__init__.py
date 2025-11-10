"""
Query routing system for ConsultantOS
Routes user queries to appropriate specialized agents
"""
from consultantos.routing.query_classifier import QueryClassifier
from consultantos.routing.agent_router import AgentRouter

__all__ = ["QueryClassifier", "AgentRouter"]
