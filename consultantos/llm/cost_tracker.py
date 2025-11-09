"""
LLM Cost Tracking System.

Tracks token usage and costs across all providers for analytics and budgeting.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class UsageRecord(BaseModel):
    """Record of LLM usage."""
    provider: str
    model: str
    tokens_used: int
    cost_usd: float
    user_id: Optional[str] = None
    analysis_id: Optional[str] = None
    agent_name: Optional[str] = None
    timestamp: datetime


class LLMCostTracker:
    """
    Track LLM API costs across providers.

    Provides:
    - Usage tracking per provider
    - Cost aggregation by user/analysis
    - Budget monitoring and alerts
    - Usage analytics
    """

    def __init__(self):
        """Initialize cost tracker."""
        self.usage_records: List[UsageRecord] = []
        self.daily_budget: Optional[float] = None
        self.monthly_budget: Optional[float] = None

    async def track_usage(
        self,
        provider: str,
        model: str,
        tokens_used: int,
        cost_per_1k_tokens: float,
        user_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        agent_name: Optional[str] = None
    ):
        """
        Track LLM usage and cost.

        Args:
            provider: Provider name (gemini, openai, anthropic)
            model: Model identifier
            tokens_used: Number of tokens consumed
            cost_per_1k_tokens: Cost per 1000 tokens in USD
            user_id: Optional user identifier
            analysis_id: Optional analysis identifier
            agent_name: Optional agent name
        """
        cost_usd = (tokens_used / 1000) * cost_per_1k_tokens

        record = UsageRecord(
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            user_id=user_id,
            analysis_id=analysis_id,
            agent_name=agent_name,
            timestamp=datetime.now()
        )

        self.usage_records.append(record)

        logger.info(
            f"Tracked LLM usage",
            extra={
                "provider": provider,
                "model": model,
                "tokens": tokens_used,
                "cost": cost_usd,
                "user_id": user_id,
                "analysis_id": analysis_id,
                "agent": agent_name
            }
        )

        # Check budget alerts
        await self._check_budget_alerts()

    async def _check_budget_alerts(self):
        """Check if budget limits are approaching or exceeded."""
        if self.daily_budget:
            daily_cost = await self.get_daily_cost()
            if daily_cost >= self.daily_budget * 0.9:
                logger.warning(
                    f"Daily LLM budget at 90%: ${daily_cost:.2f} / ${self.daily_budget:.2f}",
                    extra={"daily_cost": daily_cost, "budget": self.daily_budget}
                )
            if daily_cost >= self.daily_budget:
                logger.error(
                    f"Daily LLM budget exceeded: ${daily_cost:.2f} / ${self.daily_budget:.2f}",
                    extra={"daily_cost": daily_cost, "budget": self.daily_budget}
                )

        if self.monthly_budget:
            monthly_cost = await self.get_monthly_cost()
            if monthly_cost >= self.monthly_budget * 0.9:
                logger.warning(
                    f"Monthly LLM budget at 90%: ${monthly_cost:.2f} / ${self.monthly_budget:.2f}",
                    extra={"monthly_cost": monthly_cost, "budget": self.monthly_budget}
                )
            if monthly_cost >= self.monthly_budget:
                logger.error(
                    f"Monthly LLM budget exceeded: ${monthly_cost:.2f} / ${self.monthly_budget:.2f}",
                    extra={"monthly_cost": monthly_cost, "budget": self.monthly_budget}
                )

    async def get_daily_cost(self) -> float:
        """
        Get total LLM costs for today.

        Returns:
            Total cost in USD
        """
        today = datetime.now().date()
        return sum(
            record.cost_usd
            for record in self.usage_records
            if record.timestamp.date() == today
        )

    async def get_monthly_cost(self) -> float:
        """
        Get total LLM costs this month.

        Returns:
            Total cost in USD
        """
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum(
            record.cost_usd
            for record in self.usage_records
            if record.timestamp >= month_start
        )

    async def get_cost_by_provider(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get cost breakdown by provider.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary mapping provider to cost
        """
        records = self._filter_records(start_date, end_date)

        costs = {}
        for record in records:
            if record.provider not in costs:
                costs[record.provider] = 0.0
            costs[record.provider] += record.cost_usd

        return costs

    async def get_cost_by_user(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get cost breakdown by user.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary mapping user_id to cost
        """
        records = self._filter_records(start_date, end_date)

        costs = {}
        for record in records:
            if record.user_id:
                if record.user_id not in costs:
                    costs[record.user_id] = 0.0
                costs[record.user_id] += record.cost_usd

        return costs

    async def get_cost_by_agent(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get cost breakdown by agent.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary mapping agent_name to cost
        """
        records = self._filter_records(start_date, end_date)

        costs = {}
        for record in records:
            if record.agent_name:
                if record.agent_name not in costs:
                    costs[record.agent_name] = 0.0
                costs[record.agent_name] += record.cost_usd

        return costs

    async def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get comprehensive usage statistics.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary with usage statistics
        """
        records = self._filter_records(start_date, end_date)

        if not records:
            return {
                "total_cost": 0.0,
                "total_tokens": 0,
                "total_requests": 0,
                "by_provider": {},
                "by_agent": {},
                "average_cost_per_request": 0.0
            }

        total_cost = sum(r.cost_usd for r in records)
        total_tokens = sum(r.tokens_used for r in records)

        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_requests": len(records),
            "by_provider": await self.get_cost_by_provider(start_date, end_date),
            "by_agent": await self.get_cost_by_agent(start_date, end_date),
            "average_cost_per_request": total_cost / len(records) if records else 0.0,
            "average_tokens_per_request": total_tokens / len(records) if records else 0
        }

    def _filter_records(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[UsageRecord]:
        """
        Filter usage records by date range.

        Args:
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Filtered list of usage records
        """
        records = self.usage_records

        if start_date:
            records = [r for r in records if r.timestamp >= start_date]

        if end_date:
            records = [r for r in records if r.timestamp <= end_date]

        return records

    def set_daily_budget(self, budget_usd: float):
        """
        Set daily cost budget.

        Args:
            budget_usd: Daily budget in USD
        """
        self.daily_budget = budget_usd
        logger.info(f"Set daily LLM budget: ${budget_usd:.2f}")

    def set_monthly_budget(self, budget_usd: float):
        """
        Set monthly cost budget.

        Args:
            budget_usd: Monthly budget in USD
        """
        self.monthly_budget = budget_usd
        logger.info(f"Set monthly LLM budget: ${budget_usd:.2f}")

    async def export_usage_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Generate comprehensive usage report.

        Args:
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Detailed usage report
        """
        records = self._filter_records(start_date, end_date)

        report = {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "summary": await self.get_usage_stats(start_date, end_date),
            "by_provider": await self.get_cost_by_provider(start_date, end_date),
            "by_user": await self.get_cost_by_user(start_date, end_date),
            "by_agent": await self.get_cost_by_agent(start_date, end_date),
            "total_records": len(records),
            "date_range_days": (
                (end_date - start_date).days
                if start_date and end_date
                else None
            )
        }

        return report


# Global cost tracker instance
cost_tracker = LLMCostTracker()
