"""
Report Comparison Endpoints

Provides endpoints for comparing multiple reports side-by-side and
tracking changes over time.
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from consultantos.auth import get_current_user
from consultantos.database import get_db_service
from consultantos.models import StrategicReport

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reports", tags=["comparisons"])


# Request/Response Models
class ComparisonRequest(BaseModel):
    """Request to compare multiple reports"""
    report_ids: List[str] = Field(..., min_items=2, max_items=5, description="2-5 report IDs to compare")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to compare (default: all)")


class MetricChange(BaseModel):
    """Change in a specific metric"""
    metric_name: str
    report_id: str
    report_date: str
    value: Any
    delta: Optional[float] = None  # Change from previous
    delta_percent: Optional[float] = None


class FrameworkComparison(BaseModel):
    """Comparison of a framework across reports"""
    framework_name: str
    changes_detected: List[str]
    metrics: List[MetricChange]
    significance: str  # "major", "moderate", "minor"


class ComparisonResult(BaseModel):
    """Result of comparing multiple reports"""
    report_ids: List[str]
    companies: List[str]  # May be same company or different
    date_range: str

    # Summary
    overall_trend: str  # "improving", "stable", "declining"
    major_changes: List[str]

    # Framework comparisons
    framework_comparisons: List[FrameworkComparison]

    # Metric trends
    confidence_scores: List[MetricChange]
    key_metrics: Dict[str, List[MetricChange]]

    # Recommendations
    insights: List[str]


@router.post("/compare", response_model=ComparisonResult)
async def compare_reports(
    request: ComparisonRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Compare 2-5 reports side-by-side.

    Analyzes changes in:
    - Framework analyses (Porter, SWOT, PESTEL, Blue Ocean)
    - Confidence scores
    - Key findings
    - Strategic recommendations

    Returns trend analysis and change highlights.
    """
    try:
        logger.info(f"Comparing reports: {request.report_ids} for user {user_id}")

        # Get all reports
        db_service = get_db_service()
        reports = []
        for report_id in request.report_ids:
            report_doc = await db_service.get_document("reports", report_id)
            if not report_doc:
                raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
            reports.append(report_doc)

        # Sort by date
        reports.sort(key=lambda r: r.get('created_at', ''))

        # Extract comparison data
        companies = [r.get('company', 'Unknown') for r in reports]
        dates = [r.get('created_at', '') for r in reports]
        date_range = f"{dates[0][:10]} to {dates[-1][:10]}" if dates else "Unknown"

        # Compare confidence scores
        confidence_changes = []
        for i, report in enumerate(reports):
            confidence = report.get('confidence_score', 0)
            delta = None
            delta_percent = None
            if i > 0:
                prev_confidence = reports[i-1].get('confidence_score', 0)
                delta = confidence - prev_confidence
                delta_percent = (delta / prev_confidence * 100) if prev_confidence else 0

            confidence_changes.append(MetricChange(
                metric_name="Confidence Score",
                report_id=report.get('report_id', request.report_ids[i]),
                report_date=report.get('created_at', '')[:10],
                value=round(confidence * 100, 1),
                delta=round(delta, 3) if delta is not None else None,
                delta_percent=round(delta_percent, 1) if delta_percent is not None else None
            ))

        # Compare frameworks
        framework_comparisons = _compare_frameworks(reports, request.report_ids)

        # Determine overall trend
        overall_trend = _determine_overall_trend(confidence_changes)

        # Extract major changes
        major_changes = _extract_major_changes(framework_comparisons, confidence_changes)

        # Generate insights
        insights = _generate_comparison_insights(
            reports=reports,
            framework_comparisons=framework_comparisons,
            confidence_changes=confidence_changes,
            overall_trend=overall_trend
        )

        return ComparisonResult(
            report_ids=request.report_ids,
            companies=companies,
            date_range=date_range,
            overall_trend=overall_trend,
            major_changes=major_changes,
            framework_comparisons=framework_comparisons,
            confidence_scores=confidence_changes,
            key_metrics={},  # TODO: Add more metrics
            insights=insights
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing reports: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to compare reports: {str(e)}")


def _compare_frameworks(reports: List[Dict], report_ids: List[str]) -> List[FrameworkComparison]:
    """Compare framework analyses across reports"""
    comparisons = []

    # Porter's Five Forces
    porter_changes = []
    porter_metrics = []
    for i, report in enumerate(reports):
        porter = report.get('framework_analysis', {}).get('porters_five_forces', {})
        if porter:
            # Track each force
            for force in ['supplier_power', 'buyer_power', 'competitive_rivalry',
                         'threat_of_substitutes', 'threat_of_new_entry']:
                current_val = porter.get(force, 0)
                if i > 0:
                    prev_porter = reports[i-1].get('framework_analysis', {}).get('porters_five_forces', {})
                    prev_val = prev_porter.get(force, 0)
                    delta = current_val - prev_val
                    if abs(delta) >= 0.5:  # Significant change
                        porter_changes.append(
                            f"{force.replace('_', ' ').title()}: {prev_val}→{current_val} ({delta:+.1f})"
                        )

    if porter_changes:
        significance = "major" if len(porter_changes) >= 3 else "moderate" if len(porter_changes) >= 2 else "minor"
        comparisons.append(FrameworkComparison(
            framework_name="Porter's Five Forces",
            changes_detected=porter_changes,
            metrics=[],  # TODO: Add detailed metrics
            significance=significance
        ))

    # SWOT Analysis
    swot_changes = []
    for i in range(1, len(reports)):
        curr_swot = reports[i].get('framework_analysis', {}).get('swot_analysis', {})
        prev_swot = reports[i-1].get('framework_analysis', {}).get('swot_analysis', {})

        # Compare counts
        for category in ['strengths', 'weaknesses', 'opportunities', 'threats']:
            curr_count = len(curr_swot.get(category, []))
            prev_count = len(prev_swot.get(category, []))
            delta = curr_count - prev_count
            if delta != 0:
                swot_changes.append(
                    f"{category.title()}: {prev_count}→{curr_count} ({delta:+d})"
                )

    if swot_changes:
        comparisons.append(FrameworkComparison(
            framework_name="SWOT Analysis",
            changes_detected=swot_changes,
            metrics=[],
            significance="moderate"
        ))

    return comparisons


def _determine_overall_trend(confidence_changes: List[MetricChange]) -> str:
    """Determine overall trend from confidence changes"""
    if len(confidence_changes) < 2:
        return "stable"

    # Look at trend in last comparison
    last_change = confidence_changes[-1]
    if last_change.delta is None:
        return "stable"

    if last_change.delta > 0.05:
        return "improving"
    elif last_change.delta < -0.05:
        return "declining"
    else:
        return "stable"


def _extract_major_changes(
    framework_comparisons: List[FrameworkComparison],
    confidence_changes: List[MetricChange]
) -> List[str]:
    """Extract major changes for executive summary"""
    major_changes = []

    # Confidence changes
    if len(confidence_changes) >= 2:
        last_change = confidence_changes[-1]
        if last_change.delta_percent and abs(last_change.delta_percent) >= 10:
            direction = "increased" if last_change.delta_percent > 0 else "decreased"
            major_changes.append(
                f"Confidence score {direction} by {abs(last_change.delta_percent):.1f}%"
            )

    # Framework changes
    for comparison in framework_comparisons:
        if comparison.significance == "major":
            major_changes.append(
                f"{comparison.framework_name}: {len(comparison.changes_detected)} significant changes"
            )

    return major_changes if major_changes else ["No major changes detected"]


def _generate_comparison_insights(
    reports: List[Dict],
    framework_comparisons: List[FrameworkComparison],
    confidence_changes: List[MetricChange],
    overall_trend: str
) -> List[str]:
    """Generate insights from comparison"""
    insights = []

    # Trend insight
    if overall_trend == "improving":
        insights.append(
            f"✓ Strategic position is improving across {len(reports)} analyses. "
            f"Confidence increased from {confidence_changes[0].value}% to {confidence_changes[-1].value}%."
        )
    elif overall_trend == "declining":
        insights.append(
            f"⚠ Strategic position shows concerning decline. "
            f"Confidence dropped from {confidence_changes[0].value}% to {confidence_changes[-1].value}%. "
            f"Recommend immediate strategic review."
        )
    else:
        insights.append(
            f"Strategic position remains stable with confidence at {confidence_changes[-1].value}%."
        )

    # Framework insights
    for comparison in framework_comparisons:
        if comparison.significance == "major":
            insights.append(
                f"⚡ Major shifts detected in {comparison.framework_name}. "
                f"Review these {len(comparison.changes_detected)} changes carefully."
            )

    # Time-based insight
    if len(reports) >= 3:
        days_span = len(reports) * 30  # Rough estimate
        insights.append(
            f"Analysis covers {days_span} days with {len(reports)} snapshots. "
            f"Consider increasing monitoring frequency for faster trend detection."
        )

    return insights


@router.get("/{report_id}/evolution", tags=["comparisons"])
async def get_report_evolution(
    report_id: str,
    lookback_days: int = Query(90, ge=7, le=365, description="Days to look back"),
    user_id: str = Depends(get_current_user)
):
    """
    Get evolution of strategic position for a company.

    Finds all reports for the same company and shows how
    metrics evolved over time.
    """
    try:
        logger.info(f"Fetching evolution for report {report_id}, lookback {lookback_days} days")

        # Get base report
        db_service = get_db_service()
        base_report = await db_service.get_document("reports", report_id)
        if not base_report:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

        company = base_report.get('company', '')
        if not company:
            raise HTTPException(status_code=400, detail="Base report missing company field")

        # Extract base report date
        base_report_date_str = base_report.get('created_at') or base_report.get('date')
        if not base_report_date_str:
            raise HTTPException(status_code=400, detail="Base report missing date field (created_at or date)")

        # Parse base report date
        try:
            if isinstance(base_report_date_str, str):
                # Try ISO format first
                try:
                    base_report_date = datetime.fromisoformat(base_report_date_str.replace('Z', '+00:00'))
                except ValueError:
                    # Try other common formats
                    try:
                        base_report_date = datetime.strptime(base_report_date_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        base_report_date = datetime.strptime(base_report_date_str, '%Y-%m-%d')
            else:
                # Assume it's already a datetime object
                base_report_date = base_report_date_str
        except (ValueError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format in base report: {str(e)}")

        # Calculate cutoff date
        cutoff_date = base_report_date - timedelta(days=lookback_days)

        # Query all reports for the same company
        # Note: list_reports is synchronous, returns List[ReportMetadata]
        all_reports = db_service.list_reports(company=company, limit=1000)
        
        # Filter reports within lookback period and before base report date
        evolution_reports = []
        for report in all_reports:
            # Skip the base report itself
            report_id_attr = report.report_id if hasattr(report, 'report_id') else (report.get('report_id') if isinstance(report, dict) else None)
            if report_id_attr == report_id:
                continue

            # Get report date
            # ReportMetadata has created_at as a string attribute
            if hasattr(report, 'created_at'):
                report_date_str = report.created_at
            elif isinstance(report, dict):
                report_date_str = report.get('created_at') or report.get('date')
            else:
                continue

            # Parse report date
            try:
                if isinstance(report_date_str, str):
                    try:
                        report_date = datetime.fromisoformat(report_date_str.replace('Z', '+00:00'))
                    except ValueError:
                        try:
                            report_date = datetime.strptime(report_date_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            report_date = datetime.strptime(report_date_str, '%Y-%m-%d')
                else:
                    report_date = report_date_str
            except (ValueError, AttributeError):
                # Skip reports with invalid dates
                report_id_for_log = report.report_id if hasattr(report, 'report_id') else (report.get('report_id', 'unknown') if isinstance(report, dict) else 'unknown')
                logger.warning(f"Skipping report {report_id_for_log} due to invalid date format")
                continue

            # Check if report is within lookback period and before base report
            if cutoff_date <= report_date <= base_report_date:
                evolution_reports.append({
                    'report': report,
                    'date': report_date
                })

        # Sort chronologically (oldest first)
        evolution_reports.sort(key=lambda x: x['date'])

        # Add base report at the end
        evolution_reports.append({
            'report': base_report,
            'date': base_report_date
        })

        # Extract metrics and strategic position from each report
        evolution_data = []
        for item in evolution_reports:
            report = item['report']
            report_date = item['date']

            # Convert report to dict if it's a ReportMetadata object
            if hasattr(report, 'to_dict'):
                report_dict = report.to_dict()
            elif hasattr(report, '__dict__'):
                report_dict = report.__dict__
            elif isinstance(report, dict):
                report_dict = report
            else:
                report_dict = {}

            # Extract relevant metrics
            metrics = {
                'confidence_score': report_dict.get('confidence_score', 0),
                'report_id': report_dict.get('report_id', ''),
            }

            # Extract strategic position from framework_analysis if available
            framework_analysis = report_dict.get('framework_analysis', {})
            strategic_position = {}

            # Porter's Five Forces
            if 'porters_five_forces' in framework_analysis:
                porter = framework_analysis['porters_five_forces']
                strategic_position['porter'] = {
                    'supplier_power': porter.get('supplier_power', 0),
                    'buyer_power': porter.get('buyer_power', 0),
                    'competitive_rivalry': porter.get('competitive_rivalry', 0),
                    'threat_of_substitutes': porter.get('threat_of_substitutes', 0),
                    'threat_of_new_entry': porter.get('threat_of_new_entry', 0),
                }

            # SWOT summary counts
            if 'swot_analysis' in framework_analysis:
                swot = framework_analysis['swot_analysis']
                strategic_position['swot'] = {
                    'strengths_count': len(swot.get('strengths', [])),
                    'weaknesses_count': len(swot.get('weaknesses', [])),
                    'opportunities_count': len(swot.get('opportunities', [])),
                    'threats_count': len(swot.get('threats', [])),
                }

            evolution_data.append({
                'date': report_date.isoformat(),
                'report_id': metrics['report_id'],
                'metrics': metrics,
                'strategic_position': strategic_position
            })

        return {
            "report_id": report_id,
            "company": company,
            "lookback_days": lookback_days,
            "base_report_date": base_report_date.isoformat(),
            "cutoff_date": cutoff_date.isoformat(),
            "evolution_data": evolution_data,
            "total_reports": len(evolution_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching evolution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch evolution: {str(e)}")
