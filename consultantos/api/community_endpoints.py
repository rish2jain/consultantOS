"""
Community API endpoints (v0.5.0)
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Security, Query
from consultantos.models.community import (
    CaseStudy,
    CreateCaseStudyRequest,
    UpdateCaseStudyRequest,
    CaseStudyListResponse,
    CaseStudyStatus,
    BestPractice,
    CreateBestPracticeRequest,
    BestPracticeListResponse
)
from consultantos.auth import verify_api_key
import secrets
from datetime import datetime

router = APIRouter(prefix="/community", tags=["community"])

# In-memory stores (in production, use database)
_case_studies: dict[str, CaseStudy] = {}
_best_practices: dict[str, BestPractice] = {}

# Locks for thread-safe operations
import threading
_case_studies_lock = threading.Lock()
_best_practices_lock = threading.Lock()


# Case Studies
@router.post("/case-studies", response_model=CaseStudy, status_code=status.HTTP_201_CREATED)
async def create_case_study(
    request: CreateCaseStudyRequest,
    user_info: dict = Security(verify_api_key)
):
    """Create a new case study"""
    case_study_id = f"casestudy_{secrets.token_urlsafe(16)}"
    
    case_study = CaseStudy(
        case_study_id=case_study_id,
        title=request.title,
        description=request.description,
        company=request.company,
        industry=request.industry,
        frameworks_used=request.frameworks_used or [],
        report_id=request.report_id,
        author_id=user_info["user_id"],
        author_name=user_info.get("name"),
        tags=request.tags or [],
        category=request.category,
        key_insights=request.key_insights or [],
        challenges=request.challenges or [],
        outcomes=request.outcomes
    )
    
    _case_studies[case_study_id] = case_study
    return case_study


@router.get("/case-studies", response_model=CaseStudyListResponse)
async def list_case_studies(
    industry: Optional[str] = None,
    framework: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = "published",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List case studies with filters"""
    filtered = list(_case_studies.values())
    
    # Filter by status
    if status_filter:
        filtered = [cs for cs in filtered if cs.status.value == status_filter]
    
    # Filter by industry
    if industry:
        filtered = [cs for cs in filtered if cs.industry == industry]
    
    # Filter by framework
    if framework:
        filtered = [cs for cs in filtered if framework in cs.frameworks_used]
    
    # Filter by category
    if category:
        filtered = [cs for cs in filtered if cs.category == category]
    
    # Sort by views + likes (engagement)
    filtered.sort(key=lambda cs: cs.views + cs.likes, reverse=True)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return CaseStudyListResponse(
        case_studies=paginated,
        total=len(filtered),
        page=page,
        page_size=page_size
    )


@router.get("/case-studies/{case_study_id}", response_model=CaseStudy)
async def get_case_study(case_study_id: str):
    """Get a specific case study"""
    if case_study_id not in _case_studies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case study not found"
        )
    
    # Thread-safe view increment
    with _case_studies_lock:
        case_study = _case_studies[case_study_id]
        case_study.views += 1
        _case_studies[case_study_id] = case_study
    
    return case_study


@router.put("/case-studies/{case_study_id}", response_model=CaseStudy)
async def update_case_study(
    case_study_id: str,
    request: UpdateCaseStudyRequest,
    user_info: dict = Security(verify_api_key)
):
    """Update a case study (only author)"""
    if case_study_id not in _case_studies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case study not found"
        )
    
    case_study = _case_studies[case_study_id]
    
    if case_study.author_id != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own case studies"
        )
    
    # Update fields
    updates = request.dict(exclude_unset=True)
    for key, value in updates.items():
        setattr(case_study, key, value)
    
    case_study.updated_at = datetime.now().isoformat()
    _case_studies[case_study_id] = case_study
    
    return case_study


