"""
Report Management Agent - Handles report listing, filtering, and actions
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from consultantos.agents.base_agent import BaseAgent
from consultantos.database import get_db_service
from pydantic import BaseModel, Field
import logging
import asyncio

logger = logging.getLogger(__name__)


class ReportFilter(BaseModel):
    """Report filtering criteria"""
    company: Optional[str] = None
    industry: Optional[str] = None
    frameworks: Optional[List[str]] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = None


class ReportListResult(BaseModel):
    """Report list result"""
    reports: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = Field(default=0)
    filtered: int = Field(default=0)
    page: int = Field(default=1)
    page_size: int = Field(default=50)


class ReportManagementAgent(BaseAgent):
    """Agent for managing reports: listing, filtering, searching, and actions"""
    
    # Maximum number of reports to fetch in a single query
    # Note: For better performance, use DB-level filtering and pagination
    MAX_REPORTS_FETCH = 1000

    def __init__(self, timeout: int = 30):
        super().__init__(
            name="report_management_agent",
            timeout=timeout
        )
        self.instruction = """
        You are a report management specialist.
        Efficiently filter, search, and manage reports with high performance.
        Support complex queries and provide actionable insights.
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage reports: list, filter, search, and perform actions.

        Args:
            input_data: Dictionary containing:
                - user_id: User ID for filtering
                - action: Action to perform ('list', 'filter', 'search', 'delete', 'archive')
                - filters: ReportFilter object (for filter/search actions)
                - report_id: Report ID (for delete/archive actions)
                - page: Page number (default: 1)
                - page_size: Page size (default: 50)

        Returns:
            Result dictionary with reports and metadata
        """
        action = input_data.get("action", "list")
        user_id = input_data.get("user_id")
        page = input_data.get("page", 1)
        page_size = input_data.get("page_size", 50)

        db_service = get_db_service()
        if not db_service:
            raise Exception("Database service unavailable")

        if action == "list":
            return await self._list_reports(db_service, user_id, page, page_size)
        elif action == "filter":
            filters = input_data.get("filters", {})
            return await self._filter_reports(db_service, user_id, filters, page, page_size)
        elif action == "search":
            search_query = input_data.get("search_query", "")
            return await self._search_reports(db_service, user_id, search_query, page, page_size)
        elif action == "delete":
            report_id = input_data.get("report_id")
            return await self._delete_report(db_service, user_id, report_id)
        elif action == "archive":
            report_id = input_data.get("report_id")
            return await self._archive_report(db_service, user_id, report_id)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _list_reports(
        self,
        db_service: Any,
        user_id: Optional[str],
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """List reports with pagination"""
        try:
            all_reports = db_service.list_reports(user_id=user_id, limit=self.MAX_REPORTS_FETCH)
            
            # Paginate
            start = (page - 1) * page_size
            end = start + page_size
            paginated_reports = all_reports[start:end]
            
            result = ReportListResult(
                reports=[self._serialize_report(r) for r in paginated_reports],
                total=len(all_reports),
                filtered=len(paginated_reports),
                page=page,
                page_size=page_size
            )
            
            return {
                "success": True,
                "data": result.model_dump(),
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to list reports: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _filter_reports(
        self,
        db_service: Any,
        user_id: Optional[str],
        filters: Dict[str, Any],
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """Filter reports based on criteria"""
        try:
            all_reports = db_service.list_reports(user_id=user_id, limit=self.MAX_REPORTS_FETCH)
            
            # Apply filters
            filtered = all_reports
            if filters.get("company"):
                filtered = [r for r in filtered if getattr(r, 'company', '').lower() == filters["company"].lower()]
            if filters.get("industry"):
                filtered = [r for r in filtered if getattr(r, 'industry', '').lower() == filters["industry"].lower()]
            if filters.get("frameworks"):
                filtered = [r for r in filtered if any(fw in getattr(r, 'frameworks', []) for fw in filters["frameworks"])]
            if filters.get("status"):
                filtered = [r for r in filtered if getattr(r, 'status', '') == filters["status"]]
            if filters.get("date_from"):
                date_from = filters["date_from"]
                filtered = [
                    r for r in filtered
                    if r.created_at and self._parse_date_safe(r.created_at) and self._parse_date_safe(r.created_at) >= date_from
                ]
            if filters.get("date_to"):
                date_to = filters["date_to"]
                filtered = [
                    r for r in filtered
                    if r.created_at and self._parse_date_safe(r.created_at) and self._parse_date_safe(r.created_at) <= date_to
                ]
            
            # Paginate
            start = (page - 1) * page_size
            end = start + page_size
            paginated = filtered[start:end]
            
            result = ReportListResult(
                reports=[self._serialize_report(r) for r in paginated],
                total=len(all_reports),
                filtered=len(filtered),
                page=page,
                page_size=page_size
            )
            
            return {
                "success": True,
                "data": result.model_dump(),
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to filter reports: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _search_reports(
        self,
        db_service: Any,
        user_id: Optional[str],
        search_query: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """Search reports by keywords"""
        try:
            all_reports = db_service.list_reports(user_id=user_id, limit=self.MAX_REPORTS_FETCH)
            query_lower = search_query.lower()
            
            # Simple keyword search
            filtered = [
                r for r in all_reports
                if query_lower in getattr(r, 'company', '').lower()
                or query_lower in getattr(r, 'industry', '').lower()
                or any(query_lower in fw.lower() for fw in getattr(r, 'frameworks', []))
            ]
            
            # Paginate
            start = (page - 1) * page_size
            end = start + page_size
            paginated = filtered[start:end]
            
            result = ReportListResult(
                reports=[self._serialize_report(r) for r in paginated],
                total=len(all_reports),
                filtered=len(filtered),
                page=page,
                page_size=page_size
            )
            
            return {
                "success": True,
                "data": result.model_dump(),
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to search reports: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _delete_report(
        self,
        db_service: Any,
        user_id: Optional[str],
        report_id: str
    ) -> Dict[str, Any]:
        """Delete a report"""
        try:
            # Verify ownership - require non-None user_id
            if not user_id:
                return {
                    "success": False,
                    "data": None,
                    "error": "Authentication required"
                }
            
            report = db_service.get_report_metadata(report_id)
            if not report:
                return {
                    "success": False,
                    "data": None,
                    "error": "Report not found"
                }
            
            report_user_id = getattr(report, 'user_id', None)
            if report_user_id != user_id:
                logger.warning(f"Access denied: user {user_id} attempted to delete report {report_id} owned by {report_user_id}")
                return {
                    "success": False,
                    "data": None,
                    "error": "Access denied"
                }
            
            # Delete report
            if hasattr(db_service, 'delete_report_metadata'):
                success = db_service.delete_report_metadata(report_id)
            elif hasattr(db_service, 'delete_report'):
                success = await db_service.delete_report(report_id) if asyncio.iscoroutinefunction(db_service.delete_report) else db_service.delete_report(report_id)
            else:
                logger.error(f"db_service does not support report deletion")
                return {
                    "success": False,
                    "data": None,
                    "error": "Report deletion not supported by database service"
                }
            
            if not success:
                logger.error(f"Failed to delete report {report_id}")
                return {
                    "success": False,
                    "data": None,
                    "error": "Failed to delete report"
                }
            
            logger.info(f"Successfully deleted report {report_id} for user {user_id}")
            return {
                "success": True,
                "data": {"report_id": report_id, "deleted": True},
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to delete report: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _parse_date_safe(self, date_str: Optional[str]) -> Optional[datetime]:
        """Safely parse ISO format date string, returning None on error"""
        if not date_str:
            return None
        try:
            # Handle both 'Z' and '+00:00' timezone formats
            normalized = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(normalized)
        except (ValueError, TypeError, AttributeError) as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
            return None

    async def _archive_report(
        self,
        db_service: Any,
        user_id: Optional[str],
        report_id: str
    ) -> Dict[str, Any]:
        """Archive a report"""
        try:
            # Verify ownership - require non-None user_id
            if not user_id:
                return {
                    "success": False,
                    "data": None,
                    "error": "Authentication required"
                }
            
            report = db_service.get_report_metadata(report_id)
            if not report:
                return {
                    "success": False,
                    "data": None,
                    "error": "Report not found"
                }
            
            report_user_id = getattr(report, 'user_id', None)
            if report_user_id != user_id:
                logger.warning(f"Access denied: user {user_id} attempted to archive report {report_id} owned by {report_user_id}")
                return {
                    "success": False,
                    "data": None,
                    "error": "Access denied"
                }
            
            # Update status to archived
            success = db_service.update_report_metadata(report_id, {"status": "archived"})
            if not success:
                return {
                    "success": False,
                    "data": None,
                    "error": "Failed to update report status"
                }
            
            return {
                "success": True,
                "data": {"report_id": report_id, "status": "archived"},
                "error": None
            }
        except Exception as e:
            logger.error(f"Failed to archive report: {e}")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _serialize_report(self, report: Any) -> Dict[str, Any]:
        """Serialize report to dict"""
        return {
            "report_id": getattr(report, 'report_id', ''),
            "company": getattr(report, 'company', ''),
            "industry": getattr(report, 'industry', ''),
            "frameworks": getattr(report, 'frameworks', []),
            "status": getattr(report, 'status', 'unknown'),
            "confidence_score": getattr(report, 'confidence_score', None),
            "created_at": getattr(report, 'created_at', ''),
            "updated_at": getattr(report, 'updated_at', None),
        }

