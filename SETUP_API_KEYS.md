# Setting Up API Keys for ConsultantOS

To generate real business analyses, you need two API keys:

## 1. Google Gemini API Key (Required)

**For AI-powered analysis**

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## 2. Tavily API Key (Required)

**For web research**

1. Visit: https://tavily.com
2. Sign up for a free account
3. Go to your dashboard
4. Copy your API key

## Setting the Keys

### Option 1: Environment Variables (Recommended)

```bash
export TAVILY_API_KEY="your_tavily_key_here"
export GEMINI_API_KEY="your_gemini_key_here"
```

Then restart the backend server.

### Option 2: .env File

Create a `.env` file in the project root:

```bash
TAVILY_API_KEY=your_tavily_key_here
GEMINI_API_KEY=your_gemini_key_here
```

The system will automatically load these.

## After Setting Keys

1. Restart the backend server:
   ```bash
   # Stop current server (Ctrl+C)
   # Then restart:
   python main.py
   ```

2. Try generating an analysis again!

