"""
API endpoints for saved searches and monitoring
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid

from consultantos.models import (
    SavedSearch,
    CreateSavedSearchRequest,
    UpdateSavedSearchRequest,
    AnalysisRequest,
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator
import logging

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])
logger = logging.getLogger(__name__)


@router.post("", response_model=SavedSearch, status_code=201)
async def create_saved_search(
    request: CreateSavedSearchRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> SavedSearch:
    """
    Create a saved search configuration

    Args:
        request: Search configuration
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Created saved search
    """
    try:
        # Create saved search
        saved_search = SavedSearch(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=request.name,
            description=request.description,
            company=request.company,
            industry=request.industry,
            frameworks=request.frameworks,
            depth=request.depth,
            auto_run=request.auto_run,
            schedule=request.schedule,
        )

        # Store in database
        await db.create_saved_search(saved_search)

        logger.info(
            "saved_search_created",
            user_id=user_id,
            search_id=saved_search.id,
            company=request.company,
            auto_run=request.auto_run
        )

        return saved_search

    except Exception as e:
        logger.error("create_saved_search_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create saved search")


@router.get("", response_model=List[SavedSearch])
async def list_saved_searches(
    user_id: str = Depends(get_current_user),
    auto_run_only: bool = Query(False, description="Only return auto-run searches"),
    db = Depends(get_db_service)
) -> List[SavedSearch]:
    """
    List all user's saved searches

    Args:
        user_id: Authenticated user ID
        auto_run_only: Filter for auto-run searches only
        db: Database service

    Returns:
        List of saved searches
    """
    try:
        searches = await db.list_saved_searches(user_id, auto_run_only)
        return searches

    except Exception as e:
        logger.error("list_saved_searches_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list saved searches")


@router.get("/{search_id}", response_model=SavedSearch)
async def get_saved_search(
    search_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> SavedSearch:
    """
    Get a specific saved search

    Args:
        search_id: Saved search ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Saved search details
    """
    try:
        search = await db.get_saved_search(search_id)

        if not search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        # Verify ownership
        if search.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return search

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_saved_search_failed", search_id=search_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get saved search")


@router.patch("/{search_id}", response_model=SavedSearch)
async def update_saved_search(
    search_id: str,
    request: UpdateSavedSearchRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> SavedSearch:
    """
    Update a saved search

    Args:
        search_id: Saved search ID
        request: Update data
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Updated saved search
    """
    try:
        # Get existing search
        search = await db.get_saved_search(search_id)

        if not search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        # Verify ownership
        if search.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(search, field, value)

        search.updated_at = datetime.utcnow()

        # Save to database
        await db.update_saved_search(search)

        logger.info("saved_search_updated", search_id=search_id, user_id=user_id)

        return search

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_saved_search_failed", search_id=search_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update saved search")


@router.delete("/{search_id}", status_code=204)
async def delete_saved_search(
    search_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
):
    """
    Delete a saved search

    Args:
        search_id: Saved search ID
        user_id: Authenticated user ID
        db: Database service
    """
    try:
        # Get existing search
        search = await db.get_saved_search(search_id)

        if not search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        # Verify ownership
        if search.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Delete from database
        await db.delete_saved_search(search_id)

        logger.info("saved_search_deleted", search_id=search_id, user_id=user_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_saved_search_failed", search_id=search_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete saved search")


@router.post("/{search_id}/run", status_code=202)
async def run_saved_search(
    search_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service),
    orchestrator: AnalysisOrchestrator = Depends()
) -> dict:
    """
    Run a saved search and create new analysis

    Args:
        search_id: Saved search ID
        user_id: Authenticated user ID
        db: Database service
        orchestrator: Analysis orchestrator

    Returns:
        Job details for async execution
    """
    try:
        # Get saved search
        search = await db.get_saved_search(search_id)

        if not search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        # Verify ownership
        if search.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Create analysis request from saved search
        analysis_request = AnalysisRequest(
            company=search.company,
            industry=search.industry,
            frameworks=search.frameworks,
            depth=search.depth,
        )

        # Queue async analysis
        from consultantos.jobs.queue import job_queue
        job_id = await job_queue.enqueue(
            orchestrator.analyze,
            analysis_request,
            user_id=user_id,
            source="saved_search",
            source_id=search_id
        )

        # Update run statistics
        search.last_run = datetime.utcnow()
        search.run_count += 1
        await db.update_saved_search(search)

        logger.info(
            "saved_search_executed",
            search_id=search_id,
            user_id=user_id,
            job_id=job_id,
            company=search.company
        )

        return {
            "job_id": job_id,
            "search_id": search_id,
            "status": "queued",
            "message": f"Analysis for {search.company} queued"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("run_saved_search_failed", search_id=search_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to run saved search")


@router.get("/{search_id}/history")
async def get_search_history(
    search_id: str,
    limit: int = Query(10, ge=1, le=100),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> dict:
    """
    Get execution history for a saved search

    Args:
        search_id: Saved search ID
        limit: Maximum number of results
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Execution history
    """
    try:
        # Get saved search
        search = await db.get_saved_search(search_id)

        if not search:
            raise HTTPException(status_code=404, detail="Saved search not found")

        # Verify ownership
        if search.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get analysis history for this search
        history = await db.get_saved_search_history(search_id, limit)

        return {
            "search_id": search_id,
            "search_name": search.name,
            "company": search.company,
            "total_runs": search.run_count,
            "last_run": search.last_run,
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_search_history_failed", search_id=search_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get search history")
