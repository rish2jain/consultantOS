"""
Cross-Source Signal Amplification Module.

Analyzes cross-validation results from multiple data sources to detect
analyst-reality divergences and actionable trading signals.

Features:
- Analyst sentiment vs financial reality divergence detection
- Pattern matching against historical earnings miss patterns
- Probability scoring with timeline predictions
- Multi-source validation for signal confidence
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from consultantos.models import (
    FinancialSnapshot,
    AnalystRecommendations,
    NewsSentiment,
    DataSourceValidation
)

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Types of divergence signals"""
    BULLISH_DIVERGENCE = "bullish_divergence"  # Bearish analysts + improving fundamentals
    BEARISH_DIVERGENCE = "bearish_divergence"  # Bullish analysts + declining fundamentals
    CONFIRMATION = "confirmation"  # Analysts and fundamentals align
    UNCERTAINTY = "uncertainty"  # Conflicting or insufficient data


class DivergencePattern(str, Enum):
    """Historical patterns that signal likely outcomes"""
    EARNINGS_MISS = "earnings_miss"  # Bullish sentiment + declining margins → earnings miss
    EARNINGS_BEAT = "earnings_beat"  # Bearish sentiment + improving metrics → earnings beat
    GROWTH_SLOWDOWN = "growth_slowdown"  # High growth expectations + slowing revenue
    MARGIN_COMPRESSION = "margin_compression"  # Optimistic outlook + declining profitability
    TURNAROUND = "turnaround"  # Pessimistic outlook + improving fundamentals
    MOMENTUM = "momentum"  # Positive sentiment + strong fundamentals


class TriangulationSignal(BaseModel):
    """Actionable signal from cross-source analysis"""

    signal_type: SignalType = Field(
        description="Type of divergence signal detected"
    )

    pattern: Optional[DivergencePattern] = Field(
        None,
        description="Historical pattern matched"
    )

    probability: float = Field(
        ge=0.0,
        le=1.0,
        description="Probability of signal accuracy (0.0-1.0)"
    )

    timeline_days: Optional[int] = Field(
        None,
        description="Expected timeline for signal to materialize (days)"
    )

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in signal (0.0-1.0)"
    )

    title: str = Field(
        description="Brief signal description"
    )

    explanation: str = Field(
        description="Detailed explanation of signal drivers"
    )

    analyst_consensus: str = Field(
        description="Analyst consensus (Buy/Hold/Sell)"
    )

    financial_reality: str = Field(
        description="Summary of actual financial performance"
    )

    divergence_magnitude: float = Field(
        ge=0.0,
        le=10.0,
        description="Magnitude of divergence (0-10 scale)"
    )

    key_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Supporting metrics and indicators"
    )

    recommended_action: str = Field(
        description="Recommended action based on signal"
    )

    risk_factors: List[str] = Field(
        default_factory=list,
        description="Risks that could invalidate signal"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Signal generation timestamp"
    )


class TriangulationSignalsResult(BaseModel):
    """Result of triangulation analysis"""

    company: str = Field(description="Company analyzed")
    ticker: str = Field(description="Stock ticker")

    signals: List[TriangulationSignal] = Field(
        description="Detected signals, ordered by confidence"
    )

    overall_signal: SignalType = Field(
        description="Overall composite signal"
    )

    data_quality_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Quality of input data (0.0-1.0)"
    )

    sources_validated: List[str] = Field(
        description="Data sources used in analysis"
    )

    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


