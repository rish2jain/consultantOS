"""
Models package for ConsultantOS
"""
# Import from models.py (the file, not this package)
import sys
import os
# Get the parent directory to import models.py
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_models_file = os.path.join(_parent_dir, 'models.py')
if os.path.exists(_models_file):
    import importlib.util
    spec = importlib.util.spec_from_file_location("consultantos.models_file", _models_file)
    models_file = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_file)
    
    # Re-export all models from models.py
    AnalysisRequest = models_file.AnalysisRequest
    CompanyResearch = models_file.CompanyResearch
    MarketTrends = models_file.MarketTrends
    FinancialSnapshot = models_file.FinancialSnapshot
    PortersFiveForces = models_file.PortersFiveForces
    SWOTAnalysis = models_file.SWOTAnalysis
    PESTELAnalysis = models_file.PESTELAnalysis
    BlueOceanStrategy = models_file.BlueOceanStrategy
    FrameworkAnalysis = models_file.FrameworkAnalysis
    ExecutiveSummary = models_file.ExecutiveSummary
    StrategicReport = models_file.StrategicReport

from consultantos.models.templates import (
    FrameworkTemplate,
    TemplateLibrary,
    CreateTemplateRequest,
    UpdateTemplateRequest,
    TemplateCategory,
    TemplateVisibility
)
from consultantos.models.versioning import (
    ReportVersion,
    VersionHistory,
    CreateVersionRequest,
    VersionDiff,
    VersionStatus
)
from consultantos.models.sharing import (
    ShareAccess,
    CreateShareRequest,
    ShareListResponse,
    SharePermission
)

__all__ = [
    # Core models from models.py
    "AnalysisRequest",
    "CompanyResearch",
    "MarketTrends",
    "FinancialSnapshot",
    "PortersFiveForces",
    "SWOTAnalysis",
    "PESTELAnalysis",
    "BlueOceanStrategy",
    "FrameworkAnalysis",
    "ExecutiveSummary",
    "StrategicReport",
    # Templates
    "FrameworkTemplate",
    "TemplateLibrary",
    "CreateTemplateRequest",
    "UpdateTemplateRequest",
    "TemplateCategory",
    "TemplateVisibility",
    # Versioning
    "ReportVersion",
    "VersionHistory",
    "CreateVersionRequest",
    "VersionDiff",
    "VersionStatus",
    # Sharing
    "ShareAccess",
    "CreateShareRequest",
    "ShareListResponse",
    "SharePermission",
]

