# Phase 1 Skills - Implementation Summary

**Document**: Quick reference for implementing Phase 1 skills
**Full Architecture**: See `PHASE1_ARCHITECTURE.md` for complete details
**Date**: 2025-01-09

---

## Quick Overview

### Three Skills to Implement

1. **Conversational AI Interface** - Chat-based intelligence with RAG
2. **Enhanced Predictive Analytics** - Forecasting + scenario simulation
3. **Dark Data Mining** - Extract insights from emails/Slack/documents

### Key Stats
- **New Agents**: 3 (ConversationalAgent, ForecastingAgent, DarkDataAgent)
- **New Collections**: 8 Firestore collections
- **New Endpoints**: 23 API endpoints
- **Resource Requirements**: +9GB memory, +2GB storage
- **Development Time**: 10 weeks (2 weeks per skill + 4 weeks integration/testing)

---

## Implementation Checklist

### Week 1-2: Foundation ✅

**Database Setup**:
- [ ] Create `conversations` collection with indexes
- [ ] Create `conversation_messages` subcollection
- [ ] Create `rag_documents` collection with vector index
- [ ] Create `forecasts` collection
- [ ] Create `forecast_scenarios` collection
- [ ] Create `dark_data_sources` collection
- [ ] Create `dark_data_insights` collection
- [ ] Create `dark_data_entities` collection

**Agent Implementation**:
- [ ] `consultantos/agents/conversational_agent.py` (ConversationalAgent)
- [ ] `consultantos/agents/forecasting_agent.py` (ForecastingAgent)
- [ ] `consultantos/agents/dark_data_agent.py` (DarkDataAgent)

**Utilities**:
- [ ] `consultantos/utils/rag_system.py` (RAG embeddings + retrieval)
- [ ] `consultantos/utils/query_router.py` (Intent classification)
- [ ] `consultantos/utils/conversation_state.py` (State management)
- [ ] `consultantos/utils/scenario_simulator.py` (What-if scenarios)
- [ ] `consultantos/utils/data_connectors.py` (Gmail, Slack, Drive connectors)
- [ ] `consultantos/utils/dark_data_processor.py` (NLP pipeline)
- [ ] `consultantos/utils/privacy_manager.py` (PII detection + GDPR)

### Week 3-4: Core Features 🔧

**API Endpoints**:
- [ ] `consultantos/api/chat_endpoints.py` (7 endpoints)
- [ ] `consultantos/api/forecasting_endpoints.py` (7 endpoints)
- [ ] `consultantos/api/dark_data_endpoints.py` (9 endpoints)

**Models**:
- [ ] `consultantos/models/conversational.py` (ConversationQuery, ConversationResponse, etc.)
- [ ] `consultantos/models/forecasting.py` (ForecastRequest, ForecastResponse, ScenarioParameters, etc.)
- [ ] `consultantos/models/dark_data.py` (DarkDataSource, DarkDataInsight, ExtractionRequest, etc.)

**Integration**:
- [ ] Extend `AnalysisOrchestrator` with Phase 4 (conversational/forecasting/dark data)
- [ ] Extend `AnomalyDetector` with `forecast()` method
- [ ] Extend `IntelligenceMonitor` to integrate dark data signals
- [ ] Extend `MonitorAnalysisSnapshot` with forecast + dark data fields

### Week 5-6: Frontend Integration 🎨

**New UI Components**:
- [ ] `frontend/app/chat/page.tsx` (Chat UI)
- [ ] `frontend/app/dashboard/forecasting/page.tsx` (Forecasting UI)
- [ ] `frontend/app/dashboard/dark-data/page.tsx` (Dark Data Dashboard)
- [ ] `frontend/components/ChatMessage.tsx` (Message component)
- [ ] `frontend/components/ForecastChart.tsx` (Forecast visualization)
- [ ] `frontend/components/ScenarioComparison.tsx` (Scenario comparison UI)
- [ ] `frontend/components/InsightCard.tsx` (Dark data insights)
- [ ] `frontend/components/EntityGraph.tsx` (Entity relationship graph)

**API Integration**:
- [ ] Update `frontend/lib/api.ts` with new endpoints
- [ ] Add SSE support for streaming chat responses

### Week 7-8: Testing & Security 🧪

**Unit Tests** (≥80% coverage):
- [ ] `tests/test_conversational_agent.py`
- [ ] `tests/test_forecasting_agent.py`
- [ ] `tests/test_dark_data_agent.py`
- [ ] `tests/test_rag_system.py`
- [ ] `tests/test_scenario_simulator.py`
- [ ] `tests/test_privacy_manager.py`
- [ ] `tests/test_data_connectors.py`

**Integration Tests**:
- [ ] `tests/integration/test_conversational_flow.py`
- [ ] `tests/integration/test_forecasting_pipeline.py`
- [ ] `tests/integration/test_dark_data_extraction.py`

**E2E Tests**:
- [ ] `tests/e2e/test_chat_ui.py` (Playwright)
- [ ] `tests/e2e/test_forecasting_ui.py` (Playwright)
- [ ] `tests/e2e/test_dark_data_ui.py` (Playwright)

