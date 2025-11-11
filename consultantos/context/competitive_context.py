"""
Competitive context database for industry benchmarking and positioning.

Provides:
- Industry benchmark storage and retrieval
- Percentile calculation for metrics
- Strategic group identification
- Multi-industry benchmarking support
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics for benchmarking"""
    FINANCIAL = "financial"
    COMPETITIVE_FORCE = "competitive_force"
    MARKET_POSITION = "market_position"
    GROWTH_RATE = "growth_rate"
    SENTIMENT = "sentiment"
    CUSTOM = "custom"


class IndustryBenchmark(BaseModel):
    """Industry benchmark for a specific metric"""

    industry: str = Field(description="Industry sector")
    metric_name: str = Field(description="Name of metric")
    metric_type: MetricType = Field(description="Type of metric")

    # Statistical measures
    mean: float = Field(description="Industry mean")
    median: float = Field(description="Industry median")
    std_dev: float = Field(description="Standard deviation")
    min_value: float = Field(description="Minimum value in industry")
    max_value: float = Field(description="Maximum value in industry")

    # Percentile breakpoints (for quick percentile calculation)
    p10: float = Field(description="10th percentile")
    p25: float = Field(description="25th percentile")
    p50: float = Field(description="50th percentile (median)")
    p75: float = Field(description="75th percentile")
    p90: float = Field(description="90th percentile")

    # Metadata
    sample_size: int = Field(description="Number of companies in sample")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_source: str = Field(description="Source of benchmark data")
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in benchmark quality"
    )


class MetricPercentile(BaseModel):
    """Percentile ranking for a company metric"""

    company: str
    industry: str
    metric_name: str
    value: float

    # Percentile information
    percentile: float = Field(
        ge=0.0, le=100.0,
        description="Percentile ranking (0-100)"
    )
    percentile_interpretation: str = Field(
        description="Human-readable interpretation"
    )

    # Context
    industry_mean: float
    industry_median: float
    distance_from_mean_std: float = Field(
        description="Distance from mean in standard deviations"
    )

    # Comparative messaging
    comparative_statement: str = Field(
        description="e.g., 'Your 3.5/5 supplier power is 85th percentile'"
    )


class StrategicGroup(BaseModel):
    """Strategic group within an industry"""

    group_id: str = Field(description="Unique group identifier")
    industry: str
    group_name: str = Field(description="Descriptive name for group")

    # Group characteristics
    avg_market_cap: Optional[float] = None
    avg_revenue: Optional[float] = None
    avg_growth_rate: Optional[float] = None

    # Competitive positioning
    positioning_dimensions: Dict[str, float] = Field(
        default_factory=dict,
        description="Key dimensions defining group (e.g., price vs quality)"
    )

    # Members
    companies: List[str] = Field(description="Companies in this group")
    company_count: int = Field(description="Number of companies")

    # Metadata
    identified_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in group identification"
    )


class BenchmarkQuery(BaseModel):
    """Query for benchmark data"""

    industry: str
    metric_name: str
    metric_type: Optional[MetricType] = None
    include_related_industries: bool = Field(
        default=False,
        description="Include benchmarks from related industries"
    )