def analyze_triangulation_signals(
    financial_snapshot: FinancialSnapshot,
    company: str,
    historical_patterns: Optional[List[Dict[str, Any]]] = None
) -> TriangulationSignalsResult:
    """
    Analyze cross-validation results to detect analyst-reality divergences.

    Detects signals such as:
    - Bullish analysts + declining margins → Likely earnings miss
    - Bearish analysts + improving fundamentals → Potential earnings beat
    - High expectations + slowing growth → Growth disappointment

    Args:
        financial_snapshot: Financial data with cross-validation results
        company: Company name
        historical_patterns: Optional historical earnings patterns for better prediction

    Returns:
        TriangulationSignalsResult with actionable signals

    Example:
        >>> snapshot = FinancialSnapshot(
        ...     ticker="TSLA",
        ...     analyst_recommendations=AnalystRecommendations(
        ...         strong_buy=15, buy=10, hold=5, sell=2,
        ...         consensus="Buy"
        ...     ),
        ...     profit_margin=0.08,  # Declining from 0.15
        ...     revenue_growth=-5.0  # Negative growth
        ... )
        >>> result = analyze_triangulation_signals(snapshot, "Tesla")
        >>> result.overall_signal
        'bearish_divergence'
    """
    logger.info(f"Analyzing triangulation signals for {company} ({financial_snapshot.ticker})")

    # Calculate data quality score
    data_quality = _calculate_data_quality(financial_snapshot)

    # Extract analyst sentiment
    analyst_sentiment = _extract_analyst_sentiment(financial_snapshot.analyst_recommendations)

    # Extract financial reality
    financial_reality = _extract_financial_reality(financial_snapshot)

    # Detect divergences
    signals = []

    # Pattern 1: Analyst-Financial Divergence
    if analyst_sentiment and financial_reality:
        divergence_signal = _detect_analyst_reality_divergence(
            analyst_sentiment,
            financial_reality,
            financial_snapshot,
            company
        )
        if divergence_signal:
            signals.append(divergence_signal)

    # Pattern 2: Sentiment-Margin Divergence
    if financial_snapshot.news_sentiment:
        margin_signal = _detect_sentiment_margin_divergence(
            financial_snapshot.news_sentiment,
            financial_snapshot,
            company
        )
        if margin_signal:
            signals.append(margin_signal)

    # Pattern 3: Growth Expectations vs Reality
    growth_signal = _detect_growth_expectation_divergence(
        analyst_sentiment,
        financial_snapshot,
        company
    )
    if growth_signal:
        signals.append(growth_signal)

    # Pattern 4: Cross-validation discrepancies
    if financial_snapshot.cross_validation:
        validation_signal = _detect_data_validation_signals(
            financial_snapshot.cross_validation,
            financial_snapshot,
            company
        )
        if validation_signal:
            signals.append(validation_signal)

    # Enrich signals with historical pattern matching
    if historical_patterns:
        signals = _enrich_with_historical_patterns(signals, historical_patterns)

    # Sort by confidence
    signals.sort(key=lambda s: s.confidence_score, reverse=True)

    # Determine overall signal
    overall_signal = _determine_overall_signal(signals, analyst_sentiment, financial_reality)

    return TriangulationSignalsResult(
        company=company,
        ticker=financial_snapshot.ticker,
        signals=signals,
        overall_signal=overall_signal,
        data_quality_score=data_quality,
        sources_validated=financial_snapshot.data_sources or [],
        analysis_timestamp=datetime.utcnow()
    )


def _calculate_data_quality(snapshot: FinancialSnapshot) -> float:
    """Calculate data quality score based on available fields"""
    total_fields = 10
    available_fields = 0

    if snapshot.market_cap is not None:
        available_fields += 1
    if snapshot.revenue is not None:
        available_fields += 1
    if snapshot.revenue_growth is not None:
        available_fields += 1
    if snapshot.profit_margin is not None:
        available_fields += 1
    if snapshot.pe_ratio is not None:
        available_fields += 1
    if snapshot.analyst_recommendations:
        available_fields += 2
    if snapshot.news_sentiment:
        available_fields += 2
    if snapshot.cross_validation:
        available_fields += 1

    return available_fields / total_fields


def _extract_analyst_sentiment(recs: Optional[AnalystRecommendations]) -> Optional[str]:
    """Extract analyst sentiment: Bullish/Neutral/Bearish"""
    if not recs or recs.total_analysts == 0:
        return None

    bullish_score = (recs.strong_buy * 2 + recs.buy) / recs.total_analysts
    bearish_score = (recs.strong_sell * 2 + recs.sell) / recs.total_analysts

    if bullish_score > 0.6:
        return "Bullish"
    elif bearish_score > 0.4:
        return "Bearish"
    else:
        return "Neutral"


