# CLI Tool Issues - Detailed Analysis

This document details the specific issues encountered when trying to use Codex, Claude, and Gemini CLIs for image analysis in automated scripts.

## 🔍 Testing Environment

- **Codex CLI**: v0.57.0
- **Claude CLI**: v2.0.37 (Claude Code)
- **Gemini CLI**: v0.14.0
- **OS**: macOS (darwin 25.0.0)
- **Shell**: zsh

---

## 1. Codex CLI Issues

### Problem

```
Error: stdout is not a terminal
```

### Root Cause

Codex CLI requires an interactive terminal (TTY) to function properly. When called from Python's `subprocess.run()` with `capture_output=True`, it detects that stdout is not a terminal and fails.

### Attempted Solutions

#### Solution 1: Direct Command

```bash
codex "prompt" --image image.png
```

**Result**: ❌ Fails with "stdout is not a terminal"

#### Solution 2: Environment Variables

```python
env={**os.environ, "FORCE_COLOR": "0"}
```

**Result**: ❌ Still fails - Codex checks `isatty()` on stdout

#### Solution 3: Pseudo-TTY (pty)

Would require using `pty` module, but this is complex and may not work reliably.

### Codex CLI Help Output

```bash
$ codex --help
# Shows: -i, --image <FILE>...  Optional image(s) to attach to the initial prompt
```

### Current Implementation

```python
result = subprocess.run(
    ["codex", prompt, "--image", image_path],
    capture_output=True,
    timeout=20,
    text=True,
    env={**os.environ, "FORCE_COLOR": "0"}
)
```

### Error Details

- **Exit Code**: Non-zero
- **Error Message**: "Error: stdout is not a terminal"
- **Stderr**: Contains the error message
- **Stdout**: Empty

### Possible Fixes

1. **Use `pty` module** to create pseudo-terminal (complex)
2. **Use `script` command** to create TTY (platform-specific)
3. **Use Codex API directly** instead of CLI
4. **Run in interactive mode** (not suitable for automation)

---

## 2. Claude CLI Issues

### Problem

```
Invalid API key · Fix external API key
```

### Root Cause

Claude CLI requires authentication before use. The CLI needs to be authenticated with an API key or OAuth flow.

### Attempted Solutions

#### Solution 1: Direct Command

```bash
claude "prompt" --print
```

**Result**: ❌ Fails with "Invalid API key"

#### Solution 2: Image Path in Prompt

```bash
claude "Analyze image at path/to/image.png: prompt" --print
```

**Result**: ❌ Still requires authentication

#### Solution 3: Check for Image Flag

```bash
$ claude --help | grep -i image
# Result: No image flag found
```

Claude CLI doesn't appear to have a direct `--image` flag in the help output.

### Claude CLI Help Output

```bash
$ claude --help
Usage: claude [options] [command] [prompt]

Options:
  -p, --print  Print response and exit (useful for pipes)
  --output-format <format>  Output format: "text", "json", "stream-json"
  # ... no --image flag visible
```

### Current Implementation

```python
result = subprocess.run(
    ["claude", f"Analyze this image: {image_path}. {prompt}", "--print"],
    capture_output=True,
    timeout=15,
    text=True
)
```

### Error Details

- **Exit Code**: Non-zero
- **Error Message**: "Invalid API key · Fix external API key"
- **Stderr**: Contains authentication error
- **Stdout**: May contain error message

### Required Setup

```bash
# Need to authenticate first:
claude auth
# or set API key in environment/config
```

### Possible Fixes

1. **Run `claude auth` first** to authenticate
2. **Set API key in environment** (if supported)
3. **Check Claude CLI documentation** for image support
4. **Use Claude API directly** instead of CLI

---

## 3. Gemini CLI Issues

### Problem

Multiple issues discovered:

1. **API Quota Exhausted**: "You have exhausted your capacity on this model. Your quota will reset after 23h10m50s."
2. **MCP Server Configuration Error**: "Error during discovery for server 'env': Invalid configuration"
3. **No Direct Image Support**: May not support direct image file input

### Actual Error Output

```bash
$ gemini "Analyze UI screenshot at image.png"
Loaded cached credentials.
[ERROR] Error during discovery for server 'env': Connection failed for 'env': Invalid configuration: missing httpUrl (for Streamable HTTP), url (for SSE), and command (for stdio).
Error when talking to Gemini API Full report available at: /var/folders/.../gemini-client-error-...json
[API Error: You have exhausted your capacity on this model. Your quota will reset after 23h10m50s.]
An unexpected critical error occurred: [object Object]
```

### Root Cause

1. **Quota Exhausted**: Gemini API has hit rate limit/quota (resets in ~23 hours)
2. **MCP Configuration**: Gemini CLI has MCP (Model Context Protocol) server configuration issues with 'env' server
3. **Image Support**: Gemini CLI may not support direct image file input - it might need the image to be passed differently or may not support vision models via CLI

