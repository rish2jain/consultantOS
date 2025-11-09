# Personal Knowledge Base Guide

## Overview

The Personal Knowledge Base (PKB) is ConsultantOS's most powerful switching cost feature. It automatically aggregates insights across all your analyses, creating an increasingly valuable personal research database that would be painful to recreate elsewhere.

## The Switching Cost Mechanism

### Value Accumulation Over Time

Every analysis you run adds to your personal knowledge base:

```
Analysis 1 (Tesla) → KB Value = 1x
Analysis 2 (GM) → KB Value = 2x (+ cross-company insights)
Analysis 3 (Tesla v2) → KB Value = 3x (+ temporal patterns)
Analysis 10 → KB Value = 10x (+ industry patterns)
Analysis 50 → KB Value = 100x (+ deep connections)
```

**Key Insight**: KB value grows super-linearly. Your 50th analysis is worth far more than 50x your first analysis because of accumulated connections.

### What Makes It Sticky

1. **Automatic Indexing**: Every analysis automatically enhances your KB
2. **Semantic Search**: Find insights across all historical analyses
3. **Timeline Tracking**: See how companies/industries evolved in your research
4. **Connection Graphs**: Discover relationships between entities you've analyzed
5. **Custom Patterns**: Your unique analytical patterns and insights

## Core Features

### 1. Semantic Search Across All Analyses

Search your entire analysis history:

```bash
POST /knowledge/search
{
  "query": "battery technology competitive advantage",
  "limit": 10,
  "filters": {
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"],
    "from_date": "2024-01-01"
  }
}
```

**Returns**:
- Ranked insights from across all analyses
- Relevance scores based on query matching
- Recency boost for recent analyses
- Context from original framework analysis

### 2. Company Timeline

Track how your analysis of a company evolved:

```bash
GET /knowledge/timeline/Tesla
```

**Shows**:
- All analyses of Tesla over time
- Key changes detected between versions
- Trend summary (e.g., "Confidence improved 0.3 over 6 months")
- Framework usage evolution

### 3. Knowledge Graph

Visualize connections between entities:

```bash
GET /knowledge/connections/Tesla
```

**Returns**:
- Nodes: Companies, industries, frameworks you've analyzed
- Edges: Relationships (competitor, same industry, supplier/customer)
- Weights: Frequency of co-analysis
- Visual graph data for frontend rendering

### 4. KB Statistics

Monitor your knowledge accumulation:

```bash
GET /knowledge/stats
```

**Provides**:
- Total analyses in KB
- Companies analyzed (unique count)
- Industries covered
- Framework usage distribution
- Temporal coverage (oldest to newest)

## How It Creates Switching Costs

### The Compounding Effect

**Month 1** (5 analyses):
- Basic KB functionality
- Simple search works
- Limited value

**Month 3** (20 analyses):
- Useful cross-references
- Timeline patterns emerge
- Moderate switching pain

**Month 6** (50 analyses):
- Rich connection graph
- Deep industry knowledge
- High switching pain

**Month 12** (100+ analyses):
- Irreplaceable research asset
- Unique insights only you have
- Extreme switching pain

### What You'd Lose By Switching

1. **Search History**: Years of analyses instantly searchable
2. **Temporal Insights**: How markets evolved in your research
3. **Connection Discovery**: Relationships you didn't know existed
4. **Pattern Recognition**: Your KB learns your analytical style
5. **Cross-Analysis Synthesis**: Insights that span multiple analyses

### Migration Impossibility

To recreate your KB elsewhere, you'd need to:
1. Export all analyses (if even possible)
2. Manually index them in new system
3. Recreate temporal relationships
4. Rebuild connection graphs
5. **Lose all semantic search capabilities**
6. **Lose all automated pattern detection**

**Reality**: Most users would effectively start from zero.

## Advanced Usage

### Saved Searches with Auto-Index

Automatically add new analyses to monitored topics:

```python
# Create saved search
response = requests.post(
    "https://api.consultantos.app/saved-searches",
    json={
        "name": "EV Market Intelligence",
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "pestel"],
        "auto_run": True,
        "schedule": "0 9 * * 1"  # Every Monday 9am
    },
    headers={"X-API-Key": "your-api-key"}
)

# Auto-run results automatically index into KB
# Your knowledge base grows while you sleep!
```

### Cross-Company Analysis

Find patterns across your portfolio:

```python
# Search for common themes
response = requests.post(
    "https://api.consultantos.app/knowledge/search",
    json={
        "query": "supply chain vulnerabilities",
        "filters": {
            "industry": "Technology"
        }
    },
    headers={"X-API-Key": "your-api-key"}
)

# Results show supply chain patterns across:
# - Apple, Microsoft, Intel, NVIDIA (from your past analyses)
# - Temporal changes in supply chain risks
# - Industry-wide trends you've documented
```

