# Frontend API Configuration

## Production API URL

The frontend is now configured to use the production Cloud Run API by default:

**Production API**: `https://consultantos-api-187550875653.us-central1.run.app`

## Configuration Files Updated

### Core Configuration Files
1. **`next.config.js`** - Defaults to production API in production mode
2. **`Dockerfile`** - Default build arg set to production API
3. **`lib/api.ts`** - Main API client uses production URL in production
4. **`lib/strategic-intelligence-api.ts`** - Strategic intelligence API client
5. **`lib/mvp-api.ts`** - MVP demo API client
6. **`app/api/notifications.ts`** - Notifications API client

### Environment Files
- **`.env.production.local`** - Production API URL for local testing
- **`.env.local.example`** - Template for local development

## How It Works

### Priority Order
1. **Environment Variable** (`NEXT_PUBLIC_API_URL`) - Highest priority
2. **Production Default** - If `NODE_ENV === 'production'` → Production API
3. **Development Default** - Otherwise → `http://localhost:8080`

### For Local Development
Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

### For Production Deployment
The frontend will automatically use the production API URL when:
- Built with `NODE_ENV=production`
- Deployed to Cloud Run (environment variable is set)
- Running in production mode

## Updating the Deployed Frontend

If you need to update the deployed frontend service:

```bash
gcloud run services update consultantos-frontend \
  --region us-central1 \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app" \
  --project gen-lang-client-0079292313
```

## Testing

To test locally against production API:
```bash
cd frontend
NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app npm run dev
```

Or use the `.env.production.local` file (already created).

## Verification

After deployment, verify the frontend is using the correct API:
1. Open browser DevTools → Network tab
2. Check API requests - they should go to `consultantos-api-187550875653.us-central1.run.app`
3. No more `localhost:8080` errors in console
