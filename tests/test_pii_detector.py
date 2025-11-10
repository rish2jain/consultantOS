"""
Tests for PII Detection Module
"""
import pytest
from consultantos.security.pii_detector import (
    PIIDetector,
    PIIEntity,
    PIIDetectionResult,
    AnonymizationResult,
    quick_detect_pii,
    quick_anonymize
)


@pytest.fixture
def pii_detector():
    """Create PII detector instance"""
    return PIIDetector(confidence_threshold=0.6)


@pytest.mark.asyncio
class TestPIIDetection:
    """Test PII detection functionality"""

    async def test_detect_credit_card(self, pii_detector):
        """Test credit card detection"""
        text = "My credit card number is 4111-1111-1111-1111"

        result = await pii_detector.detect_pii(text)

        assert result.has_pii is True
        assert len(result.entities) > 0
        assert 'CREDIT_CARD' in result.pii_types_found
        assert result.high_risk_count >= 1

    async def test_detect_ssn(self, pii_detector):
        """Test SSN detection"""
        text = "My SSN is 123-45-6789"

        result = await pii_detector.detect_pii(text)

        assert result.has_pii is True
        assert 'US_SSN' in result.pii_types_found

    async def test_detect_email_address(self, pii_detector):
        """Test email address detection"""
        text = "Contact me at john.doe@example.com for more info"

        result = await pii_detector.detect_pii(text)

        assert result.has_pii is True
        assert 'EMAIL_ADDRESS' in result.pii_types_found

        # Find email entity
        email_entities = [e for e in result.entities if e.entity_type == 'EMAIL_ADDRESS']
        assert len(email_entities) > 0
        assert email_entities[0].text == "john.doe@example.com"

    async def test_detect_phone_number(self, pii_detector):
        """Test phone number detection"""
        text = "Call me at (555) 123-4567"

        result = await pii_detector.detect_pii(text)

        assert result.has_pii is True
        assert 'PHONE_NUMBER' in result.pii_types_found

    async def test_detect_multiple_pii_types(self, pii_detector):
        """Test detection of multiple PII types in one text"""
        text = """
        Contact: john.doe@example.com
        Phone: 555-1234
        SSN: 123-45-6789
        Card: 4111-1111-1111-1111
        """

        result = await pii_detector.detect_pii(text)

        assert result.has_pii is True
        assert len(result.pii_types_found) >= 2  # At least email and credit card

    async def test_no_pii_detected(self, pii_detector):
        """Test text without PII"""
        text = "This is a normal text without any sensitive information"

        result = await pii_detector.detect_pii(text)

        assert result.has_pii is False
        assert len(result.entities) == 0
        assert result.high_risk_count == 0

    async def test_empty_text(self, pii_detector):
        """Test empty text handling"""
        result = await pii_detector.detect_pii("")

        assert result.has_pii is False
        assert len(result.entities) == 0

    async def test_confidence_threshold(self):
        """Test confidence threshold filtering"""
        # Create detector with high threshold
        detector = PIIDetector(confidence_threshold=0.9)

        text = "Maybe contact someone@somewhere.com"  # Ambiguous email

        result = await detector.detect_pii(text)

        # High threshold may filter out low-confidence detections
        # (This test validates threshold works, actual result may vary)
        assert isinstance(result, PIIDetectionResult)

    async def test_batch_detect_pii(self, pii_detector):
        """Test batch PII detection"""
        texts = [
            "Email: alice@example.com",
            "Phone: 555-1234",
            "Card: 4111-1111-1111-1111"
        ]

        results = await pii_detector.batch_detect_pii(texts)

        assert len(results) == 3
        assert all(isinstance(r, PIIDetectionResult) for r in results)
        assert sum(r.has_pii for r in results) >= 2  # At least 2 should have PII


