"""
Faker-based test data factories for ConsultantOS.

Provides realistic, varied test data generation for all domain models
with support for property-based testing and reproducibility.

Usage:
    from tests.factories import ConsultantOSFactory

    # Generate single instance
    request = ConsultantOSFactory.analysis_request()

    # Generate multiple instances
    requests = ConsultantOSFactory.analysis_requests(count=10)

    # Generate with specific attributes
    monitor = ConsultantOSFactory.monitor(company="Tesla", status="active")

    # Reproducible generation with seed
    factory = ConsultantOSFactory(seed=42)
    request1 = factory.analysis_request()
    request2 = factory.analysis_request()  # Different but deterministic
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from faker import Faker
from faker.providers import BaseProvider
import random


# ============================================================================
# CUSTOM FAKER PROVIDERS
# ============================================================================

class BusinessFrameworkProvider(BaseProvider):
    """Custom provider for business analysis frameworks"""

    VALID_FRAMEWORKS = [
        "porter", "swot", "pestel", "blue_ocean",
        "ansoff", "bcg_matrix", "value_chain"
    ]

    FRAMEWORK_DESCRIPTIONS = {
        "porter": "Porter's Five Forces - Competitive forces analysis",
        "swot": "SWOT Analysis - Strengths, Weaknesses, Opportunities, Threats",
        "pestel": "PESTEL Analysis - Political, Economic, Social, Technological, Environmental, Legal",
        "blue_ocean": "Blue Ocean Strategy - Four Actions Framework",
        "ansoff": "Ansoff Matrix - Growth strategies",
        "bcg_matrix": "BCG Matrix - Portfolio analysis",
        "value_chain": "Value Chain Analysis - Value creation activities"
    }

    def framework(self) -> str:
        """Generate a random valid framework name"""
        return self.random_element(self.VALID_FRAMEWORKS)

    def frameworks(self, count: Optional[int] = None) -> List[str]:
        """Generate a list of frameworks (2-4 by default)"""
        if count is None:
            count = self.random_int(min=2, max=4)
        return self.random_sample(self.VALID_FRAMEWORKS, length=min(count, len(self.VALID_FRAMEWORKS)))

    def framework_description(self, framework: str) -> str:
        """Get description for a framework"""
        return self.FRAMEWORK_DESCRIPTIONS.get(framework, "Strategic analysis framework")


class IndustryProvider(BaseProvider):
    """Custom provider for industry sectors"""

    INDUSTRIES = [
        "Technology", "Healthcare", "Finance", "Retail", "Manufacturing",
        "Energy", "Transportation", "Telecommunications", "Real Estate",
        "Entertainment", "Education", "Hospitality", "Agriculture",
        "Aerospace", "Automotive", "Pharmaceuticals", "E-commerce",
        "Software", "Biotechnology", "Consulting", "Media", "Insurance"
    ]

    SUB_INDUSTRIES = {
        "Technology": ["Software", "Hardware", "Cloud Computing", "Cybersecurity", "AI/ML"],
        "Healthcare": ["Hospitals", "Medical Devices", "Telemedicine", "Pharmaceuticals"],
        "Finance": ["Banking", "Asset Management", "Insurance", "Fintech", "Payments"],
        "Retail": ["E-commerce", "Fashion", "Grocery", "Department Stores", "Specialty Retail"],
        "Energy": ["Oil & Gas", "Renewable Energy", "Utilities", "Nuclear", "Solar"]
    }

    def industry(self) -> str:
        """Generate a random industry sector"""
        return self.random_element(self.INDUSTRIES)

    def sub_industry(self, industry: Optional[str] = None) -> str:
        """Generate a sub-industry (optionally for specific industry)"""
        if industry and industry in self.SUB_INDUSTRIES:
            return self.random_element(self.SUB_INDUSTRIES[industry])
        # Return random sub-industry from any category
        all_subs = [sub for subs in self.SUB_INDUSTRIES.values() for sub in subs]
        return self.random_element(all_subs)


class MonitoringProvider(BaseProvider):
    """Custom provider for monitoring-specific data"""

    CHANGE_TYPES = [
        "competitive_landscape", "market_trend", "financial_metric",
        "strategic_shift", "regulatory", "technology", "leadership"
    ]

    MONITORING_FREQUENCIES = ["hourly", "daily", "weekly", "monthly"]

    MONITOR_STATUSES = ["active", "paused", "deleted", "error"]

    NOTIFICATION_CHANNELS = ["email", "slack", "webhook", "in_app"]

    def change_type(self) -> str:
        """Generate a random change type"""
        return self.random_element(self.CHANGE_TYPES)

    def monitoring_frequency(self) -> str:
        """Generate a monitoring frequency"""
        return self.random_element(self.MONITORING_FREQUENCIES)

    def monitor_status(self) -> str:
        """Generate a monitor status"""
        return self.random_element(self.MONITOR_STATUSES)

    def notification_channel(self) -> str:
        """Generate a notification channel"""
        return self.random_element(self.NOTIFICATION_CHANNELS)

    def notification_channels(self, count: Optional[int] = None) -> List[str]:
        """Generate list of notification channels (1-3 by default)"""
        if count is None:
            count = self.random_int(min=1, max=3)
        return self.random_sample(self.NOTIFICATION_CHANNELS, length=min(count, len(self.NOTIFICATION_CHANNELS)))


class FinancialDataProvider(BaseProvider):
    """Custom provider for realistic financial data"""

    def market_cap(self, size: str = "mid") -> float:
        """Generate realistic market cap based on company size

        Args:
            size: "micro", "small", "mid", "large", "mega"
        """
        ranges = {
            "micro": (50e6, 300e6),      # $50M - $300M
            "small": (300e6, 2e9),        # $300M - $2B
            "mid": (2e9, 10e9),           # $2B - $10B
            "large": (10e9, 200e9),       # $10B - $200B
            "mega": (200e9, 3e12)         # $200B - $3T
        }
        min_cap, max_cap = ranges.get(size, ranges["mid"])
        return round(self.random_int(int(min_cap), int(max_cap)), -6)  # Round to millions

    def revenue(self, market_cap: Optional[float] = None) -> float:
        """Generate realistic revenue (typically 0.5x to 2x market cap for mature companies)"""
        if market_cap:
            multiplier = self.generator.random.uniform(0.3, 2.5)
            return round(market_cap * multiplier, -6)
        return round(self.random_int(10e6, 50e9), -6)

    def revenue_growth(self) -> float:
        """Generate realistic YoY revenue growth percentage"""
        # Most companies: -10% to +50%, with bias toward positive
        return round(self.generator.random.triangular(-10, 50, 15), 2)

    def profit_margin(self) -> float:
        """Generate realistic profit margin percentage"""
        # Typical range: -20% to +40%, with bias toward 5-15%
        return round(self.generator.random.triangular(-20, 40, 10), 2)

    def pe_ratio(self) -> Optional[float]:
        """Generate realistic P/E ratio (None for unprofitable companies)"""
        if self.generator.random.random() < 0.15:  # 15% chance of being unprofitable
            return None
        # Most P/E ratios: 5 to 50, with some outliers
        return round(self.generator.random.triangular(5, 100, 20), 2)

    def stock_price(self) -> float:
        """Generate realistic stock price"""
        return round(self.generator.random.uniform(5, 500), 2)

    def confidence_score(self) -> float:
        """Generate confidence score (0.0 to 1.0)"""
        return round(self.generator.random.uniform(0.5, 1.0), 3)


# ============================================================================
# MAIN FACTORY CLASS
# ============================================================================

class ConsultantOSFactory:
    """
    Main factory class for generating test data for ConsultantOS.

    Supports reproducible test data generation with optional seeding.
    """

    def __init__(self, seed: Optional[int] = None, locale: str = "en_US"):
        """
        Initialize factory with optional seed for reproducibility.

        Args:
            seed: Random seed for deterministic generation
            locale: Faker locale (default: en_US)
        """
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        self.fake = Faker(locale)

        # Register custom providers
        self.fake.add_provider(BusinessFrameworkProvider)
        self.fake.add_provider(IndustryProvider)
        self.fake.add_provider(MonitoringProvider)
        self.fake.add_provider(FinancialDataProvider)

    # ========================================================================
    # CORE ANALYSIS MODELS
    # ========================================================================

    def analysis_request(
        self,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        frameworks: Optional[List[str]] = None,
        depth: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AnalysisRequest data.

        Args:
            company: Company name (default: random company)
            industry: Industry sector (default: random industry)
            frameworks: List of frameworks (default: random 2-4 frameworks)
            depth: Analysis depth (default: random from quick/standard/deep)

        Returns:
            Dict compatible with AnalysisRequest model
        """
        return {
            "company": company or self.fake.company(),
            "industry": industry or self.fake.industry(),
            "frameworks": frameworks or self.fake.frameworks(),
            "depth": depth or self.fake.random_element(["quick", "standard", "deep"])
        }

    def company_research(
        self,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate CompanyResearch data"""
        company = company_name or self.fake.company()
        return {
            "company_name": company,
            "description": self.fake.catch_phrase() + ". " + self.fake.bs(),
            "products_services": [
                self.fake.catch_phrase() for _ in range(self.fake.random_int(2, 5))
            ],
            "target_market": self.fake.industry() + " sector",
            "key_competitors": [
                self.fake.company() for _ in range(self.fake.random_int(3, 7))
            ],
            "recent_news": [
                self.fake.sentence() for _ in range(self.fake.random_int(3, 6))
            ],
            "sources": [
                self.fake.url() for _ in range(self.fake.random_int(5, 10))
            ]
        }

    def market_trends(self) -> Dict[str, Any]:
        """Generate MarketTrends data"""
        trend_direction = self.fake.random_element(["Growing", "Stable", "Declining"])
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

        return {
            "search_interest_trend": trend_direction,
            "interest_data": {
                month: self.fake.random_int(40, 100) for month in months
            },
            "geographic_distribution": {
                self.fake.country(): self.fake.random_int(10, 100) for _ in range(5)
            },
            "related_searches": [
                self.fake.catch_phrase() for _ in range(self.fake.random_int(5, 10))
            ],
            "competitive_comparison": {
                self.fake.company(): self.fake.random_int(20, 100) for _ in range(4)
            }
        }

    def financial_snapshot(
        self,
        ticker: Optional[str] = None,
        company_size: str = "mid"
    ) -> Dict[str, Any]:
        """
        Generate FinancialSnapshot data.

        Args:
            ticker: Stock ticker (default: random)
            company_size: Company size category for realistic market cap
        """
        market_cap = self.fake.market_cap(size=company_size)

        return {
            "ticker": ticker or self.fake.bothify("????", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "market_cap": market_cap,
            "revenue": self.fake.revenue(market_cap),
            "revenue_growth": self.fake.revenue_growth(),
            "profit_margin": self.fake.profit_margin(),
            "pe_ratio": self.fake.pe_ratio(),
            "key_metrics": {
                "debt_to_equity": round(self.fake.random.uniform(0.1, 2.0), 2),
                "current_ratio": round(self.fake.random.uniform(0.8, 3.0), 2),
                "roe": round(self.fake.random.uniform(-5, 30), 2)
            },
            "risk_assessment": self.fake.random_element([
                "Low risk - Strong fundamentals",
                "Moderate risk - Stable performance",
                "High risk - Volatile sector",
                "Elevated risk - Growth stage"
            ])
        }

    # ========================================================================
    # FRAMEWORK ANALYSIS MODELS
    # ========================================================================

    def porters_five_forces(self) -> Dict[str, Any]:
        """Generate Porter's Five Forces analysis"""
        forces = {
            "supplier_power": self.fake.random_int(1, 5),
            "buyer_power": self.fake.random_int(1, 5),
            "competitive_rivalry": self.fake.random_int(1, 5),
            "threat_of_substitutes": self.fake.random_int(1, 5),
            "threat_of_new_entrants": self.fake.random_int(1, 5)
        }

        avg_intensity = sum(forces.values()) / len(forces)
        overall = "Low" if avg_intensity < 2.5 else "Moderate" if avg_intensity < 3.5 else "High"

        return {
            **forces,
            "overall_intensity": overall,
            "detailed_analysis": {
                "supplier_power": self.fake.sentence(),
                "buyer_power": self.fake.sentence(),
                "competitive_rivalry": self.fake.sentence(),
                "threat_of_substitutes": self.fake.sentence(),
                "threat_of_new_entrants": self.fake.sentence()
            }
        }

    def swot_analysis(self) -> Dict[str, Any]:
        """Generate SWOT Analysis"""
        return {
            "strengths": [self.fake.catch_phrase() for _ in range(self.fake.random_int(3, 5))],
            "weaknesses": [self.fake.catch_phrase() for _ in range(self.fake.random_int(3, 5))],
            "opportunities": [self.fake.catch_phrase() for _ in range(self.fake.random_int(3, 5))],
            "threats": [self.fake.catch_phrase() for _ in range(self.fake.random_int(3, 5))]
        }

    def pestel_analysis(self) -> Dict[str, Any]:
        """Generate PESTEL Analysis"""
        return {
            "political": [self.fake.sentence() for _ in range(self.fake.random_int(2, 4))],
            "economic": [self.fake.sentence() for _ in range(self.fake.random_int(2, 4))],
            "social": [self.fake.sentence() for _ in range(self.fake.random_int(2, 4))],
            "technological": [self.fake.sentence() for _ in range(self.fake.random_int(2, 4))],
            "environmental": [self.fake.sentence() for _ in range(self.fake.random_int(2, 4))],
            "legal": [self.fake.sentence() for _ in range(self.fake.random_int(2, 4))]
        }

    def blue_ocean_strategy(self) -> Dict[str, Any]:
        """Generate Blue Ocean Strategy (Four Actions Framework)"""
        return {
            "eliminate": [self.fake.catch_phrase() for _ in range(self.fake.random_int(2, 4))],
            "reduce": [self.fake.catch_phrase() for _ in range(self.fake.random_int(2, 4))],
            "raise": [self.fake.catch_phrase() for _ in range(self.fake.random_int(2, 4))],
            "create": [self.fake.catch_phrase() for _ in range(self.fake.random_int(2, 4))]
        }

    # ========================================================================
    # MONITORING MODELS
    # ========================================================================

    def monitoring_config(
        self,
        frequency: Optional[str] = None,
        frameworks: Optional[List[str]] = None,
        alert_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate MonitoringConfig data.

        Args:
            frequency: Monitoring frequency (default: random)
            frameworks: Frameworks to use (default: random)
            alert_threshold: Alert confidence threshold (default: random 0.6-0.9)
        """
        return {
            "frequency": frequency or self.fake.monitoring_frequency(),
            "frameworks": frameworks or self.fake.frameworks(),
            "alert_threshold": alert_threshold or round(self.fake.random.uniform(0.6, 0.9), 2),
            "notification_channels": self.fake.notification_channels(),
            "keywords": [self.fake.word() for _ in range(self.fake.random_int(0, 5))] if self.fake.boolean() else None,
            "competitors": [self.fake.company() for _ in range(self.fake.random_int(2, 5))] if self.fake.boolean(chance_of_getting_true=70) else None
        }

    def monitor(
        self,
        company: Optional[str] = None,
        industry: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Monitor data.

        Args:
            company: Company name (default: random)
            industry: Industry (default: random)
            status: Monitor status (default: random)
            user_id: User ID (default: random UUID)
        """
        created_at = self.fake.date_time_between(start_date="-1y", end_date="now")
        last_check = self.fake.date_time_between(start_date=created_at, end_date="now") if self.fake.boolean(chance_of_getting_true=80) else None

        return {
            "id": self.fake.uuid4(),
            "user_id": user_id or self.fake.uuid4(),
            "company": company or self.fake.company(),
            "industry": industry or self.fake.industry(),
            "config": self.monitoring_config(),
            "status": status or self.fake.monitor_status(),
            "created_at": created_at,
            "last_check": last_check,
            "next_check": self.fake.date_time_between(start_date="now", end_date="+7d") if status != "paused" else None,
            "last_alert_id": self.fake.uuid4() if self.fake.boolean(chance_of_getting_true=60) else None,
            "total_alerts": self.fake.random_int(0, 50),
            "error_count": self.fake.random_int(0, 3) if status == "error" else 0,
            "last_error": self.fake.sentence() if status == "error" else None
        }

    def change(
        self,
        change_type: Optional[str] = None,
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate Change data.

        Args:
            change_type: Type of change (default: random)
            confidence: Confidence score (default: random 0.5-1.0)
        """
        return {
            "change_type": change_type or self.fake.change_type(),
            "title": self.fake.catch_phrase(),
            "description": self.fake.paragraph(),
            "confidence": confidence or self.fake.confidence_score(),
            "source_urls": [self.fake.url() for _ in range(self.fake.random_int(1, 5))],
            "detected_at": self.fake.date_time_between(start_date="-7d", end_date="now"),
            "previous_value": self.fake.word() if self.fake.boolean() else None,
            "current_value": self.fake.word() if self.fake.boolean() else None
        }

    def alert(
        self,
        monitor_id: Optional[str] = None,
        confidence: Optional[float] = None,
        num_changes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate Alert data.

        Args:
            monitor_id: Monitor ID (default: random UUID)
            confidence: Overall confidence (default: random 0.6-1.0)
            num_changes: Number of changes detected (default: 1-5)
        """
        created_at = self.fake.date_time_between(start_date="-30d", end_date="now")
        is_read = self.fake.boolean(chance_of_getting_true=60)

        num_changes = num_changes or self.fake.random_int(1, 5)
        changes = [self.change() for _ in range(num_changes)]

        return {
            "id": self.fake.uuid4(),
            "monitor_id": monitor_id or self.fake.uuid4(),
            "title": f"{num_changes} significant {'change' if num_changes == 1 else 'changes'} detected",
            "summary": self.fake.paragraph(),
            "confidence": confidence or self.fake.confidence_score(),
            "changes_detected": changes,
            "created_at": created_at,
            "read": is_read,
            "read_at": self.fake.date_time_between(start_date=created_at, end_date="now") if is_read else None,
            "user_feedback": self.fake.random_element(["helpful", "not_helpful", "false_positive"]) if is_read and self.fake.boolean() else None,
            "action_taken": self.fake.sentence() if is_read and self.fake.boolean(chance_of_getting_true=40) else None
        }

    # ========================================================================
    # USER & AUTHENTICATION MODELS
    # ========================================================================

    def user(
        self,
        email: Optional[str] = None,
        tier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate user data for authentication tests.

        Args:
            email: User email (default: random)
            tier: Subscription tier (default: random)
        """
        return {
            "id": self.fake.uuid4(),
            "email": email or self.fake.email(),
            "name": self.fake.name(),
            "company": self.fake.company(),
            "tier": tier or self.fake.random_element(["free", "professional", "enterprise"]),
            "created_at": self.fake.date_time_between(start_date="-2y", end_date="now"),
            "api_key": self.fake.sha256()[:32],
            "is_active": self.fake.boolean(chance_of_getting_true=95)
        }

    # ========================================================================
    # BULK GENERATION UTILITIES
    # ========================================================================

    def analysis_requests(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate multiple analysis requests"""
        return [self.analysis_request() for _ in range(count)]

    def monitors(self, count: int = 10, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate multiple monitors for a user"""
        uid = user_id or self.fake.uuid4()
        return [self.monitor(user_id=uid) for _ in range(count)]

    def alerts(self, count: int = 10, monitor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate multiple alerts for a monitor"""
        mid = monitor_id or self.fake.uuid4()
        return [self.alert(monitor_id=mid) for _ in range(count)]

    # ========================================================================
    # EDGE CASES & BOUNDARY VALUES
    # ========================================================================

    def edge_case_company_name(self, case_type: str) -> str:
        """
        Generate edge case company names for validation testing.

        Args:
            case_type: Type of edge case
                - "min_length": Minimum valid length (2 chars)
                - "max_length": Maximum valid length (200 chars)
                - "special_chars": Contains special characters
                - "unicode": Contains unicode characters
                - "whitespace": Contains various whitespace
                - "empty": Empty string (invalid)
                - "too_short": Below minimum (invalid)
                - "too_long": Above maximum (invalid)
        """
        cases = {
            "min_length": "AB",
            "max_length": "A" * 200,
            "special_chars": "Company & Co., Inc. [US]",
            "unicode": "Société Générale 日本",
            "whitespace": "  Multi   Space   Corp  ",
            "empty": "",
            "too_short": "A",
            "too_long": "A" * 201
        }
        return cases.get(case_type, self.fake.company())

    def edge_case_confidence(self, case_type: str) -> float:
        """
        Generate edge case confidence scores.

        Args:
            case_type: "min", "max", "below_min", "above_max", "zero", "one"
        """
        cases = {
            "min": 0.0,
            "max": 1.0,
            "below_min": -0.1,
            "above_max": 1.1,
            "zero": 0.0,
            "one": 1.0
        }
        return cases.get(case_type, 0.5)

    def edge_case_frameworks(self, case_type: str) -> List[str]:
        """
        Generate edge case framework lists.

        Args:
            case_type: "empty", "single", "max", "invalid", "duplicate"
        """
        cases = {
            "empty": [],
            "single": ["porter"],
            "max": self.fake.frameworks(count=7),  # All available
            "invalid": ["invalid_framework", "fake_framework"],
            "duplicate": ["porter", "swot", "porter"]
        }
        return cases.get(case_type, ["porter", "swot"])


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Create a default factory instance for simple imports
_default_factory = ConsultantOSFactory()

# Expose factory methods as module-level functions for convenience
analysis_request = _default_factory.analysis_request
company_research = _default_factory.company_research
market_trends = _default_factory.market_trends
financial_snapshot = _default_factory.financial_snapshot
porters_five_forces = _default_factory.porters_five_forces
swot_analysis = _default_factory.swot_analysis
pestel_analysis = _default_factory.pestel_analysis
blue_ocean_strategy = _default_factory.blue_ocean_strategy
monitoring_config = _default_factory.monitoring_config
monitor = _default_factory.monitor
change = _default_factory.change
alert = _default_factory.alert
user = _default_factory.user
