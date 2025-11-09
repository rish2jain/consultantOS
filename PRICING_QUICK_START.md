# Three-Tier Pricing Model - Quick Start Guide

## ✅ What's Been Implemented

### Backend (Complete)
1. **Subscription Models** (`consultantos/models/subscription.py`)
   - PricingTier enum (FREE, PRO, ENTERPRISE)
   - Complete tier configurations with limits
   - Subscription, UsageSummary, PromoCode models

2. **Usage Tracking** (`consultantos/billing/usage_tracker.py`)
   - Track analyses, monitors, team members
   - Auto-reset at billing period end
   - Get usage summaries

3. **Database Layer** (`consultantos/database.py`)
   - Subscription CRUD operations (both in-memory and Firestore)
   - Promo code management
   - Billing event tracking

4. **Tier Enforcement** (`consultantos/api/tier_middleware.py`)
   - `@require_tier()` decorator
   - `@require_usage_limit()` decorator
   - Feature access checks
   - Export format validation

5. **Stripe Integration** (`consultantos/billing/stripe_integration.py`)
   - Checkout session creation
   - Webhook handling
   - Subscription lifecycle management

6. **Promotions** (`consultantos/billing/promotions.py`)
   - Promo code creation/validation
   - Grandfathering for early users
   - Example campaigns (LAUNCH50, ANNUAL2024)

7. **API Endpoints** (`consultantos/api/billing_endpoints.py`)
   - GET /billing/subscription
   - GET /billing/usage
   - POST /billing/upgrade
   - POST /billing/downgrade
   - POST /billing/cancel
   - POST /billing/promo-code
   - POST /billing/webhook
   - GET /billing/history

8. **Documentation**
   - PRICING_IMPLEMENTATION_SUMMARY.md (detailed overview)
   - PRICING_GUIDE.md (user-facing tier comparison)
   - BILLING_FAQ.md (common questions)

## 🚀 Quick Integration (30 minutes)

### Step 1: Install Dependencies (2 min)
```bash
pip install stripe>=7.0.0
```

### Step 2: Environment Variables (3 min)
Add to `.env`:
```bash
# Stripe (get from https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# Price IDs (create products in Stripe Dashboard first)
STRIPE_PRICE_ID_PRO=price_YOUR_PRO_PRICE_ID
STRIPE_PRICE_ID_ENTERPRISE=price_YOUR_ENTERPRISE_PRICE_ID

# Frontend
FRONTEND_URL=http://localhost:3000
```

### Step 3: Update API Main (5 min)
Edit `consultantos/api/main.py`:

```python
# Add at top
from consultantos.api.billing_endpoints import router as billing_router
from consultantos.api.tier_middleware import check_usage_limit
from consultantos.billing.usage_tracker import get_usage_tracker
from consultantos.database import get_db_service

# Register billing router
app.include_router(billing_router, prefix="/billing", tags=["billing"])

# Add usage tracking to analysis endpoint
@app.post("/analyze", dependencies=[Depends(check_usage_limit("analyses"))])
async def create_analysis(
    request: AnalysisRequest,
    user_id: str = Depends(get_current_user_id)
):
    # ... existing code ...

    # After successful analysis, increment usage
    db_service = get_db_service()
    usage_tracker = get_usage_tracker(db_service)
    await usage_tracker.increment_usage(user_id, "analyses")

    return result
```

### Step 4: Create Stripe Products (10 min)
1. Go to https://dashboard.stripe.com/test/products
2. Create "ConsultantOS Pro":
   - Price: $49/month
   - Recurring billing
   - Copy Price ID → `.env` as `STRIPE_PRICE_ID_PRO`
3. Create "ConsultantOS Enterprise":
   - Custom pricing (or set high placeholder)
   - Copy Price ID → `.env` as `STRIPE_PRICE_ID_ENTERPRISE`
4. Go to Webhooks → Add endpoint:
   - URL: `https://your-api.com/billing/webhook`
   - Events: checkout.session.completed, invoice.payment_succeeded, invoice.payment_failed
   - Copy signing secret → `.env` as `STRIPE_WEBHOOK_SECRET`

### Step 5: Test Backend (5 min)
```bash
# Start server
python main.py

# Test subscription endpoint (replace USER_ID)
curl -H "X-User-ID: test-user" http://localhost:8080/billing/subscription

# Test usage endpoint
curl -H "X-User-ID: test-user" http://localhost:8080/billing/usage

# Should see FREE tier with default limits
```

### Step 6: Frontend Integration (5 min)
See `frontend/app/pricing/page.tsx` and `frontend/app/billing/page.tsx` examples in PRICING_IMPLEMENTATION_SUMMARY.md

## 🎯 Usage Examples

