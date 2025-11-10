# Local Testing Guide for ConsultantOS

This guide helps you test your code locally before deploying to avoid deployment failures.

## Quick Start

Run the comprehensive local test suite:

```bash
# Full test (includes Docker build and run)
./test_local_deployment.sh

# Or use Python directly
python3 test_local_deployment.py

# Skip Docker tests (faster, for quick validation)
python3 test_local_deployment.py --skip-docker
```

## What Gets Tested

### 1. Basic Validation

- ✅ **Critical Imports**: Verifies all required Python modules can be imported
- ✅ **Configuration**: Checks that configuration loads correctly
- ✅ **Dockerfile**: Validates Dockerfile exists and has required directives
- ✅ **Requirements.txt**: Checks requirements file is valid

### 2. Docker Validation (if Docker is available)

- ✅ **Docker Build**: Builds the Docker image locally
- ✅ **Docker Run**: Starts container and verifies it runs
- ✅ **Health Endpoints**: Tests `/health`, `/health/live`, `/health/ready`
- ✅ **API Documentation**: Verifies `/docs` and `/openapi.json` work

## Common Issues and Fixes

### Issue: Import Errors

**Symptom**: "Failed to import X module"

**Fix**:

```bash
# Install dependencies
pip install -r requirements.txt

# Check for missing packages
python3 -c "import consultantos.api.main"
```

### Issue: Docker Build Fails

**Symptom**: Docker build times out or fails

**Fix**:

1. Check Docker is running: `docker ps`
2. Check Dockerfile syntax: `docker build -t test .`
3. Review build logs for specific errors
4. Ensure all files are in the correct location

### Issue: Health Check Fails

**Symptom**: Container starts but health checks fail

**Fix**:

1. Check container logs: `docker logs consultantos-test`
2. Verify environment variables are set
3. Check if port 8080 is available: `lsof -i :8080`
4. Test health endpoint manually: `curl http://localhost:8080/health`

### Issue: Configuration Errors

**Symptom**: "Failed to load configuration"

**Fix**:

1. Check `.env` file exists (optional for local testing)
2. Verify `consultantos/config.py` is valid
3. Check for missing environment variables

## Manual Testing Steps

If automated tests pass, you can also manually verify:

### 1. Test Application Startup

```bash
# Start the application
python3 main.py

# In another terminal, test health
curl http://localhost:8080/health
```

### 2. Test Docker Build

**Note**: The example below uses `test-key` as placeholder values for the API keys. For real testing, you must replace `test-key` with your actual `GEMINI_API_KEY` and `TAVILY_API_KEY` values.

```bash
# Build the image
docker build -t consultantos:test .

# Run the container
# Replace 'test-key' with your actual API keys for real testing
docker run -d \
  --name consultantos-test \
  -p 8080:8080 \
  -e GEMINI_API_KEY=test-key \
  -e TAVILY_API_KEY=test-key \
  consultantos:test

# Check logs
docker logs consultantos-test

# Test health
curl http://localhost:8080/health

# Cleanup
docker stop consultantos-test
docker rm consultantos-test
```

### 3. Test API Endpoints

```bash
# Health check
curl http://localhost:8080/health

# Liveness probe
curl http://localhost:8080/health/live

# Readiness probe
curl http://localhost:8080/health/ready

# API docs
curl http://localhost:8080/docs
```

## Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All local tests pass: `./test_local_deployment.sh`
- [ ] Docker image builds successfully
- [ ] Container starts and health checks pass
- [ ] All environment variables are configured
- [ ] No import errors in logs
- [ ] API documentation is accessible

## Troubleshooting

### Docker Issues

```bash
# Check Docker status
docker info

# View container logs
docker logs consultantos-test

# Check container status
docker ps -a

# Remove old containers
docker container prune
```

### Port Conflicts

```bash
# Check if port is in use
lsof -i :8080

# Kill process using port (if needed)
kill -9 <PID>
```

### Python Environment

```bash
# Verify Python version (requires 3.11+)
python3 --version

# Check installed packages
pip list | grep consultantos

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Integration with CI/CD

You can integrate this into your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run Local Tests
  run: |
    python3 test_local_deployment.py --skip-docker

- name: Build Docker Image
  run: |
    docker build -t consultantos:${{ github.sha }} .
```

## Next Steps

After local tests pass:

1. **Commit your changes**: `git add . && git commit -m "Fix deployment issues"`
2. **Push to repository**: `git push origin main`
3. **Deploy**: Your CI/CD pipeline should now succeed

## Support

If tests fail and you can't identify the issue:

1. Check the detailed error messages in test output
2. Review container logs: `docker logs consultantos-test`
3. Check application logs for runtime errors
4. Verify all dependencies are correctly specified in `requirements.txt`
