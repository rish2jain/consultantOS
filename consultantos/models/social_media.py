"""
Social media data models for monitoring and analysis
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Tweet(BaseModel):
    """Tweet data model"""
    tweet_id: str = Field(..., description="Unique tweet identifier")
    author: str = Field(..., description="Tweet author username")
    author_id: str = Field(..., description="Tweet author user ID")
    content: str = Field(..., description="Tweet text content")
    sentiment_score: float = Field(0.0, description="Sentiment score from -1 (negative) to 1 (positive)")
    created_at: datetime = Field(..., description="Tweet creation timestamp")
    engagement: Dict[str, int] = Field(
        default_factory=lambda: {"likes": 0, "retweets": 0, "replies": 0},
        description="Engagement metrics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tweet_id": "1234567890",
                "author": "techinfluencer",
                "author_id": "987654321",
                "content": "Excited about the new AI developments!",
                "sentiment_score": 0.85,
                "created_at": "2024-01-15T10:30:00Z",
                "engagement": {
                    "likes": 245,
                    "retweets": 67,
                    "replies": 12
                }
            }
        }


class Influencer(BaseModel):
    """Social media influencer data model"""
    username: str = Field(..., description="Influencer username")
    name: str = Field(..., description="Influencer display name")
    followers_count: int = Field(..., description="Number of followers")
    following_count: int = Field(0, description="Number of accounts following")
    influence_score: float = Field(..., description="Calculated influence score")
    topics: List[str] = Field(default_factory=list, description="Topics associated with influencer")
    recent_tweets: List[Tweet] = Field(default_factory=list, description="Recent tweets from influencer")
    verified: bool = Field(False, description="Whether account is verified")
    description: str = Field("", description="Profile description")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "aiprofessor",
                "name": "Dr. AI Expert",
                "followers_count": 150000,
                "following_count": 500,
                "influence_score": 75000.0,
                "topics": ["artificial intelligence", "machine learning"],
                "verified": True,
                "description": "AI researcher and educator",
                "recent_tweets": []
            }
        }


class TrendingTopic(BaseModel):
    """Trending topic data model"""
    topic: str = Field(..., description="Topic or hashtag")
    mention_count: int = Field(..., description="Number of mentions")
    sentiment_score: float = Field(0.0, description="Average sentiment score")
    top_tweets: List[Tweet] = Field(default_factory=list, description="Top tweets about topic")
    growth_rate: float = Field(0.0, description="Growth rate percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "#AI2024",
                "mention_count": 15000,
                "sentiment_score": 0.65,
                "growth_rate": 125.5,
                "top_tweets": []
            }
        }


class CompetitorMention(BaseModel):
    """Competitor mention tracking"""
    competitor_name: str = Field(..., description="Competitor company name")
    mention_count: int = Field(..., description="Number of mentions")
    sentiment_score: float = Field(0.0, description="Average sentiment")
    share_of_voice: float = Field(0.0, description="Share of voice percentage")
    trending_topics: List[str] = Field(default_factory=list, description="Associated trending topics")

    class Config:
        json_schema_extra = {
            "example": {
                "competitor_name": "CompetitorCo",
                "mention_count": 5000,
                "sentiment_score": 0.45,
                "share_of_voice": 35.2,
                "trending_topics": ["innovation", "product launch"]
            }
        }


class CrisisAlert(BaseModel):
    """Crisis detection alert"""
    alert_id: str = Field(..., description="Unique alert identifier")
    severity: str = Field(..., description="Alert severity: low, medium, high, critical")
    trigger_type: str = Field(..., description="What triggered the alert")
    description: str = Field(..., description="Alert description")
    sentiment_shift: float = Field(..., description="Magnitude of sentiment shift")
    affected_topics: List[str] = Field(default_factory=list, description="Topics affected")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Detection timestamp")
    requires_action: bool = Field(False, description="Whether immediate action is recommended")

    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "crisis_001",
                "severity": "high",
                "trigger_type": "negative_sentiment_spike",
                "description": "Sudden negative sentiment spike detected",
                "sentiment_shift": -0.65,
                "affected_topics": ["product quality", "customer service"],
                "detected_at": "2024-01-15T14:30:00Z",
                "requires_action": True
            }
        }


class SocialMediaInsight(BaseModel):
    """Comprehensive social media monitoring insight"""
    platform: str = Field(..., description="Social media platform (twitter, linkedin, reddit)")
    overall_sentiment: float = Field(..., description="Overall sentiment score (-1 to 1)")
    sentiment_label: str = Field(..., description="Sentiment label (positive, negative, neutral)")
    trending_topics: List[TrendingTopic] = Field(default_factory=list, description="Trending topics")
    top_influencers: List[Influencer] = Field(default_factory=list, description="Top influencers")
    crisis_alerts: List[CrisisAlert] = Field(default_factory=list, description="Active crisis alerts")
    competitor_mentions: Dict[str, CompetitorMention] = Field(
        default_factory=dict,
        description="Competitor mention tracking"
    )
    time_period: Dict[str, datetime] = Field(..., description="Analysis time period")
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metrics and statistics"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "twitter",
                "overall_sentiment": 0.55,
                "sentiment_label": "positive",
                "trending_topics": [],
                "top_influencers": [],
                "crisis_alerts": [],
                "competitor_mentions": {},
                "time_period": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-15T23:59:59Z"
                },
                "metrics": {
                    "total_tweets": 50000,
                    "engagement_rate": 4.5,
                    "reach": 2500000
                }
            }
        }


class RedditPost(BaseModel):
    """Reddit post data model"""
    post_id: str = Field(..., description="Unique post identifier")
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post text content (self posts only)")
    subreddit: str = Field(..., description="Subreddit name")
    author: str = Field(..., description="Post author username")
    score: int = Field(..., description="Net upvotes (upvotes - downvotes)")
    upvote_ratio: float = Field(..., description="Ratio of upvotes to total votes")
    num_comments: int = Field(..., description="Number of comments")
    created_at: datetime = Field(..., description="Post creation timestamp")
    url: str = Field(..., description="Post URL")
    sentiment_score: float = Field(0.0, description="Sentiment score from -1 to 1")
    is_self_post: bool = Field(True, description="Whether post is text-only")
    flair: Optional[str] = Field(None, description="Post flair text")
    awards: int = Field(0, description="Total awards received")

    class Config:
        json_schema_extra = {
            "example": {
                "post_id": "abc123",
                "title": "Discussion about AI technology",
                "content": "What are your thoughts on the latest AI developments?",
                "subreddit": "artificial",
                "author": "tech_enthusiast",
                "score": 542,
                "upvote_ratio": 0.92,
                "num_comments": 87,
                "created_at": "2024-01-15T10:30:00Z",
                "url": "https://reddit.com/r/artificial/comments/abc123",
                "sentiment_score": 0.75,
                "is_self_post": True,
                "flair": "Discussion",
                "awards": 3
            }
        }


class RedditComment(BaseModel):
    """Reddit comment data model"""
    comment_id: str = Field(..., description="Unique comment identifier")
    post_id: str = Field(..., description="Parent post ID")
    author: str = Field(..., description="Comment author username")
    content: str = Field(..., description="Comment text content")
    score: int = Field(..., description="Comment score")
    created_at: datetime = Field(..., description="Comment creation timestamp")
    depth: int = Field(..., description="Comment thread depth (0 = top-level)")
    sentiment_score: float = Field(0.0, description="Sentiment score from -1 to 1")
    parent_id: Optional[str] = Field(None, description="Parent comment ID")

    class Config:
        json_schema_extra = {
            "example": {
                "comment_id": "def456",
                "post_id": "abc123",
                "author": "ai_expert",
                "content": "I think the latest developments are promising...",
                "score": 42,
                "created_at": "2024-01-15T11:00:00Z",
                "depth": 0,
                "sentiment_score": 0.65,
                "parent_id": None
            }
        }


class TrendingSubreddit(BaseModel):
    """Trending subreddit data model"""
    name: str = Field(..., description="Subreddit name")
    subscriber_count: int = Field(..., description="Number of subscribers")
    active_users: int = Field(..., description="Currently active users")
    description: str = Field(..., description="Subreddit description")
    relevance_score: float = Field(..., description="Relevance score to search keywords")
    top_posts: List[RedditPost] = Field(default_factory=list, description="Top recent posts")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "artificial",
                "subscriber_count": 250000,
                "active_users": 3500,
                "description": "Artificial Intelligence and Machine Learning",
                "relevance_score": 0.85,
                "top_posts": []
            }
        }


class RedditInsight(BaseModel):
    """Reddit-specific monitoring insight"""
    subreddits_monitored: List[str] = Field(default_factory=list, description="Monitored subreddits")
    total_posts: int = Field(..., description="Total posts analyzed")
    total_comments: int = Field(..., description="Total comments analyzed")
    overall_sentiment: float = Field(..., description="Overall sentiment score")
    trending_topics: List[str] = Field(default_factory=list, description="Trending hashtags/topics")
    top_discussions: List[RedditPost] = Field(default_factory=list, description="Top discussion posts")
    community_sentiment: Dict[str, float] = Field(
        default_factory=dict,
        description="Sentiment by subreddit"
    )
    key_influencers: List[str] = Field(default_factory=list, description="Top contributing users")

    class Config:
        json_schema_extra = {
            "example": {
                "subreddits_monitored": ["artificial", "machinelearning", "technology"],
                "total_posts": 150,
                "total_comments": 450,
                "overall_sentiment": 0.62,
                "trending_topics": ["#GPT4", "#MachineLearning", "#OpenAI"],
                "top_discussions": [],
                "community_sentiment": {
                    "artificial": 0.65,
                    "machinelearning": 0.58,
                    "technology": 0.70
                },
                "key_influencers": ["ai_researcher", "ml_expert", "tech_guru"]
            }
        }


class SocialMediaMonitorRequest(BaseModel):
    """Request model for social media monitoring"""
    company: str = Field(..., description="Company to monitor")
    keywords: List[str] = Field(..., description="Keywords to track")
    competitors: List[str] = Field(default_factory=list, description="Competitor companies to track")
    platforms: List[str] = Field(default=["twitter", "reddit"], description="Platforms to monitor")
    subreddits: Optional[List[str]] = Field(None, description="Specific subreddits to monitor (Reddit)")
    monitoring_frequency: str = Field(default="daily", description="Monitoring frequency")
    alert_threshold: float = Field(default=0.3, description="Sentiment shift threshold for alerts")
    min_influencer_followers: int = Field(default=10000, description="Minimum followers for influencer tracking")
    use_grok: bool = Field(default=False, description="Use Grok API via laozhang.ai instead of Twitter API")

    class Config:
        json_schema_extra = {
            "example": {
                "company": "TechStartup Inc",
                "keywords": ["TechStartup", "#TechStartup", "@techstartup"],
                "competitors": ["CompetitorA", "CompetitorB"],
                "platforms": ["twitter"],
                "monitoring_frequency": "daily",
                "alert_threshold": 0.3,
                "min_influencer_followers": 10000
            }
        }


class SocialMediaMonitorResponse(BaseModel):
    """Response model for social media monitoring"""
    success: bool = Field(..., description="Whether monitoring was successful")
    insights: Optional[SocialMediaInsight] = Field(None, description="Social media insights")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "insights": {
                    "platform": "twitter",
                    "overall_sentiment": 0.55,
                    "sentiment_label": "positive",
                    "trending_topics": [],
                    "top_influencers": [],
                    "crisis_alerts": [],
                    "competitor_mentions": {},
                    "time_period": {
                        "start": "2024-01-01T00:00:00Z",
                        "end": "2024-01-15T23:59:59Z"
                    },
                    "metrics": {}
                },
                "error": None,
                "execution_time": 12.5
            }
        }


class NarrativeSignal(BaseModel):
    """Synthesized social narrative signal"""

    topic: str = Field(..., description="Topic or storyline being discussed")
    stance: str = Field(..., description="Supportive/Opposed/Neutral stance")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Average sentiment (-1 to 1)")
    share_of_voice: float = Field(..., ge=0.0, le=100.0, description="% of total conversations")
    momentum: str = Field(..., description="accelerating/cooling/stable")
    platforms: List[str] = Field(default_factory=list, description="Platforms contributing to the narrative")
    supporting_evidence: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Sample links, posts, or quotes"
    )
    strategic_implication: str = Field(..., description="Why this matters strategically")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score based on data coverage")


class InfluencerSignal(BaseModel):
    """Influencer stance worth watching"""

    handle: str = Field(..., description="Influencer or author handle")
    platform: str = Field(..., description="Platform e.g. twitter/reddit")
    reach: int = Field(..., description="Approximate follower/subscriber reach")
    influence_score: float = Field(..., description="Raw influence score from connector")
    stance: str = Field(..., description="Positive/Negative/Neutral stance")
    message: str = Field(..., description="Key takeaway from influencer content")
    link: Optional[str] = Field(None, description="Reference URL if available")


class SocialSignalSummary(BaseModel):
    """Aggregated social listening signals for reports"""

    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Blended sentiment score")
    sentiment_label: str = Field(..., description="positive/negative/neutral")
    momentum: str = Field(..., description="Tailwind/Headwind/Mixed momentum reading")
    reddit_volume: int = Field(0, description="Posts + comments analyzed")
    twitter_volume: int = Field(0, description="Tweets analyzed")
    narratives: List[NarrativeSignal] = Field(default_factory=list, description="Top community narratives")
    influencer_watchlist: List[InfluencerSignal] = Field(default_factory=list, description="Influencers to watch")
    risk_alerts: List[str] = Field(default_factory=list, description="Social-driven risks")
    opportunity_alerts: List[str] = Field(default_factory=list, description="Social-driven opportunities")
    supporting_posts: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Links to representative Reddit/Twitter content"
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of synthesis")

    class Config:
        json_schema_extra = {
            "example": {
                "sentiment_score": 0.32,
                "sentiment_label": "positive",
                "momentum": "Tailwind",
                "reddit_volume": 145,
                "twitter_volume": 320,
                "narratives": [
                    {
                        "topic": "AI copilots",
                        "stance": "supportive",
                        "sentiment_score": 0.58,
                        "share_of_voice": 34.5,
                        "momentum": "accelerating",
                        "platforms": ["twitter", "reddit"],
                        "supporting_evidence": [
                            {"platform": "reddit", "title": "Copilots double output", "url": "https://reddit.com/..."}
                        ],
                        "strategic_implication": "Users expect AI copilots baked into roadmap",
                        "confidence": 0.82
                    }
                ],
                "influencer_watchlist": [
                    {
                        "handle": "@aiexpert",
                        "platform": "twitter",
                        "reach": 150000,
                        "influence_score": 74500,
                        "stance": "critical",
                        "message": "Concerned about data privacy",
                        "link": "https://twitter.com/..."
                    }
                ],
                "risk_alerts": ["Privacy backlash brewing on r/privacy"],
                "opportunity_alerts": ["Creators demanding workflow automation partnerships"],
                "supporting_posts": [
                    {
                        "platform": "reddit",
                        "title": "Users love ConsultantOS dashboards",
                        "url": "https://reddit.com/r/...",
                        "sentiment": "0.71"
                    }
                ]
            }
        }
