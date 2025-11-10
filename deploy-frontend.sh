#!/bin/bash
# Quick deployment script for ConsultantOS Frontend to Cloud Run

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
API_URL=${API_URL:-"https://consultantos-api-bdndyf33xa-uc.a.run.app"}
SERVICE_NAME="consultantos-frontend"

# Validate PROJECT_ID is set and not the placeholder
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
    echo "❌ Error: PROJECT_ID is not set or still set to placeholder value"
    echo ""
    echo "Please set GCP_PROJECT_ID environment variable:"
    echo "  export GCP_PROJECT_ID=your-actual-project-id"
    echo ""
    echo "Or set PROJECT_ID directly:"
    echo "  export PROJECT_ID=your-actual-project-id"
    echo ""
    exit 1
fi

echo "🚀 Deploying ConsultantOS Frontend to Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "API URL: $API_URL"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    exit 1
fi

# Set project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Deploy to Cloud Run
echo "🔨 Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source frontend \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "NEXT_PUBLIC_API_URL=$API_URL" \
  --project $PROJECT_ID

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "🌐 Frontend URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Update backend CORS to allow: $SERVICE_URL"
echo "2. Test the frontend at: $SERVICE_URL"
echo "3. Verify API connectivity"

