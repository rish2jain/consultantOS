"""
PII Detection and Anonymization Module
Uses Presidio for enterprise-grade PII detection and anonymization
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

try:
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False
    AnalyzerEngine = None
    RecognizerRegistry = None
    NlpEngineProvider = None
    AnonymizerEngine = None
    OperatorConfig = None

logger = logging.getLogger(__name__)


class PIIType(str, Enum):
    """PII entity types"""
    CREDIT_CARD = "CREDIT_CARD"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    SSN = "US_SSN"
    IP_ADDRESS = "IP_ADDRESS"
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    ORGANIZATION = "ORGANIZATION"
    DATE_TIME = "DATE_TIME"
    MEDICAL_LICENSE = "MEDICAL_LICENSE"
    IBAN_CODE = "IBAN_CODE"
    URL = "URL"
    CRYPTO = "CRYPTO"
    US_DRIVER_LICENSE = "US_DRIVER_LICENSE"
    US_PASSPORT = "US_PASSPORT"
    US_BANK_NUMBER = "US_BANK_NUMBER"


class PIIEntity(BaseModel):
    """Detected PII entity with metadata"""
    entity_type: str = Field(..., description="Type of PII detected (e.g., CREDIT_CARD, SSN)")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    start: int = Field(..., ge=0, description="Start position in text")
    end: int = Field(..., ge=0, description="End position in text")
    text: str = Field(..., description="Actual detected text")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_type": "CREDIT_CARD",
                "score": 0.95,
                "start": 10,
                "end": 26,
                "text": "4111-1111-1111-1111"
            }
        }


class PIIDetectionResult(BaseModel):
    """Result of PII detection analysis"""
    has_pii: bool = Field(..., description="Whether any PII was detected")
    entities: List[PIIEntity] = Field(default_factory=list, description="List of detected PII entities")
    pii_types_found: List[str] = Field(default_factory=list, description="Unique PII types detected")
    high_risk_count: int = Field(default=0, description="Count of high-risk PII (score >= 0.85)")

    class Config:
        json_schema_extra = {
            "example": {
                "has_pii": True,
                "entities": [
                    {
                        "entity_type": "CREDIT_CARD",
                        "score": 0.95,
                        "start": 10,
                        "end": 26,
                        "text": "4111-1111-1111-1111"
                    }
                ],
                "pii_types_found": ["CREDIT_CARD", "EMAIL_ADDRESS"],
                "high_risk_count": 1
            }
        }


class AnonymizationResult(BaseModel):
    """Result of anonymization operation"""
    anonymized_text: str = Field(..., description="Text with PII anonymized")
    entities_anonymized: int = Field(..., description="Number of entities anonymized")
    anonymization_map: Dict[str, str] = Field(default_factory=dict, description="Mapping of original to anonymized values")

    class Config:
        json_schema_extra = {
            "example": {
                "anonymized_text": "Contact me at <EMAIL_ADDRESS> or <PHONE_NUMBER>",
                "entities_anonymized": 2,
                "anonymization_map": {
                    "john@example.com": "<EMAIL_ADDRESS>",
                    "555-1234": "<PHONE_NUMBER>"
                }
            }
        }


class PIIDetector:
    """
    Enterprise-grade PII detection and anonymization using Microsoft Presidio

    Features:
    - Multi-entity type detection (SSN, credit cards, emails, phones, etc.)
    - Configurable confidence thresholds
    - Custom entity recognition support
    - Multiple anonymization strategies
    - GDPR/CCPA compliance support
    """

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        supported_languages: List[str] = None,
        custom_recognizers: List[Any] = None
    ):
        """
        Initialize PII detector

        Args:
            confidence_threshold: Minimum confidence score to report entity (0.0-1.0)
            supported_languages: Languages to support (default: ['en'])
            custom_recognizers: Additional custom recognizers to use
        """
        if not HAS_PRESIDIO:
            raise ImportError(
                "presidio-analyzer and presidio-anonymizer packages are required. "
                "Install with: pip install presidio-analyzer presidio-anonymizer"
            )
        
        self.confidence_threshold = confidence_threshold
        self.supported_languages = supported_languages or ['en']

        # Initialize NLP engine
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }

        try:
            nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        except Exception as e:
            logger.warning(f"Failed to initialize spaCy NLP engine: {e}. Using transformer-based fallback.")
            # Fallback to transformer-based NLP
            nlp_configuration["nlp_engine_name"] = "transformers"
            nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

        # Initialize analyzer with NLP engine
        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=self.supported_languages
        )

        # Add custom recognizers if provided
        if custom_recognizers:
            registry = RecognizerRegistry()
            for recognizer in custom_recognizers:
                registry.add_recognizer(recognizer)
            self.analyzer.registry = registry

        # Initialize anonymizer
        self.anonymizer = AnonymizerEngine()

        logger.info(
            f"PIIDetector initialized with threshold={confidence_threshold}, "
            f"languages={self.supported_languages}"
        )

    async def detect_pii(
        self,
        text: str,
        language: str = 'en',
        entity_types: Optional[List[str]] = None
    ) -> PIIDetectionResult:
        """
        Detect PII in text

        Args:
            text: Text to analyze for PII
            language: Language code (default: 'en')
            entity_types: Specific entity types to detect (None = all types)

        Returns:
            PIIDetectionResult with detected entities
        """
        if not text or not text.strip():
            return PIIDetectionResult(has_pii=False)

        try:
            # Run analysis
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=entity_types,
                score_threshold=self.confidence_threshold
            )

            # Convert to PIIEntity objects
            entities = [
                PIIEntity(
                    entity_type=result.entity_type,
                    score=result.score,
                    start=result.start,
                    end=result.end,
                    text=text[result.start:result.end]
                )
                for result in results
            ]

            # Calculate statistics
            has_pii = len(entities) > 0
            pii_types_found = list(set(entity.entity_type for entity in entities))
            high_risk_count = sum(1 for entity in entities if entity.score >= 0.85)

            logger.info(
                f"PII detection completed: found {len(entities)} entities, "
                f"{high_risk_count} high-risk, types={pii_types_found}"
            )

            return PIIDetectionResult(
                has_pii=has_pii,
                entities=entities,
                pii_types_found=pii_types_found,
                high_risk_count=high_risk_count
            )

        except Exception as e:
            logger.error(f"PII detection failed: {e}", exc_info=True)
            raise

    async def anonymize(
        self,
        text: str,
        anonymization_strategy: str = "replace",
        language: str = 'en',
        entity_types: Optional[List[str]] = None
    ) -> AnonymizationResult:
        """
        Anonymize PII in text

        Args:
            text: Text to anonymize
            anonymization_strategy: Strategy to use ('replace', 'mask', 'redact', 'hash', 'encrypt')
            language: Language code
            entity_types: Specific entity types to anonymize (None = all types)

        Returns:
            AnonymizationResult with anonymized text and mapping
        """
        if not text or not text.strip():
            return AnonymizationResult(
                anonymized_text=text,
                entities_anonymized=0
            )

        try:
            # First detect PII
            analyzer_results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=entity_types,
                score_threshold=self.confidence_threshold
            )

            if not analyzer_results:
                return AnonymizationResult(
                    anonymized_text=text,
                    entities_anonymized=0
                )

            # Define anonymization operators
            operators = self._get_anonymization_operators(anonymization_strategy)

            # Anonymize
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=operators
            )

            # Build anonymization map
            anonymization_map = {}
            for item in anonymized_result.items:
                original_text = text[item.start:item.end]
                anonymized_text = anonymized_result.text[item.start:item.end]
                anonymization_map[original_text] = anonymized_text

            logger.info(
                f"Anonymized {len(analyzer_results)} entities using '{anonymization_strategy}' strategy"
            )

            return AnonymizationResult(
                anonymized_text=anonymized_result.text,
                entities_anonymized=len(analyzer_results),
                anonymization_map=anonymization_map
            )

        except Exception as e:
            logger.error(f"Anonymization failed: {e}", exc_info=True)
            raise

    def _get_anonymization_operators(self, strategy: str) -> Dict[str, OperatorConfig]:
        """Get operator configuration for anonymization strategy"""
        strategies = {
            "replace": {"DEFAULT": OperatorConfig("replace", {"new_value": "<{entity_type}>"})},
            "mask": {"DEFAULT": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 10})},
            "redact": {"DEFAULT": OperatorConfig("redact", {})},
            "hash": {"DEFAULT": OperatorConfig("hash", {"hash_type": "sha256"})},
            "encrypt": {"DEFAULT": OperatorConfig("encrypt", {"key": "WmZq4t7w!z%C*F-J"})},
        }

        return strategies.get(strategy, strategies["replace"])

    async def detect_and_anonymize(
        self,
        text: str,
        anonymization_strategy: str = "replace",
        language: str = 'en',
        entity_types: Optional[List[str]] = None
    ) -> Tuple[PIIDetectionResult, AnonymizationResult]:
        """
        Combined detection and anonymization

        Args:
            text: Text to analyze and anonymize
            anonymization_strategy: Strategy to use
            language: Language code
            entity_types: Specific entity types to process

        Returns:
            Tuple of (PIIDetectionResult, AnonymizationResult)
        """
        detection_result = await self.detect_pii(text, language, entity_types)
        anonymization_result = await self.anonymize(text, anonymization_strategy, language, entity_types)

        return detection_result, anonymization_result

    async def batch_detect_pii(
        self,
        texts: List[str],
        language: str = 'en',
        entity_types: Optional[List[str]] = None
    ) -> List[PIIDetectionResult]:
        """
        Batch PII detection for multiple texts

        Args:
            texts: List of texts to analyze
            language: Language code
            entity_types: Specific entity types to detect

        Returns:
            List of PIIDetectionResult for each text
        """
        results = []
        for text in texts:
            result = await self.detect_pii(text, language, entity_types)
            results.append(result)

        return results

    async def validate_anonymization_quality(
        self,
        original_text: str,
        anonymized_text: str
    ) -> Dict[str, Any]:
        """
        Validate that anonymization was successful and complete

        Args:
            original_text: Original text before anonymization
            anonymized_text: Anonymized text

        Returns:
            Validation metrics
        """
        # Detect PII in both texts
        original_pii = await self.detect_pii(original_text)
        anonymized_pii = await self.detect_pii(anonymized_text)

        # Calculate metrics
        original_count = len(original_pii.entities)
        remaining_count = len(anonymized_pii.entities)
        anonymization_rate = (
            (original_count - remaining_count) / original_count * 100
            if original_count > 0 else 100.0
        )

        is_valid = remaining_count == 0

        return {
            "is_valid": is_valid,
            "anonymization_rate": round(anonymization_rate, 2),
            "original_pii_count": original_count,
            "remaining_pii_count": remaining_count,
            "remaining_entities": [entity.model_dump() for entity in anonymized_pii.entities]
        }


# Convenience functions for common use cases
async def quick_detect_pii(text: str) -> PIIDetectionResult:
    """Quick PII detection with default settings"""
    detector = PIIDetector()
    return await detector.detect_pii(text)


async def quick_anonymize(text: str, strategy: str = "replace") -> str:
    """Quick anonymization with default settings"""
    detector = PIIDetector()
    result = await detector.anonymize(text, anonymization_strategy=strategy)
    return result.anonymized_text
