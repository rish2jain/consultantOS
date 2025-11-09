"""
Subscription and pricing tier models
"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class PricingTier(str, Enum):
    """Subscription pricing tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIAL = "trial"
    SUSPENDED = "suspended"


class TierLimits(BaseModel):
    """Resource limits for each pricing tier"""
    tier: PricingTier
    analyses_per_month: int = Field(..., description="Number of analyses allowed per month")
    monitors: int = Field(..., description="Number of active monitors")
    team_members: int = Field(..., description="Number of team members allowed")
    frameworks: List[str] = Field(..., description="Available business frameworks")
    custom_frameworks: bool = Field(default=False, description="Can create custom frameworks")
    export_formats: List[str] = Field(..., description="Available export formats")
    api_access: bool = Field(default=False, description="Can use API")
    sla_hours: Optional[int] = Field(None, description="Support SLA in hours")
    white_label: bool = Field(default=False, description="White-label branding available")
    dedicated_support: bool = Field(default=False, description="Dedicated support manager")
    custom_integrations: bool = Field(default=False, description="Custom integrations available")
    priority_processing: bool = Field(default=False, description="Priority analysis queue")


# Tier configuration constants
TIER_CONFIGS = {
    PricingTier.FREE: TierLimits(
        tier=PricingTier.FREE,
        analyses_per_month=5,
        monitors=2,
        team_members=1,
        frameworks=["porter", "swot"],
        custom_frameworks=False,
        export_formats=["pdf"],
        api_access=False,
        sla_hours=None,
        white_label=False,
        dedicated_support=False,
        custom_integrations=False,
        priority_processing=False
    ),
    PricingTier.PRO: TierLimits(
        tier=PricingTier.PRO,
        analyses_per_month=50,
        monitors=20,
        team_members=10,
        frameworks=["porter", "swot", "pestel", "blue_ocean"],
        custom_frameworks=True,
        export_formats=["pdf", "docx", "xlsx", "json"],
        api_access=True,
        sla_hours=24,
        white_label=False,
        dedicated_support=False,
        custom_integrations=False,
        priority_processing=True
    ),
    PricingTier.ENTERPRISE: TierLimits(
        tier=PricingTier.ENTERPRISE,
        analyses_per_month=999999,  # Effectively unlimited
        monitors=999999,
        team_members=999999,
        frameworks=["porter", "swot", "pestel", "blue_ocean"],
        custom_frameworks=True,
        export_formats=["pdf", "docx", "xlsx", "json", "pptx"],
        api_access=True,
        sla_hours=4,
        white_label=True,
        dedicated_support=True,
        custom_integrations=True,
        priority_processing=True
    )
}


# Pricing in USD (monthly)
TIER_PRICING = {
    PricingTier.FREE: 0,
    PricingTier.PRO: 49,
    PricingTier.ENTERPRISE: None  # Contact sales
}


class Subscription(BaseModel):
    """User subscription record"""
    id: str = Field(..., description="Unique subscription ID")
    user_id: str = Field(..., description="User who owns this subscription")
    tier: PricingTier = Field(default=PricingTier.FREE, description="Current pricing tier")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE, description="Subscription status")
    current_period_start: datetime = Field(..., description="Current billing period start")
    current_period_end: datetime = Field(..., description="Current billing period end")
    analyses_used: int = Field(default=0, description="Analyses used in current period")
    monitors_active: int = Field(default=0, description="Currently active monitors")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    cancel_at_period_end: bool = Field(default=False, description="Will cancel at period end")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Special pricing/grandfathering
    custom_limits: Optional[TierLimits] = Field(None, description="Custom limits override")
    promo_code: Optional[str] = Field(None, description="Applied promo code")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sub_abc123",
                "user_id": "user_xyz789",
                "tier": "pro",
                "status": "active",
                "current_period_start": "2024-01-01T00:00:00Z",
                "current_period_end": "2024-02-01T00:00:00Z",
                "analyses_used": 10,
                "monitors_active": 5,
                "stripe_customer_id": "cus_123",
                "stripe_subscription_id": "sub_456"
            }
        }


class UsageSummary(BaseModel):
    """Current usage vs limits summary"""
    tier: PricingTier
    analyses_used: int
    analyses_limit: int
    analyses_remaining: int
    monitors_active: int
    monitors_limit: int
    team_members_count: int
    team_members_limit: int
    period_start: datetime
    period_end: datetime
    at_limit: bool = Field(..., description="True if any limit is reached")

    class Config:
        json_schema_extra = {
            "example": {
                "tier": "pro",
                "analyses_used": 35,
                "analyses_limit": 50,
                "analyses_remaining": 15,
                "monitors_active": 12,
                "monitors_limit": 20,
                "team_members_count": 5,
                "team_members_limit": 10,
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "2024-02-01T00:00:00Z",
                "at_limit": False
            }
        }


class PromoCode(BaseModel):
    """Promotional code for discounts"""
    code: str = Field(..., description="Promo code string")
    discount_percent: Optional[int] = Field(None, description="Percentage discount")
    discount_amount: Optional[int] = Field(None, description="Fixed amount discount in cents")
    max_redemptions: Optional[int] = Field(None, description="Max number of redemptions")
    redemptions_count: int = Field(default=0, description="Current redemptions")
    valid_from: datetime
    valid_until: Optional[datetime] = None
    applicable_tiers: List[PricingTier] = Field(default_factory=list, description="Tiers this applies to")
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BillingEvent(BaseModel):
    """Billing event for audit trail"""
    id: str
    subscription_id: str
    event_type: str = Field(..., description="Type: upgrade, downgrade, payment_success, payment_failed, etc.")
    amount: Optional[int] = Field(None, description="Amount in cents")
    currency: str = Field(default="usd")
    stripe_event_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UpgradeRequest(BaseModel):
    """Request to upgrade subscription tier"""
    target_tier: PricingTier
    promo_code: Optional[str] = None


class CheckoutSession(BaseModel):
    """Stripe checkout session response"""
    session_id: str
    checkout_url: str
    expires_at: datetime
