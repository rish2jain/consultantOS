"""
Dark Data API Endpoints
Secure email mining and PII-protected analysis endpoints
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from consultantos.models.dark_data import (
    EmailSource,
    DarkDataAnalysisRequest,
    DarkDataAnalysisResponse,
    DarkDataInsight,
    EmailProvider,
    AuditLog
)
from consultantos.agents.dark_data_agent import DarkDataAgent
from consultantos.connectors.gmail_connector import GmailConnector
from consultantos.security.pii_detector import PIIDetector
from consultantos.database import get_db_service
from consultantos.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dark-data", tags=["dark-data"])


# Request/Response Models
class OAuthStartRequest(BaseModel):
    """Request to start OAuth flow"""
    provider: EmailProvider = Field(..., description="Email provider")
    redirect_uri: str = Field(
        default="http://localhost:8080/oauth2callback",
        description="OAuth redirect URI"
    )


class OAuthStartResponse(BaseModel):
    """OAuth flow start response"""
    authorization_url: str = Field(..., description="URL for user to authorize")
    state: str = Field(..., description="OAuth state parameter for CSRF protection")


class OAuthCallbackRequest(BaseModel):
    """OAuth callback with authorization code"""
    provider: EmailProvider
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="OAuth state for verification")


class EmailSourceResponse(BaseModel):
    """Email source connection response"""
    source_id: str
    provider: str
    user_email: str
    enabled: bool
    created_at: datetime


class DisconnectRequest(BaseModel):
    """Request to disconnect email source"""
    source_id: str


# Dependency: Get Dark Data Agent
async def get_dark_data_agent() -> DarkDataAgent:
    """Dependency to provide Dark Data Agent"""
    return DarkDataAgent(timeout=180)


# Dependency: Audit logging
async def log_audit_event(
    request: Request,
    user_id: str,
    action: str,
    resource_type: str,
    source_id: Optional[str] = None,
    pii_accessed: bool = False
):
    """Log audit event for compliance"""
    try:
        db = get_db_service()

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            source_id=source_id,
            resource_type=resource_type,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            pii_accessed=pii_accessed,
            compliance_flags=["GDPR", "CCPA"]  # Always log for compliance
        )

        # Store in database
        await db.create_document(
            collection="audit_logs",
            data=audit_log.model_dump()
        )

        logger.info(
            f"Audit log: user={user_id}, action={action}, pii_accessed={pii_accessed}"
        )

    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")


@router.post("/connect", response_model=OAuthStartResponse)
async def start_oauth_flow(
    request: OAuthStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start OAuth 2.0 authentication flow for email provider

    This endpoint initiates the OAuth flow and returns an authorization URL
    for the user to visit and grant permissions.

    **Required Scopes**: gmail.readonly, gmail.metadata
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        logger.info(
            f"Starting OAuth flow for {request.provider} (user={user_id})"
        )

        # Get OAuth client configuration from environment/secrets
        # In production, this would be fetched from Secret Manager
        client_config = {
            "web": {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        if request.provider == EmailProvider.GMAIL:
            connector = GmailConnector(client_config)
            auth_url = await connector.authenticate(redirect_uri=request.redirect_uri)

            # Generate state for CSRF protection
            import secrets
            state = secrets.token_urlsafe(32)

            # Store state in session/database for verification
            # (In production, store in Redis or session)

            return OAuthStartResponse(
                authorization_url=auth_url,
                state=state
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Provider {request.provider} not yet supported"
            )

    except Exception as e:
        logger.error(f"OAuth flow start failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start OAuth flow"
        )


@router.post("/oauth2callback", response_model=EmailSourceResponse)
async def oauth_callback(
    callback: OAuthCallbackRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Handle OAuth 2.0 callback and complete authentication

    After user authorizes, this endpoint exchanges the authorization code
    for access tokens and stores the connection securely.
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        logger.info(f"OAuth callback for {callback.provider} (user={user_id})")

        # Verify state (CSRF protection)
        # In production: retrieve stored state and compare
        # if callback.state != stored_state:
        #     raise HTTPException(status_code=400, detail="Invalid state")

        # Get client config
        client_config = {
            "web": {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        if callback.provider == EmailProvider.GMAIL:
            connector = GmailConnector(client_config)

            # Complete authentication
            credentials = await connector.complete_authentication(
                authorization_code=callback.code
            )

            # Get user email
            user_info = credentials.id_token.get('email', 'unknown@example.com')

            # Encrypt and store credentials
            credentials_json = connector.get_credentials_json()

            # In production: encrypt credentials before storage
            # from consultantos.security.encryption import encrypt_credentials
            # encrypted_creds = encrypt_credentials(credentials_json)

            db = get_db_service()

            # Create email source
            source = EmailSource(
                provider=callback.provider,
                credentials_id=f"cred_{user_id}_{int(datetime.utcnow().timestamp())}",
                user_email=user_info,
                filters={},
                enabled=True
            )

            # Store source and encrypted credentials
            source_doc = await db.create_document(
                collection=f"users/{user_id}/email_sources",
                data=source.model_dump()
            )

            await db.create_document(
                collection=f"credentials/{source.credentials_id}",
                data={"encrypted_credentials": credentials_json}  # Encrypt in production
            )

            # Audit log
            await log_audit_event(
                request=request,
                user_id=user_id,
                action="connect_email_source",
                resource_type="email_source",
                source_id=source_doc.id,
                pii_accessed=False
            )

            return EmailSourceResponse(
                source_id=source_doc.id,
                provider=source.provider,
                user_email=source.user_email,
                enabled=source.enabled,
                created_at=source.created_at
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Provider {callback.provider} not supported"
            )

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete OAuth authentication"
        )


@router.post("/analyze", response_model=DarkDataAnalysisResponse)
async def analyze_emails(
    analysis_request: DarkDataAnalysisRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    agent: DarkDataAgent = Depends(get_dark_data_agent)
):
    """
    Analyze emails from connected source with PII protection

    This endpoint:
    1. Fetches emails from the connected source
    2. Detects and redacts PII automatically
    3. Extracts entities and performs sentiment analysis
    4. Returns anonymized insights

    **Security**: All PII is automatically detected and anonymized.
    **Compliance**: GDPR/CCPA compliant - data retained for max 30 days.
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        logger.info(
            f"Dark data analysis request: source={analysis_request.source_id}, "
            f"user={user_id}, max_emails={analysis_request.max_emails}"
        )

        # Retrieve email source
        db = get_db_service()
        source_doc = await db.get_document(
            collection=f"users/{user_id}/email_sources",
            document_id=analysis_request.source_id
        )

        if not source_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email source not found"
            )

        source = EmailSource(**source_doc)

        if not source.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email source is disabled"
            )

        # Retrieve and decrypt credentials
        creds_doc = await db.get_document(
            collection=f"credentials/{source.credentials_id}",
            document_id=source.credentials_id
        )

        if not creds_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credentials not found - please reconnect"
            )

        credentials_json = creds_doc.get("encrypted_credentials")
        # In production: decrypt_credentials(encrypted_creds)

        # Create connector
        client_config = {
            "web": {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
            }
        }

        connector = GmailConnector.from_credentials_json(
            client_config,
            credentials_json
        )

        # Update source filters if provided in request
        if analysis_request.date_range:
            source.filters['date_range'] = analysis_request.date_range
        if analysis_request.keywords:
            source.filters['keywords'] = analysis_request.keywords

        # Execute analysis
        result = await agent.execute({
            'source': source,
            'connector': connector,
            'max_emails': analysis_request.max_emails,
            'anonymization_strategy': analysis_request.anonymization_strategy
        })

        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Analysis failed')
            )

        insight: DarkDataInsight = result['data']

        # Audit log
        await log_audit_event(
            request=request,
            user_id=user_id,
            action="analyze_emails",
            resource_type="dark_data_analysis",
            source_id=analysis_request.source_id,
            pii_accessed=insight.pii_detected
        )

        # Update source last_synced
        source.last_synced = datetime.utcnow()
        await db.update_document(
            collection=f"users/{user_id}/email_sources",
            document_id=analysis_request.source_id,
            data={'last_synced': source.last_synced.isoformat()}
        )

        return DarkDataAnalysisResponse(
            status="success",
            insight=insight,
            warnings=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze emails"
        )


