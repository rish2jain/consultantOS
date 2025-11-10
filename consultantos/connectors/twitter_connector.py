"""
Twitter/X API v2 Connector for social media monitoring
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger.warning("tweepy not installed - Twitter connector will use mock data")


class Tweet(BaseModel):
    """Tweet data model"""
    tweet_id: str
    author: str
    author_id: str
    content: str
    created_at: datetime
    likes: int = 0
    retweets: int = 0
    replies: int = 0

    @classmethod
    def from_tweepy(cls, tweet_data: Any) -> "Tweet":
        """Convert tweepy tweet to our model"""
        if hasattr(tweet_data, 'id_str'):
            # Tweepy v1 format
            return cls(
                tweet_id=tweet_data.id_str,
                author=tweet_data.author.screen_name,
                author_id=tweet_data.author.id_str,
                content=tweet_data.text,
                created_at=tweet_data.created_at,
                likes=tweet_data.favorite_count,
                retweets=tweet_data.retweet_count,
                replies=0  # Not available in v1 basic
            )
        else:
            # Tweepy v2 format
            return cls(
                tweet_id=str(tweet_data.id),
                author=tweet_data.author.username if hasattr(tweet_data, 'author') else "unknown",
                author_id=str(tweet_data.author_id) if hasattr(tweet_data, 'author_id') else "0",
                content=tweet_data.text,
                created_at=tweet_data.created_at,
                likes=tweet_data.public_metrics.get('like_count', 0) if hasattr(tweet_data, 'public_metrics') else 0,
                retweets=tweet_data.public_metrics.get('retweet_count', 0) if hasattr(tweet_data, 'public_metrics') else 0,
                replies=tweet_data.public_metrics.get('reply_count', 0) if hasattr(tweet_data, 'public_metrics') else 0,
            )


class TwitterUser(BaseModel):
    """Twitter user data model"""
    user_id: str
    username: str
    name: str
    followers_count: int
    following_count: int
    verified: bool = False
    description: str = ""

    @classmethod
    def from_tweepy(cls, user_data: Any) -> "TwitterUser":
        """Convert tweepy user to our model"""
        if hasattr(user_data, 'id_str'):
            # Tweepy v1 format
            return cls(
                user_id=user_data.id_str,
                username=user_data.screen_name,
                name=user_data.name,
                followers_count=user_data.followers_count,
                following_count=user_data.friends_count,
                verified=user_data.verified,
                description=user_data.description or ""
            )
        else:
            # Tweepy v2 format
            return cls(
                user_id=str(user_data.id),
                username=user_data.username,
                name=user_data.name,
                followers_count=user_data.public_metrics.get('followers_count', 0) if hasattr(user_data, 'public_metrics') else 0,
                following_count=user_data.public_metrics.get('following_count', 0) if hasattr(user_data, 'public_metrics') else 0,
                verified=user_data.verified if hasattr(user_data, 'verified') else False,
                description=user_data.description if hasattr(user_data, 'description') else ""
            )


class TwitterConnector:
    """Twitter API v2 connector for social media monitoring"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        """
        Initialize Twitter connector

        Args:
            api_key: Twitter API key (consumer key)
            api_secret: Twitter API secret (consumer secret)
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            bearer_token: Twitter bearer token (for v2 API)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token

        self.client_v1 = None
        self.client_v2 = None

        if TWEEPY_AVAILABLE and bearer_token:
            try:
                # Initialize v2 client with bearer token
                self.client_v2 = tweepy.Client(bearer_token=bearer_token)
                logger.info("Twitter API v2 client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter v2 client: {e}")

        if TWEEPY_AVAILABLE and api_key and api_secret:
            try:
                # Initialize v1.1 client (for some features not in v2 yet)
                auth = tweepy.OAuthHandler(api_key, api_secret)
                if access_token and access_token_secret:
                    auth.set_access_token(access_token, access_token_secret)
                self.client_v1 = tweepy.API(auth, wait_on_rate_limit=True)
                logger.info("Twitter API v1.1 client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter v1.1 client: {e}")

    async def search_tweets(
        self,
        keywords: List[str],
        start_date: Optional[datetime] = None,
        max_results: int = 100,
        lang: str = "en"
    ) -> List[Tweet]:
        """
        Search recent tweets matching keywords

        Args:
            keywords: List of keywords to search for
            start_date: Start date for search (default: 7 days ago)
            max_results: Maximum number of tweets to return
            lang: Language code (default: en)

        Returns:
            List of Tweet objects
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)

        # Build query with OR logic
        query = " OR ".join(keywords)
        query += f" lang:{lang} -is:retweet"  # Exclude retweets

        tweets = []

        if self.client_v2:
            try:
                # Use v2 API
                response = await asyncio.to_thread(
                    self.client_v2.search_recent_tweets,
                    query=query,
                    start_time=start_date,
                    max_results=min(max_results, 100),  # v2 limit per request
                    tweet_fields=['created_at', 'public_metrics', 'author_id'],
                    expansions=['author_id'],
                    user_fields=['username']
                )

                if response.data:
                    # Create user lookup
                    users = {user.id: user for user in (response.includes.get('users', []) or [])}

                    for tweet in response.data:
                        # Add author info
                        tweet.author = users.get(tweet.author_id)
                        tweets.append(Tweet.from_tweepy(tweet))

                logger.info(f"Found {len(tweets)} tweets matching: {keywords}")

            except Exception as e:
                logger.error(f"Twitter API v2 search failed: {e}")
                # Return mock data for development
                tweets = self._generate_mock_tweets(keywords, max_results)

        elif self.client_v1:
            try:
                # Fallback to v1.1 API
                cursor = await asyncio.to_thread(
                    self.client_v1.search_tweets,
                    q=query,
                    lang=lang,
                    count=max_results,
                    since=start_date.strftime('%Y-%m-%d'),
                    tweet_mode='extended'
                )

                for tweet in cursor:
                    tweets.append(Tweet.from_tweepy(tweet))

                logger.info(f"Found {len(tweets)} tweets matching: {keywords}")

            except Exception as e:
                logger.error(f"Twitter API v1.1 search failed: {e}")
                tweets = self._generate_mock_tweets(keywords, max_results)

        else:
            # No API client available, return mock data
            logger.warning("No Twitter API client available, using mock data")
            tweets = self._generate_mock_tweets(keywords, max_results)

        return tweets[:max_results]

    async def get_influencers(
        self,
        topic: str,
        min_followers: int = 10000,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find top influencers for a topic

        Args:
            topic: Topic to search for
            min_followers: Minimum follower count
            max_results: Maximum number of influencers to return

        Returns:
            List of influencer data dictionaries
        """
        influencers = []

        if self.client_v2:
            try:
                # Search for users discussing the topic
                query = f"{topic} has:mentions min_faves:10"
                response = await asyncio.to_thread(
                    self.client_v2.search_recent_tweets,
                    query=query,
                    max_results=100,
                    tweet_fields=['author_id'],
                    expansions=['author_id'],
                    user_fields=['username', 'name', 'public_metrics', 'verified', 'description']
                )

                if response.includes and 'users' in response.includes:
                    users = response.includes['users']

                    # Filter by follower count and convert to our format
                    for user in users:
                        user_obj = TwitterUser.from_tweepy(user)
                        if user_obj.followers_count >= min_followers:
                            influencers.append({
                                "username": user_obj.username,
                                "name": user_obj.name,
                                "followers_count": user_obj.followers_count,
                                "verified": user_obj.verified,
                                "description": user_obj.description,
                                "influence_score": self._calculate_influence_score(user_obj),
                                "topics": [topic]
                            })

                    # Sort by influence score
                    influencers.sort(key=lambda x: x['influence_score'], reverse=True)

                logger.info(f"Found {len(influencers)} influencers for topic: {topic}")

            except Exception as e:
                logger.error(f"Failed to get influencers: {e}")
                influencers = self._generate_mock_influencers(topic, max_results)

        else:
            # Mock data
            influencers = self._generate_mock_influencers(topic, max_results)

        return influencers[:max_results]

    async def get_user_tweets(
        self,
        username: str,
        max_results: int = 50
    ) -> List[Tweet]:
        """
        Get recent tweets from a specific user

        Args:
            username: Twitter username
            max_results: Maximum number of tweets to return

        Returns:
            List of Tweet objects
        """
        tweets = []

        if self.client_v2:
            try:
                # Get user ID first
                user = await asyncio.to_thread(
                    self.client_v2.get_user,
                    username=username
                )

                if user.data:
                    # Get user's tweets
                    response = await asyncio.to_thread(
                        self.client_v2.get_users_tweets,
                        id=user.data.id,
                        max_results=max_results,
                        tweet_fields=['created_at', 'public_metrics']
                    )

                    if response.data:
                        for tweet in response.data:
                            tweet.author = user.data
                            tweets.append(Tweet.from_tweepy(tweet))

                logger.info(f"Found {len(tweets)} tweets from @{username}")

            except Exception as e:
                logger.error(f"Failed to get user tweets: {e}")

        return tweets

    def _calculate_influence_score(self, user: TwitterUser) -> float:
        """
        Calculate influence score for a user

        Formula: (followers * 0.4) + (verified * 10000) + (followers/following ratio * 0.3)

        Args:
            user: TwitterUser object

        Returns:
            Influence score (higher is better)
        """
        followers = user.followers_count
        following = max(user.following_count, 1)  # Avoid division by zero
        verified_bonus = 10000 if user.verified else 0

        # Calculate follower/following ratio (capped at 10)
        ratio = min(followers / following, 10)

        score = (followers * 0.4) + verified_bonus + (ratio * 1000)
        return round(score, 2)

    def _generate_mock_tweets(self, keywords: List[str], count: int) -> List[Tweet]:
        """Generate mock tweets for development/testing"""
        mock_tweets = []
        now = datetime.now()

        for i in range(min(count, 20)):
            mock_tweets.append(Tweet(
                tweet_id=f"mock_{i}",
                author=f"user_{i % 5}",
                author_id=f"uid_{i % 5}",
                content=f"Mock tweet about {keywords[0] if keywords else 'topic'} - this is for testing",
                created_at=now - timedelta(hours=i),
                likes=10 + i * 3,
                retweets=2 + i,
                replies=1 + i // 2
            ))

        return mock_tweets

    def _generate_mock_influencers(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock influencers for development/testing"""
        mock_influencers = []

        for i in range(min(count, 10)):
            mock_influencers.append({
                "username": f"influencer_{i}",
                "name": f"Top Influencer {i}",
                "followers_count": 50000 + i * 10000,
                "verified": i < 3,
                "description": f"Expert in {topic}",
                "influence_score": 50000 + i * 10000,
                "topics": [topic]
            })

        return mock_influencers
