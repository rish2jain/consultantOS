# Backend Import Test

**Issue**: Backend hangs during import phase (after mutex warning)

## Test Import

Run this to see where import hangs:

```bash
python -c "from consultantos.api.main import app; print('Import successful')"
```

If this hangs, the issue is in the import chain, not startup.

## Likely Culprits

1. **Firestore connection** - `consultantos.database` trying to connect during import
2. **ChromaDB initialization** - Vector store initializing during import  
3. **Orchestrator creation** - `AnalysisOrchestrator()` doing something blocking
4. **Worker initialization** - `get_worker()` creating orchestrator

## Quick Workaround

If import hangs, temporarily comment out problematic imports in `consultantos/api/main.py`:

1. Comment out worker-related imports
2. Comment out database initialization
3. Test if server starts

Then gradually uncomment to find the culprit.

---

**Next**: Test the import command above to identify where it hangs.

