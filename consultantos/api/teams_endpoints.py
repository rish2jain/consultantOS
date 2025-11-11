"""
API endpoints for team collaboration features
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
import uuid

from consultantos.models import (
    Team,
    TeamMember,
    TeamRole,
    CreateTeamRequest,
    InviteMemberRequest,
    Comment,
    CreateCommentRequest,
)
from consultantos.auth import get_current_user
from consultantos.database import get_db_service
import logging
# Email service is optional
try:
    from consultantos.services.email import send_team_invite
except ImportError:
    def send_team_invite(*args, **kwargs):
        logger.warning("Email service not available - team invite email not sent")
        return None

router = APIRouter(prefix="/teams", tags=["teams"])
logger = logging.getLogger(__name__)


# ===== Team Management =====

@router.post("", response_model=Team, status_code=201)
async def create_team(
    request: CreateTeamRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> Team:
    """
    Create a new team workspace

    Args:
        request: Team creation request
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Created team
    """
    try:
        # Create team
        team = Team(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            owner_id=user_id,
            plan=request.plan,
        )

        # Set plan limits
        if team.plan.value == "free":
            team.max_members = 5
            team.max_analyses_per_month = 50
        elif team.plan.value == "pro":
            team.max_members = 20
            team.max_analyses_per_month = 500
        else:  # enterprise
            team.max_members = 999999
            team.max_analyses_per_month = 999999

        # Store team
        await db.create_team(team)

        # Add creator as owner
        owner_member = TeamMember(
            id=str(uuid.uuid4()),
            team_id=team.id,
            user_id=user_id,
            email=(await db.get_user(user_id)).email,
            role=TeamRole.OWNER,
        )
        await db.add_team_member(owner_member)

        logger.info("team_created", team_id=team.id, owner_id=user_id, plan=team.plan)

        return team

    except Exception as e:
        logger.error("create_team_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create team")


@router.get("", response_model=List[Team])
async def list_teams(
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> List[Team]:
    """
    List teams user is a member of

    Args:
        user_id: Authenticated user ID
        db: Database service

    Returns:
        List of teams
    """
    try:
        teams = await db.list_user_teams(user_id)
        return teams

    except Exception as e:
        logger.error("list_teams_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list teams")


@router.get("/{team_id}", response_model=Team)
async def get_team(
    team_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> Team:
    """
    Get team details

    Args:
        team_id: Team ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Team details
    """
    try:
        # Verify membership
        member = await db.get_team_member(team_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        team = await db.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return team

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_team_failed", team_id=team_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get team")


# ===== Team Members =====

@router.post("/{team_id}/members", response_model=TeamMember, status_code=201)
async def invite_member(
    team_id: str,
    request: InviteMemberRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> TeamMember:
    """
    Invite a member to the team

    Args:
        team_id: Team ID
        request: Invite request
        user_id: Authenticated user ID (inviter)
        db: Database service

    Returns:
        Created team member
    """
    try:
        # Verify admin access
        inviter = await db.get_team_member(team_id, user_id)
        if not inviter or inviter.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Admin access required")

        # Get team
        team = await db.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Check member limit
        if team.member_count >= team.max_members:
            raise HTTPException(
                status_code=400,
                detail=f"Team member limit reached ({team.max_members})"
            )

        # Check if user already member
        invited_user = await db.get_user_by_email(request.email)
        if invited_user:
            existing = await db.get_team_member(team_id, invited_user.id)
            if existing:
                raise HTTPException(status_code=400, detail="User already a member")

        # Create invitation (or add directly if user exists)
        if invited_user:
            # User exists, add directly
            member = TeamMember(
                id=str(uuid.uuid4()),
                team_id=team_id,
                user_id=invited_user.id,
                email=request.email,
                role=request.role,
                invited_by=user_id,
            )
            await db.add_team_member(member)

            # Update team member count
            team.member_count += 1
            await db.update_team(team)

        else:
            # User doesn't exist, create pending invitation
            member = TeamMember(
                id=str(uuid.uuid4()),
                team_id=team_id,
                user_id="",  # Will be filled when user accepts
                email=request.email,
                role=request.role,
                invited_by=user_id,
            )
            await db.create_team_invitation(member)

        # Send invitation email
        await send_team_invite(request.email, team.name, inviter.email)

        logger.info(
            "team_member_invited",
            team_id=team_id,
            email=request.email,
            role=request.role,
            invited_by=user_id
        )

        return member

    except HTTPException:
        raise
    except Exception as e:
        logger.error("invite_member_failed", team_id=team_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to invite member")


@router.get("/{team_id}/members", response_model=List[TeamMember])
async def list_team_members(
    team_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> List[TeamMember]:
    """
    List team members

    Args:
        team_id: Team ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        List of team members
    """
    try:
        # Verify membership
        member = await db.get_team_member(team_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        members = await db.list_team_members(team_id)
        return members

    except HTTPException:
        raise
    except Exception as e:
        logger.error("list_team_members_failed", team_id=team_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list team members")


@router.delete("/{team_id}/members/{member_user_id}", status_code=204)
async def remove_member(
    team_id: str,
    member_user_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
):
    """
    Remove a team member

    Args:
        team_id: Team ID
        member_user_id: User ID to remove
        user_id: Authenticated user ID
        db: Database service
    """
    try:
        # Verify admin access
        requester = await db.get_team_member(team_id, user_id)
        if not requester or requester.role not in [TeamRole.OWNER, TeamRole.ADMIN]:
            raise HTTPException(status_code=403, detail="Admin access required")

        # Can't remove owner
        target = await db.get_team_member(team_id, member_user_id)
        if target and target.role == TeamRole.OWNER:
            raise HTTPException(status_code=400, detail="Cannot remove team owner")

        # Remove member
        await db.remove_team_member(team_id, member_user_id)

        # Update team count
        team = await db.get_team(team_id)
        team.member_count -= 1
        await db.update_team(team)

        logger.info(
            "team_member_removed",
            team_id=team_id,
            removed_user=member_user_id,
            removed_by=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("remove_member_failed", team_id=team_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to remove member")


# ===== Team Analyses =====

@router.get("/{team_id}/analyses")
async def list_team_analyses(
    team_id: str,
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> dict:
    """
    List analyses shared with team

    Args:
        team_id: Team ID
        limit: Maximum results
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Team analyses
    """
    try:
        # Verify membership
        member = await db.get_team_member(team_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        analyses = await db.list_team_analyses(team_id, limit)

        return {
            "team_id": team_id,
            "total_count": len(analyses),
            "analyses": analyses
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("list_team_analyses_failed", team_id=team_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list team analyses")


# ===== Comments =====

@router.post("/{team_id}/analyses/{analysis_id}/comments", response_model=Comment, status_code=201)
async def create_comment(
    team_id: str,
    analysis_id: str,
    request: CreateCommentRequest,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> Comment:
    """
    Add comment to analysis

    Args:
        team_id: Team ID
        analysis_id: Analysis ID
        request: Comment content
        user_id: Authenticated user ID
        db: Database service

    Returns:
        Created comment
    """
    try:
        # Verify membership
        member = await db.get_team_member(team_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        # Get user email
        user = await db.get_user(user_id)

        # Create comment
        comment = Comment(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            team_id=team_id,
            user_id=user_id,
            user_email=user.email,
            text=request.text,
            parent_id=request.parent_id,
        )

        await db.create_comment(comment)

        logger.info(
            "comment_created",
            team_id=team_id,
            analysis_id=analysis_id,
            user_id=user_id
        )

        return comment

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_comment_failed", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create comment")


@router.get("/{team_id}/analyses/{analysis_id}/comments", response_model=List[Comment])
async def list_comments(
    team_id: str,
    analysis_id: str,
    user_id: str = Depends(get_current_user),
    db = Depends(get_db_service)
) -> List[Comment]:
    """
    List comments on analysis

    Args:
        team_id: Team ID
        analysis_id: Analysis ID
        user_id: Authenticated user ID
        db: Database service

    Returns:
        List of comments
    """
    try:
        # Verify membership
        member = await db.get_team_member(team_id, user_id)
        if not member:
            raise HTTPException(status_code=403, detail="Access denied")

        comments = await db.list_comments(analysis_id)
        return comments

    except HTTPException:
        raise
    except Exception as e:
        logger.error("list_comments_failed", analysis_id=analysis_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list comments")
