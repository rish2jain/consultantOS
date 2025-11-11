"""
Version Control Agent for managing report versions and comparisons
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from consultantos.agents.base_agent import BaseAgent
from consultantos.database import get_db_service
from consultantos.models.versioning import ReportVersion, VersionHistory, VersionDiff, VersionStatus
import logging
from datetime import datetime
import secrets
import asyncio

logger = logging.getLogger(__name__)

# In-memory version store (in production, use database)
_versions: dict[str, ReportVersion] = {}
_version_history: dict[str, List[str]] = {}  # report_id -> list of version_ids
# Async locks for thread-safety
_versions_lock = asyncio.Lock()
_version_history_lock = asyncio.Lock()


class VersionListRequest(BaseModel):
    report_id: str = Field(..., description="ID of the report to get versions for.")


class VersionCreateRequest(BaseModel):
    report_id: str = Field(..., description="ID of the report to create a version for.")
    user_id: str = Field(..., description="ID of the user creating the version.")
    change_summary: Optional[str] = Field(None, description="Summary of changes in this version.")
    parent_version_id: Optional[str] = Field(None, description="Parent version ID for branching.")


class VersionCompareRequest(BaseModel):
    from_version_id: str = Field(..., description="Source version ID.")
    to_version_id: str = Field(..., description="Target version ID.")


class VersionResponse(BaseModel):
    versions: List[Dict[str, Any]] = Field(default_factory=list, description="List of versions.")
    version_history: Optional[Dict[str, Any]] = Field(None, description="Version history for a report.")
    diff: Optional[Dict[str, Any]] = Field(None, description="Version comparison diff.")
    message: Optional[str] = Field(None, description="Confirmation message for actions.")


class VersionControlAgent(BaseAgent):
    """Agent for managing report versions and comparisons"""

    def __init__(self, timeout: int = 60):
        super().__init__(name="VersionControlAgent", timeout=timeout)
        self.db_service = get_db_service()

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action_type = input_data.get("action_type", "list")

        if action_type == "list":
            request = VersionListRequest(**input_data)
            history = await self._get_version_history(request.report_id)
            return {
                "success": True,
                "data": VersionResponse(version_history=history).model_dump(),
                "error": None
            }

        elif action_type == "create":
            request = VersionCreateRequest(**input_data)
            version = await self._create_version(
                report_id=request.report_id,
                user_id=request.user_id,
                change_summary=request.change_summary,
                parent_version_id=request.parent_version_id
            )
            return {
                "success": True,
                "data": VersionResponse(
                    versions=[version.model_dump()],
                    message=f"Version {version.version_number} created successfully."
                ).model_dump(),
                "error": None
            }

        elif action_type == "compare":
            request = VersionCompareRequest(**input_data)
            diff = await self._compare_versions(
                from_version_id=request.from_version_id,
                to_version_id=request.to_version_id
            )
            return {
                "success": True,
                "data": VersionResponse(diff=diff.model_dump() if diff else None).model_dump(),
                "error": None
            }

        elif action_type == "get":
            version_id = input_data.get("version_id")
            if not version_id:
                raise ValueError("version_id is required for get action.")
            version = await self._get_version(version_id)
            return {
                "success": True,
                "data": VersionResponse(versions=[version.model_dump()] if version else []).model_dump(),
                "error": None
            }

        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    async def _get_version_history(self, report_id: str) -> Dict[str, Any]:
        """Get version history for a report"""
        try:
            async with _version_history_lock:
                version_ids = _version_history.get(report_id, []).copy()
            
            async with _versions_lock:
                versions = [_versions[vid] for vid in version_ids if vid in _versions]

            # Sort by version number
            versions.sort(key=lambda v: v.version_number)

            # Get current version (latest published or latest draft)
            current_version_id = None
            for version in reversed(versions):
                if version.status == VersionStatus.PUBLISHED:
                    current_version_id = version.version_id
                    break
            if not current_version_id and versions:
                current_version_id = versions[-1].version_id

            return {
                "report_id": report_id,
                "versions": [v.model_dump() for v in versions],
                "current_version": current_version_id,
                "total_versions": len(versions)
            }
        except (ValueError, KeyError, AttributeError) as e:
            logger.error(f"Failed to get version history for report {report_id}: {e}", exc_info=True)
            return {
                "report_id": report_id,
                "versions": [],
                "current_version": None,
                "total_versions": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error getting version history for report {report_id}: {e}", exc_info=True)
            raise

    async def _create_version(
        self,
        report_id: str,
        user_id: str,
        change_summary: Optional[str],
        parent_version_id: Optional[str]
    ) -> ReportVersion:
        """Create a new version of a report"""
        try:
            # Get the original report metadata
            report_metadata = self.db_service.get_report_metadata(report_id)

            if not report_metadata:
                raise ValueError(f"Report {report_id} not found")

            # Atomically calculate version number and create version entry
            async with _version_history_lock:
                # Determine parent version
                if not parent_version_id:
                    history = _version_history.get(report_id, [])
                    if history:
                        parent_version_id = history[-1]  # Latest version
                    else:
                        parent_version_id = None

                # Calculate version number atomically
                history = _version_history.get(report_id, [])
                version_number = len(history) + 1

                # Create new version
                version_id = f"version_{secrets.token_urlsafe(16)}"

                # Reserve slot in history immediately to prevent duplicate version numbers
                if report_id not in _version_history:
                    _version_history[report_id] = []
                _version_history[report_id].append(version_id)

            # Get parent version data if exists (outside lock to avoid deadlock)
            parent_data = {}
            if parent_version_id:
                async with _versions_lock:
                    if parent_version_id in _versions:
                        parent_version = _versions[parent_version_id]
                        parent_data = {
                            "executive_summary": parent_version.executive_summary,
                            "frameworks": parent_version.frameworks.copy(),
                            "confidence_score": parent_version.confidence_score
                        }

            version = ReportVersion(
                version_id=version_id,
                report_id=report_id,
                version_number=version_number,
                created_at=datetime.now().isoformat(),
                created_by=user_id,
                status=VersionStatus.DRAFT,
                company=report_metadata.get("company", ""),
                industry=report_metadata.get("industry"),
                frameworks=parent_data.get("frameworks", report_metadata.get("frameworks", [])),
                executive_summary=parent_data.get("executive_summary", report_metadata.get("executive_summary")),
                confidence_score=parent_data.get("confidence_score", report_metadata.get("confidence_score")),
                change_summary=change_summary,
                parent_version_id=parent_version_id
            )

            async with _versions_lock:
                _versions[version_id] = version

            return version
        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            raise

    async def _compare_versions(
        self,
        from_version_id: str,
        to_version_id: str
    ) -> Optional[VersionDiff]:
        """Compare two versions"""
        try:
            async with _versions_lock:
                from_version = _versions.get(from_version_id)
                to_version = _versions.get(to_version_id)

            if not from_version or not to_version:
                return None

            return self._calculate_diff(from_version, to_version)
        except Exception as e:
            logger.error(f"Failed to compare versions: {e}")
            return None

    def _calculate_diff(self, from_version: ReportVersion, to_version: ReportVersion) -> VersionDiff:
        """Calculate differences between two versions"""
        changes = {}

        # Compare executive summary
        if from_version.executive_summary != to_version.executive_summary:
            changes["executive_summary"] = {
                "from": from_version.executive_summary,
                "to": to_version.executive_summary
            }

        # Compare frameworks
        if set(from_version.frameworks) != set(to_version.frameworks):
            changes["frameworks"] = {
                "added": list(set(to_version.frameworks) - set(from_version.frameworks)),
                "removed": list(set(from_version.frameworks) - set(to_version.frameworks))
            }

        # Compare confidence scores
        if from_version.confidence_score != to_version.confidence_score:
            changes["confidence_score"] = {
                "from": from_version.confidence_score,
                "to": to_version.confidence_score
            }

        # Generate summary
        summary_parts = []
        if "executive_summary" in changes:
            summary_parts.append("Executive summary updated")
        if "frameworks" in changes:
            added = changes["frameworks"]["added"]
            removed = changes["frameworks"]["removed"]
            if added:
                summary_parts.append(f"Added frameworks: {', '.join(added)}")
            if removed:
                summary_parts.append(f"Removed frameworks: {', '.join(removed)}")
        if "confidence_score" in changes:
            from_score = changes["confidence_score"]["from"] or 0
            to_score = changes["confidence_score"]["to"] or 0
            summary_parts.append(f"Confidence changed from {from_score:.2f} to {to_score:.2f}")

        summary = "; ".join(summary_parts) if summary_parts else "Minor updates"

        return VersionDiff(
            from_version=from_version.version_id,
            to_version=to_version.version_id,
            changes=changes,
            summary=summary
        )

    async def _get_version(self, version_id: str) -> Optional[ReportVersion]:
        """Get a specific version"""
        async with _versions_lock:
            return _versions.get(version_id)

