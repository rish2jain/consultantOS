"""
Feedback and Quality Models

Data models for user feedback, insight ratings, corrections, and quality metrics.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum


class FeedbackType(str, Enum):
    """Type of feedback provided by user"""
    RATING = "rating"
    CORRECTION = "correction"
    COMMENT = "comment"


class ErrorCategory(str, Enum):
    """Categories of errors identified in corrections"""
    FACTUAL = "factual"  # Incorrect facts or data
    TONE = "tone"  # Inappropriate tone or language
    RELEVANCE = "relevance"  # Not relevant to analysis
    DEPTH = "depth"  # Too shallow or too deep
    STRUCTURE = "structure"  # Poor organization
    OTHER = "other"


class InsightRating(BaseModel):
    """User rating for individual insights"""
    id: str = Field(description="Unique rating ID")
    insight_id: str = Field(description="ID of the insight being rated")
    report_id: str = Field(description="ID of the parent report")
    user_id: str = Field(description="ID of user providing rating")
    rating: int = Field(ge=1, le=5, description="Rating from 1-5 stars")
    feedback_text: Optional[str] = Field(None, description="Optional text feedback")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rating_123",
                "insight_id": "insight_porter_456",
                "report_id": "report_789",
                "user_id": "user_001",
                "rating": 5,
                "feedback_text": "Very insightful competitive analysis",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class InsightCorrection(BaseModel):
    """User correction for incorrect or incomplete insights"""
    id: str = Field(description="Unique correction ID")
    insight_id: str = Field(description="ID of the insight being corrected")
    report_id: str = Field(description="ID of the parent report")
    user_id: str = Field(description="ID of user providing correction")
    section: str = Field(description="Section of report (e.g., 'porter', 'swot')")
    original_text: str = Field(description="Original insight text")
    corrected_text: str = Field(description="User's corrected version")
    explanation: Optional[str] = Field(None, description="Why correction is needed")
    error_category: ErrorCategory = Field(
        default=ErrorCategory.OTHER,
        description="Type of error being corrected"
    )
    validated: bool = Field(default=False, description="Admin has reviewed")
    incorporated: bool = Field(default=False, description="Used in retraining")
    admin_notes: Optional[str] = Field(None, description="Admin review notes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    validated_at: Optional[datetime] = None

    @validator('corrected_text')
    def corrected_text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Corrected text cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "correction_123",
                "insight_id": "insight_swot_456",
                "report_id": "report_789",
                "user_id": "user_001",
                "section": "swot",
                "original_text": "Tesla has no competitors in EV market",
                "corrected_text": "Tesla faces strong competition from Rivian, Lucid, and traditional automakers",
                "explanation": "Factually incorrect - multiple EV competitors exist",
                "error_category": "factual",
                "validated": False,
                "incorporated": False
            }
        }


class QualityMetrics(BaseModel):
    """Aggregated quality metrics for a report"""
    report_id: str = Field(description="ID of the report")
    avg_rating: float = Field(ge=0, le=5, description="Average star rating")
    total_ratings: int = Field(ge=0, description="Number of ratings received")
    corrections_count: int = Field(ge=0, description="Number of corrections submitted")
    user_satisfaction: float = Field(
        ge=0, le=1,
        description="Derived satisfaction score (0-1)"
    )
    rating_distribution: Dict[int, int] = Field(
        default_factory=dict,
        description="Distribution of 1-5 star ratings"
    )
    error_categories: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by error category"
    )
    frameworks_quality: Dict[str, float] = Field(
        default_factory=dict,
        description="Average rating per framework"
    )
    computed_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def needs_improvement(self) -> bool:
        """Flag if quality is below acceptable threshold"""
        return self.avg_rating < 3.5 or self.user_satisfaction < 0.7

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "report_789",
                "avg_rating": 4.2,
                "total_ratings": 15,
                "corrections_count": 3,
                "user_satisfaction": 0.84,
                "rating_distribution": {
                    "5": 8,
                    "4": 5,
                    "3": 2,
                    "2": 0,
                    "1": 0
                },
                "error_categories": {
                    "factual": 2,
                    "relevance": 1
                },
                "frameworks_quality": {
                    "porter": 4.5,
                    "swot": 4.0,
                    "pestel": 4.1
                }
            }
        }


class FrameworkQualityStats(BaseModel):
    """Quality statistics for a specific framework"""
    framework: str = Field(description="Framework name")
    avg_rating: float = Field(ge=0, le=5)
    total_ratings: int = Field(ge=0)
    correction_rate: float = Field(
        ge=0, le=1,
        description="Corrections / total insights ratio"
    )
    common_errors: List[ErrorCategory] = Field(
        default_factory=list,
        description="Most common error types"
    )
    trend: str = Field(
        description="Improving, stable, or declining"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "framework": "porter",
                "avg_rating": 4.3,
                "total_ratings": 50,
                "correction_rate": 0.12,
                "common_errors": ["factual", "depth"],
                "trend": "improving"
            }
        }


class QualityReport(BaseModel):
    """Comprehensive quality report for analysis system"""
    time_period: str = Field(description="Period covered (e.g., 'last_30_days')")
    overall_avg_rating: float = Field(ge=0, le=5)
    total_reports: int = Field(ge=0)
    total_ratings: int = Field(ge=0)
    total_corrections: int = Field(ge=0)
    user_satisfaction: float = Field(ge=0, le=1)
    framework_stats: List[FrameworkQualityStats] = Field(default_factory=list)
    top_rated_insights: List[str] = Field(
        default_factory=list,
        description="IDs of highest rated insights"
    )
    most_corrected_patterns: List[Dict] = Field(
        default_factory=list,
        description="Common correction patterns"
    )
    improvement_recommendations: List[str] = Field(
        default_factory=list,
        description="Suggested improvements"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "time_period": "last_30_days",
                "overall_avg_rating": 4.1,
                "total_reports": 120,
                "total_ratings": 480,
                "total_corrections": 35,
                "user_satisfaction": 0.82,
                "improvement_recommendations": [
                    "Improve factual accuracy in financial analysis",
                    "Add more depth to PESTEL framework",
                    "Enhance competitive rivalry insights"
                ]
            }
        }


class FeedbackRequest(BaseModel):
    """Request to submit feedback"""
    report_id: str
    insight_id: str
    feedback_type: FeedbackType
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None

    @validator('rating')
    def rating_required_for_rating_type(cls, v, values):
        if values.get('feedback_type') == FeedbackType.RATING and v is None:
            raise ValueError("Rating is required for RATING feedback type")
        return v


class CorrectionRequest(BaseModel):
    """Request to submit a correction"""
    report_id: str
    insight_id: str
    section: str
    original_text: str
    corrected_text: str
    explanation: Optional[str] = None
    error_category: ErrorCategory = ErrorCategory.OTHER


class LearningPattern(BaseModel):
    """Pattern learned from user feedback"""
    pattern_id: str
    pattern_type: str = Field(
        description="Type of pattern (e.g., 'common_error', 'high_quality_example')"
    )
    framework: Optional[str] = Field(None, description="Associated framework")
    description: str = Field(description="What was learned")
    example_text: str = Field(description="Example demonstrating pattern")
    occurrence_count: int = Field(ge=1, description="How many times observed")
    confidence: float = Field(
        ge=0, le=1,
        description="Confidence in this pattern"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "pattern_id": "pattern_001",
                "pattern_type": "common_error",
                "framework": "porter",
                "description": "Tendency to overlook emerging competitors in competitive rivalry",
                "example_text": "Users frequently correct to add startup competitors",
                "occurrence_count": 12,
                "confidence": 0.85
            }
        }