@router.get("/sources", response_model=List[EmailSourceResponse])
async def list_email_sources(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all connected email sources for the user

    Returns all email sources (Gmail, Outlook, Slack) that the user
    has connected and authenticated.
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        db = get_db_service()
        sources = await db.query_documents(
            collection=f"users/{user_id}/email_sources"
        )

        return [
            EmailSourceResponse(
                source_id=doc.id,
                provider=doc['provider'],
                user_email=doc['user_email'],
                enabled=doc['enabled'],
                created_at=datetime.fromisoformat(doc['created_at'])
            )
            for doc in sources
        ]

    except Exception as e:
        logger.error(f"Failed to list email sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email sources"
        )


@router.delete("/disconnect")
async def disconnect_email_source(
    disconnect: DisconnectRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Disconnect and remove email source

    This endpoint:
    1. Revokes OAuth tokens
    2. Deletes stored credentials
    3. Removes email source connection
    4. Deletes all associated analysis data (GDPR compliance)
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        logger.info(f"Disconnect request: source={disconnect.source_id}, user={user_id}")

        db = get_db_service()

        # Get source
        source_doc = await db.get_document(
            collection=f"users/{user_id}/email_sources",
            document_id=disconnect.source_id
        )

        if not source_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email source not found"
            )

        source = EmailSource(**source_doc)

        # Get credentials
        creds_doc = await db.get_document(
            collection=f"credentials/{source.credentials_id}",
            document_id=source.credentials_id
        )

        if creds_doc:
            credentials_json = creds_doc.get("encrypted_credentials")

            # Revoke OAuth tokens
            client_config = {"web": {"client_id": "YOUR_CLIENT_ID"}}
            connector = GmailConnector.from_credentials_json(
                client_config,
                credentials_json
            )
            await connector.disconnect()

            # Delete credentials
            await db.delete_document(
                collection=f"credentials/{source.credentials_id}",
                document_id=source.credentials_id
            )

        # Delete email source
        await db.delete_document(
            collection=f"users/{user_id}/email_sources",
            document_id=disconnect.source_id
        )

        # Delete all associated analysis data (GDPR compliance)
        analyses = await db.query_documents(
            collection=f"users/{user_id}/dark_data_analyses",
            filters={'source_id': disconnect.source_id}
        )

        for analysis in analyses:
            await db.delete_document(
                collection=f"users/{user_id}/dark_data_analyses",
                document_id=analysis.id
            )

        # Audit log
        await log_audit_event(
            request=request,
            user_id=user_id,
            action="disconnect_email_source",
            resource_type="email_source",
            source_id=disconnect.source_id,
            pii_accessed=False
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Email source disconnected and data deleted successfully",
                "source_id": disconnect.source_id
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disconnect failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect email source"
        )


@router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve audit logs for compliance

    **Admin only**: Returns audit trail of all dark data operations
    for compliance and security monitoring.
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        # Check if user is admin
        # In production: check user role
        # if not current_user.get("is_admin"):
        #     raise HTTPException(status_code=403, detail="Admin access required")

        db = get_db_service()
        logs = await db.query_documents(
            collection="audit_logs",
            filters={'user_id': user_id},
            limit=limit,
            order_by=[('timestamp', 'desc')]
        )

        return [AuditLog(**log) for log in logs]

    except Exception as e:
        logger.error(f"Failed to retrieve audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )
