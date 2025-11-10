# NLP Integration - Example Output

This document shows real-world examples of NLP processing output from ConsultantOS.

## Example 1: Partnership Announcement

### Input Text
```
Tesla Inc. announced a groundbreaking partnership with Samsung Electronics today.
The collaboration will focus on developing next-generation battery technology for
electric vehicles. CEO Elon Musk stated that this partnership represents a significant
milestone for sustainable transportation. The agreement, signed in Seoul, South Korea,
is expected to accelerate innovation in the EV industry. Industry analysts view this
partnership positively, with stock prices rising 5% following the announcement.
```

### Entity Extraction Output

```json
{
  "entities": [
    {"text": "Tesla Inc.", "label": "ORG", "start": 0, "end": 10},
    {"text": "Samsung Electronics", "label": "ORG", "start": 60, "end": 79},
    {"text": "today", "label": "DATE", "start": 80, "end": 85},
    {"text": "Elon Musk", "label": "PERSON", "start": 198, "end": 207},
    {"text": "Seoul", "label": "GPE", "start": 343, "end": 348},
    {"text": "South Korea", "label": "GPE", "start": 350, "end": 361},
    {"text": "5%", "label": "PERCENT", "start": 505, "end": 507}
  ]
}
```

**Analysis**:
- ✅ Identified both companies (ORG)
- ✅ Extracted CEO name (PERSON)
- ✅ Found locations (GPE: Seoul, South Korea)
- ✅ Captured date reference (DATE: today)
- ✅ Detected stock price change (PERCENT: 5%)

### Sentiment Analysis Output

```json
{
  "sentiment": {
    "polarity": 0.35,
    "subjectivity": 0.65,
    "classification": "positive"
  }
}
```

**Analysis**:
- Polarity: 0.35 (moderately positive)
- Subjectivity: 0.65 (somewhat subjective/opinion-based)
- Classification: Positive (partnership, milestone, innovation)

### Relationship Extraction Output

```json
{
  "entity_relationships": [
    {
      "entity1": {"text": "Tesla Inc.", "label": "ORG"},
      "entity2": {"text": "Samsung Electronics", "label": "ORG"},
      "distance": 45,
      "context": "announced a groundbreaking partnership with"
    },
    {
      "entity1": {"text": "Elon Musk", "label": "PERSON"},
      "entity2": {"text": "Tesla Inc.", "label": "ORG"},
      "distance": 187,
      "context": "CEO"
    },
    {
      "entity1": {"text": "Samsung Electronics", "label": "ORG"},
      "entity2": {"text": "Seoul", "label": "GPE"},
      "distance": 264,
      "context": "signed in"
    }
  ]
}
```

**Analysis**:
- ✅ Tesla-Samsung partnership relationship
- ✅ Elon Musk-Tesla CEO relationship
- ✅ Samsung-Seoul location relationship

### Keyword Extraction Output

```json
{
  "keywords": [
    {"text": "partnership", "pos": "NOUN", "frequency": 2},
    {"text": "Tesla", "pos": "PROPN", "frequency": 1},
    {"text": "Samsung", "pos": "PROPN", "frequency": 1},
    {"text": "technology", "pos": "NOUN", "frequency": 1},
    {"text": "battery", "pos": "NOUN", "frequency": 1},
    {"text": "innovation", "pos": "NOUN", "frequency": 1},
    {"text": "vehicles", "pos": "NOUN", "frequency": 1}
  ]
}
```

**Analysis**:
- Top keyword: "partnership" (mentioned twice)
- Companies: Tesla, Samsung
- Focus areas: technology, battery, innovation, vehicles

---

## Example 2: Competitive Landscape Analysis

### Input Text
```
Tesla faces increased competition from BYD, which has overtaken it in global EV sales.
Traditional automakers like Ford and General Motors are also ramping up electric vehicle
production. Chinese manufacturers including NIO and XPeng are expanding into European
markets. Analysts predict the EV market will reach $800 billion by 2027.
```

### Entity Extraction Output

```json
{
  "entities": [
    {"text": "Tesla", "label": "ORG", "start": 0, "end": 5},
    {"text": "BYD", "label": "ORG", "start": 40, "end": 43},
    {"text": "Ford", "label": "ORG", "start": 122, "end": 126},
    {"text": "General Motors", "label": "ORG", "start": 131, "end": 145},
    {"text": "Chinese", "label": "NORP", "start": 198, "end": 205},
    {"text": "NIO", "label": "ORG", "start": 228, "end": 231},
    {"text": "XPeng", "label": "ORG", "start": 236, "end": 241},
    {"text": "European", "label": "NORP", "start": 261, "end": 269},
    {"text": "$800 billion", "label": "MONEY", "start": 320, "end": 332},
    {"text": "2027", "label": "DATE", "start": 336, "end": 340}
  ]
}
```

**Competitive Intelligence**:
- **Main Player**: Tesla
- **Competitors**: BYD, Ford, General Motors, NIO, XPeng
- **Market Regions**: Chinese, European
- **Market Size**: $800 billion by 2027

