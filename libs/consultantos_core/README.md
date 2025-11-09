# consultantos-core

Shared Python package that exposes the canonical ConsultantOS data models,
configuration, storage helpers, and authentication utilities to the new
multi-service architecture. Initially this package re-exports the existing
`consultantos.*` modules so we can migrate services incrementally without a
risky big-bang refactor. As we carve out dedicated services we can move the
source files into this package proper while keeping a stable import surface
(`import consultantos_core as core`).

## Usage (local editable install)

```bash
pip install -e libs/consultantos_core
```

Then inside any Cloud Run service:

```python
from consultantos_core import models, config

def handler(request: models.AnalysisRequest) -> None:
    settings = config.get_settings()
    ...
```

See `consultantos_core/__init__.py` for the shim implementation that wires the
new package to the legacy modules until they are relocated.