class CompetitiveContextService:
    """
    Service for competitive context and benchmarking.

    Provides industry benchmarks, percentile calculations, and strategic
    group identification to contextualize company metrics.
    """

    def __init__(self, db_service):
        """
        Initialize competitive context service.

        Args:
            db_service: Database service for persistence
        """
        self.db = db_service
        self.logger = logger

        # In-memory cache for frequently accessed benchmarks
        self._benchmark_cache: Dict[str, IndustryBenchmark] = {}
        self._cache_ttl = timedelta(hours=24)
        self._cache_timestamps: Dict[str, datetime] = {}

    async def store_benchmark(
        self,
        benchmark: IndustryBenchmark
    ) -> bool:
        """
        Store industry benchmark.

        Args:
            benchmark: Benchmark data to store

        Returns:
            True if stored successfully

        Raises:
            ValueError: If benchmark data invalid
        """
        try:
            # Validate benchmark
            if benchmark.sample_size < 3:
                raise ValueError("Benchmark requires minimum 3 companies")

            if not (benchmark.min_value <= benchmark.median <= benchmark.max_value):
                raise ValueError("Invalid percentile ordering")

            # Store in database
            collection = self.db.db.collection("industry_benchmarks")
            doc_id = self._get_benchmark_id(
                benchmark.industry,
                benchmark.metric_name
            )

            doc_ref = collection.document(doc_id)
            await doc_ref.set(benchmark.dict())

            # Update cache
            cache_key = f"{benchmark.industry}:{benchmark.metric_name}"
            self._benchmark_cache[cache_key] = benchmark
            self._cache_timestamps[cache_key] = datetime.utcnow()

            self.logger.info(
                f"Stored benchmark: industry={benchmark.industry}, "
                f"metric={benchmark.metric_name}, sample_size={benchmark.sample_size}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to store benchmark: {e}", exc_info=True)
            raise

    async def get_benchmark(
        self,
        industry: str,
        metric_name: str,
        use_cache: bool = True
    ) -> Optional[IndustryBenchmark]:
        """
        Retrieve industry benchmark.

        Args:
            industry: Industry sector
            metric_name: Metric name
            use_cache: Whether to use cached data

        Returns:
            Benchmark data or None if not found
        """
        try:
            cache_key = f"{industry}:{metric_name}"

            # Check cache
            if use_cache and cache_key in self._benchmark_cache:
                cache_time = self._cache_timestamps.get(cache_key)
                if cache_time and (datetime.utcnow() - cache_time) < self._cache_ttl:
                    return self._benchmark_cache[cache_key]

            # Fetch from database
            collection = self.db.db.collection("industry_benchmarks")
            doc_id = self._get_benchmark_id(industry, metric_name)

            doc_ref = collection.document(doc_id)
            doc = await doc_ref.get()

            if doc.exists:
                benchmark = IndustryBenchmark(**doc.to_dict())

                # Update cache
                self._benchmark_cache[cache_key] = benchmark
                self._cache_timestamps[cache_key] = datetime.utcnow()

                return benchmark

            return None

        except Exception as e:
            self.logger.error(f"Failed to get benchmark: {e}", exc_info=True)
            return None

    async def calculate_percentile(
        self,
        company: str,
        industry: str,
        metric_name: str,
        value: float
    ) -> Optional[MetricPercentile]:
        """
        Calculate percentile ranking for a company metric.

        Args:
            company: Company name
            industry: Industry sector
            metric_name: Metric name
            value: Metric value to rank

        Returns:
            Percentile information or None if benchmark unavailable
        """
        try:
            # Get benchmark
            benchmark = await self.get_benchmark(industry, metric_name)
            if not benchmark:
                self.logger.warning(
                    f"No benchmark available for {industry}:{metric_name}"
                )
                return None

            # Calculate percentile using interpolation
            percentile = self._interpolate_percentile(value, benchmark)

            # Calculate distance from mean in standard deviations
            z_score = (value - benchmark.mean) / benchmark.std_dev if benchmark.std_dev > 0 else 0.0

            # Generate interpretation
            interpretation = self._interpret_percentile(percentile)

            # Generate comparative statement
            comparative = self._generate_comparative_statement(
                company, metric_name, value, percentile, benchmark
            )

            return MetricPercentile(
                company=company,
                industry=industry,
                metric_name=metric_name,
                value=value,
                percentile=percentile,
                percentile_interpretation=interpretation,
                industry_mean=benchmark.mean,
                industry_median=benchmark.median,
                distance_from_mean_std=z_score,
                comparative_statement=comparative
            )

        except Exception as e:
            self.logger.error(f"Failed to calculate percentile: {e}", exc_info=True)
            return None

    async def identify_strategic_groups(
        self,
        industry: str,
        positioning_metrics: List[str],
        min_group_size: int = 3
    ) -> List[StrategicGroup]:
        """
        Identify strategic groups within an industry.

        Uses clustering on positioning metrics to identify groups of
        companies with similar competitive strategies.

        Args:
            industry: Industry sector
            positioning_metrics: Metrics defining positioning (e.g., ["price", "quality"])
            min_group_size: Minimum companies per group

        Returns:
            List of identified strategic groups
        """
        try:
            # For MVP: Simple heuristic-based grouping
            # TODO: Implement K-means or hierarchical clustering

            # Fetch company data for industry
            companies = await self._get_industry_companies(industry)

            if len(companies) < min_group_size:
                self.logger.warning(
                    f"Insufficient companies for grouping: {len(companies)}"
                )
                return []

            # Simple grouping by size (as example)
            # In production, use multi-dimensional clustering
            groups = []

            # Group by revenue quartiles
            revenue_data = [
                (c["company"], c.get("revenue", 0))
                for c in companies
                if c.get("revenue")
            ]

            if revenue_data:
                revenue_data.sort(key=lambda x: x[1])
                quartile_size = len(revenue_data) // 4

                quartiles = [
                    ("Small Players", revenue_data[:quartile_size]),
                    ("Mid-Market", revenue_data[quartile_size:2*quartile_size]),
                    ("Large Enterprises", revenue_data[2*quartile_size:3*quartile_size]),
                    ("Market Leaders", revenue_data[3*quartile_size:])
                ]

                for group_name, companies_in_group in quartiles:
                    if len(companies_in_group) >= min_group_size:
                        avg_revenue = sum(c[1] for c in companies_in_group) / len(companies_in_group)

                        group = StrategicGroup(
                            group_id=f"{industry}_{group_name.lower().replace(' ', '_')}",
                            industry=industry,
                            group_name=group_name,
                            avg_revenue=avg_revenue,
                            companies=[c[0] for c in companies_in_group],
                            company_count=len(companies_in_group),
                            confidence_score=0.7  # Heuristic-based
                        )
                        groups.append(group)

            # Store groups
            for group in groups:
                await self._store_strategic_group(group)

            self.logger.info(
                f"Identified {len(groups)} strategic groups in {industry}"
            )

            return groups

        except Exception as e:
            self.logger.error(
                f"Failed to identify strategic groups: {e}",
                exc_info=True
            )
            return []

    async def get_multi_industry_benchmarks(
        self,
        industries: List[str],
        metric_name: str
    ) -> Dict[str, IndustryBenchmark]:
        """
        Get benchmarks across multiple industries for comparison.

        Args:
            industries: List of industries
            metric_name: Metric to benchmark

        Returns:
            Dictionary mapping industry to benchmark
        """
        try:
            benchmarks = {}

            for industry in industries:
                benchmark = await self.get_benchmark(industry, metric_name)
                if benchmark:
                    benchmarks[industry] = benchmark

            return benchmarks

        except Exception as e:
            self.logger.error(
                f"Failed to get multi-industry benchmarks: {e}",
                exc_info=True
            )
            return {}

    async def invalidate_cache(
        self,
        industry: Optional[str] = None,
        metric_name: Optional[str] = None
    ) -> None:
        """
        Invalidate benchmark cache.

        Args:
            industry: Optional industry to invalidate (None = all)
            metric_name: Optional metric to invalidate (None = all)
        """
        if industry and metric_name:
            cache_key = f"{industry}:{metric_name}"
            self._benchmark_cache.pop(cache_key, None)
            self._cache_timestamps.pop(cache_key, None)
        elif industry:
            keys_to_remove = [
                k for k in self._benchmark_cache.keys()
                if k.startswith(f"{industry}:")
            ]
            for key in keys_to_remove:
                self._benchmark_cache.pop(key, None)
                self._cache_timestamps.pop(key, None)
        else:
            self._benchmark_cache.clear()
            self._cache_timestamps.clear()

        self.logger.info(
            f"Invalidated cache: industry={industry}, metric={metric_name}"
        )

    # Private helper methods

    def _get_benchmark_id(self, industry: str, metric_name: str) -> str:
        """Generate document ID for benchmark"""
        return f"{industry.lower().replace(' ', '_')}_{metric_name.lower().replace(' ', '_')}"

    def _interpolate_percentile(
        self,
        value: float,
        benchmark: IndustryBenchmark
    ) -> float:
        """
        Calculate percentile using linear interpolation between breakpoints.

        Args:
            value: Value to rank
            benchmark: Industry benchmark data

        Returns:
            Percentile (0-100)
        """
        # Handle edge cases
        if value <= benchmark.min_value:
            return 0.0
        if value >= benchmark.max_value:
            return 100.0

        # Linear interpolation between percentile breakpoints
        breakpoints = [
            (0, benchmark.min_value),
            (10, benchmark.p10),
            (25, benchmark.p25),
            (50, benchmark.p50),
            (75, benchmark.p75),
            (90, benchmark.p90),
            (100, benchmark.max_value)
        ]

        for i in range(len(breakpoints) - 1):
            p_low, v_low = breakpoints[i]
            p_high, v_high = breakpoints[i + 1]

            if v_low <= value <= v_high:
                if v_high == v_low:
                    return p_low

                # Linear interpolation
                pct = p_low + (value - v_low) / (v_high - v_low) * (p_high - p_low)
                return round(pct, 1)

        return 50.0  # Fallback

    def _interpret_percentile(self, percentile: float) -> str:
        """Generate human-readable percentile interpretation"""
        if percentile >= 90:
            return "Top 10% (Exceptional)"
        elif percentile >= 75:
            return "Top 25% (Strong)"
        elif percentile >= 50:
            return "Above Average"
        elif percentile >= 25:
            return "Below Average"
        else:
            return "Bottom 25% (Weak)"

    def _generate_comparative_statement(
        self,
        company: str,
        metric_name: str,
        value: float,
        percentile: float,
        benchmark: IndustryBenchmark
    ) -> str:
        """Generate comparative statement for percentile"""
        interpretation = self._interpret_percentile(percentile)

        return (
            f"{company}'s {metric_name} of {value:.2f} is at the "
            f"{percentile:.0f}th percentile ({interpretation}) in "
            f"{benchmark.industry}, compared to industry median of "
            f"{benchmark.median:.2f}"
        )

    async def _get_industry_companies(
        self,
        industry: str
    ) -> List[Dict]:
        """Fetch company data for industry (placeholder)"""
        # TODO: Implement actual company data retrieval
        # For now, return empty list
        return []

    async def _store_strategic_group(self, group: StrategicGroup) -> bool:
        """Store strategic group in database"""
        try:
            collection = self.db.db.collection("strategic_groups")
            doc_ref = collection.document(group.group_id)
            await doc_ref.set(group.dict())
            return True
        except Exception as e:
            self.logger.error(f"Failed to store strategic group: {e}")
            return False
