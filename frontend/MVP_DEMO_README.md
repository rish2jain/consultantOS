# ConsultantOS MVP Demo

## Overview
This is the Hackathon MVP demo showcasing ConsultantOS's AI-powered competitive intelligence platform.

## Features

### 1. AI Chat Assistant
- **Location**: Left panel of `/mvp-demo`
- **Backend**: `POST /mvp/chat`
- **Features**:
  - Real-time AI responses powered by Google Gemini 1.5
  - Conversation history tracking
  - Auto-scrolling message view
  - Loading states and error handling
  - Mobile-responsive design

### 2. Market Forecast Visualization
- **Location**: Right panel of `/mvp-demo`
- **Backend**: `GET /mvp/forecast?periods=30`
- **Features**:
  - Interactive line chart with confidence intervals
  - Configurable time periods (7, 14, 30, 90 days)
  - Real-time statistics (current value, predicted value, % change)
  - Confidence score display
  - Recharts-powered visualization

## File Structure

```
frontend/
├── app/
│   ├── mvp-demo/
│   │   └── page.tsx              # Main MVP demo page
│   └── components/
│       ├── ChatDemo.tsx          # Chat interface component
│       └── ForecastChart.tsx     # Forecast visualization
├── lib/
│   └── mvp-api.ts                # API client for MVP endpoints
└── MVP_DEMO_README.md            # This file
```

## Running the Demo

### Prerequisites
1. Backend API running on `http://localhost:8080`
2. Node.js and npm installed

### Steps
1. **Start the backend** (from project root):
   ```bash
   python main.py
   ```

2. **Start the frontend** (from frontend directory):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the demo**:
   - Open browser to `http://localhost:3000/mvp-demo`
   - Or click "Try MVP Demo" from the homepage

## API Endpoints Used

### Chat
```typescript
POST /mvp/chat
Request: {
  query: string,
  conversation_id: string
}
Response: {
  response: string,
  conversation_id: string,
  timestamp: string
}
```

### Forecast
```typescript
GET /mvp/forecast?periods=30
Response: {
  dates: string[],
  predictions: number[],
  lower_bound: number[],
  upper_bound: number[],
  confidence: number
}
```

### Health Check
```typescript
GET /mvp/health
Response: {
  status: "healthy",
  timestamp: string
}
```

## Component Details

### ChatDemo Component
- **State Management**: Uses React hooks (useState, useRef, useEffect)
- **Features**:
  - Message history with user/AI distinction
  - Auto-scroll to latest message
  - Keyboard shortcuts (Enter to send)
  - Loading indicators
  - Error handling with retry
  - Responsive layout

### ForecastChart Component
- **Visualization**: Recharts AreaChart + LineChart
- **Features**:
  - Confidence interval shading
  - Interactive tooltips
  - Period selector dropdown
  - Statistics cards (current, predicted, % change)
  - Gradient fills for visual appeal
  - Responsive design

### mvp-api Client
- **Error Handling**: Try/catch with custom error messages
- **Type Safety**: TypeScript interfaces for all API calls
- **Configuration**: Environment-based API URL (`NEXT_PUBLIC_API_URL`)

## Styling

- **Framework**: Tailwind CSS
- **Icons**: Lucide React
- **Color Scheme**:
  - Blue/Purple gradients for headers
  - White cards with subtle shadows
  - Gray scale for text hierarchy
- **Responsive**: Mobile-first design with breakpoints

## Hackathon Demo Tips

### For Presentation:
1. Start with homepage -> Click "Try MVP Demo"
2. Demonstrate chat:
   - Ask: "What is competitive intelligence?"
   - Show real-time response
   - Show conversation history
3. Demonstrate forecast:
   - Change time period (7 days -> 90 days)
   - Point out confidence intervals
   - Highlight statistics (% change)
4. Show responsive design (resize browser)
5. Mention tech stack (Google Cloud Run, Gemini 1.5)

### Troubleshooting:
- **Backend not connecting**: Ensure `python main.py` is running
- **CORS errors**: Backend CORS is configured for localhost:3000
- **Chart not rendering**: Check browser console, ensure Recharts is installed
- **API errors**: Check Network tab in DevTools

## Future Enhancements (Post-Hackathon)

1. **Chat Features**:
   - Export conversation as PDF
   - Save conversation history
   - Multi-language support
   - Voice input/output

2. **Forecast Features**:
   - Multiple metrics (revenue, market share, etc.)
   - Scenario comparison
   - Historical data overlay
   - Export charts as images

3. **General**:
   - User authentication
   - Dashboard with multiple monitors
   - Alert system integration
   - Real-time data updates via WebSocket

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Backend**: FastAPI, Python, Google Gemini 1.5
- **Deployment**: Google Cloud Run

## Contact

For questions or issues during the hackathon, reach out to the development team.

---
Built for the November 2025 Hackathon MVP Demo
