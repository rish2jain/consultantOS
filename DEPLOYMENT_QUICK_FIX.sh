#!/bin/bash
# ConsultantOS Deployment Quick Fix Script
#
# Usage: bash DEPLOYMENT_QUICK_FIX.sh
# This script automates all deployment fixes in one shot
#
# Prerequisites:
# - You have .fixed files in the project root
# - You have git configured for this repo
# - You have Docker installed for local testing
#
# What this does:
# 1. Backups all original files
# 2. Applies all fixes (Dockerfiles + Cloud Build configs)
# 3. Tests Docker build locally
# 4. Shows commit message for review
# 5. Optionally commits and pushes

set -e  # Exit on any error

# Derive project directory dynamically, allow override via environment variable
# Try git root first (if in a git repo), fall back to current working directory
if [ -z "$PROJECT_DIR" ]; then
    if command -v git &> /dev/null && git rev-parse --show-toplevel &> /dev/null; then
        PROJECT_DIR=$(git rev-parse --show-toplevel)
    else
        PROJECT_DIR=$(pwd)
    fi
fi

echo "================================================"
echo "ConsultantOS Deployment Quick Fix"
echo "================================================"
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."
cd "$PROJECT_DIR"

if [ ! -f "Dockerfile.fixed" ]; then
  echo "❌ Error: Dockerfile.fixed not found in $PROJECT_DIR"
  echo "   Make sure you have the fixed files downloaded"
  exit 1
fi

if ! command -v docker &> /dev/null; then
  echo "⚠️  Warning: Docker not found. Skipping local build test."
  echo "   You should test locally before pushing: docker build -t consultantos:test ."
fi

if ! command -v git &> /dev/null; then
  echo "❌ Error: git not found. Required for this script."
  exit 1
fi

echo "✓ Prerequisites check complete"
echo ""

# Backup originals
echo "2. Backing up original files..."
cp Dockerfile Dockerfile.backup || true
echo "   ✓ Dockerfile backed up"

for service in api_service agent_service reporting_service task_handler_service; do
  cp "services/$service/Dockerfile" "services/$service/Dockerfile.backup" || true
  echo "   ✓ services/$service/Dockerfile backed up"
done

for config in api agent reporting task; do
  cp "cloudbuild.$config.yaml" "cloudbuild.$config.yaml.backup" || true
  echo "   ✓ cloudbuild.$config.yaml backed up"
done

echo ""

# Apply fixes
echo "3. Applying fixes..."

cp Dockerfile.fixed Dockerfile
echo "   ✓ Applied root Dockerfile fix"

cp services/api_service/Dockerfile.fixed services/api_service/Dockerfile
cp services/agent_service/Dockerfile.fixed services/agent_service/Dockerfile
cp services/reporting_service/Dockerfile.fixed services/reporting_service/Dockerfile
cp services/task_handler_service/Dockerfile.fixed services/task_handler_service/Dockerfile
echo "   ✓ Applied all service Dockerfile fixes"

cp cloudbuild.api.yaml.fixed cloudbuild.api.yaml
cp cloudbuild.agent.yaml.fixed cloudbuild.agent.yaml
cp cloudbuild.reporting.yaml.fixed cloudbuild.reporting.yaml
cp cloudbuild.task.yaml.fixed cloudbuild.task.yaml
echo "   ✓ Applied all Cloud Build configuration fixes"

echo ""

# Test local Docker build
if command -v docker &> /dev/null; then
  echo "4. Testing Docker build locally..."
  if docker build -t consultantos:quick-test -f Dockerfile . > /tmp/docker_build.log 2>&1; then
    echo "   ✓ Docker build successful"

    # Test critical imports
    echo "   Testing critical package imports..."
    if docker run --rm consultantos:quick-test python -c "
