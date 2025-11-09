"""
Tests for data models
"""
import pytest
from consultantos.models import (
    AnalysisRequest,
    PortersFiveForces,
    SWOTAnalysis,
    ExecutiveSummary
)


def test_analysis_request():
    """Test AnalysisRequest model"""
    request = AnalysisRequest(
        company="Tesla",
        industry="Electric Vehicles",
        frameworks=["porter", "swot"]
    )
    assert request.company == "Tesla"
    assert request.industry == "Electric Vehicles"
    assert "porter" in request.frameworks


def test_porters_five_forces():
    """Test PortersFiveForces model validation"""
    forces = PortersFiveForces(
        supplier_power=3.0,
        buyer_power=4.0,
        competitive_rivalry=3.5,
        threat_of_substitutes=2.5,
        threat_of_new_entrants=3.0,
        overall_intensity="Moderate",
        detailed_analysis={}
    )
    assert forces.supplier_power == 3.0
    assert forces.overall_intensity == "Moderate"


def test_porters_five_forces_validation():
    """Test PortersFiveForces validation"""
    import pydantic
    with pytest.raises(pydantic.ValidationError):  # Should fail validation
        PortersFiveForces(
            supplier_power=6.0,  # Invalid: > 5
            buyer_power=4.0,
            competitive_rivalry=3.5,
            threat_of_substitutes=2.5,
            threat_of_new_entrants=3.0,
            overall_intensity="Moderate",
            detailed_analysis={}
        )


def test_swot_analysis():
    """Test SWOTAnalysis model"""
    swot = SWOTAnalysis(
        strengths=["Strong brand", "Market leader", "Innovation"],
        weaknesses=["High debt", "Dependency on suppliers", "Limited diversification"],
        opportunities=["Growing market", "New products", "International expansion"],
        threats=["Competition", "Regulation", "Economic downturn"]
    )
    assert len(swot.strengths) >= 3
    assert len(swot.weaknesses) >= 3

