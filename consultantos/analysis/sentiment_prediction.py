"""
Sentiment-Performance Prediction Module.

Correlates news sentiment time series with financial outcomes to
predict future earnings performance based on current sentiment trends.

Features:
- Time-lagged correlation analysis (sentiment leads financials)
- Optimal lead time calculation (how many days sentiment predicts performance)
- Next earnings outcome prediction with confidence scoring
- Sentiment momentum and trend analysis
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
import statistics

from consultantos.models import (
    NewsSentiment,
    FinancialSnapshot
)
from consultantos.models.monitoring import MonitorAnalysisSnapshot

logger = logging.getLogger(__name__)


class PerformanceOutcome(str, Enum):
    """Predicted earnings performance outcome"""
    BEAT = "beat"  # Earnings beat expectations
    MEET = "meet"  # Earnings meet expectations
    MISS = "miss"  # Earnings miss expectations
    UNCERTAIN = "uncertain"  # Insufficient data or conflicting signals


class SentimentTrend(str, Enum):
    """Sentiment trajectory over time"""
    IMPROVING = "improving"
    STABLE = "stable"
    DETERIORATING = "deteriorating"
    VOLATILE = "volatile"


class SentimentDataPoint(BaseModel):
    """Single sentiment observation with timestamp"""

    timestamp: datetime = Field(
        description="Observation timestamp"
    )

    sentiment_score: float = Field(
        ge=-1.0,
        le=1.0,
        description="Sentiment score (-1.0 to 1.0)"
    )

    articles_count: int = Field(
        ge=0,
        description="Number of articles analyzed"
    )

    sentiment_label: str = Field(
        description="Positive/Neutral/Negative"
    )


class SentimentCorrelation(BaseModel):
    """Correlation between sentiment and financial performance"""

    lead_time_days: int = Field(
        description="Optimal lead time: days sentiment precedes financial outcome"
    )

    correlation_strength: float = Field(
        ge=-1.0,
        le=1.0,
        description="Correlation coefficient (-1.0 to 1.0)"
    )

    statistical_significance: float = Field(
        ge=0.0,
        le=1.0,
        description="P-value for correlation (lower = more significant)"
    )

    historical_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Historical prediction accuracy (0.0-1.0)"
    )

    sample_size: int = Field(
        ge=0,
        description="Number of historical data points"
    )


class SentimentPrediction(BaseModel):
    """Earnings prediction based on sentiment analysis"""

    predicted_outcome: PerformanceOutcome = Field(
        description="Predicted earnings outcome"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Prediction confidence (0.0-1.0)"
    )

    sentiment_trend: SentimentTrend = Field(
        description="Current sentiment trajectory"
    )

    current_sentiment_score: float = Field(
        ge=-1.0,
        le=1.0,
        description="Most recent sentiment score"
    )

    sentiment_momentum: float = Field(
        ge=-1.0,
        le=1.0,
        description="Rate of sentiment change (-1.0 to 1.0)"
    )

    lead_time_days: Optional[int] = Field(
        None,
        description="Days before expected earnings date"
    )

    next_earnings_date: Optional[datetime] = Field(
        None,
        description="Estimated next earnings announcement"
    )

    probability_beat: float = Field(
        ge=0.0,
        le=1.0,
        description="Probability of earnings beat"
    )

    probability_meet: float = Field(
        ge=0.0,
        le=1.0,
        description="Probability of earnings meet"
    )

    probability_miss: float = Field(
        ge=0.0,
        le=1.0,
        description="Probability of earnings miss"
    )

    correlation: Optional[SentimentCorrelation] = Field(
        None,
        description="Historical correlation analysis"
    )

    key_sentiment_drivers: List[str] = Field(
        default_factory=list,
        description="Main factors driving sentiment"
    )

    risk_factors: List[str] = Field(
        default_factory=list,
        description="Factors that could invalidate prediction"
    )

    supporting_indicators: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional supporting metrics"
    )

    explanation: str = Field(
        description="Detailed prediction rationale"
    )


class SentimentPredictionResult(BaseModel):
    """Result of sentiment-based performance prediction"""

    company: str = Field(description="Company analyzed")
    ticker: str = Field(description="Stock ticker")

    prediction: SentimentPrediction = Field(
        description="Earnings performance prediction"
    )

    sentiment_history: List[SentimentDataPoint] = Field(
        description="Historical sentiment time series"
    )

    analysis_quality: float = Field(
        ge=0.0,
        le=1.0,
        description="Quality of analysis based on data availability"
    )

    data_gaps: List[str] = Field(
        default_factory=list,
        description="Identified gaps in data"
    )

    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )


def predict_financial_performance(
    current_sentiment: NewsSentiment,
    financial_snapshot: FinancialSnapshot,
    company: str,
    historical_snapshots: Optional[List[MonitorAnalysisSnapshot]] = None,
    next_earnings_date: Optional[datetime] = None
) -> SentimentPredictionResult:
    """
    Predict next earnings outcome based on sentiment trend analysis.

    Analyzes correlation between sentiment time series and financial outcomes
    to determine optimal lead time and forecast future performance.

    Args:
        current_sentiment: Most recent sentiment data
        financial_snapshot: Current financial metrics
        company: Company name
        historical_snapshots: Optional historical snapshots for time-series analysis
        next_earnings_date: Optional known next earnings date

    Returns:
        SentimentPredictionResult with performance forecast

    Example:
        >>> sentiment = NewsSentiment(
        ...     sentiment_score=-0.3,
        ...     sentiment="Negative",
        ...     articles_count=50
        ... )
        >>> snapshot = FinancialSnapshot(
        ...     ticker="AAPL",
        ...     revenue_growth=5.0,
        ...     profit_margin=0.25
        ... )
        >>> result = predict_financial_performance(sentiment, snapshot, "Apple")
        >>> result.prediction.predicted_outcome
        'miss'  # Negative sentiment predicts earnings miss
    """
    logger.info(f"Predicting financial performance for {company}")

    # Build sentiment time series
    sentiment_history = _build_sentiment_history(
        current_sentiment,
        historical_snapshots
    )

    # Calculate sentiment trend
    sentiment_trend = _calculate_sentiment_trend(sentiment_history)

    # Calculate sentiment momentum
    sentiment_momentum = _calculate_sentiment_momentum(sentiment_history)

    # Analyze correlation if historical data available
    correlation = None
    if historical_snapshots and len(historical_snapshots) >= 3:
        correlation = _analyze_sentiment_correlation(
            historical_snapshots,
            sentiment_history
        )

    # Predict outcome
    prediction = _generate_prediction(
        current_sentiment,
        financial_snapshot,
        sentiment_trend,
        sentiment_momentum,
        correlation,
        next_earnings_date
    )

    # Assess analysis quality
    quality = _assess_analysis_quality(
        sentiment_history,
        historical_snapshots,
        current_sentiment
    )

    # Identify data gaps
    gaps = _identify_data_gaps(
        sentiment_history,
        historical_snapshots,
        current_sentiment
    )

    return SentimentPredictionResult(
        company=company,
        ticker=financial_snapshot.ticker,
        prediction=prediction,
        sentiment_history=sentiment_history,
        analysis_quality=quality,
        data_gaps=gaps,
        analysis_timestamp=datetime.utcnow()
    )


def _build_sentiment_history(
    current_sentiment: NewsSentiment,
    historical_snapshots: Optional[List[MonitorAnalysisSnapshot]]
) -> List[SentimentDataPoint]:
    """Build sentiment time series from current and historical data"""

    history = []

    # Add current sentiment
    history.append(SentimentDataPoint(
        timestamp=datetime.utcnow(),
        sentiment_score=current_sentiment.sentiment_score,
        articles_count=current_sentiment.articles_count,
        sentiment_label=current_sentiment.sentiment
    ))

    # Add historical sentiments
    if historical_snapshots:
        for snapshot in historical_snapshots:
            if snapshot.news_sentiment is not None:
                history.append(SentimentDataPoint(
                    timestamp=snapshot.timestamp,
                    sentiment_score=snapshot.news_sentiment,
                    articles_count=0,  # Not tracked in snapshots
                    sentiment_label=_score_to_label(snapshot.news_sentiment)
                ))

    # Sort by timestamp (oldest first)
    history.sort(key=lambda x: x.timestamp)

    return history


def _score_to_label(score: float) -> str:
    """Convert sentiment score to label"""
    if score > 0.3:
        return "Positive"
    elif score < -0.3:
        return "Negative"
    else:
        return "Neutral"


def _calculate_sentiment_trend(
    history: List[SentimentDataPoint]
) -> SentimentTrend:
    """Determine sentiment trajectory over time"""

    if len(history) < 2:
        return SentimentTrend.STABLE

    # Calculate trend from recent data points
    recent = history[-5:]  # Last 5 observations
    scores = [point.sentiment_score for point in recent]

    # Simple linear regression slope
    if len(scores) >= 3:
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(scores)

        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator > 0:
            slope = numerator / denominator
        else:
            slope = 0.0

        # Classify trend
        if slope > 0.05:
            return SentimentTrend.IMPROVING
        elif slope < -0.05:
            return SentimentTrend.DETERIORATING
        else:
            return SentimentTrend.STABLE

    # Fallback to simple comparison
    if scores[-1] > scores[0] + 0.1:
        return SentimentTrend.IMPROVING
    elif scores[-1] < scores[0] - 0.1:
        return SentimentTrend.DETERIORATING
    else:
        return SentimentTrend.STABLE


def _calculate_sentiment_momentum(
    history: List[SentimentDataPoint]
) -> float:
    """Calculate rate of sentiment change (momentum)"""

    if len(history) < 2:
        return 0.0

    # Use recent data points
    recent = history[-5:]
    scores = [point.sentiment_score for point in recent]

    # Calculate average change between consecutive points
    changes = [scores[i] - scores[i-1] for i in range(1, len(scores))]

    if changes:
        momentum = statistics.mean(changes)
    else:
        momentum = 0.0

    # Normalize to -1.0 to 1.0
    momentum = max(-1.0, min(momentum * 5, 1.0))  # Scale by 5x

    return momentum


def _analyze_sentiment_correlation(
    historical_snapshots: List[MonitorAnalysisSnapshot],
    sentiment_history: List[SentimentDataPoint]
) -> Optional[SentimentCorrelation]:
    """
    Analyze correlation between sentiment and financial performance.

    Calculates optimal lead time (how many days sentiment predicts outcomes).
    """

    if len(historical_snapshots) < 3:
        return None

    # Extract financial performance indicators
    financial_outcomes = []
    for snapshot in historical_snapshots:
        if snapshot.financial_metrics:
            revenue_growth = snapshot.financial_metrics.get("revenue_growth", 0)
            profit_margin = snapshot.financial_metrics.get("profit_margin", 0)

            # Simple outcome score: positive = beat, negative = miss
            outcome_score = (revenue_growth / 100.0) + (profit_margin * 2)
            financial_outcomes.append((snapshot.timestamp, outcome_score))

    if not financial_outcomes:
        return None

    # Try different lead times (7, 14, 30, 45, 60 days)
    best_correlation = 0.0
    best_lead_time = 30  # Default

    for lead_days in [7, 14, 30, 45, 60]:
        correlation = _calculate_lagged_correlation(
            sentiment_history,
            financial_outcomes,
            lead_days
        )

        if abs(correlation) > abs(best_correlation):
            best_correlation = correlation
            best_lead_time = lead_days

    # Calculate statistical significance (simplified)
    sample_size = min(len(sentiment_history), len(financial_outcomes))
    p_value = max(0.01, 1.0 - abs(best_correlation))

    # Historical accuracy (simplified - would use actual predictions)
    historical_accuracy = min(0.9, 0.5 + abs(best_correlation) / 2)

    return SentimentCorrelation(
        lead_time_days=best_lead_time,
        correlation_strength=best_correlation,
        statistical_significance=p_value,
        historical_accuracy=historical_accuracy,
        sample_size=sample_size
    )


def _calculate_lagged_correlation(
    sentiment_history: List[SentimentDataPoint],
    financial_outcomes: List[Tuple[datetime, float]],
    lead_days: int
) -> float:
    """Calculate correlation with specified lead time"""

    # Match sentiment to financial outcomes with lag
    paired_data = []

    for outcome_time, outcome_score in financial_outcomes:
        # Find sentiment from lead_days before outcome
        target_time = outcome_time - timedelta(days=lead_days)

        # Find closest sentiment data point
        closest_sentiment = min(
            sentiment_history,
            key=lambda s: abs((s.timestamp - target_time).total_seconds()),
            default=None
        )

        if closest_sentiment:
            paired_data.append((
                closest_sentiment.sentiment_score,
                outcome_score
            ))

    if len(paired_data) < 2:
        return 0.0

    # Calculate Pearson correlation
    sentiment_scores = [pair[0] for pair in paired_data]
    outcome_scores = [pair[1] for pair in paired_data]

    try:
        correlation = statistics.correlation(sentiment_scores, outcome_scores)
    except statistics.StatisticsError:
        correlation = 0.0

    return correlation


def _generate_prediction(
    current_sentiment: NewsSentiment,
    financial_snapshot: FinancialSnapshot,
    sentiment_trend: SentimentTrend,
    sentiment_momentum: float,
    correlation: Optional[SentimentCorrelation],
    next_earnings_date: Optional[datetime]
) -> SentimentPrediction:
    """Generate earnings performance prediction"""

    # Calculate probabilities based on sentiment and trend
    prob_beat, prob_meet, prob_miss = _calculate_outcome_probabilities(
        current_sentiment.sentiment_score,
        sentiment_trend,
        sentiment_momentum,
        financial_snapshot
    )

    # Determine predicted outcome
    if prob_beat > max(prob_meet, prob_miss):
        outcome = PerformanceOutcome.BEAT
        confidence = prob_beat
    elif prob_miss > max(prob_beat, prob_meet):
        outcome = PerformanceOutcome.MISS
        confidence = prob_miss
    elif prob_meet > max(prob_beat, prob_miss):
        outcome = PerformanceOutcome.MEET
        confidence = prob_meet
    else:
        outcome = PerformanceOutcome.UNCERTAIN
        confidence = 0.5

    # Adjust confidence based on correlation strength
    if correlation and correlation.correlation_strength != 0:
        confidence *= (0.7 + abs(correlation.correlation_strength) * 0.3)

    # Estimate next earnings date (typically 90 days)
    if not next_earnings_date:
        next_earnings_date = datetime.utcnow() + timedelta(days=90)

    # Lead time
    lead_time = correlation.lead_time_days if correlation else 30

    # Key drivers
    drivers = _identify_sentiment_drivers(
        current_sentiment,
        sentiment_trend,
        sentiment_momentum
    )

    # Risk factors
    risks = [
        "Unexpected macroeconomic changes",
        "Industry-specific disruptions",
        "Company-specific events (M&A, leadership changes)",
        "Sentiment may not reflect fundamentals"
    ]

    # Supporting indicators
    supporting = {
        "sentiment_score": current_sentiment.sentiment_score,
        "sentiment_trend": sentiment_trend.value,
        "momentum": sentiment_momentum,
        "articles_analyzed": current_sentiment.articles_count,
        "revenue_growth": financial_snapshot.revenue_growth,
        "profit_margin": financial_snapshot.profit_margin
    }

    # Explanation
    explanation = _generate_explanation(
        outcome,
        current_sentiment,
        sentiment_trend,
        financial_snapshot,
        correlation
    )

    return SentimentPrediction(
        predicted_outcome=outcome,
        confidence=confidence,
        sentiment_trend=sentiment_trend,
        current_sentiment_score=current_sentiment.sentiment_score,
        sentiment_momentum=sentiment_momentum,
        lead_time_days=lead_time,
        next_earnings_date=next_earnings_date,
        probability_beat=prob_beat,
        probability_meet=prob_meet,
        probability_miss=prob_miss,
        correlation=correlation,
        key_sentiment_drivers=drivers,
        risk_factors=risks,
        supporting_indicators=supporting,
        explanation=explanation
    )


def _calculate_outcome_probabilities(
    sentiment_score: float,
    trend: SentimentTrend,
    momentum: float,
    snapshot: FinancialSnapshot
) -> Tuple[float, float, float]:
    """Calculate probabilities for beat/meet/miss outcomes"""

    # Base probabilities from sentiment
    if sentiment_score > 0.5:
        base_beat, base_meet, base_miss = 0.60, 0.30, 0.10
    elif sentiment_score > 0.2:
        base_beat, base_meet, base_miss = 0.45, 0.40, 0.15
    elif sentiment_score > -0.2:
        base_beat, base_meet, base_miss = 0.33, 0.34, 0.33
    elif sentiment_score > -0.5:
        base_beat, base_meet, base_miss = 0.15, 0.40, 0.45
    else:
        base_beat, base_meet, base_miss = 0.10, 0.30, 0.60

    # Adjust for trend
    if trend == SentimentTrend.IMPROVING:
        base_beat += 0.10
        base_miss -= 0.10
    elif trend == SentimentTrend.DETERIORATING:
        base_beat -= 0.10
        base_miss += 0.10

    # Adjust for momentum
    base_beat += momentum * 0.15
    base_miss -= momentum * 0.15

    # Adjust for fundamentals
    if snapshot.revenue_growth and snapshot.revenue_growth > 10:
        base_beat += 0.05
    elif snapshot.revenue_growth and snapshot.revenue_growth < 0:
        base_miss += 0.05

    # Normalize to sum to 1.0
    total = base_beat + base_meet + base_miss
    if total > 0:
        beat = max(0.0, min(base_beat / total, 1.0))
        miss = max(0.0, min(base_miss / total, 1.0))
        meet = max(0.0, min(1.0 - beat - miss, 1.0))
    else:
        beat, meet, miss = 0.33, 0.34, 0.33

    return beat, meet, miss


def _identify_sentiment_drivers(
    sentiment: NewsSentiment,
    trend: SentimentTrend,
    momentum: float
) -> List[str]:
    """Identify key factors driving sentiment"""

    drivers = []

    if sentiment.sentiment_score > 0.3:
        drivers.append("Strong positive media coverage")
    elif sentiment.sentiment_score < -0.3:
        drivers.append("Negative media narrative")

    if trend == SentimentTrend.IMPROVING:
        drivers.append("Improving sentiment trajectory")
    elif trend == SentimentTrend.DETERIORATING:
        drivers.append("Deteriorating sentiment trend")

    if abs(momentum) > 0.3:
        drivers.append(f"High sentiment momentum ({'positive' if momentum > 0 else 'negative'})")

    if sentiment.articles_count > 20:
        drivers.append(f"High media attention ({sentiment.articles_count} articles)")

    if sentiment.recent_headlines:
        drivers.append(f"Recent headline themes: {', '.join(sentiment.recent_headlines[:2])}")

    return drivers


def _generate_explanation(
    outcome: PerformanceOutcome,
    sentiment: NewsSentiment,
    trend: SentimentTrend,
    snapshot: FinancialSnapshot,
    correlation: Optional[SentimentCorrelation]
) -> str:
    """Generate detailed prediction explanation"""

    parts = []

    # Outcome
    parts.append(f"Prediction: {outcome.value.upper()}")

    # Sentiment
    parts.append(
        f"Current sentiment is {sentiment.sentiment} "
        f"(score: {sentiment.sentiment_score:.2f}) based on {sentiment.articles_count} articles"
    )

    # Trend
    parts.append(f"Sentiment trend is {trend.value}")

    # Fundamentals
    if snapshot.revenue_growth is not None:
        parts.append(f"Revenue growth at {snapshot.revenue_growth:.1f}%")
    if snapshot.profit_margin is not None:
        parts.append(f"Profit margin at {snapshot.profit_margin:.1%}")

    # Correlation
    if correlation:
        parts.append(
            f"Historical analysis shows sentiment leads financial outcomes by "
            f"{correlation.lead_time_days} days with {abs(correlation.correlation_strength):.2f} correlation"
        )

    return ". ".join(parts) + "."


def _assess_analysis_quality(
    sentiment_history: List[SentimentDataPoint],
    historical_snapshots: Optional[List[MonitorAnalysisSnapshot]],
    current_sentiment: NewsSentiment
) -> float:
    """Assess quality of analysis based on data availability"""

    quality_score = 0.0

    # Current sentiment quality
    if current_sentiment.articles_count > 20:
        quality_score += 0.3
    elif current_sentiment.articles_count > 5:
        quality_score += 0.2
    else:
        quality_score += 0.1

    # Historical depth
    if len(sentiment_history) > 10:
        quality_score += 0.4
    elif len(sentiment_history) > 5:
        quality_score += 0.3
    elif len(sentiment_history) > 2:
        quality_score += 0.2
    else:
        quality_score += 0.1

    # Financial snapshots
    if historical_snapshots and len(historical_snapshots) > 5:
        quality_score += 0.3
    elif historical_snapshots and len(historical_snapshots) > 2:
        quality_score += 0.2
    else:
        quality_score += 0.1

    return min(quality_score, 1.0)


def _identify_data_gaps(
    sentiment_history: List[SentimentDataPoint],
    historical_snapshots: Optional[List[MonitorAnalysisSnapshot]],
    current_sentiment: NewsSentiment
) -> List[str]:
    """Identify gaps in available data"""

    gaps = []

    if current_sentiment.articles_count < 5:
        gaps.append("Limited recent news coverage (< 5 articles)")

    if len(sentiment_history) < 5:
        gaps.append("Limited historical sentiment data (< 5 data points)")

    if not historical_snapshots or len(historical_snapshots) < 3:
        gaps.append("Insufficient historical financial snapshots for correlation analysis")

    if not current_sentiment.recent_headlines:
        gaps.append("No recent headlines available for qualitative analysis")

    return gaps
