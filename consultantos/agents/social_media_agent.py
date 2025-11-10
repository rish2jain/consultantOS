"""
Social Media Intelligence Agent for Twitter and Reddit monitoring and sentiment analysis
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
from collections import defaultdict

from consultantos.agents.base_agent import BaseAgent
from consultantos.connectors.twitter_connector import TwitterConnector
from consultantos.connectors.reddit_connector import RedditConnector
from consultantos.connectors.grok_connector import GrokConnector
from consultantos.analytics.sentiment_analyzer import SentimentAnalyzer
from consultantos.models.social_media import (
    SocialMediaInsight,
    TrendingTopic,
    Influencer,
    CrisisAlert,
    CompetitorMention,
    Tweet,
    RedditPost,
    RedditComment,
    TrendingSubreddit,
    RedditInsight
)

logger = logging.getLogger(__name__)


class SocialMediaAgent(BaseAgent):
    """
    Social Media Intelligence Agent

    Monitors Twitter/X and Reddit for:
    - Brand mentions and sentiment
    - Competitor tracking
    - Influencer identification
    - Trending topics
    - Crisis detection (negative sentiment spikes)
    - Community sentiment analysis (Reddit)
    """

    def __init__(
        self,
        twitter_api_key: Optional[str] = None,
        twitter_api_secret: Optional[str] = None,
        twitter_bearer_token: Optional[str] = None,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None,
        reddit_user_agent: str = "ConsultantOS:v1.0 (by /u/consultantos)",
        laozhang_api_key: Optional[str] = None,
        use_grok: bool = False,
        sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english",
        timeout: int = 120
    ):
        """
        Initialize Social Media Agent

        Args:
            twitter_api_key: Twitter API key
            twitter_api_secret: Twitter API secret
            twitter_bearer_token: Twitter bearer token for v2 API
            reddit_client_id: Reddit app client ID
            reddit_client_secret: Reddit app client secret
            reddit_user_agent: User agent for Reddit API
            laozhang_api_key: Laozhang.ai API key for Grok access
            use_grok: Whether to use Grok instead of Twitter API (default: False)
            sentiment_model: HuggingFace model for sentiment analysis
            timeout: Agent timeout in seconds
        """
        super().__init__(name="SocialMediaAgent", timeout=timeout)

        # Initialize Twitter connector
        self.twitter = TwitterConnector(
            api_key=twitter_api_key,
            api_secret=twitter_api_secret,
            bearer_token=twitter_bearer_token
        )

        # Initialize Reddit connector
        self.reddit = RedditConnector(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent=reddit_user_agent
        )

        # Initialize Grok connector (optional)
        self.grok = None
        self.use_grok = use_grok
        if laozhang_api_key:
            try:
                from consultantos.config import settings
                grok_model = getattr(settings, 'laozhang_model', 'grok-4-fast-reasoning-latest')
                self.grok = GrokConnector(
                    api_key=laozhang_api_key,
                    model=grok_model,
                    timeout=min(timeout, 90)  # Grok needs more time
                )
                logger.info(f"Grok connector initialized with model: {grok_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize Grok connector: {e}")

        # Initialize sentiment analyzer
        self.sentiment_analyzer = SentimentAnalyzer(model_name=sentiment_model)

        if use_grok and self.grok:
            logger.info("SocialMediaAgent initialized with Grok (via laozhang.ai) and Reddit support")
        else:
            logger.info("SocialMediaAgent initialized with Twitter and Reddit support")

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute social media monitoring

        Args:
            input_data: Dict with:
                - company: Company name to monitor
                - keywords: List of keywords to track
                - competitors: List of competitor names (optional)
                - days_back: Days of history to analyze (default: 7)
                - min_influencer_followers: Minimum followers for influencer tracking
                - alert_threshold: Sentiment shift threshold for alerts

        Returns:
            Dict with:
                - success: bool
                - data: SocialMediaInsight object
                - error: str (if failed)
        """
        start_time = time.time()

        try:
            # Extract parameters
            company = input_data.get("company", "")
            keywords = input_data.get("keywords", [company])
            competitors = input_data.get("competitors", [])
            days_back = input_data.get("days_back", 7)
            min_followers = input_data.get("min_influencer_followers", 10000)
            alert_threshold = input_data.get("alert_threshold", 0.3)

            if not keywords:
                keywords = [company]

            logger.info(
                f"Monitoring social media for {company}",
                extra={
                    "keywords": keywords,
                    "competitors": competitors,
                    "days_back": days_back
                }
            )

            # Calculate time period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            # Check if we should use Grok instead of Twitter
            use_grok = input_data.get("use_grok", self.use_grok)
            
            if use_grok and self.grok:
                # Use Grok for sentiment analysis
                return await self._execute_with_grok(
                    company=company,
                    keywords=keywords,
                    competitors=competitors,
                    days_back=days_back,
                    min_followers=min_followers,
                    alert_threshold=alert_threshold,
                    start_date=start_date,
                    end_date=end_date
                )

            # 1. Search and analyze tweets
            logger.info("Searching tweets...")
            tweets = await self.twitter.search_tweets(
                keywords=keywords,
                start_date=start_date,
                max_results=200
            )

            logger.info(f"Found {len(tweets)} tweets")

            # 2. Analyze sentiment
            logger.info("Analyzing sentiment...")
            tweet_dicts = [tweet.model_dump() for tweet in tweets]
            enriched_tweets = await self.sentiment_analyzer.analyze_tweets(tweet_dicts)

            # 3. Calculate overall sentiment
            sentiments = [t['sentiment'] for t in enriched_tweets]
            overall_sentiment = self.sentiment_analyzer.aggregate_sentiment(sentiments)

            # 4. Identify trending topics
            logger.info("Identifying trending topics...")
            trending_topics = self._identify_trending_topics(enriched_tweets)

            # 5. Find influencers
            logger.info("Finding influencers...")
            influencers = await self._find_influencers(
                keywords=keywords,
                min_followers=min_followers
            )

            # 6. Track competitor mentions
            logger.info("Tracking competitor mentions...")
            competitor_mentions = {}
            if competitors:
                competitor_mentions = await self._track_competitors(
                    competitors=competitors,
                    start_date=start_date,
                    total_mentions=len(tweets)
                )

            # 7. Detect crises
            logger.info("Detecting potential crises...")
            crisis_alerts = self._detect_crises(
                enriched_tweets=enriched_tweets,
                threshold=alert_threshold
            )

            # 8. Calculate metrics
            metrics = self._calculate_metrics(enriched_tweets)

            # 9. Create insight object
            insight = SocialMediaInsight(
                platform="twitter",
                overall_sentiment=overall_sentiment['mean_score'],
                sentiment_label=overall_sentiment['overall_label'],
                trending_topics=trending_topics,
                top_influencers=influencers,
                crisis_alerts=crisis_alerts,
                competitor_mentions=competitor_mentions,
                time_period={
                    "start": start_date,
                    "end": end_date
                },
                metrics=metrics
            )

            execution_time = time.time() - start_time

            logger.info(
                f"Social media monitoring completed in {execution_time:.2f}s",
                extra={
                    "overall_sentiment": overall_sentiment['mean_score'],
                    "trending_topics_count": len(trending_topics),
                    "influencers_count": len(influencers),
                    "crisis_alerts": len(crisis_alerts)
                }
            )

            return {
                "success": True,
                "data": insight,
                "error": None
            }

        except Exception as e:
            logger.error(f"Social media monitoring failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    async def _execute_with_grok(
        self,
        company: str,
        keywords: List[str],
        competitors: List[str],
        days_back: int,
        min_followers: int,
        alert_threshold: float,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Execute social media monitoring using Grok API

        Args:
            company: Company name
            keywords: Keywords to track
            competitors: Competitor names
            days_back: Days of history
            min_followers: Min followers for influencers
            alert_threshold: Sentiment shift threshold
            start_date: Analysis start date
            end_date: Analysis end date

        Returns:
            Dict with success, data, and error
        """
        start_time = time.time()
        try:
            logger.info(f"Using Grok for sentiment analysis of {company}")

            # 1. Get sentiment analysis from Grok
            grok_result = await self.grok.analyze_sentiment(
                company=company,
                keywords=keywords,
                days_back=days_back,
                competitors=competitors if competitors else None
            )

            # 2. Convert Grok result to our format
            overall_sentiment_score = grok_result.get("overall_sentiment", 0.0)
            sentiment_label = grok_result.get("sentiment_label", "neutral")

            # 3. Convert trending topics
            trending_topics = []
            for i, topic in enumerate(grok_result.get("trending_topics", [])[:5]):
                trending_topics.append(
                    TrendingTopic(
                        topic=topic,
                        mention_count=5 - i,  # Approximate ranking
                        sentiment_score=overall_sentiment_score
                    )
                )

            # 4. Convert influencers
            influencers = []
            grok_influencers = grok_result.get("key_influencers", [])
            for inf in grok_influencers[:10]:
                if isinstance(inf, str):
                    # If it's just a username string
                    username = inf.replace("@", "")
                    influencers.append(
                        Influencer(
                            username=username,
                            name=username,
                            followers_count=min_followers,  # Grok doesn't provide exact counts
                            verified=False,
                            description="",
                            influence_score=1000.0,
                            topics=keywords
                        )
                    )
                elif isinstance(inf, dict):
                    # If it's a dict with more info
                    influencers.append(
                        Influencer(
                            username=inf.get("username", "").replace("@", ""),
                            name=inf.get("name", inf.get("username", "")),
                            followers_count=inf.get("followers_count", min_followers),
                            verified=inf.get("verified", False),
                            description=inf.get("description", ""),
                            influence_score=inf.get("influence_score", 1000.0),
                            topics=inf.get("topics", keywords)
                        )
                    )

            # 5. Create crisis alerts if negative sentiment
            crisis_alerts = []
            crisis_text = grok_result.get("crisis_alerts", "")
            if crisis_text and overall_sentiment_score < -alert_threshold:
                crisis_alerts.append(
                    CrisisAlert(
                        alert_type="negative_sentiment",
                        severity="high" if overall_sentiment_score < -0.5 else "medium",
                        description=crisis_text,
                        detected_at=end_date,
                        affected_keywords=keywords[:3]
                    )
                )

            # 6. Track competitor mentions
            competitor_mentions = {}
            competitor_text = grok_result.get("competitor_mentions", "")
            if competitor_text and competitors:
                for competitor in competitors:
                    if competitor.lower() in competitor_text.lower():
                        competitor_mentions[competitor] = CompetitorMention(
                            competitor_name=competitor,
                            mention_count=1,  # Approximate
                            sentiment_score=0.0,
                            context=competitor_text
                        )

            # 7. Calculate metrics
            metrics = {
                "total_mentions": "N/A (Grok analysis)",
                "sentiment_breakdown": grok_result.get("sentiment_breakdown", {}),
                "key_themes": grok_result.get("key_themes", []),
                "summary": grok_result.get("summary", ""),
                "data_source": "grok-via-laozhang",
                "analysis_method": "grok-4-all"
            }

            # 8. Create insight object
            insight = SocialMediaInsight(
                platform="grok",  # Use "grok" as platform identifier
                overall_sentiment=overall_sentiment_score,
                sentiment_label=sentiment_label,
                trending_topics=trending_topics,
                top_influencers=influencers,
                crisis_alerts=crisis_alerts,
                competitor_mentions=competitor_mentions,
                time_period={
                    "start": start_date,
                    "end": end_date
                },
                metrics=metrics
            )

            execution_time = time.time() - start_time

            logger.info(
                f"Grok sentiment analysis completed in {execution_time:.2f}s",
                extra={
                    "overall_sentiment": overall_sentiment_score,
                    "trending_topics_count": len(trending_topics),
                    "influencers_count": len(influencers),
                    "crisis_alerts": len(crisis_alerts)
                }
            )

            return {
                "success": True,
                "data": insight,
                "error": None
            }

        except Exception as e:
            logger.error(f"Grok sentiment analysis failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _identify_trending_topics(
        self,
        enriched_tweets: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[TrendingTopic]:
        """
        Identify trending topics from tweets

        Args:
            enriched_tweets: List of tweets with sentiment data
            top_n: Number of top topics to return

        Returns:
            List of TrendingTopic objects
        """
        # Extract hashtags and keywords
        topic_tweets = defaultdict(list)

        for tweet in enriched_tweets:
            content = tweet.get('content', '')

            # Extract hashtags
            words = content.split()
            for word in words:
                if word.startswith('#'):
                    topic = word.lower()
                    topic_tweets[topic].append(tweet)

        # Calculate topic statistics
        trending = []
        for topic, topic_tweet_list in topic_tweets.items():
            if len(topic_tweet_list) < 3:  # Minimum threshold
                continue

            # Calculate average sentiment
            sentiments = [t['sentiment']['sentiment_score'] for t in topic_tweet_list]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

            # Get top tweets
            sorted_tweets = sorted(
                topic_tweet_list,
                key=lambda t: t.get('engagement', {}).get('likes', 0),
                reverse=True
            )[:3]

            top_tweets = [
                Tweet(
                    tweet_id=t.get('tweet_id', ''),
                    author=t.get('author', ''),
                    author_id=t.get('author_id', ''),
                    content=t.get('content', ''),
                    sentiment_score=t.get('sentiment_score', 0.0),
                    created_at=t.get('created_at', datetime.now()),
                    engagement=t.get('engagement', {})
                )
                for t in sorted_tweets
            ]

            trending.append(TrendingTopic(
                topic=topic,
                mention_count=len(topic_tweet_list),
                sentiment_score=round(avg_sentiment, 3),
                top_tweets=top_tweets,
                growth_rate=0.0  # Would need historical data
            ))

        # Sort by mention count
        trending.sort(key=lambda t: t.mention_count, reverse=True)

        return trending[:top_n]

    async def _find_influencers(
        self,
        keywords: List[str],
        min_followers: int = 10000,
        max_results: int = 10
    ) -> List[Influencer]:
        """
        Find top influencers discussing keywords

        Args:
            keywords: Keywords to search for
            min_followers: Minimum follower count
            max_results: Maximum number of influencers to return

        Returns:
            List of Influencer objects
        """
        influencers_data = []

        for keyword in keywords[:3]:  # Limit to avoid rate limits
            try:
                keyword_influencers = await self.twitter.get_influencers(
                    topic=keyword,
                    min_followers=min_followers,
                    max_results=max_results
                )
                influencers_data.extend(keyword_influencers)
            except Exception as e:
                logger.warning(f"Failed to get influencers for {keyword}: {e}")

        # Remove duplicates and sort by influence score
        unique_influencers = {}
        for inf in influencers_data:
            username = inf['username']
            if username not in unique_influencers:
                unique_influencers[username] = inf

        sorted_influencers = sorted(
            unique_influencers.values(),
            key=lambda x: x['influence_score'],
            reverse=True
        )

        # Convert to Influencer objects
        result = []
        for inf_data in sorted_influencers[:max_results]:
            result.append(Influencer(
                username=inf_data['username'],
                name=inf_data.get('name', inf_data['username']),
                followers_count=inf_data['followers_count'],
                influence_score=inf_data['influence_score'],
                topics=inf_data.get('topics', []),
                verified=inf_data.get('verified', False),
                description=inf_data.get('description', ''),
                recent_tweets=[]
            ))

        return result

    async def _track_competitors(
        self,
        competitors: List[str],
        start_date: datetime,
        total_mentions: int
    ) -> Dict[str, CompetitorMention]:
        """
        Track competitor mentions and sentiment

        Args:
            competitors: List of competitor names
            start_date: Start date for search
            total_mentions: Total mentions for share of voice calculation

        Returns:
            Dict mapping competitor name to CompetitorMention
        """
        competitor_data = {}

        for competitor in competitors:
            try:
                # Search competitor tweets
                tweets = await self.twitter.search_tweets(
                    keywords=[competitor],
                    start_date=start_date,
                    max_results=100
                )

                if not tweets:
                    continue

                # Analyze sentiment
                tweet_dicts = [tweet.model_dump() for tweet in tweets]
                enriched = await self.sentiment_analyzer.analyze_tweets(tweet_dicts)

                # Calculate metrics
                sentiments = [t['sentiment']['sentiment_score'] for t in enriched]
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

                # Extract topics
                topics = set()
                for tweet in enriched:
                    content = tweet.get('content', '')
                    words = content.split()
                    for word in words:
                        if word.startswith('#'):
                            topics.add(word.lower())

                # Calculate share of voice
                share_of_voice = (len(tweets) / max(total_mentions, 1)) * 100

                competitor_data[competitor] = CompetitorMention(
                    competitor_name=competitor,
                    mention_count=len(tweets),
                    sentiment_score=round(avg_sentiment, 3),
                    share_of_voice=round(share_of_voice, 2),
                    trending_topics=list(topics)[:5]
                )

            except Exception as e:
                logger.warning(f"Failed to track competitor {competitor}: {e}")

        return competitor_data

    def _detect_crises(
        self,
        enriched_tweets: List[Dict[str, Any]],
        threshold: float = 0.3
    ) -> List[CrisisAlert]:
        """
        Detect potential crises from sentiment patterns

        Args:
            enriched_tweets: Tweets with sentiment data
            threshold: Sentiment shift threshold for alert

        Returns:
            List of CrisisAlert objects
        """
        alerts = []

        if len(enriched_tweets) < 10:
            return alerts  # Not enough data

        # Split into time periods
        sorted_tweets = sorted(
            enriched_tweets,
            key=lambda t: t.get('created_at', datetime.now())
        )

        mid_point = len(sorted_tweets) // 2
        earlier_tweets = sorted_tweets[:mid_point]
        recent_tweets = sorted_tweets[mid_point:]

        # Calculate sentiment for each period
        earlier_sentiments = [t['sentiment'] for t in earlier_tweets]
        recent_sentiments = [t['sentiment'] for t in recent_tweets]

        earlier_agg = self.sentiment_analyzer.aggregate_sentiment(earlier_sentiments)
        recent_agg = self.sentiment_analyzer.aggregate_sentiment(recent_sentiments)

        # Detect shift
        shift_analysis = self.sentiment_analyzer.detect_sentiment_shift(
            current_sentiment=recent_agg,
            previous_sentiment=earlier_agg,
            threshold=threshold
        )

        # Create alert if crisis detected
        if shift_analysis['is_crisis']:
            severity = self._calculate_severity(shift_analysis['shift_magnitude'])

            # Extract affected topics
            negative_tweets = [
                t for t in recent_tweets
                if t['sentiment']['sentiment_score'] < -0.3
            ]

            affected_topics = set()
            for tweet in negative_tweets[:10]:
                content = tweet.get('content', '')
                words = content.split()
                for word in words:
                    if word.startswith('#'):
                        affected_topics.add(word.lower())

            alert = CrisisAlert(
                alert_id=f"crisis_{int(datetime.now().timestamp())}",
                severity=severity,
                trigger_type="negative_sentiment_spike",
                description=f"Detected {abs(shift_analysis['shift_magnitude']):.2f} negative sentiment shift",
                sentiment_shift=shift_analysis['shift_magnitude'],
                affected_topics=list(affected_topics)[:5],
                detected_at=datetime.now(),
                requires_action=severity in ['high', 'critical']
            )

            alerts.append(alert)

        return alerts

    def _calculate_severity(self, shift_magnitude: float) -> str:
        """Calculate alert severity based on shift magnitude"""
        abs_shift = abs(shift_magnitude)

        if abs_shift >= 0.7:
            return "critical"
        elif abs_shift >= 0.5:
            return "high"
        elif abs_shift >= 0.3:
            return "medium"
        else:
            return "low"

    def _calculate_metrics(self, enriched_tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate additional metrics

        Args:
            enriched_tweets: Tweets with sentiment data

        Returns:
            Dict of metrics
        """
        if not enriched_tweets:
            return {
                "total_tweets": 0,
                "engagement_rate": 0.0,
                "reach": 0,
                "avg_likes": 0.0,
                "avg_retweets": 0.0
            }

        total_tweets = len(enriched_tweets)

        # Calculate engagement metrics
        total_likes = sum(t.get('engagement', {}).get('likes', 0) for t in enriched_tweets)
        total_retweets = sum(t.get('engagement', {}).get('retweets', 0) for t in enriched_tweets)
        total_replies = sum(t.get('engagement', {}).get('replies', 0) for t in enriched_tweets)

        total_engagement = total_likes + total_retweets + total_replies
        engagement_rate = (total_engagement / total_tweets) if total_tweets > 0 else 0.0

        # Estimate reach (simplified)
        reach = total_retweets * 100  # Each retweet reaches ~100 people (rough estimate)

        return {
            "total_tweets": total_tweets,
            "engagement_rate": round(engagement_rate, 2),
            "reach": reach,
            "avg_likes": round(total_likes / total_tweets, 2),
            "avg_retweets": round(total_retweets / total_tweets, 2),
            "total_likes": total_likes,
            "total_retweets": total_retweets,
            "total_replies": total_replies
        }

    async def _analyze_reddit(
        self,
        keywords: List[str],
        subreddits: Optional[List[str]] = None,
        days_back: int = 7
    ) -> RedditInsight:
        """
        Analyze Reddit for keywords and subreddits

        Args:
            keywords: Keywords to search for
            subreddits: Specific subreddits to monitor (None = search all)
            days_back: Days of history to analyze

        Returns:
            RedditInsight object with analysis results
        """
        logger.info("Analyzing Reddit...")

        # Calculate time filter
        time_filter = "week"
        if days_back <= 1:
            time_filter = "day"
        elif days_back <= 7:
            time_filter = "week"
        elif days_back <= 30:
            time_filter = "month"
        else:
            time_filter = "year"

        # 1. Search posts
        posts_data = await self.reddit.search_posts(
            keywords=keywords,
            subreddits=subreddits,
            time_filter=time_filter,
            limit=100
        )

        logger.info(f"Found {len(posts_data)} Reddit posts")

        # 2. Convert to RedditPost objects and analyze sentiment
        posts = []
        all_content = []

        for post_data in posts_data:
            # Analyze sentiment
            content = f"{post_data['title']} {post_data['content']}"
            if content.strip():
                all_content.append({'content': content, 'post_data': post_data})

        # Batch sentiment analysis
        if all_content:
            analyzed = await self.sentiment_analyzer.analyze_tweets(
                [{'content': item['content']} for item in all_content]
            )

            for i, item in enumerate(all_content):
                sentiment_score = analyzed[i]['sentiment']['sentiment_score']
                post_data = item['post_data']
                post_data['sentiment_score'] = sentiment_score

                posts.append(RedditPost(**post_data))

        # 3. Calculate overall sentiment
        sentiments = [p.sentiment_score for p in posts]
        overall_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

        # 4. Extract trending topics (hashtags and keywords)
        trending_topics = self._extract_reddit_topics(posts)

        # 5. Get top discussions (highest engagement)
        top_discussions = sorted(
            posts,
            key=lambda p: p.score + (p.num_comments * 2),  # Weight comments higher
            reverse=True
        )[:10]

        # 6. Calculate sentiment by subreddit
        community_sentiment = defaultdict(list)
        for post in posts:
            community_sentiment[post.subreddit].append(post.sentiment_score)

        community_sentiment_avg = {
            subreddit: round(sum(scores) / len(scores), 3)
            for subreddit, scores in community_sentiment.items()
        }

        # 7. Identify key influencers (most active posters)
        author_counts = defaultdict(int)
        for post in posts:
            if post.author != '[deleted]':
                author_counts[post.author] += 1

        key_influencers = [
            author for author, _ in
            sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        # 8. Analyze sample comments for deeper insights
        total_comments = 0
        if posts:
            # Analyze comments from top 5 posts
            for post in top_discussions[:5]:
                try:
                    comments = await self.reddit.analyze_comments(
                        post_id=post.post_id,
                        max_depth=2,
                        limit=20
                    )
                    total_comments += len(comments)

                    # Analyze comment sentiment
                    for comment_data in comments:
                        if comment_data['content'].strip():
                            analyzed = await self.sentiment_analyzer.analyze_tweets(
                                [{'content': comment_data['content']}]
                            )
                            comment_data['sentiment_score'] = analyzed[0]['sentiment']['sentiment_score']

                except Exception as e:
                    logger.warning(f"Failed to analyze comments for post {post.post_id}: {e}")

        # Create insight
        insight = RedditInsight(
            subreddits_monitored=subreddits or ['all'],
            total_posts=len(posts),
            total_comments=total_comments,
            overall_sentiment=round(overall_sentiment, 3),
            trending_topics=trending_topics,
            top_discussions=top_discussions,
            community_sentiment=community_sentiment_avg,
            key_influencers=key_influencers
        )

        logger.info(
            f"Reddit analysis complete: {len(posts)} posts, {total_comments} comments, "
            f"sentiment: {overall_sentiment:.3f}"
        )

        return insight

    def _extract_reddit_topics(self, posts: List[RedditPost]) -> List[str]:
        """
        Extract trending topics from Reddit posts

        Args:
            posts: List of RedditPost objects

        Returns:
            List of trending topic strings
        """
        # Count hashtags and common keywords
        topic_counts = defaultdict(int)

        for post in posts:
            # Extract from title
            words = post.title.split()
            for word in words:
                if word.startswith('#'):
                    topic_counts[word.lower()] += 1

            # Extract from content
            if post.content:
                words = post.content.split()
                for word in words:
                    if word.startswith('#'):
                        topic_counts[word.lower()] += 1

            # Include flair as topic
            if post.flair:
                topic_counts[f"[{post.flair}]"] += 1

        # Sort by frequency
        sorted_topics = sorted(
            topic_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top 10
        return [topic for topic, _ in sorted_topics[:10]]
