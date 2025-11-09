"""
Export formats for reports (JSON, Excel, Word)
"""
import json
import logging
from typing import Dict, Any, Optional
from io import BytesIO
from consultantos.models import StrategicReport

logger = logging.getLogger(__name__)


async def export_to_json(report: StrategicReport) -> Dict[str, Any]:
    """
    Export report as JSON
    
    Args:
        report: Strategic report to export
    
    Returns:
        Dictionary representation of the report
    """
    try:
        return report.model_dump()
    except Exception as e:
        logger.error(f"JSON export failed: {e}", exc_info=True)
        raise


async def export_to_excel(report: StrategicReport) -> bytes:
    """
    Export report as Excel workbook
    
    Args:
        report: Strategic report to export
    
    Returns:
        Excel file as bytes
    """
    try:
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Executive Summary"
        
        # Write executive summary
        ws.append(["Company", report.executive_summary.company_name])
        ws.append(["Industry", report.executive_summary.industry])
        ws.append(["Confidence Score", f"{report.executive_summary.confidence_score:.2%}"])
        ws.append([])
        ws.append(["Key Findings"])
        for finding in report.executive_summary.key_findings:
            ws.append([finding])
        
        ws.append([])
        ws.append(["Strategic Recommendation"])
        ws.append([report.executive_summary.strategic_recommendation])
        
        # Format headers
        for row in ws.iter_rows(min_row=1, max_row=10):
            for cell in row:
                if cell.value and isinstance(cell.value, str) and cell.value.isupper():
                    cell.font = Font(bold=True)
        
        # Save to bytes
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    except ImportError:
        logger.error("openpyxl not installed. Install with: pip install openpyxl")
        raise ImportError("Excel export requires openpyxl package")
    except Exception as e:
        logger.error(f"Excel export failed: {e}", exc_info=True)
        raise


async def export_to_word(report: StrategicReport) -> bytes:
    """
    Export report as Word document
    
    Args:
        report: Strategic report to export
    
    Returns:
        Word document as bytes
    """
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        # Title
        title = doc.add_heading('Strategic Analysis Report', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Company info
        doc.add_heading('Company Information', level=1)
        doc.add_paragraph(f"Company: {report.executive_summary.company_name}")
        doc.add_paragraph(f"Industry: {report.executive_summary.industry}")
        doc.add_paragraph(f"Confidence Score: {report.executive_summary.confidence_score:.2%}")
        
        # Executive Summary
        doc.add_heading('Executive Summary', level=1)
        doc.add_heading('Key Findings', level=2)
        for finding in report.executive_summary.key_findings:
            doc.add_paragraph(finding, style='List Bullet')
        
        doc.add_heading('Strategic Recommendation', level=2)
        doc.add_paragraph(report.executive_summary.strategic_recommendation)
        
        # Save to bytes
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        return output.getvalue()
    except ImportError:
        logger.error("python-docx not installed. Install with: pip install python-docx")
        raise ImportError("Word export requires python-docx package")
    except Exception as e:
        logger.error(f"Word export failed: {e}", exc_info=True)
        raise