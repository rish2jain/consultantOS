# Phase 2 Quickstart Guide

**Goal**: Get Phase 2 skills running in 30 minutes with minimal implementations

**Prerequisites**:
- Phase 1 skills deployed and functional
- Cloud Run environment configured
- Twitter/LinkedIn/Reddit API credentials

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install tweepy==4.14.0 praw==7.7.1 numpy==1.26.0 sympy==1.12 python-pptx==0.6.21
```

### 2. Configure API Keys

Create `.env`:
```bash
# Social Media APIs
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
LINKEDIN_CLIENT_ID=your_linkedin_id
LINKEDIN_CLIENT_SECRET=your_linkedin_secret
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=ConsultantOS/1.0
```

### 3. Create Firestore Collections

```bash
# Run from project root
python scripts/setup_phase2_firestore.py
```

This creates 4 new collections:
- `social_monitors` - Social listening configurations
- `social_posts` - Ingested social media content
- `scenarios` - Wargaming scenario definitions
- `dashboards` - User-created analytics dashboards

## Social Media Intelligence (10 minutes)

### Minimal SocialMediaAgent

```python
# consultantos/agents/social_media_agent.py
from typing import List, Dict, Any
from datetime import datetime, timedelta
import tweepy
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.social_media import SocialMediaAnalysis, Platform, Post
from textblob import TextBlob

class SocialMediaAgent(BaseAgent):
    """Minimal social media monitoring implementation."""

    def __init__(self):
        super().__init__()
        self.twitter_client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN")
        )

    async def _execute_internal(
        self,
        company: str,
        timeframe_hours: int = 24,
        platforms: List[str] = ["twitter"]
    ) -> SocialMediaAnalysis:
        """Monitor social media for company mentions."""

        posts = []

        # Twitter search (100 most recent tweets)
        if "twitter" in platforms:
            query = f'"{company}" -is:retweet'
            start_time = datetime.utcnow() - timedelta(hours=timeframe_hours)

            tweets = self.twitter_client.search_recent_tweets(
                query=query,
                start_time=start_time,
                max_results=100,
                tweet_fields=["created_at", "public_metrics", "author_id"]
            )

            for tweet in tweets.data or []:
                # Basic sentiment analysis
                blob = TextBlob(tweet.text)
                sentiment_score = blob.sentiment.polarity  # -1 to 1

                posts.append(Post(
                    platform=Platform.TWITTER,
                    post_id=tweet.id,
                    author_id=tweet.author_id,
                    content=tweet.text,
                    created_at=tweet.created_at,
                    sentiment_score=sentiment_score,
                    engagement_metrics={
                        "likes": tweet.public_metrics["like_count"],
                        "retweets": tweet.public_metrics["retweet_count"],
                        "replies": tweet.public_metrics["reply_count"]
                    }
                ))

        # Calculate aggregate metrics
        total_posts = len(posts)
        avg_sentiment = sum(p.sentiment_score for p in posts) / total_posts if posts else 0.0
        total_engagement = sum(
            p.engagement_metrics.get("likes", 0) +
            p.engagement_metrics.get("retweets", 0)
            for p in posts
        )

        # Identify top posts (by engagement)
        trending = sorted(
            posts,
            key=lambda p: p.engagement_metrics.get("likes", 0) + p.engagement_metrics.get("retweets", 0),
            reverse=True
        )[:10]

        return SocialMediaAnalysis(
            company=company,
            timeframe_hours=timeframe_hours,
            platforms=[Platform.TWITTER],
            posts=posts,
            total_mentions=total_posts,
            sentiment_breakdown={
                "positive": len([p for p in posts if p.sentiment_score > 0.1]),
                "neutral": len([p for p in posts if -0.1 <= p.sentiment_score <= 0.1]),
                "negative": len([p for p in posts if p.sentiment_score < -0.1])
            },
            average_sentiment=avg_sentiment,
            trending_topics=trending,
            total_engagement=total_engagement,
            analyzed_at=datetime.utcnow()
        )
