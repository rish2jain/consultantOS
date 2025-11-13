"""
Pandera validation schemas for data quality in ConsultantOS.

Ensures external data sources (yfinance, Tavily, pytrends) meet quality
standards to prevent false alerts in continuous monitoring.
"""

import logging
from typing import Any, Dict, List, Optional, Union
import pandas as pd

# Import pandera classes using pandera.pandas namespace
# Note: Using pandera.pandas namespace for better compatibility
try:
    import pandera.pandas as pa
    from pandera.pandas import Column, DataFrameSchema, Check
    from pandera.errors import SchemaError, SchemaErrors
except ImportError:
    # Fallback to top-level imports if pandera.pandas is not available
    # This may occur with older pandera versions
    import pandera as pa
    from pandera import Column, DataFrameSchema, Check
    from pandera.errors import SchemaError, SchemaErrors

logger = logging.getLogger(__name__)


# ============================================================================
# FINANCIAL DATA SCHEMAS
# ============================================================================

class FinancialDataSchema:
    """Validation schemas for financial data from yfinance and SEC EDGAR"""

    # Basic financial metrics schema
    metrics_schema = DataFrameSchema(
        {
            "ticker": Column(
                str,
                checks=[
                    Check.str_matches(r"^[A-Z]{1,5}$"),  # Valid ticker format
                ],
                nullable=False,
                description="Stock ticker symbol"
            ),
            "market_cap": Column(
                float,
                checks=[
                    Check.greater_than_or_equal_to(0),  # Non-negative
                    Check.less_than(1e15),  # Sanity check: < $1 quadrillion
                ],
                nullable=True,
                description="Market capitalization in USD"
            ),
            "revenue": Column(
                float,
                checks=[
                    Check.greater_than_or_equal_to(0),
                    Check.less_than(1e13),  # Sanity check: < $10 trillion
                ],
                nullable=True,
                description="Annual revenue in USD"
            ),
            "revenue_growth": Column(
                float,
                checks=[
                    Check.in_range(-1.0, 10.0),  # -100% to +1000% growth
                ],
                nullable=True,
                description="Year-over-year revenue growth rate"
            ),
            "profit_margin": Column(
                float,
                checks=[
                    Check.in_range(-1.0, 1.0),  # -100% to +100%
                ],
                nullable=True,
                description="Profit margin percentage"
            ),
            "pe_ratio": Column(
                float,
                checks=[
                    Check.greater_than(-100),  # Allow negative for losses
                    Check.less_than(1000),  # Sanity check: P/E < 1000
                ],
                nullable=True,
                description="Price-to-earnings ratio"
            ),
        },
        strict=False,  # Allow additional columns
        coerce=True,  # Type coercion
    )

    @staticmethod
    def validate_financial_snapshot(data: Dict[str, Any]) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate financial snapshot data.

        Args:
            data: Financial data dictionary

        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        try:
            # Convert to DataFrame for validation
            df = pd.DataFrame([{
                "ticker": data.get("ticker", ""),
                "market_cap": data.get("market_cap"),
                "revenue": data.get("revenue"),
                "revenue_growth": data.get("revenue_growth"),
                "profit_margin": data.get("profit_margin"),
                "pe_ratio": data.get("pe_ratio"),
            }])

            # Validate
            validated_df = FinancialDataSchema.metrics_schema.validate(df, lazy=True)

            # Extract validated data
            row = validated_df.iloc[0]
            cleaned_data = {
                "ticker": row["ticker"],
                "market_cap": row["market_cap"] if pd.notna(row["market_cap"]) else None,
                "revenue": row["revenue"] if pd.notna(row["revenue"]) else None,
                "revenue_growth": row["revenue_growth"] if pd.notna(row["revenue_growth"]) else None,
                "profit_margin": row["profit_margin"] if pd.notna(row["profit_margin"]) else None,
                "pe_ratio": row["pe_ratio"] if pd.notna(row["pe_ratio"]) else None,
                "key_metrics": data.get("key_metrics", {}),
                "risk_assessment": data.get("risk_assessment", "Unknown - validation required"),
            }

            logger.info(f"financial_validation_passed: ticker={data.get('ticker')}")
            return True, None, cleaned_data

        except (SchemaError, SchemaErrors) as e:
            error_msg = f"Financial data validation failed: {str(e)}"
            failure_info = getattr(e, 'failure_cases', 'See error message')
            logger.warning(
                f"financial_validation_failed: ticker={data.get('ticker')}, errors={failure_info}"
            )

            # Return partial data with warning
            # Use UNKNOWN ticker if validation failed (likely invalid ticker format)
            ticker_value = data.get("ticker", "UNKNOWN")
            # If ticker failed validation, set to UNKNOWN
            if "ticker" in str(e):
                ticker_value = "UNKNOWN"

            cleaned_data = {
                "ticker": ticker_value,
                "market_cap": None,
                "revenue": None,
                "revenue_growth": None,
                "profit_margin": None,
                "pe_ratio": None,
                "key_metrics": data.get("key_metrics", {}),
                "risk_assessment": f"High - Data validation issues: {str(e)[:100]}",
            }

            return False, error_msg, cleaned_data