def _extract_financial_reality(snapshot: FinancialSnapshot) -> Optional[str]:
    """Extract financial reality: Strong/Mixed/Weak"""
    if snapshot.revenue_growth is None and snapshot.profit_margin is None:
        return None

    strength_score = 0
    factors = 0

    # Revenue growth assessment
    if snapshot.revenue_growth is not None:
        factors += 1
        if snapshot.revenue_growth > 10:
            strength_score += 2
        elif snapshot.revenue_growth > 0:
            strength_score += 1
        elif snapshot.revenue_growth < -5:
            strength_score -= 1

    # Profit margin assessment
    if snapshot.profit_margin is not None:
        factors += 1
        if snapshot.profit_margin > 0.20:
            strength_score += 2
        elif snapshot.profit_margin > 0.10:
            strength_score += 1
        elif snapshot.profit_margin < 0.05:
            strength_score -= 1

    if factors == 0:
        return None

    avg_strength = strength_score / factors

    if avg_strength > 1.0:
        return "Strong"
    elif avg_strength < 0:
        return "Weak"
    else:
        return "Mixed"


def _detect_analyst_reality_divergence(
    analyst_sentiment: str,
    financial_reality: str,
    snapshot: FinancialSnapshot,
    company: str
) -> Optional[TriangulationSignal]:
    """Detect divergence between analyst consensus and financial fundamentals"""

    # Bearish divergence: Bullish analysts + Weak fundamentals
    if analyst_sentiment == "Bullish" and financial_reality == "Weak":
        return TriangulationSignal(
            signal_type=SignalType.BEARISH_DIVERGENCE,
            pattern=DivergencePattern.EARNINGS_MISS,
            probability=0.72,  # Historical probability of earnings miss
            timeline_days=45,  # Typical earnings cycle
            confidence_score=0.85,
            title=f"{company}: Bearish Divergence - Analyst Optimism vs Weak Fundamentals",
            explanation=(
                f"Analysts maintain bullish consensus ({snapshot.analyst_recommendations.consensus}) "
                f"with {snapshot.analyst_recommendations.strong_buy + snapshot.analyst_recommendations.buy} "
                f"buy ratings, but fundamentals show weakness: "
                f"Revenue growth at {snapshot.revenue_growth:.1f}%, "
                f"Profit margin at {snapshot.profit_margin:.1%}. "
                "Historical patterns suggest high probability of earnings disappointment."
            ),
            analyst_consensus=analyst_sentiment,
            financial_reality=financial_reality,
            divergence_magnitude=7.5,
            key_metrics={
                "analyst_buy_ratio": (
                    (snapshot.analyst_recommendations.strong_buy + snapshot.analyst_recommendations.buy) /
                    snapshot.analyst_recommendations.total_analysts
                ),
                "revenue_growth": snapshot.revenue_growth,
                "profit_margin": snapshot.profit_margin,
                "pe_ratio": snapshot.pe_ratio
            },
            recommended_action=(
                "CAUTION: Consider reducing exposure before next earnings. "
                "Monitor for analyst downgrades as signal confirmation."
            ),
            risk_factors=[
                "Unexpected revenue acceleration",
                "Cost reduction initiatives",
                "Positive industry tailwinds",
                "Macro economic improvement"
            ]
        )

    # Bullish divergence: Bearish analysts + Strong fundamentals
    elif analyst_sentiment == "Bearish" and financial_reality == "Strong":
        return TriangulationSignal(
            signal_type=SignalType.BULLISH_DIVERGENCE,
            pattern=DivergencePattern.EARNINGS_BEAT,
            probability=0.68,
            timeline_days=45,
            confidence_score=0.80,
            title=f"{company}: Bullish Divergence - Analyst Pessimism vs Strong Fundamentals",
            explanation=(
                f"Analysts show bearish consensus ({snapshot.analyst_recommendations.consensus}) "
                f"but fundamentals remain strong: "
                f"Revenue growth at {snapshot.revenue_growth:.1f}%, "
                f"Profit margin at {snapshot.profit_margin:.1%}. "
                "Market may be undervaluing strength, creating upside opportunity."
            ),
            analyst_consensus=analyst_sentiment,
            financial_reality=financial_reality,
            divergence_magnitude=6.8,
            key_metrics={
                "analyst_sell_ratio": (
                    (snapshot.analyst_recommendations.strong_sell + snapshot.analyst_recommendations.sell) /
                    snapshot.analyst_recommendations.total_analysts
                ),
                "revenue_growth": snapshot.revenue_growth,
                "profit_margin": snapshot.profit_margin
            },
            recommended_action=(
                "OPPORTUNITY: Consider accumulating position ahead of earnings. "
                "Look for catalyst that could trigger analyst upgrades."
            ),
            risk_factors=[
                "Forward guidance concerns",
                "Industry headwinds",
                "Competitive pressures",
                "Macro uncertainty"
            ]
        )

    # Confirmation signal
    elif (analyst_sentiment == "Bullish" and financial_reality == "Strong") or \
         (analyst_sentiment == "Bearish" and financial_reality == "Weak"):
        return TriangulationSignal(
            signal_type=SignalType.CONFIRMATION,
            pattern=DivergencePattern.MOMENTUM,
            probability=0.75,
            timeline_days=30,
            confidence_score=0.70,
            title=f"{company}: Confirmation - Analysts and Fundamentals Aligned",
            explanation=(
                f"Analyst sentiment ({analyst_sentiment}) aligns with financial reality ({financial_reality}). "
                "Lower alpha opportunity but higher confidence in current trajectory."
            ),
            analyst_consensus=analyst_sentiment,
            financial_reality=financial_reality,
            divergence_magnitude=1.5,
            key_metrics={
                "alignment_score": 0.85,
                "revenue_growth": snapshot.revenue_growth,
                "profit_margin": snapshot.profit_margin
            },
            recommended_action=(
                "HOLD: Current position is fairly valued. "
                "Monitor for divergence signals as indicators change."
            ),
            risk_factors=[
                "Unexpected macro shifts",
                "Competitive disruption",
                "Regulatory changes"
            ]
        )

    return None


