"""
Models package for ConsultantOS
"""
# Import from models.py (the file, not this package)
import sys
import os
# Get the parent directory to import models.py
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_models_file = os.path.join(_parent_dir, 'models.py')
if os.path.exists(_models_file):
    import importlib.util
    spec = importlib.util.spec_from_file_location("consultantos.models_file", _models_file)
    models_file = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_file)
    
    # Re-export all models from models.py
    AnalysisRequest = models_file.AnalysisRequest
    EntityMention = models_file.EntityMention
    SentimentScore = models_file.SentimentScore
    EntityRelationship = models_file.EntityRelationship
    CompanyResearch = models_file.CompanyResearch
    MarketTrends = models_file.MarketTrends
    AnalystRecommendations = models_file.AnalystRecommendations
    NewsSentiment = models_file.NewsSentiment
    DataSourceValidation = models_file.DataSourceValidation
    FinancialSnapshot = models_file.FinancialSnapshot
    PortersFiveForces = models_file.PortersFiveForces
    SWOTAnalysis = models_file.SWOTAnalysis
    PESTELAnalysis = models_file.PESTELAnalysis
    BlueOceanStrategy = models_file.BlueOceanStrategy
    FrameworkAnalysis = models_file.FrameworkAnalysis
    ExecutiveSummary = models_file.ExecutiveSummary
    StrategicReport = models_file.StrategicReport

from consultantos.models.templates import (
    FrameworkTemplate,
    TemplateLibrary,
    CreateTemplateRequest,
    UpdateTemplateRequest,
    TemplateCategory,
    TemplateVisibility
)
from consultantos.models.decisions import (
    DecisionOption,
    StrategicDecision,
    DecisionBrief,
    DecisionUrgency,
    DecisionCategory
)
from consultantos.models.versioning import (
    ReportVersion,
    VersionHistory,
    CreateVersionRequest,
    VersionDiff,
    VersionStatus
)
from consultantos.models.sharing import (
    ShareAccess,
    CreateShareRequest,
    ShareListResponse,
    SharePermission
)
from consultantos.models.subscription import (
    PricingTier,
    SubscriptionStatus,
    TierLimits,
    Subscription,
    UsageSummary,
    PromoCode,
    BillingEvent,
    UpgradeRequest,
    CheckoutSession,
    TIER_CONFIGS,
    TIER_PRICING
)
from consultantos.models.switching_costs import (
    # Saved Searches
    SavedSearch,
    CreateSavedSearchRequest,
    UpdateSavedSearchRequest,
    # Teams
    Team,
    TeamMember,
    TeamRole,
    TeamPlan,
    CreateTeamRequest,
    InviteMemberRequest,
    Comment,
    CreateCommentRequest,
    # Personal KB
    KnowledgeItem,
    Timeline,  # Make Timeline available directly
    KnowledgeGraph,
    ConnectionNode,
    ConnectionEdge,
    SearchKBRequest,
    # Custom Frameworks
    CustomFramework,
    CreateCustomFrameworkRequest,
    UpdateCustomFrameworkRequest,
    RateFrameworkRequest,
    # History & Bookmarks
    AnalysisVersion,
    CompanyHistory,
    AnalysisComparison,
    Bookmark,
    CreateBookmarkRequest,
    # Digest & Alerts
    DigestPreferences,
    DigestContent,
    DigestFrequency,
    Alert,
    CreateAlertRequest,
)

# Enhanced Report Models
from consultantos.models.enhanced_reports import (
    EnhancedPortersFiveForces,
    EnhancedSWOTAnalysis,
    EnhancedPESTELAnalysis,
    EnhancedBlueOceanStrategy,
    ActionableRecommendations,
    ActionItem,
    RiskOpportunityMatrix,
    RiskItem,
    OpportunityItem,
    EnhancedStrategicReport,
    ExecutiveSummaryLayer,
    DetailedAnalysisLayer,
    SupportingAppendices,
    CompetitiveIntelligence,
    ScenarioPlanning,
    PriorityLevel,
    Timeline as EnhancedTimeline,
    ImpactLevel,
    ConfidenceLevel,
)

# Financial Indicators Models
from consultantos.models.financial_indicators import (
    TechnicalIndicators,
    SectorPerformance,
    EconomicIndicators,
    ComprehensiveFinancialData,
)

# Strategic Intelligence Models
from consultantos.models.positioning import (
    CompetitivePosition,
    PositionTrajectory,
    StrategicGroup,
    WhiteSpaceOpportunity,
    PositionThreat,
    DynamicPositioning,
    PositioningAnalysis
)

