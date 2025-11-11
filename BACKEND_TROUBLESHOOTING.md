# Backend Troubleshooting Guide

**Date**: 2025-11-10
**Issue**: Backend process running but not listening on port 8080

## Current Status

- ✅ Backend process exists (PID 7449)
- ❌ Process not listening on port 8080
- ❌ Health endpoint not responding
- ⚠️ Process may be stuck during startup

## Diagnosis

The uvicorn process is running but not accepting connections. This typically means:
1. The application is stuck during import/startup
2. There's an error preventing the server from binding to the port
3. The process is waiting for something (database connection, etc.)

## Solutions

### Option 1: Check the Terminal Output

Look at the terminal where you started `python main.py` or `uvicorn`. You should see:
- Any import errors
- Any startup errors
- The "Uvicorn running on..." message

### Option 2: Kill and Restart

```bash
# Kill existing processes
pkill -f "uvicorn.*8080"
pkill -f "main.py"

# Wait a moment
sleep 2

# Start fresh
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS
python main.py
```

### Option 3: Check for Import Errors

```bash
# Test if the app can be imported
python -c "from consultantos.api.main import app; print('Import successful')"
```

### Option 4: Run with Verbose Logging

```bash
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload --log-level debug
```

## Expected Startup Output

When the backend starts successfully, you should see:

```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
```

## Common Startup Issues

### 1. Missing Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables Missing
Check if `.env` file exists with required variables:
- `TAVILY_API_KEY`
- `GEMINI_API_KEY`

### 3. Port Already in Use (Different Process)
```bash
lsof -i :8080
# Kill the process using the port
kill -9 <PID>
```

### 4. Import Errors
Check for any Python import errors in the terminal output.

## Verification

Once the backend starts:

```bash
# Should return JSON with status
curl http://localhost:8080/health

# Should show API docs
open http://localhost:8080/docs
```

---

**Next Step**: Check the terminal where the backend is running for error messages.

