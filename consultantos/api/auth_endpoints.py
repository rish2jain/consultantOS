"""
Authentication endpoints
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/silent-auth")
async def silent_auth():
    """
    Temporary mock endpoint for silent authentication.
    In a real application, this would handle token refreshing.
    """
    return {"message": "Silent auth successful"}
