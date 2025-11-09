# ConsultantOS Deployment - Implementation Checklist

Use this checklist to track your deployment fix implementation.

---

## Pre-Implementation (5 min)

- [ ] Read `DEPLOYMENT_ANALYSIS_README.md`
- [ ] Read `DEPLOYMENT_SUMMARY.md`
- [ ] Verify all .fixed files exist in project root
- [ ] Have `docker` installed and working: `docker --version`
- [ ] Have `git` configured: `git status`
- [ ] Have `gcloud` CLI installed: `gcloud --version`
- [ ] Verify GCP project is configured: `gcloud config get-value project`

---

## Choose Implementation Method

### Method A: Automated (Recommended - 5 min total)

- [ ] Navigate to project: `cd /Users/rish2jain/Documents/Hackathons/ConsultantOS`
- [ ] Run automation script: `bash DEPLOYMENT_QUICK_FIX.sh`
- [ ] Review proposed commit message
- [ ] Confirm push to remote
- [ ] Script performs:
  - [ ] Backups original files (*.backup)
  - [ ] Applies all .fixed files
  - [ ] Tests local Docker build
  - [ ] Commits changes to git
  - [ ] Pushes to remote master branch
- [ ] Skip to "Deployment Monitoring" section

### Method B: Manual Step-by-Step (15 min total)

#### Step 1: Backup Originals (2 min)
- [ ] `cp Dockerfile Dockerfile.backup`
- [ ] `cp services/api_service/Dockerfile services/api_service/Dockerfile.backup`
- [ ] `cp services/agent_service/Dockerfile services/agent_service/Dockerfile.backup`
- [ ] `cp services/reporting_service/Dockerfile services/reporting_service/Dockerfile.backup`
- [ ] `cp services/task_handler_service/Dockerfile services/task_handler_service/Dockerfile.backup`
- [ ] `cp cloudbuild.api.yaml cloudbuild.api.yaml.backup`
- [ ] `cp cloudbuild.agent.yaml cloudbuild.agent.yaml.backup`
- [ ] `cp cloudbuild.reporting.yaml cloudbuild.reporting.yaml.backup`
- [ ] `cp cloudbuild.task.yaml cloudbuild.task.yaml.backup`

#### Step 2: Apply Dockerfile Fixes (1 min)
- [ ] `cp Dockerfile.fixed Dockerfile`
- [ ] `cp services/api_service/Dockerfile.fixed services/api_service/Dockerfile`
- [ ] `cp services/agent_service/Dockerfile.fixed services/agent_service/Dockerfile`
- [ ] `cp services/reporting_service/Dockerfile.fixed services/reporting_service/Dockerfile`
- [ ] `cp services/task_handler_service/Dockerfile.fixed services/task_handler_service/Dockerfile`

#### Step 3: Apply Cloud Build Fixes (1 min)
- [ ] `cp cloudbuild.api.yaml.fixed cloudbuild.api.yaml`
- [ ] `cp cloudbuild.agent.yaml.fixed cloudbuild.agent.yaml`
- [ ] `cp cloudbuild.reporting.yaml.fixed cloudbuild.reporting.yaml`
- [ ] `cp cloudbuild.task.yaml.fixed cloudbuild.task.yaml`

#### Step 4: Review Requirements (1 min)
- [ ] Review `requirements.txt.recommended`
- [ ] Consider adding google-api-core pinning: `google-api-core>=1.33.0,<2.0.0`
- [ ] (Optional) Update requirements.txt with pinning

#### Step 5: Add Health Endpoint (2 min)
- [ ] Edit `consultantos/api/main.py`
- [ ] Add this code after FastAPI app initialization:
```python
@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "consultantos-api",
        "version": "1.0.0"
    }
```
- [ ] Repeat for each service's main.py (api_service, agent_service, etc.)

#### Step 6: Test Local Docker Build (5 min)
- [ ] Test build: `docker build -t consultantos:test -f Dockerfile .`
- [ ] Verify no compilation errors
- [ ] Test imports: `docker run --rm consultantos:test python -c "import kaleido; import reportlab; print('✓')"`
- [ ] Verify output shows: `✓`

#### Step 7: Commit and Push (3 min)
- [ ] `git add Dockerfile services/*/Dockerfile cloudbuild*.yaml`
- [ ] (Optional) `git add requirements.txt`
- [ ] `git commit -m "fix(deployment): Add missing system dependencies and secret configuration"`
- [ ] `git push origin master`
- [ ] Verify push completes without errors

### Method C: Deep Review (30 min total)

- [ ] Read full `DEPLOYMENT_ISSUES_ANALYSIS.md`
- [ ] Review each .fixed file in detail
- [ ] Manually make changes instead of copying
- [ ] Test each change independently
- [ ] Document any deviations
- [ ] Follow Method B steps

---

## Deployment Monitoring (10-15 min)

- [ ] Navigate to Cloud Build console or use CLI
- [ ] Get last build ID: `BUILD_ID=$(gcloud builds list --limit=1 --format='value(id)')`
- [ ] Monitor build: `gcloud builds log $BUILD_ID --stream`
- [ ] Watch for success indicators:
  - [ ] "Successfully built" message
  - [ ] Docker image pushed to GCR
  - [ ] Cloud Run deployment started
  - [ ] All steps completed (usually 10-15 min)