### Custom Framework Integration

Your custom frameworks automatically enhance KB:

```python
# Create custom framework
requests.post(
    "https://api.consultantos.app/custom-frameworks",
    json={
        "name": "Battery Supply Chain Analysis",
        "description": "Deep dive on EV battery supply dynamics",
        "prompt_template": "Analyze {company}'s battery supply chain...",
        "response_schema": {...}
    },
    headers={"X-API-Key": "your-api-key"}
)

# Use in analysis
requests.post(
    "https://api.consultantos.app/analyze",
    json={
        "company": "Tesla",
        "frameworks": ["battery_supply_chain"],  # Your custom framework
    }
)

# Results automatically indexed with custom insights
# KB now searchable by your unique analytical dimensions
```

## Retention Metrics

### User Stickiness Indicators

**Low Retention Risk** (< 10 analyses):
- KB not yet valuable
- Easy to switch platforms
- Minimal sunk cost

**Moderate Retention** (10-50 analyses):
- KB becoming useful
- Some switching pain
- Growing sunk cost

**High Retention** (50-100 analyses):
- KB highly valuable
- Significant switching pain
- High sunk cost

**Locked In** (100+ analyses):
- KB irreplaceable
- Extreme switching pain
- **Effective vendor lock-in achieved**

### Growth Indicators

Track these to identify power users:
- Analyses per month (velocity)
- Saved searches with auto-run (automation)
- Custom frameworks created (investment)
- KB search frequency (dependency)
- Timeline views (temporal analysis)

## Monetization Opportunities

### Tiered KB Features

**Free Tier**:
- 50 analyses in KB
- Basic search
- No timeline/graph

**Pro Tier**:
- Unlimited analyses
- Advanced search with filters
- Timeline tracking
- Connection graphs

**Enterprise**:
- Multi-user KB sharing
- API access to KB
- Custom export formats
- Advanced analytics

### Upgrade Triggers

Users likely to upgrade when:
1. Hit KB limits (50 analyses for free)
2. Need timeline features (after 20+ analyses)
3. Want connection graphs (after analyzing 5+ competitors)
4. Require team knowledge sharing

## Technical Implementation

### Auto-Indexing

Every analysis completion triggers:

```python
# In orchestrator after analysis completes
from consultantos.knowledge.personal_kb import PersonalKnowledgeBase

kb = PersonalKnowledgeBase(db)
await kb.add_analysis(user_id, strategic_report)

# Automatically extracts:
# - Key insights from executive summary
# - Framework-specific findings
# - Company/industry metadata
# - Temporal information
```

### Search Algorithm

1. **Keyword Matching**: Basic relevance from query terms
2. **Recency Boost**: Recent analyses weighted higher
3. **Framework Filtering**: Narrow to specific analytical dimensions
4. **Relevance Scoring**: Combined score for ranking

Future enhancements:
- Semantic embeddings (vector search)
- LLM-powered query understanding
- Cross-analysis synthesis

### Performance Optimization

- Index on company, industry, created_at
- Cache frequent searches
- Lazy-load graph connections
- Paginate timeline results

## Success Metrics

### KB Adoption
- % users with >10 analyses indexed
- Average KB size by cohort
- KB search frequency

### Switching Cost Strength
- Analysis count by user
- Time since first analysis
- Custom framework attachment
- Team KB sharing

### Revenue Impact
- KB-driven upgrades
- Retention by KB size
- Enterprise adoption via team KB

## API Reference

**Base URL**: `https://api.consultantos.app/knowledge`

### Search
- `POST /search` - Search across all analyses
  - Query: string
  - Filters: company, industry, frameworks, dates
  - Returns: Ranked knowledge items

### Timeline
- `GET /timeline/{company}` - Get company analysis timeline
  - Returns: Chronological analyses with changes

### Connections
- `GET /connections/{company}` - Get knowledge graph
  - Returns: Nodes and edges for visualization

### Statistics
- `GET /stats` - Get KB statistics
  - Returns: Counts, distributions, coverage

## Best Practices

1. **Encourage Breadth**: Analyze diverse companies/industries early
2. **Build Temporal Patterns**: Re-analyze companies quarterly
3. **Cross-Reference**: Use search to connect related analyses
4. **Create Custom Frameworks**: Invest in unique analytical approaches
5. **Share Team Knowledge**: Multiply switching costs across teams

## Support

KB questions or feature requests:
- Email: kb@consultantos.app
- Documentation: https://docs.consultantos.app/knowledge-base
- Community forum: https://community.consultantos.app
