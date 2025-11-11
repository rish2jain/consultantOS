# ConsultantOS Setup Guide

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter httpx installation issues, install packages individually:
```bash
pip install tavily-python pytrends yfinance edgartools finviz pandas-datareader reportlab plotly kaleido instructor --no-deps
pip install httpxthrottlecache hishel msgpack aiofiles filelock pyrate-limiter stamina --no-deps
```

### 2. Set Environment Variables

Create a `.env` file or export environment variables:

```bash
export TAVILY_API_KEY=your_tavily_api_key
export GEMINI_API_KEY=your_gemini_api_key
```

Or create `.env` file:
```bash
TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the Backend API

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

The API will be available at `http://localhost:8080`

### 4. Access API Documentation

Open your browser to:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Testing

Run backend tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=consultantos --cov-report=html
```

## Project Structure

```
consultantos/
├── agents/          # Agent implementations (Research, Market, Financial, Framework, Synthesis)
├── api/             # FastAPI endpoints (main, user, template, sharing, versioning, etc.)
├── models/          # Pydantic data models
├── tools/           # Data source integrations (Tavily, Trends, SEC, yfinance)
├── orchestrator/    # Multi-agent coordination
├── reports/         # PDF generation and exports
├── visualizations/  # Chart generation
├── utils/           # Utilities (retry, circuit breaker, validators, sanitize)
├── jobs/            # Async job processing
├── services/        # Services (email)
├── cache.py         # Multi-level caching
├── storage.py       # Cloud Storage integration
├── database.py      # Firestore database layer
├── auth.py          # API key authentication
├── monitoring.py    # Logging and metrics
└── config.py        # Configuration management

frontend/
├── app/             # Next.js app directory
├── components/      # React components
└── public/          # Static assets
```

## Deployment

### Backend to Cloud Run

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

**Note**: For production, use Google Secret Manager instead of environment variables:
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest
```

### Frontend to Vercel (Recommended)

```bash
cd frontend
vercel deploy
```

Or use other hosting services (Netlify, Cloudflare Pages, etc.)

## Configuration

### Environment Variables

**Required**:
- `TAVILY_API_KEY` - Tavily API key for web research
- `GEMINI_API_KEY` - Google Gemini API key for AI analysis

**Optional**:
- `GCP_PROJECT_ID` - Google Cloud Project ID (for Firestore and Cloud Storage)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON (for local development)
- `LOG_LEVEL` - Logging level (default: INFO)
- `RATE_LIMIT_PER_HOUR` - Rate limit per IP (default: 10)
- `FINNHUB_API_KEY` - Finnhub API key for financial data
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API key for technical indicators
- `LAOZHANG_API_KEY` - Grok API key (via laozhang.ai) for social media sentiment
- `REDDIT_CLIENT_ID` - Reddit API client ID for social media analysis
- `REDDIT_CLIENT_SECRET` - Reddit API client secret
- `TWITTER_BEARER_TOKEN` - Twitter API bearer token for social media analysis
- `GEMINI_MODEL` - Gemini model to use (default: gemini-1.5-flash-002)
- `LAOZHANG_MODEL` - Grok model to use (default: grok-4-fast-reasoning-latest)

## Troubleshooting

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- If httpx has issues, reinstall it: `pip install --force-reinstall httpx`

### API Key Errors
- Ensure `TAVILY_API_KEY` and `GEMINI_API_KEY` are set
- Check `.env` file exists and has correct values

### Module Not Found
- Install missing packages individually with `--no-deps` flag if needed
- Some packages (like edgartools) have complex dependencies - they're optional
- Check Python path: `python -c "import sys; print(sys.path)"`

### Port Already in Use
- Kill existing process: `lsof -ti:8080 | xargs kill` (macOS/Linux)
- Or change port in `main.py`: `uvicorn.run(..., port=8081)`

### Database Connection Issues
- Firestore is optional for development (uses in-memory fallback)
- For production, ensure `GCP_PROJECT_ID` is set
- Check service account credentials if using `GOOGLE_APPLICATION_CREDENTIALS`

### Frontend Connection Issues
- Ensure backend is running on port 8080
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` matches backend URL
- Verify CORS settings if accessing from different origin

### 5. Run the Frontend Dashboard (Optional)

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:3000`

**Frontend Features**:
- User authentication and registration
- Report history and management
- Usage statistics visualization
- API key management
- Report sharing and collaboration

**Environment Variables** (Frontend):
Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080
```

## Optional Dependencies

Some features work without all dependencies:
- SEC EDGAR: Optional (falls back gracefully if not available)
- Google Secret Manager: Optional (uses environment variables as fallback)
- Firestore Database: Optional (uses in-memory fallback for development)
- Social Media APIs: Optional (Reddit/Twitter - required for social media analysis)
- Grok API: Optional (required for advanced sentiment analysis)
- Celery + Redis: Optional (required for distributed task processing)
- Sentry: Optional (required for error tracking in production)

## Advanced Features

The following features require additional API keys:

- **Forecasting**: Uses financial data from Finnhub/Alpha Vantage
- **Social Media Analysis**: Requires Reddit and/or Twitter API keys
- **Grok Sentiment**: Requires LAOZHANG_API_KEY for advanced sentiment analysis
- **Wargaming**: Uses statistical libraries (scipy) - included in requirements.txt
- **Conversational AI**: Uses ChromaDB for RAG - included in requirements.txt

