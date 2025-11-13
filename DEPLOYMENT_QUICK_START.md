# ConsultantOS - Quick Deployment Guide

**For Google Cloud Run Hackathon Submission**

## 🚀 One-Command Deployment

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"

# Run automated deployment
./scripts/deploy.sh
```

## 📋 Pre-Deployment Checklist

1. **GCP Project Setup**
   ```bash
   gcloud projects create consultantos-hackathon
   gcloud config set project consultantos-hackathon
   ```

2. **Store API Keys**
   ```bash
   echo -n "YOUR_GEMINI_KEY" | gcloud secrets create gemini-api-key --data-file=-
   echo -n "YOUR_TAVILY_KEY" | gcloud secrets create tavily-api-key --data-file=-
   ```

3. **Create Service Account**
   ```bash
   gcloud iam service-accounts create consultantos-api-sa \
     --display-name="ConsultantOS API Service Account"
   ```

## 🎯 Hackathon Requirements Met

✅ **Cloud Run Deployment** - Both frontend and backend  
✅ **Multiple Services** (+0.4 pts) - Frontend + Backend on Cloud Run  
✅ **Google AI Models** (+0.4 pts) - Gemini 2.5 Flash  
✅ **Production-Ready** - Enterprise infrastructure  
✅ **Public Repository** - Full documentation  

## 📊 Architecture

```
Frontend (Next.js) → Cloud Run → Backend (FastAPI) → Cloud Run
                                              ↓
                                    Firestore + Cloud Storage
```

## 🔗 After Deployment

**Get URLs:**
```bash
# Backend
gcloud run services describe consultantos-api \
  --region us-central1 \
  --format 'value(status.url)'

# Frontend  
gcloud run services describe consultantos-frontend \
  --region us-central1 \
  --format 'value(status.url)'
```

**Test:**
```bash
# Health check
curl https://consultantos-api-xxx.run.app/health

# API docs
open https://consultantos-api-xxx.run.app/docs
```

## 📝 Full Documentation

See [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) for:
- Detailed step-by-step instructions
- Security configuration
- Monitoring setup
- Cost optimization
- Troubleshooting

## 🎉 Submission Checklist

- [ ] Both services deployed to Cloud Run
- [ ] Public URLs accessible
- [ ] Demo video recorded (≤3 min)
- [ ] Architecture diagram created
- [ ] README updated with deployment info
- [ ] GitHub repository is public

**Good luck! 🚀**

