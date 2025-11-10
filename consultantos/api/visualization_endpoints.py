"""Visualization endpoints serving Plotly JSON."""

from fastapi import APIRouter, HTTPException

from consultantos import models
from consultantos.visualizations import (
    create_porter_radar_figure,
    create_swot_matrix_figure,
    figure_to_json,
    get_cached_figure,
    set_cached_figure,
)

router = APIRouter(prefix="/visualizations", tags=["visualizations"])


@router.post("/porter")
async def porter_figure(data: models.PortersFiveForces, report_id: str | None = None):
    """Return Plotly JSON for a Porter's Five Forces radar chart."""

    cache_key = f"porter:{report_id}" if report_id else None
    if cache_key:
        cached = get_cached_figure(cache_key)
        if cached:
            return {"figure": cached, "cached": True}

    figure = create_porter_radar_figure(data)
    figure_json = figure_to_json(figure)
    if cache_key:
        set_cached_figure(cache_key, figure_json)
    return {"figure": figure_json, "cached": False}


@router.post("/swot")
async def swot_matrix(data: models.SWOTAnalysis, report_id: str | None = None):
    """Return Plotly JSON for a SWOT matrix."""

    cache_key = f"swot:{report_id}" if report_id else None
    if cache_key:
        cached = get_cached_figure(cache_key)
        if cached:
            return {"figure": cached, "cached": True}

    figure = create_swot_matrix_figure(data)
    figure_json = figure_to_json(figure)
    if cache_key:
        set_cached_figure(cache_key, figure_json)
    return {"figure": figure_json, "cached": False}
@router.post("/porter/from-report")
async def porter_from_report(report: models.StrategicReport, report_id: str | None = None):
    if not report.framework_analysis or not report.framework_analysis.porter_five_forces:
        raise HTTPException(status_code=400, detail="Report missing Porter's data")
    return await porter_figure(report.framework_analysis.porter_five_forces, report_id=report_id)


@router.post("/swot/from-report")
async def swot_from_report(report: models.StrategicReport, report_id: str | None = None):
    if not report.framework_analysis or not report.framework_analysis.swot_analysis:
        raise HTTPException(status_code=400, detail="Report missing SWOT data")
    return await swot_matrix(report.framework_analysis.swot_analysis, report_id=report_id)
