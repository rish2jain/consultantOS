# Phase 2 Skills Architecture - Detailed Design

**Version**: 1.0
**Date**: November 9, 2025
**Status**: Design Complete
**Dependencies**: Phase 1 (Conversational AI, Predictive Analytics, Dark Data Mining)

---

## Executive Summary

Phase 2 adds **4 differentiation skills** to ConsultantOS, building on Phase 1's foundation:

1. **Social Media Intelligence** - Real-time brand/competitor monitoring across Twitter, LinkedIn, Reddit
2. **Wargaming & Scenario Simulator** - "What-if" strategy testing with competitor response modeling
3. **Self-Service Analytics Builder** - No-code dashboard/report builder for democratizing insights
4. **Data Storytelling Engine** - Auto-generate narrative summaries with contextual explanations

**Combined Impact**:
- Phase 1 = AI-first experience (conversational, predictive, dark data)
- Phase 2 = Market differentiation (social listening, wargaming, self-service, narratives)
- Total = 7 new agents, 50+ new endpoints, unique competitive positioning

---

## Table of Contents

1. [Skill 1: Social Media Intelligence](#skill-1-social-media-intelligence)
2. [Skill 2: Wargaming & Scenario Simulator](#skill-2-wargaming--scenario-simulator)
3. [Skill 3: Self-Service Analytics Builder](#skill-3-self-service-analytics-builder)
4. [Skill 4: Data Storytelling Engine](#skill-4-data-storytelling-engine)
5. [Cross-Skill Integration](#cross-skill-integration)
6. [Database Schema](#database-schema)
7. [API Specifications](#api-specifications)
8. [Performance & Scaling](#performance--scaling)
9. [Security & Compliance](#security--compliance)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Plan](#deployment-plan)
12. [Migration from Phase 1](#migration-from-phase-1)

---

## Skill 1: Social Media Intelligence

### 1.1 Overview

**Purpose**: Real-time competitive intelligence from social media platforms

**Key Features**:
- Multi-platform monitoring (Twitter, LinkedIn, Reddit, Facebook, Instagram)
- Real-time mention tracking with webhooks
- Sentiment analysis and trend detection
- Influencer identification
- Crisis/reputation monitoring
- Integration with existing monitoring system

**Business Value**:
- Detect competitive threats 24-48 hours earlier
- Track brand sentiment in real-time
- Identify emerging trends before mainstream media
- Crisis detection and response

### 1.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│           SocialMediaAgent (New)                     │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Platform   │  │   Stream     │  │ Sentiment │ │
│  │  Connectors  │→ │  Processor   │→ │ Analyzer  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│         ↓                  ↓                 ↓       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Mention    │  │  Influencer  │  │   Alert   │ │
│  │   Tracker    │  │  Detector    │  │  Trigger  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────┘
         ↓                  ↓                 ↓
┌─────────────────────────────────────────────────────┐
│         Integration Layer                            │
│  ┌───────────────┐  ┌───────────────┐               │
│  │ NLPProcessor  │  │ EntityTracker │               │
│  │ (Reuse)       │  │ (Reuse)       │               │
│  └───────────────┘  └───────────────┘               │
│  ┌───────────────┐  ┌───────────────┐               │
│  │ Monitoring    │  │ Alert System  │               │
│  │ (Integrate)   │  │ (Integrate)   │               │
│  └───────────────┘  └───────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 1.3 Components

#### 1.3.1 Platform Connectors

**Twitter/X Connector**:
```python
# consultantos/tools/twitter_connector.py

from typing import List, Optional, AsyncIterator
import tweepy
from datetime import datetime
from consultantos.models.social_media import Tweet, TwitterMetrics

class TwitterConnector:
    """Twitter API v2 integration with streaming support"""

    def __init__(self,
                 bearer_token: str,
                 api_key: str,
                 api_secret: str,
                 access_token: str,
                 access_secret: str):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=True
        )

    async def search_mentions(
        self,
        query: str,
        max_results: int = 100,
        since: Optional[datetime] = None
    ) -> List[Tweet]:
        """Search for mentions with rate limit handling"""
        # Rate limit: 450 requests/15min window
        tweets = self.client.search_recent_tweets(
            query=query,
            max_results=max_results,
            start_time=since,
            tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
            expansions=['author_id'],
            user_fields=['username', 'verified', 'public_metrics']
        )

        return [self._parse_tweet(t) for t in tweets.data or []]

    async def stream_mentions(
        self,
        keywords: List[str]
    ) -> AsyncIterator[Tweet]:
        """Real-time streaming of mentions"""
        # Setup filtered stream with keywords
        stream = tweepy.StreamingClient(bearer_token=self.bearer_token)

        # Add rules for keywords
        for keyword in keywords:
            stream.add_rules(tweepy.StreamRule(keyword))

        # Stream tweets
        for tweet in stream.filter():
            yield self._parse_tweet(tweet)

    def _parse_tweet(self, raw_tweet) -> Tweet:
        """Parse Twitter API response to our model"""
        return Tweet(
            id=raw_tweet.id,
            text=raw_tweet.text,
            author_id=raw_tweet.author_id,
            created_at=raw_tweet.created_at,
            metrics=TwitterMetrics(
                likes=raw_tweet.public_metrics['like_count'],
                retweets=raw_tweet.public_metrics['retweet_count'],
                replies=raw_tweet.public_metrics['reply_count'],
                impressions=raw_tweet.public_metrics.get('impression_count', 0)
            )
        )
```

**LinkedIn Connector**:
```python
# consultantos/tools/linkedin_connector.py

from linkedin_api import Linkedin
from typing import List, Optional
from consultantos.models.social_media import LinkedInPost

class LinkedInConnector:
    """LinkedIn API integration for company monitoring"""

    def __init__(self, username: str, password: str):
        # Note: Use official API with OAuth2 for production
        self.api = Linkedin(username, password)

    async def get_company_posts(
        self,
        company_id: str,
        limit: int = 50
    ) -> List[LinkedInPost]:
        """Fetch recent posts from company page"""
        # Rate limit: 100 requests/day
        posts = self.api.get_company_updates(
            public_id=company_id,
            max_results=limit
        )

        return [self._parse_post(p) for p in posts]

    async def search_posts(
        self,
        keywords: List[str],
        limit: int = 50
    ) -> List[LinkedInPost]:
        """Search posts by keywords"""
        query = " OR ".join(keywords)
        results = self.api.search_posts(
            keywords=query,
            limit=limit
        )

        return [self._parse_post(p) for p in results]
```

**Reddit Connector**:
```python
# consultantos/tools/reddit_connector.py

import praw
from typing import List, Optional
from consultantos.models.social_media import RedditPost

class RedditConnector:
    """Reddit API (PRAW) integration for subreddit monitoring"""

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    async def monitor_subreddits(
        self,
        subreddits: List[str],
        keywords: List[str],
        limit: int = 100
    ) -> List[RedditPost]:
        """Monitor multiple subreddits for keyword mentions"""
        posts = []

        for subreddit_name in subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Search recent posts
            for submission in subreddit.search(
                query=" OR ".join(keywords),
                sort='new',
                time_filter='week',
                limit=limit
            ):
                posts.append(self._parse_submission(submission))

        return posts

    async def stream_mentions(
        self,
        subreddits: List[str],
        keywords: List[str]
    ):
        """Real-time stream of mentions"""
        subreddit = self.reddit.subreddit('+'.join(subreddits))

        for submission in subreddit.stream.submissions():
            if any(kw.lower() in submission.title.lower() or
                   kw.lower() in submission.selftext.lower()
                   for kw in keywords):
                yield self._parse_submission(submission)
```

#### 1.3.2 SocialMediaAgent

```python
# consultantos/agents/social_media_agent.py

from consultantos.agents.base_agent import BaseAgent
from consultantos.tools.twitter_connector import TwitterConnector
from consultantos.tools.linkedin_connector import LinkedInConnector
from consultantos.tools.reddit_connector import RedditConnector
from consultantos.tools.nlp_tool import get_nlp_processor
from consultantos.models.social_media import (
    SocialMediaAnalysis,
    MentionSummary,
    SentimentTrend,
    InfluencerProfile
)

class SocialMediaAgent(BaseAgent):
    """
    Agent for social media intelligence gathering

    Monitors multiple platforms for brand/competitor mentions,
    analyzes sentiment, identifies influencers, and triggers alerts
    """

    def __init__(self, config: dict):
        super().__init__("SocialMediaAgent", timeout=120)

        # Initialize connectors
        self.twitter = TwitterConnector(
            bearer_token=config['twitter_bearer_token'],
            api_key=config['twitter_api_key'],
            api_secret=config['twitter_api_secret'],
            access_token=config['twitter_access_token'],
            access_secret=config['twitter_access_secret']
        )

        self.linkedin = LinkedInConnector(
            username=config['linkedin_username'],
            password=config['linkedin_password']
        )

        self.reddit = RedditConnector(
            client_id=config['reddit_client_id'],
            client_secret=config['reddit_client_secret'],
            user_agent=config['reddit_user_agent']
        )

        # NLP for sentiment analysis
        self.nlp = get_nlp_processor()

    async def _execute_internal(
        self,
        company: str,
        competitors: List[str],
        timeframe_hours: int = 24,
        platforms: List[str] = ['twitter', 'linkedin', 'reddit']
    ) -> SocialMediaAnalysis:
        """
        Gather social media intelligence

        Args:
            company: Target company name
            competitors: List of competitor names
            timeframe_hours: How far back to search (default 24h)
            platforms: Which platforms to monitor

        Returns:
            SocialMediaAnalysis with mentions, sentiment, trends
        """
        since = datetime.utcnow() - timedelta(hours=timeframe_hours)
        all_companies = [company] + competitors

        # Gather mentions from all platforms (parallel)
        twitter_task = self._gather_twitter_mentions(all_companies, since) if 'twitter' in platforms else None
        linkedin_task = self._gather_linkedin_mentions(all_companies, since) if 'linkedin' in platforms else None
        reddit_task = self._gather_reddit_mentions(all_companies, since) if 'reddit' in platforms else None

        twitter_mentions, linkedin_mentions, reddit_mentions = await asyncio.gather(
            twitter_task or asyncio.sleep(0),
            linkedin_task or asyncio.sleep(0),
            reddit_task or asyncio.sleep(0)
        )

        # Combine all mentions
        all_mentions = [
            *(twitter_mentions or []),
            *(linkedin_mentions or []),
            *(reddit_mentions or [])
        ]

        # Analyze sentiment for each mention
        for mention in all_mentions:
            sentiment = self.nlp.sentiment_analysis(mention.text)
            mention.sentiment = sentiment

        # Aggregate by company
        mention_summary = self._aggregate_mentions(all_mentions, all_companies)

        # Detect sentiment trends
        sentiment_trends = self._detect_sentiment_trends(all_mentions, all_companies)

        # Identify influencers
        influencers = self._identify_influencers(all_mentions)

        # Detect crises (sudden negative sentiment spikes)
        crisis_alerts = self._detect_crises(sentiment_trends, company)

        return SocialMediaAnalysis(
            company=company,
            competitors=competitors,
            timeframe_hours=timeframe_hours,
            platforms=platforms,
            mention_summary=mention_summary,
            sentiment_trends=sentiment_trends,
            influencers=influencers,
            crisis_alerts=crisis_alerts,
            total_mentions=len(all_mentions),
            analyzed_at=datetime.utcnow()
        )

    async def _gather_twitter_mentions(
        self,
        companies: List[str],
        since: datetime
    ) -> List[Tweet]:
        """Gather Twitter mentions for all companies"""
        mentions = []

        for company in companies:
            query = f'"{company}" OR #{company.replace(" ", "")}'
            company_mentions = await self.twitter.search_mentions(
                query=query,
                max_results=100,
                since=since
            )
            mentions.extend(company_mentions)

        return mentions

    def _aggregate_mentions(
        self,
        mentions: List,
        companies: List[str]
    ) -> Dict[str, MentionSummary]:
        """Aggregate mentions by company"""
        summary = {}

        for company in companies:
            company_mentions = [
                m for m in mentions
                if company.lower() in m.text.lower()
            ]

            if not company_mentions:
                continue

            # Calculate sentiment distribution
            sentiments = [m.sentiment.classification for m in company_mentions]
            sentiment_dist = {
                'positive': sentiments.count('positive') / len(sentiments),
                'neutral': sentiments.count('neutral') / len(sentiments),
                'negative': sentiments.count('negative') / len(sentiments)
            }

            # Calculate average sentiment score
            avg_sentiment = sum(m.sentiment.polarity for m in company_mentions) / len(company_mentions)

            summary[company] = MentionSummary(
                company=company,
                total_mentions=len(company_mentions),
                sentiment_distribution=sentiment_dist,
                average_sentiment=avg_sentiment,
                top_posts=[
                    m for m in sorted(
                        company_mentions,
                        key=lambda x: x.engagement_score(),
                        reverse=True
                    )[:5]
                ]
            )

        return summary

    def _detect_sentiment_trends(
        self,
        mentions: List,
        companies: List[str]
    ) -> Dict[str, SentimentTrend]:
        """Detect sentiment changes over time"""
        trends = {}

        for company in companies:
            company_mentions = [
                m for m in mentions
                if company.lower() in m.text.lower()
            ]

            if len(company_mentions) < 10:
                continue

            # Sort by time
            company_mentions.sort(key=lambda m: m.created_at)

            # Split into two halves (before/after)
            midpoint = len(company_mentions) // 2
            early_mentions = company_mentions[:midpoint]
            recent_mentions = company_mentions[midpoint:]

            # Calculate average sentiment for each half
            early_sentiment = sum(m.sentiment.polarity for m in early_mentions) / len(early_mentions)
            recent_sentiment = sum(m.sentiment.polarity for m in recent_mentions) / len(recent_mentions)

            # Detect shift
            sentiment_change = recent_sentiment - early_sentiment

            trends[company] = SentimentTrend(
                company=company,
                early_sentiment=early_sentiment,
                recent_sentiment=recent_sentiment,
                sentiment_change=sentiment_change,
                trend_direction='improving' if sentiment_change > 0.1 else 'declining' if sentiment_change < -0.1 else 'stable'
            )

        return trends

    def _identify_influencers(
        self,
        mentions: List
    ) -> List[InfluencerProfile]:
        """Identify influential accounts"""
        # Group by author
        author_mentions = {}
        for mention in mentions:
            if mention.author_id not in author_mentions:
                author_mentions[mention.author_id] = []
            author_mentions[mention.author_id].append(mention)

        influencers = []
        for author_id, author_posts in author_mentions.items():
            # Calculate influence score
            total_engagement = sum(m.engagement_score() for m in author_posts)
            avg_engagement = total_engagement / len(author_posts)

            # Only include if significant engagement
            if avg_engagement > 100:
                influencers.append(InfluencerProfile(
                    author_id=author_id,
                    username=author_posts[0].author_username,
                    total_posts=len(author_posts),
                    total_engagement=total_engagement,
                    avg_engagement=avg_engagement,
                    verified=author_posts[0].author_verified,
                    follower_count=author_posts[0].author_followers
                ))

        # Sort by influence
        influencers.sort(key=lambda i: i.avg_engagement, reverse=True)

        return influencers[:20]  # Top 20

    def _detect_crises(
        self,
        sentiment_trends: Dict[str, SentimentTrend],
        company: str
    ) -> List[str]:
        """Detect potential PR crises"""
        alerts = []

        if company in sentiment_trends:
            trend = sentiment_trends[company]

            # Crisis if sentiment dropped significantly
            if trend.sentiment_change < -0.3:
                alerts.append(
                    f"⚠️ CRISIS ALERT: {company} sentiment dropped {abs(trend.sentiment_change):.1%} "
                    f"(from {trend.early_sentiment:.2f} to {trend.recent_sentiment:.2f})"
                )

            # Warning if sentiment declining
            elif trend.sentiment_change < -0.15:
                alerts.append(
                    f"⚠️ WARNING: {company} sentiment declining "
                    f"({trend.sentiment_change:.1%} change)"
                )

        return alerts
```

### 1.4 Data Models

```python
# consultantos/models/social_media.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime

class TwitterMetrics(BaseModel):
    """Twitter engagement metrics"""
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    impressions: int = 0

class Tweet(BaseModel):
    """Twitter post"""
    id: str
    text: str
    author_id: str
    author_username: str = ""
    author_verified: bool = False
    author_followers: int = 0
    created_at: datetime
    metrics: TwitterMetrics
    sentiment: Optional['SentimentScore'] = None
    platform: str = "twitter"

    def engagement_score(self) -> int:
        """Calculate total engagement"""
        return (
            self.metrics.likes +
            self.metrics.retweets * 3 +  # Retweets worth more
            self.metrics.replies * 2
        )

class LinkedInPost(BaseModel):
    """LinkedIn post"""
    id: str
    text: str
    author_id: str
    author_name: str = ""
    company_id: Optional[str] = None
    created_at: datetime
    reactions: int = 0
    comments: int = 0
    shares: int = 0
    sentiment: Optional['SentimentScore'] = None
    platform: str = "linkedin"

    def engagement_score(self) -> int:
        return self.reactions + self.comments * 2 + self.shares * 3

class RedditPost(BaseModel):
    """Reddit submission"""
    id: str
    title: str
    text: str
    author: str
    subreddit: str
    created_at: datetime
    score: int  # Upvotes - downvotes
    num_comments: int
    url: str
    sentiment: Optional['SentimentScore'] = None
    platform: str = "reddit"

    def engagement_score(self) -> int:
        return self.score + self.num_comments * 2

class MentionSummary(BaseModel):
    """Aggregated mention statistics"""
    company: str
    total_mentions: int
    sentiment_distribution: Dict[str, float]  # positive, neutral, negative percentages
    average_sentiment: float  # -1.0 to 1.0
    top_posts: List[Union[Tweet, LinkedInPost, RedditPost]]

class SentimentTrend(BaseModel):
    """Sentiment trend over time"""
    company: str
    early_sentiment: float  # First half of timeframe
    recent_sentiment: float  # Second half of timeframe
    sentiment_change: float  # Change delta
    trend_direction: Literal['improving', 'declining', 'stable']

class InfluencerProfile(BaseModel):
    """Influential account profile"""
    author_id: str
    username: str
    total_posts: int
    total_engagement: int
    avg_engagement: float
    verified: bool
    follower_count: int

class SocialMediaAnalysis(BaseModel):
    """Complete social media intelligence analysis"""
    company: str
    competitors: List[str]
    timeframe_hours: int
    platforms: List[str]
    mention_summary: Dict[str, MentionSummary]
    sentiment_trends: Dict[str, SentimentTrend]
    influencers: List[InfluencerProfile]
    crisis_alerts: List[str]
    total_mentions: int
    analyzed_at: datetime
```

### 1.5 API Endpoints

```python
# consultantos/api/social_media_endpoints.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from consultantos.agents.social_media_agent import SocialMediaAgent
from consultantos.models.social_media import SocialMediaAnalysis
from consultantos.auth import get_current_user

router = APIRouter(prefix="/social-media", tags=["social-media"])

@router.post("/analyze", response_model=SocialMediaAnalysis)
async def analyze_social_media(
    company: str,
    competitors: List[str] = [],
    timeframe_hours: int = 24,
    platforms: List[str] = ['twitter', 'linkedin', 'reddit'],
    user = Depends(get_current_user)
):
    """
    Analyze social media mentions and sentiment

    Rate limit: 10 requests/hour
    """
    agent = SocialMediaAgent(config={
        'twitter_bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
        # ... other credentials
    })

    try:
        analysis = await agent.execute(
            company=company,
            competitors=competitors,
            timeframe_hours=timeframe_hours,
            platforms=platforms
        )

        return analysis

    except Exception as e:
        logger.error(f"Social media analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitors", response_model=Dict[str, str])
async def create_social_monitor(
    company: str,
    keywords: List[str],
    platforms: List[str],
    alert_threshold: float = 0.7,
    user = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    """
    Create continuous social media monitor

    Will check every hour and alert on significant changes
    """
    monitor_id = str(uuid.uuid4())

    # Store monitor config
    await db.collection('social_monitors').document(monitor_id).set({
        'user_id': user.id,
        'company': company,
        'keywords': keywords,
        'platforms': platforms,
        'alert_threshold': alert_threshold,
        'created_at': datetime.utcnow(),
        'status': 'active'
    })

    # Start background monitoring
    background_tasks.add_task(
        schedule_social_monitoring,
        monitor_id=monitor_id
    )

    return {'monitor_id': monitor_id, 'status': 'active'}

@router.get("/monitors/{monitor_id}/alerts")
async def get_social_alerts(
    monitor_id: str,
    limit: int = 50,
    user = Depends(get_current_user)
):
    """Get recent alerts for a social media monitor"""
    alerts = await db.collection('social_alerts')\
        .where('monitor_id', '==', monitor_id)\
        .order_by('created_at', direction='DESCENDING')\
        .limit(limit)\
        .get()

    return [doc.to_dict() for doc in alerts]
```

### 1.6 Database Schema

**Firestore Collections**:

**`social_monitors`**:
```json
{
  "monitor_id": "uuid",
  "user_id": "user_uuid",
  "company": "Tesla",
  "keywords": ["Tesla", "#Tesla", "Elon Musk"],
  "platforms": ["twitter", "linkedin", "reddit"],
  "alert_threshold": 0.7,
  "check_frequency": "hourly",
  "status": "active",
  "created_at": "2025-11-09T12:00:00Z",
  "last_checked_at": "2025-11-09T13:00:00Z"
}
```

**`social_mentions`** (cached for 30 days):
```json
{
  "mention_id": "uuid",
  "monitor_id": "monitor_uuid",
  "platform": "twitter",
  "post_id": "twitter_post_id",
  "author_id": "twitter_user_id",
  "text": "Tesla's new battery tech is amazing!",
  "sentiment": {
    "polarity": 0.8,
    "subjectivity": 0.6,
    "classification": "positive"
  },
  "engagement": {
    "likes": 150,
    "shares": 30,
    "comments": 20
  },
  "created_at": "2025-11-09T10:30:00Z",
  "indexed_at": "2025-11-09T11:00:00Z"
}
```

**`social_alerts`**:
```json
{
  "alert_id": "uuid",
  "monitor_id": "monitor_uuid",
  "alert_type": "sentiment_decline",
  "severity": "high",
  "message": "Tesla sentiment dropped 30% in last 6 hours",
  "details": {
    "previous_sentiment": 0.6,
    "current_sentiment": 0.3,
    "mention_count": 250,
    "platforms": ["twitter", "reddit"]
  },
  "created_at": "2025-11-09T12:00:00Z",
  "acknowledged": false
}
```

### 1.7 Performance Targets

- **Real-time streaming latency**: <5 seconds from post to detection
- **Batch analysis**: 1,000 mentions processed in <30 seconds
- **Sentiment analysis throughput**: 500 posts/second
- **API response time**: <10 seconds (p95) for 24-hour analysis
- **Monitor check frequency**: Every hour (configurable)
- **Alert delivery latency**: <2 minutes from detection to notification

### 1.8 Integration Points

**With Existing Systems**:
- **NLPProcessor**: Reuse for sentiment analysis and entity extraction
- **EntityTracker**: Track social entities (people, companies, products)
- **IntelligenceMonitor**: Integrate social insights into monitoring snapshots
- **AlertScorer**: Use existing alert prioritization and throttling
- **Notification System**: Reuse multi-channel alerting (email, Slack, webhook)

**With Phase 1 Skills**:
- **Conversational AI**: "Show me negative Tesla mentions from Reddit today"
- **Predictive Analytics**: Correlate social sentiment with stock price forecasts
- **Dark Data Mining**: Cross-reference social mentions with internal communications

---

## Skill 2: Wargaming & Scenario Simulator

### 2.1 Overview

**Purpose**: "What-if" strategy testing and competitor response modeling

**Key Features**:
- Scenario definition (pricing, product launch, market entry)
- Competitor response modeling (ML + rule-based)
- Multi-move strategic chess (3-5 moves ahead)
- Monte Carlo simulation for uncertainty
- Decision tree & game tree visualization
- Integration with forecasting models

**Business Value**:
- Test strategies before execution (risk-free)
- Anticipate competitor reactions
- Identify optimal strategic paths
- Quantify strategic risks and opportunities

### 2.2 Architecture

```
┌────────────────────────────────────────────────────┐
│        WarGamingAgent (New)                        │
│                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│
│  │  Scenario    │  │  Competitor  │  │  Monte   ││
│  │  Builder     │→ │  Response    │→ │  Carlo   ││
│  │              │  │  Model       │  │  Sim     ││
│  └──────────────┘  └──────────────┘  └──────────┘│
│         ↓                  ↓                 ↓    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│
│  │   Game Tree  │  │  Outcome     │  │Decision  ││
│  │   Generator  │  │  Evaluator   │  │ Viz      ││
│  └──────────────┘  └──────────────┘  └──────────┘│
└────────────────────────────────────────────────────┘
         ↓                  ↓                 ↓
┌────────────────────────────────────────────────────┐
│         Integration Layer                          │
│  ┌───────────────┐  ┌───────────────┐             │
│  │ Forecasting   │  │ Historical    │             │
│  │ Agent (P1)    │  │ Analysis      │             │
│  └───────────────┘  └───────────────┘             │
│  ┌───────────────┐  ┌───────────────┐             │
│  │ Gemini LLM    │  │ Visualization │             │
│  │ (Response)    │  │ (Charts)      │             │
│  └───────────────┘  └───────────────┘             │
└────────────────────────────────────────────────────┘
```

### 2.3 Components

#### 2.3.1 WarGamingAgent

```python
# consultantos/agents/wargaming_agent.py

from consultantos.agents.base_agent import BaseAgent
from consultantos.agents.forecasting_agent import ForecastingAgent
from consultantos.models.wargaming import (
    Scenario,
    CompetitorResponse,
    GameTree,
    SimulationResult
)
import numpy as np
from typing import List, Dict, Tuple

class WarGamingAgent(BaseAgent):
    """
    Agent for strategic wargaming and scenario simulation

    Models "what-if" scenarios and predicts competitor responses
    to test strategies before execution
    """

    def __init__(self):
        super().__init__("WarGamingAgent", timeout=180)
        self.forecasting_agent = ForecastingAgent()

    async def _execute_internal(
        self,
        scenario: Scenario,
        competitors: List[str],
        num_moves: int = 3,
        simulations: int = 1000
    ) -> SimulationResult:
        """
        Run wargaming simulation

        Args:
            scenario: Initial strategic move to test
            competitors: List of competitor names
            num_moves: How many moves ahead to simulate (3-5)
            simulations: Monte Carlo iterations

        Returns:
            SimulationResult with outcomes, probabilities, recommendations
        """
        # Build game tree
        game_tree = await self._build_game_tree(
            scenario=scenario,
            competitors=competitors,
            depth=num_moves
        )

        # Run Monte Carlo simulations
        simulation_outcomes = await self._run_monte_carlo(
            game_tree=game_tree,
            num_simulations=simulations
        )

        # Evaluate outcomes
        outcome_analysis = self._evaluate_outcomes(simulation_outcomes)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            scenario=scenario,
            game_tree=game_tree,
            outcome_analysis=outcome_analysis
        )

        return SimulationResult(
            scenario=scenario,
            game_tree=game_tree,
            num_simulations=simulations,
            outcome_distribution=outcome_analysis['distribution'],
            expected_value=outcome_analysis['expected_value'],
            best_case=outcome_analysis['best_case'],
            worst_case=outcome_analysis['worst_case'],
            recommendations=recommendations,
            simulated_at=datetime.utcnow()
        )

    async def _build_game_tree(
        self,
        scenario: Scenario,
        competitors: List[str],
        depth: int
    ) -> GameTree:
        """
        Build game tree with possible moves/responses

        Uses combination of:
        1. Historical data (past competitive responses)
        2. ML model (trained on competitive behavior)
        3. LLM reasoning (Gemini for strategic thinking)
        """
        root = GameNode(
            move_type='our_move',
            action=scenario.action,
            player='us',
            depth=0
        )

        # Recursively build tree
        await self._expand_node(
            node=root,
            competitors=competitors,
            max_depth=depth
        )

        return GameTree(root=root, max_depth=depth)

    async def _expand_node(
        self,
        node: GameNode,
        competitors: List[str],
        max_depth: int
    ):
        """Recursively expand game tree node"""
        if node.depth >= max_depth:
            return

        # If our move, generate competitor responses
        if node.player == 'us':
            for competitor in competitors:
                # Predict competitor response
                responses = await self._predict_competitor_response(
                    our_action=node.action,
                    competitor=competitor,
                    context=node.get_history()
                )

                for response in responses:
                    child = GameNode(
                        move_type='competitor_response',
                        action=response.action,
                        player=competitor,
                        depth=node.depth + 1,
                        probability=response.probability
                    )
                    node.add_child(child)

                    # Recursively expand
                    await self._expand_node(
                        node=child,
                        competitors=competitors,
                        max_depth=max_depth
                    )

        # If competitor move, generate our counter-moves
        else:
            counter_moves = await self._generate_counter_moves(
                competitor_action=node.action,
                context=node.get_history()
            )

            for counter in counter_moves:
                child = GameNode(
                    move_type='our_counter',
                    action=counter.action,
                    player='us',
                    depth=node.depth + 1,
                    probability=counter.probability
                )
                node.add_child(child)

                await self._expand_node(
                    node=child,
                    competitors=competitors,
                    max_depth=max_depth
                )

    async def _predict_competitor_response(
        self,
        our_action: StrategicAction,
        competitor: str,
        context: List[GameNode]
    ) -> List[CompetitorResponse]:
        """
        Predict how competitor will respond to our move

        Uses 3 methods:
        1. Historical patterns (if we have data)
        2. ML model (trained on competitive behavior)
        3. LLM reasoning (Gemini for strategic thinking)
        """
        responses = []

        # Method 1: Historical patterns
        historical = await self._lookup_historical_responses(
            competitor=competitor,
            action_type=our_action.type
        )

        if historical:
            responses.extend(historical)

        # Method 2: ML model (if trained)
        if self.has_ml_model:
            ml_predictions = await self._ml_predict_response(
                competitor=competitor,
                our_action=our_action,
                context=context
            )
            responses.extend(ml_predictions)

        # Method 3: LLM reasoning (always available)
        llm_predictions = await self._llm_predict_response(
            competitor=competitor,
            our_action=our_action,
            context=context
        )
        responses.extend(llm_predictions)

        # Combine and deduplicate
        return self._combine_predictions(responses)

    async def _llm_predict_response(
        self,
        competitor: str,
        our_action: StrategicAction,
        context: List[GameNode]
    ) -> List[CompetitorResponse]:
        """Use Gemini to reason about competitor response"""
        prompt = f"""
        You are a competitive intelligence expert. Predict how {competitor} would respond to our strategic move.

        Our Move:
        Type: {our_action.type}
        Details: {our_action.description}

        Context:
        {self._format_context(context)}

        Based on {competitor}'s historical behavior, market position, and strategic priorities, what are the 3 most likely responses?
        For each response, provide:
        1. Action type (price_cut, product_launch, market_entry, partnership, etc.)
        2. Description
        3. Probability (0-1)
        4. Expected timeline (days/weeks/months)
        5. Strategic rationale
        """

        # Use structured output
        response = await self.instructor_client.chat.completions.create(
            model="gemini-1.5-flash",
            response_model=CompetitorResponsePrediction,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.responses

    async def _run_monte_carlo(
        self,
        game_tree: GameTree,
        num_simulations: int
    ) -> List[SimulationOutcome]:
        """
        Run Monte Carlo simulations through game tree

        Randomly samples paths through tree based on probabilities,
        evaluates outcomes for each path
        """
        outcomes = []

        for _ in range(num_simulations):
            # Sample random path through tree
            path = self._sample_path(game_tree.root)

            # Evaluate outcome at leaf node
            outcome = await self._evaluate_path(path)
            outcomes.append(outcome)

        return outcomes

    def _sample_path(self, node: GameNode) -> List[GameNode]:
        """Sample random path through game tree"""
        path = [node]
        current = node

        while current.children:
            # Sample child based on probabilities
            probs = [c.probability for c in current.children]
            child = np.random.choice(current.children, p=probs)
            path.append(child)
            current = child

        return path

    async def _evaluate_path(self, path: List[GameNode]) -> SimulationOutcome:
        """
        Evaluate outcome of a game tree path

        Estimates:
        - Market share impact
        - Revenue impact
        - Profit impact
        - Brand perception change
        - Strategic position change
        """
        # Extract sequence of actions
        actions = [node.action for node in path]

        # Use forecasting agent to predict outcomes
        forecast = await self.forecasting_agent.forecast_scenario(
            actions=actions,
            horizon_months=12
        )

        return SimulationOutcome(
            path=path,
            market_share_change=forecast.market_share_change,
            revenue_change=forecast.revenue_change,
            profit_change=forecast.profit_change,
            brand_perception_change=forecast.brand_change,
            probability=self._path_probability(path),
            strategic_position='better' if forecast.net_positive else 'worse'
        )
```

### 2.4 Data Models

```python
# consultantos/models/wargaming.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """Types of strategic actions"""
    PRICE_CUT = "price_cut"
    PRICE_INCREASE = "price_increase"
    PRODUCT_LAUNCH = "product_launch"
    MARKET_ENTRY = "market_entry"
    MARKET_EXIT = "market_exit"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    MARKETING_CAMPAIGN = "marketing_campaign"
    CAPACITY_EXPANSION = "capacity_expansion"
    R_AND_D_INVESTMENT = "r_and_d_investment"

class StrategicAction(BaseModel):
    """A strategic move"""
    type: ActionType
    description: str
    parameters: Dict[str, float]  # e.g., {"price_change_pct": -20}
    expected_cost: float
    timeline_months: int

class Scenario(BaseModel):
    """Initial scenario to wargame"""
    name: str
    our_company: str
    action: StrategicAction
    competitors: List[str]
    market_context: str
    assumptions: List[str]

class CompetitorResponse(BaseModel):
    """Predicted competitor response"""
    competitor: str
    action: StrategicAction
    probability: float = Field(ge=0, le=1)
    rationale: str
    expected_timeline_days: int

class GameNode(BaseModel):
    """Node in game tree"""
    move_type: Literal['our_move', 'competitor_response', 'our_counter']
    action: StrategicAction
    player: str  # 'us' or competitor name
    depth: int
    probability: float = 1.0
    children: List['GameNode'] = []

    def add_child(self, node: 'GameNode'):
        self.children.append(node)

    def get_history(self) -> List['GameNode']:
        """Get path from root to this node"""
        # Implemented via parent tracking
        pass

class GameTree(BaseModel):
    """Complete game tree"""
    root: GameNode
    max_depth: int
    total_nodes: int = 0
    total_paths: int = 0

class SimulationOutcome(BaseModel):
    """Outcome of one Monte Carlo simulation"""
    path: List[GameNode]
    market_share_change: float  # Percentage points
    revenue_change: float  # Dollar amount
    profit_change: float  # Dollar amount
    brand_perception_change: float  # -1 to 1
    probability: float  # Combined path probability
    strategic_position: Literal['better', 'worse', 'neutral']

class OutcomeDistribution(BaseModel):
    """Statistical distribution of outcomes"""
    mean_market_share_change: float
    mean_revenue_change: float
    mean_profit_change: float
    percentile_10: float  # 10th percentile (worst case)
    percentile_50: float  # Median
    percentile_90: float  # 90th percentile (best case)
    std_dev: float

class StrategicRecommendation(BaseModel):
    """Recommendation from wargaming"""
    recommendation: str
    rationale: str
    expected_outcome: str
    risk_level: Literal['low', 'medium', 'high']
    confidence: float = Field(ge=0, le=1)

class SimulationResult(BaseModel):
    """Complete wargaming simulation result"""
    scenario: Scenario
    game_tree: GameTree
    num_simulations: int
    outcome_distribution: OutcomeDistribution
    expected_value: float  # Expected profit impact
    best_case: SimulationOutcome
    worst_case: SimulationOutcome
    recommendations: List[StrategicRecommendation]
    simulated_at: datetime
```

### 2.5 API Endpoints

```python
# consultantos/api/wargaming_endpoints.py

from fastapi import APIRouter, Depends, HTTPException
from consultantos.agents.wargaming_agent import WarGamingAgent
from consultantos.models.wargaming import Scenario, SimulationResult
from consultantos.auth import get_current_user

router = APIRouter(prefix="/wargaming", tags=["wargaming"])

@router.post("/simulate", response_model=SimulationResult)
async def run_wargaming_simulation(
    scenario: Scenario,
    num_moves: int = 3,
    simulations: int = 1000,
    user = Depends(get_current_user)
):
    """
    Run wargaming simulation for strategic scenario

    Args:
        scenario: Strategic move to test
        num_moves: How many moves ahead to simulate (3-5)
        simulations: Monte Carlo iterations (100-10000)

    Returns:
        Simulation results with outcome distribution and recommendations

    Rate limit: 20 requests/hour (computationally expensive)
    """
    if num_moves > 5:
        raise HTTPException(status_code=400, detail="Max 5 moves ahead")

    if simulations > 10000:
        raise HTTPException(status_code=400, detail="Max 10000 simulations")

    agent = WarGamingAgent()

    try:
        result = await agent.execute(
            scenario=scenario,
            competitors=scenario.competitors,
            num_moves=num_moves,
            simulations=simulations
        )

        # Store result
        await db.collection('wargaming_results').add({
            'user_id': user.id,
            'scenario_name': scenario.name,
            'result': result.dict(),
            'created_at': datetime.utcnow()
        })

        return result

    except Exception as e:
        logger.error(f"Wargaming simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios/templates")
async def get_scenario_templates():
    """Get pre-built wargaming scenario templates"""
    templates = [
        {
            "name": "Price War Response",
            "description": "Test response to competitor price cut",
            "action_type": "price_cut",
            "typical_parameters": {"price_change_pct": -15}
        },
        {
            "name": "New Product Launch",
            "description": "Model reactions to new product entry",
            "action_type": "product_launch",
            "typical_parameters": {"market_segment": "premium"}
        },
        {
            "name": "Market Entry Defense",
            "description": "Defend against new market entrant",
            "action_type": "marketing_campaign",
            "typical_parameters": {"budget_increase_pct": 50}
        }
    ]

    return templates

@router.get("/history")
async def get_wargaming_history(
    limit: int = 20,
    user = Depends(get_current_user)
):
    """Get user's wargaming simulation history"""
    results = await db.collection('wargaming_results')\
        .where('user_id', '==', user.id)\
        .order_by('created_at', direction='DESCENDING')\
        .limit(limit)\
        .get()

    return [doc.to_dict() for doc in results]
```

### 2.6 Performance Targets

- **Simulation time**: <30 seconds for 3-move, 1000-simulation scenario
- **Game tree generation**: <10 seconds for 5 competitors, 3 moves
- **LLM response prediction**: <5 seconds per competitor
- **Monte Carlo throughput**: 100 simulations/second
- **Visualization rendering**: <2 seconds for decision tree (client-side)
- **API response time**: <45 seconds total (p95)

---

## Skill 3: Self-Service Analytics Builder

### 3.1 Overview

**Purpose**: No-code dashboard/report builder for democratizing insights

**Key Features**:
- Drag-and-drop report builder UI
- Custom metric definitions (user-defined formulas)
- Widget library (50+ chart types)
- Saved queries and templates
- Scheduled reports (daily/weekly/monthly)
- Export to PDF/Excel/PowerPoint
- Sharing and collaboration
- Version control

**Business Value**:
- Empower non-technical users
- Reduce dependency on data team
- Faster insights (self-serve vs request queue)
- Template marketplace (community knowledge)

### 3.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│         Frontend: Self-Service Builder              │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Drag & Drop  │  │   Widget     │  │  Query   │  │
│  │   Builder    │→ │   Library    │→ │  Editor  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│         ↓                  ↓                ↓        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │   Preview    │  │  Template    │  │  Export  │  │
│  │   Renderer   │  │  Marketplace │  │  Engine  │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
         ↓                  ↓                ↓
┌─────────────────────────────────────────────────────┐
│         Backend: Analytics Service                   │
│  ┌───────────────┐  ┌───────────────┐               │
│  │  Query        │  │  Metric       │               │
│  │  Executor     │  │  Calculator   │               │
│  └───────────────┘  └───────────────┘               │
│  ┌───────────────┐  ┌───────────────┐               │
│  │  Dashboard    │  │  Schedule     │               │
│  │  Storage      │  │  Manager      │               │
│  └───────────────┘  └───────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 3.3 Components

#### 3.3.1 Custom Metric Engine

```python
# consultantos/analytics/metric_engine.py

from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import text

class MetricEngine:
    """
    Engine for evaluating custom user-defined metrics

    Supports formulas like:
    - "revenue / customers" (simple division)
    - "SUM(revenue) / COUNT(DISTINCT customer_id)" (aggregations)
    - "LAG(revenue, 1) - revenue" (window functions)
    """

    def __init__(self, db_session):
        self.db = db_session

    async def evaluate_metric(
        self,
        metric_definition: str,
        data_source: str,
        filters: Dict[str, Any] = None,
        time_range: Dict[str, str] = None
    ) -> pd.DataFrame:
        """
        Evaluate custom metric definition

        Args:
            metric_definition: Formula like "revenue / customers"
            data_source: Which dataset to query
            filters: Optional filters (company, industry, etc.)
            time_range: Optional time range

        Returns:
            DataFrame with metric values
        """
        # Parse metric definition
        parsed = self._parse_metric(metric_definition)

        # Build SQL query
        sql_query = self._build_sql_query(
            metric=parsed,
            data_source=data_source,
            filters=filters,
            time_range=time_range
        )

        # Execute query
        result = await self.db.execute(text(sql_query))

        # Convert to DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        return df

    def _parse_metric(self, definition: str) -> Dict:
        """Parse metric formula into AST"""
        # Support operators: +, -, *, /, ()
        # Support functions: SUM, AVG, COUNT, MIN, MAX
        # Support window functions: LAG, LEAD, RANK

        # Simplified parser (use proper parser like lark in production)
        tokens = self._tokenize(definition)
        ast = self._build_ast(tokens)

        return ast

    def _build_sql_query(
        self,
        metric: Dict,
        data_source: str,
        filters: Dict = None,
        time_range: Dict = None
    ) -> str:
        """Build SQL query from metric AST"""
        # Convert AST to SQL
        select_clause = self._ast_to_sql(metric)

        # Build WHERE clause from filters
        where_conditions = []
        if filters:
            for key, value in filters.items():
                where_conditions.append(f"{key} = '{value}'")

        if time_range:
            where_conditions.append(
                f"date >= '{time_range['start']}' AND date <= '{time_range['end']}'"
            )

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        query = f"""
        SELECT
            date,
            {select_clause} as metric_value
        FROM {data_source}
        WHERE {where_clause}
        GROUP BY date
        ORDER BY date
        """

        return query
```

#### 3.3.2 Dashboard Builder Backend

```python
# consultantos/api/dashboard_builder_endpoints.py

from fastapi import APIRouter, Depends, HTTPException
from consultantos.models.dashboards import (
    Dashboard,
    Widget,
    CustomMetric,
    CreateDashboardRequest,
    ExportFormat
)
from consultantos.analytics.metric_engine import MetricEngine
from consultantos.auth import get_current_user

router = APIRouter(prefix="/dashboards", tags=["dashboards"])

@router.post("/create", response_model=Dashboard)
async def create_dashboard(
    request: CreateDashboardRequest,
    user = Depends(get_current_user)
):
    """
    Create custom dashboard

    User can define:
    - Layout (grid-based)
    - Widgets (charts, tables, KPIs)
    - Custom metrics
    - Filters
    """
    dashboard_id = str(uuid.uuid4())

    # Validate widgets
    for widget in request.widgets:
        await _validate_widget(widget)

    # Store dashboard
    dashboard = Dashboard(
        id=dashboard_id,
        name=request.name,
        description=request.description,
        widgets=request.widgets,
        layout=request.layout,
        filters=request.filters,
        created_by=user.id,
        created_at=datetime.utcnow(),
        version=1
    )

    await db.collection('custom_dashboards').document(dashboard_id).set(
        dashboard.dict()
    )

    return dashboard

@router.get("/{dashboard_id}/data")
async def get_dashboard_data(
    dashboard_id: str,
    filters: Dict[str, Any] = None,
    user = Depends(get_current_user)
):
    """
    Get data for all widgets in dashboard

    Executes queries for each widget and returns results
    """
    # Load dashboard
    dashboard_doc = await db.collection('custom_dashboards').document(dashboard_id).get()
    if not dashboard_doc.exists:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    dashboard = Dashboard(**dashboard_doc.to_dict())

    # Execute queries for each widget (in parallel)
    metric_engine = MetricEngine(db)
    widget_data = {}

    for widget in dashboard.widgets:
        data = await metric_engine.evaluate_metric(
            metric_definition=widget.metric,
            data_source=widget.data_source,
            filters={**(dashboard.filters or {}), **(filters or {})},
            time_range=widget.time_range
        )

        widget_data[widget.id] = data.to_dict('records')

    return widget_data

@router.post("/{dashboard_id}/schedule")
async def schedule_dashboard_report(
    dashboard_id: str,
    frequency: Literal['daily', 'weekly', 'monthly'],
    recipients: List[str],
    format: ExportFormat = ExportFormat.PDF,
    user = Depends(get_current_user)
):
    """
    Schedule automated dashboard report

    Will email dashboard as PDF/Excel on schedule
    """
    schedule_id = str(uuid.uuid4())

    await db.collection('scheduled_reports').document(schedule_id).set({
        'dashboard_id': dashboard_id,
        'frequency': frequency,
        'recipients': recipients,
        'format': format,
        'created_by': user.id,
        'created_at': datetime.utcnow(),
        'status': 'active',
        'next_run': _calculate_next_run(frequency)
    })

    return {'schedule_id': schedule_id, 'status': 'active'}

@router.post("/{dashboard_id}/export")
async def export_dashboard(
    dashboard_id: str,
    format: ExportFormat,
    user = Depends(get_current_user)
):
    """
    Export dashboard to PDF/Excel/PowerPoint
    """
    # Load dashboard data
    dashboard_data = await get_dashboard_data(dashboard_id)

    # Generate export
    if format == ExportFormat.PDF:
        file_path = await _export_to_pdf(dashboard_id, dashboard_data)
    elif format == ExportFormat.EXCEL:
        file_path = await _export_to_excel(dashboard_id, dashboard_data)
    elif format == ExportFormat.PPTX:
        file_path = await _export_to_pptx(dashboard_id, dashboard_data)

    # Upload to Cloud Storage
    signed_url = await storage.upload_and_sign(file_path)

    return {'download_url': signed_url, 'expires_in': 3600}

@router.get("/marketplace/templates")
async def get_template_marketplace():
    """
    Get community-shared dashboard templates

    Users can publish their dashboards as templates
    """
    templates = await db.collection('dashboard_templates')\
        .where('visibility', '==', 'public')\
        .order_by('downloads', direction='DESCENDING')\
        .limit(50)\
        .get()

    return [doc.to_dict() for doc in templates]
```

### 3.4 Frontend Components

```typescript
// frontend/app/dashboards/builder/page.tsx

import { DashboardBuilder } from '@/components/DashboardBuilder'
import { WidgetLibrary } from '@/components/WidgetLibrary'
import { useBuilderState } from '@/hooks/useBuilderState'

export default function DashboardBuilderPage() {
  const {
    widgets,
    addWidget,
    removeWidget,
    updateWidget,
    saveDashboard
  } = useBuilderState()

  return (
    <div className="flex h-screen">
      {/* Widget Library Sidebar */}
      <WidgetLibrary onAddWidget={addWidget} />

      {/* Canvas */}
      <DashboardBuilder
        widgets={widgets}
        onUpdateWidget={updateWidget}
        onRemoveWidget={removeWidget}
      />

      {/* Properties Panel */}
      <PropertiesPanel />
    </div>
  )
}
```

```typescript
// frontend/components/DashboardBuilder.tsx

import { Responsive, WidthProvider } from 'react-grid-layout'
import { Widget } from './Widget'

const ResponsiveGridLayout = WidthProvider(Responsive)

export function DashboardBuilder({ widgets, onUpdateWidget, onRemoveWidget }) {
  const [layout, setLayout] = useState([])

  return (
    <ResponsiveGridLayout
      className="dashboard-canvas"
      layouts={{ lg: layout }}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4 }}
      rowHeight={50}
      onLayoutChange={setLayout}
    >
      {widgets.map(widget => (
        <div key={widget.id} data-grid={widget.layout}>
          <Widget
            {...widget}
            onUpdate={(updates) => onUpdateWidget(widget.id, updates)}
            onRemove={() => onRemoveWidget(widget.id)}
          />
        </div>
      ))}
    </ResponsiveGridLayout>
  )
}
```

### 3.5 Data Models

```python
# consultantos/models/dashboards.py

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum

class WidgetType(str, Enum):
    """Types of dashboard widgets"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"
    GAUGE = "gauge"
    FUNNEL = "funnel"
    WATERFALL = "waterfall"

class ChartConfig(BaseModel):
    """Chart configuration"""
    x_axis: str
    y_axis: str
    group_by: Optional[str] = None
    colors: List[str] = []
    show_legend: bool = True
    show_grid: bool = True

class Widget(BaseModel):
    """Dashboard widget"""
    id: str
    type: WidgetType
    title: str
    metric: str  # Metric formula
    data_source: str
    time_range: Optional[Dict[str, str]] = None
    chart_config: Optional[ChartConfig] = None
    layout: Dict[str, int]  # Grid position: {x, y, w, h}

class DashboardLayout(BaseModel):
    """Dashboard layout configuration"""
    cols: int = 12
    rows: int = 20
    row_height: int = 50

class Dashboard(BaseModel):
    """Custom dashboard"""
    id: str
    name: str
    description: str
    widgets: List[Widget]
    layout: DashboardLayout
    filters: Optional[Dict[str, Any]] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    version: int = 1
    visibility: Literal['private', 'shared', 'public'] = 'private'

class ExportFormat(str, Enum):
    """Dashboard export formats"""
    PDF = "pdf"
    EXCEL = "excel"
    PPTX = "pptx"

class CreateDashboardRequest(BaseModel):
    """Request to create dashboard"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    widgets: List[Widget]
    layout: DashboardLayout
    filters: Optional[Dict[str, Any]] = None
```

---

## Skill 4: Data Storytelling Engine

### 4.1 Overview

**Purpose**: Auto-generate narrative summaries with contextual explanations

**Key Features**:
- Auto-generate executive briefings
- "Why this matters" context
- Personalized insights by role (CEO, CMO, CFO)
- Narrative arc: Problem → Analysis → Insight → Action
- Multi-format output (text, slides, video script)
- Tone adjustment (formal, casual, technical)

**Business Value**:
- Make insights accessible to executives
- Save time writing reports
- Ensure consistent messaging
- Improve decision-making speed

### 4.2 Architecture

```
┌─────────────────────────────────────────────────────┐
│         StorytellingAgent (New)                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │   Insight    │  │  Narrative   │  │  Tone    │  │
│  │  Extractor   │→ │  Generator   │→ │ Adjuster │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│         ↓                  ↓                ↓        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │Persona-Based │  │  Multi-Format│  │  Slide   │  │
│  │ Personalizer │  │  Formatter   │  │ Generator│  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
         ↓                  ↓                ↓
┌─────────────────────────────────────────────────────┐
│         Integration Layer                            │
│  ┌───────────────┐  ┌───────────────┐               │
│  │  Gemini LLM   │  │  Synthesis    │               │
│  │  (Narrative)  │  │  Agent        │               │
│  └───────────────┘  └───────────────┘               │
└─────────────────────────────────────────────────────┘
```

### 4.3 StorytellingAgent

```python
# consultantos/agents/storytelling_agent.py

from consultantos.agents.base_agent import BaseAgent
from consultantos.models.storytelling import (
    StoryRequest,
    Narrative,
    ExecutiveBriefing,
    SlideOutline
)

class StorytellingAgent(BaseAgent):
    """
    Agent for generating data narratives and executive briefings

    Transforms raw analysis into compelling stories with:
    - Problem framing
    - Key insights
    - Actionable recommendations
    - Role-specific personalization
    """

    def __init__(self):
        super().__init__("StorytellingAgent", timeout=60)

    async def _execute_internal(
        self,
        analysis_data: Dict,
        target_audience: Literal['CEO', 'CMO', 'CFO', 'Board', 'Team'],
        tone: Literal['formal', 'casual', 'technical'] = 'formal',
        format: Literal['text', 'slides', 'video_script'] = 'text',
        length: Literal['brief', 'standard', 'detailed'] = 'standard'
    ) -> Narrative:
        """
        Generate data narrative

        Args:
            analysis_data: Raw analysis from agents
            target_audience: Who is reading this
            tone: Communication style
            format: Output format
            length: How detailed

        Returns:
            Narrative with problem, insights, recommendations
        """
        # Extract key insights
        insights = self._extract_key_insights(analysis_data)

        # Generate narrative structure
        narrative_structure = await self._generate_narrative(
            insights=insights,
            audience=target_audience,
            tone=tone
        )

        # Personalize for audience
        personalized = self._personalize_for_audience(
            narrative=narrative_structure,
            audience=target_audience
        )

        # Format output
        if format == 'text':
            output = self._format_as_text(personalized, length)
        elif format == 'slides':
            output = self._format_as_slides(personalized)
        elif format == 'video_script':
            output = self._format_as_video_script(personalized)

        return Narrative(
            title=personalized['title'],
            executive_summary=personalized['summary'],
            problem_statement=personalized['problem'],
            key_insights=personalized['insights'],
            recommendations=personalized['recommendations'],
            next_steps=personalized['next_steps'],
            formatted_output=output,
            target_audience=target_audience,
            tone=tone,
            generated_at=datetime.utcnow()
        )

    def _extract_key_insights(self, analysis_data: Dict) -> List[Insight]:
        """Extract most important insights from analysis"""
        insights = []

        # From research agent
        if 'research' in analysis_data:
            insights.append(Insight(
                type='market_position',
                finding=analysis_data['research']['key_finding'],
                importance='high',
                supporting_data=analysis_data['research']['evidence']
            ))

        # From market agent
        if 'market' in analysis_data:
            insights.append(Insight(
                type='market_trend',
                finding=analysis_data['market']['trend'],
                importance='medium',
                supporting_data=analysis_data['market']['data']
            ))

        # From financial agent
        if 'financial' in analysis_data:
            insights.append(Insight(
                type='financial_performance',
                finding=analysis_data['financial']['summary'],
                importance='high',
                supporting_data=analysis_data['financial']['metrics']
            ))

        # From framework agent
        if 'framework' in analysis_data:
            for framework_name, framework_data in analysis_data['framework'].items():
                insights.append(Insight(
                    type=f'framework_{framework_name}',
                    finding=framework_data['key_insight'],
                    importance='high',
                    supporting_data=framework_data
                ))

        # Rank by importance
        insights.sort(key=lambda i: i.importance, reverse=True)

        return insights[:5]  # Top 5

    async def _generate_narrative(
        self,
        insights: List[Insight],
        audience: str,
        tone: str
    ) -> Dict:
        """Generate narrative structure using Gemini"""
        prompt = f"""
        You are an executive communications expert. Generate a compelling business narrative.

        Audience: {audience}
        Tone: {tone}

        Key Insights:
        {self._format_insights(insights)}

        Create a narrative with:
        1. Title (compelling, action-oriented)
        2. Executive Summary (2-3 sentences, bottom line up front)
        3. Problem Statement (what challenge/opportunity does this address?)
        4. Key Insights (3-5 bullets, "why this matters" for each)
        5. Recommendations (3 specific, actionable recommendations)
        6. Next Steps (concrete actions with owners and timelines)

        Use storytelling techniques:
        - Start with impact/outcome
        - Use concrete examples
        - Quantify when possible
        - End with clear call to action

        Tailor language for {audience}:
        - CEO: Strategic, high-level, focused on competitive position
        - CMO: Market-focused, customer-centric, brand implications
        - CFO: Financial impact, ROI, risk mitigation
        """

        response = await self.instructor_client.chat.completions.create(
            model="gemini-1.5-flash",
            response_model=NarrativeStructure,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.dict()

    def _personalize_for_audience(
        self,
        narrative: Dict,
        audience: str
    ) -> Dict:
        """Add audience-specific framing"""
        if audience == 'CEO':
            narrative['focus'] = 'strategic positioning'
            narrative['emphasis'] = [
                'competitive advantage',
                'market opportunity',
                'strategic risk'
            ]

        elif audience == 'CMO':
            narrative['focus'] = 'market and customer impact'
            narrative['emphasis'] = [
                'brand perception',
                'customer segments',
                'marketing opportunities'
            ]

        elif audience == 'CFO':
            narrative['focus'] = 'financial implications'
            narrative['emphasis'] = [
                'revenue impact',
                'cost implications',
                'ROI timeline'
            ]

        return narrative

    def _format_as_slides(self, narrative: Dict) -> SlideOutline:
        """Format narrative as slide deck outline"""
        slides = [
            {
                'number': 1,
                'title': 'Executive Summary',
                'content': narrative['summary'],
                'visual': 'key metrics dashboard'
            },
            {
                'number': 2,
                'title': 'The Challenge',
                'content': narrative['problem'],
                'visual': 'problem illustration'
            }
        ]

        # Add slide for each insight
        for i, insight in enumerate(narrative['insights'], start=3):
            slides.append({
                'number': i,
                'title': insight['title'],
                'content': insight['explanation'],
                'visual': insight['supporting_chart']
            })

        # Recommendations slide
        slides.append({
            'number': len(slides) + 1,
            'title': 'Recommended Actions',
            'content': narrative['recommendations'],
            'visual': 'action roadmap'
        })

        return SlideOutline(
            total_slides=len(slides),
            slides=slides,
            estimated_duration_minutes=len(slides) * 2
        )
```

### 4.4 API Endpoints

```python
# consultantos/api/storytelling_endpoints.py

from fastapi import APIRouter, Depends, HTTPException
from consultantos.agents.storytelling_agent import StorytellingAgent
from consultantos.models.storytelling import StoryRequest, Narrative

router = APIRouter(prefix="/storytelling", tags=["storytelling"])

@router.post("/generate", response_model=Narrative)
async def generate_narrative(
    request: StoryRequest,
    user = Depends(get_current_user)
):
    """
    Generate data narrative from analysis

    Transforms raw analysis into compelling story
    with personalization for target audience
    """
    agent = StorytellingAgent()

    try:
        narrative = await agent.execute(
            analysis_data=request.analysis_data,
            target_audience=request.target_audience,
            tone=request.tone,
            format=request.format,
            length=request.length
        )

        return narrative

    except Exception as e:
        logger.error(f"Narrative generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brief", response_model=ExecutiveBriefing)
async def generate_executive_brief(
    analysis_id: str,
    audience: Literal['CEO', 'CMO', 'CFO', 'Board'],
    user = Depends(get_current_user)
):
    """
    Generate one-page executive briefing

    Extracts key insights and formats as concise brief
    """
    # Load analysis
    analysis_doc = await db.collection('analyses').document(analysis_id).get()
    if not analysis_doc.exists:
        raise HTTPException(status_code=404, detail="Analysis not found")

    analysis_data = analysis_doc.to_dict()

    # Generate brief
    agent = StorytellingAgent()
    narrative = await agent.execute(
        analysis_data=analysis_data,
        target_audience=audience,
        tone='formal',
        format='text',
        length='brief'
    )

    return ExecutiveBriefing(
        title=narrative.title,
        summary=narrative.executive_summary,
        insights=narrative.key_insights[:3],  # Top 3
        recommendations=narrative.recommendations[:3],  # Top 3
        generated_for=audience,
        generated_at=datetime.utcnow()
    )
```

---

## Cross-Skill Integration

### Integration Matrix

| Skill | Integrates With | Integration Point |
|-------|----------------|-------------------|
| Social Media | Phase 1: Conversational AI | Chat queries: "Show negative mentions today" |
| Social Media | Phase 1: Predictive | Correlate sentiment with stock forecasts |
| Social Media | Existing: Monitoring | Social alerts in monitoring feed |
| Wargaming | Phase 1: Forecasting | Use forecasts as baseline for scenarios |
| Wargaming | Existing: Framework | SWOT outcomes inform wargaming |
| Self-Service | All Skills | Dashboards display any metric/analysis |
| Storytelling | All Skills | Generate narratives from any analysis |

### Data Flow Example

```
User Query: "What if we cut prices 20%?"
    ↓
Conversational AI (Phase 1) interprets query
    ↓
Wargaming Agent simulates scenario
    ├─ Uses Forecasting Agent for baseline
    ├─ Uses Historical Analysis for competitor patterns
    └─ Runs Monte Carlo simulation
    ↓
Social Media Agent checks current sentiment
    ↓
Storytelling Agent generates executive brief
    ↓
User sees: Narrative with probability distribution + social sentiment context
```

---

## Database Schema

### New Firestore Collections

**`social_monitors`**, **`social_mentions`**, **`social_alerts`** (see Section 1.6)

**`wargaming_results`**:
```json
{
  "result_id": "uuid",
  "user_id": "user_uuid",
  "scenario_name": "Price War Response",
  "scenario": {
    "our_company": "Tesla",
    "action": {
      "type": "price_cut",
      "description": "Cut Model 3 price by 20%",
      "parameters": {"price_change_pct": -20}
    },
    "competitors": ["BYD", "NIO"]
  },
  "game_tree": {...},
  "outcome_distribution": {
    "mean_revenue_change": -15000000,
    "percentile_10": -50000000,
    "percentile_90": 20000000
  },
  "recommendations": [...],
  "created_at": "2025-11-09T14:00:00Z"
}
```

**`custom_dashboards`**:
```json
{
  "dashboard_id": "uuid",
  "name": "Executive Dashboard",
  "widgets": [
    {
      "id": "widget_1",
      "type": "line_chart",
      "title": "Revenue Trend",
      "metric": "SUM(revenue)",
      "data_source": "financial_snapshots",
      "layout": {"x": 0, "y": 0, "w": 6, "h": 4}
    }
  ],
  "created_by": "user_uuid",
  "visibility": "private",
  "version": 1
}
```

**`scheduled_reports`**:
```json
{
  "schedule_id": "uuid",
  "dashboard_id": "dashboard_uuid",
  "frequency": "weekly",
  "recipients": ["ceo@company.com"],
  "format": "pdf",
  "next_run": "2025-11-16T09:00:00Z",
  "status": "active"
}
```

**`narratives`**:
```json
{
  "narrative_id": "uuid",
  "analysis_id": "analysis_uuid",
  "title": "Q4 Competitive Position: Key Insights",
  "executive_summary": "Tesla maintains #1 position...",
  "target_audience": "CEO",
  "tone": "formal",
  "generated_at": "2025-11-09T15:00:00Z"
}
```

---

## API Specifications

### New Endpoints Summary

**Social Media (7 endpoints)**:
- `POST /social-media/analyze` - Analyze mentions/sentiment
- `POST /social-media/monitors` - Create monitor
- `GET /social-media/monitors/{id}/alerts` - Get alerts
- `GET /social-media/stream` - Real-time stream
- `DELETE /social-media/monitors/{id}` - Delete monitor
- `PUT /social-media/monitors/{id}` - Update monitor
- `GET /social-media/influencers` - Get influencers

**Wargaming (5 endpoints)**:
- `POST /wargaming/simulate` - Run simulation
- `GET /wargaming/scenarios/templates` - Get templates
- `GET /wargaming/history` - Get history
- `POST /wargaming/scenarios` - Save scenario
- `GET /wargaming/{id}/visualize` - Get viz data

**Dashboards (10 endpoints)**:
- `POST /dashboards/create` - Create dashboard
- `GET /dashboards/{id}` - Get dashboard
- `GET /dashboards/{id}/data` - Get data
- `PUT /dashboards/{id}` - Update dashboard
- `DELETE /dashboards/{id}` - Delete dashboard
- `POST /dashboards/{id}/schedule` - Schedule report
- `POST /dashboards/{id}/export` - Export
- `GET /dashboards/marketplace/templates` - Templates
- `POST /dashboards/fork/{id}` - Fork template
- `GET /dashboards` - List dashboards

**Storytelling (4 endpoints)**:
- `POST /storytelling/generate` - Generate narrative
- `POST /storytelling/brief` - Executive brief
- `GET /storytelling/{id}` - Get narrative
- `POST /storytelling/regenerate` - Regenerate

**Total**: 26 new endpoints

---

## Performance & Scaling

### Resource Requirements

**Per Skill**:
- Social Media: +4GB memory (streaming buffers), +500MB storage/day
- Wargaming: +3GB memory (Monte Carlo), +100MB storage/simulation
- Dashboards: +2GB memory (query cache), +500MB storage (dashboard configs)
- Storytelling: +1GB memory (LLM context), +50MB storage/narrative

**Total Phase 2**: +10GB memory, +~2GB storage/day

### Performance Targets

| Skill | Operation | Target (p95) |
|-------|-----------|-------------|
| Social Media | Real-time stream latency | <5s |
| Social Media | 24h analysis | <10s |
| Wargaming | 3-move, 1000-sim | <30s |
| Wargaming | Game tree generation | <10s |
| Dashboards | Dashboard render | <3s |
| Dashboards | Query execution | <5s |
| Storytelling | Narrative generation | <15s |
| Storytelling | Executive brief | <10s |

### Scaling Strategy

**Horizontal Scaling**:
- Deploy each skill as separate Cloud Run service
- Auto-scale based on request load
- Use Cloud Tasks for async operations

**Caching**:
- Social media mentions: 30-day cache
- Wargaming results: Permanent cache (user-specific)
- Dashboard queries: 1-hour cache
- Narratives: Permanent cache (versioned)

---

## Security & Compliance

### Authentication & Authorization

**Social Media**:
- Requires user OAuth tokens for platforms
- Store encrypted in Secret Manager
- Scope: Read-only access

**Wargaming**:
- User-level access control
- Results private by default
- Option to share with team

**Dashboards**:
- RBAC: Owner, Editor, Viewer
- Public templates require approval
- Rate limit: 100 dashboards/user

**Storytelling**:
- Access control tied to analysis access
- No PII in narratives
- Audit log for generation

### Privacy Compliance

**GDPR**:
- Social media data: 30-day retention
- Right to delete: Cascading deletes
- Data export: Include all generated content

**Data Minimization**:
- Only store essential metadata
- Aggregate before storage
- Delete raw data after processing

---

## Testing Strategy

### Unit Tests (150+ tests)

**Social Media**:
- Platform connectors (mocked APIs)
- Sentiment analysis pipeline
- Influencer detection algorithm

**Wargaming**:
- Game tree generation
- Monte Carlo simulation
- Outcome evaluation

**Dashboards**:
- Metric engine parser
- Query builder
- Layout engine

**Storytelling**:
- Insight extraction
- Narrative generation (mocked LLM)
- Personalization logic

### Integration Tests (40+ tests)

- Social → Monitoring integration
- Wargaming → Forecasting integration
- Dashboards → All data sources
- Storytelling → All agents

### E2E Tests (10 scenarios)

1. Create social monitor → Detect crisis → Send alert
2. Run wargaming → Get recommendations → Export PDF
3. Build dashboard → Schedule report → Receive email
4. Generate narrative → Export slides → Share with team

---

## Deployment Plan

### Rollout Strategy

**Week 1**: Social Media Intelligence
- Deploy connectors
- Enable monitoring
- Beta with 10 users

**Week 2**: Wargaming
- Deploy simulation engine
- Add templates
- Beta with 20 users

**Week 3**: Self-Service Dashboards
- Deploy builder UI
- Seed template marketplace
- Beta with 50 users

**Week 4**: Data Storytelling
- Deploy narrative engine
- Integrate with all agents
- General availability

### Deployment Commands

```bash
# Social Media Service
gcloud run deploy social-media-service \
  --source ./consultantos/agents/social_media_agent.py \
  --region us-central1 \
  --memory 4Gi \
  --set-env-vars "TWITTER_BEARER_TOKEN=${TWITTER_TOKEN}"

# Wargaming Service
gcloud run deploy wargaming-service \
  --source ./consultantos/agents/wargaming_agent.py \
  --region us-central1 \
  --memory 3Gi \
  --timeout 300

# Dashboard Builder (Frontend)
cd frontend && npm run build
gcloud run deploy dashboard-builder \
  --source . \
  --region us-central1

# Storytelling Service
gcloud run deploy storytelling-service \
  --source ./consultantos/agents/storytelling_agent.py \
  --region us-central1 \
  --memory 2Gi
```

---

## Migration from Phase 1

### Compatibility

**No Breaking Changes**: Phase 2 is purely additive

**Database**: New collections only, no schema changes to existing

**APIs**: New endpoints, existing endpoints unchanged

**Frontend**: New pages, existing pages unchanged

### Migration Steps

1. Deploy Phase 2 services (parallel to Phase 1)
2. Update frontend with new UI components
3. Enable features via feature flags
4. Gradual rollout (10% → 50% → 100%)
5. Monitor performance and errors

---

## Implementation Timeline

**Total**: 8 weeks with 2 developers

| Week | Skill | Milestone |
|------|-------|-----------|
| 1-2 | Social Media | Connectors + Agent + API |
| 3-4 | Wargaming | Simulation + API + Templates |
| 5-6 | Dashboards | Builder UI + Backend + Marketplace |
| 7-8 | Storytelling | Narrative Engine + All Integrations |

---

## Success Metrics

**Adoption**:
- 50% of users create social monitor (within 30 days)
- 30% of users run wargaming simulation (within 60 days)
- 70% of users create custom dashboard (within 90 days)
- 80% of reports include AI narrative (within 90 days)

**Engagement**:
- Social monitors checked daily
- 5+ wargaming scenarios per user/month
- 3+ custom dashboards per user
- Narratives shared 2x more than raw reports

**Business Impact**:
- 40% faster strategic decision-making
- 60% reduction in manual report creation
- 90% user satisfaction with narratives
- 50% increase in competitive threat detection

---

**End of Phase 2 Architecture Document**

---

**Next Steps**:
1. Review Phase 2 design with team
2. Begin implementation (Week 1: Social Media)
3. Set up monitoring and alerting
4. Create Phase 3 roadmap (if needed)

**Questions?** Review `PHASE2_IMPLEMENTATION_SUMMARY.md` for detailed checklist and `PHASE2_QUICKSTART.md` for getting started quickly.
