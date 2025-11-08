"""
Ticker symbol resolution utility
"""
import logging
from typing import Optional
import yfinance as yf
from consultantos.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)


def resolve_ticker(company_name: str) -> Optional[str]:
    """
    Resolve company name to ticker symbol
    
    Args:
        company_name: Company name to resolve
    
    Returns:
        Ticker symbol or None if not found
    """
    # Try direct lookup first
    try:
        ticker = yf.Ticker(company_name)
        info = ticker.info
        if info and info.get('symbol'):
            symbol = info.get('symbol')
            logger.info(f"Resolved '{company_name}' to ticker '{symbol}'")
            return symbol
    except Exception as e:
        logger.debug(f"Direct lookup failed for '{company_name}': {e}")
    
    # Try common variations
    variations = [
        company_name.upper(),
        company_name.replace(" ", ""),
        company_name.replace(" ", "-"),
        company_name[:4].upper(),  # First 4 letters
    ]
    
    for variation in variations:
        try:
            ticker = yf.Ticker(variation)
            info = ticker.info
            if info and info.get('symbol') and info.get('longName'):
                # Verify it's actually the company we're looking for
                symbol = info.get('symbol')
                logger.info(f"Resolved '{company_name}' to ticker '{symbol}' via variation '{variation}'")
                return symbol
        except Exception:
            continue
    
    logger.warning(f"Could not resolve ticker for '{company_name}'")
    return None


def guess_ticker(company_name: str) -> str:
    """
    Guess ticker symbol (fallback method)
    
    Args:
        company_name: Company name
    
    Returns:
        Guessed ticker (first 4 letters uppercase)
    """
    # Remove common words
    words_to_remove = ["inc", "corp", "corporation", "incorporated", "ltd", "limited", "llc", "co", "company"]
    cleaned = company_name.lower()
    for word in words_to_remove:
        cleaned = cleaned.replace(f" {word}", "").replace(f" {word}.", "")
    
    # Take first 4 characters
    ticker = cleaned.replace(" ", "").upper()[:4]
    logger.info(f"Guessed ticker '{ticker}' for '{company_name}'")
    return ticker

