"""
Example: Reddit Monitoring with ConsultantOS

This script demonstrates how to use the Reddit integration for social media monitoring.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from consultantos.agents.social_media_agent import SocialMediaAgent


async def example_1_search_reddit_posts():
    """Example 1: Search Reddit posts for keywords"""
    print("\n" + "="*80)
    print("Example 1: Search Reddit Posts")
    print("="*80)

    agent = SocialMediaAgent(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ConsultantOS:v1.0")
    )

    # Search for AI-related posts
    posts = await agent.reddit.search_posts(
        keywords=["artificial intelligence", "AI"],
        subreddits=["artificial", "machinelearning"],  # Specific subreddits
        time_filter="week",
        limit=10
    )

    print(f"\nFound {len(posts)} posts about AI:\n")

    for i, post in enumerate(posts[:5], 1):
        print(f"{i}. [{post['subreddit']}] {post['title']}")
        print(f"   Score: {post['score']} | Comments: {post['num_comments']} | "
              f"Upvote Ratio: {post['upvote_ratio']:.2%}")
        print(f"   Author: u/{post['author']} | Posted: {post['created_at'].strftime('%Y-%m-%d %H:%M')}")
        if post['flair']:
            print(f"   Flair: {post['flair']}")
        print()


async def example_2_analyze_reddit_sentiment():
    """Example 2: Analyze sentiment of Reddit discussions"""
    print("\n" + "="*80)
    print("Example 2: Analyze Reddit Sentiment")
    print("="*80)

    agent = SocialMediaAgent(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ConsultantOS:v1.0")
    )

    # Analyze Reddit for a company
    reddit_insight = await agent._analyze_reddit(
        keywords=["OpenAI", "ChatGPT"],
        subreddits=["artificial", "ChatGPT", "OpenAI"],
        days_back=7
    )

    print(f"\nReddit Sentiment Analysis:")
    print(f"  Total Posts: {reddit_insight.total_posts}")
    print(f"  Total Comments: {reddit_insight.total_comments}")
    print(f"  Overall Sentiment: {reddit_insight.overall_sentiment:.3f}")
    print(f"    {'🟢 Positive' if reddit_insight.overall_sentiment > 0.2 else '🔴 Negative' if reddit_insight.overall_sentiment < -0.2 else '🟡 Neutral'}")

    print(f"\nCommunity Sentiment by Subreddit:")
    for subreddit, sentiment in reddit_insight.community_sentiment.items():
        emoji = "🟢" if sentiment > 0.2 else "🔴" if sentiment < -0.2 else "🟡"
        print(f"  {emoji} r/{subreddit}: {sentiment:.3f}")

    print(f"\nTrending Topics:")
    for topic in reddit_insight.trending_topics[:10]:
        print(f"  - {topic}")

    print(f"\nKey Contributors:")
    for user in reddit_insight.key_influencers[:10]:
        print(f"  - u/{user}")


async def example_3_discover_trending_subreddits():
    """Example 3: Discover trending subreddits for a topic"""
    print("\n" + "="*80)
    print("Example 3: Discover Trending Subreddits")
    print("="*80)

    agent = SocialMediaAgent(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ConsultantOS:v1.0")
    )

    # Find trending subreddits for AI
    subreddits = await agent.reddit.find_trending_subreddits(
        keywords=["artificial intelligence", "machine learning"],
        min_subscribers=10000,
        limit=10
    )

    print(f"\nTop {len(subreddits)} trending subreddits for AI:\n")

    for i, sub in enumerate(subreddits, 1):
        print(f"{i}. r/{sub['name']}")
        print(f"   Subscribers: {sub['subscriber_count']:,} | Active: {sub['active_users']:,}")
        print(f"   Relevance: {sub['relevance_score']:.2%}")
        print(f"   Description: {sub['description'][:100]}...")
        print()


async def example_4_analyze_comments():
    """Example 4: Analyze comments in a discussion"""
    print("\n" + "="*80)
    print("Example 4: Analyze Comment Threads")
    print("="*80)

    agent = SocialMediaAgent(
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ConsultantOS:v1.0")
    )

    # First, find a popular post
    posts = await agent.reddit.search_posts(
        keywords=["ChatGPT"],
        subreddits=["ChatGPT"],
        time_filter="week",
        limit=1
    )

    if not posts:
        print("No posts found")
        return

    post = posts[0]
    print(f"\nAnalyzing comments for: {post['title']}")
    print(f"Post URL: {post['url']}\n")

    # Analyze comments
    comments = await agent.reddit.analyze_comments(
        post_id=post['post_id'],
        max_depth=3,
        limit=50
    )

    print(f"Found {len(comments)} comments\n")

    # Group by depth
    depth_counts = {}
    for comment in comments:
        depth = comment['depth']
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

    print("Comment Distribution by Depth:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} comments")

    print("\nTop 5 Comments:")
    sorted_comments = sorted(comments, key=lambda c: c['score'], reverse=True)
    for i, comment in enumerate(sorted_comments[:5], 1):
        indent = "  " * comment['depth']
        print(f"{i}. {indent}[Score: {comment['score']}] u/{comment['author']}")
        preview = comment['content'][:100].replace('\n', ' ')
        print(f"{indent}   {preview}...")
        print()


async def example_5_multi_platform_monitoring():
    """Example 5: Combined Twitter + Reddit monitoring"""
    print("\n" + "="*80)
    print("Example 5: Multi-Platform Monitoring (Twitter + Reddit)")
    print("="*80)

    agent = SocialMediaAgent(
        twitter_bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
        reddit_client_id=os.getenv("REDDIT_CLIENT_ID"),
        reddit_client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        reddit_user_agent=os.getenv("REDDIT_USER_AGENT", "ConsultantOS:v1.0")
    )

    company = "OpenAI"
    keywords = ["OpenAI", "ChatGPT", "GPT-4"]

    print(f"\nMonitoring {company} across Twitter and Reddit...")

    # Monitor Twitter
    print("\n📱 Analyzing Twitter...")
    twitter_result = await agent.execute({
        "company": company,
        "keywords": keywords,
        "days_back": 7,
        "competitors": [],
        "alert_threshold": 1.0
    })

    # Monitor Reddit
    print("🤖 Analyzing Reddit...")
    reddit_insight = await agent._analyze_reddit(
        keywords=keywords,
        subreddits=None,  # Search all of Reddit
        days_back=7
    )

    # Combine insights
    print("\n" + "="*80)
    print("Combined Multi-Platform Insights")
    print("="*80)

    if twitter_result.get("success"):
        twitter_insight = twitter_result["data"]
        print(f"\n📱 Twitter:")
        print(f"   Sentiment: {twitter_insight.overall_sentiment:.3f} ({twitter_insight.sentiment_label})")
        print(f"   Tweets Analyzed: {twitter_insight.metrics.get('total_tweets', 0)}")
        print(f"   Trending Topics: {[t.topic for t in twitter_insight.trending_topics[:5]]}")

    print(f"\n🤖 Reddit:")
    print(f"   Sentiment: {reddit_insight.overall_sentiment:.3f}")
    print(f"   Posts Analyzed: {reddit_insight.total_posts}")
    print(f"   Comments Analyzed: {reddit_insight.total_comments}")
    print(f"   Trending Topics: {reddit_insight.trending_topics[:5]}")

    # Overall sentiment
    if twitter_result.get("success"):
        combined_sentiment = (twitter_insight.overall_sentiment + reddit_insight.overall_sentiment) / 2
        print(f"\n🌐 Overall Sentiment (Combined): {combined_sentiment:.3f}")
        if combined_sentiment > 0.2:
            print("   Status: 🟢 Positive - Brand sentiment is strong across platforms")
        elif combined_sentiment < -0.2:
            print("   Status: 🔴 Negative - Consider crisis response")
        else:
            print("   Status: 🟡 Neutral - Monitor for changes")


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("ConsultantOS Reddit Monitoring Examples")
    print("="*80)

    # Check if Reddit credentials are configured
    if not os.getenv("REDDIT_CLIENT_ID") or not os.getenv("REDDIT_CLIENT_SECRET"):
        print("\n⚠️  Reddit API credentials not found!")
        print("The examples will use mock data for demonstration.\n")
        print("To use real Reddit data:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create a new app (select 'script' type)")
        print("3. Add credentials to .env:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
        print("   REDDIT_USER_AGENT=ConsultantOS:v1.0 (by /u/your_username)")
        print()

    try:
        # Run examples
        await example_1_search_reddit_posts()
        await example_2_analyze_reddit_sentiment()
        await example_3_discover_trending_subreddits()
        await example_4_analyze_comments()
        await example_5_multi_platform_monitoring()

        print("\n" + "="*80)
        print("All examples completed successfully!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
