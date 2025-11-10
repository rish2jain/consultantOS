"""
Tests for Reddit connector
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from consultantos.connectors.reddit_connector import RedditConnector


@pytest.fixture
def reddit_connector():
    """Create Reddit connector instance with mock credentials"""
    return RedditConnector(
        client_id="test_client_id",
        client_secret="test_client_secret",
        user_agent="TestAgent:v1.0"
    )


@pytest.fixture
def mock_reddit_post():
    """Create mock Reddit post"""
    post = Mock()
    post.id = "abc123"
    post.title = "Test Discussion about AI"
    post.selftext = "What are your thoughts on AI?"
    post.subreddit.display_name = "artificial"
    post.author = Mock()
    post.author.__str__ = Mock(return_value="test_user")
    post.score = 542
    post.upvote_ratio = 0.92
    post.num_comments = 87
    post.created_utc = datetime.now().timestamp()
    post.url = "https://reddit.com/r/artificial/comments/abc123"
    post.is_self = True
    post.link_flair_text = "Discussion"
    post.total_awards_received = 3
    return post


@pytest.fixture
def mock_reddit_comment():
    """Create mock Reddit comment"""
    comment = Mock()
    comment.id = "def456"
    comment.author = Mock()
    comment.author.__str__ = Mock(return_value="commenter")
    comment.body = "Great discussion!"
    comment.score = 42
    comment.created_utc = datetime.now().timestamp()
    comment.parent_id = None
    comment.replies = []
    return comment


@pytest.mark.asyncio
async def test_search_posts_success(reddit_connector, mock_reddit_post):
    """Test successful post search"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        # Mock subreddit search
        mock_subreddit = Mock()
        mock_subreddit.search = Mock(return_value=[mock_reddit_post])
        mock_reddit.subreddit = Mock(return_value=mock_subreddit)

        posts = await reddit_connector.search_posts(
            keywords=["AI", "technology"],
            time_filter="week",
            limit=10
        )

        assert len(posts) > 0
        assert posts[0]['post_id'] == "abc123"
        assert posts[0]['title'] == "Test Discussion about AI"
        assert posts[0]['subreddit'] == "artificial"
        assert posts[0]['score'] == 542


@pytest.mark.asyncio
async def test_search_posts_specific_subreddits(reddit_connector, mock_reddit_post):
    """Test searching specific subreddits"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        mock_subreddit = Mock()
        mock_subreddit.search = Mock(return_value=[mock_reddit_post])
        mock_reddit.subreddit = Mock(return_value=mock_subreddit)

        posts = await reddit_connector.search_posts(
            keywords=["AI"],
            subreddits=["artificial", "machinelearning"],
            time_filter="week",
            limit=10
        )

        assert len(posts) > 0
        # Verify subreddit was called for each subreddit
        assert mock_reddit.subreddit.call_count >= 1


@pytest.mark.asyncio
async def test_search_posts_no_api(reddit_connector):
    """Test search posts without API (mock data)"""
    reddit_connector.reddit = None  # Simulate no API

    posts = await reddit_connector.search_posts(
        keywords=["test"],
        limit=5
    )

    assert len(posts) > 0
    assert all('post_id' in p for p in posts)
    assert all('title' in p for p in posts)


@pytest.mark.asyncio
async def test_get_subreddit_posts_hot(reddit_connector, mock_reddit_post):
    """Test getting hot posts from subreddit"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        mock_subreddit = Mock()
        mock_subreddit.hot = Mock(return_value=[mock_reddit_post])
        mock_reddit.subreddit = Mock(return_value=mock_subreddit)

        posts = await reddit_connector.get_subreddit_posts(
            subreddit_name="artificial",
            sort="hot",
            limit=10
        )

        assert len(posts) > 0
        assert posts[0]['subreddit'] == "artificial"
        mock_subreddit.hot.assert_called_once()


@pytest.mark.asyncio
async def test_get_subreddit_posts_top(reddit_connector, mock_reddit_post):
    """Test getting top posts from subreddit"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        mock_subreddit = Mock()
        mock_subreddit.top = Mock(return_value=[mock_reddit_post])
        mock_reddit.subreddit = Mock(return_value=mock_subreddit)

        posts = await reddit_connector.get_subreddit_posts(
            subreddit_name="technology",
            sort="top",
            time_filter="month",
            limit=10
        )

        assert len(posts) > 0
        mock_subreddit.top.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_comments(reddit_connector, mock_reddit_comment):
    """Test comment analysis"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        mock_submission = Mock()
        mock_submission.comments = Mock()
        mock_submission.comments.replace_more = Mock()
        mock_submission.comments.__iter__ = Mock(return_value=iter([mock_reddit_comment]))
        mock_reddit.submission = Mock(return_value=mock_submission)

        comments = await reddit_connector.analyze_comments(
            post_id="abc123",
            max_depth=3,
            limit=50
        )

        assert len(comments) > 0
        assert comments[0]['comment_id'] == "def456"
        assert comments[0]['post_id'] == "abc123"
        assert comments[0]['content'] == "Great discussion!"