**Security Audit**:
- [ ] PII detection accuracy >95%
- [ ] RBAC implementation (Admin, Analyst, Viewer roles)
- [ ] OAuth2 implementation for data connectors
- [ ] Encryption of OAuth tokens
- [ ] Audit logging for dark data access
- [ ] Rate limiting enforcement
- [ ] Prompt injection prevention

### Week 9-10: Deployment & Launch 🚀

**Infrastructure**:
- [ ] Set up Firestore indexes (`firebase firestore:indexes:deploy`)
- [ ] Create secrets in Secret Manager (OAUTH_ENCRYPTION_KEY, etc.)
- [ ] Configure Cloud Run with new environment variables

**Data Migration**:
- [ ] Run `scripts/backfill_rag_documents.py` (index existing reports)
- [ ] Run `scripts/migrate_monitor_snapshots.py` (extend snapshots)

**Deployment**:
- [ ] Deploy backend to Cloud Run (canary: 10% → 50% → 100%)
- [ ] Deploy frontend (Next.js build)
- [ ] Set up monitoring dashboards
- [ ] Configure alerts (latency, accuracy, PII detection)

**Launch**:
- [ ] Beta rollout to 10 users
- [ ] Gather feedback
- [ ] Iterate based on feedback
- [ ] General availability

---

## Quick Reference: File Structure

```
consultantos/
├── agents/
│   ├── conversational_agent.py         # NEW
│   ├── forecasting_agent.py            # NEW
│   └── dark_data_agent.py              # NEW
├── api/
│   ├── chat_endpoints.py               # NEW
│   ├── forecasting_endpoints.py        # NEW
│   └── dark_data_endpoints.py          # NEW
├── models/
│   ├── conversational.py               # NEW
│   ├── forecasting.py                  # NEW
│   └── dark_data.py                    # NEW
├── utils/
│   ├── rag_system.py                   # NEW
│   ├── query_router.py                 # NEW
│   ├── conversation_state.py           # NEW
│   ├── scenario_simulator.py           # NEW
│   ├── data_connectors.py              # NEW
│   ├── dark_data_processor.py          # NEW
│   └── privacy_manager.py              # NEW
├── monitoring/
│   ├── anomaly_detector.py             # EXTEND: add forecast()
│   ├── intelligence_monitor.py         # EXTEND: add dark_data_signals
│   └── timeseries_optimizer.py         # EXTEND: expose get_timeseries()
└── orchestrator/
    └── orchestrator.py                 # EXTEND: add Phase 4

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx                    # NEW
│   └── dashboard/
│       ├── forecasting/
│       │   └── page.tsx                # NEW
│       └── dark-data/
│           └── page.tsx                # NEW
└── components/
    ├── ChatMessage.tsx                 # NEW
    ├── ForecastChart.tsx               # NEW
    ├── ScenarioComparison.tsx          # NEW
    ├── InsightCard.tsx                 # NEW
    └── EntityGraph.tsx                 # NEW

scripts/
├── backfill_rag_documents.py           # NEW
└── migrate_monitor_snapshots.py        # NEW

tests/
├── test_conversational_agent.py        # NEW
├── test_forecasting_agent.py           # NEW
├── test_dark_data_agent.py             # NEW
├── integration/
│   ├── test_conversational_flow.py     # NEW
│   ├── test_forecasting_pipeline.py    # NEW
│   └── test_dark_data_extraction.py    # NEW
└── e2e/
    ├── test_chat_ui.py                 # NEW
    ├── test_forecasting_ui.py          # NEW
    └── test_dark_data_ui.py            # NEW
```

---

## Quick Reference: API Endpoints

### Conversational AI (`/chat`)
- `POST /chat/conversations` - Create conversation
- `POST /chat/conversations/{id}/messages` - Send message (streaming or not)
- `GET /chat/conversations/{id}` - Get conversation history
- `GET /chat/conversations` - List conversations
- `DELETE /chat/conversations/{id}` - Delete conversation
- `POST /chat/rag/index` - Index report for RAG
- `GET /chat/suggestions` - Get query suggestions

### Predictive Analytics (`/forecasting`)
- `POST /forecasting/generate` - Generate forecast
- `GET /forecasting/{forecast_id}` - Get forecast
- `POST /forecasting/scenarios` - Run scenario simulation
- `GET /forecasting/scenarios/{id}` - Get scenario results
- `GET /forecasting/monitors/{id}/forecasts` - Get monitor forecasts
- `POST /forecasting/compare` - Compare scenarios
- `GET /forecasting/accuracy` - Get accuracy metrics

### Dark Data Mining (`/dark-data`)
- `POST /dark-data/sources` - Connect new source (OAuth)
- `GET /dark-data/sources` - List connected sources
- `DELETE /dark-data/sources/{id}` - Disconnect source
- `POST /dark-data/extract` - Trigger extraction job
- `GET /dark-data/insights` - Query insights
- `GET /dark-data/entities` - Get entity relationships
- `GET /dark-data/trends` - Get trending topics
- `GET /dark-data/jobs/{job_id}` - Get job status
- `POST /dark-data/privacy/redact` - Manual PII redaction

