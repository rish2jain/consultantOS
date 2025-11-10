# ConsultantOS Architecture Documentation Index

This directory contains comprehensive architecture documentation for ConsultantOS, a Continuous Competitive Intelligence Platform.

## Documentation Files

### 1. **ARCHITECTURE_SUMMARY.md** ⭐ START HERE
**Executive overview of the entire architecture**
- Project overview and core innovation
- Technology stack at a glance
- Key components overview
- Data flow summary
- Design patterns used
- Performance characteristics
- Deployment model
- Security architecture
- Strengths & weaknesses
- Getting started guide

**Best for**: Quick understanding, executive briefing, onboarding

---

### 2. **ARCHITECTURE.md** 📖 COMPREHENSIVE REFERENCE
**Detailed 15-section architecture analysis**

Sections covered:
1. Agent Orchestration Flow (BaseAgent pattern, 5 agents, orchestrator)
2. Data Flow Patterns (request flow, monitoring flow, Pydantic models)
3. External Integrations (data sources, tools, LLM integration)
4. Monitoring & Intelligence System (components, change detection, alerts)
5. Database & Storage Patterns (Firestore schema, Cloud Storage, caching)
6. API Structure (20+ endpoints, middleware, authentication)
7. Frontend Architecture (tech stack, pages, key components)
8. Key Design Patterns (8 patterns explained with examples)
9. Error Handling & Resilience (graceful degradation, Sentry, validation)
10. Performance & Scalability (concurrency, caching, database optimization)
11. Monitoring & Observability (logging, metrics, tracing)
12. Security Considerations (API keys, data protection, CORS)
13. Deployment Architecture (Cloud Run, frontend, background processing)
14. Data Consistency & Transactions (snapshot lifecycle, deduplication)
15. Extension Points (custom agents, frameworks, channels, metrics)

**Best for**: Deep understanding, system design, troubleshooting, extending

---

### 3. **ARCHITECTURE_DIAGRAMS.md** 📊 VISUAL REFERENCE
**ASCII diagrams and visual flows for all major components**

Diagrams included:
1. System Architecture Overview (full stack diagram)
2. Agent Orchestration Flow (3-phase execution with decisions)
3. Monitoring & Change Detection Flow (background worker pipeline)
4. Data Model Hierarchy (Pydantic model relationships)
5. Cache Strategy (multi-level caching with TTL)
6. Error Recovery & Resilience (error handling state machine)
7. Frontend Component Hierarchy (Next.js component tree)
8. Database Schema (Firestore collections and indexes)
9. Agent State Machine (execution lifecycle)
10. Request/Response Flow (HTTP request journey)

**Best for**: Visual learners, system design discussions, documentation

---

## Quick Navigation

### By Focus Area

**Agent Architecture**
- See ARCHITECTURE_SUMMARY.md → "Agent-Based Intelligence System"
- See ARCHITECTURE.md → Section 1 "Agent Orchestration Flow"
- See ARCHITECTURE_DIAGRAMS.md → "Agent Orchestration Flow" & "Agent State Machine"

**API & Endpoints**
- See ARCHITECTURE.md → Section 6 "API Structure"
- See ARCHITECTURE_DIAGRAMS.md → "System Architecture Overview"

**Monitoring System**
- See ARCHITECTURE.md → Section 4 "Monitoring & Intelligence System"
- See ARCHITECTURE_DIAGRAMS.md → "Monitoring & Change Detection Flow"

**Database & Storage**
- See ARCHITECTURE.md → Section 5 "Database & Storage Patterns"
- See ARCHITECTURE_DIAGRAMS.md → "Database Schema"

**Frontend**
- See ARCHITECTURE.md → Section 7 "Frontend Architecture"
- See ARCHITECTURE_DIAGRAMS.md → "Frontend Component Hierarchy"

**Data Flow**
- See ARCHITECTURE_SUMMARY.md → "Data Flow Summary"
- See ARCHITECTURE_DIAGRAMS.md → "Request/Response Flow"

**Design Patterns**
- See ARCHITECTURE.md → Section 8 "Key Design Patterns"
- See ARCHITECTURE_SUMMARY.md → "Design Patterns Used"

