# API Keys Setup Guide for Full System Deployment

## Quick Setup: Minimum Required Keys

To get **Core + MVP features working**, you only need **2 keys**:

```bash
# REQUIRED - Core AI functionality
export GEMINI_API_KEY="your_gemini_api_key_here"

# REQUIRED - Web research
export TAVILY_API_KEY="your_tavily_api_key_here"
```

---

## Complete Setup: All Features Enabled

For **all 13 agents** to work (Core + Phase 1 + Phase 2), use this setup:

### 🔴 REQUIRED (2 keys) - Core System

#### 1. Gemini API Key (Google AI)

**What it enables**: All AI agents (research, market, financial, framework, synthesis)

**How to get it**:

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

#### 2. Tavily API Key (Web Research)

**What it enables**: ResearchAgent (web search and content extraction)

**How to get it**:

1. Go to https://app.tavily.com
2. Sign up for free account
3. Copy your API key from dashboard

```bash
export TAVILY_API_KEY="your_tavily_api_key_here"
```

---

### 🟡 RECOMMENDED (4 keys) - Phase 1 & 2 Core Features

#### 3. Alpha Vantage API Key (Financial Data)

**What it enables**: Enhanced financial analysis, technical indicators, sector performance

**How to get it** (FREE):

1. Go to https://www.alphavantage.co/support/#api-key
2. Enter email
3. Get instant free API key
4. Free tier: 25 calls/day, 5 calls/minute (sufficient for demos)

```bash
export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_api_key_here"
```

#### 4. Finnhub API Key (Real-time Financial)

**What it enables**: Real-time stock data, analyst recommendations, earnings

**How to get it** (FREE):

1. Go to https://finnhub.io/register
2. Sign up for free account
3. Copy API key from dashboard
4. Free tier: 60 calls/minute (sufficient)

```bash
export FINNHUB_API_KEY="your_finnhub_api_key_here"
```

#### 5. Reddit API Credentials (Social Media Intelligence)

**What it enables**: SocialMediaAgent - Reddit sentiment, discussions, trends

**How to get it** (FREE):

1. Go to https://www.reddit.com/prefs/apps
2. Click "create app" or "create another app"
3. Select **"script"** as app type
4. Name: ConsultantOS
5. Redirect URI: http://localhost:8080 (doesn't matter for script apps)
6. Copy **Client ID** (under app name) and **Client Secret**

```bash
export REDDIT_CLIENT_ID="your_reddit_client_id_here"
export REDDIT_CLIENT_SECRET="your_reddit_client_secret_here"
export REDDIT_USER_AGENT="ConsultantOS:v1.0 (by /u/your_reddit_username)"
```

#### 6. Twitter API Bearer Token (Social Media Intelligence)

**What it enables**: SocialMediaAgent - Twitter sentiment, trending topics

**How to get it** (FREE - Essential Access):

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Create a new app (or use existing)
3. Go to "Keys and Tokens" tab
4. Generate **Bearer Token** (under Authentication Tokens)
5. Copy the bearer token

**Note**: Twitter now requires Essential Access ($100/month) for API v2. If you don't have this:

- Skip this key - SocialMediaAgent will work with Reddit only
- Or use free tier with limited features

```bash
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token_here"
```

---

### 🟢 OPTIONAL (Nice to Have)

#### 7. Slack Webhook (Alerting)

**What it enables**: Alert notifications sent to Slack

**How to get it** (FREE):

1. Go to https://api.slack.com/apps
2. Create new app
3. Enable "Incoming Webhooks"
4. Add webhook to workspace
5. Copy webhook URL

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

#### 8. Sentry DSN (Error Tracking)

**What it enables**: Production error monitoring and performance tracking

**How to get it** (FREE tier available):

1. Go to https://sentry.io
2. Create account and project
3. Copy DSN from Settings → Client Keys

```bash
export SENTRY_DSN="https://your-dsn@o12345.ingest.sentry.io/67890"
```

---

## Feature Matrix: What Works with Which Keys

| Agent/Feature            | Required Keys  | Optional Keys          | Status                          |
| ------------------------ | -------------- | ---------------------- | ------------------------------- |
| **Core Agents**          |                |                        |                                 |
| ResearchAgent            | GEMINI, TAVILY | -                      | ✅ Required                     |
| MarketAgent              | GEMINI         | -                      | ✅ Required                     |
| FinancialAgent           | GEMINI         | FINNHUB, ALPHA_VANTAGE | ⚠️ Works without, limited data  |
| FrameworkAgent           | GEMINI         | -                      | ✅ Required                     |
| SynthesisAgent           | GEMINI         | -                      | ✅ Required                     |
| **Phase 1 Agents**       |                |                        |                                 |
| EnhancedForecastingAgent | GEMINI         | ALPHA_VANTAGE          | ⚠️ Works without, uses yfinance |
| DarkDataAgent            | GEMINI         | Gmail OAuth            | ⚠️ Works, needs user Gmail auth |
| ConversationalAgentMVP   | GEMINI         | -                      | ✅ Required                     |
| **Phase 2 Agents**       |                |                        |                                 |
| SocialMediaAgent         | GEMINI         | REDDIT*\*, TWITTER*\*  | ⚠️ Works with partial keys      |
| WargamingAgent           | GEMINI         | -                      | ✅ Required                     |
| AnalyticsBuilderAgent    | GEMINI         | -                      | ✅ Required                     |
| StorytellingAgent        | GEMINI         | -                      | ✅ Required                     |

