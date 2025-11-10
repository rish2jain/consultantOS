"""
Dark Data Agent for Email Mining
Analyzes emails with PII detection, entity extraction, and sentiment analysis
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter

from pydantic import BaseModel, Field
from textblob import TextBlob

from consultantos.agents.base_agent import BaseAgent
from consultantos.models.dark_data import (
    EmailSource,
    DarkDataInsight,
    EntityExtraction,
    SentimentAnalysis,
    TopicCluster,
    EmailMetadata
)
from consultantos.security.pii_detector import PIIDetector, PIIDetectionResult
from consultantos.connectors.gmail_connector import GmailConnector, GmailEmail

logger = logging.getLogger(__name__)


class DarkDataResult(BaseModel):
    """Dark data analysis result"""
    success: bool
    data: Optional[DarkDataInsight] = None
    error: Optional[str] = None


class DarkDataAgent(BaseAgent):
    """
    Agent for mining and analyzing dark data from emails

    Capabilities:
    - Gmail/Outlook/Slack email mining
    - PII detection and automatic redaction
    - Entity extraction (companies, people, financial figures)
    - Sentiment analysis
    - Topic clustering
    - Security compliance (GDPR, CCPA)
    """

    def __init__(self, timeout: int = 180):
        """
        Initialize Dark Data Agent

        Args:
            timeout: Per-agent timeout in seconds (default: 180s for email processing)
        """
        super().__init__(name="DarkDataAgent", timeout=timeout)
        self.pii_detector = PIIDetector(confidence_threshold=0.6)

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute dark data mining and analysis

        Args:
            input_data: Must contain:
                - source: EmailSource configuration
                - connector: GmailConnector instance (authenticated)
                - max_emails: Maximum emails to analyze
                - anonymization_strategy: PII anonymization strategy

        Returns:
            Dict with success status and DarkDataInsight
        """
        try:
            start_time = datetime.utcnow()

            # Extract input parameters
            source: EmailSource = input_data['source']
            connector: GmailConnector = input_data['connector']
            max_emails: int = input_data.get('max_emails', 100)
            anonymization_strategy: str = input_data.get('anonymization_strategy', 'replace')

            logger.info(
                f"Starting dark data analysis for {source.provider} "
                f"(max_emails={max_emails}, user={source.user_email})"
            )

            # Step 1: Fetch emails based on filters
            emails = await self._fetch_emails(connector, source, max_emails)

            if not emails:
                return {
                    'success': True,
                    'data': DarkDataInsight(
                        source=source,
                        emails_analyzed=0,
                        entities_found=EntityExtraction(),
                        sentiment=SentimentAnalysis(
                            overall_score=0.0,
                            polarity='neutral',
                            subjectivity=0.0
                        ),
                        pii_detected=False,
                        anonymized_content="No emails found matching filters.",
                        analysis_duration=0.0
                    )
                }

            logger.info(f"Fetched {len(emails)} emails for analysis")

            # Step 2: Detect PII across all emails
            pii_results, pii_summary = await self._detect_pii_batch(emails)

            # Step 3: Extract entities from emails
            entities = await self._extract_entities(emails)

            # Step 4: Perform sentiment analysis
            sentiment = await self._analyze_sentiment(emails)

            # Step 5: Cluster topics
            topics = await self._cluster_topics(emails)

            # Step 6: Generate anonymized summary
            anonymized_summary = await self._generate_anonymized_summary(
                emails, anonymization_strategy
            )

            # Step 7: Calculate risk score
            risk_score = self._calculate_risk_score(pii_results, sentiment)

            # Build insight
            analysis_duration = (datetime.utcnow() - start_time).total_seconds()

            insight = DarkDataInsight(
                source=source,
                emails_analyzed=len(emails),
                entities_found=entities,
                sentiment=sentiment,
                key_topics=topics,
                pii_detected=any(r.has_pii for r in pii_results),
                pii_summary=pii_summary,
                anonymized_content=anonymized_summary,
                risk_score=risk_score,
                metadata={
                    'email_date_range': self._get_date_range(emails),
                    'unique_senders': len(set(e.sender for e in emails)),
                    'emails_with_attachments': sum(1 for e in emails if e.has_attachments)
                },
                analysis_duration=analysis_duration
            )

            logger.info(
                f"Dark data analysis completed: {len(emails)} emails, "
                f"PII detected: {insight.pii_detected}, risk score: {risk_score:.2f}"
            )

            return {
                'success': True,
                'data': insight
            }

        except Exception as e:
            logger.error(f"Dark data analysis failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def _fetch_emails(
        self,
        connector: GmailConnector,
        source: EmailSource,
        max_emails: int
    ) -> List[GmailEmail]:
        """Fetch emails based on source configuration"""
        try:
            filters = source.filters

            # Extract filter parameters
            date_range = filters.get('date_range')
            keywords = filters.get('keywords', [])
            labels = filters.get('labels', [])

            if keywords:
                # Search by keywords
                emails = await connector.search_emails(
                    keywords=keywords,
                    date_range=date_range,
                    max_results=max_emails,
                    include_body=True
                )
            else:
                # List all emails with filters
                message_ids = await connector.list_emails(
                    max_results=max_emails,
                    date_range=date_range,
                    label_ids=labels
                )

                emails = await connector.batch_get_emails(
                    message_ids,
                    include_body=True
                )

            return emails

        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            raise

    async def _detect_pii_batch(
        self,
        emails: List[GmailEmail]
    ) -> tuple[List[PIIDetectionResult], Dict[str, int]]:
        """Detect PII across all emails and generate summary"""
        try:
            # Combine all email content
            texts = [
                f"Subject: {email.subject}\nBody: {email.body}"
                for email in emails
            ]

            # Batch detect PII
            pii_results = await self.pii_detector.batch_detect_pii(texts)

            # Generate summary of PII types found
            all_pii_types = []
            for result in pii_results:
                all_pii_types.extend(result.pii_types_found)

            pii_summary = dict(Counter(all_pii_types))

            logger.info(f"PII detection: {len(pii_results)} emails, types found: {pii_summary}")

            return pii_results, pii_summary

        except Exception as e:
            logger.error(f"PII detection failed: {e}")
            return [], {}

    async def _extract_entities(self, emails: List[GmailEmail]) -> EntityExtraction:
        """Extract structured entities from emails using Gemini"""
        try:
            # Prepare prompt for entity extraction
            email_text = "\n\n".join([
                f"Subject: {email.subject}\nContent: {email.snippet or email.body[:500]}"
                for email in emails[:50]  # Limit to first 50 for efficiency
            ])

            prompt = f"""
            Analyze the following emails and extract key entities:

            {email_text}

            Extract the following:
            1. Company names mentioned
            2. Person names mentioned (executives, stakeholders)
            3. Location names (cities, countries)
            4. Financial figures (amounts, currencies) with context
            5. Important dates mentioned
            6. URLs found

            Return structured entities.
            """

            # Define extraction model
            class ExtractedEntities(BaseModel):
                companies: List[str] = Field(default_factory=list)
                people: List[str] = Field(default_factory=list)
                locations: List[str] = Field(default_factory=list)
                financial_figures: List[Dict[str, Any]] = Field(default_factory=list)
                dates: List[str] = Field(default_factory=list)
                urls: List[str] = Field(default_factory=list)

            # Generate structured entities
            result = await self.generate_structured(
                prompt=prompt,
                response_model=ExtractedEntities,
                temperature=0.3,
                max_tokens=2000
            )

            return EntityExtraction(
                companies=result.companies,
                people=result.people,
                locations=result.locations,
                financial_figures=result.financial_figures,
                dates=result.dates,
                urls=result.urls
            )

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return EntityExtraction()

    async def _analyze_sentiment(self, emails: List[GmailEmail]) -> SentimentAnalysis:
        """Analyze sentiment of email communications"""
        try:
            # Combine email content for overall sentiment
            combined_text = " ".join([
                f"{email.subject} {email.body[:1000]}"
                for email in emails
            ])

            # Use TextBlob for sentiment analysis
            blob = TextBlob(combined_text)
            sentiment = blob.sentiment

            # Determine polarity classification
            if sentiment.polarity > 0.2:
                polarity = "positive"
            elif sentiment.polarity < -0.2:
                polarity = "negative"
            else:
                polarity = "neutral"

            # Extract key sentiment-bearing phrases
            sentences = blob.sentences[:10]  # Top 10 sentences
            key_phrases = [
                str(sent)
                for sent in sentences
                if abs(sent.sentiment.polarity) > 0.5
            ][:5]

            return SentimentAnalysis(
                overall_score=round(sentiment.polarity, 2),
                polarity=polarity,
                subjectivity=round(sentiment.subjectivity, 2),
                key_phrases=key_phrases
            )

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentAnalysis(
                overall_score=0.0,
                polarity='neutral',
                subjectivity=0.5,
                key_phrases=[]
            )

    async def _cluster_topics(self, emails: List[GmailEmail]) -> List[TopicCluster]:
        """Cluster emails into topics using Gemini"""
        try:
            # Sample subjects for topic identification
            subjects = [email.subject for email in emails[:100]]
            subjects_text = "\n".join(f"- {s}" for s in subjects)

            prompt = f"""
            Analyze these email subjects and identify 3-5 main topic clusters:

            {subjects_text}

            For each topic cluster, provide:
            1. Topic name/label
            2. Key keywords representing the topic
            3. Estimated number of emails in this cluster
            4. Relevance score (0.0-1.0)
            """

            # Define topic model
            class TopicClusters(BaseModel):
                topics: List[TopicCluster]

            result = await self.generate_structured(
                prompt=prompt,
                response_model=TopicClusters,
                temperature=0.3,
                max_tokens=1500
            )

            return result.topics

        except Exception as e:
            logger.error(f"Topic clustering failed: {e}")
            return []

    async def _generate_anonymized_summary(
        self,
        emails: List[GmailEmail],
        strategy: str
    ) -> str:
        """Generate anonymized summary of email insights"""
        try:
            # Sample emails for summary
            sample_emails = emails[:20]

            # Combine content
            combined_content = "\n\n".join([
                f"Subject: {email.subject}\nSnippet: {email.snippet}"
                for email in sample_emails
            ])

            # Anonymize the content
            anonymized = await self.pii_detector.anonymize(
                combined_content,
                anonymization_strategy=strategy
            )

            # Generate summary using Gemini
            prompt = f"""
            Generate a brief executive summary of these email communications:

            {anonymized.anonymized_text}

            Focus on:
            - Main themes and topics discussed
            - Key insights or patterns
            - Important actions or decisions mentioned

            Keep summary concise (3-5 sentences) and professional.
            """

            class Summary(BaseModel):
                summary: str

            result = await self.generate_structured(
                prompt=prompt,
                response_model=Summary,
                temperature=0.5,
                max_tokens=500
            )

            return result.summary

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Unable to generate summary due to processing error."

    def _calculate_risk_score(
        self,
        pii_results: List[PIIDetectionResult],
        sentiment: SentimentAnalysis
    ) -> float:
        """Calculate overall risk score based on PII and sentiment"""
        # PII risk component (0-0.6)
        emails_with_pii = sum(1 for r in pii_results if r.has_pii)
        pii_rate = emails_with_pii / len(pii_results) if pii_results else 0
        high_risk_pii = sum(r.high_risk_count for r in pii_results)

        pii_risk = (pii_rate * 0.4) + (min(high_risk_pii / 10, 1.0) * 0.2)

        # Sentiment risk component (0-0.2)
        # Negative sentiment increases risk
        sentiment_risk = max(-sentiment.overall_score, 0) * 0.2

        # Subjectivity component (0-0.2)
        # High subjectivity suggests informal/risky communication
        subjectivity_risk = sentiment.subjectivity * 0.2

        total_risk = min(pii_risk + sentiment_risk + subjectivity_risk, 1.0)

        return round(total_risk, 2)

    def _get_date_range(self, emails: List[GmailEmail]) -> Dict[str, str]:
        """Get date range of analyzed emails"""
        if not emails:
            return {}

        timestamps = [email.timestamp for email in emails]
        return {
            'earliest': min(timestamps).isoformat(),
            'latest': max(timestamps).isoformat()
        }