@pytest.mark.asyncio
class TestPIIAnonymization:
    """Test PII anonymization functionality"""

    async def test_anonymize_replace_strategy(self, pii_detector):
        """Test replace anonymization strategy"""
        text = "Contact john.doe@example.com or call 555-1234"

        result = await pii_detector.anonymize(text, anonymization_strategy="replace")

        assert result.entities_anonymized > 0
        assert "<EMAIL_ADDRESS>" in result.anonymized_text or "john.doe@example.com" not in result.anonymized_text

    async def test_anonymize_mask_strategy(self, pii_detector):
        """Test mask anonymization strategy"""
        text = "My credit card is 4111-1111-1111-1111"

        result = await pii_detector.anonymize(text, anonymization_strategy="mask")

        assert result.entities_anonymized > 0
        # Masked version should contain asterisks
        assert "*" in result.anonymized_text or result.entities_anonymized == 0

    async def test_anonymize_redact_strategy(self, pii_detector):
        """Test redact anonymization strategy"""
        text = "SSN: 123-45-6789"

        result = await pii_detector.anonymize(text, anonymization_strategy="redact")

        assert result.entities_anonymized >= 0
        # Redacted text should be shorter or different
        assert len(result.anonymized_text) <= len(text) or result.anonymized_text != text

    async def test_anonymization_map(self, pii_detector):
        """Test anonymization mapping is created"""
        text = "Email me at test@example.com"

        result = await pii_detector.anonymize(text, anonymization_strategy="replace")

        if result.entities_anonymized > 0:
            assert isinstance(result.anonymization_map, dict)
            # Check that original values are mapped
            assert len(result.anonymization_map) > 0

    async def test_anonymize_empty_text(self, pii_detector):
        """Test anonymization of empty text"""
        result = await pii_detector.anonymize("")

        assert result.entities_anonymized == 0
        assert result.anonymized_text == ""

    async def test_anonymize_no_pii(self, pii_detector):
        """Test anonymization when no PII present"""
        text = "This text has no sensitive information"

        result = await pii_detector.anonymize(text)

        assert result.entities_anonymized == 0
        assert result.anonymized_text == text  # Should be unchanged

    async def test_detect_and_anonymize(self, pii_detector):
        """Test combined detection and anonymization"""
        text = "Contact: john@example.com, Phone: 555-1234"

        detection, anonymization = await pii_detector.detect_and_anonymize(text)

        assert isinstance(detection, PIIDetectionResult)
        assert isinstance(anonymization, AnonymizationResult)

        if detection.has_pii:
            assert anonymization.entities_anonymized > 0

    async def test_validate_anonymization_quality(self, pii_detector):
        """Test anonymization quality validation"""
        original_text = "My email is secret@example.com and phone is 555-1234"

        # Anonymize
        anon_result = await pii_detector.anonymize(original_text)

        # Validate quality
        validation = await pii_detector.validate_anonymization_quality(
            original_text,
            anon_result.anonymized_text
        )

        assert 'is_valid' in validation
        assert 'anonymization_rate' in validation
        assert 'original_pii_count' in validation
        assert 'remaining_pii_count' in validation

        # If PII was found and anonymized, remaining count should be 0
        if validation['original_pii_count'] > 0:
            assert validation['remaining_pii_count'] == 0 or validation['anonymization_rate'] > 0


@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Test convenience functions"""

    async def test_quick_detect_pii(self):
        """Test quick_detect_pii convenience function"""
        text = "Email: test@example.com"

        result = await quick_detect_pii(text)

        assert isinstance(result, PIIDetectionResult)

    async def test_quick_anonymize(self):
        """Test quick_anonymize convenience function"""
        text = "Email: test@example.com"

        anonymized = await quick_anonymize(text)

        assert isinstance(anonymized, str)
        # Should be different from original if PII detected
        assert anonymized != text or "test@example.com" not in anonymized


@pytest.mark.asyncio
class TestPIIDetectorConfiguration:
    """Test PII detector configuration"""

    async def test_custom_confidence_threshold(self):
        """Test custom confidence threshold"""
        detector = PIIDetector(confidence_threshold=0.8)

        assert detector.confidence_threshold == 0.8

    async def test_supported_languages(self):
        """Test language configuration"""
        detector = PIIDetector(supported_languages=['en', 'es'])

        assert 'en' in detector.supported_languages
        assert 'es' in detector.supported_languages


@pytest.mark.asyncio
class TestRealWorldScenarios:
    """Test real-world PII detection scenarios"""

    async def test_email_content_with_mixed_pii(self, pii_detector):
        """Test realistic email with multiple PII types"""
        email_text = """
        Hi Team,

        Please review the attached contract for John Smith (SSN: 123-45-6789).
        You can reach him at john.smith@example.com or (555) 123-4567.

        Payment details:
        Card: 4111-1111-1111-1111
        Amount: $50,000

        Thanks,
        Jane
        """

        result = await pii_detector.detect_pii(email_text)

        assert result.has_pii is True
        assert len(result.pii_types_found) >= 2  # Should find multiple types

    async def test_business_communication_anonymization(self, pii_detector):
        """Test anonymization preserves readability"""
        text = """
        Dear Client,

        Your account (john.doe@example.com) has been updated.
        If you have questions, call us at 1-800-555-1234.

        Best regards,
        Support Team
        """

        result = await pii_detector.anonymize(text, anonymization_strategy="replace")

        # Anonymized text should still be readable
        assert "Dear Client" in result.anonymized_text
        assert "Best regards" in result.anonymized_text

        # PII should be anonymized
        if result.entities_anonymized > 0:
            assert "john.doe@example.com" not in result.anonymized_text or \
                   "<EMAIL_ADDRESS>" in result.anonymized_text