```

### API Endpoint

```python
# consultantos/api/social_endpoints.py
from fastapi import APIRouter, HTTPException
from consultantos.agents.social_media_agent import SocialMediaAgent
from consultantos.models.social_media import SocialMediaAnalysis

router = APIRouter(prefix="/social", tags=["social"])

@router.post("/analyze", response_model=SocialMediaAnalysis)
async def analyze_social_media(
    company: str,
    timeframe_hours: int = 24,
    platforms: List[str] = ["twitter"]
):
    """Analyze social media for company mentions."""
    agent = SocialMediaAgent()
    try:
        return await agent.execute(
            company=company,
            timeframe_hours=timeframe_hours,
            platforms=platforms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Test It

```bash
curl -X POST "http://localhost:8080/social/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "timeframe_hours": 24,
    "platforms": ["twitter"]
  }'
```

Expected response:
```json
{
  "company": "Tesla",
  "timeframe_hours": 24,
  "platforms": ["twitter"],
  "total_mentions": 87,
  "sentiment_breakdown": {
    "positive": 45,
    "neutral": 30,
    "negative": 12
  },
  "average_sentiment": 0.23,
  "trending_topics": [...]
}
```

## Wargaming Simulator (10 minutes)

### Minimal WarGamingAgent

```python
# consultantos/agents/wargaming_agent.py
import random
from typing import List, Dict
import numpy as np
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.wargaming import Scenario, SimulationResult, Move, Outcome

class WarGamingAgent(BaseAgent):
    """Minimal wargaming implementation with Monte Carlo simulation."""

    async def _execute_internal(
        self,
        scenario: Scenario,
        competitors: List[str],
        num_moves: int = 2,
        simulations: int = 500
    ) -> SimulationResult:
        """Simulate strategic scenarios with competitor responses."""

        outcomes = []

        # Run Monte Carlo simulations
        for sim_id in range(simulations):
            outcome = self._simulate_scenario(scenario, competitors, num_moves)
            outcomes.append(outcome)

        # Calculate statistics
        success_rate = len([o for o in outcomes if o.success]) / simulations
        avg_market_share = np.mean([o.final_market_share for o in outcomes])
        avg_revenue_impact = np.mean([o.revenue_impact for o in outcomes])

        # Best and worst case scenarios
        best_case = max(outcomes, key=lambda o: o.revenue_impact)
        worst_case = min(outcomes, key=lambda o: o.revenue_impact)

        return SimulationResult(
            scenario=scenario,
            num_simulations=simulations,
            success_rate=success_rate,
            expected_market_share=avg_market_share,
            expected_revenue_impact=avg_revenue_impact,
            best_case=best_case,
            worst_case=worst_case,
            confidence_interval=(
                np.percentile([o.revenue_impact for o in outcomes], 5),
                np.percentile([o.revenue_impact for o in outcomes], 95)
            )
        )

    def _simulate_scenario(
        self,
        scenario: Scenario,
        competitors: List[str],
        num_moves: int
    ) -> Outcome:
        """Simulate a single scenario iteration."""

        market_share = scenario.baseline_market_share
        revenue_impact = 0.0
        moves = []

        # Initial player move
        if scenario.action == "price_cut_10_percent":
            # Market share gain depends on price elasticity
            elasticity = random.uniform(1.2, 1.8)  # Price elasticity of demand
            market_share_gain = 0.10 * elasticity * random.uniform(0.8, 1.2)
            market_share += market_share_gain
            revenue_impact = -0.10  # 10% price cut

        moves.append(Move(
            actor="player",
            action=scenario.action,
            market_share_change=market_share_gain,
            revenue_change=revenue_impact
        ))

        # Competitor responses (simplified)
        for move_num in range(num_moves - 1):
            for competitor in competitors:
                # Random competitor response
                response_type = random.choices(
                    ["match_price", "quality_upgrade", "marketing_boost", "no_action"],
                    weights=[0.4, 0.2, 0.3, 0.1]
                )[0]

                if response_type == "match_price":
                    # Lose half of gained market share
                    market_share -= market_share_gain * 0.5
                    moves.append(Move(
                        actor=competitor,
                        action="price_match",
                        market_share_change=-market_share_gain * 0.5,
                        revenue_change=0.0
                    ))

                elif response_type == "quality_upgrade":
                    # Slight market share loss
                    market_share -= random.uniform(0.01, 0.03)

                elif response_type == "marketing_boost":
                    # Minimal impact
                    market_share -= random.uniform(0.005, 0.015)

        # Final revenue calculation
        # Revenue = (1 + revenue_impact) * (market_share / baseline_market_share)
        final_revenue_multiplier = (1 + revenue_impact) * (market_share / scenario.baseline_market_share)

        return Outcome(
            success=market_share > scenario.baseline_market_share,
            final_market_share=market_share,
            revenue_impact=final_revenue_multiplier - 1.0,  # % change
            moves=moves
        )
```

### API Endpoint

```python
# consultantos/api/wargaming_endpoints.py
from fastapi import APIRouter, HTTPException
from consultantos.agents.wargaming_agent import WarGamingAgent
from consultantos.models.wargaming import Scenario, SimulationResult

router = APIRouter(prefix="/wargaming", tags=["wargaming"])

@router.post("/simulate", response_model=SimulationResult)
async def simulate_scenario(scenario: Scenario, competitors: List[str]):
    """Run Monte Carlo simulation for strategic scenario."""
    agent = WarGamingAgent()
    try:
        return await agent.execute(
            scenario=scenario,
            competitors=competitors,
            num_moves=3,
            simulations=1000
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Test It

```bash
curl -X POST "http://localhost:8080/wargaming/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": {
      "name": "Price Cut Strategy",
      "action": "price_cut_10_percent",
      "baseline_market_share": 0.25
    },
    "competitors": ["Competitor A", "Competitor B"]
  }'