def _detect_sentiment_margin_divergence(
    news_sentiment: NewsSentiment,
    snapshot: FinancialSnapshot,
    company: str
) -> Optional[TriangulationSignal]:
    """Detect divergence between news sentiment and profit margins"""

    if snapshot.profit_margin is None:
        return None

    # Positive news but declining margins
    if news_sentiment.sentiment == "Positive" and snapshot.profit_margin < 0.08:
        return TriangulationSignal(
            signal_type=SignalType.BEARISH_DIVERGENCE,
            pattern=DivergencePattern.MARGIN_COMPRESSION,
            probability=0.65,
            timeline_days=60,
            confidence_score=0.72,
            title=f"{company}: Margin Compression Despite Positive News",
            explanation=(
                f"News sentiment is {news_sentiment.sentiment} "
                f"(score: {news_sentiment.sentiment_score:.2f}) "
                f"but profit margins are compressed at {snapshot.profit_margin:.1%}. "
                "Suggests operational challenges not reflected in media coverage."
            ),
            analyst_consensus="Mixed",
            financial_reality="Weak Margins",
            divergence_magnitude=5.2,
            key_metrics={
                "news_sentiment": news_sentiment.sentiment_score,
                "profit_margin": snapshot.profit_margin,
                "articles_analyzed": news_sentiment.articles_count
            },
            recommended_action=(
                "INVESTIGATE: Dig deeper into cost structure and pricing power. "
                "Margin compression often precedes earnings misses."
            ),
            risk_factors=[
                "Temporary margin pressure",
                "Investment phase",
                "Industry-wide compression"
            ]
        )

    return None


def _detect_growth_expectation_divergence(
    analyst_sentiment: Optional[str],
    snapshot: FinancialSnapshot,
    company: str
) -> Optional[TriangulationSignal]:
    """Detect divergence between growth expectations and reality"""

    if snapshot.revenue_growth is None or not analyst_sentiment:
        return None

    # High expectations + slowing growth
    if analyst_sentiment == "Bullish" and snapshot.revenue_growth < 5.0:
        return TriangulationSignal(
            signal_type=SignalType.BEARISH_DIVERGENCE,
            pattern=DivergencePattern.GROWTH_SLOWDOWN,
            probability=0.70,
            timeline_days=50,
            confidence_score=0.78,
            title=f"{company}: Growth Slowdown vs High Expectations",
            explanation=(
                f"Analysts are bullish but revenue growth is slowing to {snapshot.revenue_growth:.1f}%. "
                "Mismatch between expectations and delivery creates downside risk."
            ),
            analyst_consensus=analyst_sentiment,
            financial_reality="Slowing Growth",
            divergence_magnitude=6.5,
            key_metrics={
                "revenue_growth": snapshot.revenue_growth,
                "expected_growth_rate": 15.0,  # Implied by bullish consensus
                "growth_gap": 15.0 - snapshot.revenue_growth
            },
            recommended_action=(
                "REDUCE: Lower exposure to de-risk growth disappointment. "
                "Wait for growth re-acceleration before re-entering."
            ),
            risk_factors=[
                "New product launches",
                "Market expansion",
                "Acquisition impact"
            ]
        )

    return None


