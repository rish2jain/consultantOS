# Suggested Commands

## Backend Development

### Start Server
```bash
# With auto-reload (development)
python main.py

# Or with uvicorn directly
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### Testing
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=consultantos

# Run specific test file
pytest tests/test_agents.py -v

# Run specific test
pytest tests/test_agents.py::test_research -v

# Generate HTML coverage report
pytest tests/ --cov=consultantos --cov-report=html
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Update requirements after adding packages
pip freeze > requirements.txt
```

### Environment Setup
```bash
# Create .env file with required variables
TAVILY_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Optional GCP variables
GCP_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
LOG_LEVEL=INFO
RATE_LIMIT_PER_HOUR=10
```

## Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server (port 3000)
npm run dev

# Production build
npm run build

# Run production server
npm run start

# Run ESLint
npm run lint
```

## Deployment

### Deploy to Cloud Run
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"
```

## Health Checks & API Testing

### Health Check
```bash
curl http://localhost:8080/health
```

### API Documentation
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Test Analysis Endpoint
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

## Utility Commands (Darwin/macOS)

### Git
```bash
git status                    # Check status
git branch                    # List branches
git checkout -b feature/name  # Create feature branch
git diff                      # Review changes
git add .                     # Stage all changes
git commit -m "message"       # Commit changes
```

### File Operations
```bash
ls -la                        # List files with details
find . -name "*.py"          # Find Python files
grep -r "search_term" .      # Search in files
tree -L 2                    # Show directory tree (if installed)
```

### Process Management
```bash
lsof -i :8080                # Check what's using port 8080
kill -9 <pid>                # Kill process by PID
ps aux | grep python         # Find Python processes
```

## Quick Reference

### Start Full Stack Development
```bash
# Terminal 1: Backend
python main.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Run Complete Quality Checks
```bash
# Backend
pytest tests/ -v --cov=consultantos

# Frontend
cd frontend && npm run lint
```
