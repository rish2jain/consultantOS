#!/bin/bash
# Setup script for Google Secret Manager
# This script creates secrets in Secret Manager and grants Cloud Run access

set -e

# Get project ID from environment variable or gcloud config
if [ -n "$GCP_PROJECT_ID" ]; then
    PROJECT_ID="$GCP_PROJECT_ID"
else
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ ERROR: GCP project ID is required"
        echo "   Set GCP_PROJECT_ID environment variable:"
        echo "   export GCP_PROJECT_ID=your-project-id"
        echo ""
        echo "   Or configure gcloud default project:"
        echo "   gcloud config set project your-project-id"
        exit 1
    fi
fi

echo "🔐 Setting up Google Secret Manager for ConsultantOS"
echo "Project ID: $PROJECT_ID"

# Set the project
gcloud config set project "$PROJECT_ID"

# Enable Secret Manager API
echo "📦 Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com

# Function to create or update secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    echo "🔑 Creating/updating secret: $secret_name"
    
    # Check if secret exists
    if gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        echo "   Secret exists, adding new version..."
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --data-file=- \
            --project="$PROJECT_ID"
    else
        echo "   Creating new secret..."
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --data-file=- \
            --replication-policy="automatic" \
            --project="$PROJECT_ID"
    fi
}

# Get secret values (prompt if not set)
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Enter your Gemini API key:"
    read -s GEMINI_API_KEY
fi

if [ -z "$TAVILY_API_KEY" ]; then
    echo "Enter your Tavily API key:"
    read -s TAVILY_API_KEY
fi

# Create secrets
create_secret "gemini-api-key" "$GEMINI_API_KEY"
create_secret "tavily-api-key" "$TAVILY_API_KEY"

# Get the default Cloud Run service account
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "🔓 Granting Secret Manager access to Cloud Run service account..."
echo "   Service Account: $SERVICE_ACCOUNT"

# Grant access to secrets
for secret in "gemini-api-key" "tavily-api-key"; do
    echo "   Granting access to $secret..."
    gcloud secrets add-iam-policy-binding "$secret" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor" \
        --project="$PROJECT_ID" \
        --quiet || echo "   ⚠️  Policy may already exist"
done

# Also grant access to custom service accounts if they exist
for service in "consultantos-api" "consultantos-agent" "consultantos-reporting" "consultantos-task"; do
    SERVICE_ACCOUNT="${service}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Check if service account exists
    if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" &>/dev/null; then
        echo "   Granting access to custom service account: $SERVICE_ACCOUNT"
        for secret in "gemini-api-key" "tavily-api-key"; do
            gcloud secrets add-iam-policy-binding "$secret" \
                --member="serviceAccount:${SERVICE_ACCOUNT}" \
                --role="roles/secretmanager.secretAccessor" \
                --project="$PROJECT_ID" \
                --quiet || echo "   ⚠️  Policy may already exist"
        done
    fi
done

echo ""
echo "✅ Secret Manager setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify secrets exist:"
echo "      gcloud secrets list --project=$PROJECT_ID"
echo ""
echo "   2. Test secret access:"
echo "      gcloud secrets versions access latest --secret=gemini-api-key --project=$PROJECT_ID"
echo ""
echo "   3. Deploy to Cloud Run (secrets will be automatically mounted):"
echo "      gcloud builds submit --config cloudbuild.yaml"
echo ""

