"""
Tier enforcement middleware and decorators
"""
from functools import wraps
from typing import Callable, Optional
from fastapi import HTTPException, Depends, Header
from consultantos.models.subscription import PricingTier, TIER_CONFIGS
from consultantos.billing.usage_tracker import get_usage_tracker
from consultantos.database import get_db_service
import logging

logger = logging.getLogger(__name__)


# Tier hierarchy for permission checking
TIER_HIERARCHY = {
    PricingTier.FREE: 0,
    PricingTier.PRO: 1,
    PricingTier.ENTERPRISE: 2
}


async def get_current_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> Optional[str]:
    """
    Extract user ID from headers.
    In production, this would validate JWT token and extract user_id.
    """
    return x_user_id


async def check_tier_access(
    required_tier: PricingTier,
    user_id: Optional[str] = Depends(get_current_user_id)
) -> bool:
    """
    Dependency to check if user has required tier access.

    Args:
        required_tier: Minimum tier required
        user_id: Current user ID from headers

    Returns:
        True if authorized

    Raises:
        HTTPException: If tier insufficient
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide X-User-ID header."
        )

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    try:
        subscription = await usage_tracker.get_subscription(user_id)

        # Check tier hierarchy
        user_tier_level = TIER_HIERARCHY[subscription.tier]
        required_tier_level = TIER_HIERARCHY[required_tier]

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "insufficient_tier",
                    "message": f"This feature requires {required_tier.value} tier or higher",
                    "current_tier": subscription.tier.value,
                    "required_tier": required_tier.value,
                    "upgrade_url": "/billing/upgrade"
                }
            )

        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking tier access for user {user_id}: {e}")
        # Fail open for availability - allow the request
        return True


async def check_usage_limit(
    resource_type: str,
    user_id: Optional[str] = Depends(get_current_user_id),
    increment: int = 1
) -> bool:
    """
    Dependency to check if user is within usage limits.

    Args:
        resource_type: Type of resource (analyses, monitors, etc.)
        user_id: Current user ID
        increment: Amount to check (for pre-flight checks)

    Returns:
        True if within limits

    Raises:
        HTTPException: If limit exceeded
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    try:
        # Check if period needs reset
        await usage_tracker.check_and_reset_if_needed(user_id)

        # Check limits
        within_limit = await usage_tracker.check_limit(user_id, resource_type, increment)

        if not within_limit:
            subscription = await usage_tracker.get_subscription(user_id)
            limits = TIER_CONFIGS[subscription.tier]

            if resource_type == "analyses":
                limit = limits.analyses_per_month
                used = subscription.analyses_used
            elif resource_type == "monitors":
                limit = limits.monitors
                used = subscription.monitors_active
            else:
                limit = "N/A"
                used = "N/A"

            raise HTTPException(
                status_code=429,
                detail={
                    "error": "limit_exceeded",
                    "message": f"You have reached your {resource_type} limit for {subscription.tier.value} tier",
                    "resource_type": resource_type,
                    "limit": limit,
                    "used": used,
                    "tier": subscription.tier.value,
                    "upgrade_url": "/billing/upgrade"
                }
            )

        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking usage limit for user {user_id}: {e}")
        # Fail open for availability
        return True


def require_tier(required_tier: PricingTier):
    """
    Decorator to enforce tier requirements on endpoints.

    Usage:
        @router.post("/custom-framework")
        @require_tier(PricingTier.PRO)
        async def create_custom_framework(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or headers
            user_id = kwargs.get("user_id") or kwargs.get("x_user_id")

            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            await check_tier_access(required_tier, user_id)
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_usage_limit(resource_type: str, increment: int = 1):
    """
    Decorator to check usage limits before executing endpoint.

    Usage:
        @router.post("/analyze")
        @require_usage_limit("analyses")
        async def create_analysis(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or kwargs.get("x_user_id")

            if not user_id:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            await check_usage_limit(resource_type, user_id, increment)
            return await func(*args, **kwargs)

        return wrapper
    return decorator


async def check_feature_access(
    feature: str,
    user_id: Optional[str] = Depends(get_current_user_id)
) -> bool:
    """
    Check if user has access to a specific feature.

    Args:
        feature: Feature name (api_access, white_label, custom_frameworks, etc.)
        user_id: Current user ID

    Returns:
        True if authorized

    Raises:
        HTTPException: If feature not available in tier
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    try:
        subscription = await usage_tracker.get_subscription(user_id)
        limits = TIER_CONFIGS[subscription.tier]

        # Map feature to limit attribute
        feature_map = {
            "api_access": limits.api_access,
            "white_label": limits.white_label,
            "custom_frameworks": limits.custom_frameworks,
            "dedicated_support": limits.dedicated_support,
            "custom_integrations": limits.custom_integrations,
            "priority_processing": limits.priority_processing
        }

        if feature not in feature_map:
            logger.warning(f"Unknown feature: {feature}")
            return True  # Unknown features are allowed

        if not feature_map[feature]:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "feature_unavailable",
                    "message": f"Feature '{feature}' is not available in your {subscription.tier.value} tier",
                    "feature": feature,
                    "tier": subscription.tier.value,
                    "upgrade_url": "/billing/upgrade"
                }
            )

        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking feature access for user {user_id}: {e}")
        return True


async def check_export_format(
    export_format: str,
    user_id: Optional[str] = Depends(get_current_user_id)
) -> bool:
    """
    Check if user can export in requested format.

    Args:
        export_format: Requested format (pdf, docx, xlsx, json, pptx)
        user_id: Current user ID

    Returns:
        True if authorized

    Raises:
        HTTPException: If format not available
    """
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    try:
        subscription = await usage_tracker.get_subscription(user_id)
        limits = TIER_CONFIGS[subscription.tier]

        if export_format not in limits.export_formats:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "format_unavailable",
                    "message": f"Export format '{export_format}' is not available in {subscription.tier.value} tier",
                    "available_formats": limits.export_formats,
                    "requested_format": export_format,
                    "upgrade_url": "/billing/upgrade"
                }
            )

        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking export format for user {user_id}: {e}")
        return True
