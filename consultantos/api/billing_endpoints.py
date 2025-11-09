"""
Billing and subscription management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from typing import Optional, List
from consultantos.models.subscription import (
    Subscription, UsageSummary, UpgradeRequest,
    CheckoutSession, BillingEvent, PricingTier
)
from consultantos.billing.usage_tracker import get_usage_tracker
from consultantos.billing.stripe_integration import StripeIntegration
from consultantos.billing.promotions import PromotionManager
from consultantos.database import get_db_service
from consultantos.api.tier_middleware import get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/subscription", response_model=Subscription)
async def get_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Get current subscription details"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    subscription = await usage_tracker.get_subscription(user_id)
    return subscription


@router.get("/usage", response_model=UsageSummary)
async def get_usage(
    user_id: str = Depends(get_current_user_id)
):
    """Get current usage summary"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    # Check and reset if period ended
    await usage_tracker.check_and_reset_if_needed(user_id)

    usage_summary = await usage_tracker.get_usage_summary(user_id)
    return usage_summary


@router.post("/upgrade", response_model=CheckoutSession)
async def initiate_upgrade(
    request: UpgradeRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Initiate subscription upgrade"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    stripe_integration = StripeIntegration()

    # Validate promo code if provided
    if request.promo_code:
        promo_manager = PromotionManager()
        promo = await promo_manager.validate_promo_code(
            request.promo_code,
            request.target_tier
        )
        if not promo:
            raise HTTPException(status_code=400, detail="Invalid promo code")

    # Create Stripe checkout session
    checkout_session = await stripe_integration.create_checkout_session(
        user_id=user_id,
        tier=request.target_tier,
        promo_code=request.promo_code
    )

    return checkout_session


@router.post("/downgrade")
async def schedule_downgrade(
    target_tier: PricingTier,
    user_id: str = Depends(get_current_user_id)
):
    """Schedule downgrade at period end"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    subscription = await usage_tracker.get_subscription(user_id)

    # Validate downgrade path
    from consultantos.api.tier_middleware import TIER_HIERARCHY
    if TIER_HIERARCHY[target_tier] >= TIER_HIERARCHY[subscription.tier]:
        raise HTTPException(
            status_code=400,
            detail="Cannot downgrade to same or higher tier. Use /upgrade instead."
        )

    # Schedule for period end
    subscription.cancel_at_period_end = True
    # In production, update Stripe subscription with new price at period end

    await db_service.update_subscription(subscription)

    return {
        "message": f"Downgrade to {target_tier.value} scheduled for {subscription.current_period_end}",
        "effective_date": subscription.current_period_end
    }


@router.post("/cancel")
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Cancel subscription at period end"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    subscription = await usage_tracker.get_subscription(user_id)
    subscription.cancel_at_period_end = True

    # Cancel in Stripe if Stripe subscription exists
    if subscription.stripe_subscription_id:
        import stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

    await db_service.update_subscription(subscription)

    return {
        "message": "Subscription cancelled. Access continues until period end.",
        "access_until": subscription.current_period_end
    }


@router.post("/promo-code")
async def apply_promo_code(
    code: str,
    user_id: str = Depends(get_current_user_id)
):
    """Validate and apply promo code"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)
    promo_manager = PromotionManager()

    subscription = await usage_tracker.get_subscription(user_id)

    # Validate promo code
    promo = await promo_manager.validate_promo_code(code, subscription.tier)
    if not promo:
        raise HTTPException(status_code=400, detail="Invalid or expired promo code")

    return {
        "valid": True,
        "code": promo.code,
        "discount_percent": promo.discount_percent,
        "discount_amount": promo.discount_amount,
        "message": f"Promo code {promo.code} is valid!"
    }


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    import stripe
    from consultantos.config import settings

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle event
    stripe_integration = StripeIntegration()
    success = await stripe_integration.handle_webhook(event)

    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/history", response_model=List[BillingEvent])
async def get_billing_history(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id)
):
    """Get billing event history"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)

    subscription = await usage_tracker.get_subscription(user_id)
    events = await db_service.list_billing_events(subscription.id, limit)

    return events