**Error Handling**
- See ARCHITECTURE.md → Section 9 "Error Handling & Resilience"
- See ARCHITECTURE_DIAGRAMS.md → "Error Recovery & Resilience"

**Performance**
- See ARCHITECTURE.md → Section 10 "Performance & Scalability"
- See ARCHITECTURE_SUMMARY.md → "Performance Characteristics"

**Security**
- See ARCHITECTURE.md → Section 12 "Security Considerations"
- See ARCHITECTURE_SUMMARY.md → "Security Architecture"

**Deployment**
- See ARCHITECTURE.md → Section 13 "Deployment Architecture"
- See ARCHITECTURE_SUMMARY.md → "Deployment Model"

---

### By Audience

**Project Manager / Product Owner**
1. Read: ARCHITECTURE_SUMMARY.md
2. Focus: "Core Innovation", "Key Components", "Roadmap"
3. Time: 15-20 minutes

**Software Engineer (New to Project)**
1. Read: ARCHITECTURE_SUMMARY.md (full)
2. Skim: ARCHITECTURE.md sections 1, 2, 6, 7
3. Reference: ARCHITECTURE_DIAGRAMS.md as needed
4. Time: 1-2 hours

**DevOps / Infrastructure**
1. Read: ARCHITECTURE_SUMMARY.md → "Deployment Model"
2. Read: ARCHITECTURE.md → Section 13 "Deployment Architecture"
3. Check: ARCHITECTURE.md → Section 11 "Monitoring & Observability"
4. Time: 30-45 minutes

**Database Engineer**
1. Read: ARCHITECTURE_SUMMARY.md → Performance section
2. Read: ARCHITECTURE.md → Section 5 "Database & Storage Patterns"
3. Reference: ARCHITECTURE_DIAGRAMS.md → "Database Schema"
4. Time: 45 minutes

**Full Stack Developer (Extending Features)**
1. Read: ARCHITECTURE_SUMMARY.md (full)
2. Read: ARCHITECTURE.md → Sections 1, 2, 4, 6, 7, 8, 15
3. Reference: ARCHITECTURE_DIAGRAMS.md as needed
4. Time: 2-3 hours

**Security/Compliance Reviewer**
1. Read: ARCHITECTURE.md → Sections 9 (Error Handling), 12 (Security)
2. Read: ARCHITECTURE_SUMMARY.md → "Security Architecture"
3. Time: 30 minutes

---

## Key Takeaways

### Architecture Strengths

✓ **Scalable Multi-Agent System**: 5 specialized agents orchestrated efficiently  
✓ **Intelligent Caching**: Multi-level (disk + semantic) reduces costs 60-70%  
✓ **Continuous Intelligence**: Real-time monitoring with Prophet-based anomaly detection  
✓ **Error Resilient**: Graceful degradation, circuit breakers, retries  
✓ **Modular Design**: Clear separation of concerns throughout  
✓ **Cloud Native**: GCP-integrated, serverless-ready, auto-scaling  
✓ **Observable**: Sentry integration, Prometheus metrics, structured logging  
✓ **Type Safe**: Pydantic models and validation throughout  

### Areas for Improvement

⚠ Agent timeout coupling (all 60s, should be per-agent)  
⚠ No explicit cache invalidation strategy  
⚠ Only Tavily has circuit breaker (not Gemini)  
⚠ Rate limiting per-IP only (no per-user quotas)  
⚠ No queue depth limits for monitoring  
⚠ No complete event sourcing/audit trail  
⚠ Single region deployment (us-central1 only)  

---

## Code Organization

