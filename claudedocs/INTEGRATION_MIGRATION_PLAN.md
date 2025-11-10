# Integration & Migration Plan

**Comprehensive strategy for integrating Phase 1 and Phase 2 skills into ConsultantOS with zero-downtime migration**

**Version**: 1.0
**Last Updated**: November 9, 2025
**Status**: Ready for Implementation

---

## Executive Summary

This document outlines the strategy for:

1. **Integrating Phase 1 + Phase 2** skills with existing ConsultantOS
2. **Migrating users** from current system to enhanced platform
3. **Managing backward compatibility** during transition
4. **Rolling out features** gradually with feature flags
5. **Mitigating risks** and ensuring production stability

**Timeline**: 16 weeks (4 months)
- Phase 1 Implementation: Weeks 1-8
- Phase 2 Implementation: Weeks 9-16
- Parallel rollout with feature flags

**Migration Approach**: Blue-Green deployment with gradual user migration

---

## Table of Contents

1. [Architecture Integration](#architecture-integration)
2. [Data Migration Strategy](#data-migration-strategy)
3. [Feature Flag System](#feature-flag-system)
4. [Backward Compatibility](#backward-compatibility)
5. [Rollout Strategy](#rollout-strategy)
6. [Risk Mitigation](#risk-mitigation)
7. [Testing Strategy](#testing-strategy)
8. [Monitoring & Observability](#monitoring--observability)
9. [User Communication](#user-communication)
10. [Rollback Plan](#rollback-plan)

---

## Architecture Integration

### Current ConsultantOS Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Existing System (v1.0)                     │
├──────────────────────────────────────────────────────────────┤
│  Research │ Market │ Financial │ Framework │ Synthesis       │
│  Agent    │ Agent  │ Agent     │ Agent     │ Agent           │
├──────────────────────────────────────────────────────────────┤
│                   Orchestrator (Multi-Agent)                  │
├──────────────────────────────────────────────────────────────┤
│  Monitoring System │ Anomaly Detection │ NLP Integration     │
├──────────────────────────────────────────────────────────────┤
│              FastAPI Backend + Next.js Frontend              │
├──────────────────────────────────────────────────────────────┤
│         Firestore │ Cloud Storage │ Cloud Run Deployment     │
└──────────────────────────────────────────────────────────────┘
```

### Integrated Architecture (v2.0)

```
┌──────────────────────────────────────────────────────────────┐
│                    Phase 2 Skills (NEW)                       │
│  Social Media │ Wargaming │ Analytics Builder │ Storytelling  │
├──────────────────────────────────────────────────────────────┤
│                    Phase 1 Skills (NEW)                       │
│  Conversational AI │ Forecasting │ Dark Data Mining          │
├──────────────────────────────────────────────────────────────┤
│                    Existing System (v1.0)                     │
│  Research │ Market │ Financial │ Framework │ Synthesis       │
├──────────────────────────────────────────────────────────────┤
│            Enhanced Orchestrator (Cross-Phase Routing)        │
├──────────────────────────────────────────────────────────────┤
│  Monitoring System │ Anomaly Detection │ NLP Integration     │
├──────────────────────────────────────────────────────────────┤
│              FastAPI Backend + Next.js Frontend              │
├──────────────────────────────────────────────────────────────┤
│         Firestore │ Cloud Storage │ Cloud Run Deployment     │
└──────────────────────────────────────────────────────────────┘
```

### Integration Layers

#### 1. Orchestrator Enhancement

**Current**: `AnalysisOrchestrator` coordinates 5 existing agents

**Enhanced**: `EnhancedOrchestrator` coordinates 12 agents (5 existing + 7 new)

**New Capabilities**:
- Cross-phase agent routing
- Intelligent skill selection based on query
- Parallel execution across phases
- Dependency resolution (e.g., Forecasting → Wargaming)

**Implementation**:

```python
# consultantos/orchestrator/enhanced_orchestrator.py

class EnhancedOrchestrator:
    """Enhanced orchestrator with Phase 1 + Phase 2 coordination."""

    def __init__(self):
        # Existing agents
        self.research_agent = ResearchAgent()
        self.market_agent = MarketAgent()
        self.financial_agent = FinancialAgent()
        self.framework_agent = FrameworkAgent()
        self.synthesis_agent = SynthesisAgent()

        # Phase 1 agents
        self.conversational_agent = ConversationalAgent()
        self.forecasting_agent = ForecastingAgent()
        self.dark_data_agent = DarkDataAgent()

        # Phase 2 agents
        self.social_media_agent = SocialMediaAgent()
        self.wargaming_agent = WarGamingAgent()
        self.storytelling_agent = StorytellingAgent()

    async def execute_analysis(
        self,
        company: str,
        industry: str,
        frameworks: List[str],
        enable_phase1: bool = False,
        enable_phase2: bool = False
    ):
        """Execute analysis with optional Phase 1/2 skills."""

        # Phase 0: Existing multi-agent analysis (always runs)
        phase0_results = await self._execute_phase0(company, industry, frameworks)

        results = {"phase0": phase0_results}

        # Phase 1: Conversational AI, Forecasting, Dark Data (optional)
        if enable_phase1:
            phase1_results = await self._execute_phase1(company, phase0_results)
            results["phase1"] = phase1_results

        # Phase 2: Social Media, Wargaming, Storytelling (optional)
        if enable_phase2:
            phase2_results = await self._execute_phase2(
                company,
                phase0_results,
                phase1_results if enable_phase1 else None
            )
            results["phase2"] = phase2_results

        return results

    async def _execute_phase1(self, company: str, phase0_results: Dict):
        """Execute Phase 1 skills in parallel."""
        tasks = [
            self.forecasting_agent.execute(
                metric_name="market_share",
                historical_data=phase0_results.get("market_data")
            ),
            self.dark_data_agent.execute(
                company=company,
                sources=["email", "slack"]
            )
        ]
        forecast, dark_data = await asyncio.gather(*tasks)
        return {"forecast": forecast, "dark_data": dark_data}

    async def _execute_phase2(
        self,
        company: str,
        phase0_results: Dict,
        phase1_results: Optional[Dict]
    ):
        """Execute Phase 2 skills with cross-phase integration."""

        tasks = []

        # Social Media Intelligence
        tasks.append(
            self.social_media_agent.execute(
                company=company,
                timeframe_hours=24
            )
        )

        # Wargaming (uses Phase 1 forecast if available)
        if phase1_results and "forecast" in phase1_results:
            tasks.append(
                self.wargaming_agent.execute(
                    scenario=Scenario(
                        action="price_cut_10_percent",
                        baseline_forecast=phase1_results["forecast"]
                    )
                )
            )

        # Execute in parallel
        results_list = await asyncio.gather(*tasks)

        # Storytelling (synthesizes all phases)
        all_data = {
            **phase0_results,
            **(phase1_results or {}),
            "social_media": results_list[0],
            "wargaming": results_list[1] if len(results_list) > 1 else None
        }

        narrative = await self.storytelling_agent.execute(
            analysis_data=all_data,
            target_audience="CEO"
        )

        return {
            "social_media": results_list[0],
            "wargaming": results_list[1] if len(results_list) > 1 else None,
            "narrative": narrative
        }
```

#### 2. API Versioning

**Strategy**: Maintain v1 endpoints, add v2 with new features

**Approach**:
```
/api/v1/analyze          → Existing functionality (unchanged)
/api/v2/analyze          → Enhanced with Phase 1/2 support
/api/v2/conversational   → New Phase 1 endpoints
/api/v2/social           → New Phase 2 endpoints
```

**Implementation**:

```python
# consultantos/api/main.py

from fastapi import FastAPI
from consultantos.api import v1_router, v2_router

app = FastAPI(title="ConsultantOS API", version="2.0")

# V1 routes (existing, unchanged)
app.include_router(v1_router, prefix="/api/v1")

# V2 routes (new, with Phase 1/2)
app.include_router(v2_router, prefix="/api/v2")
```

```python
# consultantos/api/v2/analysis_endpoints.py

@router.post("/analyze", response_model=EnhancedAnalysisResponse)
async def analyze_v2(
    request: AnalysisRequest,
    enable_phase1: bool = False,
    enable_phase2: bool = False
):
    """Enhanced analysis with optional Phase 1/2 skills."""
    orchestrator = EnhancedOrchestrator()
    return await orchestrator.execute_analysis(
        company=request.company,
        industry=request.industry,
        frameworks=request.frameworks,
        enable_phase1=enable_phase1,
        enable_phase2=enable_phase2
    )
```

#### 3. Database Schema Evolution

**Approach**: Additive schema changes (no breaking changes)

**New Collections**:
```
# Phase 1 Collections
conversations/           # Conversational AI chat history
forecasts/               # Forecasting predictions
dark_data_insights/      # Dark data mining results

# Phase 2 Collections
social_monitors/         # Social media monitoring configs
social_posts/            # Ingested social content
scenarios/               # Wargaming scenarios
simulations/             # Simulation results
dashboards/              # User-created dashboards
narratives/              # AI-generated narratives
```

**Migration**: Collections are created on-demand (no data migration required)

---

## Data Migration Strategy

### Migration Approach: Zero-Downtime Blue-Green

**Principle**: New features run in parallel with existing system, users gradually migrated

**Phases**:

1. **Green Environment (Existing)**: v1.0 continues serving all users
2. **Blue Environment (New)**: v2.0 deployed with Phase 1/2, feature flags OFF
3. **Gradual Migration**: Users opted-in to beta, feature flags ON
4. **Full Cutover**: All users on v2.0, v1.0 deprecated

### Migration Timeline

```
Week 0: Deploy v2.0 (Blue) with feature flags OFF
  ├─ All users on v1.0 (Green)
  └─ No impact to production

Week 2: Internal beta testing (10 internal users)
  ├─ Feature flags ON for internal users
  └─ Monitor errors, performance

Week 4: Public beta (10% of user base)
  ├─ Opt-in via dashboard
  └─ Collect feedback

Week 8: Gradual rollout (50% of users)
  ├─ Auto-migrate engaged users
  └─ Monitor metrics

Week 12: Full rollout (100% of users)
  ├─ v1.0 deprecated
  └─ v2.0 becomes default
```

### Data Compatibility

**Backward Compatibility**: All existing data (reports, monitors, templates) works with v2.0

**Forward Compatibility**: New data (forecasts, narratives) only available in v2.0

**Migration Required**: None (additive-only changes)

**User Impact**: Zero (seamless transition)

---

## Feature Flag System

### Implementation

**Library**: LaunchDarkly or custom Firestore-based flags

**Flags**:

```python
# consultantos/feature_flags.py

class FeatureFlags:
    """Feature flag management for gradual rollout."""

    def __init__(self):
        self.db = get_firestore_client()

    async def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        default: bool = False
    ) -> bool:
        """Check if feature is enabled for user."""

        # Check global flag
        global_flag = await self._get_global_flag(flag_name)
        if global_flag.get("enabled_for_all"):
            return True
        if global_flag.get("disabled_for_all"):
            return False

        # Check user-specific override
        if user_id:
            user_flag = await self._get_user_flag(flag_name, user_id)
            if user_flag:
                return user_flag.get("enabled", default)

        # Check percentage rollout
        percentage = global_flag.get("percentage", 0)
        if percentage > 0:
            # Deterministic hash-based rollout
            user_hash = hash(user_id or "anonymous") % 100
            return user_hash < percentage

        return default

    async def _get_global_flag(self, flag_name: str) -> Dict:
        doc = await self.db.collection("feature_flags").document(flag_name).get()
        return doc.to_dict() if doc.exists else {}

    async def _get_user_flag(self, flag_name: str, user_id: str) -> Optional[Dict]:
        doc = await self.db.collection("user_feature_flags") \
            .document(f"{user_id}_{flag_name}").get()
        return doc.to_dict() if doc.exists else None
```

### Flag Definitions

```yaml
feature_flags:
  phase1_conversational_ai:
    enabled_for_all: false
    percentage: 0  # 0-100
    description: "Conversational AI chat interface"

  phase1_forecasting:
    enabled_for_all: false
    percentage: 0
    description: "Predictive analytics and forecasting"

  phase1_dark_data:
    enabled_for_all: false
    percentage: 0
    description: "Dark data mining (email, Slack, Drive)"

  phase2_social_media:
    enabled_for_all: false
    percentage: 0
    description: "Social media intelligence monitoring"

  phase2_wargaming:
    enabled_for_all: false
    percentage: 0
    description: "Wargaming and scenario simulation"

  phase2_analytics_builder:
    enabled_for_all: false
    percentage: 0
    description: "Self-service analytics dashboard builder"

  phase2_storytelling:
    enabled_for_all: false
    percentage: 0
    description: "AI-powered data storytelling"
```

### Usage in Code

```python
# consultantos/api/v2/conversational_endpoints.py

@router.post("/chat")
async def chat(query: str, conversation_id: str, user_id: str):
    """Conversational AI endpoint (feature flagged)."""

    # Check feature flag
    flags = FeatureFlags()
    if not await flags.is_enabled("phase1_conversational_ai", user_id):
        raise HTTPException(
            status_code=403,
            detail="Conversational AI not enabled for this user"
        )

    # Execute agent
    agent = ConversationalAgent()
    return await agent.execute(query, conversation_id)
```

---

## Backward Compatibility

### API Compatibility

**v1 Endpoints**: Maintained indefinitely (no breaking changes)

**v2 Endpoints**: Superset of v1 (all v1 features available in v2)

**Deprecation Policy**:
- v1 supported for 12 months after v2 launch
- Deprecation warnings added to v1 responses (HTTP header: `X-API-Deprecated: true`)
- Migration guide provided in API documentation

### Data Model Compatibility

**Existing Models**: Unchanged (reports, monitors, alerts)

**New Models**: Additive only (forecasts, narratives, dashboards)

**Schema Versioning**:
```python
class Report(BaseModel):
    schema_version: str = "1.0"  # Existing reports
    # ... existing fields

class EnhancedReport(Report):
    schema_version: str = "2.0"  # New reports with Phase 1/2
    forecast: Optional[ForecastResult] = None
    narrative: Optional[Narrative] = None
    social_analysis: Optional[SocialMediaAnalysis] = None
```

### Frontend Compatibility

**v1 Dashboard**: Unchanged (continue to use v1 API)

**v2 Dashboard**: New UI with Phase 1/2 features (uses v2 API)

**User Choice**: Users can opt-in to v2 dashboard via feature flag

---

## Rollout Strategy

### Stage 1: Internal Beta (Week 2-4)

**Participants**: 10 internal users (engineering, product, executive team)

**Features Enabled**:
- Phase 1: Conversational AI, Forecasting
- Phase 2: Storytelling (CEO narratives only)

**Monitoring**:
- Error rates (<1% target)
- Response times (<2s target)
- User feedback (daily check-ins)

**Success Criteria**:
- ✅ Zero critical bugs
- ✅ Performance SLAs met
- ✅ Positive user feedback (≥4/5 rating)

### Stage 2: Public Beta (Week 4-8)

**Participants**: 10% of user base (opt-in via dashboard)

**Features Enabled**:
- All Phase 1 skills
- Phase 2: Social Media Intelligence only (to manage load)

**Monitoring**:
- Error rates, response times (Cloud Monitoring)
- User engagement (daily active users per skill)
- Support tickets (track common issues)

**Success Criteria**:
- ✅ ≥20% of beta users active weekly
- ✅ ≥4/5 satisfaction rating
- ✅ <5 critical bugs reported

### Stage 3: Gradual Rollout (Week 8-12)

**Participants**: 50% of user base (auto-enrolled based on engagement)

**Features Enabled**:
- All Phase 1 skills
- All Phase 2 skills (gradual: Social → Wargaming → Analytics → Storytelling)

**Rollout Cadence**:
- Week 8: Social Media Intelligence (50% users)
- Week 9: Wargaming Simulator (50% users)
- Week 10: Analytics Builder (50% users)
- Week 11: Data Storytelling (50% users)

**Monitoring**:
- Resource usage (CPU, memory, Cloud Run autoscaling)
- Cost metrics (Gemini API calls, social API calls)
- User retention (week-over-week)

**Success Criteria**:
- ✅ 99.9% uptime
- ✅ Cost per user < budget threshold
- ✅ ≥80% retention

### Stage 4: Full Rollout (Week 12+)

**Participants**: 100% of user base

**Features Enabled**: All Phase 1 + Phase 2 skills

**Transition**:
- v2.0 becomes default for all new users
- Existing users auto-migrated (email notification)
- v1.0 marked as deprecated (12-month sunset)

**Post-Launch Monitoring**: Continuous tracking of success metrics

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Social API Rate Limits** | HIGH | MEDIUM | Implement exponential backoff, queue management, batch processing |
| **LLM Cost Overruns** | HIGH | MEDIUM | Per-user quotas, model caching, prompt optimization |
| **Database Performance** | MEDIUM | LOW | Firestore index optimization, caching layer (Redis) |
| **Cloud Run Autoscaling** | MEDIUM | MEDIUM | Pre-warm instances, gradual traffic ramp, circuit breakers |
| **Wargaming Timeout** | LOW | HIGH | Async Cloud Tasks, reduce simulation iterations |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Low User Adoption** | HIGH | MEDIUM | In-app tutorials, sample dashboards, customer success outreach |
| **Feature Confusion** | MEDIUM | MEDIUM | Clear UI labels, onboarding flow, documentation |
| **Premium Tier Cannibalization** | HIGH | LOW | Phase 2 features behind paywall, free tier limits |
| **Competitor Launch** | MEDIUM | LOW | Accelerate timeline, differentiate on quality |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Deployment Failure** | HIGH | LOW | Canary deployments, automated rollback, pre-deploy tests |
| **Data Loss** | CRITICAL | VERY LOW | Daily Firestore backups, multi-region replication |
| **Security Breach** | CRITICAL | VERY LOW | OAuth2 scopes, API key rotation, PII detection, security audit |
| **Support Overwhelm** | MEDIUM | MEDIUM | Self-service docs, FAQ, chatbot support (Conversational AI!) |

---

## Testing Strategy

### Unit Tests

**Coverage Target**: ≥85% for all new modules

**Mocking Strategy**:
- Mock all external APIs (Twitter, LinkedIn, Reddit, Gemini)
- Use pytest fixtures for common test data
- Validate Pydantic models rigorously

**Test Files**:
```
tests/
├─ phase1/
│  ├─ test_conversational_agent.py
│  ├─ test_forecasting_agent.py
│  └─ test_dark_data_agent.py
├─ phase2/
│  ├─ test_social_media_agent.py
│  ├─ test_wargaming_agent.py
│  ├─ test_metric_engine.py
│  └─ test_storytelling_agent.py
└─ integration/
   ├─ test_enhanced_orchestrator.py
   └─ test_cross_phase_workflows.py
```

### Integration Tests

**Focus**: Cross-phase agent interactions

**Scenarios**:
1. **Conversational AI → Social Media**: User asks about sentiment, routes to social agent
2. **Forecasting → Wargaming**: Baseline forecast used in scenario simulation
3. **Dark Data → Storytelling**: Hidden insights surfaced in executive narrative

**Implementation**:
```python
# tests/integration/test_cross_phase_workflows.py

@pytest.mark.asyncio
async def test_conversational_to_social_routing():
    """Test ConversationalAgent routing to SocialMediaAgent."""
    conv_agent = ConversationalAgent()
    response = await conv_agent.execute(
        query="What's the social sentiment for Tesla?",
        conversation_id="test_123"
    )
    assert response.agent == "social_media"
    assert "sentiment" in response.response.lower()
```

### Performance Tests

**Load Testing**: Simulate 1000 concurrent users

**Stress Testing**: Push to 2000 users to find breaking point

**Endurance Testing**: Run for 24 hours to detect memory leaks

**Tools**: Locust, Apache JMeter

**Targets**:
- Social Media: 10,000 posts/hour ingestion
- Wargaming: 1000 simulations in <30 seconds
- Analytics: 100 concurrent dashboard loads

### User Acceptance Testing (UAT)

**Participants**: 20 representative users (analysts, executives, strategists)

**Scenarios**:
1. Create social media monitor and detect crisis
2. Simulate pricing scenario and compare outcomes
3. Build custom dashboard without coding
4. Generate executive narrative for board meeting

**Feedback Collection**: Post-task surveys, usability metrics (time-to-complete, error rates)

---

## Monitoring & Observability

### Metrics to Track

**System Health**:
- API response times (p50, p95, p99)
- Error rates (by endpoint, by agent)
- Cloud Run autoscaling events
- Database query performance

**Business Metrics**:
- Daily active users (overall, per skill)
- Feature adoption (% of users using Phase 1/2)
- Premium conversions (free → paid)
- User retention (day 7, day 30, day 90)

**Cost Metrics**:
- Gemini API token usage
- Social API call counts (Twitter, LinkedIn, Reddit)
- Cloud Run vCPU hours
- Firestore read/write operations

### Dashboards

**Engineering Dashboard** (Cloud Monitoring):
- Latency heatmaps
- Error rate trends
- Resource utilization (CPU, memory)
- Autoscaling metrics

**Business Dashboard** (Custom Analytics):
- User engagement funnel (signup → Phase 1 → Phase 2)
- Feature adoption over time
- Cohort retention analysis
- Revenue impact (premium tier)

### Alerting

**Critical Alerts** (PagerDuty):
- Error rate >1% for >5 minutes
- API response time p95 >3 seconds
- Cloud Run instance failures
- Database connection errors

**Warning Alerts** (Slack):
- Social API rate limits approaching
- Gemini token usage >80% of quota
- Unusual traffic patterns (potential DDoS)

---

## User Communication

### Pre-Launch (Week -2)

**Email Campaign**: "Exciting New Features Coming to ConsultantOS"
- Tease Phase 1 and Phase 2 capabilities
- Invite to beta testing (opt-in link)
- Timeline: "Rolling out over next 8 weeks"

**In-App Announcement**: Banner on dashboard
- "Try our new Conversational AI assistant (beta)"
- Link to feature tour

### During Rollout (Week 0-12)

**Weekly Updates**: Email newsletter
- Feature spotlight (e.g., "This week: Social Media Intelligence")
- Success stories (case studies from beta users)
- Tips and tricks (how to get the most value)

**In-App Onboarding**: Interactive tutorials
- Guided tour for each Phase 1/2 skill
- Sample scenarios and dashboards
- Video walkthroughs (2-3 minutes each)

### Post-Launch (Week 12+)

**Retrospective Blog Post**: "How We Built Conversational AI at ConsultantOS"
- Technical deep dive (engineering blog)
- User impact stories (product blog)
- Lessons learned

**Webinar Series**: "Mastering Phase 2 Skills"
- Live demos of wargaming, analytics builder, storytelling
- Q&A with product team
- Advanced use cases

---

## Rollback Plan

### Trigger Conditions

Rollback to v1.0 if:
- Error rate >5% for >30 minutes
- Critical data loss or corruption
- Security breach detected
- Performance degradation >50% (vs baseline)

### Rollback Procedure

**Automated Rollback** (Cloud Run):
```bash
# Rollback to previous revision
gcloud run services update consultantos \
  --platform managed \
  --region us-central1 \
  --to-latest
```

**Manual Rollback Steps**:

1. **Disable Feature Flags**: Set all Phase 1/2 flags to `enabled_for_all: false`
2. **Redirect Traffic**: Route 100% traffic to v1.0 Cloud Run service
3. **Database Rollback**: No action needed (additive schema changes only)
4. **User Notification**: In-app banner "Temporarily reverting to previous version"
5. **Incident Response**: Root cause analysis, bug fixes, re-deploy

**Recovery Time Objective (RTO)**: <15 minutes

**Recovery Point Objective (RPO)**: Zero data loss (all writes to Firestore are immediate)

---

## Success Criteria

### Technical Success (Week 12)

- ✅ **Uptime**: ≥99.9%
- ✅ **Error Rate**: <1%
- ✅ **Response Time**: p95 <2 seconds
- ✅ **Test Coverage**: ≥85%

### User Success (Day 90)

- ✅ **Engagement**: ≥40% of active users use Phase 1/2 features
- ✅ **Satisfaction**: ≥4.5/5 rating for new features
- ✅ **Retention**: ≥85% of Phase 2 users active after 90 days

### Business Success (Day 90)

- ✅ **Premium Conversion**: ≥15% of free users upgrade
- ✅ **Revenue Impact**: ≥20% increase in MRR
- ✅ **NPS**: ≥50 for Phase 2 features

---

## Timeline Summary

| Week | Milestone | Activities |
|------|-----------|------------|
| 0 | Deploy v2.0 (Blue) | Feature flags OFF, no user impact |
| 2 | Internal Beta | 10 internal users, Phase 1 + Storytelling |
| 4 | Public Beta Start | 10% of users, opt-in, Social Media only |
| 6 | Public Beta Expand | 10% users, all Phase 1 + Social Media |
| 8 | Gradual Rollout (50%) | Auto-enroll engaged users, Social + Wargaming |
| 10 | Add Analytics Builder | 50% users, all Phase 2 except Storytelling |
| 11 | Add Data Storytelling | 50% users, full Phase 2 |
| 12 | Full Rollout (100%) | All users, v2.0 default, v1.0 deprecated |
| 16 | Post-Launch Review | Retrospective, success metrics review |

---

## Appendices

### Appendix A: API Migration Guide

**v1 → v2 Mapping**:

| v1 Endpoint | v2 Endpoint | Changes |
|-------------|-------------|---------|
| `POST /api/v1/analyze` | `POST /api/v2/analyze` | Added `enable_phase1`, `enable_phase2` params |
| N/A | `POST /api/v2/conversational/chat` | New: Conversational AI |
| N/A | `POST /api/v2/forecast` | New: Forecasting |
| N/A | `POST /api/v2/social/analyze` | New: Social Media |
| N/A | `POST /api/v2/wargaming/simulate` | New: Wargaming |
| N/A | `POST /api/v2/analytics/evaluate-metric` | New: Analytics Builder |
| N/A | `POST /api/v2/storytelling/generate` | New: Storytelling |

### Appendix B: Database Migration Scripts

**Firestore Index Creation**:

```bash
# Create indexes for Phase 1/2 collections
gcloud firestore indexes create --collection-group=social_posts \
  --field-config field-path=monitor_id,order=ASCENDING \
  --field-config field-path=created_at,order=DESCENDING

gcloud firestore indexes create --collection-group=scenarios \
  --field-config field-path=user_id,order=ASCENDING \
  --field-config field-path=created_at,order=DESCENDING

gcloud firestore indexes create --collection-group=dashboards \
  --field-config field-path=user_id,order=ASCENDING \
  --field-config field-path=updated_at,order=DESCENDING
```

### Appendix C: Environment Variables

**New Variables for Phase 1/2**:

```bash
# Phase 1
ENABLE_PHASE1=true
ENABLE_FORECASTING=true
ENABLE_DARK_DATA=true

# Phase 2
ENABLE_PHASE2=true
TWITTER_API_KEY=<your_key>
TWITTER_API_SECRET=<your_secret>
LINKEDIN_CLIENT_ID=<your_id>
LINKEDIN_CLIENT_SECRET=<your_secret>
REDDIT_CLIENT_ID=<your_id>
REDDIT_CLIENT_SECRET=<your_secret>

# Feature Flags
FEATURE_FLAG_BACKEND=firestore  # or "launchdarkly"
LAUNCHDARKLY_SDK_KEY=<your_key>  # if using LaunchDarkly
```

---

**Document Version**: 1.0
**Last Updated**: November 9, 2025
**Next Review**: Week 4 (Post-Beta Launch)
**Maintained By**: Engineering Lead, Product Manager