```

Expected response:
```json
{
  "num_simulations": 1000,
  "success_rate": 0.68,
  "expected_market_share": 0.28,
  "expected_revenue_impact": -0.03,
  "confidence_interval": [-0.12, 0.06],
  "best_case": {...},
  "worst_case": {...}
}
```

## Self-Service Analytics (5 minutes)

### Minimal MetricEngine

```python
# consultantos/analytics/metric_engine.py
import pandas as pd
from typing import Dict, Any
from sympy import sympify
from consultantos.database import get_firestore_client

class MetricEngine:
    """Parse and evaluate custom metric formulas."""

    async def evaluate_metric(
        self,
        metric_definition: str,  # e.g., "revenue / customers"
        data_source: str = "analysis_snapshots",
        filters: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """Evaluate custom metric formula against data source."""

        # Parse formula to extract variables
        expr = sympify(metric_definition)
        variables = [str(s) for s in expr.free_symbols]

        # Fetch data from Firestore
        db = get_firestore_client()
        collection = db.collection(data_source)
        query = collection

        # Apply filters
        if filters:
            for field, value in filters.items():
                query = query.where(field, "==", value)

        docs = query.stream()

        # Build DataFrame
        data = []
        for doc in docs:
            doc_data = doc.to_dict()
            row = {var: doc_data.get(var, 0) for var in variables}
            row["timestamp"] = doc_data.get("timestamp")
            data.append(row)

        df = pd.DataFrame(data)

        # Evaluate formula
        if not df.empty:
            # Replace variable names with DataFrame columns
            formula_str = metric_definition
            for var in variables:
                formula_str = formula_str.replace(var, f"df['{var}']")

            df["result"] = eval(formula_str)

        return df[["timestamp", "result"]]
```

### API Endpoint

```python
# consultantos/api/analytics_builder_endpoints.py
from fastapi import APIRouter, HTTPException
from consultantos.analytics.metric_engine import MetricEngine
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["analytics"])

class MetricRequest(BaseModel):
    formula: str
    data_source: str = "analysis_snapshots"
    filters: Dict[str, Any] = {}

@router.post("/evaluate-metric")
async def evaluate_custom_metric(request: MetricRequest):
    """Evaluate custom metric formula."""
    engine = MetricEngine()
    try:
        df = await engine.evaluate_metric(
            metric_definition=request.formula,
            data_source=request.data_source,
            filters=request.filters
        )
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Formula evaluation failed: {str(e)}")
```

### Test It

```bash
curl -X POST "http://localhost:8080/analytics/evaluate-metric" \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "revenue / customers",
    "data_source": "analysis_snapshots",
    "filters": {"company": "Tesla"}
  }'
