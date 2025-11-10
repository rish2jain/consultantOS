# Reddit Integration Quick Start

## Installation

```bash
# Install dependencies
pip install praw>=7.7.1

# Or install all requirements
pip install -r requirements.txt
```

## Configuration

### 1. Create Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Click "create app" or "create another app"
3. Fill in the form:
   - **Name**: ConsultantOS (or your app name)
   - **App type**: Select **"script"**
   - **Description**: Social media monitoring for ConsultantOS
   - **About URL**: (leave blank or add your URL)
   - **Redirect URI**: http://localhost:8080 (required but not used for read-only)
   - **Permissions**: (default read permissions are sufficient)
4. Click "create app"
5. **Copy your credentials**:
   - **Client ID**: String below "personal use script"
   - **Client Secret**: The "secret" field

### 2. Add to .env

```bash
# Reddit API Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ConsultantOS:v1.0 (by /u/your_reddit_username)
```

**Important**: Replace `your_reddit_username` with your actual Reddit username in the user agent.

## API Endpoints

### Search Reddit Posts
```bash
POST http://localhost:8080/social-media/reddit/search

{
  "keywords": ["AI", "machine learning"],
  "subreddits": ["artificial", "machinelearning"],
  "time_filter": "week",
  "limit": 50
}
```

### Find Trending Subreddits
```bash
GET http://localhost:8080/social-media/reddit/subreddits?keywords=AI&limit=10
```

### Analyze Comments
```bash
GET http://localhost:8080/social-media/reddit/comments/abc123?max_depth=3&limit=100
```

### Combined Twitter + Reddit
```bash
GET http://localhost:8080/social-media/combined?company=OpenAI&days_back=7
```

## Python Usage

```python
from consultantos.agents.social_media_agent import SocialMediaAgent

# Initialize agent
agent = SocialMediaAgent(
    reddit_client_id="your_client_id",
    reddit_client_secret="your_client_secret",
    reddit_user_agent="ConsultantOS:v1.0 (by /u/username)"
)

# Search posts
posts = await agent.reddit.search_posts(
    keywords=["AI"],
    subreddits=["artificial"],
    time_filter="week",
    limit=100
)

# Analyze Reddit
insight = await agent._analyze_reddit(
    keywords=["OpenAI"],
    subreddits=["artificial", "ChatGPT"],
    days_back=7
)

print(f"Sentiment: {insight.overall_sentiment}")
print(f"Posts: {insight.total_posts}")
print(f"Comments: {insight.total_comments}")
```

## Example Output

### Reddit Post
```json
{
  "post_id": "abc123",
  "title": "Discussion about GPT-4",
  "content": "What are your thoughts on GPT-4?",
  "subreddit": "artificial",
  "author": "ai_enthusiast",
  "score": 542,
  "upvote_ratio": 0.92,
  "num_comments": 87,
  "sentiment_score": 0.75,
  "is_self_post": true,
  "flair": "Discussion",
  "awards": 3
}
```

### Reddit Insight
```json
{
  "subreddits_monitored": ["artificial", "machinelearning"],
  "total_posts": 150,
  "total_comments": 450,
  "overall_sentiment": 0.62,
  "trending_topics": ["#GPT4", "[Discussion]", "#AI"],
  "community_sentiment": {
    "artificial": 0.65,
    "machinelearning": 0.58
  },
  "key_influencers": ["ai_researcher", "ml_expert"]
}
```

## Testing

```bash
# Run all Reddit tests
pytest tests/test_reddit_connector.py -v

# Run specific test
pytest tests/test_reddit_connector.py::test_search_posts_success -v

# Run with coverage
pytest tests/test_reddit_connector.py --cov=consultantos.connectors.reddit_connector
```

## Mock Data (No API Required)

The integration includes mock data for development without API credentials:

```python
# Works without credentials!
connector = RedditConnector()  # No credentials
posts = await connector.search_posts(keywords=["AI"], limit=20)
# Returns 20 realistic mock posts
```

## Common Use Cases

### Monitor Brand Sentiment
```python
insight = await agent._analyze_reddit(
    keywords=["YourBrand", "#YourBrand"],
    subreddits=["technology", "reviews"],
    days_back=7
)

for subreddit, sentiment in insight.community_sentiment.items():
    print(f"r/{subreddit}: {sentiment:.2f}")
```

### Track Competitor
```python
posts = await agent.reddit.search_posts(
    keywords=["CompetitorName"],
    time_filter="week",
    limit=100
)

# Analyze sentiment and engagement
```

### Find Product Discussions
```python
subreddits = await agent.reddit.find_trending_subreddits(
    keywords=["your product"],
    min_subscribers=5000,
    limit=20
)

# Monitor these subreddits for feedback
```

### Deep Discussion Analysis
```python
# Find top post
posts = await agent.reddit.search_posts(
    keywords=["topic"],
    time_filter="week",
    limit=1
)

# Analyze comments
comments = await agent.reddit.analyze_comments(
    post_id=posts[0]['post_id'],
    max_depth=3,
    limit=200
)
```

## Troubleshooting

### "PRAW not installed"
```bash
pip install praw>=7.7.1
```

### "Failed to initialize Reddit API"
- Check `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env`
- Verify credentials at https://www.reddit.com/prefs/apps
- Ensure app type is "script"

### Empty results
- Verify subreddit exists and is public
- Try broader time filter (week → month)
- Check if keywords are relevant

### Rate limits
- Reddit allows 60 requests/minute with authentication
- PRAW handles rate limiting automatically
- Use specific subreddits to reduce API calls

## Next Steps

1. ✅ Configure Reddit credentials
2. ✅ Test with example script: `python examples/reddit_monitoring_example.py`
3. ✅ Explore API endpoints: http://localhost:8080/docs
4. ✅ Build monitoring workflows
5. ✅ Integrate with dashboards

For detailed documentation, see: `REDDIT_INTEGRATION_SUMMARY.md`