```
consultantos/
├── agents/
│   ├── base_agent.py           # Abstract base class
│   ├── research_agent.py        # Tavily web search
│   ├── market_agent.py          # Google Trends
│   ├── financial_agent.py       # yfinance/Finnhub/Alpha Vantage
│   ├── framework_agent.py       # Porter/SWOT/PESTEL/Blue Ocean
│   └── synthesis_agent.py       # Executive summary
│
├── orchestrator/
│   └── orchestrator.py          # 3-phase orchestration
│
├── monitoring/
│   ├── intelligence_monitor.py  # Core monitoring
│   ├── anomaly_detector.py      # Prophet-based detection
│   ├── alert_scorer.py          # Priority scoring
│   ├── snapshot_aggregator.py   # Change detection
│   └── timeseries_optimizer.py  # Compression & optimization
│
├── api/
│   ├── main.py                  # FastAPI app setup
│   ├── monitoring_endpoints.py  # /monitors routes
│   ├── template_endpoints.py    # /templates routes
│   ├── auth_endpoints.py        # /auth routes
│   └── ... (15+ more endpoint files)
│
├── models/
│   ├── monitoring.py            # Monitor, Alert, Change models
│   ├── financial_indicators.py  # Financial data models
│   └── ... (other domain models)
│
├── tools/
│   ├── tavily_tool.py          # Web search wrapper
│   ├── financial_tool.py        # Financial data fetcher
│   ├── finnhub_tool.py         # Analyst data
│   ├── nlp_tool.py             # NLP enrichment
│   └── ... (other tool integrations)
│
├── database.py                  # Firestore abstraction
├── cache.py                     # Multi-level caching
├── storage.py                   # Cloud Storage integration
├── config.py                    # Settings management
├── auth.py                      # Authentication
└── prompts.py                   # LLM prompts

frontend/
├── app/
│   ├── page.tsx                # Home page
│   ├── layout.tsx              # Root layout
│   ├── dashboard/
│   │   ├── page.tsx            # Main monitoring dashboard
│   │   └── [id]/page.tsx       # Monitor detail
│   ├── analysis/
│   │   └── page.tsx            # One-off analysis
│   ├── reports/
│   │   ├── page.tsx            # Report history
│   │   └── [id]/page.tsx       # Report viewer
│   ├── components/             # 70+ reusable components
│   ├── hooks/                  # useKeyboardShortcuts, useWebSocket
│   └── api/                    # Client-side API
└── next.config.js
```

---

## External References

**Technologies Used:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js 14 Docs](https://nextjs.org/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Google Firestore Guide](https://cloud.google.com/firestore/docs)
- [Google Gemini API](https://ai.google.dev/)
- [Instructor Python](https://github.com/jxnl/instructor)
- [Sentry Documentation](https://docs.sentry.io/)
- [Prometheus Metrics](https://prometheus.io/docs/)

---

## Common Tasks

### "I want to add a new framework (e.g., Porter's Five Forces)"
See: ARCHITECTURE.md → Section 15 "Extension Points" → "Custom Frameworks"

### "I need to understand how alerts work"
See: ARCHITECTURE.md → Section 4 "Monitoring & Intelligence System"  
See: ARCHITECTURE_DIAGRAMS.md → "Monitoring & Change Detection Flow"

### "How does caching reduce costs?"
See: ARCHITECTURE_SUMMARY.md → "Multi-Level Caching"  
See: ARCHITECTURE_DIAGRAMS.md → "Cache Strategy"

### "What happens when an agent times out?"
See: ARCHITECTURE.md → Section 9 "Error Handling & Resilience"  
See: ARCHITECTURE_DIAGRAMS.md → "Error Recovery & Resilience"

### "How do I deploy this to production?"
See: ARCHITECTURE_SUMMARY.md → "Deployment Model"  
See: ARCHITECTURE.md → Section 13 "Deployment Architecture"

### "What are the security implications?"
See: ARCHITECTURE_SUMMARY.md → "Security Architecture"  
See: ARCHITECTURE.md → Section 12 "Security Considerations"

---

## Document History

| Date | Changes |
|------|---------|
| 2025-11-09 | Initial comprehensive architecture documentation |
| | Created ARCHITECTURE_SUMMARY.md, ARCHITECTURE.md, ARCHITECTURE_DIAGRAMS.md |
| | Analyzed 30+ files across all 7 focus areas |
| | Documented 15 comprehensive sections |
| | Added 10 detailed ASCII diagrams |

---

## Questions?

For clarification on specific components:
1. Check the relevant section in ARCHITECTURE.md
2. Look for visual diagram in ARCHITECTURE_DIAGRAMS.md
3. Reference the code in consultantos/ or frontend/ directories
4. Consult CLAUDE.md for project guidelines

---

**Documentation Generated**: November 9, 2025  
**Analysis Depth**: Very thorough (30+ files examined)  
**Coverage**: All 7 focus areas (agents, API, monitoring, models, tools, database, frontend)

