# Available Grok Models via laozhang.ai

## ✅ All Models Now Available!

After updating your laozhang.ai account, you now have access to **9 different Grok models** with varying speed and capability trade-offs.

## Performance Comparison

| Model | Response Time | Tokens | Best For |
|-------|--------------|--------|----------|
| **grok-4-fast-non-reasoning-latest** | **1.80s** ⚡ | 362 | Real-time, simple queries |
| **grok-4-fast-reasoning-latest** | **1.94s** ⚡ | 511 | **Recommended: Fast + Reasoning** |
| grok-4-fast-non-reasoning | 2.26s | 362 | Fast responses |
| grok-4-fast | 4.18s | 642 | Balanced speed/quality |
| grok-4-fast-reasoning | 4.81s | 909 | Fast with reasoning |
| grok-4-latest | 18.32s | 1266 | Comprehensive analysis |
| grok-4 | 19.25s | 1378 | Full Grok 4 capabilities |
| grok-4-all | 112.69s | 688 | Most comprehensive (slow) |
| grok-4-0709 | 134.44s | 1476 | Legacy version |

## Recommendations

### 🏆 **Default: `grok-4-fast-reasoning-latest`** (1.94s)
- **Why**: Best balance of speed and reasoning capability
- **Use for**: Most sentiment analysis tasks
- **Speed**: ~2 seconds (60x faster than grok-4-all!)
- **Capability**: Has reasoning + real-time X data access

### ⚡ **Fastest: `grok-4-fast-non-reasoning-latest`** (1.80s)
- **Why**: Fastest response time
- **Use for**: Simple sentiment queries, high-volume processing
- **Speed**: ~1.8 seconds
- **Note**: May have limited reasoning capabilities

### 🚀 **Balanced: `grok-4-fast`** (4.18s)
- **Why**: Good balance without "latest" suffix
- **Use for**: Stable, predictable performance
- **Speed**: ~4 seconds

### 🧠 **Comprehensive: `grok-4-all`** (112.69s)
- **Why**: Most thorough analysis
- **Use for**: Deep analysis, batch processing
- **Speed**: ~113 seconds (use async/background jobs)
- **Note**: Only use when you need maximum depth

## Configuration

### Option 1: Environment Variable (Recommended)
```bash
# In your .env file
LAOZHANG_MODEL=grok-4-fast-reasoning-latest
```

### Option 2: Config File
```python
# In consultantos/config.py
laozhang_model: str = "grok-4-fast-reasoning-latest"
```

## Model Selection Guide

### Choose `grok-4-fast-reasoning-latest` if:
- ✅ You want the best speed/quality balance
- ✅ You need real-time sentiment analysis
- ✅ You're doing interactive queries
- ✅ **Default choice for most use cases**

### Choose `grok-4-fast-non-reasoning-latest` if:
- ⚡ You need absolute fastest response
- ⚡ You're processing high volumes
- ⚡ Simple sentiment classification is enough

### Choose `grok-4-fast` if:
- 🎯 You want stable, predictable performance
- 🎯 You prefer non-"latest" versions

### Choose `grok-4-all` if:
- 🧠 You need maximum depth/accuracy
- 🧠 You're doing batch processing
- 🧠 Response time is not critical

## Performance Impact

**Before (grok-4-all)**: ~113 seconds per query
**After (grok-4-fast-reasoning-latest)**: ~2 seconds per query

**Speed improvement: ~57x faster!** 🚀

## Testing

To test all available models:
```bash
python test_grok4_fast_models.py
```

To check available models:
```bash
python test_list_models.py
```

## Current Default

The system is now configured to use **`grok-4-fast-reasoning-latest`** by default, which provides:
- ⚡ Fast response times (~2 seconds)
- 🧠 Reasoning capabilities
- 📊 Real-time X data access
- 💰 Efficient token usage (511 tokens)

This is the recommended model for most sentiment analysis use cases!

