"""
Feedback Processor - Learning System

Processes user feedback to improve future analyses through pattern recognition
and prompt enhancement.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

from consultantos.models.feedback import (
    InsightCorrection,
    InsightRating,
    QualityReport,
    LearningPattern,
    ErrorCategory
)
from consultantos.database import get_db_service
from consultantos.monitoring import get_logger

logger = get_logger(__name__)


class FeedbackProcessor:
    """
    Process user feedback to improve future analyses.

    Responsibilities:
    - Analyze corrections and ratings for patterns
    - Generate learning insights
    - Update few-shot examples in prompts
    - Track quality trends over time
    """

    def __init__(self, db=None):
        self.db = db or get_db_service()
        self.min_pattern_occurrences = 3  # Minimum occurrences to consider a pattern
        self.pattern_confidence_threshold = 0.7

    async def process_correction(
        self,
        correction: InsightCorrection
    ) -> Dict[str, any]:
        """
        Analyze a correction and update learning patterns.

        Workflow:
        1. Store correction in database
        2. Categorize type of error
        3. Check for pattern matches
        4. Update or create learning patterns
        5. Track correction statistics

        Returns:
            Dict with processing results and any patterns identified
        """
        try:
            # Extract correction characteristics
            characteristics = self._analyze_correction(correction)

            # Check for existing patterns
            matching_patterns = await self._find_matching_patterns(
                correction,
                characteristics
            )

            # Update existing patterns or create new ones
            updated_patterns = []
            if matching_patterns:
                for pattern in matching_patterns:
                    updated = await self._update_pattern(pattern, correction)
                    updated_patterns.append(updated)
            else:
                # Create new pattern if this is a novel correction type
                new_pattern = await self._create_pattern(correction, characteristics)
                if new_pattern:
                    updated_patterns.append(new_pattern)

            logger.info(
                "correction_processed",
                correction_id=correction.id,
                error_category=correction.error_category,
                patterns_updated=len(updated_patterns)
            )

            return {
                "processed": True,
                "correction_id": correction.id,
                "characteristics": characteristics,
                "patterns_updated": len(updated_patterns),
                "patterns": [p.pattern_id for p in updated_patterns]
            }

        except Exception as e:
            logger.error(
                "correction_processing_failed",
                correction_id=correction.id,
                error=str(e)
            )
            return {
                "processed": False,
                "error": str(e)
            }

    async def generate_quality_report(
        self,
        report_id: str
    ) -> QualityReport:
        """
        Generate comprehensive quality report for a specific analysis.

        Aggregates:
        - All ratings for insights in this report
        - All corrections submitted
        - Derived quality metrics
        - Comparison to historical performance
        """
        try:
            # Fetch feedback data
            ratings = await self.db.get_ratings_for_report(report_id)
            corrections = await self.db.get_corrections_for_report(report_id)

            # Calculate metrics
            avg_rating = (
                sum(r.rating for r in ratings) / len(ratings)
                if ratings else 0.0
            )

            # User satisfaction (weighted formula)
            weighted_sum = sum(r.rating * (r.rating / 5.0) for r in ratings)
            max_possible = len(ratings) * 5
            user_satisfaction = weighted_sum / max_possible if max_possible > 0 else 0.0

            # Framework-specific quality
            framework_quality = defaultdict(list)
            for rating in ratings:
                # Extract framework from insight_id (e.g., "insight_porter_123")
                if "_" in rating.insight_id:
                    framework = rating.insight_id.split("_")[1]
                    framework_quality[framework].append(rating.rating)

            frameworks_quality = {
                framework: sum(ratings) / len(ratings)
                for framework, ratings in framework_quality.items()
            }

            # Error category distribution
            error_categories = defaultdict(int)
            for correction in corrections:
                error_categories[correction.error_category.value] += 1

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                avg_rating,
                corrections,
                frameworks_quality
            )

            quality_report = QualityReport(
                time_period="current_report",
                overall_avg_rating=round(avg_rating, 2),
                total_reports=1,
                total_ratings=len(ratings),
                total_corrections=len(corrections),
                user_satisfaction=round(user_satisfaction, 2),
                framework_stats=[],  # Would include FrameworkQualityStats
                top_rated_insights=[],
                most_corrected_patterns=[],
                improvement_recommendations=recommendations,
                generated_at=datetime.utcnow()
            )

            logger.info(
                "quality_report_generated",
                report_id=report_id,
                avg_rating=quality_report.overall_avg_rating
            )

            return quality_report

        except Exception as e:
            logger.error(
                "quality_report_generation_failed",
                report_id=report_id,
                error=str(e)
            )
            raise

    async def improve_prompts(
        self,
        framework: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Use validated corrections to improve prompts.

        Process:
        1. Fetch validated corrections with high confidence
        2. Identify low-rated insight patterns (negative examples)
        3. Identify high-rated insights (positive examples)
        4. Generate prompt improvements
        5. Return structured prompt updates

        Returns:
            Dict with positive/negative examples and recommendations
        """
        try:
            # Fetch validated corrections
            corrections = await self.db.get_validated_corrections(
                framework=framework,
                limit=100
            )

            # Fetch learning patterns
            patterns = await self.db.get_learning_patterns(
                framework=framework,
                min_confidence=self.pattern_confidence_threshold
            )

            # Identify common error patterns (negative examples)
            negative_examples = await self._extract_negative_examples(
                corrections,
                patterns
            )

            # Fetch high-rated insights (positive examples)
            high_rated = await self.db.get_high_rated_insights(
                framework=framework,
                min_rating=4.5,
                limit=20
            )
            positive_examples = [
                {
                    "insight_id": r.insight_id,
                    "text": r.feedback_text,
                    "rating": r.rating
                }
                for r in high_rated if r.feedback_text
            ]

            # Generate prompt improvement recommendations
            recommendations = self._generate_prompt_recommendations(
                negative_examples,
                positive_examples,
                patterns
            )

            result = {
                "framework": framework or "all",
                "negative_examples": negative_examples,
                "positive_examples": positive_examples[:10],  # Top 10
                "patterns_used": len(patterns),
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "prompt_improvements_generated",
                framework=framework,
                negative_count=len(negative_examples),
                positive_count=len(positive_examples)
            )

            return result

        except Exception as e:
            logger.error(
                "prompt_improvement_failed",
                framework=framework,
                error=str(e)
            )
            raise

    def _analyze_correction(
        self,
        correction: InsightCorrection
    ) -> Dict[str, any]:
        """Extract characteristics from a correction"""
        return {
            "error_category": correction.error_category.value,
            "section": correction.section,
            "has_explanation": bool(correction.explanation),
            "text_length_diff": len(correction.corrected_text) - len(correction.original_text),
            "correction_type": self._classify_correction_type(correction)
        }

    def _classify_correction_type(
        self,
        correction: InsightCorrection
    ) -> str:
        """Classify the type of correction"""
        original = correction.original_text.lower()
        corrected = correction.corrected_text.lower()

        if len(corrected) > len(original) * 1.5:
            return "expansion"  # Adding more detail
        elif len(corrected) < len(original) * 0.5:
            return "reduction"  # Removing unnecessary content
        elif "competitor" in corrected and "competitor" not in original:
            return "missing_competitor"
        elif any(word in corrected for word in ["however", "but", "although"]):
            return "adding_nuance"
        else:
            return "general_correction"

    async def _find_matching_patterns(
        self,
        correction: InsightCorrection,
        characteristics: Dict
    ) -> List[LearningPattern]:
        """Find existing patterns that match this correction"""
        all_patterns = await self.db.get_learning_patterns(
            framework=correction.section
        )

        matching = []
        for pattern in all_patterns:
            # Match based on error category and correction type
            if (pattern.framework == correction.section and
                characteristics["error_category"] in pattern.description.lower()):
                matching.append(pattern)

        return matching

    async def _update_pattern(
        self,
        pattern: LearningPattern,
        correction: InsightCorrection
    ) -> LearningPattern:
        """Update existing pattern with new correction"""
        pattern.occurrence_count += 1
        pattern.last_updated = datetime.utcnow()

        # Recalculate confidence based on occurrence count
        pattern.confidence = min(
            0.95,
            0.5 + (pattern.occurrence_count / 20) * 0.45
        )

        # Update example if this correction is more detailed
        if (correction.explanation and
            len(correction.explanation) > len(pattern.example_text)):
            pattern.example_text = (
                f"{correction.original_text} → {correction.corrected_text}\n"
                f"Reason: {correction.explanation}"
            )

        await self.db.update_learning_pattern(pattern)
        return pattern

    async def _create_pattern(
        self,
        correction: InsightCorrection,
        characteristics: Dict
    ) -> Optional[LearningPattern]:
        """Create new learning pattern from correction"""
        # Only create pattern if correction has explanation
        if not correction.explanation:
            return None

        pattern = LearningPattern(
            pattern_id=f"pattern_{datetime.utcnow().timestamp()}",
            pattern_type="common_error",
            framework=correction.section,
            description=f"{characteristics['error_category']}: {characteristics['correction_type']}",
            example_text=(
                f"{correction.original_text} → {correction.corrected_text}\n"
                f"Reason: {correction.explanation}"
            ),
            occurrence_count=1,
            confidence=0.5,  # Start with low confidence
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )

        await self.db.store_learning_pattern(pattern)
        return pattern

    async def _generate_recommendations(
        self,
        avg_rating: float,
        corrections: List[InsightCorrection],
        frameworks_quality: Dict[str, float]
    ) -> List[str]:
        """Generate actionable improvement recommendations"""
        recommendations = []

        # Overall rating recommendations
        if avg_rating < 3.5:
            recommendations.append(
                "Overall rating below target. Conduct thorough review of analysis quality."
            )
        elif avg_rating < 4.0:
            recommendations.append(
                "Rating has room for improvement. Focus on depth and accuracy."
            )

        # Framework-specific recommendations
        for framework, quality in frameworks_quality.items():
            if quality < 3.5:
                recommendations.append(
                    f"Improve {framework.upper()} framework quality (current: {quality:.1f}/5.0)"
                )

        # Correction-based recommendations
        error_counts = defaultdict(int)
        for correction in corrections:
            error_counts[correction.error_category.value] += 1

        if error_counts["factual"] > 2:
            recommendations.append(
                f"High factual error rate ({error_counts['factual']} corrections). "
                "Enhance data validation and source verification."
            )

        if error_counts["depth"] > 2:
            recommendations.append(
                f"Depth issues identified ({error_counts['depth']} corrections). "
                "Adjust prompts to provide more detailed analysis."
            )

        return recommendations

    async def _extract_negative_examples(
        self,
        corrections: List[InsightCorrection],
        patterns: List[LearningPattern]
    ) -> List[Dict]:
        """Extract negative examples from corrections for prompt improvement"""
        negative_examples = []

        # Group corrections by error category
        by_category = defaultdict(list)
        for correction in corrections:
            if correction.validated and correction.explanation:
                by_category[correction.error_category.value].append(correction)

        # Take top corrections from each category
        for category, corr_list in by_category.items():
            # Sort by occurrence in patterns (more common errors first)
            sorted_corrections = sorted(
                corr_list,
                key=lambda c: sum(
                    1 for p in patterns
                    if c.section == p.framework and category in p.description
                ),
                reverse=True
            )

            for correction in sorted_corrections[:3]:  # Top 3 per category
                negative_examples.append({
                    "category": category,
                    "framework": correction.section,
                    "original": correction.original_text,
                    "corrected": correction.corrected_text,
                    "explanation": correction.explanation
                })

        return negative_examples

    def _generate_prompt_recommendations(
        self,
        negative_examples: List[Dict],
        positive_examples: List[Dict],
        patterns: List[LearningPattern]
    ) -> List[str]:
        """Generate specific prompt improvement recommendations"""
        recommendations = []

        # Recommendations based on negative examples
        if negative_examples:
            common_categories = defaultdict(int)
            for ex in negative_examples:
                common_categories[ex["category"]] += 1

            for category, count in common_categories.items():
                if category == "factual":
                    recommendations.append(
                        f"Add fact-checking step: {count} factual errors identified. "
                        "Include 'Verify all claims against source data' in prompts."
                    )
                elif category == "depth":
                    recommendations.append(
                        f"Increase analysis depth: {count} shallow insights. "
                        "Add 'Provide 3-4 supporting points for each claim' to prompts."
                    )
                elif category == "relevance":
                    recommendations.append(
                        f"Improve relevance filtering: {count} off-topic insights. "
                        "Add 'Focus only on strategic business implications' to prompts."
                    )

        # Recommendations based on high-performing patterns
        if patterns:
            high_confidence_patterns = [
                p for p in patterns if p.confidence > 0.8
            ]
            if high_confidence_patterns:
                recommendations.append(
                    f"Incorporate {len(high_confidence_patterns)} validated patterns "
                    "as positive examples in few-shot prompts."
                )

        # Recommendations based on positive examples
        if positive_examples:
            recommendations.append(
                f"Use {len(positive_examples)} high-rated insights as few-shot examples "
                "to maintain quality standards."
            )

        return recommendations
