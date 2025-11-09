# Feedback Loop & Quality Flywheel Guide

## Overview

ConsultantOS implements a **continuous learning system** that improves analysis quality over time through user feedback. The system collects ratings, corrections, and patterns to automatically enhance prompts and reduce errors.

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    USER FEEDBACK FLOW                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Insight Rating  │    │    Correction    │    │  Quality Metrics │
│    (1-5 stars)   │───▶│   Submission     │───▶│   Calculation    │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                              │                          │
                              ▼                          ▼
                    ┌──────────────────┐      ┌──────────────────┐
                    │ FeedbackProcessor│      │  Quality Report  │
                    │   (Learning)     │      │   (Analytics)    │
                    └──────────────────┘      └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Prompt Enhancement│
                    │ (Negative/Positive│
                    │    Examples)      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Improved Analysis│
                    │    Quality       │
                    └──────────────────┘
```

### Data Models

#### InsightRating
```python
{
    "id": "rating_123",
    "insight_id": "insight_porter_456",  # Framework-specific insight
    "report_id": "report_789",
    "user_id": "user_001",
    "rating": 5,  # 1-5 stars
    "feedback_text": "Very insightful competitive analysis",
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### InsightCorrection
```python
{
    "id": "correction_123",
    "insight_id": "insight_swot_456",
    "report_id": "report_789",
    "user_id": "user_001",
    "section": "swot",
    "original_text": "Tesla has no competitors in EV market",
    "corrected_text": "Tesla faces strong competition from Rivian, Lucid, and traditional automakers",
    "explanation": "Factually incorrect - multiple EV competitors exist",
    "error_category": "factual",  # factual, tone, relevance, depth, structure
    "validated": False,  # Admin review required
    "incorporated": False,  # Used in retraining
    "created_at": "2024-01-15T10:35:00Z"
}
```

#### LearningPattern
```python
{
    "pattern_id": "pattern_001",
    "pattern_type": "common_error",
    "framework": "porter",
    "description": "Tendency to overlook emerging competitors in competitive rivalry",
    "example_text": "Users frequently correct to add startup competitors",
    "occurrence_count": 12,
    "confidence": 0.85,  # 0-1 confidence score
    "created_at": "2024-01-10T00:00:00Z",
    "last_updated": "2024-01-15T10:35:00Z"
}
```

---

## API Endpoints

### Submit Rating

**POST** `/feedback/insights/{insight_id}/rating`

Rate an individual insight with 1-5 stars.

**Request:**
```bash
curl -X POST "http://localhost:8080/feedback/insights/insight_porter_456/rating?rating=5&report_id=report_789" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_text": "Excellent competitive analysis with specific data"
  }'
```

**Response:**
```json
{
    "id": "rating_123",
    "insight_id": "insight_porter_456",
    "report_id": "report_789",
    "user_id": "user_001",
    "rating": 5,
    "feedback_text": "Excellent competitive analysis with specific data",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Submit Correction

**POST** `/feedback/insights/{insight_id}/correction`

Submit a correction for incorrect or incomplete insight.

**Request:**
```bash
curl -X POST "http://localhost:8080/feedback/insights/insight_swot_456/correction" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "report_id": "report_789",
    "section": "swot",
    "original_text": "Tesla has no EV competitors",
    "corrected_text": "Tesla competes with Rivian, Lucid, and traditional automakers entering EV market",
    "explanation": "Factually incorrect - overlooks major EV competitors",
    "error_category": "factual"
  }'
