"""
Competitive context and benchmarking infrastructure.

Provides industry benchmarks, percentile calculations, and strategic group analysis
for contextualizing company metrics against market standards.
"""

from .competitive_context import (
    CompetitiveContextService,
    IndustryBenchmark,
    MetricPercentile,
    StrategicGroup,
)

__all__ = [
    "CompetitiveContextService",
    "IndustryBenchmark",
    "MetricPercentile",
    "StrategicGroup",
]