import sys
print('Python version:', sys.version.split()[0])
import fastapi; print('FastAPI:', fastapi.__version__)
import pydantic; print('Pydantic:', pydantic.__version__)
import kaleido; print('Kaleido: available')
import reportlab; print('ReportLab: available')
print('\n✓ All critical packages present')
" > /tmp/docker_test.log 2>&1; then
      echo "   ✓ All critical packages available"
    else
      echo "   ⚠️  Warning: Some packages may be missing"
      tail -10 /tmp/docker_test.log
    fi
  else
    echo "   ❌ Docker build failed. Check logs:"
    tail -20 /tmp/docker_build.log
    echo ""
    echo "   This usually means:"
    echo "   - requirements.txt has unresolvable version conflicts"
    echo "   - A package is unavailable for python:3.11-slim"
    echo ""
    echo "   See DEPLOYMENT_ISSUES_ANALYSIS.md for detailed troubleshooting"
    exit 1
  fi
else
  echo "4. Skipping Docker build test (Docker not installed)"
  echo "   Test manually: docker build -t consultantos:test ."
fi

echo ""

# Show git status
echo "5. Changes to be committed:"
echo "================================================"
git diff --name-only
echo ""
echo "================================================"
echo ""

# Show commit message
echo "6. Proposed commit message:"
echo "================================================"
cat << 'EOF'
fix(deployment): Add missing system dependencies and secret configuration

CRITICAL FIX: Add system libraries required by Python packages
- build-essential: Required by reportlab and edgartools
- python3-dev: Required by reportlab C extensions
- libffi-dev: Required by kaleido and cryptography
- libssl-dev: Required by cryptography and reportlab
- curl: For health checks
- ca-certificates: For SSL/TLS connections

Fixes these build failures:
- "ffi.h: No such file or directory"
- "error: command 'x86_64-linux-gnu-gcc' failed"
- "ModuleNotFoundError" at startup

ADDITIONAL FIXES:
- Add --set-secrets to Cloud Build YAML for API key injection
- Add HEALTHCHECK directive to Dockerfile
- Pin google-api-core to prevent version conflicts
- Add /health endpoint documentation

Files changed:
- Dockerfile (root and all 4 service Dockerfiles)
- cloudbuild.api.yaml, cloudbuild.agent.yaml, cloudbuild.reporting.yaml, cloudbuild.task.yaml
- requirements.txt (add google-api-core pinning)

This fixes the Cloud Run deployment failures.
EOF
echo "================================================"
echo ""

# Ask to proceed
read -p "Do you want to commit and push these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "7. Committing and pushing..."

  git add Dockerfile \
           services/api_service/Dockerfile \
           services/agent_service/Dockerfile \
           services/reporting_service/Dockerfile \
           services/task_handler_service/Dockerfile \
           cloudbuild.api.yaml \
           cloudbuild.agent.yaml \
           cloudbuild.reporting.yaml \
           cloudbuild.task.yaml

  git commit -m "fix(deployment): Add missing system dependencies and secret configuration

CRITICAL FIX: Add system libraries required by Python packages
- build-essential: Required by reportlab and edgartools
- python3-dev: Required by reportlab C extensions
- libffi-dev: Required by kaleido and cryptography
- libssl-dev: Required by cryptography and reportlab
- curl: For health checks
- ca-certificates: For SSL/TLS connections

ADDITIONAL FIXES:
- Add --set-secrets to Cloud Build YAML for API key injection
- Add HEALTHCHECK to Dockerfile
- Pin google-api-core to prevent version conflicts

This fixes Cloud Run deployment failures."

  echo ""
  echo "Pushing to remote..."
  git push origin master

  echo ""
  echo "✓ Changes committed and pushed!"
  echo ""
  echo "Next steps:"
  echo "1. Monitor Cloud Build: gcloud builds log --stream"
  echo "2. Check Cloud Run services: gcloud run services list"
  echo "3. Test health endpoints: curl https://<SERVICE_URL>/health"

else
  echo "Skipped commit. You can commit manually when ready:"
  echo ""
  echo "git add Dockerfile services/*/Dockerfile cloudbuild*.yaml"
  echo "git commit -m '<message from above>'"
  echo "git push origin master"
fi

echo ""
echo "================================================"
echo "✓ Deployment quick fix complete!"
echo "================================================"
