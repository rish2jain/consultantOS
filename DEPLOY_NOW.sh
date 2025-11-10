#!/bin/bash
set -e

echo "======================================"
echo "ConsultantOS Full System Deployment"
echo "======================================"

# Load environment variables from .env file
if [ -f .env ]; then
    echo "✓ Loading API keys from .env file..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "✗ ERROR: .env file not found!"
    exit 1
fi

# Validate required keys
echo ""
echo "Validating API keys..."
MISSING_KEYS=0

if [ -z "$GEMINI_API_KEY" ]; then
    echo "✗ GEMINI_API_KEY is missing (REQUIRED)"
    MISSING_KEYS=1
else
    echo "✓ GEMINI_API_KEY found"
fi

if [ -z "$TAVILY_API_KEY" ]; then
    echo "⚠️  TAVILY_API_KEY is missing (highly recommended)"
else
    echo "✓ TAVILY_API_KEY found"
fi

if [ -z "$ALPHA_VANTAGE_API_KEY" ]; then
    echo "⚠️  ALPHA_VANTAGE_API_KEY is missing (recommended for Phase 1)"
else
    echo "✓ ALPHA_VANTAGE_API_KEY found"
fi

if [ -z "$FINNHUB_API_KEY" ]; then
    echo "⚠️  FINNHUB_API_KEY is missing (recommended for Phase 1)"
else
    echo "✓ FINNHUB_API_KEY found"
fi

if [ -z "$REDDIT_CLIENT_ID" ]; then
    echo "⚠️  REDDIT_CLIENT_ID is missing (optional for Phase 2 social media)"
else
    echo "✓ REDDIT_CLIENT_ID found"
fi

if [ -z "$REDDIT_CLIENT_SECRET" ]; then
    echo "⚠️  REDDIT_CLIENT_SECRET is missing (optional for Phase 2 social media)"
else
    echo "✓ REDDIT_CLIENT_SECRET found"
fi

if [ $MISSING_KEYS -eq 1 ]; then
    echo ""
    echo "✗ ERROR: Required API keys are missing. Please add them to .env file."
    exit 1
fi

echo ""
echo "======================================"
echo "Starting deployment to Cloud Run..."
echo "======================================"

# Build environment variables string for Cloud Run
ENV_VARS="GEMINI_API_KEY=${GEMINI_API_KEY}"

if [ ! -z "$TAVILY_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},TAVILY_API_KEY=${TAVILY_API_KEY}"
fi

if [ ! -z "$ALPHA_VANTAGE_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}"
fi

if [ ! -z "$FINNHUB_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},FINNHUB_API_KEY=${FINNHUB_API_KEY}"
fi

if [ ! -z "$REDDIT_CLIENT_ID" ]; then
    ENV_VARS="${ENV_VARS},REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}"
fi

if [ ! -z "$REDDIT_CLIENT_SECRET" ]; then
    ENV_VARS="${ENV_VARS},REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}"
fi

if [ ! -z "$REDDIT_USER_AGENT" ]; then
    ENV_VARS="${ENV_VARS},REDDIT_USER_AGENT=${REDDIT_USER_AGENT}"
fi

if [ ! -z "$TWITTER_BEARER_TOKEN" ]; then
    ENV_VARS="${ENV_VARS},TWITTER_BEARER_TOKEN=${TWITTER_BEARER_TOKEN}"
fi

if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    ENV_VARS="${ENV_VARS},SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}"
fi

if [ ! -z "$SENTRY_DSN" ]; then
    ENV_VARS="${ENV_VARS},SENTRY_DSN=${SENTRY_DSN}"
fi

if [ ! -z "$LAOZHANG_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},LAOZHANG_API_KEY=${LAOZHANG_API_KEY}"
fi

echo ""
echo "Deploying with the following configuration:"
echo "  Region: us-central1"
echo "  Memory: 4Gi"
echo "  CPU: 2"
echo "  Timeout: 300s"
echo "  API Keys: $(echo $ENV_VARS | tr ',' '\n' | grep -o '^[^=]*' | wc -l | xargs) configured"
echo ""

# Deploy to Cloud Run
gcloud run deploy consultantos-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "${ENV_VARS}"

DEPLOY_STATUS=$?

echo ""
echo "======================================"
if [ $DEPLOY_STATUS -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. Get your service URL from the output above"
    echo "2. Test health endpoint: curl https://YOUR-SERVICE-URL/health"
    echo "3. Test integration health: curl https://YOUR-SERVICE-URL/integration/health"
    echo "4. Check available agents in the integration health response"
    echo ""
    echo "For detailed testing, see: FULL_DEPLOYMENT_PLAN.md"
else
    echo "✗ Deployment failed!"
    echo "======================================"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check error messages above"
    echo "2. Verify gcloud is configured: gcloud config list"
    echo "3. Verify project is set: gcloud config get-value project"
    echo "4. Check Cloud Run API is enabled"
    exit 1
fi
