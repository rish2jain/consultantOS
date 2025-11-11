"""
Historical pattern models for ConsultantOS

Models for pattern matching and predictive intelligence based on historical company trajectories.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class PatternCategory(str, Enum):
    """Category of historical pattern"""
    DISRUPTION = "disruption"          # Market disruption patterns
    FLYWHEEL = "flywheel"             # Compound growth patterns
    DECLINE = "decline"               # Deterioration patterns
    RECOVERY = "recovery"             # Turnaround patterns
    INNOVATION = "innovation"         # Innovation cycle patterns
    COMPETITIVE = "competitive"       # Competitive dynamics patterns


class OutcomeLikelihood(str, Enum):
    """Likelihood of predicted outcome"""
    VERY_LOW = "very_low"      # <20%
    LOW = "low"                # 20-40%
    MODERATE = "moderate"      # 40-60%
    HIGH = "high"              # 60-80%
    VERY_HIGH = "very_high"    # >80%


class PatternSignal(BaseModel):
    """Individual signal within a pattern"""
    signal_name: str = Field(..., description="Name of the signal")
    signal_type: str = Field(..., description="Type of signal (metric, event, ratio, etc.)")
    threshold: Optional[float] = Field(None, description="Threshold value if applicable")
    direction: str = Field(..., description="increasing/decreasing/stable")
    weight: float = Field(..., ge=0.0, le=1.0, description="Importance weight in pattern (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "signal_name": "gross_margin_compression",
                "signal_type": "ratio",
                "threshold": 0.4,
                "direction": "decreasing",
                "weight": 0.85
            }
        }


class HistoricalPattern(BaseModel):
    """Definition of a historical pattern"""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    pattern_name: str = Field(..., description="Human-readable pattern name")
    category: PatternCategory = Field(..., description="Pattern category")
    description: str = Field(..., description="Detailed pattern description")
    signals: List[PatternSignal] = Field(..., description="Signals that define this pattern")
    historical_examples: List[str] = Field(..., description="Companies that exhibited this pattern")
    typical_duration_months: int = Field(..., ge=0, description="Typical duration of pattern")
    typical_outcome: str = Field(..., description="Most common outcome")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Historical success/failure rate")
    required_conditions: List[str] = Field(..., description="Necessary conditions for pattern")
    warning_signs: List[str] = Field(default_factory=list, description="Early warning indicators")

    class Config:
        json_schema_extra = {
            "example": {
                "pattern_id": "disruptive_growth_asymmetric",
                "pattern_name": "Asymmetric Disruption Growth",
                "category": "disruption",
                "description": "Rapid growth in underserved segment followed by market leadership",
                "signals": [],
                "historical_examples": ["Netflix 2007-2012", "Tesla 2012-2020", "Airbnb 2010-2015"],
                "typical_duration_months": 48,
                "typical_outcome": "Category leadership or significant market share gain",
                "success_rate": 0.65,
                "required_conditions": [
                    "Incumbent complacency",
                    "Technology enabler",
                    "Underserved customer segment"
                ],
                "warning_signs": ["Incumbent response", "Regulatory pressure"]
            }
        }


class PatternMatch(BaseModel):
    """A match between current company data and historical pattern"""
    pattern: HistoricalPattern = Field(..., description="The matched historical pattern")
    match_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in pattern match (0-1)")
    matched_signals: List[str] = Field(..., description="Signals that matched")
    missing_signals: List[str] = Field(default_factory=list, description="Expected signals not present")
    divergence_points: List[str] = Field(default_factory=list, description="How current situation differs")
    stage_in_pattern: str = Field(..., description="Where in pattern lifecycle (early/mid/late)")
    time_to_outcome_estimate: str = Field(..., description="Estimated time to typical outcome")

    class Config:
        json_schema_extra = {
            "example": {
                "pattern": {},
                "match_confidence": 0.78,
                "matched_signals": ["rapid_growth_underserved", "tech_enabler", "low_initial_quality"],
                "missing_signals": ["network_effects"],
                "divergence_points": ["Stronger incumbent response than historical cases"],
                "stage_in_pattern": "mid",
                "time_to_outcome_estimate": "18-24 months"
            }
        }


class PredictedOutcome(BaseModel):
    """Predicted outcome based on pattern matching"""
    outcome_description: str = Field(..., description="Description of predicted outcome")
    likelihood: OutcomeLikelihood = Field(..., description="Likelihood category")
    probability: float = Field(..., ge=0.0, le=1.0, description="Numeric probability (0-1)")
    time_horizon: str = Field(..., description="Expected timeframe for outcome")
    confidence_factors: List[str] = Field(..., description="Factors supporting this prediction")
    risk_factors: List[str] = Field(..., description="Factors that could prevent outcome")
    alternative_scenarios: List[str] = Field(default_factory=list, description="Other possible outcomes")
    recommended_actions: List[str] = Field(..., description="Actions to increase success probability")

    class Config:
        json_schema_extra = {
            "example": {
                "outcome_description": "Market leadership in electric vehicle segment within 5 years",
                "likelihood": "high",
                "probability": 0.72,
                "time_horizon": "36-60 months",
                "confidence_factors": [
                    "Strong pattern match with Tesla 2012-2017",
                    "Technology advantage established",
                    "Customer loyalty metrics exceeding pattern average"
                ],
                "risk_factors": [
                    "Regulatory changes",
                    "Supply chain disruption",
                    "Aggressive incumbent response"
                ],
                "alternative_scenarios": [
                    "Acquisition by major incumbent (30% probability)",
                    "Plateau at niche player status (15% probability)"
                ],
                "recommended_actions": [
                    "Accelerate production scaling",
                    "Build defensible moat in battery technology",
                    "Establish brand before incumbents respond"
                ]
            }
        }


class PatternLibrary(BaseModel):
    """Collection of historical patterns"""
    patterns: List[HistoricalPattern] = Field(..., description="All defined patterns")
    last_updated: str = Field(..., description="Last update date")
    version: str = Field(..., description="Pattern library version")
    coverage_stats: Dict[str, int] = Field(..., description="Number of patterns per category")

    def get_patterns_by_category(self, category: PatternCategory) -> List[HistoricalPattern]:
        """Get all patterns in a specific category"""
        return [p for p in self.patterns if p.category == category]

    def get_pattern_by_id(self, pattern_id: str) -> Optional[HistoricalPattern]:
        """Get a specific pattern by ID"""
        for pattern in self.patterns:
            if pattern.pattern_id == pattern_id:
                return pattern
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "patterns": [],
                "last_updated": "2024-11-10",
                "version": "1.0.0",
                "coverage_stats": {
                    "disruption": 8,
                    "flywheel": 6,
                    "decline": 5,
                    "recovery": 4,
                    "innovation": 7,
                    "competitive": 6
                }
            }
        }


class HistoricalPatternAnalysis(BaseModel):
    """Complete historical pattern matching analysis"""
    matched_patterns: List[PatternMatch] = Field(..., description="Patterns that match current situation")
    predicted_outcomes: List[PredictedOutcome] = Field(..., description="Predicted outcomes ranked by probability")
    most_likely_scenario: str = Field(..., description="Single most likely outcome")
    scenario_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of most likely scenario")
    key_decision_points: List[str] = Field(..., description="Critical upcoming decision points")
    historical_analogies: List[str] = Field(..., description="Best historical company analogies")
    pattern_strength: float = Field(..., ge=0.0, le=1.0, description="Overall pattern match strength")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in predictions")
    analysis_date: str = Field(..., description="Date of analysis")

    @property
    def primary_pattern(self) -> Optional[PatternMatch]:
        """Get the strongest pattern match"""
        if not self.matched_patterns:
            return None
        return max(self.matched_patterns, key=lambda x: x.match_confidence)

    @property
    def disruption_risk(self) -> float:
        """Calculate disruption risk score"""
        disruption_matches = [
            m for m in self.matched_patterns
            if m.pattern.category == PatternCategory.DISRUPTION
        ]
        if not disruption_matches:
            return 0.0
        return max(m.match_confidence for m in disruption_matches)

    @property
    def decline_risk(self) -> float:
        """Calculate decline risk score"""
        decline_matches = [
            m for m in self.matched_patterns
            if m.pattern.category == PatternCategory.DECLINE
        ]
        if not decline_matches:
            return 0.0
        return max(m.match_confidence for m in decline_matches)

    class Config:
        json_schema_extra = {
            "example": {
                "matched_patterns": [],
                "predicted_outcomes": [],
                "most_likely_scenario": "Transition to category leader via platform strategy",
                "scenario_probability": 0.68,
                "key_decision_points": [
                    "International expansion timing (next 6 months)",
                    "Platform vs vertical integration choice (12 months)",
                    "M&A strategy for complementary capabilities (18 months)"
                ],
                "historical_analogies": [
                    "Salesforce 2004-2008 platform transition",
                    "Amazon 2002-2006 marketplace evolution"
                ],
                "pattern_strength": 0.75,
                "confidence_score": 0.82,
                "analysis_date": "2024-11-10"
            }
        }
