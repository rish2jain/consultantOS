"""
Security module for ConsultantOS
Handles PII detection, data anonymization, and security compliance
"""
from consultantos.security.pii_detector import PIIDetector, PIIEntity

__all__ = ["PIIDetector", "PIIEntity"]