```

**Response:**
```json
{
    "id": "correction_123",
    "insight_id": "insight_swot_456",
    "report_id": "report_789",
    "validated": false,
    "incorporated": false,
    "created_at": "2024-01-15T10:35:00Z"
}
```

### Get Report Quality

**GET** `/feedback/reports/{report_id}/quality`

Get aggregated quality metrics for a specific report.

**Response:**
```json
{
    "report_id": "report_789",
    "avg_rating": 4.2,
    "total_ratings": 15,
    "corrections_count": 3,
    "user_satisfaction": 0.84,
    "rating_distribution": {
        "5": 8,
        "4": 5,
        "3": 2,
        "2": 0,
        "1": 0
    },
    "error_categories": {
        "factual": 2,
        "relevance": 1
    },
    "frameworks_quality": {
        "porter": 4.5,
        "swot": 4.0,
        "pestel": 4.1
    },
    "computed_at": "2024-01-15T11:00:00Z",
    "needs_improvement": false
}
```

### Get Quality Report

**GET** `/feedback/quality/report?days=30`

Generate comprehensive quality report across all analyses.

**Response:**
```json
{
    "time_period": "last_30_days",
    "overall_avg_rating": 4.1,
    "total_reports": 120,
    "total_ratings": 480,
    "total_corrections": 35,
    "user_satisfaction": 0.82,
    "most_corrected_patterns": [
        {
            "error_category": "factual",
            "count": 15,
            "percentage": 42.9
        },
        {
            "error_category": "depth",
            "count": 10,
            "percentage": 28.6
        }
    ],
    "improvement_recommendations": [
        "High factual error rate (15 corrections). Improve data validation and fact-checking.",
        "Depth issues identified (10 corrections). Adjust prompts to provide more detailed analysis."
    ],
    "generated_at": "2024-01-15T11:00:00Z"
}
```

### Get Pending Corrections (Admin)

**GET** `/feedback/corrections/pending?limit=50`

Get pending corrections awaiting admin review.

**Response:**
```json
[
    {
        "id": "correction_123",
        "insight_id": "insight_swot_456",
        "section": "swot",
        "original_text": "...",
        "corrected_text": "...",
        "explanation": "...",
        "error_category": "factual",
        "validated": false,
        "created_at": "2024-01-15T10:35:00Z"
    }
]
```

### Validate Correction (Admin)

**POST** `/feedback/corrections/{correction_id}/validate?approved=true`

Validate a user-submitted correction (admin only).

**Response:**
```json
{
    "correction_id": "correction_123",
    "validated": true,
    "approved": true,
    "message": "Correction validated successfully"
}
```

---

## Learning System

### FeedbackProcessor

The `FeedbackProcessor` analyzes user feedback to improve future analyses.

```python
from consultantos.learning import FeedbackProcessor

processor = FeedbackProcessor()

# Process a correction
result = await processor.process_correction(correction)
# Returns: {
#   "processed": True,
#   "patterns_updated": 2,
#   "patterns": ["pattern_001", "pattern_002"]
# }

# Generate prompt improvements
improvements = await processor.improve_prompts(framework="porter")
# Returns: {
#   "framework": "porter",
#   "negative_examples": [...],  # Common errors to avoid
#   "positive_examples": [...],  # High-quality insights
#   "recommendations": [...]     # Quality guidelines
# }
```

### Pattern Recognition

The system automatically identifies patterns in corrections:

1. **Categorizes errors** by type (factual, depth, relevance, tone, structure)
2. **Tracks occurrence frequency** to identify common mistakes
3. **Builds confidence scores** based on validation and repetition
4. **Generates learning patterns** for prompt enhancement

Example pattern:
```python
{
    "pattern_type": "common_error",
    "framework": "porter",
    "description": "factual: missing_competitor",
    "example_text": "Original: 'No significant competitors'\nCorrected: 'Competes with 5 major players including X, Y, Z'\nLesson: Always include specific competitor names and market positions",
    "occurrence_count": 12,
    "confidence": 0.85
}
```

### Prompt Enhancement

The system enhances prompts with feedback-based examples:

```python
from consultantos.prompts import get_enhanced_porter_prompt

# Get enhanced prompt with learning examples
enhanced_prompt = await get_enhanced_porter_prompt(
    company="Tesla",
    industry="Electric Vehicles",
    research=research_data,
    market=market_data,
    financial=financial_data,
    feedback_processor=processor
)