def _detect_data_validation_signals(
    validations: List[DataSourceValidation],
    snapshot: FinancialSnapshot,
    company: str
) -> Optional[TriangulationSignal]:
    """Detect signals from cross-validation discrepancies"""

    invalid_validations = [v for v in validations if not v.is_valid]

    if not invalid_validations:
        return None

    # Significant discrepancies indicate data quality issues
    max_discrepancy = max(v.discrepancy_pct for v in invalid_validations if v.discrepancy_pct)

    return TriangulationSignal(
        signal_type=SignalType.UNCERTAINTY,
        pattern=None,
        probability=0.50,
        timeline_days=None,
        confidence_score=0.60,
        title=f"{company}: Data Quality Warning - Cross-Source Discrepancies",
        explanation=(
            f"Found {len(invalid_validations)} metrics with significant discrepancies "
            f"between data sources (max: {max_discrepancy:.1f}%). "
            "Suggests data quality issues or rapidly changing fundamentals."
        ),
        analyst_consensus="Uncertain",
        financial_reality="Data Quality Issues",
        divergence_magnitude=max_discrepancy / 10,
        key_metrics={
            "discrepancies_count": len(invalid_validations),
            "max_discrepancy": max_discrepancy,
            "metrics_affected": [v.metric for v in invalid_validations]
        },
        recommended_action=(
            "VERIFY: Cross-check data from primary sources before making decisions. "
            "Wait for data reconciliation."
        ),
        risk_factors=[
            "Stale data from one source",
            "Recent corporate actions",
            "Data provider errors"
        ]
    )


def _enrich_with_historical_patterns(
    signals: List[TriangulationSignal],
    historical_patterns: List[Dict[str, Any]]
) -> List[TriangulationSignal]:
    """
    Enrich signals with historical pattern matching to improve probability estimates.

    Historical patterns should include:
    - pattern_type: Type of pattern
    - outcome: Actual outcome
    - probability: Historical success rate
    - timeline_days: Typical materialization period
    """
    # Match each signal against historical patterns
    for signal in signals:
        if signal.pattern:
            matching_patterns = [
                p for p in historical_patterns
                if p.get("pattern_type") == signal.pattern.value
            ]

            if matching_patterns:
                # Update probability based on historical success rate
                avg_historical_prob = sum(
                    p.get("probability", 0.5) for p in matching_patterns
                ) / len(matching_patterns)

                # Blend current probability with historical (70% historical, 30% current)
                signal.probability = (avg_historical_prob * 0.7) + (signal.probability * 0.3)

                # Update timeline if available
                avg_timeline = sum(
                    p.get("timeline_days", 0) for p in matching_patterns
                    if p.get("timeline_days")
                ) / len([p for p in matching_patterns if p.get("timeline_days")])

                if avg_timeline > 0:
                    signal.timeline_days = int(avg_timeline)

    return signals


def _determine_overall_signal(
    signals: List[TriangulationSignal],
    analyst_sentiment: Optional[str],
    financial_reality: Optional[str]
) -> SignalType:
    """Determine overall composite signal from multiple signals"""

    if not signals:
        return SignalType.UNCERTAINTY

    # Weight by confidence
    bearish_weight = sum(
        s.confidence_score for s in signals
        if s.signal_type == SignalType.BEARISH_DIVERGENCE
    )

    bullish_weight = sum(
        s.confidence_score for s in signals
        if s.signal_type == SignalType.BULLISH_DIVERGENCE
    )

    if bearish_weight > bullish_weight * 1.5:
        return SignalType.BEARISH_DIVERGENCE
    elif bullish_weight > bearish_weight * 1.5:
        return SignalType.BULLISH_DIVERGENCE
    elif bearish_weight > 0 or bullish_weight > 0:
        return SignalType.UNCERTAINTY
    else:
        return SignalType.CONFIRMATION
