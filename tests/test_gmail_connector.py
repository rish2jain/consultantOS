"""
Tests for Gmail Connector
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

from consultantos.connectors.gmail_connector import GmailConnector, GmailEmail


@pytest.fixture
def client_config():
    """OAuth client configuration"""
    return {
        "web": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


@pytest.fixture
def mock_credentials():
    """Mock OAuth credentials"""
    creds = Mock(spec=Credentials)
    creds.valid = True
    creds.token = "test_token"
    creds.to_json.return_value = '{"token": "test_token"}'
    return creds


@pytest.fixture
def gmail_connector(client_config, mock_credentials):
    """Create Gmail connector with mock credentials"""
    return GmailConnector(client_config, mock_credentials)


@pytest.mark.asyncio
class TestGmailAuthentication:
    """Test Gmail authentication flow"""

    async def test_authenticate_generates_url(self, client_config):
        """Test OAuth URL generation"""
        connector = GmailConnector(client_config)

        with patch('consultantos.connectors.gmail_connector.Flow') as mock_flow:
            mock_flow_instance = Mock()
            mock_flow_instance.authorization_url.return_value = (
                "https://accounts.google.com/o/oauth2/auth?...",
                "state123"
            )
            mock_flow.from_client_config.return_value = mock_flow_instance

            auth_url = await connector.authenticate()

            assert "https://accounts.google.com" in auth_url
            mock_flow.from_client_config.assert_called_once()

    async def test_complete_authentication(self, client_config):
        """Test completing OAuth authentication"""
        connector = GmailConnector(client_config)

        with patch('consultantos.connectors.gmail_connector.Flow') as mock_flow:
            mock_flow_instance = Mock()
            mock_creds = Mock(spec=Credentials)
            mock_creds.valid = True

            mock_flow_instance.credentials = mock_creds
            mock_flow_instance.fetch_token = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance

            credentials = await connector.complete_authentication(
                authorization_code="test_code"
            )

            assert credentials is not None
            assert connector.credentials == mock_creds
            mock_flow_instance.fetch_token.assert_called_once_with(code="test_code")

    async def test_disconnect(self, gmail_connector):
        """Test disconnecting and revoking credentials"""
        with patch('requests.post') as mock_post:
            await gmail_connector.disconnect()

            assert gmail_connector.credentials is None
            assert gmail_connector.service is None
            mock_post.assert_called_once()


@pytest.mark.asyncio
class TestGmailEmailOperations:
    """Test Gmail email operations"""

    async def test_list_emails(self, gmail_connector):
        """Test listing email message IDs"""
        mock_messages_response = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'},
                {'id': 'msg3'}
            ]
        }

        # Mock Gmail API service
        gmail_connector.service = Mock()
        gmail_connector.service.users().messages().list().execute.return_value = mock_messages_response

        message_ids = await gmail_connector.list_emails(max_results=10)

        assert len(message_ids) == 3
        assert 'msg1' in message_ids

    async def test_list_emails_with_query(self, gmail_connector):
        """Test listing emails with search query"""
        gmail_connector.service = Mock()
        gmail_connector.service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'msg1'}]
        }

        message_ids = await gmail_connector.list_emails(
            max_results=10,
            query="from:test@example.com"
        )

        assert len(message_ids) > 0

    async def test_list_emails_with_date_range(self, gmail_connector):
        """Test listing emails with date range filter"""
        gmail_connector.service = Mock()
        gmail_connector.service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'msg1'}]
        }

        message_ids = await gmail_connector.list_emails(
            max_results=10,
            date_range={'start': '2024-01-01', 'end': '2024-12-31'}
        )

        assert isinstance(message_ids, list)

    async def test_get_email(self, gmail_connector):
        """Test fetching single email"""
        mock_message = {
            'id': 'msg1',
            'threadId': 'thread1',
            'snippet': 'Test snippet',
            'labelIds': ['INBOX'],
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'recipient@example.com'},
                    {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00 +0000'}
                ],
                'body': {
                    'data': 'VGVzdCBib2R5'  # Base64 encoded "Test body"
                },
                'parts': []
            }
        }

        gmail_connector.service = Mock()
        gmail_connector.service.users().messages().get().execute.return_value = mock_message

        email = await gmail_connector.get_email('msg1')

        assert isinstance(email, GmailEmail)
        assert email.message_id == 'msg1'
        assert email.subject == 'Test Subject'
        assert email.sender == 'sender@example.com'

    async def test_batch_get_emails(self, gmail_connector):
        """Test batch fetching emails"""
        # Mock get_email to return sample emails
        async def mock_get_email(msg_id, include_body=True):
            return GmailEmail(
                message_id=msg_id,
                thread_id='thread1',
                subject='Test',
                sender='test@example.com',
                recipients=['user@example.com'],
                body='Test body',
                timestamp=datetime(2024, 1, 1),
                labels=['INBOX'],
                has_attachments=False,
                snippet='Test'
            )

        gmail_connector.get_email = mock_get_email

        message_ids = ['msg1', 'msg2', 'msg3']
        emails = await gmail_connector.batch_get_emails(message_ids)

        assert len(emails) == 3
        assert all(isinstance(e, GmailEmail) for e in emails)

    async def test_search_emails(self, gmail_connector):
        """Test searching emails by keywords"""
        # Mock list_emails
        async def mock_list_emails(max_results, query, date_range):
            return ['msg1', 'msg2']

        # Mock batch_get_emails
        async def mock_batch_get_emails(message_ids, include_body):
            return [
                GmailEmail(
                    message_id='msg1',
                    thread_id='thread1',
                    subject='Acquisition proposal',
                    sender='test@example.com',
                    recipients=['user@example.com'],
                    body='Interested in acquisition',
                    timestamp=datetime(2024, 1, 1),
                    labels=['INBOX'],
                    has_attachments=False,
                    snippet='Acquisition...'
                )
            ]

        gmail_connector.list_emails = mock_list_emails
        gmail_connector.batch_get_emails = mock_batch_get_emails

        emails = await gmail_connector.search_emails(
            keywords=['acquisition', 'merger'],
            max_results=10
        )

        assert len(emails) > 0
        assert isinstance(emails[0], GmailEmail)

    async def test_get_labels(self, gmail_connector):
        """Test fetching Gmail labels"""
        mock_labels = {
            'labels': [
                {'id': 'INBOX', 'name': 'INBOX'},
                {'id': 'SENT', 'name': 'SENT'},
                {'id': 'Label_1', 'name': 'Important'}
            ]
        }

        gmail_connector.service = Mock()
        gmail_connector.service.users().labels().list().execute.return_value = mock_labels

        labels = await gmail_connector.get_labels()

        assert len(labels) == 3
        assert labels[0]['name'] == 'INBOX'


@pytest.mark.asyncio
class TestGmailRateLimiting:
    """Test rate limiting functionality"""

    async def test_rate_limit_enforcement(self, gmail_connector):
        """Test rate limit is enforced"""
        # Exceed rate limit
        gmail_connector._request_count = gmail_connector.MAX_REQUESTS_PER_MINUTE

        with pytest.raises(Exception, match="Rate limit exceeded"):
            gmail_connector._check_rate_limit()

    async def test_rate_limit_reset(self, gmail_connector):
        """Test rate limit resets after time window"""
        from datetime import timedelta

        # Set request count and old timestamp
        gmail_connector._request_count = 100
        gmail_connector._request_window_start = datetime.utcnow() - timedelta(seconds=70)

        # Should reset counter
        gmail_connector._check_rate_limit()

        assert gmail_connector._request_count == 1  # Reset + current request

    async def test_rate_limit_counter_increments(self, gmail_connector):
        """Test rate limit counter increments"""
        initial_count = gmail_connector._request_count

        gmail_connector._check_rate_limit()

        assert gmail_connector._request_count == initial_count + 1


@pytest.mark.asyncio
class TestGmailErrorHandling:
    """Test error handling"""

    async def test_api_error_handling(self, gmail_connector):
        """Test handling of Gmail API errors"""
        gmail_connector.service = Mock()

        # Mock HttpError
        error = HttpError(
            resp=Mock(status=403),
            content=b'Forbidden'
        )

        gmail_connector.service.users().messages().list().execute.side_effect = error

        with pytest.raises(HttpError):
            await gmail_connector.list_emails(max_results=10)

    async def test_not_authenticated_error(self):
        """Test error when not authenticated"""
        client_config = {
            "web": {
                "client_id": "test",
                "client_secret": "test"
            }
        }

        connector = GmailConnector(client_config)

        with pytest.raises(Exception, match="Not authenticated"):
            await connector.list_emails(max_results=10)


@pytest.mark.asyncio
class TestGmailCredentialManagement:
    """Test credential management"""

    def test_get_credentials_json(self, gmail_connector):
        """Test getting credentials as JSON"""
        json_creds = gmail_connector.get_credentials_json()

        assert json_creds is not None
        assert isinstance(json_creds, str)

    def test_from_credentials_json(self, client_config):
        """Test creating connector from JSON credentials"""
        credentials_json = '{"token": "test_token", "refresh_token": "refresh"}'

        with patch('consultantos.connectors.gmail_connector.Credentials') as mock_creds:
            mock_creds.from_authorized_user_info.return_value = Mock(valid=True)

            connector = GmailConnector.from_credentials_json(
                client_config,
                credentials_json
            )

            assert connector is not None
            assert connector.credentials is not None


@pytest.mark.asyncio
class TestGmailBodyExtraction:
    """Test email body extraction"""

    async def test_extract_plain_text_body(self, gmail_connector):
        """Test extracting plain text body"""
        payload = {
            'body': {
                'data': 'VGVzdCBib2R5'  # Base64 "Test body"
            }
        }

        body = gmail_connector._extract_body(payload)

        assert body == "Test body"

    async def test_extract_multipart_body(self, gmail_connector):
        """Test extracting multipart message body"""
        import base64

        payload = {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'data': base64.urlsafe_b64encode(b'Part 1').decode()
                    }
                },
                {
                    'mimeType': 'text/html',
                    'body': {
                        'data': base64.urlsafe_b64encode(b'<p>Part 2</p>').decode()
                    }
                }
            ]
        }

        body = gmail_connector._extract_body(payload)

        assert 'Part 1' in body
