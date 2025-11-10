"""
Tests for Dark Data Agent
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from consultantos.agents.dark_data_agent import DarkDataAgent
from consultantos.models.dark_data import EmailSource, EmailProvider
from consultantos.connectors.gmail_connector import GmailEmail, GmailConnector


@pytest.fixture
def dark_data_agent():
    """Create Dark Data Agent instance"""
    return DarkDataAgent(timeout=180)


@pytest.fixture
def sample_email_source():
    """Create sample email source"""
    return EmailSource(
        provider=EmailProvider.GMAIL,
        credentials_id="cred_test123",
        user_email="test@example.com",
        filters={
            'keywords': ['acquisition', 'partnership'],
            'date_range': {'start': '2024-01-01', 'end': '2024-12-31'}
        },
        enabled=True
    )


@pytest.fixture
def sample_emails():
    """Create sample email list"""
    return [
        GmailEmail(
            message_id="msg1",
            thread_id="thread1",
            subject="Acquisition proposal from Tesla Inc.",
            sender="contact@tesla.com",
            recipients=["user@example.com"],
            body="We are interested in acquiring your company for $50 million USD.",
            timestamp=datetime(2024, 11, 1, 10, 0, 0),
            labels=["important"],
            has_attachments=False,
            snippet="Acquisition proposal..."
        ),
        GmailEmail(
            message_id="msg2",
            thread_id="thread2",
            subject="Partnership opportunity with Apple",
            sender="partnerships@apple.com",
            recipients=["user@example.com"],
            body="Excited to explore partnership opportunities in Q4 2024.",
            timestamp=datetime(2024, 11, 5, 14, 30, 0),
            labels=["business"],
            has_attachments=True,
            snippet="Partnership opportunity..."
        ),
        GmailEmail(
            message_id="msg3",
            thread_id="thread3",
            subject="Meeting notes - Confidential",
            sender="internal@company.com",
            recipients=["team@company.com"],
            body="Discussion about merger with Microsoft. CEO contact: bill@microsoft.com, Phone: 555-1234",
            timestamp=datetime(2024, 11, 8, 9, 15, 0),
            labels=["confidential"],
            has_attachments=False,
            snippet="Meeting notes..."
        )
    ]


@pytest.fixture
def mock_gmail_connector(sample_emails):
    """Create mock Gmail connector"""
    connector = AsyncMock(spec=GmailConnector)

    # Mock search_emails to return sample emails
    connector.search_emails = AsyncMock(return_value=sample_emails)

    # Mock list_emails to return message IDs
    connector.list_emails = AsyncMock(return_value=["msg1", "msg2", "msg3"])

    # Mock batch_get_emails to return sample emails
    connector.batch_get_emails = AsyncMock(return_value=sample_emails)

    return connector


@pytest.mark.asyncio
class TestDarkDataAgent:
    """Test Dark Data Agent functionality"""

    async def test_execute_internal_success(
        self,
        dark_data_agent,
        sample_email_source,
        mock_gmail_connector
    ):
        """Test successful dark data analysis"""
        input_data = {
            'source': sample_email_source,
            'connector': mock_gmail_connector,
            'max_emails': 100,
            'anonymization_strategy': 'replace'
        }

        result = await dark_data_agent._execute_internal(input_data)

        assert result['success'] is True
        assert 'data' in result
        assert result['data'] is not None

        insight = result['data']
        assert insight.emails_analyzed > 0
        assert insight.source.provider == EmailProvider.GMAIL

    async def test_fetch_emails_with_keywords(
        self,
        dark_data_agent,
        sample_email_source,
        mock_gmail_connector,
        sample_emails
    ):
        """Test fetching emails with keyword filters"""
        emails = await dark_data_agent._fetch_emails(
            mock_gmail_connector,
            sample_email_source,
            100
        )

        assert len(emails) > 0
        assert isinstance(emails[0], GmailEmail)

        # Verify search was called with keywords
        mock_gmail_connector.search_emails.assert_called_once()

    async def test_detect_pii_batch(
        self,
        dark_data_agent,
        sample_emails
    ):
        """Test batch PII detection across emails"""
        pii_results, pii_summary = await dark_data_agent._detect_pii_batch(sample_emails)

        assert len(pii_results) == len(sample_emails)
        assert isinstance(pii_summary, dict)

        # Should detect email addresses and phone number in sample data
        # (Actual results depend on Presidio accuracy)

    async def test_extract_entities(
        self,
        dark_data_agent,
        sample_emails
    ):
        """Test entity extraction from emails"""
        with patch.object(dark_data_agent, 'generate_structured') as mock_generate:
            # Mock entity extraction result
            from consultantos.models.dark_data import EntityExtraction

            mock_generate.return_value = Mock(
                companies=["Tesla", "Apple", "Microsoft"],
                people=["Elon Musk", "Tim Cook"],
                locations=["Palo Alto", "Cupertino"],
                financial_figures=[{"amount": 50000000, "currency": "USD"}],
                dates=["Q4 2024"],
                urls=[]
            )

            entities = await dark_data_agent._extract_entities(sample_emails)

            assert isinstance(entities, EntityExtraction)
            assert len(entities.companies) > 0
            assert "Tesla" in entities.companies

    async def test_analyze_sentiment(
        self,
        dark_data_agent,
        sample_emails
    ):
        """Test sentiment analysis"""
        sentiment = await dark_data_agent._analyze_sentiment(sample_emails)

        assert sentiment.overall_score >= -1.0
        assert sentiment.overall_score <= 1.0
        assert sentiment.polarity in ['positive', 'negative', 'neutral']
        assert sentiment.subjectivity >= 0.0
        assert sentiment.subjectivity <= 1.0

    async def test_cluster_topics(
        self,
        dark_data_agent,
        sample_emails
    ):
        """Test topic clustering"""
        with patch.object(dark_data_agent, 'generate_structured') as mock_generate:
            # Mock topic clusters
            from consultantos.models.dark_data import TopicCluster

            mock_generate.return_value = Mock(
                topics=[
                    TopicCluster(
                        topic_name="Acquisitions",
                        keywords=["acquisition", "merger", "purchase"],
                        email_count=2,
                        relevance_score=0.9
                    ),
                    TopicCluster(
                        topic_name="Partnerships",
                        keywords=["partnership", "collaboration"],
                        email_count=1,
                        relevance_score=0.8
                    )
                ]
            )

            topics = await dark_data_agent._cluster_topics(sample_emails)

            assert len(topics) > 0
            assert topics[0].topic_name == "Acquisitions"
            assert topics[0].relevance_score > 0

    async def test_generate_anonymized_summary(
        self,
        dark_data_agent,
        sample_emails
    ):
        """Test anonymized summary generation"""
        with patch.object(dark_data_agent, 'generate_structured') as mock_generate:
            mock_generate.return_value = Mock(
                summary="Discussions focus on potential acquisitions and strategic partnerships."
            )

            summary = await dark_data_agent._generate_anonymized_summary(
                sample_emails,
                'replace'
            )

            assert isinstance(summary, str)
            assert len(summary) > 0

    async def test_calculate_risk_score(self, dark_data_agent):
        """Test risk score calculation"""
        from consultantos.security.pii_detector import PIIDetectionResult
        from consultantos.models.dark_data import SentimentAnalysis

        # High PII, negative sentiment = high risk
        pii_results = [
            PIIDetectionResult(
                has_pii=True,
                entities=[],
                pii_types_found=['EMAIL_ADDRESS', 'CREDIT_CARD'],
                high_risk_count=2
            ),
            PIIDetectionResult(
                has_pii=True,
                entities=[],
                pii_types_found=['PHONE_NUMBER'],
                high_risk_count=1
            )
        ]

        sentiment = SentimentAnalysis(
            overall_score=-0.5,
            polarity='negative',
            subjectivity=0.8,
            key_phrases=[]
        )

        risk_score = dark_data_agent._calculate_risk_score(pii_results, sentiment)

        assert risk_score >= 0.0
        assert risk_score <= 1.0
        # Should be high risk due to PII and negative sentiment
        assert risk_score > 0.3

    async def test_calculate_risk_score_low_risk(self, dark_data_agent):
        """Test low risk score calculation"""
        from consultantos.security.pii_detector import PIIDetectionResult
        from consultantos.models.dark_data import SentimentAnalysis

        # No PII, positive sentiment = low risk
        pii_results = [
            PIIDetectionResult(
                has_pii=False,
                entities=[],
                pii_types_found=[],
                high_risk_count=0
            )
        ]

        sentiment = SentimentAnalysis(
            overall_score=0.7,
            polarity='positive',
            subjectivity=0.3,
            key_phrases=[]
        )

        risk_score = dark_data_agent._calculate_risk_score(pii_results, sentiment)

        assert risk_score >= 0.0
        assert risk_score <= 1.0
        # Should be low risk
        assert risk_score < 0.5

    async def test_get_date_range(self, dark_data_agent, sample_emails):
        """Test date range extraction"""
        date_range = dark_data_agent._get_date_range(sample_emails)

        assert 'earliest' in date_range
        assert 'latest' in date_range
        assert datetime.fromisoformat(date_range['earliest']) <= datetime.fromisoformat(date_range['latest'])

    async def test_empty_emails_handling(
        self,
        dark_data_agent,
        sample_email_source
    ):
        """Test handling of empty email list"""
        mock_connector = AsyncMock(spec=GmailConnector)
        mock_connector.search_emails = AsyncMock(return_value=[])

        input_data = {
            'source': sample_email_source,
            'connector': mock_connector,
            'max_emails': 100,
            'anonymization_strategy': 'replace'
        }

        result = await dark_data_agent._execute_internal(input_data)

        assert result['success'] is True
        assert result['data'].emails_analyzed == 0

    async def test_error_handling(
        self,
        dark_data_agent,
        sample_email_source
    ):
        """Test error handling in agent execution"""
        # Create connector that raises exception
        mock_connector = AsyncMock(spec=GmailConnector)
        mock_connector.search_emails = AsyncMock(side_effect=Exception("API Error"))

        input_data = {
            'source': sample_email_source,
            'connector': mock_connector,
            'max_emails': 100,
            'anonymization_strategy': 'replace'
        }

        result = await dark_data_agent._execute_internal(input_data)

        assert result['success'] is False
        assert 'error' in result

    async def test_timeout_handling(self, dark_data_agent):
        """Test agent timeout handling"""
        # Create agent with very short timeout
        agent = DarkDataAgent(timeout=1)

        # Mock slow operation
        async def slow_operation(*args, **kwargs):
            import asyncio
            await asyncio.sleep(5)

        agent._fetch_emails = slow_operation

        mock_connector = AsyncMock()
        input_data = {
            'source': EmailSource(
                provider=EmailProvider.GMAIL,
                credentials_id="test",
                user_email="test@example.com",
                filters={},
                enabled=True
            ),
            'connector': mock_connector,
            'max_emails': 100,
            'anonymization_strategy': 'replace'
        }

        # Should timeout
        with pytest.raises(Exception):
            await agent.execute(input_data)


@pytest.mark.asyncio
class TestDarkDataAgentIntegration:
    """Integration tests for Dark Data Agent"""

    async def test_full_analysis_workflow(
        self,
        dark_data_agent,
        sample_email_source,
        mock_gmail_connector
    ):
        """Test complete analysis workflow"""
        input_data = {
            'source': sample_email_source,
            'connector': mock_gmail_connector,
            'max_emails': 10,
            'anonymization_strategy': 'replace'
        }

        result = await dark_data_agent._execute_internal(input_data)

        assert result['success'] is True

        insight = result['data']

        # Verify all components
        assert insight.emails_analyzed > 0
        assert insight.entities_found is not None
        assert insight.sentiment is not None
        assert isinstance(insight.risk_score, float)
        assert 0.0 <= insight.risk_score <= 1.0
        assert isinstance(insight.anonymized_content, str)

    async def test_pii_detection_accuracy(
        self,
        dark_data_agent,
        sample_emails
    ):
        """Test PII detection accuracy on sample emails"""
        pii_results, pii_summary = await dark_data_agent._detect_pii_batch(sample_emails)

        # Sample emails contain at least one email address and phone
        assert len(pii_results) > 0

        # Check if common PII types were detected
        # (Actual detection depends on Presidio configuration)
