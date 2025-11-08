"""
Report versioning models for ConsultantOS (v0.4.0)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VersionStatus(str, Enum):
    """Version status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ReportVersion(BaseModel):
    """Report version model"""
    version_id: str
    report_id: str = Field(..., description="Parent report ID")
    version_number: int = Field(..., gt=0, description="Version number (1, 2, 3...)")
    
    # Version metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = Field(..., description="User ID")
    status: VersionStatus = VersionStatus.DRAFT
    
    # Content snapshot
    company: str
    industry: Optional[str] = None
    frameworks: List[str]
    executive_summary: Optional[Dict[str, Any]] = None
    
    # Storage
    pdf_url: Optional[str] = None
    signed_url: Optional[str] = None
    
    # Change tracking
    change_summary: Optional[str] = None
    parent_version_id: Optional[str] = None  # For branching
    
    # Metrics
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Confidence score between 0 and 1")
    execution_time_seconds: Optional[float] = None


class VersionHistory(BaseModel):
    """Version history for a report"""
    report_id: str
    versions: List[ReportVersion]
    current_version: Optional[str] = None  # Current version ID
    total_versions: int


class CreateVersionRequest(BaseModel):
    """Request to create a new version"""
    report_id: str
    change_summary: Optional[str] = None
    parent_version_id: Optional[str] = None


class VersionDiff(BaseModel):
    """Version difference model"""
    from_version: str
    to_version: str
    changes: Dict[str, Any] = Field(..., description="Detailed changes")
    summary: str = Field(..., description="Human-readable summary of changes")