### Attempted Solutions

#### Solution 1: Positional Prompt with Image Path

```bash
gemini "Analyze this UI screenshot at path/to/image.png: prompt"
```

**Result**: ⚠️ May work but image path is just text, not actual image data

#### Solution 2: Check for Image Flag

```bash
$ gemini --help | grep -i image
# Result: No image flag found
```

#### Solution 3: Try `--image` Flag Anyway

```bash
gemini --image image.png "prompt"
```

**Result**: ❌ Unknown argument (if flag doesn't exist)

### Gemini CLI Help Output

```bash
$ gemini --help
Usage: gemini [options] [command] [query]

Options:
  -p, --prompt  Prompt (deprecated: Use positional prompt)
  -i, --prompt-interactive  Execute prompt and continue in interactive mode
  # ... no --image flag visible
```

### Current Implementation

```python
full_prompt = f"{prompt}\n\nImage file path: {image_path}"
result = subprocess.run(
    ["gemini", full_prompt],
    capture_output=True,
    timeout=30,
    text=True
)
```

### Error Details

- **Status**: May execute but image is referenced as text path, not actual image
- **Issue**: Gemini CLI might not load/process the image file automatically
- **Result**: Analysis would be based on text description, not visual content

### Possible Fixes

1. **Check Gemini CLI documentation** for image support syntax
2. **Use base64 encoding** and include in prompt
3. **Use Gemini API directly** with vision model
4. **Check for extensions** that support images

---

## 📋 Summary of Issues

| CLI Tool   | Issue                        | Root Cause                      | Fix Complexity              |
| ---------- | ---------------------------- | ------------------------------- | --------------------------- |
| **Codex**  | "stdout is not a terminal"   | Requires interactive TTY        | High - needs pty/script     |
| **Claude** | "Invalid API key"            | Requires CLI authentication     | Medium - run `claude auth`  |
| **Gemini** | Quota exhausted + MCP errors | API quota limit + config issues | Medium - wait or fix config |

---

## 🔧 Recommended Solutions

### Option 1: Fix Authentication (Claude)

```bash
# Run once to authenticate
claude auth

# Then CLI should work
claude "prompt" --print
```

### Option 2: Use Pseudo-TTY (Codex)

```python
import pty
import os

# Create pseudo-terminal for Codex
master, slave = pty.openpty()
# ... complex implementation
```

### Option 3: Use APIs Directly

Instead of CLI tools, use the APIs directly:

- **Gemini API**: `google-generativeai` (already in requirements)
- **Claude API**: `anthropic` package
- **OpenAI API**: `openai` package (for Codex/GPT-4 Vision)

### Option 4: Manual CLI Testing

Test each CLI manually to find correct syntax:

```bash
# Test Codex
codex "test" --image test.png

# Test Claude (after auth)
claude "test" --print

# Test Gemini
gemini "test with image path"
```

---

## 🧪 Actual Test Results

### Codex CLI Test

```bash
$ codex "Analyze this UI" --image image.png
Error: stdout is not a terminal
```

**Status**: ❌ Fails in non-interactive mode

### Claude CLI Test

```bash
$ claude "Analyze this UI screenshot" --print
Invalid API key · Fix external API key
```

**Status**: ❌ Needs authentication (`claude auth`)

### Gemini CLI Test

```bash
$ gemini "Analyze UI screenshot at image.png"
[API Error: You have exhausted your capacity on this model. Your quota will reset after 23h10m50s.]
```

**Status**: ❌ Quota exhausted + MCP config issues

## 🔧 Recommended Fixes

### For Claude (Easiest)

```bash
# 1. Authenticate
claude auth

# 2. Test
claude "test" --print

# 3. If that works, test with image path in prompt
claude "Analyze this UI screenshot at path/to/image.png" --print
```

### For Codex (Complex)

Would need to use `pty` module or run in actual terminal. Not recommended for automation.

### For Gemini (Wait or Fix Config)

1. Wait for quota reset (~23 hours)
2. Fix MCP server configuration
3. Or use Gemini API directly (already available)

---

## 💡 Current Workaround

**Technical metrics analysis is working perfectly** and provides:

- ✅ Visual hierarchy scoring
- ✅ Color contrast analysis
- ✅ Text readability metrics
- ✅ Whitespace analysis
- ✅ Overall UX scoring

**Semantic analysis** (component detection, accessibility issues) would be nice-to-have but is **optional**. The technical metrics alone provide actionable insights.

---

## 📝 Next Steps

1. **For Codex**: Research if there's a `--no-tty` or `--batch` flag
2. **For Claude**: Run `claude auth` and test if it works after authentication
3. **For Gemini**: Check documentation for image input syntax
4. **Alternative**: Use APIs directly instead of CLIs for more reliable automation

---

**Last Updated**: 2025-11-12
**Status**: Technical metrics working, CLI semantic analysis blocked by tool limitations