### Build Success Indicators
- [ ] No "error:" lines in logs
- [ ] No "FAILURE" status
- [ ] Final message shows: "Cloud Run deployment succeeded"
- [ ] All 4 services deployed (if using separate Cloud Build configs)

### Build Failure - Investigate
- [ ] Check error message in logs
- [ ] Common issues:
  - [ ] `ffi.h: No such file` → libffi-dev missing
  - [ ] `gcc: command not found` → build-essential missing
  - [ ] Import errors → Check requirements.txt
  - [ ] Secret not found → Verify secrets in Secret Manager
- [ ] See `DEPLOYMENT_FIX_IMPLEMENTATION.md` Troubleshooting section

---

## Post-Deployment Verification (5-10 min)

### Cloud Run Services Status
- [ ] Check services are running: `gcloud run services list`
- [ ] All 4 services should show status "OK" in green:
  - [ ] consultantos-api
  - [ ] consultantos-agent
  - [ ] consultantos-reporting
  - [ ] consultantos-task

### Health Check Verification
- [ ] Get API service URL: `gcloud run services describe consultantos-api --region=us-central1 --format='value(status.url)'`
- [ ] Test health endpoint: `curl https://<SERVICE_URL>/health`
- [ ] Verify response (should be JSON):
  ```json
  {"status":"healthy","service":"consultantos-api",...}
  ```
- [ ] Repeat for other services (agent, reporting, task)

### Log Verification
- [ ] Check for startup errors: `gcloud run logs read consultantos-api --region=us-central1 --limit=20`
- [ ] Look for lines like:
  - [ ] No "ModuleNotFoundError"
  - [ ] No "ImportError"
  - [ ] No "PermissionDenied"
  - [ ] No "AttributeError"

### API Response Test
- [ ] Test that API responds: `curl https://<SERVICE_URL>/docs`
- [ ] Should return HTML (Swagger UI)
- [ ] Verify no 500 errors

### Secret Access Verification
- [ ] Services should have access to API keys
- [ ] Check Cloud Run environment: `gcloud run services describe consultantos-api --region=us-central1 --format=json | jq '.spec.template.spec.containers[0].env'`
- [ ] Should show environment variables (though secrets are masked)

---

## Success Verification Checklist

When ALL of these are true, your deployment is fixed:

- [ ] Docker build completes successfully locally
- [ ] No "compilation failed" errors in Cloud Build logs
- [ ] Cloud Build deployment shows "SUCCESS"
- [ ] All 4 Cloud Run services show status "OK"
- [ ] Health endpoints return 200 OK with JSON response
- [ ] No ImportError or ModuleNotFoundError in logs
- [ ] API /docs endpoint returns Swagger UI (200 OK)
- [ ] No permission errors accessing secrets
- [ ] No startup errors in any service logs

**Deployment is COMPLETE when: All boxes above are checked ✓**

---

## Troubleshooting Quick Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `ffi.h: No such file` | Missing libffi-dev | Check Dockerfile has libffi-dev in apt-get |
| `gcc: command not found` | Missing build-essential | Check Dockerfile has build-essential |
| `ModuleNotFoundError` | Package not installed | Check requirements.txt is complete |
| Health check fails | No /health endpoint | Add @app.get("/health") to FastAPI |
| `PermissionDenied` accessing secrets | Service account missing permissions | Grant secretmanager.secretAccessor role |
| Build timeout | Docker build too slow | Increase build machine resources |

See `DEPLOYMENT_FIX_IMPLEMENTATION.md` Troubleshooting for detailed solutions.

---

## Rollback Plan (If Needed)

If something goes wrong, you can rollback:

```bash
# Restore original files
cp Dockerfile.backup Dockerfile
cp services/api_service/Dockerfile.backup services/api_service/Dockerfile
# ... etc for all files

# OR revert git commits
git revert <commit-hash>
git push origin master

# OR reset to previous state
git reset --hard HEAD~1
git push --force origin master
```

---

## Documentation References

- **Quick Overview**: `DEPLOYMENT_SUMMARY.md`
- **Step-by-Step Guide**: `DEPLOYMENT_FIX_IMPLEMENTATION.md`
- **Detailed Analysis**: `DEPLOYMENT_ISSUES_ANALYSIS.md`
- **Complete Index**: `DEPLOYMENT_ANALYSIS_README.md`
- **Automation Script**: `DEPLOYMENT_QUICK_FIX.sh`

---

## Notes Section

Use this space to document your implementation:

```
Date Started: _______________
Implementation Method: A / B / C
Issues Encountered: _______________
Resolution: _______________
Date Completed: _______________
Deployment Status: SUCCESS / FAILED
Notes: _______________
```

---

## Final Verification (Before Declaring Success)

Before you close this ticket, complete this final checklist:

- [ ] All deployment fixes applied
- [ ] All tests passing
- [ ] All services running ("OK" status)
- [ ] Health checks passing
- [ ] No errors in logs
- [ ] API responding to requests
- [ ] Documentation updated (if needed)
- [ ] Team notified of successful deployment
- [ ] Monitoring configured (if needed)
- [ ] Backup files stored safely
- [ ] Deployment process documented for future reference

---

**Deployment Fix Implementation: COMPLETE**

Estimated total time: 20-55 minutes depending on method chosen
Recommended method: Method A (Automated, 5 minutes)

Good luck! Your deployment should be working now. 🚀