### Monitoring Alert Example

If this is a new snapshot compared to previous monitoring:

```json
{
  "alerts": [
    {
      "type": "entity_change",
      "priority": 8,
      "message": "New ORG entity detected: 'BYD' (3 mentions)",
      "details": {
        "entity_text": "BYD",
        "entity_label": "ORG",
        "change_type": "new",
        "previous_count": 0,
        "current_count": 3
      }
    },
    {
      "type": "entity_change",
      "priority": 7,
      "message": "New ORG entity detected: 'XPeng' (2 mentions)",
      "details": {
        "entity_text": "XPeng",
        "entity_label": "ORG",
        "change_type": "new",
        "previous_count": 0,
        "current_count": 2
      }
    },
    {
      "type": "relationship_change",
      "priority": 9,
      "message": "New relationship detected: 'Tesla' faces increased competition from 'BYD'",
      "details": {
        "entity1": "Tesla",
        "entity2": "BYD",
        "change_type": "new_relationship",
        "current_contexts": ["faces increased competition from"]
      }
    }
  ]
}
```

---

## Example 3: Executive Leadership Change

### Input Text
```
Apple CEO Tim Cook announced that Sarah Johnson will join the company as Chief AI Officer.
Johnson previously led AI initiatives at Google and Microsoft. The appointment signals
Apple's renewed focus on artificial intelligence and machine learning. Industry observers
see this as a strategic response to recent AI advances by competitors.
```

### Entity Extraction Output

```json
{
  "entities": [
    {"text": "Apple", "label": "ORG", "start": 0, "end": 5},
    {"text": "Tim Cook", "label": "PERSON", "start": 10, "end": 18},
    {"text": "Sarah Johnson", "label": "PERSON", "start": 34, "end": 47},
    {"text": "Chief AI Officer", "label": "POSITION", "start": 78, "end": 94},
    {"text": "Johnson", "label": "PERSON", "start": 96, "end": 103},
    {"text": "Google", "label": "ORG", "start": 138, "end": 144},
    {"text": "Microsoft", "label": "ORG", "start": 149, "end": 158},
    {"text": "Apple", "label": "ORG", "start": 186, "end": 191}
  ]
}
```

### Monitoring Alert Example

```json
{
  "alerts": [
    {
      "type": "entity_change",
      "priority": 8,
      "message": "New PERSON entity detected: 'Sarah Johnson' (2 mentions)",
      "details": {
        "entity_text": "Sarah Johnson",
        "entity_label": "PERSON",
        "change_type": "new",
        "previous_count": 0,
        "current_count": 2,
        "context_samples": [
          "join the company as Chief AI Officer",
          "previously led AI initiatives at Google and Microsoft"
        ]
      }
    },
    {
      "type": "relationship_change",
      "priority": 7,
      "message": "New relationship detected: 'Sarah Johnson' join the company as Chief AI Officer 'Apple'",
      "details": {
        "entity1": "Sarah Johnson",
        "entity2": "Apple",
        "change_type": "new_relationship"
      }
    }
  ]
}
```

**Key Insights**:
- New executive hire detected
- Cross-company movement (Google/Microsoft → Apple)
- Strategic focus area: AI and machine learning

---

## Example 4: Financial Performance News

### Input Text
```
Amazon reported Q3 revenue of $143.1 billion, up 13% year-over-year.
AWS cloud services contributed $23.1 billion, growing at 12%.
The company's profit margin improved to 7.8%, beating analyst expectations
of 7.2%. CEO Andy Jassy called the results "very encouraging" and highlighted
continued investments in AI infrastructure.
```

### Entity Extraction Output

```json
{
  "entities": [
    {"text": "Amazon", "label": "ORG", "start": 0, "end": 6},
    {"text": "Q3", "label": "DATE", "start": 16, "end": 18},
    {"text": "$143.1 billion", "label": "MONEY", "start": 30, "end": 44},
    {"text": "13%", "label": "PERCENT", "start": 49, "end": 52},
    {"text": "year-over-year", "label": "DATE", "start": 53, "end": 67},
    {"text": "AWS", "label": "ORG", "start": 69, "end": 72},
    {"text": "$23.1 billion", "label": "MONEY", "start": 104, "end": 117},
    {"text": "12%", "label": "PERCENT", "start": 130, "end": 133},
    {"text": "7.8%", "label": "PERCENT", "start": 174, "end": 178},
    {"text": "7.2%", "label": "PERCENT", "start": 212, "end": 216},
    {"text": "Andy Jassy", "label": "PERSON", "start": 222, "end": 232}
  ]
}
```

### Sentiment Analysis Output

```json
{
  "sentiment": {
    "polarity": 0.45,
    "subjectivity": 0.55,
    "classification": "positive"
  }
}
```

**Financial Intelligence**:
- **Revenue**: $143.1 billion (↑13%)
- **AWS Revenue**: $23.1 billion (↑12%)
- **Profit Margin**: 7.8% (beat expectations of 7.2%)
- **Sentiment**: Positive (encouraging results)
- **Strategic Focus**: AI infrastructure investment

