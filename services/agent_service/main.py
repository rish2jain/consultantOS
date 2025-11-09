"""Agent service exposing orchestrator execution."""

from fastapi import FastAPI, HTTPException

from consultantos_core import models as core_models
from consultantos.orchestrator import AnalysisOrchestrator

app = FastAPI(title="ConsultantOS Agent Service", version="0.1.0")
_orchestrator = AnalysisOrchestrator()


@app.post("/execute", response_model=core_models.StrategicReport)
async def execute_analysis(request: core_models.AnalysisRequest):
    """Run the multi-agent workflow and return the structured report."""

    try:
        report = await _orchestrator.execute(request)
        return report
    except Exception as exc:  # pragma: no cover - surfaced to HTTP
        raise HTTPException(status_code=500, detail=str(exc)) from exc
