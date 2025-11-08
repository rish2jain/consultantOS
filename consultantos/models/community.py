"""
Community models for ConsultantOS (v0.5.0)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CaseStudyStatus(str, Enum):
    """Case study status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CaseStudy(BaseModel):
    """Case study model"""
    case_study_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    
    # Content
    company: str
    industry: Optional[str] = None
    frameworks_used: List[str] = Field(default_factory=list)
    report_id: Optional[str] = None  # Link to original report
    
    # Author
    author_id: str
    author_name: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    status: CaseStudyStatus = CaseStudyStatus.DRAFT
    
    # Engagement
    views: int = 0
    likes: int = 0
    liked_by: set[str] = Field(default_factory=set)  # Track users who liked
    bookmarks: int = 0
    
    # Tags and categorization
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    
    # Lessons learned
    key_insights: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    outcomes: Optional[str] = None


class CreateCaseStudyRequest(BaseModel):
    """Request to create a case study"""
    title: str
    description: str
    company: str
    industry: Optional[str] = None
    frameworks_used: Optional[List[str]] = None
    report_id: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    key_insights: Optional[List[str]] = None
    challenges: Optional[List[str]] = None
    outcomes: Optional[str] = None


class UpdateCaseStudyRequest(BaseModel):
    """Request to update a case study"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    key_insights: Optional[List[str]] = None
    challenges: Optional[List[str]] = None
    outcomes: Optional[str] = None


class CaseStudyListResponse(BaseModel):
    """List of case studies"""
    case_studies: List[CaseStudy]
    total: int
    page: int = 1
    page_size: int = 20


class BestPractice(BaseModel):
    """Best practice model"""
    practice_id: str
    title: str
    description: str
    category: str  # e.g., "framework_application", "data_sources", "presentation"
    
    # Author
    author_id: str
    author_name: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: Optional[str] = None
    
    # Engagement
    upvotes: int = 0
    downvotes: int = 0
    upvoters: set[str] = Field(default_factory=set)  # Track users who upvoted
    downvoters: set[str] = Field(default_factory=set)  # Track users who downvoted
    
    # Content
    steps: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class CreateBestPracticeRequest(BaseModel):
    """Request to create a best practice"""
    title: str
    description: str
    category: str
    steps: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class BestPracticeListResponse(BaseModel):
    """List of best practices"""
    practices: List[BestPractice]
    total: int
    page: int = 1
    page_size: int = 20

