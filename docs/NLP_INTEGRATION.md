# NLP Integration for ConsultantOS

## Overview

ConsultantOS now includes advanced NLP capabilities powered by spaCy and TextBlob for entity extraction, sentiment analysis, and relationship tracking. This enables structured competitive intelligence from unstructured text sources.

## Features

### 1. Entity Extraction
- **Named Entity Recognition (NER)**: Automatically extract companies, people, locations, dates, products, money values, and percentages
- **Entity Types Supported**:
  - `ORG` - Organizations (companies, agencies)
  - `PERSON` - People (executives, founders)
  - `GPE` - Geopolitical entities (countries, cities)
  - `DATE` - Dates and time periods
  - `PRODUCT` - Products and services
  - `MONEY` - Monetary values
  - `PERCENT` - Percentages

### 2. Sentiment Analysis
- **Polarity**: -1.0 (negative) to 1.0 (positive)
- **Subjectivity**: 0.0 (objective) to 1.0 (subjective)
- **Classification**: Positive, Negative, or Neutral

### 3. Relationship Extraction
- **Entity Co-occurrence**: Detect entities mentioned together
- **Context Extraction**: Capture surrounding text context
- **Distance-based**: Configurable proximity threshold

### 4. Keyword Extraction
- **POS-based**: Filter by part-of-speech tags
- **Frequency-ranked**: Top N most important terms
- **Stopword filtering**: Remove common words

### 5. Entity Tracking (Monitoring)
- **Change Detection**: Track entity mentions across snapshots
- **Relationship Changes**: Detect new partnerships, acquisitions
- **Smart Alerts**: Priority-based alerts for significant changes

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

For better accuracy (larger model):
```bash
python -m spacy download en_core_web_md
```

## Usage

### Basic NLP Processing

```python
from consultantos.tools.nlp_tool import NLPProcessor

# Initialize processor
nlp = NLPProcessor(model_name="en_core_web_sm")

# Extract entities
text = "Tesla CEO Elon Musk announced partnership with Samsung in Seoul"
entities = nlp.entity_extraction(text)
# [{'text': 'Tesla', 'label': 'ORG', 'start': 0, 'end': 5}, ...]

# Analyze sentiment
sentiment = nlp.sentiment_analysis(text)
# {'polarity': 0.2, 'subjectivity': 0.4, 'classification': 'positive'}

# Extract keywords
keywords = nlp.keyword_extraction(text, top_n=5)
# [{'text': 'Tesla', 'pos': 'PROPN', 'frequency': 1}, ...]

# Extract relationships
relationships = nlp.relationship_extraction(text)
# [{'entity1': {'text': 'Tesla', 'label': 'ORG'},
#   'entity2': {'text': 'Samsung', 'label': 'ORG'},
#   'distance': 15, 'context': 'announced partnership with'}]
```

### ResearchAgent Integration

The ResearchAgent automatically enriches research results with NLP analysis:

```python
from consultantos.agents.research_agent import ResearchAgent

# NLP enabled by default
agent = ResearchAgent(enable_nlp=True)

# Execute research
result = await agent.execute({
    "company": "Tesla",
    "industry": "Electric Vehicles"
})

# Access NLP-enriched data
print(f"Entities: {len(result.entities)}")
print(f"Sentiment: {result.sentiment.classification}")
print(f"Relationships: {len(result.entity_relationships)}")
print(f"Keywords: {len(result.keywords)}")
```

### Entity Tracking for Monitoring

Track entity changes across monitoring snapshots:

```python
from consultantos.monitoring.entity_tracker import EntityTracker, track_entity_changes

# Initialize tracker
tracker = EntityTracker(significance_threshold=2)

# Compare snapshots
entity_changes = tracker.compare_entities(
    previous_entities=previous_snapshot.entities,
    current_entities=current_snapshot.entities
)

relationship_changes = tracker.compare_relationships(
    previous_relationships=previous_snapshot.entity_relationships,
    current_relationships=current_snapshot.entity_relationships
)

# Generate alerts
alerts = tracker.generate_alerts(
    entity_changes=entity_changes,
    relationship_changes=relationship_changes,
    focus_companies=["Tesla", "BYD", "NIO"]
)

# High-priority alerts (priority >= 7)
high_priority = [alert for alert in alerts if alert['priority'] >= 7]
```

### Convenience Function

Quick analysis without managing processor lifecycle:

```python
from consultantos.tools.nlp_tool import analyze_text

# One-line analysis
results = analyze_text(
    "Tesla announces new battery technology partnership",
    include_relationships=True
)

print(results['entities'])
print(results['sentiment'])
print(results['keywords'])
print(results['relationships'])
```

