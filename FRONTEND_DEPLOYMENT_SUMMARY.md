# Frontend Dashboard - Cloud Run Deployment Summary

✅ **Yes, the dashboard can be deployed to Cloud Run!** 

I've created all the necessary configuration files for deploying the Next.js frontend dashboard to Google Cloud Run.

## Files Created

1. **`frontend/Dockerfile`** - Multi-stage Docker build for Next.js
2. **`frontend/.dockerignore`** - Excludes unnecessary files from Docker build
3. **`frontend/next.config.js`** - Updated with `output: 'standalone'` for Cloud Run
4. **`cloudbuild.frontend.yaml`** - Cloud Build configuration for CI/CD
5. **`deploy-frontend.sh`** - Quick deployment script
6. **`frontend/DEPLOYMENT.md`** - Comprehensive deployment guide

## Quick Deploy

### Option 1: Using the Deployment Script (Easiest)

```bash
# Set environment variables
export GCP_PROJECT_ID=your-project-id
export API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app

# Run deployment script
./deploy-frontend.sh
```

### Option 2: Direct gcloud Command

```bash
gcloud run deploy consultantos-frontend \
  --source frontend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app"
```

### Option 3: Using Cloud Build

```bash
gcloud builds submit --config=cloudbuild.frontend.yaml \
  --substitutions=_API_URL=https://consultantos-api-bdndyf33xa-uc.a.run.app
```

## Important: Update Backend CORS

After deploying the frontend, you **must** update the backend CORS settings to allow the new frontend URL.

### Method 1: Environment Variable (Recommended)

Set the `CORS_ORIGINS` environment variable in Cloud Run:

```bash
# Get your frontend URL after deployment
FRONTEND_URL=$(gcloud run services describe consultantos-frontend \
  --region us-central1 \
  --format 'value(status.url)')

# Update backend CORS
gcloud run services update consultantos-api \
  --region us-central1 \
  --set-env-vars "CORS_ORIGINS=http://localhost:3000,${FRONTEND_URL}"
```

### Method 2: Update config.py

Alternatively, update `consultantos/config.py`:

```python
cors_origins: str = "http://localhost:3000,https://consultantos-frontend-xxx.run.app"
```

Then redeploy the backend.

## Configuration

### Environment Variables

The frontend needs:
- `NEXT_PUBLIC_API_URL` - Backend API URL (set during deployment)

### Cloud Run Settings

- **Memory**: 512Mi (minimum for Next.js)
- **CPU**: 1
- **Timeout**: 300 seconds
- **Max Instances**: 10
- **Port**: 8080 (Cloud Run sets this automatically)

## Testing

After deployment:

1. **Get the frontend URL**:
   ```bash
   gcloud run services describe consultantos-frontend \
     --region us-central1 \
     --format 'value(status.url)'
   ```

2. **Visit the URL** in your browser

3. **Check browser console** for any errors

4. **Test API connectivity** by making a request

## Troubleshooting

### Build Fails
- Check `frontend/Dockerfile` syntax
- Verify `package.json` is valid
- Ensure Node.js 20 is available

### Runtime Errors
- Check Cloud Run logs: `gcloud run services logs read consultantos-frontend --region us-central1`
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Ensure backend is accessible

### CORS Errors
- Update backend CORS settings (see above)
- Verify frontend URL matches exactly in CORS config

## Cost Estimate

- **512Mi memory, 1 CPU**: ~$0.00002400 per request-second
- **With 0 min instances**: Only pay when serving traffic
- **Estimated monthly cost**: $5-20 for low-medium traffic

## Next Steps

1. ✅ Deploy frontend using one of the methods above
2. ✅ Update backend CORS settings
3. ✅ Test the complete flow
4. ⏭️ Set up custom domain (optional)
5. ⏭️ Configure monitoring and alerts

## Documentation

See `frontend/DEPLOYMENT.md` for detailed deployment instructions, troubleshooting, and advanced configuration options.