---

## Quick Reference: Performance Targets

| Skill | Metric | Target |
|-------|--------|--------|
| **Conversational AI** | Response time (p95) | <5s |
| | Cache hit rate | >60% |
| | Concurrent conversations | 100 |
| **Predictive Analytics** | Forecast generation (p95) | <10s |
| | Scenario simulation (p95) | <15s |
| | Forecast accuracy (MAE) | <15% |
| **Dark Data Mining** | Processing speed | 10,000 docs/hour |
| | PII detection accuracy | >95% |
| | Extraction time (100 docs) | <30s |

---

## Quick Reference: Resource Requirements

**Conversational AI**:
- Memory: 2GB per instance
- CPU: 1 vCPU per 20 conversations
- Storage: 100MB per 1,000 conversations
- LLM tokens: 2,000 tokens/query avg

**Predictive Analytics**:
- Memory: 4GB per instance
- CPU: 2 vCPUs (Prophet training)
- Storage: 50MB per 100 forecasts
- Computation: 10 CPU-seconds per forecast

**Dark Data Mining**:
- Memory: 3GB per instance
- CPU: 2 vCPUs (NLP processing)
- Storage: 500MB per 10,000 documents
- API calls: 1 external API call per document

---

## Quick Reference: Security Checklist

- [ ] API key authentication (existing `auth.py`)
- [ ] OAuth2 for data connectors (Gmail, Slack, Drive)
- [ ] RBAC for dark data (Admin, Analyst, Viewer)
- [ ] PII detection & redaction (emails, phones, SSNs)
- [ ] Encryption at rest (Firestore, OAuth tokens)
- [ ] Encryption in transit (HTTPS/TLS)
- [ ] Rate limiting (slowapi)
- [ ] Input sanitization (prevent prompt injection, XSS, SQL injection)
- [ ] Audit logging (dark data access, forecasts, conversations)
- [ ] GDPR compliance (right-to-delete, data minimization)

---

## Quick Reference: Deployment Commands

**Set up secrets**:
```bash
gcloud secrets create OAUTH_ENCRYPTION_KEY --data-file=- < encryption_key.txt
gcloud secrets create GMAIL_CLIENT_ID --data-file=- < gmail_client_id.txt
gcloud secrets create GMAIL_CLIENT_SECRET --data-file=- < gmail_client_secret.txt
```

**Deploy backend**:
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --set-env-vars "TAVILY_API_KEY=${TAVILY_API_KEY}" \
  --set-secrets "OAUTH_ENCRYPTION_KEY=OAUTH_ENCRYPTION_KEY:latest"
```

**Deploy frontend**:
```bash
cd frontend
npm run build
npm run deploy  # or gcloud app deploy
```

**Backfill data**:
```bash
python scripts/backfill_rag_documents.py
python scripts/migrate_monitor_snapshots.py
```

**Canary deployment**:
```bash
# 10% traffic
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-phase1=10,consultantos-current=90

# Monitor for 1 hour, then 50%
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-phase1=50,consultantos-current=50

# Monitor for 1 hour, then 100%
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-phase1=100
```

---

## Success Criteria

**Conversational AI**:
- [ ] Response time <5s (p95) ✅
- [ ] Cache hit rate >60% ✅
- [ ] User satisfaction >4/5 ✅
- [ ] Conversation length >3 turns avg ✅

**Predictive Analytics**:
- [ ] Forecast accuracy MAE <15% (3-month) ✅
- [ ] Forecast generation <10s (p95) ✅
- [ ] User adoption >50% of monitors ✅

**Dark Data Mining**:
- [ ] Documents processed >10,000/hour ✅
- [ ] PII detection accuracy >95% ✅
- [ ] Insight generation >100/hour ✅
- [ ] Zero PII leaks (GDPR compliance) ✅

---

## Common Issues & Solutions

**Issue**: RAG retrieval slow (>2s)
- **Solution**: Pre-generate embeddings, use vector DB (Pinecone/Weaviate), increase cache TTL

**Issue**: Forecast accuracy low (<70%)
- **Solution**: Retrain models weekly, use ensemble (Prophet + ARIMA + ETS), increase historical data window

**Issue**: PII not detected
- **Solution**: Update regex patterns, use ML-based PII detection (spaCy NER), manual review samples

**Issue**: OAuth tokens expired
- **Solution**: Implement automatic token refresh, notify users when re-auth needed

**Issue**: Extraction jobs timeout
- **Solution**: Increase timeout, batch processing (50 docs at a time), parallel extraction

**Issue**: High LLM costs
- **Solution**: Increase cache hit rate, use Gemini Flash instead of Pro, reduce context window

---

## Next Steps After Phase 1

**Phase 2 Skills** (Future):
- Multi-modal intelligence (images, PDFs, presentations)
- Automated insight generation
- Competitive benchmarking
- AI-powered report writing

**Phase 3 Enhancements**:
- Voice-based intelligence (speech-to-text)
- Real-time collaboration
- Advanced visualizations
- Mobile app

---

**For complete architecture details, see `PHASE1_ARCHITECTURE.md` (3,565 lines)**
