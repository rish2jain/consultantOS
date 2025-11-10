"""
Tests for dashboard builder
"""
import pytest
from datetime import datetime

from consultantos.analytics.dashboard_builder import DashboardBuilder, DashboardBuilderError
from consultantos.models.analytics import (
    Dashboard,
    DashboardElement,
    DashboardPosition,
    DashboardLayout,
)


@pytest.fixture
def builder():
    """Create dashboard builder fixture"""
    return DashboardBuilder()


@pytest.fixture
def sample_element():
    """Create sample dashboard element"""
    return DashboardElement(
        element_id="elem-1",
        type="chart",
        chart_id="chart-1",
        position=DashboardPosition(x=0, y=0, width=6, height=4),
    )


class TestDashboardCreation:
    """Test dashboard creation"""

    @pytest.mark.asyncio
    async def test_create_empty_dashboard(self, builder):
        """Test creating empty dashboard"""
        dashboard = await builder.create_dashboard(
            name="Test Dashboard",
            description="A test dashboard",
        )

        assert dashboard.name == "Test Dashboard"
        assert dashboard.description == "A test dashboard"
        assert len(dashboard.elements) == 0
        assert dashboard.layout == DashboardLayout.GRID

    @pytest.mark.asyncio
    async def test_create_dashboard_with_elements(self, builder, sample_element):
        """Test creating dashboard with elements"""
        dashboard = await builder.create_dashboard(
            name="Test Dashboard",
            elements=[sample_element],
        )

        assert len(dashboard.elements) == 1
        assert dashboard.elements[0].chart_id == "chart-1"

    @pytest.mark.asyncio
    async def test_create_dashboard_with_tags(self, builder):
        """Test creating dashboard with tags"""
        tags = ["finance", "metrics"]
        dashboard = await builder.create_dashboard(
            name="Test Dashboard",
            tags=tags,
        )

        assert dashboard.tags == tags

    @pytest.mark.asyncio
    async def test_dashboard_refresh_interval(self, builder):
        """Test dashboard refresh interval"""
        dashboard = await builder.create_dashboard(
            name="Test Dashboard",
            refresh_interval=600,
        )

        assert dashboard.refresh_interval == 600


