"""
Advanced analysis modules for ConsultantOS

System dynamics, momentum tracking, and historical pattern analysis.

Phase 1 Quick Wins:
- Cross-source signal amplification (triangulation_signals)
- Geographic opportunity detection (geographic_opportunities)
- Sentiment-performance prediction (sentiment_prediction)
"""
# Import only if modules exist (some may not be implemented yet)
try:
    from .feedback_loops import FeedbackLoopDetector
except ImportError:
    FeedbackLoopDetector = None

try:
    from .momentum_tracking import MomentumTrackingEngine
except ImportError:
    MomentumTrackingEngine = None

try:
    from .historical_patterns import HistoricalPatternMatcher
except ImportError:
    HistoricalPatternMatcher = None

# Legacy pattern library support
try:
    from .pattern_library import (
        PatternLibraryService,
        HistoricalPattern as LegacyHistoricalPattern,
        PatternMatch as LegacyPatternMatch,
        PatternCategory as LegacyPatternCategory,
    )
    _LEGACY_AVAILABLE = True
except ImportError:
    _LEGACY_AVAILABLE = False

# Phase 1 Quick Wins - Strategic Intelligence Modules (import only if they exist)
try:
    from .triangulation_signals import (
        analyze_triangulation_signals,
        TriangulationSignal,
        TriangulationSignalsResult,
        SignalType,
        DivergencePattern,
    )
except ImportError:
    analyze_triangulation_signals = None
    TriangulationSignal = None
    TriangulationSignalsResult = None
    SignalType = None
    DivergencePattern = None

try:
    from .geographic_opportunities import (
        analyze_geographic_opportunities,
        GeographicOpportunity,
        GeographicOpportunityResult,
        OpportunityIndex,
    )
except ImportError:
    analyze_geographic_opportunities = None
    GeographicOpportunity = None
    GeographicOpportunityResult = None
    OpportunityIndex = None

try:
    from .sentiment_prediction import (
        predict_financial_performance,
        SentimentPrediction,
        SentimentPredictionResult,
        PerformanceOutcome,
        SentimentTrend,
    )
except ImportError:
    predict_financial_performance = None
    SentimentPrediction = None
    SentimentPredictionResult = None
    PerformanceOutcome = None
    SentimentTrend = None

__all__ = []

# Add modules that are available
if FeedbackLoopDetector:
    __all__.append("FeedbackLoopDetector")
if MomentumTrackingEngine:
    __all__.append("MomentumTrackingEngine")
if HistoricalPatternMatcher:
    __all__.append("HistoricalPatternMatcher")

# Phase 1 Quick Wins
if analyze_triangulation_signals:
    __all__.extend([
        "analyze_triangulation_signals",
        "TriangulationSignal",
        "TriangulationSignalsResult",
        "SignalType",
        "DivergencePattern",
    ])
if analyze_geographic_opportunities:
    __all__.extend([
        "analyze_geographic_opportunities",
        "GeographicOpportunity",
        "GeographicOpportunityResult",
        "OpportunityIndex",
    ])
if predict_financial_performance:
    __all__.extend([
        "predict_financial_performance",
        "SentimentPrediction",
        "SentimentPredictionResult",
        "PerformanceOutcome",
        "SentimentTrend",
    ])

if _LEGACY_AVAILABLE:
    __all__.extend([
        "PatternLibraryService",
        "LegacyHistoricalPattern",
        "LegacyPatternMatch",
        "LegacyPatternCategory",
    ])
