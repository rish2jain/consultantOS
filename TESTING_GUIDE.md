# ConsultantOS Testing Guide

## ✅ Test Results

All core features are working! Here's what was tested:

- ✅ **Health Check**: Backend is healthy and responding
- ✅ **User Registration**: Successfully created test account
- ✅ **User Login**: Authentication working correctly
- ✅ **Reports Endpoint**: Accessible and returning data
- ✅ **Metrics Endpoint**: Working and showing statistics
- ✅ **Silent Auth**: Endpoint responding correctly

## 🧪 Test Account

A test account has been created for you:

- **Email**: `test@consultantos.com`
- **Password**: `TestPassword123!`

## 🚀 How to Test

### 1. Test the Dashboard (Frontend)

1. **Open the dashboard**: http://localhost:3000
2. **Login** with the test account:
   - Email: `test@consultantos.com`
   - Password: `TestPassword123!`
3. **What you'll see**:
   - Metrics cards showing statistics
   - Reports table (currently empty - no reports generated yet)
   - Visualizations section (will show charts when reports exist)

### 2. Test via API (Command Line)

#### Quick Test Commands

```bash
# 1. Login and get API key
curl -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@consultantos.com",
    "password": "TestPassword123!"
  }'

# 2. List your reports (use the access_token from step 1)
curl -X GET "http://localhost:8080/reports" \
  -H "X-API-Key: YOUR_ACCESS_TOKEN"

# 3. Get metrics
curl -X GET "http://localhost:8080/metrics" \
  -H "X-API-Key: YOUR_ACCESS_TOKEN"
```

### 3. Test Analysis Generation (Requires API Keys)

To test the full analysis feature, you need to set API keys:

```bash
# Set API keys in your terminal
export TAVILY_API_KEY="your_tavily_key"
export GEMINI_API_KEY="your_gemini_key"

# Then restart the backend server, or run:
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS
python main.py
```

Then generate an analysis:

```bash
# Get API key first
API_KEY=$(curl -s -X POST "http://localhost:8080/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@consultantos.com", "password": "TestPassword123!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Generate analysis
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

### 4. Test via Interactive API Docs

1. **Open Swagger UI**: http://localhost:8080/docs
2. **Try endpoints**:
   - `/users/login` - Login to get API key
   - `/reports` - List your reports
   - `/metrics` - View system metrics
   - `/analyze` - Generate analysis (if API keys set)

## 📋 Test Checklist

- [x] Backend server running on port 8080
- [x] Frontend server running on port 3000
- [x] Health endpoint responding
- [x] User registration working
- [x] User login working
- [x] Reports endpoint accessible
- [x] Metrics endpoint accessible
- [ ] Dashboard login (test manually)
- [ ] Generate analysis (requires API keys)
- [ ] View reports in dashboard (after generating one)

## 🔑 Getting API Keys (Optional)

If you want to test the full analysis feature:

1. **Tavily API Key** (for web research):
   - Visit: https://tavily.com
   - Sign up and get your API key

2. **Google Gemini API Key** (for AI analysis):
   - Visit: https://makersuite.google.com/app/apikey
   - Create an API key

Then set them:
```bash
export TAVILY_API_KEY="your_key_here"
export GEMINI_API_KEY="your_key_here"
```

## 🐛 Troubleshooting

### Frontend not loading?
- Check: http://localhost:3000
- Make sure frontend dev server is running: `cd frontend && npm run dev`

### Backend not responding?
- Check: http://localhost:8080/health
- Make sure backend is running: `python main.py` or `uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080`

### Login fails?
- Make sure you're using: `test@consultantos.com` / `TestPassword123!`
- Or register a new account via the dashboard

### Analysis fails?
- Check that API keys are set: `echo $TAVILY_API_KEY $GEMINI_API_KEY`
- Check backend logs for error messages

## 📊 What to Test Next

1. **Dashboard Features**:
   - Login/logout
   - View metrics
   - View reports table
   - Click on reports to see details

2. **API Features** (via http://localhost:8080/docs):
   - Report sharing
   - Export formats (JSON, Excel, Word)
   - Report versioning
   - Comments
   - Templates

3. **Full Workflow**:
   - Generate an analysis
   - View it in the dashboard
   - Download the PDF
   - Share it with a link

## 🎯 Quick Test Script

Run the automated test script:

```bash
./test_app.sh
```

This will test all endpoints and give you a summary.

