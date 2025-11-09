"""
Input sanitization utilities
"""
import html
import re
from typing import Any, Dict, List, Union


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove HTML tags and escape HTML entities
    text = html.escape(text)
    
    # Remove SQL injection patterns: statement terminators, comment markers, and quotes
    # Note: Proper SQL injection protection must come from parameterized/prepared
    # statements at the database layer, not from ad-hoc string stripping.
    # This removal is a minimal defense-in-depth measure.
    text = re.sub(r'[;\'"]', '', text)  # Remove semicolons, single quotes, double quotes
    text = re.sub(r'--', '', text)  # Remove SQL comment markers
    
    # Remove script tags and javascript: protocols
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


def sanitize_dict(data: Dict[str, Any], max_length: int = 1000) -> Dict[str, Any]:
    """
    Sanitize all string values in a dictionary
    
    Args:
        data: Dictionary to sanitize
        max_length: Maximum length for string values
    
    Returns:
        Sanitized dictionary with all string values sanitized
    """
    sanitized: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value, max_length)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, max_length)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_input(item, max_length) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized