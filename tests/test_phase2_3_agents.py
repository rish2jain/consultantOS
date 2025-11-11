"""
Unit tests for Phase 2 & 3 dashboard agents
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from consultantos.agents import (
    NotificationAgent,
    VersionControlAgent,
    TemplateAgent,
    VisualizationAgent,
    AlertFeedbackAgent,
)


# ============================================================================
# NOTIFICATION AGENT TESTS
# ============================================================================

class TestNotificationAgent:
    """Tests for NotificationAgent"""

    @pytest.mark.asyncio
    async def test_notification_agent_list(self):
        """Test notification agent list action"""
        agent = NotificationAgent()

        mock_notification = {
            "id": "notif_1",
            "type": "alert",
            "title": "Test Notification",
            "description": "Test description",
            "read": False,
            "created_at": datetime.now().isoformat(),
            "link": None
        }

        mock_db = Mock()
        mock_db.db = Mock()
        mock_collection = Mock()
        mock_query = Mock()
        mock_query.stream.return_value = [Mock(id="notif_1", to_dict=lambda: {
            "type": "alert",
            "title": "Test Notification",
            "summary": "Test description",
            "read": False,
            "created_at": datetime.now(),
            "link": None
        })]
        mock_collection.order_by.return_value = mock_query
        mock_db.db.collection.return_value = mock_collection

        with patch('consultantos.agents.notification_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action_type": "list",
                "user_id": "test_user",
                "limit": 50,
                "unread_only": False
            })

            assert result["success"] is True
            assert "data" in result
            assert result["data"]["count"] >= 0

    @pytest.mark.asyncio
    async def test_notification_agent_settings(self):
        """Test notification agent settings action"""
        agent = NotificationAgent()

        mock_db = Mock()
        mock_db.db = Mock()
        mock_user_ref = Mock()
        mock_db.db.collection.return_value.document.return_value = mock_user_ref

        with patch('consultantos.agents.notification_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action_type": "settings",
                "user_id": "test_user",
                "in_app_enabled": True,
                "email_enabled": False,
                "email_frequency": "daily"
            })

            assert result["success"] is True
            assert "data" in result
            assert result["data"]["settings"] is not None


# ============================================================================
# VERSION CONTROL AGENT TESTS
# ============================================================================

class TestVersionControlAgent:
    """Tests for VersionControlAgent"""

    @pytest.mark.asyncio
    async def test_version_control_agent_list(self):
        """Test version control agent list action"""
        agent = VersionControlAgent()

        result = await agent.execute({
            "action_type": "list",
            "report_id": "report_1"
        })

        assert result["success"] is True
        assert "data" in result
        assert "version_history" in result["data"]

    @pytest.mark.asyncio
    async def test_version_control_agent_create(self):
        """Test version control agent create action"""
        agent = VersionControlAgent()

        mock_db = Mock()
        mock_db.get_report_metadata.return_value = {
            "company": "Tesla",
            "industry": "EV",
            "frameworks": ["porter"],
            "executive_summary": {},
            "confidence_score": 0.85
        }

        with patch('consultantos.agents.version_control_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action_type": "create",
                "report_id": "report_1",
                "user_id": "test_user",
                "change_summary": "Test version"
            })

            assert result["success"] is True
            assert "data" in result
            assert len(result["data"]["versions"]) == 1

    @pytest.mark.asyncio
    async def test_version_control_agent_compare(self):
        """Test version control agent compare action"""
        agent = VersionControlAgent()

        # First create two versions
        mock_db = Mock()
        mock_db.get_report_metadata.return_value = {
            "company": "Tesla",
            "industry": "EV",
            "frameworks": ["porter"],
            "executive_summary": {},
            "confidence_score": 0.85
        }

        with patch('consultantos.agents.version_control_agent.get_db_service', return_value=mock_db):
            # Create first version
            result1 = await agent.execute({
                "action_type": "create",
                "report_id": "report_1",
                "user_id": "test_user"
            })
            version1_id = result1["data"]["versions"][0]["version_id"]

            # Create second version
            result2 = await agent.execute({
                "action_type": "create",
                "report_id": "report_1",
                "user_id": "test_user"
            })
            version2_id = result2["data"]["versions"][0]["version_id"]

            # Compare versions
            result = await agent.execute({
                "action_type": "compare",
                "from_version_id": version1_id,
                "to_version_id": version2_id
            })

            assert result["success"] is True
            assert "data" in result


# ============================================================================
# TEMPLATE AGENT TESTS
# ============================================================================

class TestTemplateAgent:
    """Tests for TemplateAgent"""

    @pytest.mark.asyncio
    async def test_template_agent_list(self):
        """Test template agent list action"""
        agent = TemplateAgent()

        result = await agent.execute({
            "action_type": "list",
            "page": 1,
            "page_size": 20
        })

        assert result["success"] is True
        assert "data" in result
        assert "templates" in result["data"]

    @pytest.mark.asyncio
    async def test_template_agent_create(self):
        """Test template agent create action"""
        agent = TemplateAgent()

        result = await agent.execute({
            "action_type": "create",
            "name": "Test Template",
            "category": "porter",
            "framework_type": "porter",
            "prompt_template": "Analyze {company}",
            "structure": {"type": "object"},
            "user_id": "test_user"
        })

        assert result["success"] is True
        assert "data" in result
        assert result["data"]["template"] is not None
        assert result["data"]["template"]["name"] == "Test Template"


# ============================================================================
# VISUALIZATION AGENT TESTS
# ============================================================================

class TestVisualizationAgent:
    """Tests for VisualizationAgent"""

    @pytest.mark.asyncio
    async def test_visualization_agent_create_porter(self):
        """Test visualization agent create Porter chart"""
        agent = VisualizationAgent()

        porter_data = {
            "threat_of_new_entrants": 0.6,
            "bargaining_power_of_suppliers": 0.5,
            "bargaining_power_of_buyers": 0.7,
            "threat_of_substitute_products": 0.4,
            "intensity_of_rivalry": 0.8
        }

        with patch('consultantos.agents.visualization_agent.create_porter_radar_figure') as mock_create:
            mock_figure = Mock()
            mock_figure.to_dict.return_value = {"data": [], "layout": {}}
            mock_create.return_value = mock_figure

            with patch('consultantos.agents.visualization_agent.figure_to_json', return_value={"data": [], "layout": {}}):
                result = await agent.execute({
                    "action_type": "create",
                    "chart_type": "porter",
                    "data": porter_data
                })

                assert result["success"] is True
                assert "data" in result
                assert "figure" in result["data"]

    @pytest.mark.asyncio
    async def test_visualization_agent_create_generic(self):
        """Test visualization agent create generic chart"""
        agent = VisualizationAgent()

        with patch('consultantos.agents.visualization_agent.get_cached_figure', return_value=None):
            result = await agent.execute({
                "action_type": "create",
                "chart_type": "bar",
                "data": {"x": ["A", "B", "C"], "y": [1, 2, 3]}
            })

            assert result["success"] is True
            assert "data" in result


# ============================================================================
# ALERT FEEDBACK AGENT TESTS
# ============================================================================

class TestAlertFeedbackAgent:
    """Tests for AlertFeedbackAgent"""

    @pytest.mark.asyncio
    async def test_alert_feedback_agent_submit(self):
        """Test alert feedback agent submit action"""
        agent = AlertFeedbackAgent()

        mock_alert = Mock()
        mock_alert.monitor_id = "monitor_1"
        mock_alert.user_feedback = None
        mock_alert.action_taken = None

        mock_monitor = Mock()
        mock_monitor.user_id = "test_user"

        mock_db = Mock()
        mock_db.get_alert = AsyncMock(return_value=mock_alert)
        mock_db.get_monitor = AsyncMock(return_value=mock_monitor)
        mock_db.update_alert = AsyncMock()

        with patch('consultantos.agents.alert_feedback_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action_type": "submit",
                "alert_id": "alert_1",
                "user_id": "test_user",
                "feedback": "helpful",
                "action_taken": "Reviewed report"
            })

            assert result["success"] is True
            assert "data" in result
            assert "message" in result["data"]

    @pytest.mark.asyncio
    async def test_alert_feedback_agent_stats(self):
        """Test alert feedback agent stats action"""
        agent = AlertFeedbackAgent()

        mock_monitor = Mock()
        mock_monitor.id = "monitor_1"
        mock_monitor.user_id = "test_user"

        mock_alert = Mock()
        mock_alert.user_feedback = "helpful"
        mock_alert.action_taken = "Reviewed"
        mock_alert.created_at = datetime.now()

        mock_db = Mock()
        mock_db.get_user_monitors = AsyncMock(return_value=[mock_monitor])
        mock_db.get_monitor_alerts = AsyncMock(return_value=[mock_alert])

        with patch('consultantos.agents.alert_feedback_agent.get_db_service', return_value=mock_db):
            result = await agent.execute({
                "action_type": "stats",
                "user_id": "test_user"
            })

            assert result["success"] is True
            assert "data" in result
            assert "stats" in result["data"]
            assert result["data"]["stats"]["total_feedback"] >= 0