```

Expected response:
```json
[
  {"timestamp": "2025-11-01T00:00:00Z", "result": 5234.56},
  {"timestamp": "2025-11-02T00:00:00Z", "result": 5401.23},
  ...
]
```

## Data Storytelling (5 minutes)

### Minimal StorytellingAgent

```python
# consultantos/agents/storytelling_agent.py
from typing import Dict, Literal
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.storytelling import Narrative
import instructor
from pydantic import Field

class NarrativeOutput(BaseModel):
    """Structured narrative response."""
    executive_summary: str = Field(description="2-3 sentence summary")
    key_insights: List[str] = Field(description="3-5 bullet points")
    full_narrative: str = Field(description="500-word narrative")
    recommendations: List[str] = Field(description="3 actionable recommendations")

class StorytellingAgent(BaseAgent):
    """Generate AI narratives personalized by audience role."""

    async def _execute_internal(
        self,
        analysis_data: Dict,
        target_audience: Literal["CEO", "CMO", "CFO", "Board"] = "CEO",
        tone: Literal["formal", "casual", "technical"] = "formal"
    ) -> Narrative:
        """Generate persona-adapted narrative from analysis data."""

        # Persona-specific prompts
        persona_prompts = {
            "CEO": "Focus on strategic implications, competitive positioning, and business impact. Be concise and action-oriented.",
            "CMO": "Emphasize market trends, customer insights, brand perception, and marketing opportunities.",
            "CFO": "Highlight financial metrics, ROI, cost implications, and revenue projections. Use quantitative language.",
            "Board": "Provide high-level strategic overview with governance, risk, and long-term value creation focus."
        }

        prompt = f"""
You are generating an executive narrative for a {target_audience} based on competitive intelligence analysis.

**Audience Context**: {persona_prompts[target_audience]}
**Tone**: {tone}

**Analysis Data**:
{json.dumps(analysis_data, indent=2)}

Generate a comprehensive narrative that:
1. Opens with a compelling executive summary (2-3 sentences)
2. Presents 3-5 key insights most relevant to a {target_audience}
3. Provides a 500-word full narrative in {tone} tone
4. Concludes with 3 actionable recommendations

Adapt language and focus to {target_audience} priorities.
"""

        # Use Instructor for structured output
        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            response_model=NarrativeOutput
        )

        return Narrative(
            target_audience=target_audience,
            tone=tone,
            executive_summary=response.executive_summary,
            key_insights=response.key_insights,
            full_text=response.full_narrative,
            recommendations=response.recommendations,
            generated_at=datetime.utcnow()
        )
```

### API Endpoint

```python
# consultantos/api/storytelling_endpoints.py
from fastapi import APIRouter, HTTPException
from consultantos.agents.storytelling_agent import StorytellingAgent
from consultantos.models.storytelling import Narrative

router = APIRouter(prefix="/storytelling", tags=["storytelling"])

