"""
Report versioning API endpoints (v0.5.0)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Security
from consultantos.models.versioning import (
    ReportVersion,
    VersionHistory,
    CreateVersionRequest,
    VersionDiff,
    VersionStatus
)
from consultantos.auth import verify_api_key, get_api_key
from consultantos.database import get_db_service
import secrets
from datetime import datetime
import json

router = APIRouter(prefix="/versions", tags=["versions"])

# In-memory version store (in production, use database)
_versions: dict[str, ReportVersion] = {}
_version_history: dict[str, List[str]] = {}  # report_id -> list of version_ids


def calculate_diff(from_version: ReportVersion, to_version: ReportVersion) -> VersionDiff:
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
        summary_parts.append(f"Confidence changed from {changes['confidence_score']['from']:.2f} to {changes['confidence_score']['to']:.2f}")
    
    summary = "; ".join(summary_parts) if summary_parts else "Minor updates"
    
    return VersionDiff(
        from_version=from_version.version_id,
        to_version=to_version.version_id,
        changes=changes,
        summary=summary
    )


@router.post("", response_model=ReportVersion, status_code=status.HTTP_201_CREATED)
async def create_version(
    request: CreateVersionRequest,
    user_info: dict = Security(verify_api_key)
):
    """Create a new version of a report"""
    # Get the original report metadata
    db_service = get_db_service()
    report_metadata = db_service.get_report_metadata(request.report_id)
    
    if not report_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Determine parent version
    parent_version_id = request.parent_version_id
    if not parent_version_id:
        # Get current version or create first version
        history = _version_history.get(request.report_id, [])
        if history:
            parent_version_id = history[-1]  # Latest version
        else:
            parent_version_id = None
    
    # Calculate version number
    history = _version_history.get(request.report_id, [])
    version_number = len(history) + 1
    
    # Create new version
    version_id = f"version_{secrets.token_urlsafe(16)}"
    
    # Get parent version data if exists
    parent_data = {}
    if parent_version_id and parent_version_id in _versions:
        parent_version = _versions[parent_version_id]
        parent_data = {
            "executive_summary": parent_version.executive_summary,
            "frameworks": parent_version.frameworks.copy(),
            "confidence_score": parent_version.confidence_score
        }
    
    version = ReportVersion(
        version_id=version_id,
        report_id=request.report_id,
        version_number=version_number,
        created_by=user_info["user_id"],
        status=VersionStatus.DRAFT,
        company=report_metadata.company,
        industry=report_metadata.industry,
        frameworks=parent_data.get("frameworks", report_metadata.frameworks),
        executive_summary=parent_data.get("executive_summary"),
        pdf_url=report_metadata.pdf_url,
        change_summary=request.change_summary,
        parent_version_id=parent_version_id,
        confidence_score=parent_data.get("confidence_score", report_metadata.confidence_score),
        execution_time_seconds=report_metadata.execution_time_seconds
    )
    
    _versions[version_id] = version
    
    # Update history
    if request.report_id not in _version_history:
        _version_history[request.report_id] = []
    _version_history[request.report_id].append(version_id)
    
    return version


@router.get("/report/{report_id}", response_model=VersionHistory)
async def get_version_history(
    report_id: str,
    api_key: Optional[str] = Security(get_api_key, use_cache=False)
):
    """Get version history for a report (authentication optional for read access)"""
    version_ids = _version_history.get(report_id, [])
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
    
    return VersionHistory(
        report_id=report_id,
        versions=versions,
        current_version=current_version_id,
        total_versions=len(versions)
    )


@router.get("/{version_id}", response_model=ReportVersion)
async def get_version(
    version_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Get a specific version"""
    if version_id not in _versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    return _versions[version_id]


@router.post("/{version_id}/publish", response_model=ReportVersion)
async def publish_version(
    version_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Publish a version (make it the current version)"""
    if version_id not in _versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    version = _versions[version_id]
    
    # Check ownership
    if version.created_by != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only publish your own versions"
        )
    
    version.status = VersionStatus.PUBLISHED
    _versions[version_id] = version
    
    return version


@router.post("/{version_id}/rollback", response_model=ReportVersion)
async def rollback_to_version(
    version_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Rollback to a specific version (creates a new version based on it)"""
    if version_id not in _versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    source_version = _versions[version_id]
    
    # Create new version based on this one
    request = CreateVersionRequest(
        report_id=source_version.report_id,
        change_summary=f"Rollback to version {source_version.version_number}",
        parent_version_id=version_id
    )
    
    return await create_version(request, user_info)


@router.get("/{from_version_id}/diff/{to_version_id}", response_model=VersionDiff)
async def compare_versions(
    from_version_id: str,
    to_version_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Compare two versions"""
    if from_version_id not in _versions or to_version_id not in _versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both versions not found"
        )
    
    from_version = _versions[from_version_id]
    to_version = _versions[to_version_id]
    
    if from_version.report_id != to_version.report_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Versions must be from the same report"
        )
    
    return calculate_diff(from_version, to_version)


@router.post("/{version_id}/branch", response_model=ReportVersion)
async def create_branch(
    version_id: str,
    change_summary: Optional[str] = None,
    user_info: dict = Security(verify_api_key)
):
    """Create a branch from a version"""
    if version_id not in _versions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    source_version = _versions[version_id]
    
    request = CreateVersionRequest(
        report_id=source_version.report_id,
        change_summary=change_summary or f"Branch from version {source_version.version_number}",
        parent_version_id=version_id
    )
    
    return await create_version(request, user_info)

