#!/bin/bash

# ConsultantOS Cloud Run Deployment Script
# Automates deployment of both frontend and backend services

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-consultantos-hackathon}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="consultantos-api"
FRONTEND_SERVICE="consultantos-frontend"

# Validate PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ PROJECT_ID is not set. Please set GCP_PROJECT_ID environment variable.${NC}"
    exit 1
fi

# Service account email
SERVICE_ACCOUNT="consultantos-api-sa@$PROJECT_ID.iam.gserviceaccount.com"

echo -e "${GREEN}🚀 ConsultantOS Cloud Run Deployment${NC}"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Some features may not work.${NC}"
fi

# Set project
echo -e "${YELLOW}🔧 Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔌 Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    firestore.googleapis.com \
    storage-component.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    --quiet

# Check if secrets exist (try both naming conventions)
echo -e "${YELLOW}🔐 Checking secrets...${NC}"
GEMINI_SECRET=""
TAVILY_SECRET=""

# Try lowercase with hyphens first (preferred)
if gcloud secrets describe gemini-api-key --project=$PROJECT_ID &> /dev/null; then
    GEMINI_SECRET="gemini-api-key"
elif gcloud secrets describe GEMINI_API_KEY --project=$PROJECT_ID &> /dev/null; then
    GEMINI_SECRET="GEMINI_API_KEY"
else
    echo -e "${RED}❌ Secret 'gemini-api-key' or 'GEMINI_API_KEY' not found.${NC}"
    echo "Please create it first:"
    echo "  echo -n 'YOUR_KEY' | gcloud secrets create gemini-api-key --data-file=-"
    exit 1
fi

if gcloud secrets describe tavily-api-key --project=$PROJECT_ID &> /dev/null; then
    TAVILY_SECRET="tavily-api-key"
elif gcloud secrets describe TAVILY_API_KEY --project=$PROJECT_ID &> /dev/null; then
    TAVILY_SECRET="TAVILY_API_KEY"
else
    echo -e "${RED}❌ Secret 'tavily-api-key' or 'TAVILY_API_KEY' not found.${NC}"
    echo "Please create it first:"
    echo "  echo -n 'YOUR_KEY' | gcloud secrets create tavily-api-key --data-file=-"
    exit 1
fi

# Check for SESSION_SECRET (try both naming conventions)
SESSION_SECRET=""
if gcloud secrets describe session-secret --project=$PROJECT_ID &> /dev/null; then
    SESSION_SECRET="session-secret"
elif gcloud secrets describe SESSION_SECRET --project=$PROJECT_ID &> /dev/null; then
    SESSION_SECRET="SESSION_SECRET"
else
    echo -e "${RED}❌ Secret 'session-secret' or 'SESSION_SECRET' not found.${NC}"
    echo "Please create it first:"
    echo "  echo -n 'YOUR_SESSION_SECRET' | gcloud secrets create session-secret --data-file=-"
    exit 1
fi

echo -e "${GREEN}✅ Found secrets: $GEMINI_SECRET, $TAVILY_SECRET, $SESSION_SECRET${NC}"

# Check if service account exists
echo -e "${YELLOW}🔍 Checking service account...${NC}"
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID &> /dev/null; then
    echo -e "${RED}❌ Service account '$SERVICE_ACCOUNT' not found.${NC}"
    echo "Please create it first by running DEPLOYMENT_PLAN.md Step 1.3, or create it now:"
    echo "  gcloud iam service-accounts create consultantos-api-sa \\"
    echo "    --display-name='ConsultantOS API Service Account' \\"
    echo "    --project=$PROJECT_ID"
    exit 1
fi

# Deploy backend
echo -e "${GREEN}📦 Deploying backend API...${NC}"
gcloud run deploy $BACKEND_SERVICE \
    --source . \
    --region $REGION \
    --platform managed \
    --service-account $SERVICE_ACCOUNT \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production" \
    --set-secrets "GEMINI_API_KEY=$GEMINI_SECRET:latest,TAVILY_API_KEY=$TAVILY_SECRET:latest,SESSION_SECRET=$SESSION_SECRET:latest" \
    --project $PROJECT_ID \
    --quiet

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)

echo -e "${GREEN}✅ Backend deployed: $BACKEND_URL${NC}"

# Test backend health
echo -e "${YELLOW}🏥 Testing backend health...${NC}"
if curl -f -s "$BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    exit 1
fi

# Deploy frontend
echo -e "${GREEN}🎨 Deploying frontend dashboard...${NC}"
cd frontend

gcloud run deploy $FRONTEND_SERVICE \
    --source . \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "NEXT_PUBLIC_API_URL=$BACKEND_URL" \
    --project $PROJECT_ID \
    --quiet

cd ..

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
    --region $REGION \
    --format 'value(status.url)' \
    --project $PROJECT_ID)

echo -e "${GREEN}✅ Frontend deployed: $FRONTEND_URL${NC}"

# Summary
echo ""
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=========================================="
echo -e "${GREEN}Frontend URL:${NC} $FRONTEND_URL"
echo -e "${GREEN}Backend URL:${NC} $BACKEND_URL"
echo -e "${GREEN}API Docs:${NC} $BACKEND_URL/docs"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Update backend CORS to include: $FRONTEND_URL"
echo "2. Test the frontend: open $FRONTEND_URL"
echo "3. Verify API connectivity"
echo "4. Check Cloud Run logs if issues occur"
echo ""
echo -e "${GREEN}✅ Ready for hackathon submission!${NC}"

