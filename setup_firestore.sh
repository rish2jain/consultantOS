#!/bin/bash
# Setup script for Firestore configuration

echo "🔧 Configuring Firestore for ConsultantOS..."

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Install Google Cloud SDK: https://cloud.google.com/sdk"
    exit 1
fi

# Get GCP project ID
export GCP_PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ GCP project not configured. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ GCP Project ID: $GCP_PROJECT_ID"

# Check if Firestore API is enabled
if ! gcloud services list --enabled --project=$GCP_PROJECT_ID | grep -q firestore.googleapis.com; then
    echo "📦 Enabling Firestore API..."
    gcloud services enable firestore.googleapis.com --project=$GCP_PROJECT_ID
    echo "✅ Firestore API enabled"
else
    echo "✅ Firestore API already enabled"
fi

# Check if database exists
if ! gcloud firestore databases list --project=$GCP_PROJECT_ID 2>/dev/null | grep -q "(default)"; then
    echo "📦 Creating Firestore database..."
    if gcloud firestore databases create --location=us-central1 --type=firestore-native --project=$GCP_PROJECT_ID 2>&1; then
        echo "✅ Firestore database created (may take 1-2 minutes to be fully available)"
    else
        echo "❌ Failed to create Firestore database. Check the error message above."
        exit 1
    fi
else
    echo "✅ Firestore database already exists"
fi

# Set environment variable
export GCP_PROJECT_ID=$GCP_PROJECT_ID
echo ""
echo "✅ Firestore configuration complete!"
echo ""
echo "To use Firestore, set the environment variable:"
echo "  export GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo ""
echo "Or add to your .env file:"
echo "  GCP_PROJECT_ID=$GCP_PROJECT_ID"
echo ""