@pytest.mark.asyncio
async def test_analyze_comments_nested(reddit_connector, mock_reddit_comment):
    """Test nested comment analysis"""
    # Create nested comment structure
    reply = Mock()
    reply.id = "ghi789"
    reply.author = Mock()
    reply.author.__str__ = Mock(return_value="replier")
    reply.body = "I agree!"
    reply.score = 10
    reply.created_utc = datetime.now().timestamp()
    reply.replies = []

    mock_reddit_comment.replies = [reply]

    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        mock_submission = Mock()
        mock_submission.comments = Mock()
        mock_submission.comments.replace_more = Mock()
        mock_submission.comments.__iter__ = Mock(return_value=iter([mock_reddit_comment]))
        mock_reddit.submission = Mock(return_value=mock_submission)

        comments = await reddit_connector.analyze_comments(
            post_id="abc123",
            max_depth=2,
            limit=50
        )

        assert len(comments) > 0
        # Check depth tracking
        assert any(c['depth'] == 0 for c in comments)


@pytest.mark.asyncio
async def test_find_trending_subreddits(reddit_connector, mock_reddit_post):
    """Test finding trending subreddits"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        # Mock search results
        mock_subreddit_all = Mock()
        mock_subreddit_all.search = Mock(return_value=[mock_reddit_post])

        # Mock specific subreddit details
        mock_post_subreddit = Mock()
        mock_post_subreddit.display_name = "artificial"
        mock_post_subreddit.subscribers = 250000
        mock_post_subreddit.active_user_count = 3500
        mock_post_subreddit.public_description = "AI Discussion"
        mock_post_subreddit.top = Mock(return_value=[])

        mock_reddit_post.subreddit = mock_post_subreddit
        mock_reddit.subreddit = Mock(return_value=mock_subreddit_all)

        subreddits = await reddit_connector.find_trending_subreddits(
            keywords=["AI", "machine learning"],
            min_subscribers=1000,
            limit=5
        )

        assert len(subreddits) > 0
        assert 'name' in subreddits[0]
        assert 'subscriber_count' in subreddits[0]
        assert 'relevance_score' in subreddits[0]


@pytest.mark.asyncio
async def test_find_trending_subreddits_no_api(reddit_connector):
    """Test trending subreddits without API"""
    reddit_connector.reddit = None

    subreddits = await reddit_connector.find_trending_subreddits(
        keywords=["test"],
        limit=5
    )

    assert len(subreddits) > 0
    assert all('name' in s for s in subreddits)
    assert all('subscriber_count' in s for s in subreddits)


@pytest.mark.asyncio
async def test_get_user_profile(reddit_connector):
    """Test getting user profile"""
    with patch.object(reddit_connector, 'reddit') as mock_reddit:
        mock_user = Mock()
        mock_user.name = "test_user"
        mock_user.link_karma = 5000
        mock_user.comment_karma = 12000
        mock_user.created_utc = (datetime.now() - timedelta(days=365)).timestamp()
        mock_user.is_gold = False
        mock_user.is_mod = False
        mock_reddit.redditor = Mock(return_value=mock_user)

        profile = await reddit_connector.get_user_profile("test_user")

        assert profile['username'] == "test_user"
        assert profile['link_karma'] == 5000
        assert profile['comment_karma'] == 12000


@pytest.mark.asyncio
async def test_post_to_dict(reddit_connector, mock_reddit_post):
    """Test converting post to dictionary"""
    post_dict = reddit_connector._post_to_dict(mock_reddit_post)

    assert post_dict['post_id'] == "abc123"
    assert post_dict['title'] == "Test Discussion about AI"
    assert post_dict['subreddit'] == "artificial"
    assert post_dict['author'] == "test_user"
    assert post_dict['score'] == 542
    assert post_dict['upvote_ratio'] == 0.92
    assert post_dict['is_self_post'] is True


@pytest.mark.asyncio
async def test_comment_to_dict(reddit_connector, mock_reddit_comment):
    """Test converting comment to dictionary"""
    comment_dict = reddit_connector._comment_to_dict(
        mock_reddit_comment,
        depth=0,
        post_id="abc123"
    )

    assert comment_dict['comment_id'] == "def456"
    assert comment_dict['post_id'] == "abc123"
    assert comment_dict['author'] == "commenter"
    assert comment_dict['content'] == "Great discussion!"
    assert comment_dict['depth'] == 0


def test_generate_mock_posts(reddit_connector):
    """Test mock post generation"""
    posts = reddit_connector._generate_mock_posts(["test"], 10)

    assert len(posts) == 10
    assert all('post_id' in p for p in posts)
    assert all('title' in p for p in posts)
    assert all('subreddit' in p for p in posts)


def test_generate_mock_comments(reddit_connector):
    """Test mock comment generation"""
    comments = reddit_connector._generate_mock_comments("abc123", 10)

    assert len(comments) == 10
    assert all('comment_id' in c for c in comments)
    assert all(c['post_id'] == "abc123" for c in comments)


def test_generate_mock_subreddits(reddit_connector):
    """Test mock subreddit generation"""
    subreddits = reddit_connector._generate_mock_subreddits(["AI"], 5)

    assert len(subreddits) == 5
    assert all('name' in s for s in subreddits)
    assert all('subscriber_count' in s for s in subreddits)
    assert all('relevance_score' in s for s in subreddits)


def test_generate_mock_user(reddit_connector):
    """Test mock user generation"""
    user = reddit_connector._generate_mock_user("test_user")

    assert user['username'] == "test_user"
    assert 'link_karma' in user
    assert 'comment_karma' in user
    assert 'created_at' in user
