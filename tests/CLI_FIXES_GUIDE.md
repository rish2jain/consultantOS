# CLI Fixes Guide - Step by Step

Based on the detailed analysis in `CLI_ISSUES_DETAILED.md`, here are step-by-step fixes for each CLI tool.

## 🔧 Quick Fix Summary

| CLI | Issue | Quick Fix | Time |
|-----|-------|-----------|------|
| **Claude** | Needs auth | Run `claude auth` | 2 min |
| **Codex** | TTY issue | Use API instead | N/A |
| **Gemini** | Quota + Config | Wait or use API | N/A |

---

## 1. Fix Claude CLI (EASIEST - Recommended)

### Step 1: Authenticate
```bash
claude auth
```
This will open a browser or prompt for authentication.

### Step 2: Verify Authentication
```bash
claude "test" --print
```
Should return a response (not "Invalid API key").

### Step 3: Test with Image
```bash
TEST_IMAGE="tests/e2e/screenshots/scenario1-1-access-app-2025-11-08T20-17-52-674Z.png"
claude "Analyze this UI screenshot at $TEST_IMAGE. Provide JSON with ui_components, accessibility_issues, and design_recommendations." --print
```

### Step 4: Update Analyzer
If Claude works after auth, the analyzer should automatically use it (it's in the auto-detect priority).

**Expected Result**: ✅ Claude CLI should work after authentication

---

## 2. Fix Codex CLI (COMPLEX - Not Recommended)

### The Problem
Codex requires an interactive terminal (TTY). Python's `subprocess.run()` with `capture_output=True` doesn't provide a TTY.

### Option A: Use Pseudo-TTY (Complex)
```python
import pty
import os
import select

def run_codex_with_pty(prompt, image_path):
    master, slave = pty.openpty()
    
    try:
        process = subprocess.Popen(
            ["codex", prompt, "--image", image_path],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            start_new_session=True
        )
        os.close(slave)
        
        output = b""
        while True:
            if process.poll() is not None:
                break
            if select.select([master], [], [], 0.1)[0]:
                data = os.read(master, 1024)
                if not data:
                    break
                output += data
        
        return output.decode('utf-8')
    finally:
        os.close(master)
```

**Complexity**: High
**Reliability**: Medium (may still have issues)

### Option B: Use OpenAI API Directly (Recommended)
Instead of Codex CLI, use OpenAI's API with GPT-4 Vision:
```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"file://{image_path}"}}
        ]
    }]
)
```

**Complexity**: Low
**Reliability**: High

---

## 3. Fix Gemini CLI (WAIT or USE API)

### The Problem
1. **Quota Exhausted**: API quota limit reached (resets in ~23 hours)
2. **MCP Config Error**: MCP server 'env' has invalid configuration

### Option A: Wait for Quota Reset
```bash
# Check current quota status
gemini "test" 2>&1 | grep -i quota

# Wait ~23 hours for reset
```

### Option B: Fix MCP Configuration
```bash
# Check MCP config
gemini mcp list

# Fix 'env' server configuration
# (Check Gemini CLI documentation for MCP server setup)
```

### Option C: Use Gemini API Directly (Recommended)
The codebase already has Gemini API integration:
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Load image
img = Image.open(image_path)

# Analyze
response = model.generate_content([prompt, img])
```

**Complexity**: Low (already implemented)
**Reliability**: High

---

## 🎯 Recommended Approach

### Best Solution: Use APIs Directly

Instead of fighting with CLI limitations, use the APIs directly:

1. **Gemini API**: ✅ Already in codebase (`google-generativeai`)
2. **Claude API**: Install `anthropic` package
3. **OpenAI API**: Install `openai` package (for GPT-4 Vision)

### Why APIs Are Better:
- ✅ No TTY issues
- ✅ No authentication complexity
- ✅ More reliable for automation
- ✅ Better error handling
- ✅ Already partially implemented

### Implementation:
```python
# In ux_image_analyzer.py, add API methods:

def _semantic_analysis_gemini_api(self, img: Image.Image, prompt: str) -> Dict:
    """Use Gemini API directly"""
    if not GEMINI_AVAILABLE:
        return {}
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, img])
        return self._parse_semantic_response(response.text)
    except Exception as e:
        print(f"⚠️  Gemini API error: {e}")
        return {}
```

---

## 📋 Action Items

### Immediate (5 minutes)
- [ ] Run `claude auth` to authenticate Claude CLI
- [ ] Test: `claude "test" --print`
- [ ] If successful, test with image path

### Short-term (30 minutes)
- [ ] Implement Gemini API fallback (already available)
- [ ] Test Gemini API with image analysis
- [ ] Update analyzer to prefer API over CLI

### Long-term (Optional)
- [ ] Add Claude API support (`anthropic` package)
- [ ] Add OpenAI GPT-4 Vision support
- [ ] Keep CLI as fallback for manual use

---

## 🔍 Testing Commands

After applying fixes, test each CLI:

```bash
# Test Claude (after auth)
claude "Analyze this UI" --print

# Test Codex (in actual terminal, not script)
codex "Analyze this UI" --image image.png

# Test Gemini (after quota reset)
gemini "Analyze this UI screenshot at image.png"
```

---

**Status**: 
- Claude: Needs `claude auth` ✅ Easy fix
- Codex: Use API instead ✅ Better approach  
- Gemini: Use API (already available) ✅ Best solution

