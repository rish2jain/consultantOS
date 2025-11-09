# ConsultantOS Services

This directory holds the Cloud Run friendly service boundaries called out in the
hackathon roadmap. Each service currently depends on the legacy monolith but
exposes a clean FastAPI surface so we can peel functionality off incrementally.

| Service | Purpose |
| ------- | ------- |
| `api_service` | Public API gateway + routers. Eventually becomes the thin ingress that validates requests and enqueues Cloud Tasks. |
| `agent_service` | Google ADK-powered orchestration of the specialized agents. For now it wraps the existing `AnalysisOrchestrator`. |
| `reporting_service` | Report/PDF generation endpoints that turn `StrategicReport` payloads into shareable artifacts. |
| `task_handler_service` | Cloud Tasks worker that chains agent execution + report generation. Initially still calls the orchestrator directly, giving us a standalone worker entrypoint. |

Each service has its own `main.py`, `requirements.txt`, and `Dockerfile` so we
can deploy it independently on Cloud Run. The shared logic comes from the new
`consultantos_core` package under `libs/`.
