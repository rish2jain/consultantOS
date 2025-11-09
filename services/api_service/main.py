"""API gateway service for ConsultantOS."""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from consultantos.api.main import app as legacy_app
from consultantos_core import models as core_models

app = legacy_app

logger = logging.getLogger(__name__)

_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
_TASKS_LOCATION = os.getenv("CLOUD_TASKS_LOCATION", "us-central1")
_TASKS_QUEUE = os.getenv("CLOUD_TASKS_QUEUE", "analysis-tasks")
_TASK_HANDLER_URL = os.getenv("TASK_HANDLER_SERVICE_URL")
_TASK_HANDLER_AUDIENCE = os.getenv("TASK_HANDLER_SERVICE_AUDIENCE", _TASK_HANDLER_URL)
_TASK_HANDLER_SA = os.getenv("TASK_HANDLER_SERVICE_ACCOUNT")

_tasks_client: Optional[tasks_v2.CloudTasksClient] = None


def _get_tasks_client() -> tasks_v2.CloudTasksClient:
    global _tasks_client
    if _tasks_client is None:
        _tasks_client = tasks_v2.CloudTasksClient()
    return _tasks_client


def _validate_task_config():
    missing = [
        name
        for name, value in {
            "GCP_PROJECT_ID": _PROJECT_ID,
            "TASK_HANDLER_SERVICE_URL": _TASK_HANDLER_URL,
            "TASK_HANDLER_SERVICE_ACCOUNT": _TASK_HANDLER_SA,
        }.items()
        if not value
    ]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing Cloud Tasks configuration: {', '.join(missing)}",
        )


@app.post("/analyze/async-task")
async def enqueue_analysis_task(analysis_request: core_models.AnalysisRequest):
    """Enqueue an analysis request for asynchronous processing via Cloud Tasks."""

    _validate_task_config()
    
    try:
        client = _get_tasks_client()
        parent = client.queue_path(_PROJECT_ID, _TASKS_LOCATION, _TASKS_QUEUE)
    except Exception as exc:
        logger.exception("Failed to construct Cloud Tasks parent path")
        raise HTTPException(
            status_code=503,
            detail="Failed to enqueue task"
        ) from exc

    job_id = uuid.uuid4().hex
    payload = {
        "job_id": job_id,
        "analysis_request": analysis_request.model_dump(),
        "enqueued_at": datetime.now(timezone.utc).isoformat(),
    }

    body = json.dumps(payload).encode("utf-8")
    http_request = tasks_v2.HttpRequest(
        http_method=tasks_v2.HttpMethod.POST,
        url=_TASK_HANDLER_URL.rstrip("/") + "/tasks/process",
        headers={"Content-Type": "application/json"},
        body=body,
    )

    http_request.oidc_token.service_account_email = _TASK_HANDLER_SA
    if _TASK_HANDLER_AUDIENCE:
        http_request.oidc_token.audience = _TASK_HANDLER_AUDIENCE

    task = tasks_v2.Task(
        http_request=http_request,
        schedule_time=timestamp_pb2.Timestamp(seconds=int(datetime.now(timezone.utc).timestamp())),
    )

    try:
        response = client.create_task(parent=parent, task=task)
        return {"job_id": job_id, "task_name": response.name}
    except Exception as exc:
        logger.exception("Failed to create Cloud Task")
        raise HTTPException(
            status_code=503,
            detail="Failed to enqueue task"
        ) from exc


__all__ = ["app"]
