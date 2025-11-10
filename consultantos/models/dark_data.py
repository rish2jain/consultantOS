"""
Dark Data Models
Models for email mining, PII detection, and dark data insights
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class EmailProvider(str, Enum):
    """Supported email providers"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    SLACK = "slack"


class EmailSource(BaseModel):
    """Email source configuration"""
    provider: EmailProvider = Field(..., description="Email provider (gmail, outlook, slack)")
    credentials_id: str = Field(..., description="Encrypted credentials reference ID")
    user_email: str = Field(..., description="User's email address")
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Email filters (date_range, sender, keywords, labels)"
    )
    enabled: bool = Field(default=True, description="Whether this source is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_synced: Optional[datetime] = Field(None, description="Last successful sync timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "gmail",
                "credentials_id": "cred_abc123def456",
                "user_email": "user@example.com",
                "filters": {
                    "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                    "keywords": ["acquisition", "merger", "partnership"],
                    "labels": ["important", "business"]
                },
                "enabled": True
            }
        }


class EntityExtraction(BaseModel):
    """Extracted entities from email content"""
    companies: List[str] = Field(default_factory=list, description="Company names mentioned")
    people: List[str] = Field(default_factory=list, description="Person names mentioned")
    locations: List[str] = Field(default_factory=list, description="Locations mentioned")
    financial_figures: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Financial amounts and currencies"
    )
    dates: List[str] = Field(default_factory=list, description="Important dates mentioned")
    urls: List[str] = Field(default_factory=list, description="URLs found in content")

    class Config:
        json_schema_extra = {
            "example": {
                "companies": ["Tesla", "Apple Inc.", "Microsoft"],
                "people": ["Elon Musk", "Tim Cook"],
                "locations": ["Palo Alto", "Cupertino"],
                "financial_figures": [
                    {"amount": 44000000000, "currency": "USD", "context": "acquisition price"}
                ],
                "dates": ["Q4 2024", "January 15, 2025"],
                "urls": ["https://example.com/report"]
            }
        }


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results"""
    overall_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Overall sentiment score (-1.0 negative to 1.0 positive)"
    )
    polarity: str = Field(..., description="Polarity classification (positive, negative, neutral)")
    subjectivity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Subjectivity score (0.0 objective to 1.0 subjective)"
    )
    key_phrases: List[str] = Field(default_factory=list, description="Key sentiment-bearing phrases")

    @field_validator('polarity')
    @classmethod
    def validate_polarity(cls, v):
        valid = ['positive', 'negative', 'neutral']
        if v not in valid:
            raise ValueError(f"Polarity must be one of {valid}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 0.65,
                "polarity": "positive",
                "subjectivity": 0.7,
                "key_phrases": ["very excited", "great opportunity", "strong partnership"]
            }
        }


class TopicCluster(BaseModel):
    """Topic clustering result"""
    topic_name: str = Field(..., description="Name/label of the topic")
    keywords: List[str] = Field(..., description="Keywords representing the topic")
    email_count: int = Field(..., ge=0, description="Number of emails in this topic cluster")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Topic relevance score")

    class Config:
        json_schema_extra = {
            "example": {
                "topic_name": "Product Launch",
                "keywords": ["launch", "product", "release", "marketing", "timeline"],
                "email_count": 45,
                "relevance_score": 0.82
            }
        }


class DarkDataInsight(BaseModel):
    """Comprehensive dark data analysis insight"""
    source: EmailSource = Field(..., description="Source of the data")
    emails_analyzed: int = Field(..., ge=0, description="Total emails analyzed")
    entities_found: EntityExtraction = Field(..., description="Extracted entities")
    sentiment: SentimentAnalysis = Field(..., description="Sentiment analysis results")
    key_topics: List[TopicCluster] = Field(default_factory=list, description="Topic clusters identified")
    pii_detected: bool = Field(..., description="Whether PII was detected")
    pii_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of each PII type detected"
    )
    anonymized_content: str = Field(..., description="Anonymized summary content")
    risk_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall risk score based on PII and sensitive content"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_duration: Optional[float] = Field(None, description="Analysis duration in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "source": {
                    "provider": "gmail",
                    "credentials_id": "cred_abc123",
                    "user_email": "user@example.com",
                    "filters": {"keywords": ["acquisition"]}
                },
                "emails_analyzed": 150,
                "entities_found": {
                    "companies": ["Tesla", "Apple"],
                    "people": ["Elon Musk"],
                    "financial_figures": [{"amount": 1000000, "currency": "USD"}]
                },
                "sentiment": {
                    "overall_score": 0.5,
                    "polarity": "positive",
                    "subjectivity": 0.6,
                    "key_phrases": ["great opportunity"]
                },
                "key_topics": [
                    {
                        "topic_name": "Acquisition Discussions",
                        "keywords": ["acquisition", "merger", "due diligence"],
                        "email_count": 45,
                        "relevance_score": 0.9
                    }
                ],
                "pii_detected": True,
                "pii_summary": {"EMAIL_ADDRESS": 50, "PHONE_NUMBER": 25},
                "anonymized_content": "Discussions about acquisition involving <ORGANIZATION>...",
                "risk_score": 0.65
            }
        }


class EmailMetadata(BaseModel):
    """Email message metadata"""
    message_id: str = Field(..., description="Unique email message ID")
    subject: str = Field(..., description="Email subject")
    sender: str = Field(..., description="Sender email address (anonymized if contains PII)")
    recipients: List[str] = Field(default_factory=list, description="Recipient email addresses")
    timestamp: datetime = Field(..., description="Email sent timestamp")
    has_attachments: bool = Field(default=False, description="Whether email has attachments")
    labels: List[str] = Field(default_factory=list, description="Email labels/categories")
    thread_id: Optional[str] = Field(None, description="Email thread ID")

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_12345",
                "subject": "Re: Acquisition proposal",
                "sender": "john@<REDACTED>",
                "recipients": ["jane@<REDACTED>", "team@<REDACTED>"],
                "timestamp": "2024-11-09T10:30:00Z",
                "has_attachments": True,
                "labels": ["important", "business"]
            }
        }


class DarkDataAnalysisRequest(BaseModel):
    """Request to analyze dark data from email source"""
    source_id: str = Field(..., description="Email source ID to analyze")
    date_range: Optional[Dict[str, str]] = Field(
        None,
        description="Date range filter {start: ISO date, end: ISO date}"
    )
    keywords: Optional[List[str]] = Field(None, description="Keyword filters")
    max_emails: int = Field(default=100, ge=1, le=1000, description="Maximum emails to analyze")
    include_attachments: bool = Field(default=False, description="Whether to analyze attachments")
    anonymization_strategy: str = Field(
        default="replace",
        description="PII anonymization strategy (replace, mask, redact, hash)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source_id": "src_abc123",
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "keywords": ["acquisition", "partnership"],
                "max_emails": 200,
                "include_attachments": False,
                "anonymization_strategy": "replace"
            }
        }


class DarkDataAnalysisResponse(BaseModel):
    """Response from dark data analysis"""
    status: str = Field(..., description="Analysis status (success, partial, error)")
    insight: Optional[DarkDataInsight] = Field(None, description="Analysis insights")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "insight": {
                    "emails_analyzed": 150,
                    "pii_detected": True,
                    "risk_score": 0.65
                },
                "warnings": ["Some emails could not be processed due to encoding issues"]
            }
        }


class AuditLog(BaseModel):
    """Audit log entry for dark data operations"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="Action performed (connect, analyze, disconnect)")
    source_id: Optional[str] = Field(None, description="Email source ID")
    resource_type: str = Field(..., description="Type of resource (email_source, analysis)")
    ip_address: Optional[str] = Field(None, description="User IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    pii_accessed: bool = Field(default=False, description="Whether PII was accessed")
    compliance_flags: List[str] = Field(
        default_factory=list,
        description="Compliance-related flags (GDPR, CCPA, etc.)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional audit metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-11-09T10:30:00Z",
                "user_id": "user_123",
                "action": "analyze_emails",
                "source_id": "src_abc123",
                "resource_type": "email_source",
                "ip_address": "192.168.1.1",
                "pii_accessed": True,
                "compliance_flags": ["GDPR", "CCPA"]
            }
        }
