"""
Pydantic models for MVP features
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request for conversational agent"""
    query: str = Field(..., description="User question or message")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier for maintaining context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the key competitive advantages of Tesla?",
                "conversation_id": "conv_123"
            }
        }


class ChatResponse(BaseModel):
    """Chat response from conversational agent"""
    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Based on market analysis, Tesla's key competitive advantages include...",
                "conversation_id": "conv_123",
                "timestamp": "2025-11-09T12:00:00"
            }
        }


class ForecastPrediction(BaseModel):
    """Single forecast data point"""
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    value: float = Field(..., description="Predicted value")
    lower_bound: float = Field(..., description="Lower confidence interval")
    upper_bound: float = Field(..., description="Upper confidence interval")


class ForecastResult(BaseModel):
    """Forecasting result with predictions"""
    metric_name: str = Field(default="Revenue", description="Forecasted metric name")
    predictions: List[ForecastPrediction] = Field(..., description="Forecast predictions")
    confidence_level: float = Field(default=0.95, description="Confidence interval level")
    generated_at: datetime = Field(default_factory=datetime.now, description="Forecast generation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "Revenue",
                "predictions": [
                    {
                        "date": "2025-12-01",
                        "value": 100000.0,
                        "lower_bound": 95000.0,
                        "upper_bound": 105000.0
                    }
                ],
                "confidence_level": 0.95,
                "generated_at": "2025-11-09T12:00:00"
            }
        }
