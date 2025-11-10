"""
Reddit API Connector using PRAW for social media monitoring
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

try:
    import praw
    from praw.models import MoreComments
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("praw not installed - Reddit connector will use mock data")


class RedditConnector:
    """Reddit API connector for social media monitoring"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: str = "ConsultantOS:v1.0 (by /u/consultantos)"
    ):
        """
        Initialize Reddit connector

        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string for Reddit API
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.reddit = None

        if PRAW_AVAILABLE and client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent,
                    check_for_async=False
                )
                # Test connection
                self.reddit.read_only = True
                logger.info("Reddit API connector initialized (read-only)")
            except Exception as e:
                logger.warning(f"Failed to initialize Reddit API: {e}")
                self.reddit = None

    async def search_posts(
        self,
        keywords: List[str],
        subreddits: Optional[List[str]] = None,
        time_filter: str = "week",
        limit: int = 100,
        sort: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search posts across subreddits

        Args:
            keywords: Keywords to search for
            subreddits: Specific subreddits to search (None = all)
            time_filter: Time filter - hour, day, week, month, year, all
            limit: Maximum posts to return
            sort: Sort method - relevance, hot, top, new, comments

        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit API not available, using mock data")
            return self._generate_mock_posts(keywords, limit)

        posts = []

        try:
            # Build search query
            query = " OR ".join(keywords)

            if subreddits:
                # Search specific subreddits
                for subreddit_name in subreddits[:5]:  # Limit to avoid rate limits
                    try:
                        subreddit = await asyncio.to_thread(
                            self.reddit.subreddit,
                            subreddit_name
                        )

                        search_results = await asyncio.to_thread(
                            lambda: list(subreddit.search(
                                query,
                                time_filter=time_filter,
                                limit=limit // len(subreddits),
                                sort=sort
                            ))
                        )

                        for post in search_results:
                            posts.append(self._post_to_dict(post))

                    except Exception as e:
                        logger.warning(f"Failed to search r/{subreddit_name}: {e}")
            else:
                # Search all of Reddit
                search_results = await asyncio.to_thread(
                    lambda: list(self.reddit.subreddit("all").search(
                        query,
                        time_filter=time_filter,
                        limit=limit,
                        sort=sort
                    ))
                )

                for post in search_results:
                    posts.append(self._post_to_dict(post))

            logger.info(f"Found {len(posts)} Reddit posts for keywords: {keywords}")

        except Exception as e:
            logger.error(f"Reddit search failed: {e}")
            posts = self._generate_mock_posts(keywords, limit)

        return posts[:limit]

    async def get_subreddit_posts(
        self,
        subreddit_name: str,
        sort: str = "hot",
        limit: int = 100,
        time_filter: str = "week"
    ) -> List[Dict[str, Any]]:
        """
        Get posts from specific subreddit

        Args:
            subreddit_name: Subreddit name (without r/)
            sort: Sort method - hot, new, top, rising, controversial
            limit: Maximum posts to return
            time_filter: Time filter for 'top' and 'controversial'

        Returns:
            List of post dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit API not available, using mock data")
            return self._generate_mock_posts([subreddit_name], limit)

        posts = []

        try:
            subreddit = await asyncio.to_thread(
                self.reddit.subreddit,
                subreddit_name
            )

            # Get posts based on sort method
            if sort == "hot":
                post_list = await asyncio.to_thread(
                    lambda: list(subreddit.hot(limit=limit))
                )
            elif sort == "new":
                post_list = await asyncio.to_thread(
                    lambda: list(subreddit.new(limit=limit))
                )
            elif sort == "top":
                post_list = await asyncio.to_thread(
                    lambda: list(subreddit.top(time_filter=time_filter, limit=limit))
                )
            elif sort == "rising":
                post_list = await asyncio.to_thread(
                    lambda: list(subreddit.rising(limit=limit))
                )
            elif sort == "controversial":
                post_list = await asyncio.to_thread(
                    lambda: list(subreddit.controversial(time_filter=time_filter, limit=limit))
                )
            else:
                post_list = await asyncio.to_thread(
                    lambda: list(subreddit.hot(limit=limit))
                )

            for post in post_list:
                posts.append(self._post_to_dict(post))

            logger.info(f"Found {len(posts)} posts from r/{subreddit_name} (sort={sort})")

        except Exception as e:
            logger.error(f"Failed to get posts from r/{subreddit_name}: {e}")
            posts = self._generate_mock_posts([subreddit_name], limit)

        return posts

    async def analyze_comments(
        self,
        post_id: str,
        max_depth: int = 3,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Analyze comment threads for a post

        Args:
            post_id: Reddit post ID
            max_depth: Maximum comment thread depth
            limit: Maximum comments to return

        Returns:
            List of comment dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit API not available, using mock data")
            return self._generate_mock_comments(post_id, limit)

        comments = []

        try:
            submission = await asyncio.to_thread(
                self.reddit.submission,
                id=post_id
            )

            # Expand comment forest
            await asyncio.to_thread(
                submission.comments.replace_more,
                limit=0
            )

            # Traverse comment tree
            comment_queue = [(c, 0) for c in submission.comments]

            while comment_queue and len(comments) < limit:
                comment, depth = comment_queue.pop(0)

                if isinstance(comment, MoreComments):
                    continue

                if depth <= max_depth:
                    comments.append(self._comment_to_dict(comment, depth, post_id))

                    # Add replies to queue
                    if depth < max_depth:
                        for reply in comment.replies:
                            comment_queue.append((reply, depth + 1))

            logger.info(f"Analyzed {len(comments)} comments for post {post_id}")

        except Exception as e:
            logger.error(f"Failed to analyze comments for post {post_id}: {e}")
            comments = self._generate_mock_comments(post_id, limit)

        return comments[:limit]

    async def find_trending_subreddits(
        self,
        keywords: List[str],
        min_subscribers: int = 1000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find active subreddits for keywords

        Args:
            keywords: Keywords to search for
            min_subscribers: Minimum subscriber count
            limit: Maximum subreddits to return

        Returns:
            List of subreddit dictionaries
        """
        if not self.reddit:
            logger.warning("Reddit API not available, using mock data")
            return self._generate_mock_subreddits(keywords, limit)

        subreddits = []
        seen_subreddits = set()

        try:
            # Search for posts and extract subreddits
            query = " OR ".join(keywords)

            search_results = await asyncio.to_thread(
                lambda: list(self.reddit.subreddit("all").search(
                    query,
                    time_filter="week",
                    limit=100,
                    sort="top"
                ))
            )

            # Count posts per subreddit
            subreddit_counts = {}
            for post in search_results:
                subreddit_name = post.subreddit.display_name
                if subreddit_name not in subreddit_counts:
                    subreddit_counts[subreddit_name] = {
                        'count': 0,
                        'subreddit': post.subreddit
                    }
                subreddit_counts[subreddit_name]['count'] += 1

            # Sort by post count and get subreddit details
            sorted_subreddits = sorted(
                subreddit_counts.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )

            for subreddit_name, data in sorted_subreddits[:limit * 2]:
                if subreddit_name in seen_subreddits:
                    continue

                try:
                    subreddit = data['subreddit']

                    # Check subscriber minimum
                    if subreddit.subscribers < min_subscribers:
                        continue

                    # Get top posts for relevance
                    top_posts = await asyncio.to_thread(
                        lambda: list(subreddit.top(time_filter="week", limit=3))
                    )

                    subreddits.append({
                        'name': subreddit_name,
                        'subscriber_count': subreddit.subscribers,
                        'active_users': getattr(subreddit, 'active_user_count', 0) or 0,
                        'description': subreddit.public_description or '',
                        'relevance_score': data['count'] / max(len(search_results), 1),
                        'top_posts': [self._post_to_dict(p) for p in top_posts]
                    })

                    seen_subreddits.add(subreddit_name)

                    if len(subreddits) >= limit:
                        break

                except Exception as e:
                    logger.warning(f"Failed to get details for r/{subreddit_name}: {e}")

            logger.info(f"Found {len(subreddits)} trending subreddits for keywords: {keywords}")

        except Exception as e:
            logger.error(f"Failed to find trending subreddits: {e}")
            subreddits = self._generate_mock_subreddits(keywords, limit)

        return subreddits[:limit]

    async def get_user_profile(
        self,
        username: str
    ) -> Dict[str, Any]:
        """
        Get user profile information

        Args:
            username: Reddit username (without u/)

        Returns:
            User profile dictionary
        """
        if not self.reddit:
            logger.warning("Reddit API not available, using mock data")
            return self._generate_mock_user(username)

        try:
            user = await asyncio.to_thread(
                self.reddit.redditor,
                username
            )

            profile = {
                'username': user.name,
                'link_karma': user.link_karma,
                'comment_karma': user.comment_karma,
                'created_at': datetime.fromtimestamp(user.created_utc),
                'is_gold': user.is_gold if hasattr(user, 'is_gold') else False,
                'is_mod': user.is_mod if hasattr(user, 'is_mod') else False
            }

            logger.info(f"Retrieved profile for u/{username}")
            return profile

        except Exception as e:
            logger.error(f"Failed to get user profile for u/{username}: {e}")
            return self._generate_mock_user(username)

    def _post_to_dict(self, post: Any) -> Dict[str, Any]:
        """Convert PRAW post to dictionary"""
        return {
            'post_id': post.id,
            'title': post.title,
            'content': post.selftext if post.is_self else '',
            'subreddit': post.subreddit.display_name,
            'author': str(post.author) if post.author else '[deleted]',
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'num_comments': post.num_comments,
            'created_at': datetime.fromtimestamp(post.created_utc),
            'url': post.url,
            'is_self_post': post.is_self,
            'flair': post.link_flair_text,
            'awards': post.total_awards_received if hasattr(post, 'total_awards_received') else 0,
            'engagement': {
                'score': post.score,
                'comments': post.num_comments,
                'upvote_ratio': post.upvote_ratio
            }
        }

    def _comment_to_dict(self, comment: Any, depth: int, post_id: str) -> Dict[str, Any]:
        """Convert PRAW comment to dictionary"""
        return {
            'comment_id': comment.id,
            'post_id': post_id,
            'author': str(comment.author) if comment.author else '[deleted]',
            'content': comment.body,
            'score': comment.score,
            'created_at': datetime.fromtimestamp(comment.created_utc),
            'depth': depth,
            'parent_id': comment.parent_id if hasattr(comment, 'parent_id') else None
        }

    def _generate_mock_posts(self, keywords: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate mock posts for development/testing"""
        mock_posts = []
        now = datetime.now()

        for i in range(min(count, 20)):
            mock_posts.append({
                'post_id': f"mock_post_{i}",
                'title': f"Discussion about {keywords[0] if keywords else 'topic'} - Post {i}",
                'content': f"This is a mock Reddit post about {keywords[0] if keywords else 'topic'}. Lorem ipsum dolor sit amet.",
                'subreddit': f"MockSubreddit{i % 3}",
                'author': f"mock_user_{i % 5}",
                'score': 100 + i * 10,
                'upvote_ratio': 0.85 + (i % 10) * 0.01,
                'num_comments': 20 + i * 3,
                'created_at': now - timedelta(hours=i),
                'url': f"https://reddit.com/r/mock/post_{i}",
                'is_self_post': i % 2 == 0,
                'flair': f"Flair{i % 3}" if i % 2 == 0 else None,
                'awards': i % 5,
                'engagement': {
                    'score': 100 + i * 10,
                    'comments': 20 + i * 3,
                    'upvote_ratio': 0.85 + (i % 10) * 0.01
                }
            })

        return mock_posts

    def _generate_mock_comments(self, post_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock comments for development/testing"""
        mock_comments = []
        now = datetime.now()

        for i in range(min(count, 30)):
            mock_comments.append({
                'comment_id': f"mock_comment_{i}",
                'post_id': post_id,
                'author': f"mock_user_{i % 7}",
                'content': f"This is a mock comment number {i}. Great discussion!",
                'score': 10 + i * 2,
                'created_at': now - timedelta(hours=i),
                'depth': i % 3,
                'parent_id': f"mock_comment_{i-1}" if i > 0 and i % 3 != 0 else None
            })

        return mock_comments

    def _generate_mock_subreddits(self, keywords: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate mock subreddits for development/testing"""
        mock_subreddits = []

        for i in range(min(count, 10)):
            mock_subreddits.append({
                'name': f"{keywords[0] if keywords else 'topic'}{i}",
                'subscriber_count': 50000 + i * 10000,
                'active_users': 1000 + i * 200,
                'description': f"Community for discussing {keywords[0] if keywords else 'topic'}",
                'relevance_score': 1.0 - (i * 0.1),
                'top_posts': []
            })

        return mock_subreddits

    def _generate_mock_user(self, username: str) -> Dict[str, Any]:
        """Generate mock user profile"""
        return {
            'username': username,
            'link_karma': 5000,
            'comment_karma': 12000,
            'created_at': datetime.now() - timedelta(days=365),
            'is_gold': False,
            'is_mod': False
        }
