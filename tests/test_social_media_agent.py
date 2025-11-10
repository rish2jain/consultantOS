"""
Tests for Social Media Intelligence Agent
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from consultantos.agents.social_media_agent import SocialMediaAgent
from consultantos.connectors.twitter_connector import TwitterConnector, Tweet, TwitterUser
from consultantos.analytics.sentiment_analyzer import SentimentAnalyzer
from consultantos.models.social_media import (
    SocialMediaInsight,
    TrendingTopic,
    Influencer,
    CrisisAlert,
    CompetitorMention
)


# Mock data fixtures
@pytest.fixture
def mock_tweets():
    """Generate mock tweets for testing"""
    now = datetime.now()
    tweets = []

    for i in range(20):
        tweets.append(Tweet(
            tweet_id=f"tweet_{i}",
            author=f"user_{i % 5}",
            author_id=f"uid_{i % 5}",
            content=f"This is a test tweet about #AI and #innovation - tweet {i}",
            sentiment_score=0.5 if i < 15 else -0.7,  # Mix of positive and negative
            created_at=now - timedelta(hours=i),
            engagement={
                "likes": 10 + i * 2,
                "retweets": 5 + i,
                "replies": 2 + i // 2
            }
        ))

    return tweets


@pytest.fixture
def mock_influencers():
    """Generate mock influencers for testing"""
    return [
        {
            "username": "ai_expert",
            "name": "AI Expert",
            "followers_count": 100000,
            "verified": True,
            "description": "AI researcher and educator",
            "influence_score": 75000.0,
            "topics": ["AI", "machine learning"]
        },
        {
            "username": "tech_guru",
            "name": "Tech Guru",
            "followers_count": 50000,
            "verified": False,
            "description": "Technology enthusiast",
            "influence_score": 35000.0,
            "topics": ["technology", "innovation"]
        }
    ]


@pytest.fixture
def mock_twitter_connector(mock_tweets, mock_influencers):
    """Mock Twitter connector"""
    connector = Mock(spec=TwitterConnector)

    # Mock search_tweets
    async def mock_search_tweets(*args, **kwargs):
        return mock_tweets
    connector.search_tweets = AsyncMock(side_effect=mock_search_tweets)

    # Mock get_influencers
    async def mock_get_influencers(*args, **kwargs):
        return mock_influencers
    connector.get_influencers = AsyncMock(side_effect=mock_get_influencers)

    # Mock get_user_tweets
    async def mock_get_user_tweets(*args, **kwargs):
        return mock_tweets[:5]
    connector.get_user_tweets = AsyncMock(side_effect=mock_get_user_tweets)

    return connector


@pytest.fixture
def mock_sentiment_analyzer():
    """Mock sentiment analyzer"""
    analyzer = Mock(spec=SentimentAnalyzer)

    # Mock analyze_tweets
    async def mock_analyze_tweets(tweets):
        enriched = []
        for tweet in tweets:
            tweet_copy = tweet.copy()
            # Use existing sentiment_score or generate one
            score = tweet_copy.get('sentiment_score', 0.5)
            tweet_copy['sentiment'] = {
                'sentiment_score': score,
                'label': 'positive' if score > 0.2 else 'negative' if score < -0.2 else 'neutral',
                'confidence': abs(score)
            }
            enriched.append(tweet_copy)
        return enriched
    analyzer.analyze_tweets = AsyncMock(side_effect=mock_analyze_tweets)

    # Mock aggregate_sentiment
    def mock_aggregate_sentiment(sentiments):
        if not sentiments:
            return {
                'mean_score': 0.0,
                'overall_label': 'neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }

        scores = [s['sentiment_score'] for s in sentiments]
        mean_score = sum(scores) / len(scores)

        return {
            'mean_score': mean_score,
            'overall_label': 'positive' if mean_score > 0.2 else 'negative' if mean_score < -0.2 else 'neutral',
            'positive_count': sum(1 for s in scores if s > 0.2),
            'negative_count': sum(1 for s in scores if s < -0.2),
            'neutral_count': sum(1 for s in scores if -0.2 <= s <= 0.2)
        }
    analyzer.aggregate_sentiment = Mock(side_effect=mock_aggregate_sentiment)

    # Mock detect_sentiment_shift
    def mock_detect_shift(current, previous, threshold=0.3):
        curr_score = current.get('mean_score', 0.0)
        prev_score = previous.get('mean_score', 0.0)
        shift = curr_score - prev_score

        return {
            'shift_detected': abs(shift) >= threshold,
            'is_crisis': shift < -threshold,
            'shift_magnitude': shift,
            'current_score': curr_score,
            'previous_score': prev_score,
            'direction': 'negative' if shift < 0 else 'positive'
        }
    analyzer.detect_sentiment_shift = Mock(side_effect=mock_detect_shift)

    return analyzer


class TestSocialMediaAgent:
    """Test suite for SocialMediaAgent"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = SocialMediaAgent()

        assert agent.name == "SocialMediaAgent"
        assert agent.timeout == 120
        assert agent.twitter is not None
        assert agent.sentiment_analyzer is not None

    @pytest.mark.asyncio
    async def test_execute_basic_monitoring(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test basic social media monitoring execution"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        input_data = {
            "company": "TestCo",
            "keywords": ["TestCo", "#TestCo"],
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        # Verify success
        assert result['success'] is True
        assert result['error'] is None
        assert result['data'] is not None

        # Verify data structure
        insight: SocialMediaInsight = result['data']
        assert insight.platform == "twitter"
        assert insight.overall_sentiment is not None
        assert insight.sentiment_label in ['positive', 'negative', 'neutral']
        assert isinstance(insight.trending_topics, list)
        assert isinstance(insight.top_influencers, list)
        assert isinstance(insight.metrics, dict)

        # Verify Twitter connector was called
        mock_twitter_connector.search_tweets.assert_called_once()
        mock_twitter_connector.get_influencers.assert_called()

    @pytest.mark.asyncio
    async def test_competitor_tracking(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test competitor mention tracking"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        input_data = {
            "company": "TestCo",
            "keywords": ["TestCo"],
            "competitors": ["CompetitorA", "CompetitorB"],
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        assert result['success'] is True
        insight: SocialMediaInsight = result['data']

        # Verify competitor tracking
        assert isinstance(insight.competitor_mentions, dict)

        # Twitter search should be called for main company + competitors
        assert mock_twitter_connector.search_tweets.call_count >= 2

    @pytest.mark.asyncio
    async def test_crisis_detection(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test crisis detection functionality"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        input_data = {
            "company": "TestCo",
            "keywords": ["TestCo"],
            "alert_threshold": 0.3,
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        assert result['success'] is True
        insight: SocialMediaInsight = result['data']

        # Check crisis alerts structure
        assert isinstance(insight.crisis_alerts, list)

        # If shift detected, verify alert structure
        if insight.crisis_alerts:
            alert = insight.crisis_alerts[0]
            assert isinstance(alert, CrisisAlert)
            assert alert.severity in ['low', 'medium', 'high', 'critical']
            assert alert.trigger_type == "negative_sentiment_spike"
            assert alert.sentiment_shift < 0  # Negative shift

    @pytest.mark.asyncio
    async def test_influencer_identification(self, mock_twitter_connector, mock_sentiment_analyzer, mock_influencers):
        """Test influencer identification"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        input_data = {
            "company": "TestCo",
            "keywords": ["AI", "technology"],
            "min_influencer_followers": 10000,
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        assert result['success'] is True
        insight: SocialMediaInsight = result['data']

        # Verify influencers found
        assert len(insight.top_influencers) > 0

        for influencer in insight.top_influencers:
            assert isinstance(influencer, Influencer)
            assert influencer.followers_count >= 10000
            assert influencer.influence_score > 0

    @pytest.mark.asyncio
    async def test_trending_topics(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test trending topic identification"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        input_data = {
            "company": "TestCo",
            "keywords": ["TestCo"],
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        assert result['success'] is True
        insight: SocialMediaInsight = result['data']

        # Verify trending topics structure
        assert isinstance(insight.trending_topics, list)

        for topic in insight.trending_topics:
            assert isinstance(topic, TrendingTopic)
            assert topic.topic.startswith('#')
            assert topic.mention_count > 0

    @pytest.mark.asyncio
    async def test_metrics_calculation(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test engagement metrics calculation"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        input_data = {
            "company": "TestCo",
            "keywords": ["TestCo"],
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        assert result['success'] is True
        insight: SocialMediaInsight = result['data']

        # Verify metrics present
        metrics = insight.metrics
        assert 'total_tweets' in metrics
        assert 'engagement_rate' in metrics
        assert 'reach' in metrics
        assert 'avg_likes' in metrics
        assert 'avg_retweets' in metrics

        # Verify values are reasonable
        assert metrics['total_tweets'] > 0
        assert metrics['engagement_rate'] >= 0
        assert metrics['reach'] >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test error handling when Twitter API fails"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        # Make Twitter connector raise error
        mock_twitter_connector.search_tweets.side_effect = Exception("Twitter API error")

        input_data = {
            "company": "TestCo",
            "keywords": ["TestCo"],
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        # Should handle error gracefully
        assert result['success'] is False
        assert result['error'] is not None
        assert "Twitter API error" in result['error']

    @pytest.mark.asyncio
    async def test_severity_calculation(self):
        """Test alert severity calculation"""
        agent = SocialMediaAgent()

        # Test different severity levels
        assert agent._calculate_severity(-0.75) == "critical"
        assert agent._calculate_severity(-0.55) == "high"
        assert agent._calculate_severity(-0.35) == "medium"
        assert agent._calculate_severity(-0.15) == "low"

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_twitter_connector, mock_sentiment_analyzer):
        """Test handling of empty results"""
        agent = SocialMediaAgent()
        agent.twitter = mock_twitter_connector
        agent.sentiment_analyzer = mock_sentiment_analyzer

        # Mock empty tweet results
        mock_twitter_connector.search_tweets.return_value = AsyncMock(return_value=[])

        input_data = {
            "company": "UnknownCo",
            "keywords": ["UnknownCo"],
            "days_back": 7
        }

        result = await agent._execute_internal(input_data)

        # Should still succeed with empty data
        assert result['success'] is True
        insight: SocialMediaInsight = result['data']
        assert insight.metrics['total_tweets'] == 0


class TestTwitterConnector:
    """Test suite for TwitterConnector"""

    def test_connector_initialization(self):
        """Test connector initializes correctly"""
        connector = TwitterConnector(
            bearer_token="test_token"
        )

        assert connector.bearer_token == "test_token"

    @pytest.mark.asyncio
    async def test_search_tweets_mock_data(self):
        """Test search_tweets returns mock data when no API available"""
        connector = TwitterConnector()  # No credentials

        tweets = await connector.search_tweets(
            keywords=["test"],
            max_results=10
        )

        # Should return mock data
        assert len(tweets) > 0
        assert isinstance(tweets[0], Tweet)

    @pytest.mark.asyncio
    async def test_get_influencers_mock_data(self):
        """Test get_influencers returns mock data when no API available"""
        connector = TwitterConnector()  # No credentials

        influencers = await connector.get_influencers(
            topic="AI",
            min_followers=10000
        )

        # Should return mock data
        assert len(influencers) > 0
        assert influencers[0]['followers_count'] >= 10000

    def test_influence_score_calculation(self):
        """Test influence score calculation"""
        connector = TwitterConnector()

        user = TwitterUser(
            user_id="123",
            username="test_user",
            name="Test User",
            followers_count=100000,
            following_count=1000,
            verified=True
        )

        score = connector._calculate_influence_score(user)

        # Score should include followers, ratio, and verified bonus
        assert score > 0
        assert score > 40000  # Base followers * 0.4
        assert score > 50000  # Should include verified bonus


class TestSentimentAnalyzer:
    """Test suite for SentimentAnalyzer"""

    @pytest.mark.asyncio
    async def test_analyze_text(self):
        """Test text sentiment analysis"""
        analyzer = SentimentAnalyzer()

        # Test positive text
        result = await analyzer.analyze_text("This is amazing and wonderful!")
        assert result['sentiment_score'] > 0
        assert result['label'] == 'positive'

        # Test negative text
        result = await analyzer.analyze_text("This is terrible and awful!")
        assert result['sentiment_score'] < 0
        assert result['label'] == 'negative'

        # Test neutral text
        result = await analyzer.analyze_text("This is a product.")
        assert result['label'] == 'neutral'

    @pytest.mark.asyncio
    async def test_analyze_batch(self):
        """Test batch sentiment analysis"""
        analyzer = SentimentAnalyzer()

        texts = [
            "Great product!",
            "Terrible experience.",
            "It's okay."
        ]

        results = await analyzer.analyze_batch(texts)

        assert len(results) == 3
        assert results[0]['label'] == 'positive'
        assert results[1]['label'] == 'negative'

    def test_aggregate_sentiment(self):
        """Test sentiment aggregation"""
        analyzer = SentimentAnalyzer()

        sentiments = [
            {'sentiment_score': 0.8, 'label': 'positive'},
            {'sentiment_score': 0.5, 'label': 'positive'},
            {'sentiment_score': -0.3, 'label': 'negative'},
            {'sentiment_score': 0.1, 'label': 'neutral'}
        ]

        result = analyzer.aggregate_sentiment(sentiments)

        assert 'mean_score' in result
        assert 'positive_count' in result
        assert 'negative_count' in result
        assert result['total_count'] == 4
        assert result['positive_count'] == 2
        assert result['negative_count'] == 1

    def test_detect_sentiment_shift(self):
        """Test sentiment shift detection"""
        analyzer = SentimentAnalyzer()

        current = {'mean_score': -0.5}
        previous = {'mean_score': 0.5}

        result = analyzer.detect_sentiment_shift(current, previous, threshold=0.3)

        assert result['shift_detected'] is True
        assert result['is_crisis'] is True
        assert result['shift_magnitude'] == -1.0
        assert result['direction'] == 'negative'


# Integration tests
@pytest.mark.asyncio
async def test_end_to_end_monitoring(mock_twitter_connector, mock_sentiment_analyzer):
    """Test complete end-to-end monitoring workflow"""
    agent = SocialMediaAgent()
    agent.twitter = mock_twitter_connector
    agent.sentiment_analyzer = mock_sentiment_analyzer

    # Complete monitoring request
    input_data = {
        "company": "TechCorp",
        "keywords": ["TechCorp", "#TechCorp"],
        "competitors": ["CompetitorA"],
        "days_back": 7,
        "min_influencer_followers": 10000,
        "alert_threshold": 0.3
    }

    result = await agent._execute_internal(input_data)

    # Verify complete workflow executed
    assert result['success'] is True

    insight: SocialMediaInsight = result['data']

    # Verify all components present
    assert insight.platform == "twitter"
    assert insight.overall_sentiment is not None
    assert len(insight.trending_topics) >= 0
    assert len(insight.top_influencers) >= 0
    assert len(insight.crisis_alerts) >= 0
    assert insight.metrics['total_tweets'] > 0

    # Verify time period
    assert 'start' in insight.time_period
    assert 'end' in insight.time_period


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
