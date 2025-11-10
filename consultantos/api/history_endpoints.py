"""
API endpoints for analysis history, versioning, and bookmarks
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
import uuid

from consultantos.models import (
    AnalysisVersion,
    CompanyHistory,
    AnalysisComparison,
    Bookmark,
    CreateBookmarkRequest,
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
from consultantos.log_utils import get_logger

router = APIRouter(prefix="/history", tags=["history"])
logger = get_logger(__name__)


# ===== Company History =====

@router.get("/company/{company}", response_model=CompanyHistory)
async def get_company_history(
    company: str,
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> CompanyHistory:
    """
    Get all versions of analyses for a company

    Args:
        company: Company name
        limit: Maximum results
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Company analysis history
    """
    try:
        # Get all analyses for this company
        versions = await db.list_company_analyses(user_id, company, limit)

        history = CompanyHistory(
            company=company,
            versions=versions,
            total_count=len(versions),
        )

        logger.info(
            "company_history_retrieved",
            user_id=user_id,
            company=company,
            count=len(versions)
        )

        return history

    except Exception as e:
        logger.error("get_company_history_failed", company=company, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get company history")


# ===== Analysis Comparison =====

@router.get("/compare", response_model=AnalysisComparison)
async def compare_analyses(
    analysis_id_1: str = Query(..., description="First analysis ID"),
    analysis_id_2: str = Query(..., description="Second analysis ID"),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> AnalysisComparison:
    """
    Compare two analyses side-by-side

    Args:
        analysis_id_1: First analysis ID
        analysis_id_2: Second analysis ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Comparison results
    """
    try:
        # Get both analyses
        analysis1 = await db.get_analysis(analysis_id_1)
        analysis2 = await db.get_analysis(analysis_id_2)

        if not analysis1 or not analysis2:
            raise HTTPException(status_code=404, detail="One or both analyses not found")

        # Verify access
        if analysis1['user_id'] != user_id or analysis2['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Build version objects
        version1 = AnalysisVersion(
            id=analysis_id_1,
            company=analysis1['company'],
            industry=analysis1['industry'],
            user_id=user_id,
            frameworks=analysis1.get('frameworks', []),
            created_at=analysis1['created_at'],
            confidence=analysis1.get('confidence', 0.0),
            key_findings=self._extract_key_findings(analysis1),
            report_url=analysis1.get('report_url'),
        )

        version2 = AnalysisVersion(
            id=analysis_id_2,
            company=analysis2['company'],
            industry=analysis2['industry'],
            user_id=user_id,
            frameworks=analysis2.get('frameworks', []),
            created_at=analysis2['created_at'],
            confidence=analysis2.get('confidence', 0.0),
            key_findings=self._extract_key_findings(analysis2),
            report_url=analysis2.get('report_url'),
        )

        # Calculate differences
        differences = self._calculate_differences(analysis1, analysis2)
        summary = self._generate_comparison_summary(version1, version2, differences)

        comparison = AnalysisComparison(
            analysis_1=version1,
            analysis_2=version2,
            differences=differences,
            summary=summary,
        )

        logger.info(
            "analyses_compared",
            user_id=user_id,
            analysis1=analysis_id_1,
            analysis2=analysis_id_2
        )

        return comparison

    except HTTPException:
        raise
    except Exception as e:
        logger.error("compare_analyses_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to compare analyses")


    def _extract_key_findings(self, analysis: dict) -> List[str]:
        """Extract key findings from analysis"""
        findings = []

        # Extract from executive summary
        if 'executive_summary' in analysis:
            summary = analysis['executive_summary']
            if isinstance(summary, dict) and 'key_findings' in summary:
                findings.extend(summary['key_findings'])

        # Extract from frameworks
        if 'framework_analysis' in analysis:
            frameworks = analysis['framework_analysis']
            if isinstance(frameworks, dict):
                for framework_name, framework_data in frameworks.items():
                    if isinstance(framework_data, dict):
                        # Add first insight from each framework
                        for key, value in framework_data.items():
                            if isinstance(value, str) and len(value) > 10:
                                findings.append(f"{framework_name}: {value[:100]}")
                                break

        return findings[:5]  # Limit to top 5

    def _calculate_differences(self, analysis1: dict, analysis2: dict) -> dict:
        """Calculate differences between analyses"""
        differences = {}

        # Framework differences
        frameworks1 = set(analysis1.get('frameworks', []))
        frameworks2 = set(analysis2.get('frameworks', []))

        differences['added_frameworks'] = list(frameworks2 - frameworks1)
        differences['removed_frameworks'] = list(frameworks1 - frameworks2)
        differences['common_frameworks'] = list(frameworks1 & frameworks2)

        # Time difference
        time_diff = analysis2['created_at'] - analysis1['created_at']
        differences['time_between'] = f"{time_diff.days} days"

        # Confidence change
        conf1 = analysis1.get('confidence', 0.0)
        conf2 = analysis2.get('confidence', 0.0)
        differences['confidence_change'] = conf2 - conf1

        return differences

    def _generate_comparison_summary(
        self,
        v1: AnalysisVersion,
        v2: AnalysisVersion,
        diffs: dict
    ) -> str:
        """Generate human-readable comparison summary"""
        parts = []

        parts.append(f"Comparing analyses of {v1.company} from {v1.created_at.strftime('%Y-%m-%d')} and {v2.created_at.strftime('%Y-%m-%d')}")

        if diffs.get('added_frameworks'):
            parts.append(f"Added frameworks: {', '.join(diffs['added_frameworks'])}")

        if diffs.get('removed_frameworks'):
            parts.append(f"Removed frameworks: {', '.join(diffs['removed_frameworks'])}")

        if diffs.get('confidence_change'):
            change = diffs['confidence_change']
            if change > 0:
                parts.append(f"Confidence improved by {change:.2f}")
            elif change < 0:
                parts.append(f"Confidence decreased by {abs(change):.2f}")

        return ". ".join(parts)


# ===== Bookmarks =====

@router.post("/bookmarks", response_model=Bookmark, status_code=201)
async def create_bookmark(
    analysis_id: str = Query(..., description="Analysis ID to bookmark"),
    request: CreateBookmarkRequest = None,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> Bookmark:
    """
    Bookmark an analysis

    Args:
        analysis_id: Analysis to bookmark
        request: Bookmark metadata
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Created bookmark
    """
    try:
        # Get analysis
        analysis = await db.get_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Verify access
        if analysis['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if already bookmarked
        existing = await db.get_bookmark(user_id, analysis_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already bookmarked")

        # Create bookmark
        bookmark = Bookmark(
            id=str(uuid.uuid4()),
            user_id=user_id,
            analysis_id=analysis_id,
            company=analysis['company'],
            tags=request.tags if request else [],
            notes=request.notes if request else None,
        )

        await db.create_bookmark(bookmark)

        logger.info("bookmark_created", user_id=user_id, analysis_id=analysis_id)

        return bookmark

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_bookmark_failed", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create bookmark")


@router.get("/bookmarks", response_model=List[Bookmark])
async def list_bookmarks(
    tags: List[str] = Query(None, description="Filter by tags"),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> List[Bookmark]:
    """
    List user's bookmarks

    Args:
        tags: Filter by tags
        user_id: Authenticated user ID
        db: Database service

    Returns:
        List of bookmarks
    """
    try:
        bookmarks = await db.list_bookmarks(user_id, tags)

        logger.info("bookmarks_listed", user_id=user_id, count=len(bookmarks))

        return bookmarks

    except Exception as e:
        logger.error("list_bookmarks_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list bookmarks")


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
):
    """
    Delete a bookmark

    Args:
        bookmark_id: Bookmark ID
        user_id: Authenticated user ID
        db: Database service
    """
    try:
        # Get bookmark
        bookmark = await db.get_bookmark_by_id(bookmark_id)
        if not bookmark:
            raise HTTPException(status_code=404, detail="Bookmark not found")

        # Verify ownership
        if bookmark.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete
        await db.delete_bookmark(bookmark_id)

        logger.info("bookmark_deleted", user_id=user_id, bookmark_id=bookmark_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_bookmark_failed", bookmark_id=bookmark_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete bookmark")
