"""
Social Media Intelligence API Endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field

from consultantos.agents.social_media_agent import SocialMediaAgent
from consultantos.models.social_media import (
    SocialMediaMonitorRequest,
    SocialMediaMonitorResponse,
    SocialMediaInsight
)
from consultantos.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social-media", tags=["Social Media Intelligence"])


# Dependency to get social media agent
def get_social_media_agent() -> SocialMediaAgent:
    """Get configured social media agent"""
    return SocialMediaAgent(
        twitter_bearer_token=settings.twitter_bearer_token,
        twitter_api_key=settings.twitter_api_key,
        twitter_api_secret=settings.twitter_api_secret,
        reddit_client_id=settings.reddit_client_id,
        reddit_client_secret=settings.reddit_client_secret,
        reddit_user_agent=settings.reddit_user_agent,
        laozhang_api_key=settings.laozhang_api_key,
        use_grok=False,  # Default to False, can be overridden per request
        timeout=120
    )


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    keywords: List[str] = Field(..., description="Keywords to monitor")
    frequency: str = Field(default="daily", description="Monitoring frequency")
    alert_threshold: float = Field(default=0.3, description="Alert threshold for sentiment shifts")


class SentimentAnalysisRequest(BaseModel):
    """Request for sentiment analysis"""
    company: str = Field(..., description="Company name")
    keywords: List[str] = Field(..., description="Keywords to analyze")
    days_back: int = Field(default=7, description="Days of history to analyze")
    use_grok: bool = Field(default=False, description="Use Grok API instead of Twitter API")


class InfluencerSearchRequest(BaseModel):
    """Request for influencer search"""
    topic: str = Field(..., description="Topic to search for")
    min_followers: int = Field(default=10000, description="Minimum follower count")
    max_results: int = Field(default=50, description="Maximum number of results")


class TrendingTopicsRequest(BaseModel):
    """Request for trending topics"""
    keywords: List[str] = Field(..., description="Keywords to analyze")
    days_back: int = Field(default=7, description="Days of history to analyze")
    top_n: int = Field(default=10, description="Number of top topics to return")


class AlertConfiguration(BaseModel):
    """Crisis alert configuration"""
    company: str = Field(..., description="Company to monitor")
    keywords: List[str] = Field(..., description="Keywords for monitoring")
    threshold: float = Field(default=0.3, description="Sentiment shift threshold")
    severity_levels: List[str] = Field(
        default=["high", "critical"],
        description="Severity levels to alert on"
    )


@router.post("/monitor", response_model=SocialMediaMonitorResponse)
async def monitor_social_media(
    request: SocialMediaMonitorRequest,
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Start social media monitoring for a company

    Monitors Twitter/X for:
    - Brand mentions and sentiment
    - Competitor tracking
    - Influencer identification
    - Trending topics
    - Crisis detection

    Args:
        request: Monitoring configuration
        agent: Social media agent instance

    Returns:
        SocialMediaMonitorResponse with insights and metrics
    """
    try:
        logger.info(f"Starting social media monitoring for {request.company}")

        # Execute monitoring (check if use_grok is in request)
        use_grok = getattr(request, 'use_grok', False)
        result = await agent.execute({
            "company": request.company,
            "use_grok": use_grok,
            "keywords": request.keywords,
            "competitors": request.competitors,
            "days_back": 7,  # Default to 1 week
            "min_influencer_followers": request.min_influencer_followers,
            "alert_threshold": request.alert_threshold
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Monitoring failed: {result.get('error')}"
            )

        return SocialMediaMonitorResponse(
            success=True,
            insights=result["data"],
            error=None,
            execution_time=0.0  # Will be set by middleware
        )

    except Exception as e:
        logger.error(f"Social media monitoring error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment", response_model=dict)
async def get_sentiment_analysis(
    company: str = Query(..., description="Company name"),
    keywords: List[str] = Query(None, description="Keywords to analyze"),
    days_back: int = Query(default=7, description="Days of history"),
    use_grok: bool = Query(default=False, description="Use Grok API instead of Twitter API"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Get sentiment analysis for a company

    Args:
        company: Company name to analyze
        keywords: Optional keywords (defaults to company name)
        days_back: Days of history to analyze
        use_grok: Use Grok API via laozhang.ai instead of Twitter API
        agent: Social media agent instance

    Returns:
        Sentiment analysis results
    """
    try:
        if not keywords:
            keywords = [company]

        logger.info(f"Getting sentiment for {company} (use_grok={use_grok})")

        result = await agent.execute({
            "company": company,
            "keywords": keywords,
            "days_back": days_back,
            "competitors": [],
            "alert_threshold": 1.0,  # Disable alerts
            "use_grok": use_grok
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Sentiment analysis failed: {result.get('error')}"
            )

        insight: SocialMediaInsight = result["data"]

        return {
            "company": company,
            "overall_sentiment": insight.overall_sentiment,
            "sentiment_label": insight.sentiment_label,
            "metrics": insight.metrics,
            "time_period": insight.time_period
        }

    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/influencers", response_model=dict)
async def find_influencers(
    topic: str = Query(..., description="Topic to search for"),
    min_followers: int = Query(default=10000, description="Minimum followers"),
    max_results: int = Query(default=50, description="Maximum results"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Find top influencers for a topic

    Args:
        topic: Topic to search for
        min_followers: Minimum follower count
        max_results: Maximum number of influencers
        agent: Social media agent instance

    Returns:
        List of top influencers
    """
    try:
        logger.info(f"Finding influencers for topic: {topic}")

        # Use agent's method directly
        influencers = await agent._find_influencers(
            keywords=[topic],
            min_followers=min_followers,
            max_results=max_results
        )

        return {
            "topic": topic,
            "influencer_count": len(influencers),
            "influencers": [inf.model_dump() for inf in influencers]
        }

    except Exception as e:
        logger.error(f"Influencer search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", response_model=dict)
async def get_trending_topics(
    keywords: List[str] = Query(..., description="Keywords to analyze"),
    days_back: int = Query(default=7, description="Days of history"),
    top_n: int = Query(default=10, description="Number of top topics"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Get trending topics related to keywords

    Args:
        keywords: Keywords to analyze
        days_back: Days of history to analyze
        top_n: Number of top topics to return
        agent: Social media agent instance

    Returns:
        Trending topics and statistics
    """
    try:
        logger.info(f"Getting trending topics for: {keywords}")

        result = await agent.execute({
            "company": keywords[0] if keywords else "",
            "keywords": keywords,
            "days_back": days_back,
            "competitors": [],
            "alert_threshold": 1.0  # Disable alerts
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Trend analysis failed: {result.get('error')}"
            )

        insight: SocialMediaInsight = result["data"]

        # Sort by mention count and limit
        trending = sorted(
            insight.trending_topics,
            key=lambda t: t.mention_count,
            reverse=True
        )[:top_n]

        return {
            "keywords": keywords,
            "trending_count": len(trending),
            "trending_topics": [topic.model_dump() for topic in trending],
            "time_period": insight.time_period
        }

    except Exception as e:
        logger.error(f"Trending topics error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/configure", response_model=dict)
async def configure_crisis_alerts(
    config: AlertConfiguration
):
    """
    Configure crisis alert settings

    Args:
        config: Alert configuration

    Returns:
        Configuration confirmation
    """
    try:
        logger.info(f"Configuring alerts for {config.company}")

        # In a real implementation, this would store the configuration
        # For now, just return the configuration
        return {
            "success": True,
            "message": "Alert configuration saved",
            "config": config.model_dump()
        }

    except Exception as e:
        logger.error(f"Alert configuration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=dict)
async def get_active_alerts(
    company: str = Query(..., description="Company name"),
    keywords: List[str] = Query(None, description="Keywords to monitor"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Get active crisis alerts for a company

    Args:
        company: Company name
        keywords: Optional keywords (defaults to company name)
        agent: Social media agent instance

    Returns:
        Active crisis alerts
    """
    try:
        if not keywords:
            keywords = [company]

        logger.info(f"Getting active alerts for {company}")

        result = await agent.execute({
            "company": company,
            "keywords": keywords,
            "days_back": 3,  # Last 3 days for recent alerts
            "competitors": [],
            "alert_threshold": 0.3
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Alert retrieval failed: {result.get('error')}"
            )

        insight: SocialMediaInsight = result["data"]

        return {
            "company": company,
            "alert_count": len(insight.crisis_alerts),
            "alerts": [alert.model_dump() for alert in insight.crisis_alerts],
            "requires_immediate_action": any(
                alert.requires_action for alert in insight.crisis_alerts
            )
        }

    except Exception as e:
        logger.error(f"Alert retrieval error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitors", response_model=dict)
async def track_competitors(
    company: str = Query(..., description="Your company name"),
    competitors: List[str] = Query(..., description="Competitor names"),
    days_back: int = Query(default=7, description="Days of history"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Track competitor mentions and sentiment

    Args:
        company: Your company name
        competitors: List of competitor names
        days_back: Days of history to analyze
        agent: Social media agent instance

    Returns:
        Competitor tracking data
    """
    try:
        logger.info(f"Tracking competitors for {company}: {competitors}")

        result = await agent.execute({
            "company": company,
            "keywords": [company],
            "competitors": competitors,
            "days_back": days_back,
            "alert_threshold": 1.0  # Disable alerts
        })

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Competitor tracking failed: {result.get('error')}"
            )

        insight: SocialMediaInsight = result["data"]

        return {
            "company": company,
            "competitors_tracked": len(insight.competitor_mentions),
            "competitor_data": {
                name: mention.model_dump()
                for name, mention in insight.competitor_mentions.items()
            },
            "time_period": insight.time_period
        }

    except Exception as e:
        logger.error(f"Competitor tracking error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reddit/search", response_model=dict)
async def search_reddit_posts(
    keywords: List[str] = Query(..., description="Keywords to search for"),
    subreddits: Optional[List[str]] = Query(None, description="Specific subreddits"),
    time_filter: str = Query(default="week", description="Time filter"),
    limit: int = Query(default=100, description="Maximum posts"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Search Reddit posts by keywords

    Args:
        keywords: Keywords to search for
        subreddits: Optional specific subreddits to search
        time_filter: Time filter (hour, day, week, month, year, all)
        limit: Maximum number of posts to return
        agent: Social media agent instance

    Returns:
        Reddit search results with sentiment analysis
    """
    try:
        logger.info(f"Searching Reddit for: {keywords}")

        # Search posts
        posts_data = await agent.reddit.search_posts(
            keywords=keywords,
            subreddits=subreddits,
            time_filter=time_filter,
            limit=limit
        )

        # Analyze sentiment for posts
        from consultantos.models.social_media import RedditPost
        posts = []

        for post_data in posts_data:
            content = f"{post_data['title']} {post_data['content']}"
            if content.strip():
                analyzed = await agent.sentiment_analyzer.analyze_tweets(
                    [{'content': content}]
                )
                post_data['sentiment_score'] = analyzed[0]['sentiment']['sentiment_score']

            posts.append(RedditPost(**post_data))

        return {
            "success": True,
            "post_count": len(posts),
            "posts": [post.model_dump() for post in posts],
            "subreddits_found": list(set(p.subreddit for p in posts))
        }

    except Exception as e:
        logger.error(f"Reddit search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reddit/subreddits", response_model=dict)
async def get_trending_subreddits(
    keywords: List[str] = Query(..., description="Keywords to search for"),
    min_subscribers: int = Query(default=1000, description="Minimum subscribers"),
    limit: int = Query(default=10, description="Maximum subreddits"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Find trending subreddits for keywords

    Args:
        keywords: Keywords to search for
        min_subscribers: Minimum subscriber count
        limit: Maximum number of subreddits
        agent: Social media agent instance

    Returns:
        Trending subreddits ranked by relevance
    """
    try:
        logger.info(f"Finding trending subreddits for: {keywords}")

        subreddits = await agent.reddit.find_trending_subreddits(
            keywords=keywords,
            min_subscribers=min_subscribers,
            limit=limit
        )

        return {
            "success": True,
            "subreddit_count": len(subreddits),
            "subreddits": subreddits
        }

    except Exception as e:
        logger.error(f"Subreddit discovery error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reddit/comments/{post_id}", response_model=dict)
async def analyze_reddit_comments(
    post_id: str,
    max_depth: int = Query(default=3, description="Maximum comment depth"),
    limit: int = Query(default=100, description="Maximum comments"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Analyze comments for a Reddit post

    Args:
        post_id: Reddit post ID
        max_depth: Maximum comment thread depth
        limit: Maximum comments to analyze
        agent: Social media agent instance

    Returns:
        Comment analysis with sentiment
    """
    try:
        logger.info(f"Analyzing comments for post: {post_id}")

        comments_data = await agent.reddit.analyze_comments(
            post_id=post_id,
            max_depth=max_depth,
            limit=limit
        )

        # Analyze sentiment for comments
        from consultantos.models.social_media import RedditComment
        comments = []

        for comment_data in comments_data:
            if comment_data['content'].strip():
                analyzed = await agent.sentiment_analyzer.analyze_tweets(
                    [{'content': comment_data['content']}]
                )
                comment_data['sentiment_score'] = analyzed[0]['sentiment']['sentiment_score']

            comments.append(RedditComment(**comment_data))

        # Calculate overall sentiment
        sentiments = [c.sentiment_score for c in comments]
        overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        return {
            "success": True,
            "post_id": post_id,
            "comment_count": len(comments),
            "overall_sentiment": round(overall_sentiment, 3),
            "comments": [comment.model_dump() for comment in comments]
        }

    except Exception as e:
        logger.error(f"Comment analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/combined", response_model=dict)
async def get_combined_insights(
    company: str = Query(..., description="Company name"),
    keywords: List[str] = Query(None, description="Keywords to track"),
    subreddits: Optional[List[str]] = Query(None, description="Subreddits to monitor"),
    days_back: int = Query(default=7, description="Days of history"),
    agent: SocialMediaAgent = Depends(get_social_media_agent)
):
    """
    Get combined Twitter + Reddit insights

    Args:
        company: Company name to monitor
        keywords: Optional keywords (defaults to company name)
        subreddits: Optional specific subreddits for Reddit
        days_back: Days of history to analyze
        agent: Social media agent instance

    Returns:
        Combined multi-platform insights
    """
    try:
        if not keywords:
            keywords = [company]

        logger.info(f"Getting combined insights for {company}")

        # Analyze Twitter
        twitter_result = await agent.execute({
            "company": company,
            "keywords": keywords,
            "days_back": days_back,
            "competitors": [],
            "alert_threshold": 1.0
        })

        # Analyze Reddit
        reddit_insight = await agent._analyze_reddit(
            keywords=keywords,
            subreddits=subreddits,
            days_back=days_back
        )

        # Combine insights
        twitter_insight = twitter_result.get("data") if twitter_result.get("success") else None

        combined_sentiment = 0.0
        sentiment_sources = 0

        if twitter_insight:
            combined_sentiment += twitter_insight.overall_sentiment
            sentiment_sources += 1

        if reddit_insight:
            combined_sentiment += reddit_insight.overall_sentiment
            sentiment_sources += 1

        overall_sentiment = combined_sentiment / sentiment_sources if sentiment_sources > 0 else 0.0

        # Combine trending topics
        all_trending = []
        if twitter_insight:
            all_trending.extend([t.topic for t in twitter_insight.trending_topics])
        if reddit_insight:
            all_trending.extend(reddit_insight.trending_topics)

        # Count topic frequencies
        from collections import Counter
        topic_counts = Counter(all_trending)
        top_trending = [topic for topic, _ in topic_counts.most_common(10)]

        return {
            "success": True,
            "company": company,
            "platforms": ["twitter", "reddit"],
            "overall_sentiment": round(overall_sentiment, 3),
            "sentiment_label": "positive" if overall_sentiment > 0.2 else "negative" if overall_sentiment < -0.2 else "neutral",
            "trending_topics": top_trending,
            "twitter_insights": twitter_insight.model_dump() if twitter_insight else None,
            "reddit_insights": reddit_insight.model_dump() if reddit_insight else None,
            "time_period": {
                "start": (datetime.now() - timedelta(days=days_back)).isoformat(),
                "end": datetime.now().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Combined insights error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for social media service"""
    return {
        "status": "healthy",
        "service": "social-media-intelligence",
        "platforms": ["twitter", "reddit"],
        "endpoints": [
            "/social-media/monitor",
            "/social-media/sentiment",
            "/social-media/influencers",
            "/social-media/trends",
            "/social-media/alerts",
            "/social-media/competitors",
            "/social-media/reddit/search",
            "/social-media/reddit/subreddits",
            "/social-media/reddit/comments/{post_id}",
            "/social-media/combined"
        ]
    }
