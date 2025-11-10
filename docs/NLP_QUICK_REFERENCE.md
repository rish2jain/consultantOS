# NLP Integration - Quick Reference Card

## Installation

```bash
# Quick setup
./scripts/setup_nlp.sh

# Manual
pip install spacy>=3.7.0 textblob>=0.17.0
python -m spacy download en_core_web_sm
python -m textblob.download_corpora
```

## Basic Usage

### Quick Analysis
```python
from consultantos.tools.nlp_tool import analyze_text

results = analyze_text("Your text here", include_relationships=True)
print(results['entities'])      # Entity list
print(results['sentiment'])     # Sentiment scores
print(results['keywords'])      # Key terms
print(results['relationships']) # Entity pairs
```

### NLP Processor
```python
from consultantos.tools.nlp_tool import NLPProcessor

nlp = NLPProcessor()

# Extract entities
entities = nlp.entity_extraction(text, entity_types=['ORG', 'PERSON'])

# Analyze sentiment
sentiment = nlp.sentiment_analysis(text)

# Extract relationships
relationships = nlp.relationship_extraction(text, max_distance=100)

# Extract keywords
keywords = nlp.keyword_extraction(text, top_n=10)

# Process full article
results = nlp.process_article(title, content, extract_relationships=True)
```

## ResearchAgent Integration

```python
from consultantos.agents.research_agent import ResearchAgent

# NLP enabled by default
agent = ResearchAgent(enable_nlp=True)

result = await agent.execute({
    "company": "Tesla",
    "industry": "Electric Vehicles"
})

# Access NLP data
for entity in result.entities:
    print(f"{entity.label}: {entity.text}")

print(f"Sentiment: {result.sentiment.classification}")
print(f"Relationships: {len(result.entity_relationships)}")
```

## Entity Tracking

```python
from consultantos.monitoring.entity_tracker import track_entity_changes

tracking = track_entity_changes(
    previous_entities=prev.entities,
    current_entities=curr.entities,
    previous_relationships=prev.entity_relationships,
    current_relationships=curr.entity_relationships,
    focus_companies=["Tesla", "BYD"]
)

# Review high-priority alerts
high_priority = [a for a in tracking['alerts'] if a['priority'] >= 7]
for alert in high_priority:
    print(f"[P{alert['priority']}] {alert['message']}")
```

## Entity Types

| Label | Description | Examples |
|-------|-------------|----------|
| ORG | Organizations | Tesla, Samsung, Apple |
| PERSON | People | Elon Musk, Tim Cook |
| GPE | Geopolitical entities | Seoul, California, USA |
| DATE | Dates/times | Q3 2024, yesterday, 2027 |
| PRODUCT | Products | iPhone, Model 3 |
| MONEY | Money values | $100M, €50B |
| PERCENT | Percentages | 15%, 7.5% |

## Sentiment Classification

| Classification | Polarity Range | Example |
|---------------|----------------|---------|
| Positive | > 0.1 | "Excellent results" |
| Neutral | -0.1 to 0.1 | "Results announced" |
| Negative | < -0.1 | "Disappointing performance" |

## Alert Priorities

| Priority | Meaning | Example |
|----------|---------|---------|
| 9-10 | Critical | New partnership, major competitor |
| 7-8 | High | New entity, relationship change |
| 4-6 | Medium | Mention increase, sentiment shift |
| 1-3 | Low | Minor changes |

## Common Patterns

### Competitor Detection
```python
# Filter for new organization entities
new_competitors = [
    change for change in entity_changes
    if change.change_type == "new"
    and change.entity_label == "ORG"
    and change.current_count >= 3  # Significance threshold
]
```

### Partnership Detection
```python
# Find new relationships with partnership context
partnerships = [
    change for change in relationship_changes
    if change.change_type == "new_relationship"
    and any(word in ' '.join(change.current_contexts).lower()
            for word in ['partner', 'collaborate', 'alliance'])
]
```

### Sentiment Tracking
```python
# Compare sentiment across snapshots
polarity_change = curr.sentiment.polarity - prev.sentiment.polarity

if abs(polarity_change) > 0.3:  # Significant change
    print(f"Sentiment shift: {polarity_change:+.2f}")
```

## Configuration

### NLP Processor
```python
# Small, fast model (default)
NLPProcessor(model_name="en_core_web_sm")

# Larger, more accurate model
NLPProcessor(model_name="en_core_web_md")

# Disable caching
NLPProcessor(cache_enabled=False)
```

### Entity Tracker
```python
# Higher threshold (less noise)
EntityTracker(significance_threshold=5)

# Lower threshold (more coverage)
EntityTracker(significance_threshold=1)
```

### ResearchAgent
```python
# Enable NLP (default)
ResearchAgent(enable_nlp=True)

# Disable NLP (faster)
ResearchAgent(enable_nlp=False)
```

## Testing

```bash
# Run all tests
pytest tests/test_nlp_tool.py -v

# Run with coverage
pytest tests/test_nlp_tool.py --cov=consultantos.tools.nlp_tool

# Run specific test
pytest tests/test_nlp_tool.py::TestNLPProcessor::test_entity_extraction_basic
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
    polarity=0.5,       # -1.0 to 1.0
    subjectivity=0.6,   # 0.0 to 1.0
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

## Performance Tips

1. **Lazy Loading**: Model loads on first use
2. **Caching**: Use `get_nlp_processor()` for singleton
3. **Language Detection**: Non-English text auto-skipped
4. **Graceful Degradation**: NLP failures don't break system
5. **Batching**: Process multiple texts together when possible

## Troubleshooting

### Model Not Found
```bash
# Download spaCy model
python -m spacy download en_core_web_sm
```

### Slow Performance
```python
# Use smaller model
nlp = NLPProcessor(model_name="en_core_web_sm")

# Disable relationship extraction (slower)
results = nlp.process_article(title, content, extract_relationships=False)
```

### Memory Issues
```python
# Process in smaller batches
# Disable caching if needed
nlp = NLPProcessor(cache_enabled=False)
```

## File Locations

```
consultantos/
├── tools/nlp_tool.py              # NLP processor
├── monitoring/entity_tracker.py   # Entity tracking
├── agents/research_agent.py       # Integrated NLP
└── models.py                      # NLP data models

tests/
└── test_nlp_tool.py              # Comprehensive tests

docs/
├── NLP_INTEGRATION.md            # Full documentation
├── NLP_EXAMPLE_OUTPUT.md         # Example outputs
└── NLP_QUICK_REFERENCE.md        # This file

scripts/
└── setup_nlp.sh                  # Setup automation
```

## Key Commands

```bash
# Setup
./scripts/setup_nlp.sh

# Test
pytest tests/test_nlp_tool.py -v

# Run server with NLP
python main.py

# Check model
python -c "import spacy; spacy.load('en_core_web_sm')"
```

## Resources

- **Full Docs**: `docs/NLP_INTEGRATION.md`
- **Examples**: `docs/NLP_EXAMPLE_OUTPUT.md`
- **Tests**: `tests/test_nlp_tool.py`
- **spaCy Docs**: https://spacy.io
- **TextBlob Docs**: https://textblob.readthedocs.io
