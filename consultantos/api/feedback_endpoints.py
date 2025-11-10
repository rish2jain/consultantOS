"""
Feedback API Endpoints

Endpoints for user feedback, insight ratings, corrections, and quality reporting.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import uuid
from datetime import datetime, timedelta

from consultantos.models.feedback import (
    InsightRating,
    InsightCorrection,
    QualityMetrics,
    QualityReport,
    FeedbackRequest,
    CorrectionRequest,
    FrameworkQualityStats,
    ErrorCategory
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
from consultantos.log_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/insights/{insight_id}/rating", response_model=InsightRating)
async def rate_insight(
    insight_id: str,
    rating: int = Query(..., ge=1, le=5, description="Rating from 1-5 stars"),
    feedback_text: Optional[str] = None,
    report_id: str = Query(..., description="Parent report ID"),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> InsightRating:
    """
    Rate an individual insight with 1-5 stars.

    This allows users to provide feedback on specific insights within a report,
    helping the system learn which insights are most valuable.
    """
    try:
        # Create rating record
        rating_obj = InsightRating(
            id=f"rating_{uuid.uuid4().hex[:12]}",
            insight_id=insight_id,
            report_id=report_id,
            user_id=user_id,
            rating=rating,
            feedback_text=feedback_text,
            created_at=datetime.utcnow()
        )

        # Store in database
        await db.store_rating(rating_obj)

        logger.info(
            "insight_rated",
            insight_id=insight_id,
            report_id=report_id,
            rating=rating,
            user_id=user_id
        )

        return rating_obj

    except Exception as e:
        logger.error(
            "rating_failed",
            insight_id=insight_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to submit rating"
        )


@router.post("/insights/{insight_id}/correction", response_model=InsightCorrection)
async def submit_correction(
    insight_id: str,
    correction: CorrectionRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> InsightCorrection:
    """
    Submit a correction for an incorrect or incomplete insight.

    Users can provide corrected text and explanation, which feeds into
    the learning system to improve future analyses.
    """
    try:
        # Create correction record
        correction_obj = InsightCorrection(
            id=f"correction_{uuid.uuid4().hex[:12]}",
            insight_id=insight_id,
            report_id=correction.report_id,
            user_id=user_id,
            section=correction.section,
            original_text=correction.original_text,
            corrected_text=correction.corrected_text,
            explanation=correction.explanation,
            error_category=correction.error_category,
            validated=False,
            incorporated=False,
            created_at=datetime.utcnow()
        )

        # Store in database
        await db.store_correction(correction_obj)

        logger.info(
            "correction_submitted",
            insight_id=insight_id,
            report_id=correction.report_id,
            error_category=correction.error_category,
            user_id=user_id
        )

        return correction_obj

    except Exception as e:
        logger.error(
            "correction_failed",
            insight_id=insight_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to submit correction"
        )


@router.get("/reports/{report_id}/quality", response_model=QualityMetrics)
async def get_report_quality(
    report_id: str,
    db = Depends(get_db_service)
) -> QualityMetrics:
    """
    Get aggregated quality metrics for a specific report.

    Returns ratings, corrections, and derived quality scores.
    """
    try:
        # Fetch all ratings for this report
        ratings = await db.get_ratings_for_report(report_id)
        corrections = await db.get_corrections_for_report(report_id)

        if not ratings and not corrections:
            # No feedback yet
            return QualityMetrics(
                report_id=report_id,
                avg_rating=0.0,
                total_ratings=0,
                corrections_count=0,
                user_satisfaction=0.0,
                rating_distribution={},
                error_categories={},
                frameworks_quality={}
            )

        # Calculate metrics
        total_ratings = len(ratings)
        avg_rating = sum(r.rating for r in ratings) / total_ratings if total_ratings > 0 else 0.0

        # Rating distribution
        rating_dist = {i: 0 for i in range(1, 6)}
        for r in ratings:
            rating_dist[r.rating] = rating_dist.get(r.rating, 0) + 1

        # Error categories
        error_cats = {}
        for c in corrections:
            cat = c.error_category.value
            error_cats[cat] = error_cats.get(cat, 0) + 1

        # User satisfaction (derived from ratings)
        # Formula: (weighted sum of ratings - min possible) / (max possible - min possible)
        weighted_sum = sum(r.rating * (r.rating / 5.0) for r in ratings)
        max_possible = total_ratings * 5
        user_satisfaction = weighted_sum / max_possible if max_possible > 0 else 0.0

        # Framework quality (requires insight metadata - placeholder for now)
        frameworks_quality = {}

        metrics = QualityMetrics(
            report_id=report_id,
            avg_rating=round(avg_rating, 2),
            total_ratings=total_ratings,
            corrections_count=len(corrections),
            user_satisfaction=round(user_satisfaction, 2),
            rating_distribution=rating_dist,
            error_categories=error_cats,
            frameworks_quality=frameworks_quality,
            computed_at=datetime.utcnow()
        )

        logger.info(
            "quality_metrics_computed",
            report_id=report_id,
            avg_rating=metrics.avg_rating,
            user_satisfaction=metrics.user_satisfaction
        )

        return metrics

    except Exception as e:
        logger.error(
            "quality_metrics_failed",
            report_id=report_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to compute quality metrics"
        )


@router.get("/quality/report", response_model=QualityReport)
async def get_quality_report(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db = Depends(get_db_service)
) -> QualityReport:
    """
    Generate comprehensive quality report across all analyses.

    Used by admins to track system quality over time and identify
    areas for improvement.
    """
    try:
        # Calculate time window
        start_date = datetime.utcnow() - timedelta(days=days)

        # Fetch all ratings and corrections in time window
        all_ratings = await db.get_ratings_since(start_date)
        all_corrections = await db.get_corrections_since(start_date)

        # Overall metrics
        total_reports = len(set(r.report_id for r in all_ratings))
        total_ratings = len(all_ratings)
        total_corrections = len(all_corrections)

        overall_avg_rating = (
            sum(r.rating for r in all_ratings) / total_ratings
            if total_ratings > 0 else 0.0
        )

        # User satisfaction
        weighted_sum = sum(r.rating * (r.rating / 5.0) for r in all_ratings)
        max_possible = total_ratings * 5
        user_satisfaction = weighted_sum / max_possible if max_possible > 0 else 0.0

        # Framework statistics (placeholder - would need insight metadata)
        framework_stats = []

        # Top rated insights (placeholder)
        top_rated_insights = []

        # Common correction patterns
        correction_patterns = []
        error_categories = {}
        for c in all_corrections:
            cat = c.error_category.value
            error_categories[cat] = error_categories.get(cat, 0) + 1

        for cat, count in sorted(error_categories.items(), key=lambda x: x[1], reverse=True)[:5]:
            correction_patterns.append({
                "error_category": cat,
                "count": count,
                "percentage": round(count / total_corrections * 100, 1) if total_corrections > 0 else 0
            })

        # Generate improvement recommendations
        recommendations = _generate_recommendations(
            overall_avg_rating,
            correction_patterns,
            user_satisfaction
        )

        report = QualityReport(
            time_period=f"last_{days}_days",
            overall_avg_rating=round(overall_avg_rating, 2),
            total_reports=total_reports,
            total_ratings=total_ratings,
            total_corrections=total_corrections,
            user_satisfaction=round(user_satisfaction, 2),
            framework_stats=framework_stats,
            top_rated_insights=top_rated_insights,
            most_corrected_patterns=correction_patterns,
            improvement_recommendations=recommendations,
            generated_at=datetime.utcnow()
        )

        logger.info(
            "quality_report_generated",
            days=days,
            avg_rating=report.overall_avg_rating,
            user_satisfaction=report.user_satisfaction
        )

        return report

    except Exception as e:
        logger.error(
            "quality_report_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate quality report"
        )


@router.get("/corrections/pending", response_model=List[InsightCorrection])
async def get_pending_corrections(
    limit: int = Query(50, ge=1, le=500),
    db = Depends(get_db_service),
    user_id: str = Depends(get_current_user)
) -> List[InsightCorrection]:
    """
    Get pending corrections awaiting admin review.

    Admin endpoint for reviewing and validating user-submitted corrections.
    """
    try:
        # Check if user is admin (placeholder - implement proper admin check)
        # if not await db.is_admin(user_id):
        #     raise HTTPException(status_code=403, detail="Admin access required")

        corrections = await db.get_pending_corrections(limit=limit)

        logger.info(
            "pending_corrections_fetched",
            count=len(corrections),
            user_id=user_id
        )

        return corrections

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "pending_corrections_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch pending corrections"
        )


@router.post("/corrections/{correction_id}/validate")
async def validate_correction(
    correction_id: str,
    approved: bool = Query(..., description="Whether to approve correction"),
    admin_notes: Optional[str] = None,
    db = Depends(get_db_service),
    user_id: str = Depends(get_current_user)
) -> dict:
    """
    Validate a user-submitted correction.

    Admin endpoint to approve or reject corrections, which then
    feed into the learning system.
    """
    try:
        # Check if user is admin (placeholder)
        # if not await db.is_admin(user_id):
        #     raise HTTPException(status_code=403, detail="Admin access required")

        # Update correction status
        await db.update_correction(
            correction_id=correction_id,
            validated=True,
            validated_at=datetime.utcnow(),
            admin_notes=admin_notes
        )

        logger.info(
            "correction_validated",
            correction_id=correction_id,
            approved=approved,
            admin_user_id=user_id
        )

        return {
            "correction_id": correction_id,
            "validated": True,
            "approved": approved,
            "message": "Correction validated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "correction_validation_failed",
            correction_id=correction_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to validate correction"
        )


def _generate_recommendations(
    avg_rating: float,
    correction_patterns: List[dict],
    user_satisfaction: float
) -> List[str]:
    """Generate improvement recommendations based on metrics"""
    recommendations = []

    # Rating-based recommendations
    if avg_rating < 3.5:
        recommendations.append(
            "Overall rating is below target (3.5). Prioritize quality improvements across all frameworks."
        )
    elif avg_rating < 4.0:
        recommendations.append(
            "Rating is acceptable but has room for improvement. Focus on consistency."
        )

    # Satisfaction-based recommendations
    if user_satisfaction < 0.7:
        recommendations.append(
            "User satisfaction is low. Review recent corrections and user feedback for common issues."
        )

    # Correction pattern-based recommendations
    if correction_patterns:
        top_error = correction_patterns[0]
        error_cat = top_error.get("error_category", "")
        count = top_error.get("count", 0)

        if error_cat == "factual" and count > 5:
            recommendations.append(
                f"High number of factual errors ({count}). Improve data validation and fact-checking."
            )
        elif error_cat == "relevance" and count > 5:
            recommendations.append(
                f"Relevance issues detected ({count}). Refine prompts to focus on core strategic insights."
            )
        elif error_cat == "depth" and count > 5:
            recommendations.append(
                f"Depth issues identified ({count}). Adjust prompts to provide more detailed analysis."
            )

    # Default recommendation if all metrics are good
    if not recommendations:
        recommendations.append(
            "Quality metrics are strong. Continue monitoring and maintain current standards."
        )

    return recommendations
