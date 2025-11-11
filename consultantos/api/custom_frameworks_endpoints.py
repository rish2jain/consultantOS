"""
API endpoints for custom framework builder
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid

from consultantos.models import (
    CustomFramework,
    CreateCustomFrameworkRequest,
    UpdateCustomFrameworkRequest,
    RateFrameworkRequest,
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
import logging

router = APIRouter(prefix="/custom-frameworks", tags=["custom-frameworks"])
logger = logging.getLogger(__name__)


@router.post("", response_model=CustomFramework, status_code=201)
async def create_custom_framework(
    request: CreateCustomFrameworkRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> CustomFramework:
    """
    Create a custom analysis framework

    Args:
        request: Framework definition
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Created framework
    """
    try:
        # Validate response schema is valid JSON schema
        if not isinstance(request.response_schema, dict):
            raise HTTPException(
                status_code=400,
                detail="response_schema must be a valid JSON schema object"
            )

        # Create framework
        framework = CustomFramework(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=request.name,
            description=request.description,
            prompt_template=request.prompt_template,
            response_schema=request.response_schema,
            is_public=request.is_public,
            category=request.category,
            tags=request.tags,
        )

        # Store in database
        await db.create_custom_framework(framework)

        logger.info(
            "custom_framework_created",
            framework_id=framework.id,
            user_id=user_id,
            is_public=framework.is_public
        )

        return framework

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_framework_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create framework")


@router.get("", response_model=List[CustomFramework])
async def list_custom_frameworks(
    user_id: str = Depends(get_current_user),
    include_public: bool = Query(True, description="Include public frameworks"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db = Depends(get_db_service)
) -> List[CustomFramework]:
    """
    List user's custom frameworks (and optionally public ones)

    Args:
        user_id: Authenticated user ID
        include_public: Include community public frameworks
        category: Filter by category
        db: Database service

    Returns:
        List of frameworks
    """
    try:
        # Get user's frameworks
        user_frameworks = await db.list_custom_frameworks(user_id, category)

        # Optionally include public frameworks
        if include_public:
            public_frameworks = await db.list_public_frameworks(category)
            # Deduplicate (user's own public frameworks already in user_frameworks)
            user_framework_ids = {f.id for f in user_frameworks}
            for framework in public_frameworks:
                if framework.id not in user_framework_ids:
                    user_frameworks.append(framework)

        # Sort by usage_count for discovery
        user_frameworks.sort(key=lambda x: x.usage_count, reverse=True)

        return user_frameworks

    except Exception as e:
        logger.error("list_frameworks_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list frameworks")


@router.get("/community", response_model=List[CustomFramework])
async def list_community_frameworks(
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query("rating", description="Sort by: rating, usage, recent"),
    limit: int = Query(20, ge=1, le=100),
    db = Depends(get_db_service)
) -> List[CustomFramework]:
    """
    Browse community-shared frameworks

    Args:
        category: Filter by category
        sort_by: Sort order
        limit: Maximum results
        db: Database service

    Returns:
        List of public frameworks
    """
    try:
        frameworks = await db.list_public_frameworks(category)

        # Sort
        if sort_by == "rating":
            frameworks.sort(key=lambda x: (x.rating, x.rating_count), reverse=True)
        elif sort_by == "usage":
            frameworks.sort(key=lambda x: x.usage_count, reverse=True)
        elif sort_by == "recent":
            frameworks.sort(key=lambda x: x.created_at, reverse=True)

        return frameworks[:limit]

    except Exception as e:
        logger.error("list_community_frameworks_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list community frameworks")


@router.get("/{framework_id}", response_model=CustomFramework)
async def get_custom_framework(
    framework_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> CustomFramework:
    """
    Get a custom framework

    Args:
        framework_id: Framework ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Framework details
    """
    try:
        framework = await db.get_custom_framework(framework_id)

        if not framework:
            raise HTTPException(status_code=404, detail="Framework not found")

        # Check access (must be owner or public)
        if framework.user_id != user_id and not framework.is_public:
            raise HTTPException(status_code=403, detail="Access denied")

        return framework

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_framework_failed", framework_id=framework_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get framework")


@router.patch("/{framework_id}", response_model=CustomFramework)
async def update_custom_framework(
    framework_id: str,
    request: UpdateCustomFrameworkRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> CustomFramework:
    """
    Update a custom framework

    Args:
        framework_id: Framework ID
        request: Update data
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Updated framework
    """
    try:
        # Get existing framework
        framework = await db.get_custom_framework(framework_id)

        if not framework:
            raise HTTPException(status_code=404, detail="Framework not found")

        # Verify ownership
        if framework.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only owner can update")

        # Update fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(framework, field, value)

        framework.updated_at = datetime.utcnow()

        # Save
        await db.update_custom_framework(framework)

        logger.info("framework_updated", framework_id=framework_id, user_id=user_id)

        return framework

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_framework_failed", framework_id=framework_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update framework")


@router.delete("/{framework_id}", status_code=204)
async def delete_custom_framework(
    framework_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
):
    """
    Delete a custom framework

    Args:
        framework_id: Framework ID
        user_id: Authenticated user ID
        db: Database service
    """
    try:
        # Get framework
        framework = await db.get_custom_framework(framework_id)

        if not framework:
            raise HTTPException(status_code=404, detail="Framework not found")

        # Verify ownership
        if framework.user_id != user_id:
            raise HTTPException(status_code=403, detail="Only owner can delete")

        # Delete
        await db.delete_custom_framework(framework_id)

        logger.info("framework_deleted", framework_id=framework_id, user_id=user_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_framework_failed", framework_id=framework_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete framework")


@router.post("/{framework_id}/rate", response_model=CustomFramework)
async def rate_framework(
    framework_id: str,
    request: RateFrameworkRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> CustomFramework:
    """
    Rate a public framework

    Args:
        framework_id: Framework ID
        request: Rating data
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Updated framework with new rating
    """
    try:
        # Get framework
        framework = await db.get_custom_framework(framework_id)

        if not framework:
            raise HTTPException(status_code=404, detail="Framework not found")

        # Must be public to rate
        if not framework.is_public:
            raise HTTPException(status_code=400, detail="Can only rate public frameworks")

        # Can't rate own framework
        if framework.user_id == user_id:
            raise HTTPException(status_code=400, detail="Cannot rate your own framework")

        # Store rating
        await db.add_framework_rating(framework_id, user_id, request.rating, request.review)

        # Update framework average rating
        ratings = await db.get_framework_ratings(framework_id)
        framework.rating = sum(r['rating'] for r in ratings) / len(ratings)
        framework.rating_count = len(ratings)

        await db.update_custom_framework(framework)

        logger.info(
            "framework_rated",
            framework_id=framework_id,
            user_id=user_id,
            rating=request.rating
        )

        return framework

    except HTTPException:
        raise
    except Exception as e:
        logger.error("rate_framework_failed", framework_id=framework_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to rate framework")


@router.post("/{framework_id}/use", status_code=200)
async def use_framework(
    framework_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> dict:
    """
    Increment usage count when framework is used

    Args:
        framework_id: Framework ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Success message
    """
    try:
        # Get framework
        framework = await db.get_custom_framework(framework_id)

        if not framework:
            raise HTTPException(status_code=404, detail="Framework not found")

        # Increment usage count
        framework.usage_count += 1
        await db.update_custom_framework(framework)

        logger.info("framework_used", framework_id=framework_id, user_id=user_id)

        return {"message": "Usage recorded", "usage_count": framework.usage_count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("use_framework_failed", framework_id=framework_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to record usage")
