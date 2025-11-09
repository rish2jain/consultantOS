"""Reporting service that turns StrategicReport payloads into PDFs."""

import asyncio
import base64
import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response

from consultantos_core import models as core_models
from consultantos.reports import generate_pdf_report

app = FastAPI(title="ConsultantOS Reporting Service", version="0.1.0")
logger = logging.getLogger(__name__)


@app.post("/reports/pdf", response_model=None)
async def create_pdf(report: core_models.StrategicReport, report_id: str | None = None):
    """Generate PDF report asynchronously to avoid blocking the event loop."""
    try:
        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(
            None, generate_pdf_report, report, report_id
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=report.pdf"},
        )
    except ValueError as exc:
        logger.exception("PDF generation validation error")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF generation failed")
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from exc


@app.post("/reports/pdf/base64")
async def create_pdf_base64(report: core_models.StrategicReport, report_id: str | None = None):
    """Generate PDF report as base64-encoded string asynchronously."""
    try:
        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(
            None, generate_pdf_report, report, report_id
        )
        encoded = base64.b64encode(pdf_bytes).decode("utf-8")
        return {"pdf_base64": encoded}
    except ValueError as exc:
        logger.exception("PDF generation validation error")
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)}
        )
    except Exception as exc:
        logger.exception("PDF generation failed")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate PDF"}
        )