### Enforce Tier for Endpoint
```python
from consultantos.api.tier_middleware import require_tier
from consultantos.models.subscription import PricingTier

@router.post("/custom-framework")
@require_tier(PricingTier.PRO)
async def create_custom_framework(
    framework: CustomFramework,
    user_id: str = Depends(get_current_user_id)
):
    # Only PRO and ENTERPRISE users can access
    pass
```

### Check Usage Before Operation
```python
from consultantos.api.tier_middleware import check_usage_limit

@router.post("/monitor", dependencies=[Depends(check_usage_limit("monitors"))])
async def create_monitor(
    monitor: Monitor,
    user_id: str = Depends(get_current_user_id)
):
    # Check passed, create monitor
    await usage_tracker.increment_usage(user_id, "monitors")
    pass
```

### Validate Export Format
```python
from consultantos.api.tier_middleware import check_export_format

@router.get("/export/{format}")
async def export_report(
    format: str,
    user_id: str = Depends(get_current_user_id)
):
    # Will raise 403 if format not available in user's tier
    await check_export_format(format, user_id)

    # Generate export
    pass
```

### Create Promo Code
```python
from consultantos.billing.promotions import PromotionManager

promo_manager = PromotionManager()

# 50% off for 100 users
await promo_manager.create_promo_code(
    code="LAUNCH50",
    discount_percent=50,
    max_redemptions=100,
    valid_days=30,
    applicable_tiers=[PricingTier.PRO]
)
```

### Grandfather Early Users
```python
from consultantos.billing.promotions import PromotionManager
from consultantos.models.subscription import TierLimits, PricingTier

promo_manager = PromotionManager()

# Custom limits for early adopters
custom_limits = TierLimits(
    tier=PricingTier.FREE,
    analyses_per_month=10,  # 2x normal
    monitors=4,  # 2x normal
    team_members=1,
    frameworks=["porter", "swot", "pestel"],  # Bonus framework
    custom_frameworks=False,
    export_formats=["pdf", "docx"],  # Bonus format
    api_access=False
)

early_users = ["user1", "user2", "user3"]
await promo_manager.grandfather_early_users(early_users, custom_limits, "Early Adopter")
```

## 🧪 Testing Checklist

- [ ] Free user can create 5 analyses
- [ ] Free user blocked at 6th analysis with upgrade prompt
- [ ] Pro user can create 50 analyses
- [ ] Free user cannot export DOCX (only PRO+)
- [ ] Promo code validates correctly
- [ ] Stripe checkout URL generated
- [ ] Webhook processes checkout completion
- [ ] Subscription activates after payment
- [ ] Usage resets at period end
- [ ] Downgrade scheduled for period end
- [ ] Cancellation preserves access until period end

## 📊 Monitoring

### Key Metrics to Track
- **Conversion**: Free → Pro upgrade rate
- **MRR**: Monthly recurring revenue
- **Churn**: Cancellation rate
- **Limit Hits**: Users hitting usage limits (conversion opportunity)
- **Promo Redemptions**: Campaign effectiveness

### Logs to Watch
```bash
# Usage limit hits
grep "limit_exceeded" logs/

# Successful upgrades
grep "subscription_created" logs/

# Failed payments
grep "payment_failed" logs/
```

## 🔧 Troubleshooting

**Issue**: "insufficient_tier" error on valid endpoint
- Check `TIER_HIERARCHY` in `tier_middleware.py`
- Verify subscription tier in database
- Confirm user_id in headers

**Issue**: Stripe webhook fails verification
- Verify `STRIPE_WEBHOOK_SECRET` matches Stripe dashboard
- Check webhook endpoint is publicly accessible
- Ensure raw request body passed to Stripe verification

**Issue**: Usage not resetting
- Check `check_and_reset_if_needed()` called before usage checks
- Verify `current_period_end` date in subscription
- Check server timezone settings

**Issue**: Promo code not applying
- Verify code exists in database
- Check `valid_until` date
- Confirm tier in `applicable_tiers`
- Check max_redemptions not exceeded

## 📚 Next Steps

1. **Frontend**: Build pricing page and billing dashboard
2. **Analytics**: Add conversion tracking
3. **Email**: Implement upgrade prompts and payment reminders
4. **Testing**: Comprehensive E2E tests
5. **Production**: Switch to live Stripe keys
6. **Monitoring**: Set up billing alerts and dashboards

## 🎉 Success Criteria

- ✅ Three tiers clearly defined
- ✅ Usage tracking working
- ✅ Limits enforced at API level
- ✅ Stripe checkout functional
- ✅ Webhooks processing
- ✅ Promo codes working
- ⏳ Frontend pricing page
- ⏳ Billing dashboard
- ⏳ Production deployment

---

**Need Help?**
- Implementation summary: `PRICING_IMPLEMENTATION_SUMMARY.md`
- User guide: `PRICING_GUIDE.md`
- FAQ: `BILLING_FAQ.md`
