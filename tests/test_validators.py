"""
Comprehensive tests for Pandera data validation schemas.

Tests validation logic for financial data, market trends, research data,
and monitoring snapshots to ensure bad external data is caught and cleaned.
"""

import pytest
from datetime import datetime
from consultantos.utils.schemas import (
    FinancialDataSchema,
    MarketDataSchema,
    ResearchDataSchema,
    MonitorSnapshotSchema,
    validate_and_clean_data,
    log_validation_metrics,
)


# ============================================================================
# FINANCIAL DATA VALIDATION TESTS
# ============================================================================

class TestFinancialDataValidation:
    """Test financial data validation schemas"""

    def test_valid_financial_snapshot(self):
        """Valid financial data should pass validation"""
        valid_data = {
            "ticker": "TSLA",
            "market_cap": 800_000_000_000.0,
            "revenue": 90_000_000_000.0,
            "revenue_growth": 0.25,
            "profit_margin": 0.15,
            "pe_ratio": 65.0,
            "key_metrics": {"eps": 3.2},
            "risk_assessment": "Medium - High volatility",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(valid_data)

        assert is_valid is True
        assert error_msg is None
        assert cleaned["ticker"] == "TSLA"
        assert cleaned["market_cap"] == 800_000_000_000.0
        assert cleaned["revenue_growth"] == 0.25

    def test_invalid_ticker_format(self):
        """Invalid ticker format should fail validation"""
        invalid_data = {
            "ticker": "invalid_ticker_123",  # Invalid format
            "market_cap": 1_000_000_000.0,
            "revenue": 500_000_000.0,
            "revenue_growth": 0.1,
            "profit_margin": 0.05,
            "pe_ratio": 20.0,
            "key_metrics": {},
            "risk_assessment": "Low",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(invalid_data)

        assert is_valid is False
        assert error_msg is not None
        assert "validation failed" in error_msg.lower()
        # Should return fallback data
        assert cleaned["ticker"] == "UNKNOWN"

    def test_negative_market_cap(self):
        """Negative market cap should fail validation"""
        invalid_data = {
            "ticker": "TEST",
            "market_cap": -1_000_000.0,  # Negative value
            "revenue": 500_000_000.0,
            "revenue_growth": 0.1,
            "profit_margin": 0.05,
            "pe_ratio": 20.0,
            "key_metrics": {},
            "risk_assessment": "Medium",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(invalid_data)

        assert is_valid is False
        assert error_msg is not None

    def test_extreme_revenue_growth(self):
        """Revenue growth outside reasonable range should fail"""
        invalid_data = {
            "ticker": "TEST",
            "market_cap": 1_000_000_000.0,
            "revenue": 500_000_000.0,
            "revenue_growth": 15.0,  # 1500% growth - unrealistic
            "profit_margin": 0.05,
            "pe_ratio": 20.0,
            "key_metrics": {},
            "risk_assessment": "High",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(invalid_data)

        assert is_valid is False
        assert cleaned["revenue_growth"] is None  # Should be sanitized

    def test_missing_optional_fields(self):
        """Missing optional fields should still validate"""
        minimal_data = {
            "ticker": "AAPL",
            "market_cap": None,
            "revenue": None,
            "revenue_growth": None,
            "profit_margin": None,
            "pe_ratio": None,
            "key_metrics": {},
            "risk_assessment": "Unknown",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(minimal_data)

        # Should pass with None values
        assert is_valid is True
        assert cleaned["ticker"] == "AAPL"
        assert cleaned["market_cap"] is None

    def test_profit_margin_out_of_range(self):
        """Profit margin outside -100% to +100% should fail"""
        invalid_data = {
            "ticker": "TEST",
            "market_cap": 1_000_000_000.0,
            "revenue": 500_000_000.0,
            "revenue_growth": 0.1,
            "profit_margin": 1.5,  # 150% margin - impossible
            "pe_ratio": 20.0,
            "key_metrics": {},
            "risk_assessment": "High",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(invalid_data)

        assert is_valid is False
        assert cleaned["profit_margin"] is None


# ============================================================================
# MARKET DATA VALIDATION TESTS
# ============================================================================

class TestMarketDataValidation:
    """Test market trend data validation schemas"""

    def test_valid_market_trends(self):
        """Valid market trends should pass validation"""
        valid_data = {
            "search_interest_trend": "Growing",
            "interest_data": {"2024-01": 75, "2024-02": 80},
            "geographic_distribution": {"US": 85, "UK": 60, "DE": 55},
            "related_searches": ["electric vehicles", "tesla model 3"],
            "competitive_comparison": {"tesla": 90, "ford": 45},
        }

        is_valid, error_msg, cleaned = MarketDataSchema.validate_market_trends(valid_data)

        assert is_valid is True
        assert error_msg is None
        assert cleaned["search_interest_trend"] == "Growing"
        assert cleaned["geographic_distribution"]["US"] == 85

    def test_invalid_trend_direction(self):
        """Invalid trend direction should fail validation"""
        invalid_data = {
            "search_interest_trend": "Skyrocketing",  # Invalid value
            "interest_data": {},
            "geographic_distribution": {},
            "related_searches": [],
            "competitive_comparison": {},
        }

        is_valid, error_msg, cleaned = MarketDataSchema.validate_market_trends(invalid_data)

        assert is_valid is False
        assert error_msg is not None
        # Should default to Unknown
        assert cleaned["search_interest_trend"] == "Unknown"

    def test_invalid_interest_score(self):
        """Interest scores outside 0-100 range should fail"""
        invalid_data = {
            "search_interest_trend": "Stable",
            "interest_data": {},
            "geographic_distribution": {"US": 150},  # Invalid score
            "related_searches": [],
            "competitive_comparison": {},
        }

        is_valid, error_msg, cleaned = MarketDataSchema.validate_market_trends(invalid_data)

        assert is_valid is False
        assert error_msg is not None

    def test_wrong_data_type_for_interest_data(self):
        """Non-dict interest_data should fail validation"""
        invalid_data = {
            "search_interest_trend": "Growing",
            "interest_data": ["invalid", "list"],  # Should be dict
            "geographic_distribution": {},
            "related_searches": [],
            "competitive_comparison": {},
        }

        is_valid, error_msg, cleaned = MarketDataSchema.validate_market_trends(invalid_data)

        assert is_valid is False
        assert cleaned["interest_data"] == {}

    def test_empty_market_trends(self):
        """Empty market trends should validate with defaults"""
        empty_data = {
            "search_interest_trend": "Unknown",
            "interest_data": {},
            "geographic_distribution": {},
            "related_searches": [],
            "competitive_comparison": {},
        }

        is_valid, error_msg, cleaned = MarketDataSchema.validate_market_trends(empty_data)

        assert is_valid is True
        assert cleaned["search_interest_trend"] == "Unknown"


# ============================================================================
# RESEARCH DATA VALIDATION TESTS
# ============================================================================

class TestResearchDataValidation:
    """Test research data validation schemas"""

    def test_valid_research_data(self):
        """Valid research data should pass validation"""
        valid_data = {
            "company_name": "Tesla Inc",
            "description": "Tesla is an electric vehicle and clean energy company.",
            "products_services": ["Model 3", "Model Y", "Solar Panels"],
            "target_market": "Global automotive and energy markets",
            "key_competitors": ["Ford", "GM", "Rivian"],
            "recent_news": ["Q4 earnings beat", "New Gigafactory"],
            "sources": [
                "https://tesla.com",
                "https://reuters.com/tesla-news",
            ],
        }

        is_valid, error_msg, cleaned = ResearchDataSchema.validate_research_data(valid_data)

        assert is_valid is True
        assert error_msg is None
        assert cleaned["company_name"] == "Tesla Inc"
        assert len(cleaned["sources"]) == 2

    def test_missing_company_name(self):
        """Missing company name should fail validation"""
        invalid_data = {
            "company_name": "",  # Empty
            "description": "A company description",
            "products_services": [],
            "target_market": "Global",
            "key_competitors": [],
            "recent_news": [],
            "sources": [],
        }

        is_valid, error_msg, cleaned = ResearchDataSchema.validate_research_data(invalid_data)

        assert is_valid is False
        assert "required" in error_msg.lower()
        assert cleaned["company_name"] == "Unknown"

    def test_short_description(self):
        """Description shorter than 10 chars should fail"""
        invalid_data = {
            "company_name": "Test Corp",
            "description": "Short",  # Too short
            "products_services": [],
            "target_market": "Global",
            "key_competitors": [],
            "recent_news": [],
            "sources": [],
        }

        is_valid, error_msg, cleaned = ResearchDataSchema.validate_research_data(invalid_data)

        assert is_valid is False
        assert "description" in error_msg.lower()

    def test_invalid_url_in_sources(self):
        """Invalid URLs should be filtered out"""
        data_with_invalid_urls = {
            "company_name": "Test Corp",
            "description": "A test company for validation",
            "products_services": [],
            "target_market": "Global",
            "key_competitors": [],
            "recent_news": [],
            "sources": [
                "https://valid.com",
                "not-a-url",
                "ftp://invalid-protocol.com",
                "https://another-valid.com",
            ],
        }

        is_valid, error_msg, cleaned = ResearchDataSchema.validate_research_data(data_with_invalid_urls)

        assert is_valid is True
        # Should filter out invalid URLs
        assert len(cleaned["sources"]) == 2
        assert "https://valid.com" in cleaned["sources"]

    def test_non_list_products(self):
        """Non-list products_services should fail"""
        invalid_data = {
            "company_name": "Test Corp",
            "description": "A test company for validation",
            "products_services": "Product A",  # Should be list
            "target_market": "Global",
            "key_competitors": [],
            "recent_news": [],
            "sources": [],
        }

        is_valid, error_msg, cleaned = ResearchDataSchema.validate_research_data(invalid_data)

        assert is_valid is False
        assert "must be a list" in error_msg.lower()


# ============================================================================
# MONITORING SNAPSHOT VALIDATION TESTS
# ============================================================================

class TestMonitorSnapshotValidation:
    """Test monitoring snapshot validation schemas"""

    def test_valid_snapshot(self):
        """Valid monitoring snapshot should pass validation"""
        valid_snapshot = {
            "monitor_id": "mon-123",
            "timestamp": datetime.utcnow(),
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "competitive_forces": {
                "competitive_rivalry": "High intensity with Ford and GM",
                "supplier_power": "Moderate supplier power",
                "buyer_power": "High buyer power",
                "threat_of_substitutes": "Low threat",
                "threat_of_new_entrants": "Moderate threat",
            },
            "market_trends": ["EV adoption growing", "Battery costs declining"],
            "financial_metrics": {
                "revenue": 90_000_000_000,
                "market_cap": 800_000_000_000,
            },
            "strategic_position": {
                "strengths": ["Brand", "Technology"],
                "weaknesses": ["Production", "Quality"],
            },
        }

        is_valid, error_msg, cleaned = MonitorSnapshotSchema.validate_snapshot(valid_snapshot)

        assert is_valid is True
        assert error_msg is None
        assert cleaned["monitor_id"] == "mon-123"
        assert cleaned["company"] == "Tesla"

    def test_missing_required_fields(self):
        """Missing required fields should fail validation"""
        invalid_snapshot = {
            "monitor_id": "",  # Empty
            "timestamp": None,  # Missing
            "company": "Tesla",
            "industry": "",  # Empty
        }

        is_valid, error_msg, cleaned = MonitorSnapshotSchema.validate_snapshot(invalid_snapshot)

        assert is_valid is False
        assert "required" in error_msg.lower()

    def test_invalid_competitive_forces_type(self):
        """Non-string competitive force values should fail"""
        invalid_snapshot = {
            "monitor_id": "mon-123",
            "timestamp": datetime.utcnow(),
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "competitive_forces": {
                "competitive_rivalry": 123,  # Should be string
            },
            "market_trends": [],
            "financial_metrics": {},
        }

        is_valid, error_msg, cleaned = MonitorSnapshotSchema.validate_snapshot(invalid_snapshot)

        assert is_valid is False
        assert "must be a string" in error_msg.lower()

    def test_negative_financial_metrics(self):
        """Negative values in disallowed financial metrics should fail"""
        invalid_snapshot = {
            "monitor_id": "mon-123",
            "timestamp": datetime.utcnow(),
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "competitive_forces": {},
            "market_trends": [],
            "financial_metrics": {
                "revenue": -1_000_000,  # Negative revenue invalid
                "market_cap": 800_000_000_000,
            },
        }

        is_valid, error_msg, cleaned = MonitorSnapshotSchema.validate_snapshot(invalid_snapshot)

        assert is_valid is False
        assert "cannot be negative" in error_msg.lower()

    def test_non_list_market_trends(self):
        """Non-list market_trends should fail"""
        invalid_snapshot = {
            "monitor_id": "mon-123",
            "timestamp": datetime.utcnow(),
            "company": "Tesla",
            "industry": "Electric Vehicles",
            "competitive_forces": {},
            "market_trends": "Growing trend",  # Should be list
            "financial_metrics": {},
        }

        is_valid, error_msg, cleaned = MonitorSnapshotSchema.validate_snapshot(invalid_snapshot)

        assert is_valid is False
        assert "must be a list" in error_msg.lower()


# ============================================================================
# UNIFIED VALIDATION FUNCTION TESTS
# ============================================================================

class TestUnifiedValidation:
    """Test unified validation and cleaning function"""

    def test_validate_financial_type(self):
        """Unified function should route to financial validator"""
        data = {
            "ticker": "AAPL",
            "market_cap": 3_000_000_000_000.0,
            "revenue": 400_000_000_000.0,
            "revenue_growth": 0.08,
            "profit_margin": 0.25,
            "pe_ratio": 28.0,
            "key_metrics": {},
            "risk_assessment": "Low",
        }

        is_valid, error_msg, cleaned = validate_and_clean_data(data, "financial")

        assert is_valid is True
        assert cleaned["ticker"] == "AAPL"

    def test_validate_market_type(self):
        """Unified function should route to market validator"""
        data = {
            "search_interest_trend": "Declining",
            "interest_data": {},
            "geographic_distribution": {},
            "related_searches": [],
            "competitive_comparison": {},
        }

        is_valid, error_msg, cleaned = validate_and_clean_data(data, "market")

        assert is_valid is True
        assert cleaned["search_interest_trend"] == "Declining"

    def test_validate_research_type(self):
        """Unified function should route to research validator"""
        data = {
            "company_name": "Apple Inc",
            "description": "Technology company selling hardware and software",
            "products_services": ["iPhone", "Mac", "iPad"],
            "target_market": "Global consumer electronics",
            "key_competitors": ["Samsung", "Google"],
            "recent_news": [],
            "sources": ["https://apple.com"],
        }

        is_valid, error_msg, cleaned = validate_and_clean_data(data, "research")

        assert is_valid is True
        assert cleaned["company_name"] == "Apple Inc"

    def test_validate_snapshot_type(self):
        """Unified function should route to snapshot validator"""
        data = {
            "monitor_id": "mon-456",
            "timestamp": datetime.utcnow(),
            "company": "Apple",
            "industry": "Technology",
            "competitive_forces": {},
            "market_trends": [],
            "financial_metrics": {},
        }

        is_valid, error_msg, cleaned = validate_and_clean_data(data, "snapshot")

        assert is_valid is True
        assert cleaned["monitor_id"] == "mon-456"

    def test_unknown_data_type(self):
        """Unknown data type should fail gracefully"""
        data = {"some": "data"}

        is_valid, error_msg, cleaned = validate_and_clean_data(data, "unknown_type")

        assert is_valid is False
        assert "Unknown data type" in error_msg


# ============================================================================
# EDGE CASES AND INTEGRATION TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_financial_data(self):
        """Completely empty financial data should fail"""
        empty_data = {}

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(empty_data)

        assert is_valid is False
        assert cleaned["ticker"] == "UNKNOWN"

    def test_unicode_company_names(self):
        """Unicode characters in company names should be handled"""
        unicode_data = {
            "company_name": "Société Générale",
            "description": "French banking company with international operations",
            "products_services": [],
            "target_market": "Global banking",
            "key_competitors": [],
            "recent_news": [],
            "sources": [],
        }

        is_valid, error_msg, cleaned = ResearchDataSchema.validate_research_data(unicode_data)

        assert is_valid is True
        assert cleaned["company_name"] == "Société Générale"

    def test_very_large_financial_numbers(self):
        """Very large but realistic numbers should validate"""
        large_data = {
            "ticker": "BRK",
            "market_cap": 900_000_000_000.0,  # $900B
            "revenue": 300_000_000_000.0,  # $300B
            "revenue_growth": 0.05,
            "profit_margin": 0.10,
            "pe_ratio": 15.0,
            "key_metrics": {},
            "risk_assessment": "Low",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(large_data)

        assert is_valid is True
        assert cleaned["market_cap"] == 900_000_000_000.0

    def test_null_values_in_optional_fields(self):
        """Null values in optional fields should be preserved"""
        data_with_nulls = {
            "ticker": "TEST",
            "market_cap": None,
            "revenue": 100_000_000.0,
            "revenue_growth": None,
            "profit_margin": None,
            "pe_ratio": None,
            "key_metrics": {},
            "risk_assessment": "Unknown",
        }

        is_valid, error_msg, cleaned = FinancialDataSchema.validate_financial_snapshot(data_with_nulls)

        assert is_valid is True
        assert cleaned["market_cap"] is None
        assert cleaned["pe_ratio"] is None
        assert cleaned["revenue"] == 100_000_000.0