# ============================================================================
# MARKET DATA SCHEMAS
# ============================================================================

class MarketDataSchema:
    """Validation schemas for market trend data from pytrends"""

    trends_schema = DataFrameSchema(
        {
            "keyword": Column(
                str,
                checks=[
                    Check.str_length(min_value=1, max_value=100),
                ],
                nullable=False,
                description="Search keyword"
            ),
            "interest_score": Column(
                float,
                checks=[
                    Check.in_range(0, 100),  # Google Trends score range
                ],
                nullable=True,
                description="Search interest score (0-100)"
            ),
            "trend_direction": Column(
                str,
                checks=[
                    Check.isin(["Growing", "Stable", "Declining", "Unknown"]),
                ],
                nullable=True,
                description="Trend direction classification"
            ),
        },
        strict=False,
        coerce=True,
    )

    @staticmethod
    def validate_market_trends(data: Dict[str, Any]) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate market trends data.

        Args:
            data: Market trends data dictionary

        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        try:
            # Validate search interest trend
            trend = data.get("search_interest_trend", "Unknown")
            if trend not in ["Growing", "Stable", "Declining", "Unknown"]:
                raise ValueError(f"Invalid trend direction: {trend}")

            # Validate interest data structure
            interest_data = data.get("interest_data", {})
            if not isinstance(interest_data, dict):
                raise ValueError("interest_data must be a dictionary")

            # Validate geographic distribution
            geo_dist = data.get("geographic_distribution", {})
            if not isinstance(geo_dist, dict):
                raise ValueError("geographic_distribution must be a dictionary")

            # Validate interest scores in geographic data
            for region, score in geo_dist.items():
                if score is not None and (score < 0 or score > 100):
                    raise ValueError(f"Invalid interest score for {region}: {score}")

            cleaned_data = {
                "search_interest_trend": trend,
                "interest_data": interest_data,
                "geographic_distribution": geo_dist,
                "related_searches": data.get("related_searches", []),
                "competitive_comparison": data.get("competitive_comparison", {}),
            }

            logger.info("market_trends_validation_passed")
            return True, None, cleaned_data

        except (ValueError, SchemaError) as e:
            error_msg = f"Market trends validation failed: {str(e)}"
            logger.warning(f"market_trends_validation_failed: error={str(e)}")

            # Return partial data
            cleaned_data = {
                "search_interest_trend": "Unknown",
                "interest_data": {},
                "geographic_distribution": {},
                "related_searches": [],
                "competitive_comparison": {},
            }

            return False, error_msg, cleaned_data


# ============================================================================
# RESEARCH DATA SCHEMAS
# ============================================================================

class ResearchDataSchema:
    """Validation schemas for research data from Tavily"""

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        return url.startswith(("http://", "https://"))

    @staticmethod
    def validate_research_data(data: Dict[str, Any]) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate research data from web search.

        Args:
            data: Research data dictionary

        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        try:
            errors = []

            # Validate company name
            company_name = data.get("company_name", "").strip()
            if not company_name:
                errors.append("company_name is required")
                company_name = "Unknown"  # Set default for error cases

            # Validate description
            description = data.get("description", "").strip()
            if len(description) < 10:
                errors.append("description must be at least 10 characters")

            # Validate sources (URLs)
            sources = data.get("sources", [])
            if not isinstance(sources, list):
                errors.append("sources must be a list")
            else:
                valid_sources = [
                    s for s in sources
                    if isinstance(s, str) and ResearchDataSchema.validate_url(s)
                ]
                if len(valid_sources) < len(sources):
                    logger.warning(
                        f"research_validation: removed {len(sources) - len(valid_sources)} invalid URLs"
                    )

            # Validate lists
            for field in ["products_services", "key_competitors", "recent_news"]:
                value = data.get(field, [])
                if not isinstance(value, list):
                    errors.append(f"{field} must be a list")

            if errors:
                raise ValueError("; ".join(errors))

            cleaned_data = {
                "company_name": company_name,
                "description": description,
                "products_services": data.get("products_services", []),
                "target_market": data.get("target_market", "Unknown"),
                "key_competitors": data.get("key_competitors", []),
                "recent_news": data.get("recent_news", []),
                "sources": valid_sources if sources else [],
            }

            logger.info(f"research_validation_passed: company={company_name}")
            return True, None, cleaned_data

        except ValueError as e:
            error_msg = f"Research data validation failed: {str(e)}"
            logger.warning(f"research_validation_failed: error={str(e)}")

            # Return minimal valid data
            cleaned_data = {
                "company_name": data.get("company_name") or "Unknown",  # Handle empty strings
                "description": f"Limited research data available. Validation issues: {str(e)[:100]}",
                "products_services": [],
                "target_market": "Unknown",
                "key_competitors": [],
                "recent_news": [],
                "sources": [],
            }

            return False, error_msg, cleaned_data


