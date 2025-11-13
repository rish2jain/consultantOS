# Mutex Deadlock Fix - ChromaDB Initialization

## Problem

The backend was getting stuck at mutex lock during startup. Investigation revealed that ChromaDB initialization was blocking inside a `threading.Lock()`, causing deadlocks when:

1. ChromaDB/DuckDB tried to acquire file locks during initialization
2. Multiple threads attempted to initialize ChromaDB simultaneously
3. The initialization took too long, blocking other operations

## Root Cause

In `consultantos/cache.py`, the `get_chroma_collection()` function used a blocking lock acquisition:

```python
with _chroma_lock:  # This blocks if lock is held
    if _chroma_client is None:
        _chroma_client = chromadb.Client(...)  # This can block/hang
```

If ChromaDB initialization hung (due to DuckDB file locks or network issues), the lock would never be released, causing all subsequent calls to block indefinitely.

## Solution

Changed to **non-blocking lock acquisition** with graceful degradation:

1. **Non-blocking lock**: Use `acquire(blocking=False)` to avoid deadlocks
2. **Graceful degradation**: If lock is held or initialization fails, return `None` (semantic cache is optional)
3. **Better error handling**: Mark failed initialization to avoid repeated attempts
4. **Disable telemetry**: Prevent network calls during initialization that might block

## Changes Made

### File: `consultantos/cache.py`

**Before:**
```python
def get_chroma_collection():
    if _chroma_client is None:
        with _chroma_lock:  # Blocking - can cause deadlock
            if _chroma_client is None:
                _chroma_client = chromadb.Client(...)  # Can hang
```

**After:**
```python
def get_chroma_collection():
    # Fast path check
    if _chroma_client is not None:
        return _chroma_collection
    
    # Non-blocking lock acquisition
    lock_acquired = _chroma_lock.acquire(blocking=False)
    if not lock_acquired:
        # Another thread is initializing - return None gracefully
        return None
    
    try:
        if _chroma_client is None:
            try:
                _chroma_client = chromadb.Client(Settings(
                    anonymized_telemetry=False  # Avoid blocking network calls
                ))
                # ... initialization ...
            except Exception as e:
                _chroma_client = False  # Mark as failed
                logger.warning(f"ChromaDB init failed: {e}")
    finally:
        _chroma_lock.release()
```

## Benefits

1. ✅ **No deadlocks**: Non-blocking lock prevents indefinite blocking
2. ✅ **Graceful degradation**: Application continues even if ChromaDB fails
3. ✅ **Better performance**: Fast path for already-initialized case
4. ✅ **Resilient**: Handles concurrent initialization attempts gracefully

## Testing

To verify the fix:

1. **Start backend**: Should start without hanging
   ```bash
   python main.py
   ```

2. **Check logs**: Should see either:
   - `"Initialized ChromaDB semantic cache"` (success)
   - `"Failed to initialize ChromaDB"` (graceful failure)
   - No hanging/deadlock

3. **Verify functionality**: Application should work even if ChromaDB is unavailable (semantic cache is optional)

## Related Issues

- ChromaDB initialization can be slow if DuckDB file locks are held
- Network calls during telemetry can block startup
- Multiple threads trying to initialize simultaneously can cause race conditions

## Future Improvements

1. Consider lazy initialization: Only initialize ChromaDB when actually needed
2. Add timeout mechanism for ChromaDB initialization
3. Consider using asyncio.to_thread for truly async initialization
4. Add health check endpoint to verify ChromaDB status

