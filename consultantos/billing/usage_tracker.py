"""
Usage tracking against tier limits
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from consultantos.models.subscription import (
    Subscription, PricingTier, TierLimits, UsageSummary, TIER_CONFIGS
)
from consultantos.database import DatabaseService
import logging

logger = logging.getLogger(__name__)


class UsageTracker:
    """Track and enforce usage limits for subscription tiers"""

    def __init__(self, db_service: DatabaseService):
        self.db = db_service

    async def check_limit(
        self,
        user_id: str,
        resource_type: str,
        increment: int = 0
    ) -> bool:
        """
        Check if user is within their tier limits for a resource.

        Args:
            user_id: User identifier
            resource_type: Type of resource (analyses, monitors, team_members, etc.)
            increment: Optional increment to test (for pre-flight checks)

        Returns:
            True if within limits, False if limit exceeded
        """
        try:
            subscription = await self.get_subscription(user_id)
            limits = self._get_limits(subscription)
            current_usage = await self._get_current_usage(user_id, resource_type, subscription)

            if resource_type == "analyses":
                return (current_usage + increment) < limits.analyses_per_month
            elif resource_type == "monitors":
                return (current_usage + increment) < limits.monitors
            elif resource_type == "team_members":
                return (current_usage + increment) < limits.team_members
            elif resource_type == "framework":
                # Check if framework is available in tier
                framework_name = increment  # Framework name passed as increment
                return framework_name in limits.frameworks or limits.custom_frameworks
            elif resource_type == "export_format":
                # Check if export format is available
                format_name = increment  # Format name passed as increment
                return format_name in limits.export_formats
            elif resource_type == "api_access":
                return limits.api_access
            else:
                logger.warning(f"Unknown resource type: {resource_type}")
                return True  # Default to allowing unknown resources

        except Exception as e:
            logger.error(f"Error checking limit for user {user_id}, resource {resource_type}: {e}")
            # Fail open for availability - allow the operation
            return True

    async def increment_usage(
        self,
        user_id: str,
        resource_type: str,
        amount: int = 1
    ) -> bool:
        """
        Increment usage counter for a resource.

        Args:
            user_id: User identifier
            resource_type: Type of resource to increment
            amount: Amount to increment by

        Returns:
            True if successful, False otherwise
        """
        try:
            subscription = await self.get_subscription(user_id)

            if resource_type == "analyses":
                subscription.analyses_used += amount
            elif resource_type == "monitors":
                subscription.monitors_active += amount
            # team_members tracked separately in user management

            subscription.updated_at = datetime.utcnow()
            await self.db.update_subscription(subscription)

            logger.info(f"Incremented {resource_type} usage for user {user_id} by {amount}")
            return True

        except Exception as e:
            logger.error(f"Error incrementing usage for user {user_id}, resource {resource_type}: {e}")
            return False

    async def decrement_usage(
        self,
        user_id: str,
        resource_type: str,
        amount: int = 1
    ) -> bool:
        """
        Decrement usage counter (e.g., when deleting a monitor).

        Args:
            user_id: User identifier
            resource_type: Type of resource to decrement
            amount: Amount to decrement by

        Returns:
            True if successful, False otherwise
        """
        try:
            subscription = await self.get_subscription(user_id)

            if resource_type == "monitors":
                subscription.monitors_active = max(0, subscription.monitors_active - amount)

            subscription.updated_at = datetime.utcnow()
            await self.db.update_subscription(subscription)

            logger.info(f"Decremented {resource_type} usage for user {user_id} by {amount}")
            return True

        except Exception as e:
            logger.error(f"Error decrementing usage for user {user_id}, resource {resource_type}: {e}")
            return False

    async def get_usage_summary(self, user_id: str) -> UsageSummary:
        """
        Get comprehensive usage summary vs limits.

        Args:
            user_id: User identifier

        Returns:
            UsageSummary with current usage and limits
        """
        subscription = await self.get_subscription(user_id)
        limits = self._get_limits(subscription)

        # Get team member count
        team_members_count = await self._get_team_member_count(user_id)

        # Check if at any limit
        at_limit = (
            subscription.analyses_used >= limits.analyses_per_month or
            subscription.monitors_active >= limits.monitors or
            team_members_count >= limits.team_members
        )

        return UsageSummary(
            tier=subscription.tier,
            analyses_used=subscription.analyses_used,
            analyses_limit=limits.analyses_per_month,
            analyses_remaining=max(0, limits.analyses_per_month - subscription.analyses_used),
            monitors_active=subscription.monitors_active,
            monitors_limit=limits.monitors,
            team_members_count=team_members_count,
            team_members_limit=limits.team_members,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            at_limit=at_limit
        )

    async def reset_period_usage(self, user_id: str) -> bool:
        """
        Reset usage counters for new billing period.
        Called automatically when period rolls over.

        Args:
            user_id: User identifier

        Returns:
            True if successful
        """
        try:
            subscription = await self.get_subscription(user_id)

            # Reset counters
            subscription.analyses_used = 0
            # Note: monitors_active is not reset (it's a count, not usage)

            # Update period dates
            subscription.current_period_start = subscription.current_period_end
            subscription.current_period_end = subscription.current_period_start + timedelta(days=30)
            subscription.updated_at = datetime.utcnow()

            await self.db.update_subscription(subscription)

            logger.info(f"Reset usage for user {user_id} for new billing period")
            return True

        except Exception as e:
            logger.error(f"Error resetting period usage for user {user_id}: {e}")
            return False

    async def get_subscription(self, user_id: str) -> Subscription:
        """
        Get subscription for user, creating default free tier if none exists.

        Args:
            user_id: User identifier

        Returns:
            Subscription object
        """
        subscription = await self.db.get_subscription(user_id)

        if not subscription:
            # Create default free tier subscription
            now = datetime.utcnow()
            subscription = Subscription(
                id=f"sub_{user_id}",
                user_id=user_id,
                tier=PricingTier.FREE,
                status="active",
                current_period_start=now,
                current_period_end=now + timedelta(days=30),
                analyses_used=0,
                monitors_active=0
            )
            await self.db.create_subscription(subscription)
            logger.info(f"Created default free subscription for user {user_id}")

        return subscription

    def _get_limits(self, subscription: Subscription) -> TierLimits:
        """Get tier limits, respecting custom overrides"""
        if subscription.custom_limits:
            return subscription.custom_limits
        return TIER_CONFIGS[subscription.tier]

    async def _get_current_usage(
        self,
        user_id: str,
        resource_type: str,
        subscription: Subscription
    ) -> int:
        """Get current usage for a resource type"""
        if resource_type == "analyses":
            return subscription.analyses_used
        elif resource_type == "monitors":
            return subscription.monitors_active
        elif resource_type == "team_members":
            return await self._get_team_member_count(user_id)
        return 0

    async def _get_team_member_count(self, user_id: str) -> int:
        """Get count of team members"""
        # TODO: Implement team member counting when team management is added
        # For now, return 1 (just the user)
        return 1

    async def check_and_reset_if_needed(self, user_id: str) -> bool:
        """
        Check if billing period has ended and reset usage if needed.

        Args:
            user_id: User identifier

        Returns:
            True if reset occurred, False otherwise
        """
        try:
            subscription = await self.get_subscription(user_id)

            if datetime.utcnow() >= subscription.current_period_end:
                await self.reset_period_usage(user_id)
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking/resetting period for user {user_id}: {e}")
            return False


# Global usage tracker instance (initialized with DB service)
_usage_tracker: Optional[UsageTracker] = None


def get_usage_tracker(db_service: DatabaseService) -> UsageTracker:
    """Get or create global usage tracker instance"""
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker(db_service)
    return _usage_tracker
