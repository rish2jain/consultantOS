"""
Stripe billing integration
"""
import stripe
from typing import Optional, Dict
from datetime import datetime, timedelta
from consultantos.config import settings
from consultantos.models.subscription import (
    PricingTier, Subscription, SubscriptionStatus,
    CheckoutSession, BillingEvent
)
from consultantos.database import get_db_service
import logging
import uuid

logger = logging.getLogger(__name__)

# Initialize Stripe with secret key
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


class StripeIntegration:
    """Handle Stripe billing operations"""

    def __init__(self):
        self.db = get_db_service()

    async def create_checkout_session(
        self,
        user_id: str,
        tier: PricingTier,
        promo_code: Optional[str] = None
    ) -> CheckoutSession:
        """
        Create Stripe checkout session for subscription upgrade.

        Args:
            user_id: User identifier
            tier: Target pricing tier
            promo_code: Optional promo code

        Returns:
            CheckoutSession with checkout URL
        """
        try:
            # Get user details
            user = await self.db.get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Map tier to Stripe Price ID
            price_id = self._get_price_id(tier)

            # Create checkout session
            session_params = {
                "customer_email": user.email,
                "line_items": [{
                    "price": price_id,
                    "quantity": 1
                }],
                "mode": "subscription",
                "success_url": f"{settings.frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
                "cancel_url": f"{settings.frontend_url}/billing/cancel",
                "metadata": {
                    "user_id": user_id,
                    "tier": tier.value
                }
            }

            # Add promo code if provided
            if promo_code:
                # In production, validate promo code in Stripe
                session_params["discounts"] = [{
                    "coupon": promo_code
                }]

            session = stripe.checkout.Session.create(**session_params)

            return CheckoutSession(
                session_id=session.id,
                checkout_url=session.url,
                expires_at=datetime.fromtimestamp(session.expires_at)
            )

        except Exception as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    async def handle_webhook(self, event: Dict) -> bool:
        """
        Handle Stripe webhook events.

        Args:
            event: Stripe event object

        Returns:
            True if handled successfully
        """
        event_type = event.get("type")

        try:
            if event_type == "checkout.session.completed":
                await self._handle_checkout_completed(event["data"]["object"])
            elif event_type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event["data"]["object"])
            elif event_type == "invoice.payment_failed":
                await self._handle_payment_failed(event["data"]["object"])
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(event["data"]["object"])
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event["data"]["object"])
            else:
                logger.info(f"Unhandled event type: {event_type}")

            return True

        except Exception as e:
            logger.error(f"Error handling webhook {event_type}: {e}")
            return False

    async def _handle_checkout_completed(self, session: Dict):
        """Handle successful checkout"""
        user_id = session["metadata"]["user_id"]
        tier = PricingTier(session["metadata"]["tier"])
        subscription_id = session["subscription"]

        # Create or update subscription
        now = datetime.utcnow()
        subscription = Subscription(
            id=f"sub_{user_id}",
            user_id=user_id,
            tier=tier,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=now + timedelta(days=30),
            analyses_used=0,
            monitors_active=0,
            stripe_customer_id=session["customer"],
            stripe_subscription_id=subscription_id
        )

        await self.db.create_subscription(subscription)

        # Log billing event
        event = BillingEvent(
            id=str(uuid.uuid4()),
            subscription_id=subscription.id,
            event_type="subscription_created",
            amount=session.get("amount_total"),
            currency="usd",
            stripe_event_id=session["id"]
        )
        await self.db.create_billing_event(event)

        logger.info(f"Activated {tier.value} subscription for user {user_id}")

    async def _handle_payment_succeeded(self, invoice: Dict):
        """Handle successful payment"""
        subscription_id = invoice.get("subscription")
        # Log successful payment event
        logger.info(f"Payment succeeded for subscription {subscription_id}")

    async def _handle_payment_failed(self, invoice: Dict):
        """Handle failed payment"""
        subscription_id = invoice.get("subscription")

        # Find user by Stripe subscription ID
        # In production, maintain a mapping or query Firestore
        logger.warning(f"Payment failed for subscription {subscription_id}")

        # Update subscription status to past_due
        # await self.db.update_subscription(...)

    async def _handle_subscription_updated(self, subscription: Dict):
        """Handle subscription updates"""
        # Handle plan changes, renewals, etc.
        logger.info(f"Subscription updated: {subscription['id']}")

    async def _handle_subscription_deleted(self, subscription: Dict):
        """Handle subscription cancellation"""
        # Update user subscription to cancelled
        logger.info(f"Subscription cancelled: {subscription['id']}")

    def _get_price_id(self, tier: PricingTier) -> str:
        """Map tier to Stripe Price ID"""
        if tier == PricingTier.PRO:
            return settings.stripe_price_id_pro
        elif tier == PricingTier.ENTERPRISE:
            return settings.stripe_price_id_enterprise
        else:
            raise ValueError(f"No price ID for tier: {tier}")
