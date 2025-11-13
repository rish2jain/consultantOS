"""Persistent storage for live dashboards."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from pathlib import Path
from typing import Dict, List, Optional

from consultantos.config import settings
from consultantos.dashboards.models import LiveDashboard
from consultantos.database import get_db_client

try:
    from google.cloud.firestore_v1 import FieldFilter
except Exception:  # pragma: no cover - optional dependency
    FieldFilter = None


logger = logging.getLogger(__name__)


class DashboardRepository:
    """Repository that persists dashboards to Firestore with disk fallback."""

    def __init__(self, storage_dir: Optional[str] = None) -> None:
        self._firestore_collection = None
        try:
            client = get_db_client()
            if client is not None:
                self._firestore_collection = client.collection("dashboards")
                logger.info("DashboardRepository using Firestore backend")
        except Exception as exc:
            logger.warning("Firestore unavailable for dashboards: %s", exc)
            self._firestore_collection = None

        base_dir = storage_dir or settings.cache_dir or os.path.join("/tmp", "consultantos")
        self._dir = Path(base_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / "dashboards.json"
        self._lock = threading.RLock()
        self._dashboards: Dict[str, Dict] = {}
        self._load_from_disk()

    # ------------------------------------------------------------------
    # Public async API
    # ------------------------------------------------------------------
    async def save_dashboard(self, dashboard: LiveDashboard) -> None:
        await asyncio.to_thread(self._save_dashboard_sync, dashboard)

    async def get_dashboard(self, dashboard_id: str) -> Optional[LiveDashboard]:
        return await asyncio.to_thread(self._get_dashboard_sync, dashboard_id)

    async def delete_dashboard(self, dashboard_id: str) -> None:
        await asyncio.to_thread(self._delete_dashboard_sync, dashboard_id)

    async def list_dashboards_for_user(self, user_id: str) -> List[LiveDashboard]:
        return await asyncio.to_thread(self._list_dashboards_for_user_sync, user_id)

    # ------------------------------------------------------------------
    # Internal sync helpers (run in thread pool)
    # ------------------------------------------------------------------
    def _save_dashboard_sync(self, dashboard: LiveDashboard) -> None:
        serialized = dashboard.model_dump(mode="json")

        if self._firestore_collection is not None:
            try:
                self._firestore_collection.document(dashboard.id).set(serialized)
            except Exception as exc:
                logger.warning("Failed to persist dashboard to Firestore: %s", exc)

        with self._lock:
            self._dashboards[dashboard.id] = serialized
            self._write_locked()

    def _get_dashboard_sync(self, dashboard_id: str) -> Optional[LiveDashboard]:
        if self._firestore_collection is not None:
            try:
                doc = self._firestore_collection.document(dashboard_id).get()
                if doc.exists:
                    return LiveDashboard.model_validate(doc.to_dict())
            except Exception as exc:
                logger.warning("Failed to load dashboard from Firestore: %s", exc)

        with self._lock:
            payload = self._dashboards.get(dashboard_id)
            if not payload:
                return None
            return LiveDashboard.model_validate(payload)

    def _delete_dashboard_sync(self, dashboard_id: str) -> None:
        if self._firestore_collection is not None:
            try:
                self._firestore_collection.document(dashboard_id).delete()
            except Exception as exc:
                logger.warning("Failed to delete dashboard from Firestore: %s", exc)

        with self._lock:
            if dashboard_id in self._dashboards:
                self._dashboards.pop(dashboard_id)
                self._write_locked()

    def _list_dashboards_for_user_sync(self, user_id: str) -> List[LiveDashboard]:
        if self._firestore_collection is not None:
            try:
                query = self._firestore_collection
                if user_id:
                    if FieldFilter is not None:
                        query = query.where(filter=FieldFilter("user_id", "==", user_id))
                    else:
                        query = query.where("user_id", "==", user_id)
                docs = list(query.stream())
                dashboards = [
                    LiveDashboard.model_validate(doc.to_dict())
                    for doc in docs if doc.exists
                ]
                dashboards.sort(key=lambda d: d.last_updated, reverse=True)
                return dashboards
            except Exception as exc:
                logger.warning("Failed to list dashboards from Firestore: %s", exc)

        with self._lock:
            dashboards = [
                LiveDashboard.model_validate(payload)
                for payload in self._dashboards.values()
                if payload.get("user_id") == user_id
            ]
        dashboards.sort(key=lambda d: d.last_updated, reverse=True)
        return dashboards

    def _load_from_disk(self) -> None:
        if not self._file.exists():
            return
        try:
            with self._file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    self._dashboards = data
        except (OSError, json.JSONDecodeError) as e:
            # Corrupt cache – start fresh
            logger.warning(
                "Cache corruption detected, resetting dashboards cache",
                extra={"cache_file": str(self._file), "error": str(e)},
                exc_info=True
            )
            self._dashboards = {}

    def _write_locked(self) -> None:
        tmp_path = self._file.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(self._dashboards, handle)
        tmp_path.replace(self._file)


__all__ = ["DashboardRepository"]