## Data Models

### EntityMention

```python
from consultantos.models import EntityMention

entity = EntityMention(
    text="Tesla Inc.",
    label="ORG",
    start=0,
    end=10
)
```

### SentimentScore

```python
from consultantos.models import SentimentScore

sentiment = SentimentScore(
    polarity=0.5,
    subjectivity=0.6,
    classification="positive"
)
```

### EntityRelationship

```python
from consultantos.models import EntityRelationship

relationship = EntityRelationship(
    entity1={"text": "Tesla", "label": "ORG"},
    entity2={"text": "Samsung", "label": "ORG"},
    distance=50,
    context="announced partnership with"
)
```

### Enhanced CompanyResearch

The `CompanyResearch` model now includes NLP fields:

```python
from consultantos.models import CompanyResearch

research = CompanyResearch(
    company_name="Tesla Inc.",
    description="Electric vehicle manufacturer",
    products_services=["Model 3", "Model Y"],
    target_market="Global EV market",
    key_competitors=["BYD", "NIO"],
    recent_news=["Partnership announcement"],
    sources=["https://..."],

    # NLP enrichment
    entities=[...],  # List[EntityMention]
    sentiment=sentiment,  # SentimentScore
    entity_relationships=[...],  # List[EntityRelationship]
    keywords=[...]  # List[Dict[str, Any]]
)
```

## Entity Tracking Use Cases

### 1. Competitor Detection

Automatically detect new competitors mentioned in news:

```python
# Filter for new organization entities
new_competitors = [
    change for change in entity_changes
    if change.change_type == "new" and change.entity_label == "ORG"
]

# Alert: "New ORG entity detected: 'BYD Auto' (5 mentions)"
```

### 2. Partnership Monitoring

Track partnership announcements:

```python
# Filter for new relationships
new_partnerships = [
    change for change in relationship_changes
    if change.change_type == "new_relationship"
    and "partner" in ' '.join(change.current_contexts).lower()
]

# Alert: "New relationship detected: 'Tesla' announced partnership with 'Samsung'"
```

### 3. Sentiment Trends

Track sentiment changes over time:

```python
# Compare sentiment across snapshots
if current.sentiment.polarity > previous.sentiment.polarity + 0.2:
    # Alert: "Significant positive sentiment shift detected"
    pass
```

### 4. Executive Changes

Track leadership mentions:

```python
# Filter for person entities
executives = [
    entity for entity in entities
    if entity.label == "PERSON"
]

# Track changes in executive mentions
executive_changes = [
    change for change in entity_changes
    if change.entity_label == "PERSON"
]
```

## Configuration

### NLP Processor Configuration

```python
# Use smaller, faster model (default)
nlp = NLPProcessor(model_name="en_core_web_sm")

# Use larger, more accurate model
nlp = NLPProcessor(model_name="en_core_web_md")

# Disable caching
nlp = NLPProcessor(cache_enabled=False)
```

### Entity Tracker Configuration

```python
# Higher threshold = only track very significant entities
tracker = EntityTracker(significance_threshold=5)

# Lower threshold = track more entities (may be noisier)
tracker = EntityTracker(significance_threshold=1)
```

### ResearchAgent Configuration

```python
# Enable NLP (default)
agent = ResearchAgent(enable_nlp=True)

# Disable NLP (faster, no enrichment)
agent = ResearchAgent(enable_nlp=False)
```

## Performance Considerations

### Lazy Loading

The spaCy model is lazily loaded on first use, avoiding startup overhead:

```python
processor = NLPProcessor()  # No model loaded yet
entities = processor.entity_extraction(text)  # Model loaded on first use
```

### Caching

NLP results can be cached to avoid reprocessing:

```python
# Singleton pattern - reuses same processor instance
from consultantos.tools.nlp_tool import get_nlp_processor

processor = get_nlp_processor()  # Cached instance
```

### Graceful Degradation

NLP failures don't break the system:

```python
# If NLP fails, ResearchAgent continues with empty NLP fields
if self.enable_nlp:
    try:
        research_data = self._enrich_with_nlp(research_data, context)
    except Exception as e:
        logger.warning(f"NLP enrichment failed: {e}")
        # Continue with empty NLP fields
```

## Testing

### Run NLP Tests

```bash
# Run all NLP tests
pytest tests/test_nlp_tool.py -v

# Run with coverage
pytest tests/test_nlp_tool.py --cov=consultantos.tools.nlp_tool

# Run specific test
pytest tests/test_nlp_tool.py::TestNLPProcessor::test_entity_extraction_basic -v
```