@router.post("/generate", response_model=Narrative)
async def generate_narrative(
    analysis_data: Dict,
    target_audience: str = "CEO",
    tone: str = "formal"
):
    """Generate AI narrative from analysis data."""
    agent = StorytellingAgent()
    try:
        return await agent.execute(
            analysis_data=analysis_data,
            target_audience=target_audience,
            tone=tone
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Test It

```bash
curl -X POST "http://localhost:8080/storytelling/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_data": {
      "company": "Tesla",
      "market_share": 0.28,
      "sentiment": 0.65,
      "growth_rate": 0.15
    },
    "target_audience": "CEO",
    "tone": "formal"
  }'
```

Expected response:
```json
{
  "target_audience": "CEO",
  "tone": "formal",
  "executive_summary": "Tesla's competitive position strengthened in Q4 with 28% market share (+3pp YoY), positive social sentiment, and sustained 15% growth trajectory.",
  "key_insights": [
    "Market share gains driven by price optimization and product portfolio expansion",
    "Social sentiment (0.65) indicates strong brand perception despite competitive pressure",
    "Growth trajectory sustainable but requires continued innovation investment"
  ],
  "full_text": "...",
  "recommendations": [
    "Maintain aggressive pricing strategy while competitors respond",
    "Invest in brand building to sustain positive social sentiment",
    "Accelerate R&D for next-generation products to defend market position"
  ]
}
```

## Integration with Phase 1 (5 minutes)

### Conversational AI + Social Media

```python
# consultantos/agents/conversational_agent.py (updated)

class ConversationalAgent(BaseAgent):
    async def _route_query(self, query: str) -> Dict:
        """Route user query to appropriate agent."""

        # Detect social media intent
        social_keywords = ["sentiment", "social", "twitter", "mentions", "what are people saying"]
        if any(keyword in query.lower() for keyword in social_keywords):
            # Extract company from query
            company = self._extract_entity(query, entity_type="company")

            # Call SocialMediaAgent
            social_agent = SocialMediaAgent()
            social_data = await social_agent.execute(
                company=company,
                timeframe_hours=24
            )

            # Format response for chat
            return {
                "response": f"Recent social analysis for {company}: {social_data.total_mentions} mentions with {social_data.average_sentiment:.2f} avg sentiment.",
                "data": social_data,
                "agent": "social_media"
            }

        # ... other routing logic
```

### Forecasting + Wargaming

```python
# consultantos/agents/wargaming_agent.py (updated)

async def _execute_internal(
    self,
    scenario: Scenario,
    use_forecast: bool = True
) -> SimulationResult:
    """Simulate scenario with optional forecast integration."""

    if use_forecast:
        # Get baseline forecast from ForecastingAgent
        forecast_agent = ForecastingAgent()
        forecast = await forecast_agent.forecast_metric(
            metric_name="market_share",
            horizon_months=6
        )

        # Use forecast as baseline for simulation
        scenario.baseline_market_share = forecast.predictions[-1]
        scenario.baseline_forecast = forecast.predictions

    # ... rest of simulation logic
```

## Verify Installation

```bash
# Run all Phase 2 tests
pytest tests/test_social_media_agent.py -v
pytest tests/test_wargaming_agent.py -v
pytest tests/test_metric_engine.py -v
pytest tests/test_storytelling_agent.py -v

# Check API documentation
open http://localhost:8080/docs#/social
open http://localhost:8080/docs#/wargaming
open http://localhost:8080/docs#/analytics
open http://localhost:8080/docs#/storytelling
```

## Next Steps

1. **Expand Social Connectors**: Add LinkedIn and Reddit support
2. **Advanced Wargaming**: Multi-player game theory, Nash equilibria
3. **Analytics UI**: Build drag-and-drop dashboard builder frontend
4. **Storytelling Formats**: Add PowerPoint and video script generation

## Troubleshooting

**Twitter API 403 Error**:
- Verify `TWITTER_BEARER_TOKEN` is set correctly
- Check API access tier (need v2 access)
- Use `TWITTER_API_KEY` + `TWITTER_API_SECRET` for OAuth 1.0a

**Simulation Timeout**:
- Reduce `simulations` from 1000 → 500
- Enable Cloud Tasks for async processing
- Cache game trees for common scenarios

**Formula Parser Error**:
- Check formula syntax (use Python operators: `+`, `-`, `*`, `/`)
- Ensure variable names match data source fields exactly
- Test with simple formulas first: `revenue`, `customers`, `revenue / customers`

**Narrative Quality Issues**:
- Add few-shot examples to prompt
- Increase response length limit
- Use GPT-4 instead of Gemini for complex narratives

## Related Documentation

- **Full Architecture**: `PHASE2_ARCHITECTURE.md`
- **Implementation Plan**: `PHASE2_IMPLEMENTATION_SUMMARY.md`
- **Visual Diagrams**: `PHASE2_ARCHITECTURE_DIAGRAMS.md`
- **Complete Index**: `PHASE2_INDEX.md`

---

**Quickstart Version**: 1.0
**Last Updated**: November 9, 2025
**Estimated Time**: 30 minutes