@router.post("/case-studies/{case_study_id}/like")
async def like_case_study(
    case_study_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Like a case study"""
    user_id = user_info["user_id"]
    
    if case_study_id not in _case_studies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case study not found"
        )
    
    with _case_studies_lock:
        case_study = _case_studies[case_study_id]
        
        # Check if user already liked
        if user_id in case_study.liked_by:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already liked this case study"
            )
        
        # Add like
        case_study.liked_by.add(user_id)
        case_study.likes += 1
        _case_studies[case_study_id] = case_study
    
    return {"message": "Case study liked", "likes": case_study.likes}


@router.post("/case-studies/{case_study_id}/publish", response_model=CaseStudy)
async def publish_case_study(
    case_study_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Publish a case study"""
    if case_study_id not in _case_studies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case study not found"
        )
    
    case_study = _case_studies[case_study_id]
    
    if case_study.author_id != user_info["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only publish your own case studies"
        )
    
    case_study.status = CaseStudyStatus.PUBLISHED
    case_study.updated_at = datetime.now().isoformat()
    _case_studies[case_study_id] = case_study
    
    return case_study


# Best Practices
@router.post("/best-practices", response_model=BestPractice, status_code=status.HTTP_201_CREATED)
async def create_best_practice(
    request: CreateBestPracticeRequest,
    user_info: dict = Security(verify_api_key)
):
    """Create a new best practice"""
    practice_id = f"practice_{secrets.token_urlsafe(16)}"
    
    practice = BestPractice(
        practice_id=practice_id,
        title=request.title,
        description=request.description,
        category=request.category,
        steps=request.steps or [],
        examples=request.examples or [],
        tags=request.tags or [],
        author_id=user_info["user_id"],
        author_name=user_info.get("name")
    )
    
    _best_practices[practice_id] = practice
    return practice


@router.get("/best-practices", response_model=BestPracticeListResponse)
async def list_best_practices(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """List best practices with filters"""
    filtered = list(_best_practices.values())
    
    # Filter by category
    if category:
        filtered = [p for p in filtered if p.category == category]
    
    # Filter by tag
    if tag:
        filtered = [p for p in filtered if tag in p.tags]
    
    # Sort by upvotes - downvotes (net score)
    filtered.sort(key=lambda p: p.upvotes - p.downvotes, reverse=True)
    
    # Pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return BestPracticeListResponse(
        practices=paginated,
        total=len(filtered),
        page=page,
        page_size=page_size
    )


@router.post("/best-practices/{practice_id}/upvote")
async def upvote_practice(
    practice_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Upvote a best practice"""
    user_id = user_info["user_id"]
    
    if practice_id not in _best_practices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Best practice not found"
        )
    
    with _best_practices_lock:
        practice = _best_practices[practice_id]
        
        # Check if already upvoted
        if user_id in practice.upvoters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already upvoted this practice"
            )
        
        # If previously downvoted, remove downvote
        if user_id in practice.downvoters:
            practice.downvoters.remove(user_id)
            practice.downvotes = max(0, practice.downvotes - 1)
        
        # Add upvote
        practice.upvoters.add(user_id)
        practice.upvotes += 1
        _best_practices[practice_id] = practice
    
    return {"message": "Upvoted", "upvotes": practice.upvotes, "downvotes": practice.downvotes}


@router.post("/best-practices/{practice_id}/downvote")
async def downvote_practice(
    practice_id: str,
    user_info: dict = Security(verify_api_key)
):
    """Downvote a best practice"""
    user_id = user_info["user_id"]
    
    if practice_id not in _best_practices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Best practice not found"
        )
    
    with _best_practices_lock:
        practice = _best_practices[practice_id]
        
        # Check if already downvoted
        if user_id in practice.downvoters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already downvoted this practice"
            )
        
        # If previously upvoted, remove upvote
        if user_id in practice.upvoters:
            practice.upvoters.remove(user_id)
            practice.upvotes = max(0, practice.upvotes - 1)
        
        # Add downvote
        practice.downvoters.add(user_id)
        practice.downvotes += 1
        _best_practices[practice_id] = practice
    
    return {"message": "Downvoted", "upvotes": practice.upvotes, "downvotes": practice.downvotes}

