"""
LLM Provider Management API endpoints.

Endpoints for:
- Provider health monitoring
- Cost tracking and analytics
- Provider configuration
- Usage statistics
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

import logging
from consultantos.agents.base_agent import BaseAgent
from consultantos.llm.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/providers", tags=["providers"])


class ProviderHealthResponse(BaseModel):
    """Provider health status response."""
    provider: str
    is_healthy: bool
    total_requests: int
    failed_requests: int
    failure_rate: float
    consecutive_failures: int
    tokens_used: int
    estimated_cost: float
    capabilities: Dict[str, Any]


class CostSummaryResponse(BaseModel):
    """Cost summary response."""
    daily_cost: float
    monthly_cost: float
    by_provider: Dict[str, float]
    by_agent: Dict[str, float]
    total_tokens: int
    total_requests: int


class UsageStatsResponse(BaseModel):
    """Detailed usage statistics."""
    total_cost: float
    total_tokens: int
    total_requests: int
    by_provider: Dict[str, float]
    by_agent: Dict[str, float]
    average_cost_per_request: float
    average_tokens_per_request: float


@router.get("/health", response_model=Dict[str, ProviderHealthResponse])
async def get_provider_health():
    """
    Get health status for all LLM providers.

    Returns:
        Dictionary mapping provider names to health status
    """
    try:
        if BaseAgent._provider_manager is None:
            raise HTTPException(
                status_code=503,
                detail="Provider manager not initialized"
            )

        stats = BaseAgent._provider_manager.get_provider_stats()

        health_responses = {}
        for provider_name, provider_stats in stats.items():
            health_responses[provider_name] = ProviderHealthResponse(
                provider=provider_name,
                is_healthy=provider_stats["is_healthy"],
                total_requests=provider_stats["total_requests"],
                failed_requests=provider_stats["failed_requests"],
                failure_rate=provider_stats["failure_rate"],
                consecutive_failures=provider_stats["consecutive_failures"],
                tokens_used=provider_stats["tokens_used"],
                estimated_cost=provider_stats["estimated_cost"],
                capabilities=provider_stats["capabilities"]
            )

        return health_responses

    except Exception as e:
        logger.error(f"Failed to get provider health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/{provider_name}/reset")
async def reset_provider_health(provider_name: str):
    """
    Reset health status for a specific provider.

    Args:
        provider_name: Name of provider to reset

    Returns:
        Success message
    """
    try:
        if BaseAgent._provider_manager is None:
            raise HTTPException(
                status_code=503,
                detail="Provider manager not initialized"
            )

        BaseAgent._provider_manager.reset_provider_health(provider_name)

        return {
            "status": "success",
            "message": f"Reset health for provider: {provider_name}"
        }

    except Exception as e:
        logger.error(f"Failed to reset provider health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/summary", response_model=CostSummaryResponse)
async def get_cost_summary():
    """
    Get cost summary (daily and monthly).

    Returns:
        Cost breakdown by time period, provider, and agent
    """
    try:
        daily_cost = await cost_tracker.get_daily_cost()
        monthly_cost = await cost_tracker.get_monthly_cost()
        by_provider = await cost_tracker.get_cost_by_provider()
        by_agent = await cost_tracker.get_cost_by_agent()

        # Get token counts
        stats = await cost_tracker.get_usage_stats()

        return CostSummaryResponse(
            daily_cost=daily_cost,
            monthly_cost=monthly_cost,
            by_provider=by_provider,
            by_agent=by_agent,
            total_tokens=stats["total_tokens"],
            total_requests=stats["total_requests"]
        )

    except Exception as e:
        logger.error(f"Failed to get cost summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get detailed usage statistics.

    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Comprehensive usage statistics
    """
    try:
        stats = await cost_tracker.get_usage_stats(start_date, end_date)

        return UsageStatsResponse(
            total_cost=stats["total_cost"],
            total_tokens=stats["total_tokens"],
            total_requests=stats["total_requests"],
            by_provider=stats["by_provider"],
            by_agent=stats["by_agent"],
            average_cost_per_request=stats["average_cost_per_request"],
            average_tokens_per_request=stats["average_tokens_per_request"]
        )

    except Exception as e:
        logger.error(f"Failed to get usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/export")
async def export_usage_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Export detailed usage report.

    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering

    Returns:
        Comprehensive usage report
    """
    try:
        report = await cost_tracker.export_usage_report(start_date, end_date)
        return report

    except Exception as e:
        logger.error(f"Failed to export usage report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configuration")
async def get_provider_configuration():
    """
    Get current provider configuration.

    Returns:
        Provider configuration details
    """
    try:
        if BaseAgent._provider_manager is None:
            raise HTTPException(
                status_code=503,
                detail="Provider manager not initialized"
            )

        pm = BaseAgent._provider_manager

        return {
            "available_providers": list(pm.providers.keys()),
            "primary_provider": pm.primary_provider,
            "enable_fallback": pm.enable_fallback,
            "routing_strategy": pm.routing_strategy,
            "fallback_order": pm.fallback_order,
            "budgets": {
                "daily": cost_tracker.daily_budget,
                "monthly": cost_tracker.monthly_budget
            }
        }

    except Exception as e:
        logger.error(f"Failed to get provider configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
