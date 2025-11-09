"""Task handler service: orchestrates analysis + report generation."""

import asyncio
import base64
import logging
import os
from typing import Optional

import httpx
import google.auth.transport.requests
import google.oauth2.id_token
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from pydantic import BaseModel

from consultantos_core import models as core_models, storage as core_storage, database as core_db
from consultantos.orchestrator import AnalysisOrchestrator
from consultantos.reports import generate_pdf_report

app = FastAPI(title="ConsultantOS Task Handler", version="0.1.0")
logger = logging.getLogger(__name__)
_orchestrator = AnalysisOrchestrator()

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL")
REPORTING_SERVICE_URL = os.getenv("REPORTING_SERVICE_URL")
SERVICE_AUDIENCE = os.getenv("SERVICE_AUTH_AUDIENCE")
EXPECTED_AUDIENCE = os.getenv("TASK_HANDLER_SERVICE_AUDIENCE", SERVICE_AUDIENCE)

_auth_request = google.auth.transport.requests.Request()


class AnalysisTask(BaseModel):
    job_id: str
    analysis_request: core_models.AnalysisRequest
    user_id: Optional[str] = None


async def _get_id_token(audience: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, google.oauth2.id_token.fetch_id_token, _auth_request, audience
    )


async def _post_json(url: str, payload: dict, params: dict | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if SERVICE_AUDIENCE:
        token = await _get_id_token(SERVICE_AUDIENCE or url)
        headers["Authorization"] = f"Bearer {token}"

    timeout = httpx.Timeout(120.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(url, json=payload, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.exception(f"HTTP error calling {url}")
            raise HTTPException(
                status_code=502,
                detail=f"Service call failed: {str(exc)}"
            ) from exc


async def _execute_via_agent_service(request_model: core_models.AnalysisRequest) -> core_models.StrategicReport:
    if not AGENT_SERVICE_URL:
        return await _orchestrator.execute(request_model)

    data = await _post_json(
        AGENT_SERVICE_URL.rstrip("/") + "/execute",
        request_model.model_dump(),
    )
    return core_models.StrategicReport.model_validate(data)


async def _generate_pdf_via_reporting_service(report: core_models.StrategicReport, report_id: str) -> bytes:
    if not REPORTING_SERVICE_URL:
        # Run synchronous PDF generation in executor to avoid blocking event loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, generate_pdf_report, report, report_id
        )

    data = await _post_json(
        REPORTING_SERVICE_URL.rstrip("/") + "/reports/pdf/base64",
        report.model_dump(),
        params={"report_id": report_id},
    )
    return base64.b64decode(data["pdf_base64"])


async def _verify_cloud_tasks_token(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> None:
    """Verify Cloud Tasks OIDC Bearer token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    try:
        # Verify the token with Google's OAuth2 ID token verifier
        idinfo = google.oauth2.id_token.verify_token(
            token, _auth_request, audience=EXPECTED_AUDIENCE
        )
        
        # Verify issuer is Google
        if idinfo.get("iss") not in ["https://accounts.google.com", "accounts.google.com"]:
            raise HTTPException(status_code=401, detail="Invalid token issuer")
        
        logger.debug(f"Verified Cloud Tasks token for issuer: {idinfo.get('iss')}")
    except ValueError as exc:
        logger.warning(f"Token verification failed: {exc}")
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


@app.post("/tasks/process")
async def process_task(
    request: Request,
    _: None = Depends(_verify_cloud_tasks_token)
):
    """Process an async analysis task with authentication, timeouts, and error handling."""

    try:
        payload = AnalysisTask.model_validate(await request.json())
    except Exception as exc:  # pragma: no cover - validation errors
        logger.warning(f"Invalid task payload: {exc}")
        raise HTTPException(status_code=400, detail="Invalid task payload") from exc

    report_id = payload.job_id
    
    try:
        # 1. Execute analysis via agent service (with timeout and error handling)
        try:
            report = await _execute_via_agent_service(payload.analysis_request)
        except httpx.HTTPError as exc:
            logger.exception(f"Agent service call failed for job {report_id}")
            raise HTTPException(
                status_code=502,
                detail="Analysis service unavailable"
            ) from exc
        except Exception as exc:
            logger.exception(f"Analysis execution failed for job {report_id}")
            raise HTTPException(
                status_code=500,
                detail="Analysis execution failed"
            ) from exc

        # 2. Generate PDF via reporting service (with timeout and error handling)
        try:
            pdf_bytes = await _generate_pdf_via_reporting_service(report, report_id)
        except httpx.HTTPError as exc:
            logger.exception(f"Reporting service call failed for job {report_id}")
            raise HTTPException(
                status_code=502,
                detail="Report generation service unavailable"
            ) from exc
        except Exception as exc:
            logger.exception(f"PDF generation failed for job {report_id}")
            raise HTTPException(
                status_code=500,
                detail="PDF generation failed"
            ) from exc

        # 3. Upload PDF to GCS
        try:
            storage = core_storage.get_storage_service()
            pdf_url = storage.upload_pdf(report_id, pdf_bytes)
        except Exception as exc:
            logger.exception(f"GCS upload failed for job {report_id}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload PDF"
            ) from exc

        # 4. Update database
        try:
            db = core_db.get_db_service()
            metadata = core_db.ReportMetadata(
                report_id=report_id,
                company=payload.analysis_request.company,
                industry=payload.analysis_request.industry,
                frameworks=payload.analysis_request.frameworks,
                status="completed",
                confidence_score=report.executive_summary.confidence_score,
                user_id=payload.user_id,
            )
            db.create_report_metadata(metadata)
        except Exception as exc:
            logger.exception(f"Database update failed for job {report_id}")
            # Don't fail the entire request if DB update fails, but log it
            # PDF is already uploaded, so we can still return success
            logger.warning(f"Job {report_id} completed but database update failed")

        return {"status": "success", "report_id": report_id, "report_url": pdf_url}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as exc:  # pragma: no cover
        logger.exception(f"Unexpected error processing task {report_id}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from exc