class TestElementManagement:
    """Test element management"""

    @pytest.mark.asyncio
    async def test_add_element(self, builder, sample_element):
        """Test adding element"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")

        updated = await builder.add_element(dashboard, sample_element)

        assert len(updated.elements) == 1
        assert updated.elements[0].element_id == "elem-1"
        assert "chart-1" in updated.charts

    @pytest.mark.asyncio
    async def test_add_multiple_elements(self, builder):
        """Test adding multiple elements"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")

        elem1 = DashboardElement(
            element_id="elem-1",
            type="chart",
            chart_id="chart-1",
            position=DashboardPosition(x=0, y=0, width=6, height=4),
        )
        elem2 = DashboardElement(
            element_id="elem-2",
            type="kpi",
            kpi_id="kpi-1",
            position=DashboardPosition(x=6, y=0, width=6, height=4),
        )

        dashboard = await builder.add_element(dashboard, elem1)
        dashboard = await builder.add_element(dashboard, elem2)

        assert len(dashboard.elements) == 2
        assert "chart-1" in dashboard.charts
        assert "kpi-1" in dashboard.kpis

    @pytest.mark.asyncio
    async def test_remove_element(self, builder, sample_element):
        """Test removing element"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")
        dashboard = await builder.add_element(dashboard, sample_element)

        updated = await builder.remove_element(dashboard, "elem-1")

        assert len(updated.elements) == 0

    @pytest.mark.asyncio
    async def test_update_element_position(self, builder, sample_element):
        """Test updating element position"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")
        dashboard = await builder.add_element(dashboard, sample_element)

        new_position = DashboardPosition(x=6, y=4, width=6, height=4)
        updated = await builder.update_element_position(
            dashboard,
            "elem-1",
            new_position,
        )

        assert updated.elements[0].position.x == 6
        assert updated.elements[0].position.y == 4

    @pytest.mark.asyncio
    async def test_reorder_elements(self, builder):
        """Test reordering elements"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")

        elem1 = DashboardElement(
            element_id="elem-1",
            position=DashboardPosition(x=0, y=0, width=6, height=4),
            order=0,
        )
        elem2 = DashboardElement(
            element_id="elem-2",
            position=DashboardPosition(x=6, y=0, width=6, height=4),
            order=1,
        )

        dashboard = await builder.add_element(dashboard, elem1)
        dashboard = await builder.add_element(dashboard, elem2)

        # Reorder
        updated = await builder.reorder_elements(dashboard, ["elem-2", "elem-1"])

        assert updated.elements[0].element_id == "elem-2"
        assert updated.elements[1].element_id == "elem-1"


class TestTemplates:
    """Test template functionality"""

    @pytest.mark.asyncio
    async def test_get_executive_template(self, builder):
        """Test getting executive template"""
        template = await builder.get_template("executive")

        assert template.name == "Executive Dashboard"
        assert template.category == "executive"
        assert template.dashboard.is_template is True

    @pytest.mark.asyncio
    async def test_get_sales_template(self, builder):
        """Test getting sales template"""
        template = await builder.get_template("sales")

        assert template.name == "Sales Dashboard"
        assert template.category == "sales"

    @pytest.mark.asyncio
    async def test_get_finance_template(self, builder):
        """Test getting finance template"""
        template = await builder.get_template("finance")

        assert template.name == "Finance Dashboard"
        assert template.category == "finance"

    @pytest.mark.asyncio
    async def test_get_marketing_template(self, builder):
        """Test getting marketing template"""
        template = await builder.get_template("marketing")

        assert template.name == "Marketing Dashboard"
        assert template.category == "marketing"

    @pytest.mark.asyncio
    async def test_get_operations_template(self, builder):
        """Test getting operations template"""
        template = await builder.get_template("operations")

        assert template.name == "Operations Dashboard"
        assert template.category == "operations"

    @pytest.mark.asyncio
    async def test_get_nonexistent_template(self, builder):
        """Test getting non-existent template"""
        with pytest.raises(DashboardBuilderError):
            await builder.get_template("nonexistent")

    @pytest.mark.asyncio
    async def test_create_from_template(self, builder):
        """Test creating dashboard from template"""
        dashboard = await builder.create_from_template(
            template_name="executive",
            name="My Executive Dashboard",
        )

        assert dashboard.name == "My Executive Dashboard"
        assert dashboard.is_template is False


class TestLayoutValidation:
    """Test layout validation"""

    @pytest.mark.asyncio
    async def test_validate_non_overlapping_layout(self, builder):
        """Test validation of non-overlapping layout"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")

        elem1 = DashboardElement(
            element_id="elem-1",
            position=DashboardPosition(x=0, y=0, width=6, height=4),
        )
        elem2 = DashboardElement(
            element_id="elem-2",
            position=DashboardPosition(x=6, y=0, width=6, height=4),
        )

        dashboard = await builder.add_element(dashboard, elem1)
        dashboard = await builder.add_element(dashboard, elem2)

        is_valid = builder.validate_layout(dashboard)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_overlapping_layout(self, builder):
        """Test validation of overlapping layout"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")

        elem1 = DashboardElement(
            element_id="elem-1",
            position=DashboardPosition(x=0, y=0, width=6, height=4),
        )
        elem2 = DashboardElement(
            element_id="elem-2",
            position=DashboardPosition(x=3, y=2, width=6, height=4),
        )

        dashboard = await builder.add_element(dashboard, elem1)
        dashboard = await builder.add_element(dashboard, elem2)

        is_valid = builder.validate_layout(dashboard)
        assert is_valid is False


class TestSerialization:
    """Test serialization and deserialization"""

    @pytest.mark.asyncio
    async def test_export_to_json(self, builder):
        """Test exporting dashboard to JSON"""
        dashboard = await builder.create_dashboard(
            name="Test Dashboard",
            description="Test",
        )

        json_str = await builder.export_as_json(dashboard)

        assert "Test Dashboard" in json_str
        assert isinstance(json_str, str)

    @pytest.mark.asyncio
    async def test_import_from_json(self, builder):
        """Test importing dashboard from JSON"""
        dashboard = await builder.create_dashboard(
            name="Test Dashboard",
            description="Test",
        )

        json_str = await builder.export_as_json(dashboard)
        imported = await builder.import_from_json(json_str)

        assert imported.name == "Test Dashboard"
        assert imported.description == "Test"


class TestDashboardUpdate:
    """Test dashboard updates"""

    @pytest.mark.asyncio
    async def test_updated_at_changes(self, builder):
        """Test that updated_at timestamp changes"""
        dashboard = await builder.create_dashboard(name="Test Dashboard")
        original_updated = dashboard.updated_at

        # Add element
        elem = DashboardElement(
            element_id="elem-1",
            position=DashboardPosition(x=0, y=0, width=6, height=4),
        )
        updated = await builder.add_element(dashboard, elem)

        assert updated.updated_at >= original_updated
