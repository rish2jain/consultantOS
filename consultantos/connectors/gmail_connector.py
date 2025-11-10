"""
Gmail Connector with OAuth 2.0 Authentication
Secure email mining with rate limiting and error handling
"""
import logging
import base64
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


@dataclass
class GmailEmail:
    """Gmail email message"""
    message_id: str
    thread_id: str
    subject: str
    sender: str
    recipients: List[str]
    body: str
    timestamp: datetime
    labels: List[str]
    has_attachments: bool
    snippet: str


class GmailConnector:
    """
    Gmail API connector with OAuth 2.0 authentication

    Features:
    - OAuth 2.0 flow for secure authentication
    - Read emails with flexible filters
    - Extract attachments
    - Rate limiting and error handling
    - Secure credential storage
    """

    # OAuth 2.0 scopes required
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.metadata'
    ]

    # Rate limiting settings
    MAX_REQUESTS_PER_MINUTE = 250  # Gmail API quota
    MAX_REQUESTS_PER_DAY = 1000000

    def __init__(
        self,
        client_config: Dict[str, Any],
        credentials: Optional[Credentials] = None
    ):
        """
        Initialize Gmail connector

        Args:
            client_config: OAuth 2.0 client configuration
            credentials: Pre-existing OAuth credentials (if available)
        """
        self.client_config = client_config
        self.credentials = credentials
        self.service = None
        self._request_count = 0
        self._request_window_start = datetime.utcnow()

        if credentials and credentials.valid:
            self._build_service()

        logger.info("GmailConnector initialized")

    def _build_service(self):
        """Build Gmail API service"""
        try:
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Gmail API service built successfully")
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {e}")
            raise

    async def authenticate(self, redirect_uri: str = 'http://localhost:8080/oauth2callback') -> str:
        """
        Start OAuth 2.0 authentication flow

        Args:
            redirect_uri: OAuth redirect URI

        Returns:
            Authorization URL for user to visit
        """
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )

            logger.info(f"Generated OAuth URL: {auth_url}")
            return auth_url

        except Exception as e:
            logger.error(f"OAuth authentication failed: {e}")
            raise

    async def complete_authentication(
        self,
        authorization_code: str,
        redirect_uri: str = 'http://localhost:8080/oauth2callback'
    ) -> Credentials:
        """
        Complete OAuth 2.0 authentication with authorization code

        Args:
            authorization_code: Authorization code from OAuth callback
            redirect_uri: OAuth redirect URI (must match initial request)

        Returns:
            OAuth credentials
        """
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=redirect_uri
            )

            # Exchange authorization code for credentials
            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials

            # Build service with new credentials
            self._build_service()

            logger.info("OAuth authentication completed successfully")
            return self.credentials

        except Exception as e:
            logger.error(f"Failed to complete authentication: {e}")
            raise

    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.utcnow()

        # Reset counter every minute
        if (now - self._request_window_start).seconds >= 60:
            self._request_count = 0
            self._request_window_start = now

        if self._request_count >= self.MAX_REQUESTS_PER_MINUTE:
            raise Exception("Rate limit exceeded. Please wait before making more requests.")

        self._request_count += 1

    async def list_emails(
        self,
        max_results: int = 100,
        query: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        date_range: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        List email message IDs matching filters

        Args:
            max_results: Maximum number of messages to return
            query: Gmail search query (e.g., "from:example@gmail.com subject:important")
            label_ids: List of label IDs to filter by
            date_range: Date range filter {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}

        Returns:
            List of message IDs
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")

        try:
            self._check_rate_limit()

            # Build query string
            query_parts = []
            if query:
                query_parts.append(query)

            if date_range:
                if 'start' in date_range:
                    query_parts.append(f"after:{date_range['start']}")
                if 'end' in date_range:
                    query_parts.append(f"before:{date_range['end']}")

            final_query = ' '.join(query_parts) if query_parts else None

            # Execute list request
            result = await asyncio.to_thread(
                self.service.users().messages().list,
                userId='me',
                maxResults=max_results,
                q=final_query,
                labelIds=label_ids
            )

            response = result.execute()
            messages = response.get('messages', [])

            message_ids = [msg['id'] for msg in messages]
            logger.info(f"Found {len(message_ids)} messages matching filters")

            return message_ids

        except HttpError as e:
            logger.error(f"Gmail API error listing messages: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to list emails: {e}")
            raise

    async def get_email(self, message_id: str, include_body: bool = True) -> GmailEmail:
        """
        Get email message by ID

        Args:
            message_id: Gmail message ID
            include_body: Whether to fetch full message body

        Returns:
            GmailEmail object
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")

        try:
            self._check_rate_limit()

            # Determine format
            format_type = 'full' if include_body else 'metadata'

            # Fetch message
            result = await asyncio.to_thread(
                self.service.users().messages().get,
                userId='me',
                id=message_id,
                format=format_type
            )

            message = result.execute()

            # Parse message
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}

            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown')
            recipients = headers.get('To', '').split(',')
            date_str = headers.get('Date', '')

            # Parse timestamp
            try:
                from email.utils import parsedate_to_datetime
                timestamp = parsedate_to_datetime(date_str)
            except:
                timestamp = datetime.utcnow()

            # Extract body
            body = ""
            if include_body:
                body = self._extract_body(message['payload'])

            # Get labels and attachments info
            labels = message.get('labelIds', [])
            has_attachments = any(
                part.get('filename') for part in message['payload'].get('parts', [])
            )

            email = GmailEmail(
                message_id=message_id,
                thread_id=message.get('threadId', ''),
                subject=subject,
                sender=sender,
                recipients=[r.strip() for r in recipients],
                body=body,
                timestamp=timestamp,
                labels=labels,
                has_attachments=has_attachments,
                snippet=message.get('snippet', '')
            )

            return email

        except HttpError as e:
            logger.error(f"Gmail API error fetching message {message_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get email {message_id}: {e}")
            raise

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        body = ""

        if 'body' in payload and 'data' in payload['body']:
            # Decode base64 body
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        elif 'parts' in payload:
            # Multi-part message - extract text/plain or text/html
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

                # Recursively handle nested parts
                if 'parts' in part:
                    body += self._extract_body(part)

        return body

    async def batch_get_emails(
        self,
        message_ids: List[str],
        include_body: bool = True,
        batch_size: int = 50
    ) -> List[GmailEmail]:
        """
        Fetch multiple emails in batches

        Args:
            message_ids: List of message IDs to fetch
            include_body: Whether to fetch full message bodies
            batch_size: Number of messages to fetch per batch

        Returns:
            List of GmailEmail objects
        """
        emails = []

        for i in range(0, len(message_ids), batch_size):
            batch = message_ids[i:i + batch_size]

            # Fetch batch concurrently (respecting rate limits)
            tasks = [self.get_email(msg_id, include_body) for msg_id in batch]

            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.warning(f"Failed to fetch email: {result}")
                    else:
                        emails.append(result)

            except Exception as e:
                logger.error(f"Batch fetch failed: {e}")

            # Rate limiting delay between batches
            if i + batch_size < len(message_ids):
                await asyncio.sleep(0.5)

        logger.info(f"Fetched {len(emails)}/{len(message_ids)} emails")
        return emails

    async def search_emails(
        self,
        keywords: List[str],
        date_range: Optional[Dict[str, str]] = None,
        max_results: int = 100,
        include_body: bool = True
    ) -> List[GmailEmail]:
        """
        Search emails by keywords

        Args:
            keywords: List of keywords to search for
            date_range: Optional date range filter
            max_results: Maximum results to return
            include_body: Whether to fetch full bodies

        Returns:
            List of matching GmailEmail objects
        """
        # Build query from keywords
        keyword_query = ' OR '.join(f'"{kw}"' for kw in keywords)

        # Get message IDs
        message_ids = await self.list_emails(
            max_results=max_results,
            query=keyword_query,
            date_range=date_range
        )

        if not message_ids:
            logger.info("No emails found matching search criteria")
            return []

        # Fetch full emails
        emails = await self.batch_get_emails(message_ids, include_body)

        return emails

    async def get_labels(self) -> List[Dict[str, str]]:
        """
        Get all Gmail labels for the user

        Returns:
            List of label dicts with 'id' and 'name'
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")

        try:
            self._check_rate_limit()

            result = await asyncio.to_thread(
                self.service.users().labels().list,
                userId='me'
            )

            response = result.execute()
            labels = response.get('labels', [])

            return [{'id': label['id'], 'name': label['name']} for label in labels]

        except HttpError as e:
            logger.error(f"Gmail API error fetching labels: {e}")
            raise

    async def disconnect(self):
        """Disconnect and revoke credentials"""
        if self.credentials:
            try:
                from google.auth.transport.requests import Request
                import requests

                # Revoke token
                requests.post(
                    'https://oauth2.googleapis.com/revoke',
                    params={'token': self.credentials.token},
                    headers={'content-type': 'application/x-www-form-urlencoded'}
                )

                logger.info("Gmail credentials revoked successfully")

            except Exception as e:
                logger.error(f"Failed to revoke credentials: {e}")

            finally:
                self.credentials = None
                self.service = None

    def get_credentials_json(self) -> Optional[str]:
        """
        Get credentials as JSON for storage

        Returns:
            JSON string of credentials or None
        """
        if not self.credentials:
            return None

        return self.credentials.to_json()

    @classmethod
    def from_credentials_json(
        cls,
        client_config: Dict[str, Any],
        credentials_json: str
    ) -> 'GmailConnector':
        """
        Create connector from stored credentials JSON

        Args:
            client_config: OAuth client configuration
            credentials_json: JSON string of stored credentials

        Returns:
            GmailConnector instance
        """
        credentials = Credentials.from_authorized_user_info(
            eval(credentials_json)  # Convert JSON string to dict
        )

        return cls(client_config, credentials)
