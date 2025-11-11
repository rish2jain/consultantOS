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
    Timeline,
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

# Optional imports for additional models (may not exist after refactor)
try:
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
    _has_enhanced_reports = True
except ImportError:
    _has_enhanced_reports = False

try:
    from consultantos.models.financial_indicators import (
        TechnicalIndicators,
        SectorPerformance,
        EconomicIndicators,
        ComprehensiveFinancialData,
    )
    _has_financial_indicators = True
except ImportError:
    _has_financial_indicators = False

try:
    from consultantos.models.positioning import (
        CompetitivePosition,
        PositionTrajectory,
        StrategicGroup,
        WhiteSpaceOpportunity,
        PositionThreat,
        DynamicPositioning,
        PositioningAnalysis
    )
    _has_positioning = True
except ImportError:
    _has_positioning = False

try:
    from consultantos.models.disruption import (
        DisruptionThreat,
        DisruptionAssessment,
        VulnerabilityBreakdown,
        TechnologyTrend,
        CustomerJobMisalignment,
        BusinessModelShift,
        DisruptionScoreComponents
    )
    _has_disruption = True
except ImportError:
    _has_disruption = False

try:
    from consultantos.models.decisions import (
        DecisionUrgency,
        DecisionCategory,
        DecisionOption,
        StrategicDecision,
        DecisionBrief
    )
    _has_decisions = True
except ImportError:
    _has_decisions = False

try:
    from consultantos.models.systems import (
        LoopType,
        CausalLink,
        FeedbackLoop,
        LeveragePoint,
        SystemDynamicsAnalysis
    )
    _has_systems = True
except ImportError:
    _has_systems = False

try:
    from consultantos.models.momentum import (
        MomentumMetric,
        FlywheelVelocity,
        MomentumAnalysis
    )
    _has_momentum = True
except ImportError:
    _has_momentum = False

try:
    from consultantos.models.strategic_intelligence import (
        StrategicHealthScore,
        EnhancedStrategicReport as SI_EnhancedReport,
        StrategicInsight,
        GeographicExpansionOpportunity
    )
    _has_strategic_intelligence = True
except ImportError:
    _has_strategic_intelligence = False

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
]

# Conditionally add optional models to __all__
if _has_enhanced_reports:
    __all__.extend([
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
    ])

if _has_financial_indicators:
    __all__.extend([
        "TechnicalIndicators",
        "SectorPerformance",
        "EconomicIndicators",
        "ComprehensiveFinancialData",
    ])

if _has_positioning:
    __all__.extend([
        "CompetitivePosition",
        "PositionTrajectory",
        "StrategicGroup",
        "WhiteSpaceOpportunity",
        "PositionThreat",
        "DynamicPositioning",
        "PositioningAnalysis",
    ])

if _has_disruption:
    __all__.extend([
        "DisruptionThreat",
        "DisruptionAssessment",
        "VulnerabilityBreakdown",
        "TechnologyTrend",
        "CustomerJobMisalignment",
        "BusinessModelShift",
        "DisruptionScoreComponents",
    ])

if _has_decisions:
    __all__.extend([
        "DecisionUrgency",
        "DecisionCategory",
        "DecisionOption",
        "StrategicDecision",
        "DecisionBrief",
    ])

if _has_systems:
    __all__.extend([
        "LoopType",
        "CausalLink",
        "FeedbackLoop",
        "LeveragePoint",
        "SystemDynamicsAnalysis",
    ])

if _has_momentum:
    __all__.extend([
        "MomentumMetric",
        "FlywheelVelocity",
        "MomentumAnalysis",
    ])

if _has_strategic_intelligence:
    __all__.extend([
        "StrategicHealthScore",
        "SI_EnhancedReport",
        "StrategicInsight",
        "GeographicExpansionOpportunity",
    ])

