"""
Promotional code management and grandfathering
"""
from datetime import datetime, timedelta
from typing import Optional, List
from consultantos.models.subscription import (
    PromoCode, PricingTier, TierLimits, Subscription
)
from consultantos.database import get_db_service
import logging

logger = logging.getLogger(__name__)


class PromotionManager:
    """Manage promotional codes and special pricing"""

    def __init__(self):
        self.db = get_db_service()

    async def create_promo_code(
        self,
        code: str,
        discount_percent: Optional[int] = None,
        discount_amount: Optional[int] = None,
        max_redemptions: Optional[int] = None,
        valid_days: int = 30,
        applicable_tiers: Optional[List[PricingTier]] = None
    ) -> PromoCode:
        """
        Create a promotional code.

        Args:
            code: Promo code string
            discount_percent: Percentage discount (0-100)
            discount_amount: Fixed amount discount in cents
            max_redemptions: Maximum number of redemptions
            valid_days: Number of days code is valid
            applicable_tiers: Tiers this code applies to

        Returns:
            Created PromoCode
        """
        now = datetime.utcnow()
        promo = PromoCode(
            code=code.upper(),
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            max_redemptions=max_redemptions,
            redemptions_count=0,
            valid_from=now,
            valid_until=now + timedelta(days=valid_days),
            applicable_tiers=applicable_tiers or list(PricingTier),
            active=True
        )

        await self.db.create_promo_code(promo)
        logger.info(f"Created promo code: {code}")

        return promo

    async def validate_promo_code(
        self,
        code: str,
        tier: PricingTier
    ) -> Optional[PromoCode]:
        """
        Validate a promo code for use.

        Args:
            code: Promo code to validate
            tier: Target tier for subscription

        Returns:
            PromoCode if valid, None otherwise
        """
        promo = await self.db.get_promo_code(code.upper())

        if not promo:
            logger.warning(f"Promo code not found: {code}")
            return None

        # Check if active
        if not promo.active:
            logger.warning(f"Promo code inactive: {code}")
            return None

        # Check validity dates
        now = datetime.utcnow()
        if now < promo.valid_from:
            logger.warning(f"Promo code not yet valid: {code}")
            return None

        if promo.valid_until and now > promo.valid_until:
            logger.warning(f"Promo code expired: {code}")
            return None

        # Check max redemptions
        if promo.max_redemptions and promo.redemptions_count >= promo.max_redemptions:
            logger.warning(f"Promo code max redemptions reached: {code}")
            return None

        # Check applicable tiers
        if tier not in promo.applicable_tiers:
            logger.warning(f"Promo code not applicable to tier {tier}: {code}")
            return None

        return promo

    async def redeem_promo_code(self, code: str) -> bool:
        """
        Increment redemption count for promo code.

        Args:
            code: Promo code being redeemed

        Returns:
            True if successful
        """
        promo = await self.db.get_promo_code(code.upper())
        if not promo:
            return False

        promo.redemptions_count += 1
        await self.db.update_promo_code(promo)

        logger.info(f"Redeemed promo code: {code} ({promo.redemptions_count} total)")
        return True

    async def grandfather_early_users(
        self,
        user_ids: List[str],
        custom_limits: TierLimits,
        label: str = "Early Adopter"
    ) -> int:
        """
        Apply grandfathered pricing/limits to early users.

        Args:
            user_ids: List of user IDs to grandfather
            custom_limits: Custom tier limits to apply
            label: Label for grandfathering (e.g., "Early Adopter", "Beta User")

        Returns:
            Number of users successfully grandfathered
        """
        count = 0
        for user_id in user_ids:
            try:
                from consultantos.billing.usage_tracker import get_usage_tracker
                usage_tracker = get_usage_tracker(self.db)
                subscription = await usage_tracker.get_subscription(user_id)

                # Apply custom limits
                subscription.custom_limits = custom_limits

                # Add note to subscription metadata (if we extend the model)
                # subscription.grandfathered = True
                # subscription.grandfathered_label = label

                await self.db.update_subscription(subscription)
                count += 1

                logger.info(f"Grandfathered user {user_id} with {label} limits")

            except Exception as e:
                logger.error(f"Failed to grandfather user {user_id}: {e}")

        logger.info(f"Grandfathered {count}/{len(user_ids)} users as '{label}'")
        return count

    async def create_launch_promo(self) -> PromoCode:
        """Create a launch promotion (example)"""
        return await self.create_promo_code(
            code="LAUNCH50",
            discount_percent=50,
            max_redemptions=100,
            valid_days=30,
            applicable_tiers=[PricingTier.PRO]
        )

    async def create_annual_upgrade_promo(self) -> PromoCode:
        """Create annual upgrade promotion (example)"""
        return await self.create_promo_code(
            code="ANNUAL2024",
            discount_amount=9900,  # $99 off in cents
            max_redemptions=None,  # Unlimited
            valid_days=365,
            applicable_tiers=[PricingTier.PRO, PricingTier.ENTERPRISE]
        )