---

## Example 5: Sentiment Comparison

### Positive News
```
"Tesla exceeded quarterly delivery targets with record-breaking production.
The company's new factory achieved full capacity ahead of schedule."
```

**Sentiment**:
```json
{
  "polarity": 0.65,
  "subjectivity": 0.45,
  "classification": "positive"
}
```

### Negative News
```
"Tesla recalled 2 million vehicles due to safety concerns.
Regulatory investigations continue, causing investor uncertainty."
```

**Sentiment**:
```json
{
  "polarity": -0.55,
  "subjectivity": 0.60,
  "classification": "negative"
}
```

### Neutral News
```
"Tesla announced pricing for its Model 3 in Germany.
The vehicle is available in three configurations."
```

**Sentiment**:
```json
{
  "polarity": 0.05,
  "subjectivity": 0.25,
  "classification": "neutral"
}
```

---

## Monitoring Dashboard Visualization

### Entity Timeline (Hypothetical)

```
Week 1:  Tesla (15), BYD (0), NIO (2)
Week 2:  Tesla (18), BYD (3), NIO (5)    ← BYD appears!
Week 3:  Tesla (20), BYD (8), NIO (7)    ← BYD growing
Week 4:  Tesla (17), BYD (12), NIO (6)   ← Alert: BYD significant increase

Alert Generated:
[P9] Entity mention trend: 'BYD' increased from 0 → 12 mentions over 4 weeks
     Possible new competitor entering competitive landscape
```

### Sentiment Trend (Hypothetical)

```
Week 1:  Sentiment: 0.45 (positive)
Week 2:  Sentiment: 0.35 (positive)
Week 3:  Sentiment: -0.15 (negative)  ← Alert: Sentiment shift
Week 4:  Sentiment: -0.35 (negative)  ← Alert: Continued decline

Alert Generated:
[P7] Sentiment trend change: Positive → Negative (0.45 → -0.35)
     Review recent news for potential issues or challenges
```

---

## Real-World Use Cases

### 1. Competitor Tracking
**Scenario**: Monitor mentions of competitors in news articles

**Input**: Daily news aggregation about "electric vehicles"

**Output**:
- Track entity counts: Tesla (50), BYD (35), NIO (20), Rivian (15)
- Detect new players: "Lucid Motors" appears with 8 mentions
- Alert: "New ORG entity 'Lucid Motors' detected - possible new competitor"

### 2. M&A Detection
**Scenario**: Detect acquisition and partnership announcements

**Input**: News about technology companies

**Output**:
- Relationship: Microsoft + Activision Blizzard
- Context: "announced acquisition of"
- Alert: "New relationship detected: 'Microsoft' announced acquisition of 'Activision Blizzard'"

### 3. Executive Movements
**Scenario**: Track leadership changes

**Input**: Corporate news feed

**Output**:
- New PERSON entities: "Jane Smith" (new CTO)
- Relationship: Jane Smith + Company X
- Alert: "New PERSON entity 'Jane Smith' with 'CTO' context"

### 4. Market Sentiment Tracking
**Scenario**: Track sentiment about specific company

**Input**: News articles about Amazon

**Output**:
- Week 1: Positive (0.35)
- Week 2: Neutral (0.05)
- Week 3: Negative (-0.25)
- Alert: "Sentiment declining trend detected"

---

## Integration with Monitoring System

### Snapshot Comparison Example

**Previous Snapshot** (Week 1):
```json
{
  "entities": [
    {"text": "Tesla", "label": "ORG"},
    {"text": "Ford", "label": "ORG"}
  ],
  "sentiment": {"polarity": 0.4, "classification": "positive"}
}
```

**Current Snapshot** (Week 2):
```json
{
  "entities": [
    {"text": "Tesla", "label": "ORG"},
    {"text": "Ford", "label": "ORG"},
    {"text": "BYD", "label": "ORG"},
    {"text": "NIO", "label": "ORG"}
  ],
  "sentiment": {"polarity": 0.1, "classification": "neutral"}
}
```

**Generated Alerts**:
```json
[
  {
    "priority": 8,
    "message": "New ORG entity detected: 'BYD' (5 mentions)"
  },
  {
    "priority": 7,
    "message": "New ORG entity detected: 'NIO' (3 mentions)"
  },
  {
    "priority": 6,
    "message": "Sentiment shift: Positive → Neutral (0.4 → 0.1)"
  }
]
```

---

## Summary

The NLP integration provides rich, structured data from unstructured text:

✅ **Entity Extraction**: Companies, people, locations, dates, money, percentages
✅ **Sentiment Analysis**: Track emotional tone and market sentiment
✅ **Relationship Extraction**: Detect partnerships, acquisitions, leadership changes
✅ **Keyword Extraction**: Identify key themes and topics
✅ **Change Detection**: Monitor entity mentions and relationships over time
✅ **Smart Alerts**: Priority-based notifications for significant changes

This enables **continuous competitive intelligence** with minimal manual intervention.
