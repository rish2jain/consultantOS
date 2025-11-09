"""
Models for switching cost features (saved searches, teams, personal KB, custom frameworks)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


# ===== Saved Searches =====

class SavedSearch(BaseModel):
    """Saved search configuration for reuse and monitoring"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    company: str
    industry: str
    frameworks: List[str]
    depth: str = "standard"
    auto_run: bool = False  # Run automatically on schedule
    schedule: Optional[str] = None  # cron expression (e.g., "0 9 * * 1" for Monday 9am)
    last_run: Optional[datetime] = None
    run_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('schedule')
    def validate_cron(cls, v):
        """Validate cron expression format"""
        if v and not cls._is_valid_cron(v):
            raise ValueError('Invalid cron expression')
        return v

    @staticmethod
    def _is_valid_cron(cron_expr: str) -> bool:
        """Basic cron validation (5 or 6 fields)"""
        parts = cron_expr.split()
        return len(parts) in [5, 6]


class CreateSavedSearchRequest(BaseModel):
    """Request to create saved search"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    company: str
    industry: str
    frameworks: List[str] = Field(..., min_items=1)
    depth: str = "standard"
    auto_run: bool = False
    schedule: Optional[str] = None


class UpdateSavedSearchRequest(BaseModel):
    """Request to update saved search"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    auto_run: Optional[bool] = None
    schedule: Optional[str] = None


# ===== Teams =====

class TeamRole(str, Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamPlan(str, Enum):
    """Team subscription plans"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Team(BaseModel):
    """Team workspace"""
    id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    plan: TeamPlan = TeamPlan.FREE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    member_count: int = 1
    analyses_count: int = 0
    storage_used_mb: float = 0.0

    # Plan limits
    max_members: int = 5  # FREE: 5, PRO: 20, ENTERPRISE: unlimited
    max_analyses_per_month: int = 50  # FREE: 50, PRO: 500, ENTERPRISE: unlimited


class TeamMember(BaseModel):
    """Team member"""
    id: str
    team_id: str
    user_id: str
    email: str
    role: TeamRole
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    invited_by: Optional[str] = None  # user_id who sent invite


class CreateTeamRequest(BaseModel):
    """Request to create team"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    plan: TeamPlan = TeamPlan.FREE


class InviteMemberRequest(BaseModel):
    """Request to invite team member"""
    email: str
    role: TeamRole = TeamRole.MEMBER


class Comment(BaseModel):
    """Comment on analysis"""
    id: str
    analysis_id: str
    team_id: str
    user_id: str
    user_email: str
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    parent_id: Optional[str] = None  # For threaded comments
    reactions: Dict[str, int] = Field(default_factory=dict)  # e.g., {"👍": 3, "❤️": 1}


class CreateCommentRequest(BaseModel):
    """Request to create comment"""
    text: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[str] = None


# ===== Personal Knowledge Base =====

class KnowledgeItem(BaseModel):
    """Item in personal knowledge base"""
    id: str
    user_id: str
    analysis_id: str
    company: str
    industry: str
    frameworks_used: List[str]
    key_insights: List[str]
    created_at: datetime
    relevance_score: float = 0.0  # For search ranking


class Timeline(BaseModel):
    """Timeline of analyses for a company"""
    company: str
    analyses: List[Dict[str, Any]]  # Analysis metadata sorted by date
    trend_summary: str
    key_changes: List[str]


class ConnectionNode(BaseModel):
    """Node in knowledge graph"""
    id: str
    type: str  # "company", "industry", "framework"
    name: str
    analysis_count: int


class ConnectionEdge(BaseModel):
    """Edge in knowledge graph"""
    source: str  # node id
    target: str  # node id
    weight: int  # number of shared analyses
    relationship: str  # "same_industry", "competitor", "supplier", etc.


class KnowledgeGraph(BaseModel):
    """Graph of connections between entities"""
    nodes: List[ConnectionNode]
    edges: List[ConnectionEdge]


class SearchKBRequest(BaseModel):
    """Request to search knowledge base"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = None  # e.g., {"company": "Tesla", "frameworks": ["porter"]}


# ===== Custom Frameworks =====

class CustomFramework(BaseModel):
    """User-created custom analysis framework"""
    id: str
    user_id: str
    name: str
    description: str
    prompt_template: str  # Template with placeholders like {company}, {industry}
    response_schema: Dict[str, Any]  # JSON schema for structured output
    is_public: bool = False  # Can others use it?
    category: Optional[str] = None  # "competitive", "financial", "market", etc.
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = 0
    rating: float = 0.0  # Average user rating
    rating_count: int = 0


class CreateCustomFrameworkRequest(BaseModel):
    """Request to create custom framework"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    prompt_template: str = Field(..., min_length=50)
    response_schema: Dict[str, Any]
    is_public: bool = False
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class UpdateCustomFrameworkRequest(BaseModel):
    """Request to update custom framework"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    prompt_template: Optional[str] = None
    response_schema: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class RateFrameworkRequest(BaseModel):
    """Request to rate a framework"""
    rating: float = Field(..., ge=1.0, le=5.0)
    review: Optional[str] = Field(None, max_length=1000)


# ===== Analysis History =====

class AnalysisVersion(BaseModel):
    """Version of analysis for a company"""
    id: str
    company: str
    industry: str
    user_id: str
    frameworks: List[str]
    created_at: datetime
    confidence: float
    key_findings: List[str]
    report_url: Optional[str] = None


class CompanyHistory(BaseModel):
    """History of all analyses for a company"""
    company: str
    versions: List[AnalysisVersion]
    total_count: int


class AnalysisComparison(BaseModel):
    """Comparison between two analyses"""
    analysis_1: AnalysisVersion
    analysis_2: AnalysisVersion
    differences: Dict[str, Any]  # Framework-specific differences
    summary: str


class Bookmark(BaseModel):
    """Bookmarked analysis"""
    id: str
    user_id: str
    analysis_id: str
    company: str
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CreateBookmarkRequest(BaseModel):
    """Request to create bookmark"""
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)


# ===== Email Digest =====

class DigestFrequency(str, Enum):
    """Email digest frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DigestPreferences(BaseModel):
    """User's digest preferences"""
    user_id: str
    enabled: bool = True
    frequency: DigestFrequency = DigestFrequency.WEEKLY
    include_monitored: bool = True  # Include auto-run saved searches
    include_team_activity: bool = True
    include_kb_insights: bool = True
    send_time: str = "09:00"  # HH:MM format
    timezone: str = "UTC"


class DigestContent(BaseModel):
    """Content for email digest"""
    user_id: str
    period_start: datetime
    period_end: datetime
    monitored_companies: List[Dict[str, Any]]  # Companies from saved searches
    team_activity: List[Dict[str, Any]]  # Team analyses and comments
    kb_insights: List[str]  # New patterns/insights from KB
    alerts: List[Dict[str, Any]]  # Important changes detected


class Alert(BaseModel):
    """Alert for significant changes"""
    id: str
    user_id: str
    company: str
    alert_type: str  # "significant_change", "new_competitor", "framework_shift"
    severity: str  # "low", "medium", "high"
    message: str
    details: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False


class CreateAlertRequest(BaseModel):
    """Request to create custom alert"""
    company: str
    alert_type: str
    conditions: Dict[str, Any]  # Conditions that trigger alert
