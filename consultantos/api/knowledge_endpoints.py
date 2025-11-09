"""
API endpoints for personal knowledge base
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from consultantos.models import (
    KnowledgeItem,
    Timeline,
    KnowledgeGraph,
    SearchKBRequest,
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
from consultantos.knowledge.personal_kb import PersonalKnowledgeBase
import logging

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)


@router.post("/search", response_model=List[KnowledgeItem])
async def search_knowledge_base(
    request: SearchKBRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> List[KnowledgeItem]:
    """
    Search across all user's analyses

    Args:
        request: Search query and filters
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Ranked knowledge items
    """
    try:
        kb = PersonalKnowledgeBase(db)
        results = await kb.search_kb(user_id, request)

        logger.info(
            "kb_searched",
            user_id=user_id,
            query=request.query,
            results=len(results)
        )

        return results

    except Exception as e:
        logger.error("search_kb_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to search knowledge base")


@router.get("/timeline/{company}", response_model=Timeline)
async def get_company_timeline(
    company: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> Timeline:
    """
    Show how analysis of company changed over time

    Args:
        company: Company name
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Timeline of analyses
    """
    try:
        kb = PersonalKnowledgeBase(db)
        timeline = await kb.get_timeline(company, user_id)

        logger.info("timeline_retrieved", user_id=user_id, company=company)

        return timeline

    except Exception as e:
        logger.error("get_timeline_failed", company=company, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get timeline")


@router.get("/connections/{company}", response_model=KnowledgeGraph)
async def get_company_connections(
    company: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> KnowledgeGraph:
    """
    Show connections between companies/industries user analyzed

    Args:
        company: Starting company
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Knowledge graph
    """
    try:
        kb = PersonalKnowledgeBase(db)
        graph = await kb.get_connections(company, user_id)

        logger.info(
            "connections_retrieved",
            user_id=user_id,
            company=company,
            nodes=len(graph.nodes),
            edges=len(graph.edges)
        )

        return graph

    except Exception as e:
        logger.error("get_connections_failed", company=company, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get connections")


@router.get("/stats", response_model=dict)
async def get_kb_stats(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> dict:
    """
    Get knowledge base statistics

    Args:
        user_id: Authenticated user ID
        db: Database service

    Returns:
        KB statistics
    """
    try:
        # Get all knowledge items
        items = await db.list_knowledge_items(user_id)

        # Calculate statistics
        total_analyses = len(items)
        companies_analyzed = len(set(item.company for item in items))
        industries_covered = len(set(item.industry for item in items))

        # Framework usage
        framework_counts = {}
        for item in items:
            for framework in item.frameworks_used:
                framework_counts[framework] = framework_counts.get(framework, 0) + 1

        # Recent activity
        if items:
            items.sort(key=lambda x: x.created_at, reverse=True)
            most_recent = items[0].created_at
            oldest = items[-1].created_at
        else:
            most_recent = None
            oldest = None

        stats = {
            "total_analyses": total_analyses,
            "companies_analyzed": companies_analyzed,
            "industries_covered": industries_covered,
            "framework_usage": framework_counts,
            "most_recent_analysis": most_recent,
            "first_analysis": oldest,
        }

        logger.info("kb_stats_retrieved", user_id=user_id)

        return stats

    except Exception as e:
        logger.error("get_kb_stats_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get KB stats")
