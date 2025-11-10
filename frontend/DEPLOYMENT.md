# Frontend Dashboard - Cloud Run Deployment Guide

This guide explains how to deploy the ConsultantOS Next.js frontend dashboard to Google Cloud Run.

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed (for local testing)
- Backend API deployed and accessible

## Quick Deploy

### Option 1: Using Cloud Build (Recommended)

```bash
# Set your project ID
export PROJECT_ID=your-project-id
export API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app

# Submit build
gcloud builds submit --config=cloudbuild.frontend.yaml \
  --substitutions=_API_URL=$API_URL \
  --project=$PROJECT_ID
```

### Option 2: Using gcloud run deploy (Direct)

```bash
# Navigate to project root
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS

# Set environment variables
export API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app
export PROJECT_ID=your-project-id
export REGION=us-central1

# Deploy
gcloud run deploy consultantos-frontend \
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
```

### Option 3: Manual Docker Build & Deploy

```bash
# Build the Docker image
cd frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app \
  -t gcr.io/$PROJECT_ID/consultantos-frontend:latest \
  -f Dockerfile .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/consultantos-frontend:latest

# Deploy to Cloud Run
gcloud run deploy consultantos-frontend \
  --image gcr.io/$PROJECT_ID/consultantos-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app"
```

## Configuration

### Environment Variables

The frontend needs the following environment variable:

- `NEXT_PUBLIC_API_URL`: Backend API URL (required)
  - Production: `https://consultantos-api-bdndyf33xa-uc.a.run.app`
  - Local: `http://localhost:8080`

### Build Arguments

When building the Docker image, you can pass:

- `NEXT_PUBLIC_API_URL`: API URL (defaults to `http://localhost:8080`)

## Local Testing

### Test Docker Build Locally

```bash
cd frontend

# Build image
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8080 \
  -t consultantos-frontend:local .

# Run container
docker run -p 3000:8080 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8080 \
  consultantos-frontend:local

# Access at http://localhost:3000
```

## Deployment Settings

### Recommended Cloud Run Settings

- **Memory**: 512Mi (minimum for Next.js)
- **CPU**: 1 (can scale to 2 for better performance)
- **Timeout**: 300 seconds (5 minutes)
- **Max Instances**: 10 (adjust based on traffic)
- **Min Instances**: 0 (for cost optimization) or 1 (for faster cold starts)

### Scaling Configuration

```bash
# Update scaling settings
gcloud run services update consultantos-frontend \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10 \
  --cpu-throttling
```

## Post-Deployment

### Get the Service URL

```bash
gcloud run services describe consultantos-frontend \
  --region us-central1 \
  --format 'value(status.url)'
```

### Update CORS on Backend

Ensure your backend API allows requests from the frontend URL:

```python
# In consultantos/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://consultantos-frontend-xxx.run.app",  # Add your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Verify Deployment

1. Visit the Cloud Run service URL
2. Check browser console for any errors
3. Test API connectivity by making a request
4. Verify environment variables are set correctly

## Troubleshooting

### Build Fails

**Issue**: Docker build fails with dependency errors

**Solution**:
```bash
# Clear npm cache and rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Runtime Errors

**Issue**: App crashes on startup

**Solution**:
- Check Cloud Run logs: `gcloud run services logs read consultantos-frontend --region us-central1`
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Ensure backend API is accessible from Cloud Run

### CORS Errors

**Issue**: Browser shows CORS errors when calling API

**Solution**:
- Update backend CORS settings to include frontend URL
- Verify `NEXT_PUBLIC_API_URL` matches backend URL exactly

### Slow Cold Starts

**Issue**: First request takes a long time

**Solution**:
```bash
# Set minimum instances to 1
gcloud run services update consultantos-frontend \
  --region us-central1 \
  --min-instances 1
```

## Cost Optimization

### Reduce Costs

1. **Set min-instances to 0** (default) - only pay when serving traffic
2. **Use CPU throttling** - reduces costs during low traffic
3. **Optimize memory** - start with 512Mi, increase only if needed
4. **Set max-instances** - prevent runaway scaling costs

### Monitor Usage

```bash
# View service metrics
gcloud run services describe consultantos-frontend \
  --region us-central1 \
  --format yaml
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Frontend

on:
  push:
    branches: [master]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud builds submit --config=cloudbuild.frontend.yaml \
            --substitutions=_API_URL=${{ secrets.API_URL }}
```

## Next Steps

1. Deploy the frontend using one of the methods above
2. Update backend CORS settings with the new frontend URL
3. Test the complete flow end-to-end
4. Set up custom domain (optional)
5. Configure monitoring and alerts

## Support

For issues or questions:
- Check Cloud Run logs
- Review Next.js build output
- Verify environment variables
- Test API connectivity

