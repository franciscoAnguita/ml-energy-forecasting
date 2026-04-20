"""
API Schemas Module
Pydantic models for request and response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class PredictionInput(BaseModel):
    """
    Input schema for energy consumption prediction
    
    All fields are required for making a prediction.
    Pydantic automatically validates types and ranges.
    """
    
    voltage: float = Field(
        ...,
        description="Voltage in volts (V)",
        ge=200.0,
        le=260.0,
        example=240.5
    )
    
    global_intensity: float = Field(
        ...,
        description="Global current intensity in amperes (A)",
        ge=0.0,
        le=50.0,
        example=4.6
    )
    
    sub_metering_1: float = Field(
        ...,
        description="Kitchen energy consumption in watt-hours",
        ge=0.0,
        example=1.2
    )
    
    sub_metering_2: float = Field(
        ...,
        description="Laundry energy consumption in watt-hours",
        ge=0.0,
        example=0.8
    )
    
    sub_metering_3: float = Field(
        ...,
        description="Climate control energy consumption in watt-hours",
        ge=0.0,
        example=17.0
    )
    
    hour: int = Field(
        ...,
        description="Hour of day (0-23)",
        ge=0,
        le=23,
        example=14
    )
    
    day_of_week: int = Field(
        ...,
        description="Day of week (0=Monday, 6=Sunday)",
        ge=0,
        le=6,
        example=2
    )
    
    month: int = Field(
        ...,
        description="Month (1-12)",
        ge=1,
        le=12,
        example=4
    )
    
    is_weekend: int = Field(
        ...,
        description="Weekend indicator (0=weekday, 1=weekend)",
        ge=0,
        le=1,
        example=0
    )

    # global_reactive_power: float = Field(
    #     ...,
    #     description="Reactive power in kW",
    #     ge=0.0,
    #     le=1.0,
    #     example=0.15
    # )
    
    @validator('is_weekend')
    def validate_weekend_consistency(cls, v, values):
        """
        Validate that is_weekend matches day_of_week        
        This catches user errors where they set is_weekend=1 but day_of_week=2 (Tuesday)
        """
       
        if 'day_of_week' in values:
            day = values['day_of_week']
            expected_weekend = 1 if day >= 5 else 0
            if v != expected_weekend:
                raise ValueError(
                    f"is_weekend={v} doesn't match day_of_week={day}. "
                    f"Expected is_weekend={expected_weekend}"
                )
        return v
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "voltage": 240.5,
                "global_intensity": 4.6,
                "sub_metering_1": 1.2,
                "sub_metering_2": 0.8,
                "sub_metering_3": 17.0,
                "hour": 14,
                "day_of_week": 2,
                "month": 4,
                "is_weekend": 0
            }
        }


class PredictionOutput(BaseModel):
    """
    Output schema for energy consumption prediction    
    Returns predicted consumption with classification and metadata
    """
    
    predicted_consumption_kw: float = Field(
        ...,
        description="Predicted energy consumption in kilowatts (kW)",
        example=2.34
    )
    
    consumption_level: str = Field(
        ...,
        description="Consumption classification (Low/Medium/High)",
        example="Medium"
    )
    
    confidence: float = Field(
        ...,
        description="Model confidence score (0-1)",
        ge=0.0,
        le=1.0,
        example=0.92
    )
    
    timestamp: str = Field(
        ...,
        description="Prediction timestamp (ISO format)",
        example="2024-04-16T14:30:00"
    )
    
    features_used: dict = Field(
        ...,
        description="Input features used for prediction",
        example={
            "voltage": 240.5,
            "hour": 14,
            "is_weekend": 0
        }
    )
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "predicted_consumption_kw": 2.34,
                "consumption_level": "Medium",
                "confidence": 0.92,
                "timestamp": "2024-04-16T14:30:00",
                "features_used": {
                    "voltage": 240.5,
                    "global_intensity": 4.6,
                    "hour": 14,
                    "is_weekend": 0
                }
            }
        }


class BatchPredictionInput(BaseModel):
    """
    Input schema for batch predictions    
    Allows multiple predictions in a single request
    """
    
    predictions: List[PredictionInput] = Field(
        ...,
        description="List of prediction inputs",
        min_items=1,
        max_items=100  # Limit batch size
    )
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "voltage": 240.5,
                        "global_intensity": 4.6,
                        "sub_metering_1": 1.2,
                        "sub_metering_2": 0.8,
                        "sub_metering_3": 17.0,
                        "hour": 14,
                        "day_of_week": 2,
                        "month": 4,
                        "is_weekend": 0
                    },
                    {
                        "voltage": 238.2,
                        "global_intensity": 3.2,
                        "sub_metering_1": 0.5,
                        "sub_metering_2": 0.2,
                        "sub_metering_3": 10.0,
                        "hour": 3,
                        "day_of_week": 2,
                        "month": 4,
                        "is_weekend": 0
                    }
                ]
            }
        }


class BatchPredictionOutput(BaseModel):
    """
    Output schema for batch predictions
    """
    
    predictions: List[dict] = Field(
        ...,
        description="List of predictions"
    )
    
    count: int = Field(
        ...,
        description="Number of predictions made",
        example=2
    )
    
    timestamp: str = Field(
        ...,
        description="Batch prediction timestamp",
        example="2024-04-16T14:30:00"
    )
    
    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "predicted_consumption_kw": 2.34,
                        "consumption_level": "Medium"
                    },
                    {
                        "predicted_consumption_kw": 0.85,
                        "consumption_level": "Low"
                    }
                ],
                "count": 2,
                "timestamp": "2024-04-16T14:30:00"
            }
        }


class ModelInfo(BaseModel):
    """
    Schema for model information endpoint
    """
    
    model_type: str = Field(
        ...,
        description="Type of ML model",
        example="RandomForestRegressor"
    )
    
    n_estimators: int = Field(
        ...,
        description="Number of trees in the forest",
        example=100
    )
    
    training_date: Optional[str] = Field(
        None,
        description="Date when model was trained",
        example="2024-04-15"
    )
    
    metrics: dict = Field(
        ...,
        description="Model performance metrics",
        example={
            "test_r2": 0.92,
            "test_mae": 0.15,
            "test_rmse": 0.21
        }
    )
    
    features: List[str] = Field(
        ...,
        description="List of features used by the model",
        example=[
            "voltage",
            "global_intensity",
            "sub_metering_1",
            "sub_metering_2",
            "sub_metering_3",
            "hour",
            "day_of_week",
            "month",
            "is_weekend"
        ]
    )


class HealthCheck(BaseModel):
    """
    Schema for health check endpoint
    """
    
    status: str = Field(
        ...,
        description="API status",
        example="healthy"
    )
    
    model_loaded: bool = Field(
        ...,
        description="Whether the ML model is loaded",
        example=True
    )
    
    timestamp: str = Field(
        ...,
        description="Health check timestamp",
        example="2024-04-16T14:30:00"
    )
    
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )


class ErrorResponse(BaseModel):
    """
    Schema for error responses
    """
    
    error: str = Field(
        ...,
        description="Error type",
        example="PredictionError"
    )
    
    message: str = Field(
        ...,
        description="Error message",
        example="Model failed to make prediction"
    )
    
    timestamp: str = Field(
        ...,
        description="Error timestamp",
        example="2024-04-16T14:30:00"
    )
    
    details: Optional[dict] = Field(
        None,
        description="Additional error details"
    )
