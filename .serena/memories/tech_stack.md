# Technology Stack

## Backend
- **Framework**: FastAPI (0.120.4) with Uvicorn
- **Language**: Python 3.11+
- **AI/LLM**: Google Gemini AI + Instructor for structured outputs
- **Data Validation**: Pydantic (2.12.5) with type hints

## Data Sources
- **Web Research**: Tavily API
- **Market Trends**: pytrends (Google Trends)
- **Financial Data**: yfinance, edgartools (SEC EDGAR), finviz, pandas-datareader
- **Data Processing**: pandas (2.1.0+)

## Storage & Caching
- **Vector Store**: ChromaDB (0.4.0+)
- **Disk Cache**: diskcache (5.6.0+)
- **Database**: Google Cloud Firestore (optional)
- **Cloud Storage**: Google Cloud Storage (optional)

## Report Generation
- **PDF**: ReportLab (4.0.0+)
- **Visualizations**: Plotly (5.18.0+) with Kaleido rendering

## API & Security
- **Rate Limiting**: slowapi (0.1.9+)
- **Authentication**: API key via headers/query params
- **File Upload**: python-multipart

## Google Cloud Platform (Optional)
- Cloud Run (deployment)
- Firestore (database)
- Cloud Storage (file storage)
- Secret Manager (secrets)
- Cloud Logging (logging)

## Frontend
- **Framework**: Next.js 14.2.32
- **Language**: TypeScript 5.3+
- **UI Library**: React 18.2
- **Data Fetching**: TanStack React Query 5.0, Axios
- **Styling**: Tailwind CSS 3.3
- **Charts**: Recharts 2.10
- **Icons**: Lucide React 0.294

## Testing
- **Framework**: pytest (7.4.0+)
- **Async Testing**: pytest-asyncio (0.21.0+)
- **Coverage**: pytest-cov (4.1.0+)
- **Mode**: asyncio_mode = auto

## Development
- **Environment**: python-dotenv (1.0.0+)
- **Logging**: structlog (23.2.0+)
- **HTTP Client**: httpx (0.25.0+)