### Test Coverage

- Entity extraction (basic, filtered, empty text)
- Sentiment analysis (positive, negative, neutral)
- Relationship extraction (basic, distance filtering)
- Keyword extraction (basic, POS filtering)
- Language detection and non-English handling
- Edge cases (long text, special characters, numbers)
- Integration scenarios (competitor detection, partnerships)

## Architecture

### NLP Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ResearchAgent                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Tavily    │→ │   LLM        │→ │   NLP        │      │
│  │   Search    │  │   Extraction │  │   Enrichment │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   CompanyResearch                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Standard   │  │   Entities   │  │   Sentiment  │      │
│  │   Fields     │  │   Keywords   │  │   Relations  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               Monitoring & Entity Tracking                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Snapshot   │  │   Compare    │  │   Generate   │      │
│  │   Storage    │  │   Entities   │  │   Alerts     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Entity Tracking Flow

```
Previous Snapshot          Current Snapshot
┌─────────────┐            ┌─────────────┐
│  Entities   │            │  Entities   │
│  Relations  │            │  Relations  │
└─────────────┘            └─────────────┘
       │                          │
       └────────┬─────────────────┘
                ↓
        ┌───────────────┐
        │ EntityTracker │
        └───────────────┘
                ↓
    ┌───────────────────────┐
    │   Change Detection    │
    │  - New entities       │
    │  - Removed entities   │
    │  - Changed mentions   │
    │  - New relationships  │
    └───────────────────────┘
                ↓
        ┌───────────────┐
        │ Alert System  │
        │ - Priority    │
        │ - Messages    │
        └───────────────┘
```

## Example Outputs

### Entity Extraction Example

```json
[
  {"text": "Tesla Inc.", "label": "ORG", "start": 0, "end": 10},
  {"text": "Elon Musk", "label": "PERSON", "start": 15, "end": 24},
  {"text": "Samsung Electronics", "label": "ORG", "start": 50, "end": 69},
  {"text": "Seoul", "label": "GPE", "start": 73, "end": 78},
  {"text": "$10 billion", "label": "MONEY", "start": 95, "end": 106}
]
```

### Sentiment Analysis Example

```json
{
  "polarity": 0.35,
  "subjectivity": 0.65,
  "classification": "positive"
}
```

### Relationship Extraction Example

```json
[
  {
    "entity1": {"text": "Tesla", "label": "ORG"},
    "entity2": {"text": "Samsung", "label": "ORG"},
    "distance": 45,
    "context": "announced strategic partnership with"
  }
]
```

### Entity Tracking Alert Example

```json
{
  "type": "entity_change",
  "priority": 8,
  "message": "New ORG entity detected: 'BYD Auto' (7 mentions)",
  "details": {
    "entity_text": "BYD Auto",
    "entity_label": "ORG",
    "change_type": "new",
    "previous_count": 0,
    "current_count": 7
  }
}
```

## Troubleshooting

### Model Not Found

```bash
# Error: Can't find model 'en_core_web_sm'
python -m spacy download en_core_web_sm
```

### Non-English Text

Non-English text is automatically detected and skipped:

```python
# Returns empty list for non-English text
entities = nlp.entity_extraction("这是中文文本")  # []
```

### Performance Issues

For large-scale processing, consider:

1. Use smaller model (`en_core_web_sm` vs `en_core_web_md`)
2. Enable caching
3. Process in batches
4. Disable relationship extraction (slower)

```python
# Faster configuration
nlp = NLPProcessor(model_name="en_core_web_sm", cache_enabled=True)
results = nlp.process_article(title, content, extract_relationships=False)
```

## Future Enhancements

1. **Multi-language support**: Add language detection and multi-language models
2. **Custom entity types**: Train custom NER for industry-specific entities
3. **Advanced relationship extraction**: Use dependency parsing for better relationships
4. **Coreference resolution**: Link pronouns to entities
5. **Topic modeling**: Add LDA/NMF for topic extraction
6. **Aspect-based sentiment**: Sentiment per aspect (product, service, price)
7. **Entity linking**: Link entities to knowledge bases (Wikipedia, Wikidata)
8. **Temporal relationship tracking**: Track entity relationships over time graphs

## References

- [spaCy Documentation](https://spacy.io/usage)
- [TextBlob Sentiment Analysis](https://textblob.readthedocs.io/en/dev/quickstart.html#sentiment-analysis)
- [Named Entity Recognition Guide](https://spacy.io/usage/linguistic-features#named-entities)
- [Entity Linking](https://spacy.io/api/entitylinker)