# Disruption Analysis Models
from consultantos.models.disruption import (
    DisruptionThreat,
    DisruptionAssessment,
    VulnerabilityBreakdown,
    TechnologyTrend,
    CustomerJobMisalignment,
    BusinessModelShift,
    DisruptionScoreComponents
)
from consultantos.models.decisions import (
    DecisionUrgency,
    DecisionCategory,
    DecisionOption,
    StrategicDecision,
    DecisionBrief
)
from consultantos.models.systems import (
    LoopType,
    CausalLink,
    FeedbackLoop,
    LeveragePoint,
    SystemDynamicsAnalysis
)
from consultantos.models.momentum import (
    MomentumMetric,
    FlywheelVelocity,
    MomentumAnalysis
)
from consultantos.models.strategic_intelligence import (
    StrategicHealthScore,
    EnhancedStrategicReport as SI_EnhancedReport,
    StrategicInsight,
    GeographicExpansionOpportunity
)

__all__ = [
    # Core models from models.py
    "AnalysisRequest",
    "EntityMention",
    "SentimentScore",
    "EntityRelationship",
    "CompanyResearch",
    "MarketTrends",
    "AnalystRecommendations",
    "NewsSentiment",
    "DataSourceValidation",
    "FinancialSnapshot",
    "PortersFiveForces",
    "SWOTAnalysis",
    "PESTELAnalysis",
    "BlueOceanStrategy",
    "FrameworkAnalysis",
    "ExecutiveSummary",
    "StrategicReport",
    # Templates
    "FrameworkTemplate",
    "TemplateLibrary",
    "CreateTemplateRequest",
    "UpdateTemplateRequest",
    "TemplateCategory",
    "TemplateVisibility",
    # Versioning
    "ReportVersion",
    "VersionHistory",
    "CreateVersionRequest",
    "VersionDiff",
    "VersionStatus",
    # Sharing
    "ShareAccess",
    "CreateShareRequest",
    "ShareListResponse",
    "SharePermission",
    # Subscription
    "PricingTier",
    "SubscriptionStatus",
    "TierLimits",
    "Subscription",
    "UsageSummary",
    "PromoCode",
    "BillingEvent",
    "UpgradeRequest",
    "CheckoutSession",
    "TIER_CONFIGS",
    "TIER_PRICING",
    # Switching Costs
    "SavedSearch",
    "CreateSavedSearchRequest",
    "UpdateSavedSearchRequest",
    "Team",
    "TeamMember",
    "TeamRole",
    "TeamPlan",
    "CreateTeamRequest",
    "InviteMemberRequest",
    "Comment",
    "CreateCommentRequest",
    "KnowledgeItem",
    "Timeline",
    "KnowledgeGraph",
    "ConnectionNode",
    "ConnectionEdge",
    "SearchKBRequest",
    "CustomFramework",
    "CreateCustomFrameworkRequest",
    "UpdateCustomFrameworkRequest",
    "RateFrameworkRequest",
    "AnalysisVersion",
    "CompanyHistory",
    "AnalysisComparison",
    "Bookmark",
    "CreateBookmarkRequest",
    "DigestPreferences",
    "DigestContent",
    "DigestFrequency",
    "Alert",
    "CreateAlertRequest",
    # Enhanced Reports
    "EnhancedPortersFiveForces",
    "EnhancedSWOTAnalysis",
    "EnhancedPESTELAnalysis",
    "EnhancedBlueOceanStrategy",
    "ActionableRecommendations",
    "ActionItem",
    "RiskOpportunityMatrix",
    "RiskItem",
    "OpportunityItem",
    "EnhancedStrategicReport",
    "ExecutiveSummaryLayer",
    "DetailedAnalysisLayer",
    "SupportingAppendices",
    "CompetitiveIntelligence",
    "ScenarioPlanning",
    "PriorityLevel",
    "EnhancedTimeline",
    "ImpactLevel",
    "ConfidenceLevel",
    # Financial Indicators
    "TechnicalIndicators",
    "SectorPerformance",
    "EconomicIndicators",
    "ComprehensiveFinancialData",
    # Strategic Intelligence - Positioning
    "CompetitivePosition",
    "PositionTrajectory",
    "StrategicGroup",
    "WhiteSpaceOpportunity",
    "PositionThreat",
    "DynamicPositioning",
    "PositioningAnalysis",
    # Strategic Intelligence - Disruption
    "DisruptionThreat",
    "VulnerabilityBreakdown",
    "TechnologyTrend",
    "CustomerJobMisalignment",
    "BusinessModelShift",
    "DisruptionAssessment",
    "DisruptionScoreComponents",
    # Strategic Intelligence - Decisions
    "DecisionUrgency",
    "DecisionCategory",
    "DecisionOption",
    "StrategicDecision",
    "DecisionBrief",
    # Strategic Intelligence - Systems
    "LoopType",
    "CausalLink",
    "FeedbackLoop",
    "LeveragePoint",
    "SystemDynamicsAnalysis",
    # Strategic Intelligence - Momentum
    "MomentumMetric",
    "FlywheelVelocity",
    "MomentumAnalysis",
    # Strategic Intelligence - Reports
    "StrategicHealthScore",
    "SI_EnhancedReport",
    "StrategicInsight",
    "GeographicExpansionOpportunity",
]