# ============================================================================
# MONITORING SNAPSHOT SCHEMAS
# ============================================================================

class MonitorSnapshotSchema:
    """Validation schemas for monitoring analysis snapshots"""

    @staticmethod
    def validate_confidence_score(score: float) -> bool:
        """Validate confidence score is in valid range"""
        return 0.0 <= score <= 1.0

    @staticmethod
    def validate_change_percentage(pct: float) -> bool:
        """Validate percentage change is reasonable"""
        return -1.0 <= pct <= 10.0  # -100% to +1000%

    @staticmethod
    def validate_snapshot(snapshot: Dict[str, Any]) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate monitoring snapshot data.

        Args:
            snapshot: Snapshot data dictionary

        Returns:
            Tuple of (is_valid, error_message, cleaned_data)
        """
        try:
            errors = []

            # Validate required fields
            required_fields = ["monitor_id", "timestamp", "company", "industry"]
            for field in required_fields:
                if field not in snapshot or not snapshot[field]:
                    errors.append(f"{field} is required")

            # Validate competitive forces structure
            competitive_forces = snapshot.get("competitive_forces", {})
            if competitive_forces:
                expected_forces = [
                    "competitive_rivalry",
                    "supplier_power",
                    "buyer_power",
                    "threat_of_substitutes",
                    "threat_of_new_entrants",
                ]
                for force in expected_forces:
                    if force in competitive_forces:
                        value = competitive_forces[force]
                        if not isinstance(value, str):
                            errors.append(f"{force} must be a string")

            # Validate financial metrics
            financial_metrics = snapshot.get("financial_metrics", {})
            if financial_metrics:
                for metric_name, value in financial_metrics.items():
                    if value is not None and isinstance(value, (int, float)):
                        if value < 0 and metric_name not in ["revenue_growth", "profit_margin", "pe_ratio"]:
                            errors.append(f"{metric_name} cannot be negative: {value}")

            # Validate market trends
            market_trends = snapshot.get("market_trends", [])
            if not isinstance(market_trends, list):
                errors.append("market_trends must be a list")

            if errors:
                raise ValueError("; ".join(errors))

            cleaned_data = snapshot.copy()

            logger.info(
                f"snapshot_validation_passed: monitor_id={snapshot.get('monitor_id')}"
            )
            return True, None, cleaned_data

        except ValueError as e:
            error_msg = f"Snapshot validation failed: {str(e)}"
            logger.warning(
                f"snapshot_validation_failed: monitor_id={snapshot.get('monitor_id')}, error={str(e)}"
            )

            # Return snapshot with validation warning
            cleaned_data = snapshot.copy()
            if "validation_errors" not in cleaned_data:
                cleaned_data["validation_errors"] = []
            cleaned_data["validation_errors"].append(error_msg)

            return False, error_msg, cleaned_data


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_and_clean_data(
    data: Dict[str, Any],
    data_type: str
) -> tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Unified validation function for all data types.

    Args:
        data: Data dictionary to validate
        data_type: Type of data (financial, market, research, snapshot)

    Returns:
        Tuple of (is_valid, error_message, cleaned_data)
    """
    validators = {
        "financial": FinancialDataSchema.validate_financial_snapshot,
        "market": MarketDataSchema.validate_market_trends,
        "research": ResearchDataSchema.validate_research_data,
        "snapshot": MonitorSnapshotSchema.validate_snapshot,
    }

    validator = validators.get(data_type)
    if not validator:
        logger.error(f"Unknown data type for validation: {data_type}")
        return False, f"Unknown data type: {data_type}", data

    try:
        return validator(data)
    except Exception as e:
        logger.error(
            f"Validation failed with exception: data_type={data_type}, error={str(e)}",
            exc_info=True
        )
        return False, f"Validation exception: {str(e)}", data


def log_validation_metrics(
    data_type: str,
    is_valid: bool,
    error_message: Optional[str] = None
) -> None:
    """
    Log validation metrics for monitoring.

    Args:
        data_type: Type of data validated
        is_valid: Whether validation passed
        error_message: Optional error message
    """
    status = "passed" if is_valid else "failed"
    logger.info(
        f"validation_metrics: data_type={data_type}, status={status}, "
        f"error={error_message if error_message else 'none'}"
    )
