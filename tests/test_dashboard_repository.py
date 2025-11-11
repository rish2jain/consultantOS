import asyncio
from datetime import datetime

import pytest

from consultantos.dashboards.models import LiveDashboard
from consultantos.dashboards.repository import DashboardRepository


@pytest.mark.asyncio
async def test_dashboard_repository_roundtrip(tmp_path):
    repo = DashboardRepository(storage_dir=tmp_path.as_posix())

    dashboard = LiveDashboard(
        id="dash_test",
        company="TestCo",
        industry="Technology",
        template="executive_summary",
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        user_id="user-123",
        sections=[],
        alerts=[],
        metrics=[],
        metadata={"frameworks": ["swot"]},
    )

    await repo.save_dashboard(dashboard)

    loaded = await repo.get_dashboard("dash_test")
    assert loaded is not None
    assert loaded.company == "TestCo"

    user_dashboards = await repo.list_dashboards_for_user("user-123")
    assert len(user_dashboards) == 1
    assert user_dashboards[0].id == "dash_test"

    await repo.delete_dashboard("dash_test")
    assert await repo.get_dashboard("dash_test") is None