# Enhanced prompt includes:
# 1. Base Porter's 5 Forces template
# 2. Common errors to avoid (from corrections)
# 3. Excellent examples (from high ratings)
# 4. Quality guidelines (from patterns)
```

**Enhanced prompt structure:**
```markdown
[Base Porter's 5 Forces Template]

**AVOID THESE COMMON ERRORS** (Based on user corrections):
1. ❌ **FACTUAL** in PORTER:
   Bad: "No significant competitors exist"
   Better: "Faces competition from Rivian, Lucid, and 10+ traditional automakers"
   Lesson: Always name specific competitors with market data

**EXCELLENT INSIGHT EXAMPLES** (Highly rated by users):
1. ✅ **PORTER** - 5/5 stars
   "Competitive rivalry is HIGH (4.5/5): 15 direct competitors with Tesla at 18% US EV market share vs Rivian 5%, Lucid 2%. Market growing 40% YoY reduces rivalry slightly."

**QUALITY GUIDELINES** (From feedback analysis):
• **Factual Accuracy**: Verify all data points against source material
• **Analysis Depth**: Provide 3-4 supporting points for each major insight
• **Strategic Relevance**: Focus on insights that directly impact business strategy
```

---

## Database Schema

### Firestore Collections

#### `insight_ratings`
```javascript
{
    // Document ID: rating.id
    "insight_id": "insight_porter_456",
    "report_id": "report_789",
    "user_id": "user_001",
    "rating": 5,
    "feedback_text": "...",
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Indexes Required:**
- `report_id` (for aggregating ratings by report)
- `created_at` (for time-based queries)
- `rating` (for finding high-rated insights)

#### `insight_corrections`
```javascript
{
    // Document ID: correction.id
    "insight_id": "insight_swot_456",
    "report_id": "report_789",
    "user_id": "user_001",
    "section": "swot",
    "original_text": "...",
    "corrected_text": "...",
    "explanation": "...",
    "error_category": "factual",
    "validated": false,
    "incorporated": false,
    "admin_notes": null,
    "created_at": "2024-01-15T10:35:00Z",
    "validated_at": null
}
```

**Indexes Required:**
- `report_id`
- `validated` (for pending corrections queue)
- `section` + `validated` (composite index for framework-specific validated corrections)
- `created_at`

#### `learning_patterns`
```javascript
{
    // Document ID: pattern.pattern_id
    "pattern_type": "common_error",
    "framework": "porter",
    "description": "...",
    "example_text": "...",
    "occurrence_count": 12,
    "confidence": 0.85,
    "created_at": "2024-01-10T00:00:00Z",
    "last_updated": "2024-01-15T10:35:00Z"
}
```

**Indexes Required:**
- `framework` + `confidence` (composite index for framework-specific patterns)
- `confidence` (for high-confidence pattern retrieval)

---

## Quality Flywheel

The system creates a self-reinforcing quality loop:

```
┌──────────────────┐
│  User Feedback   │
│  (Ratings +      │
│   Corrections)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Pattern Learning │
│  (Categorize,    │
│   Aggregate)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Prompt Enhancement│
│  (Add Examples,  │
│   Guidelines)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Better Analysis  │
│  (Fewer Errors,  │
│   Higher Ratings)│
└────────┬─────────┘
         │
         └──────────────┐
                        │
                        ▼
            ┌──────────────────┐
            │   Repeat Cycle   │
            │  (Continuous      │
            │   Improvement)    │
            └──────────────────┘
```

### Quality Metrics Tracked

1. **Average Rating** (target: > 4.0/5.0)
2. **User Satisfaction** (derived from rating distribution, target: > 0.8)
3. **Correction Rate** (corrections per insight, target: < 0.15)
4. **Error Categories** (distribution of error types)
5. **Framework Quality** (per-framework average ratings)
6. **Pattern Confidence** (learning pattern reliability)

### Improvement Triggers

**Automatic**:
- Validated corrections automatically update learning patterns
- Patterns with confidence > 0.7 enhance prompts
- High-rated insights (≥ 4.5 stars) become positive examples

**Manual (Admin)**:
- Review pending corrections
- Validate/reject user submissions
- Manually incorporate high-value corrections

**Quarterly**:
- Review quality trends
- Update base prompts with validated patterns
- Adjust quality thresholds

---

## Usage Examples

### End-to-End Feedback Flow

```python
# 1. User generates report
response = requests.post("http://localhost:8080/analyze", json={
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
})
report_id = response.json()["report_id"]

# 2. User rates insights
requests.post(
    f"http://localhost:8080/feedback/insights/insight_porter_123/rating",
    params={"rating": 5, "report_id": report_id},
    json={"feedback_text": "Excellent competitive analysis"}
)

# 3. User corrects an error
requests.post(
    f"http://localhost:8080/feedback/insights/insight_swot_456/correction",
    json={
        "report_id": report_id,
        "section": "swot",
        "original_text": "No major threats identified",
        "corrected_text": "Regulatory changes in EU pose significant threat with €2B potential compliance costs",
        "explanation": "Missing critical regulatory threat",
        "error_category": "factual"
    }
)

# 4. System learns from correction
# (Automatic - FeedbackProcessor processes in background)

# 5. Admin validates correction
requests.post(
    "http://localhost:8080/feedback/corrections/correction_123/validate",
    params={"approved": True},
    json={"admin_notes": "Valid regulatory concern"}
)

# 6. Next analysis uses enhanced prompts
# (Automatic - prompts include learning examples)
```

### Admin Quality Dashboard

```python
# Get comprehensive quality report
response = requests.get("http://localhost:8080/feedback/quality/report?days=30")
quality_report = response.json()

print(f"Average Rating: {quality_report['overall_avg_rating']}/5.0")
print(f"User Satisfaction: {quality_report['user_satisfaction']}")
print(f"Total Corrections: {quality_report['total_corrections']}")
print("\nTop Issues:")
for pattern in quality_report['most_corrected_patterns']:
    print(f"- {pattern['error_category']}: {pattern['count']} ({pattern['percentage']}%)")
print("\nRecommendations:")
for rec in quality_report['improvement_recommendations']:
    print(f"- {rec}")
```

---

## Development Workflow

### Adding New Error Categories

1. Update `ErrorCategory` enum in `consultantos/models/feedback.py`:
```python
class ErrorCategory(str, Enum):
    FACTUAL = "factual"
    TONE = "tone"
    RELEVANCE = "relevance"
    DEPTH = "depth"
    STRUCTURE = "structure"
    COMPLETENESS = "completeness"  # NEW
```

2. Update `FeedbackProcessor._analyze_correction()` to handle new category

3. Update frontend correction modal to include new option

### Customizing Pattern Detection

Modify `FeedbackProcessor._classify_correction_type()` to add custom pattern detection logic:

```python
def _classify_correction_type(self, correction: InsightCorrection) -> str:
    original = correction.original_text.lower()
    corrected = correction.corrected_text.lower()

    # Custom pattern detection
    if "market share" in corrected and "market share" not in original:
        return "missing_market_data"

    # Existing logic...
    return "general_correction"
```

### Adjusting Learning Thresholds

Modify `FeedbackProcessor` initialization:

```python
class FeedbackProcessor:
    def __init__(self, db=None):
        self.db = db or get_db_service()
        self.min_pattern_occurrences = 5  # Require 5+ occurrences (was 3)
        self.pattern_confidence_threshold = 0.8  # Higher confidence bar (was 0.7)
```

---

## Performance Considerations

### Caching

- Quality reports cached for 1 hour
- Learning patterns cached in memory
- Feedback database queries optimized with indexes

### Scalability

- Async processing for all feedback operations
- Background jobs for pattern updates
- Batch processing for prompt enhancements

### Privacy

- User IDs hashed in analytics
- Correction text sanitized before storage
- Admin review required for pattern incorporation

---

## Success Criteria

### Quantitative Targets

- **Average Rating**: > 4.0/5.0 stars
- **User Satisfaction**: > 0.8 (80%)
- **Correction Rate**: < 15% of insights
- **Pattern Confidence**: > 0.75 for incorporated patterns
- **Response Time**: < 200ms for feedback submission

### Qualitative Goals

- Users find feedback submission easy and intuitive
- Corrections lead to measurable quality improvements
- Patterns accurately reflect real quality issues
- Enhanced prompts demonstrably reduce error rates

### Monitoring Dashboard

Track these metrics in real-time:
1. Feedback submission rate (submissions per report)
2. Validation queue length (pending corrections)
3. Pattern growth (new patterns per week)
4. Quality trend (30-day moving average rating)
5. Error category distribution

---

## Troubleshooting

### Common Issues

**Low feedback submission rate**:
- Make feedback UI more prominent
- Simplify correction modal
- Add gamification (badges, leaderboards)

**High correction rate**:
- Review base prompts for clarity
- Increase validation thresholds
- Add more context to prompts

**Pattern confidence stagnation**:
- Increase pattern occurrence threshold
- Review validation quality
- Add admin pattern review process

**Slow quality improvement**:
- Shorten feedback-to-prompt cycle
- Increase weight of validated corrections
- Add A/B testing for prompt variants

---

## Future Enhancements

### Planned Features

1. **Automated Pattern Detection**: ML-based pattern recognition
2. **A/B Testing**: Compare prompt variants automatically
3. **User Segmentation**: Track quality by user expertise level
4. **Predictive Quality**: Predict insight quality before generation
5. **Framework Recommendations**: Suggest best frameworks per company/industry
6. **Collaborative Filtering**: Learn from similar companies' feedback
7. **Real-time Feedback**: Live correction during report generation
8. **Quality Forecasting**: Predict future quality trends

### Research Opportunities

- **Reinforcement Learning**: Use feedback as reward signal for model training
- **Active Learning**: Prioritize uncertain insights for user review
- **Transfer Learning**: Apply patterns across similar frameworks/industries
- **Explainable AI**: Provide transparency on why insights changed

---

## References

- **API Documentation**: `/docs` (Swagger UI)
- **Database Schema**: `consultantos/database.py`
- **Feedback Models**: `consultantos/models/feedback.py`
- **Learning System**: `consultantos/learning/feedback_processor.py`
- **Prompt Enhancement**: `consultantos/prompts.py`

---

## Support

For questions or issues:
- GitHub Issues: [ConsultantOS Issues](https://github.com/your-repo/issues)
- Documentation: This guide
- API Docs: `http://localhost:8080/docs`

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Production Ready