---

## Deployment Commands

### Minimum Deployment (Core + MVP)

```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "\
GEMINI_API_KEY=${GEMINI_API_KEY},\
TAVILY_API_KEY=${TAVILY_API_KEY}"
```

**Result**: 9 agents available (Core 5 + ConversationalMVP + Forecasting + Wargaming + Analytics + Storytelling)

### Recommended Deployment (Full Features)

```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "\
GEMINI_API_KEY=${GEMINI_API_KEY},\
TAVILY_API_KEY=${TAVILY_API_KEY},\
ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY},\
FINNHUB_API_KEY=${FINNHUB_API_KEY},\
REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID},\
REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}"
```

**Result**: 13 agents available (all features enabled, Twitter optional)

### Maximum Deployment (Everything + Monitoring)

```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "\
GEMINI_API_KEY=${GEMINI_API_KEY},\
TAVILY_API_KEY=${TAVILY_API_KEY},\
ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY},\
FINNHUB_API_KEY=${FINNHUB_API_KEY},\
REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID},\
REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET},\
TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN},\
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL},\
SENTRY_DSN=${SENTRY_DSN}"
```

**Result**: All 13 agents + alerts + error monitoring

---

## Cost Breakdown (Monthly)

| Service           | Free Tier                | Paid Plan                   | Recommended             |
| ----------------- | ------------------------ | --------------------------- | ----------------------- |
| **Google Gemini** | Free (60 req/min)        | $0.35/1M tokens             | ✅ Free sufficient      |
| **Tavily**        | $0 (1000 searches/month) | $50/month                   | ✅ Free sufficient      |
| **Alpha Vantage** | Free (25 calls/day)      | $50/month                   | ✅ Free sufficient      |
| **Finnhub**       | Free (60 calls/min)      | $0-100/month                | ✅ Free sufficient      |
| **Reddit API**    | Free (100 req/min)       | Free                        | ✅ Always free          |
| **Twitter API**   | ~~Free~~ $100/month      | $100-5000/month             | ⚠️ Skip if no budget    |
| **Slack**         | Free                     | Free                        | ✅ Always free          |
| **Sentry**        | Free (5K errors/month)   | $26/month                   | ✅ Free sufficient      |
| **Total**         | **$0/month**             | **$100/month** (if Twitter) | **Recommend free tier** |

---

## Quick Start: 5-Minute Setup

**For hackathon demo, get these 4 keys** (all free, 5 minutes each):

1. **Gemini** (2 min): https://makersuite.google.com/app/apikey
2. **Tavily** (1 min): https://app.tavily.com → Sign up → Copy key
3. **Alpha Vantage** (1 min): https://www.alphavantage.co/support/#api-key
4. **Reddit** (1 min): https://www.reddit.com/prefs/apps → Create app → Copy ID/Secret

**Then deploy**:

```bash
export GEMINI_API_KEY="..."
export TAVILY_API_KEY="..."
export ALPHA_VANTAGE_API_KEY="..."
export REDDIT_CLIENT_ID="..."
export REDDIT_CLIENT_SECRET="..."

# Deploy with 5 keys = 12+ agents enabled
gcloud run deploy consultantos --source . --region us-central1 \
  --allow-unauthenticated --memory 4Gi --cpu 2 --timeout 300 \
  --set-env-vars "\
GEMINI_API_KEY=${GEMINI_API_KEY},\
TAVILY_API_KEY=${TAVILY_API_KEY},\
ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY},\
REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID},\
REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}"
```

---

## Troubleshooting

### "Agent X is unavailable"

- Check if API key is set correctly
- Check Cloud Run logs: `gcloud run logs read consultantos`
- Verify key is valid (test in curl/browser)

### Rate Limits Hit

- Gemini: 60 req/min free tier (increase to paid if needed)
- Alpha Vantage: 25 calls/day free (switch to Finnhub or paid)
- Reddit: 100 req/min (sufficient, no action needed)

### Missing Optional Features

- System works with graceful degradation
- Only required features: GEMINI + TAVILY
- All others are optional enhancements

---

## Security Best Practices

1. **Never commit API keys to git**

   - Use `.env` file locally (already in `.gitignore`)
   - Use Cloud Run env vars for production

2. **Use Google Secret Manager** (production)

   ```bash
   echo "your-key" | gcloud secrets create gemini-api-key --data-file=-
   ```

3. **Rotate keys regularly**

   - Regenerate keys every 90 days
   - Use different keys for dev/staging/prod

4. **Monitor usage**
   - Check API dashboards monthly
   - Set up alerts for rate limits
   - Use Sentry for error tracking

---

## Next Steps

1. ✅ Get minimum 2 keys (Gemini + Tavily)
2. ✅ Get recommended 4 keys (+ Alpha Vantage + Reddit)
3. ✅ Set environment variables
4. ✅ Deploy to Cloud Run
5. ✅ Test with `/integration/health` endpoint
6. ✅ Verify agent availability
7. ✅ Run full integration test
