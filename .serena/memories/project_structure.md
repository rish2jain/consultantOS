# Project Structure

## Root Directory
```
ConsultantOS/
├── consultantos/          # Main backend package
├── frontend/              # Next.js frontend application
├── tests/                 # Backend test suite (mirrors consultantos/)
├── docs/                  # Project documentation
├── claudedocs/            # Claude-specific reports and analyses
├── main.py                # Backend entry point
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── Dockerfile             # Container configuration
├── cloudbuild.yaml        # GCP Cloud Build config
└── .env                   # Environment variables
```

## Backend Package (consultantos/)

### Core Modules
```
consultantos/
├── agents/                # 5 specialized agents
│   ├── base_agent.py          # BaseAgent abstract class
│   ├── research_agent.py      # Web research via Tavily
│   ├── market_agent.py        # Market trends via pytrends
│   ├── financial_agent.py     # Financial data (yfinance, SEC)
│   ├── framework_agent.py     # Strategic framework analysis
│   └── synthesis_agent.py     # Executive summary generation
│
├── orchestrator/          # Multi-agent coordination
│   └── analysis_orchestrator.py  # Phased execution + caching
│
├── api/                   # FastAPI endpoints (thin layer)
│   ├── main.py                # App setup, CORS, rate limiting
│   ├── user_endpoints.py      # User management
│   ├── template_endpoints.py  # Template management
│   ├── sharing_endpoints.py   # Report sharing
│   ├── versioning_endpoints.py # Version control
│   ├── comments_endpoints.py  # Comments system
│   ├── community_endpoints.py # Community features
│   └── analytics_endpoints.py # Analytics tracking
│
├── models/                # Pydantic domain models (shared)
│   └── *.py                   # Request/response models
│
├── tools/                 # External data integrations
│   ├── tavily_tool.py         # Tavily API wrapper
│   ├── trends_tool.py         # Google Trends
│   ├── financial_tool.py      # yfinance + SEC EDGAR
│   └── ...
│
├── reports/               # PDF generation and exports
│   ├── pdf_generator.py       # ReportLab PDF creation
│   ├── json_export.py         # JSON export
│   ├── excel_export.py        # Excel export
│   └── word_export.py         # Word export
│
├── visualizations/        # Chart generation
│   └── plotly_charts.py       # Plotly chart rendering
│
├── jobs/                  # Async job queue
│   ├── job_queue.py           # Job management
│   └── worker.py              # Background worker
│
├── services/              # Cross-cutting services
│   └── email_service.py       # Email notifications
│
├── utils/                 # Utilities
│   ├── validators.py          # Input validation
│   ├── sanitizers.py          # String sanitization
│   ├── retry.py               # Retry logic
│   └── circuit_breaker.py     # Circuit breaker pattern
│
├── cache.py               # Multi-level caching
├── storage.py             # Cloud Storage integration
├── database.py            # Firestore database layer
├── auth.py                # API key authentication
├── monitoring.py          # Structured logging
├── config.py              # Configuration management
├── prompts.py             # LLM prompts
└── models.py              # Shared Pydantic models
```

## Frontend Structure (frontend/)
```
frontend/
├── app/                   # Next.js 14 app directory
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Home page
│   ├── register/              # Registration
│   └── ...
├── components/            # React components
│   ├── ui/                    # Reusable UI components
│   └── features/              # Feature-specific components
├── public/                # Static assets
├── package.json           # Node dependencies
├── tsconfig.json          # TypeScript config
├── tailwind.config.js     # Tailwind CSS config
└── next.config.js         # Next.js config
```

## Tests Structure (tests/)
```
tests/
├── test_agents.py         # Agent unit tests
├── test_api.py            # API endpoint tests
├── test_models.py         # Pydantic model tests
├── test_orchestrator.py   # Orchestrator tests
├── test_tools.py          # Data tool tests
├── test_cache.py          # Caching tests
└── conftest.py            # Pytest fixtures
```

## Key Architectural Layers

### 1. API Layer (api/)
- **Purpose**: Thin validation, auth, and delegation layer
- **Responsibilities**: Input validation, authentication, rate limiting, routing
- **Pattern**: No business logic - delegate to agents/orchestrator

### 2. Business Logic Layer (agents/, orchestrator/)
- **Purpose**: Core analysis and coordination
- **Responsibilities**: Multi-agent orchestration, data analysis, framework application
- **Pattern**: BaseAgent inheritance, async execution, graceful degradation

### 3. Data Layer (tools/, cache.py, database.py, storage.py)
- **Purpose**: External data access and persistence
- **Responsibilities**: API integration, caching, database ops, cloud storage
- **Pattern**: Tool abstraction, multi-level caching, optional GCP services

### 4. Presentation Layer (reports/, visualizations/)
- **Purpose**: Output generation
- **Responsibilities**: PDF generation, chart creation, data export
- **Pattern**: Graceful rendering failures, multiple export formats

## Configuration Files

- **pytest.ini**: Test discovery and async mode configuration
- **Dockerfile**: Multi-stage build for Cloud Run deployment
- **cloudbuild.yaml**: GCP Cloud Build CI/CD pipeline
- **.env**: Environment variables (not committed)
- **.gitignore**: Git exclusions
- **requirements.txt**: Python package dependencies
- **package.json**: Frontend dependencies and scripts
