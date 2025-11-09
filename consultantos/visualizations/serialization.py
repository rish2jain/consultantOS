"""Utilities for serializing Plotly figures."""

from __future__ import annotations

import json
from typing import Any, Dict

import plotly.graph_objects as go
import plotly.io as pio


def figure_to_json(figure: go.Figure) -> Dict[str, Any]:
    """Return a JSON-serializable dict representation of a Plotly figure."""

    json_str = pio.to_json(figure, validate=False)
    return json.loads(json_str)
