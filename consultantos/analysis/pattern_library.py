"""
Historical pattern library for strategic intelligence.

Stores and matches historical patterns to provide predictive insights:
- Pattern storage (e.g., "Sentiment decline → Earnings miss: 73% accuracy")
- Pattern matching (find similar historical trajectories)
- Confidence scoring based on sample size
- Pattern categories (disruption, flywheel, competitive moves, etc.)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field
import numpy as np

logger = logging.getLogger(__name__)


class PatternCategory(str, Enum):
    """Categories of strategic patterns"""
    DISRUPTION = "disruption"
    FLYWHEEL = "flywheel"
    COMPETITIVE_MOVE = "competitive_move"
    MARKET_SHIFT = "market_shift"
    REGULATORY_CHANGE = "regulatory_change"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    LEADERSHIP_CHANGE = "leadership_change"
    PRODUCT_LAUNCH = "product_launch"
    MERGER_ACQUISITION = "merger_acquisition"
    FINANCIAL_DISTRESS = "financial_distress"


class PatternSignal(BaseModel):
    """Single signal in a pattern"""

    metric_name: str = Field(description="Metric being tracked")
    change_type: str = Field(description="Type of change (increase, decrease, stable)")
    threshold: Optional[float] = Field(
        default=None,
        description="Threshold value if applicable"
    )
    time_offset_days: int = Field(
        description="Days from pattern start (0 = start)"
    )


class PatternOutcome(BaseModel):
    """Outcome of a pattern"""

    outcome_type: str = Field(description="Type of outcome")
    description: str = Field(description="Outcome description")
    time_to_outcome_days: int = Field(
        description="Days from pattern start to outcome"
    )
    severity: float = Field(
        ge=0.0,
        le=10.0,
        description="Severity/magnitude of outcome"
    )


class HistoricalPattern(BaseModel):
    """Historical pattern with signals and outcomes"""

    pattern_id: str = Field(description="Unique pattern identifier")
    category: PatternCategory
    name: str = Field(description="Pattern name")
    description: str = Field(description="Detailed pattern description")

    # Pattern definition
    signals: List[PatternSignal] = Field(
        description="Sequence of signals defining pattern"
    )
    outcome: PatternOutcome = Field(
        description="Expected outcome when pattern occurs"
    )

    # Historical evidence
    occurrence_count: int = Field(
        description="Number of times pattern observed"
    )
    successful_predictions: int = Field(
        description="Number of times outcome occurred"
    )
    accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Prediction accuracy (successful / total)"
    )

    # Sample data
    example_companies: List[str] = Field(
        default_factory=list,
        description="Companies where pattern was observed"
    )
    example_dates: List[datetime] = Field(
        default_factory=list,
        description="Dates when pattern occurred"
    )

    # Metadata
    industry: Optional[str] = Field(
        default=None,
        description="Industry specificity (None = cross-industry)"
    )
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in pattern"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PatternMatch(BaseModel):
    """Match between current trajectory and historical pattern"""

    pattern_id: str
    pattern_name: str
    category: PatternCategory

    # Match quality
    similarity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="How closely current trajectory matches pattern"
    )
    signals_matched: int = Field(
        description="Number of signals matched so far"
    )
    total_signals: int = Field(
        description="Total signals in pattern"
    )

    # Prediction
    predicted_outcome: PatternOutcome
    predicted_outcome_date: datetime = Field(
        description="Estimated date for outcome"
    )
    prediction_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in prediction"
    )

    # Evidence
    pattern_accuracy: float = Field(
        description="Historical accuracy of this pattern"
    )
    similar_cases: List[str] = Field(
        description="Companies with similar trajectories"
    )

    matched_at: datetime = Field(default_factory=datetime.utcnow)


class PatternSearchQuery(BaseModel):
    """Query for pattern matching"""

    monitor_id: str
    current_metrics: Dict[str, List[Tuple[datetime, float]]] = Field(
        description="Current metric time series"
    )
    category_filter: Optional[PatternCategory] = None
    industry_filter: Optional[str] = None
    min_accuracy: float = Field(default=0.6, ge=0.0, le=1.0)


class PatternLibraryService:
    """
    Service for historical pattern storage and matching.

    Provides pattern-based predictive capabilities by matching current
    trajectories against historical patterns with known outcomes.
    """

    def __init__(self, db_service):
        """
        Initialize pattern library service.

        Args:
            db_service: Database service for persistence
        """
        self.db = db_service
        self.logger = logger

    async def store_pattern(
        self,
        pattern: HistoricalPattern
    ) -> bool:
        """
        Store historical pattern.

        Args:
            pattern: Pattern to store

        Returns:
            True if stored successfully

        Raises:
            ValueError: If pattern data invalid
        """
        try:
            # Validate pattern
            if pattern.occurrence_count < 3:
                raise ValueError("Pattern requires minimum 3 occurrences")

            if pattern.successful_predictions > pattern.occurrence_count:
                raise ValueError("Successful predictions cannot exceed occurrences")

            # Calculate accuracy if not set
            if pattern.occurrence_count > 0:
                pattern.accuracy = pattern.successful_predictions / pattern.occurrence_count

            # Update confidence score based on sample size
            pattern.confidence_score = self._calculate_confidence(
                pattern.occurrence_count,
                pattern.accuracy
            )

            # Store in database
            collection = self.db.db.collection("historical_patterns")
            doc_ref = collection.document(pattern.pattern_id)
            await doc_ref.set(pattern.dict())

            self.logger.info(
                f"Stored pattern: {pattern.name} "
                f"(accuracy={pattern.accuracy:.1%}, occurrences={pattern.occurrence_count})"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to store pattern: {e}", exc_info=True)
            raise

    async def get_pattern(
        self,
        pattern_id: str
    ) -> Optional[HistoricalPattern]:
        """
        Retrieve historical pattern.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern or None if not found
        """
        try:
            collection = self.db.db.collection("historical_patterns")
            doc_ref = collection.document(pattern_id)
            doc = await doc_ref.get()

            if doc.exists:
                return HistoricalPattern(**doc.to_dict())

            return None

        except Exception as e:
            self.logger.error(f"Failed to get pattern: {e}", exc_info=True)
            return None

    async def find_matching_patterns(
        self,
        query: PatternSearchQuery,
        max_matches: int = 5
    ) -> List[PatternMatch]:
        """
        Find patterns matching current trajectory.

        Args:
            query: Search query with current metrics
            max_matches: Maximum number of matches to return

        Returns:
            List of pattern matches ordered by similarity
        """
        try:
            # Fetch candidate patterns
            patterns = await self._get_candidate_patterns(
                category=query.category_filter,
                industry=query.industry_filter,
                min_accuracy=query.min_accuracy
            )

            if not patterns:
                self.logger.info("No candidate patterns found")
                return []

            # Score each pattern
            matches = []
            for pattern in patterns:
                match = await self._match_pattern(query, pattern)
                if match and match.similarity_score >= 0.5:
                    matches.append(match)

            # Sort by similarity and confidence
            matches.sort(
                key=lambda m: (m.similarity_score * m.prediction_confidence),
                reverse=True
            )

            self.logger.info(
                f"Found {len(matches)} matching patterns for monitor {query.monitor_id}"
            )

            return matches[:max_matches]

        except Exception as e:
            self.logger.error(f"Failed to find matching patterns: {e}", exc_info=True)
            return []

    async def update_pattern_accuracy(
        self,
        pattern_id: str,
        outcome_occurred: bool,
        company: str,
        date: datetime
    ) -> bool:
        """
        Update pattern accuracy based on new observation.

        Args:
            pattern_id: Pattern to update
            outcome_occurred: Whether predicted outcome occurred
            company: Company where pattern was observed
            date: Date of observation

        Returns:
            True if updated successfully
        """
        try:
            pattern = await self.get_pattern(pattern_id)
            if not pattern:
                raise ValueError(f"Pattern {pattern_id} not found")

            # Update counts
            pattern.occurrence_count += 1
            if outcome_occurred:
                pattern.successful_predictions += 1

            # Recalculate accuracy
            pattern.accuracy = pattern.successful_predictions / pattern.occurrence_count

            # Update confidence
            pattern.confidence_score = self._calculate_confidence(
                pattern.occurrence_count,
                pattern.accuracy
            )

            # Add to examples
            if company not in pattern.example_companies:
                pattern.example_companies.append(company)
            pattern.example_dates.append(date)

            pattern.last_updated = datetime.utcnow()

            # Store updated pattern
            await self.store_pattern(pattern)

            self.logger.info(
                f"Updated pattern {pattern_id}: "
                f"accuracy={pattern.accuracy:.1%}, "
                f"occurrences={pattern.occurrence_count}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to update pattern accuracy: {e}", exc_info=True)
            return False

    async def get_patterns_by_category(
        self,
        category: PatternCategory,
        min_accuracy: float = 0.6,
        min_occurrences: int = 5
    ) -> List[HistoricalPattern]:
        """
        Get patterns by category.

        Args:
            category: Pattern category
            min_accuracy: Minimum accuracy threshold
            min_occurrences: Minimum occurrence count

        Returns:
            List of patterns matching criteria
        """
        try:
            collection = self.db.db.collection("historical_patterns")

            query = collection.where("category", "==", category.value)
            query = query.where("accuracy", ">=", min_accuracy)
            query = query.where("occurrence_count", ">=", min_occurrences)
            query = query.order_by("accuracy", direction="DESCENDING")

            docs = await query.stream()
            patterns = [HistoricalPattern(**doc.to_dict()) for doc in docs]

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to get patterns by category: {e}", exc_info=True)
            return []

    async def get_top_patterns(
        self,
        limit: int = 10,
        min_confidence: float = 0.7
    ) -> List[HistoricalPattern]:
        """
        Get top patterns by confidence.

        Args:
            limit: Maximum number of patterns
            min_confidence: Minimum confidence threshold

        Returns:
            List of top patterns
        """
        try:
            collection = self.db.db.collection("historical_patterns")

            query = collection.where("confidence_score", ">=", min_confidence)
            query = query.order_by("confidence_score", direction="DESCENDING")
            query = query.limit(limit)

            docs = await query.stream()
            patterns = [HistoricalPattern(**doc.to_dict()) for doc in docs]

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to get top patterns: {e}", exc_info=True)
            return []

    # Private helper methods

    async def _get_candidate_patterns(
        self,
        category: Optional[PatternCategory] = None,
        industry: Optional[str] = None,
        min_accuracy: float = 0.6
    ) -> List[HistoricalPattern]:
        """Fetch candidate patterns for matching"""
        try:
            collection = self.db.db.collection("historical_patterns")

            query = collection.where("accuracy", ">=", min_accuracy)

            if category:
                query = query.where("category", "==", category.value)

            if industry:
                # Include both industry-specific and cross-industry patterns
                docs = await query.stream()
                patterns = [HistoricalPattern(**doc.to_dict()) for doc in docs]
                patterns = [
                    p for p in patterns
                    if p.industry is None or p.industry == industry
                ]
                return patterns

            docs = await query.stream()
            return [HistoricalPattern(**doc.to_dict()) for doc in docs]

        except Exception as e:
            self.logger.error(f"Failed to get candidate patterns: {e}")
            return []

    async def _match_pattern(
        self,
        query: PatternSearchQuery,
        pattern: HistoricalPattern
    ) -> Optional[PatternMatch]:
        """
        Match current trajectory against a pattern.

        Args:
            query: Current metrics
            pattern: Pattern to match against

        Returns:
            Pattern match or None if no match
        """
        try:
            # Calculate similarity between current metrics and pattern signals
            signals_matched = 0
            similarity_scores = []

            for signal in pattern.signals:
                if signal.metric_name not in query.current_metrics:
                    continue

                # Check if signal matches current data
                metric_data = query.current_metrics[signal.metric_name]
                signal_match, score = self._check_signal_match(
                    metric_data, signal
                )

                if signal_match:
                    signals_matched += 1
                    similarity_scores.append(score)

            if signals_matched == 0:
                return None

            # Calculate overall similarity
            similarity_score = sum(similarity_scores) / len(similarity_scores)

            # Calculate prediction confidence
            prediction_confidence = (
                similarity_score *
                pattern.accuracy *
                pattern.confidence_score
            )

            # Estimate outcome date
            avg_time_to_outcome = pattern.outcome.time_to_outcome_days
            predicted_outcome_date = datetime.utcnow() + timedelta(
                days=avg_time_to_outcome
            )

            match = PatternMatch(
                pattern_id=pattern.pattern_id,
                pattern_name=pattern.name,
                category=pattern.category,
                similarity_score=similarity_score,
                signals_matched=signals_matched,
                total_signals=len(pattern.signals),
                predicted_outcome=pattern.outcome,
                predicted_outcome_date=predicted_outcome_date,
                prediction_confidence=prediction_confidence,
                pattern_accuracy=pattern.accuracy,
                similar_cases=pattern.example_companies[:5]
            )

            return match

        except Exception as e:
            self.logger.error(f"Failed to match pattern: {e}")
            return None

    def _check_signal_match(
        self,
        metric_data: List[Tuple[datetime, float]],
        signal: PatternSignal
    ) -> Tuple[bool, float]:
        """
        Check if metric data matches a signal.

        Args:
            metric_data: List of (timestamp, value) tuples
            signal: Signal to match

        Returns:
            (matched, similarity_score)
        """
        if len(metric_data) < 2:
            return False, 0.0

        # Get values around signal time offset
        # For simplicity, use recent data
        recent_values = [v for _, v in metric_data[-10:]]

        std = np.std(recent_values)
        if std == 0 or np.allclose(recent_values, recent_values[0]):
            return False, 0.0

        if signal.change_type == "increase":
            # Check for upward trend
            trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
            if trend > 0:
                return True, min(1.0, abs(trend) / std)

        elif signal.change_type == "decrease":
            # Check for downward trend
            trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]
            if trend < 0:
                return True, min(1.0, abs(trend) / std)

        elif signal.change_type == "stable":
            # Check for stability (low variance)
            std_dev = np.std(recent_values)
            mean_val = np.mean(recent_values)
            if mean_val != 0:
                cv = std_dev / abs(mean_val)  # Coefficient of variation
                if cv < 0.1:  # 10% threshold
                    return True, 1.0 - cv

        return False, 0.0

    def _calculate_confidence(
        self,
        occurrence_count: int,
        accuracy: float
    ) -> float:
        """
        Calculate confidence score based on sample size and accuracy.

        Uses Wilson score interval for binomial proportion confidence.

        Args:
            occurrence_count: Number of observations
            accuracy: Accuracy rate

        Returns:
            Confidence score (0.0-1.0)
        """
        if occurrence_count == 0:
            return 0.0

        # Wilson score (simplified)
        z = 1.96  # 95% confidence interval

        p_hat = accuracy
        n = occurrence_count

        numerator = p_hat + (z * z) / (2 * n)
        denominator = 1 + (z * z) / n

        confidence = numerator / denominator

        return min(1.0, max(0.0, confidence))
