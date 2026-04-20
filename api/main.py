"""
FastAPI Main Application
Energy Consumption Forecasting API
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import joblib
from pathlib import Path
from contextlib import asynccontextmanager

# Import schemas
from api.schemas import (
    PredictionInput,
    PredictionOutput,
    BatchPredictionInput,
    BatchPredictionOutput,
    ModelInfo,
    HealthCheck,
    ErrorResponse
)

# Import prediction functions
from api.predict import (
    make_prediction,
    make_batch_predictions,
    get_model_info,
    validate_input_ranges
)

# Import config
from src.config import MODEL_PATH, SCALER_PATH, API_TITLE, API_DESCRIPTION, API_VERSION

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware (allows frontend applications to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and scaler
model = None
scaler = None


@asynccontextmanager
async def load_model(app: FastAPI):
    """
    Loads the trained model and scaler when the API starts
    
    This runs once at startup, not on every request.
    Makes the API much faster since model loading is slow.
    """
    global model, scaler
    
    try:
        logger.info("Loading model and scaler...")
        
        # Check if model file exists
        if not MODEL_PATH.exists():
            logger.error(f"Model file not found at {MODEL_PATH}")
            logger.error("Please train the model first: python -m src.model_training")
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        
        # Check if scaler file exists
        if not SCALER_PATH.exists():
            logger.error(f"Scaler file not found at {SCALER_PATH}")
            raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
        
        # Load model and scaler
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        logger.info("✅ Model and scaler loaded successfully")
        logger.info(f"   Model type: {type(model).__name__}")
        logger.info(f"   Model path: {MODEL_PATH}")
        logger.info(f"   Scaler path: {SCALER_PATH}")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        # Don't raise - allow API to start but endpoints will fail gracefully
        model = None
        scaler = None

    yield  # API runs here
    
    # SHUTDOWN: Cleanup (if needed)
    logger.info("API shutting down...")

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=load_model  
)


@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Basic API information
    
    Returns:
        dict: API status and information
    """
    return {
        "message": API_TITLE,
        "status": "running",
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthCheck,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check():
    """
    Health check endpoint
    
    Used by monitoring systems to verify the API is running correctly.
    Checks if the model is loaded and ready to make predictions.
    
    Returns:
        HealthCheck: API health status
    """
    return HealthCheck(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat(),
        version=API_VERSION
    )


@app.post(
    "/predict",
    response_model=PredictionOutput,
    tags=["Predictions"],
    summary="Make a single prediction",
    responses={
        200: {"description": "Prediction successful"},
        422: {"description": "Validation error"},
        500: {"description": "Prediction failed"}
    }
)
async def predict(input_data: PredictionInput):
    """
    Predict energy consumption for given input features
    
    This endpoint takes household electricity features and returns:
    - Predicted consumption in kW
    - Consumption level classification (Low/Medium/High)
    - Model confidence score
    - Timestamp
    
    Args:
        input_data (PredictionInput): Input features
        
    Returns:
        PredictionOutput: Prediction results
        
    Raises:
        HTTPException: If model not loaded or prediction fails
    """
    
    # Check if model is loaded
    if model is None or scaler is None:
        logger.error("Prediction attempted but model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        # Validate input ranges
        #validate_input_ranges(input_data.dict()) dict() is deprecated
        validate_input_ranges(input_data.model_dump())
        
        # Make prediction
        logger.info(f"Prediction request: hour={input_data.hour}, weekend={input_data.is_weekend}")
        #   result = make_prediction(model, scaler, input_data.dict()) dict() is deprecated
        result = make_prediction(model, scaler, input_data.model_dump())
        
        return PredictionOutput(**result)
        
    except ValueError as e:
        # Validation or prediction error
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post(
    "/predict-batch",
    response_model=BatchPredictionOutput,
    tags=["Predictions"],
    summary="Make batch predictions",
    responses={
        200: {"description": "Batch prediction successful"},
        422: {"description": "Validation error"},
        500: {"description": "Batch prediction failed"}
    }
)
async def predict_batch(batch_input: BatchPredictionInput):
    """
    Make predictions for multiple inputs at once
    
    More efficient than making individual /predict calls.
    Useful for:
    - Forecasting next 24 hours
    - Analyzing different scenarios
    - Bulk data processing
    
    Args:
        batch_input (BatchPredictionInput): List of prediction inputs
        
    Returns:
        BatchPredictionOutput: List of predictions
        
    Raises:
        HTTPException: If model not loaded or prediction fails
    """
   
    # Check if model is loaded
    if model is None or scaler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        # Validate batch size
        if len(batch_input.predictions) > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Batch size too large. Maximum 100 predictions per request."
            )
        
        # Convert Pydantic models to dicts
        #inputs_list = [item.dict() for item in batch_input.predictions]  dict() deprecated
        inputs_list = [item.model_dump() for item in batch_input.predictions]
        
        
        # Make batch predictions
        logger.info(f"Batch prediction request: {len(inputs_list)} items")
        result = make_batch_predictions(model, scaler, inputs_list)
        
        return BatchPredictionOutput(**result)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get(
    "/model-info",
    response_model=ModelInfo,
    tags=["Model"],
    summary="Get model information"
)
async def model_information():
    """
    Get information about the trained model
    
    Returns metadata about the model including:
    - Model type
    - Number of estimators (for ensemble models)
    - Training metrics
    - Features used
    
    Returns:
        ModelInfo: Model metadata
        
    Raises:
        HTTPException: If model not loaded
    """
    
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        info = get_model_info(model)
        return ModelInfo(**info)
        
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    
    Catches any unhandled exceptions and returns a consistent error format.
    This prevents the API from crashing and leaking error details.
    """
    
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": type(exc).__name__,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# Additional utility endpoints

@app.get("/version", tags=["Info"])
async def version():
    """Get API version"""
    return {"version": API_VERSION}


@app.get("/features", tags=["Info"])
async def get_features():
    """
    Get list of features expected by the model
    
    Useful for API clients to know what data to provide
    """
    return {
        "required_features": [
            "voltage",
            "global_intensity",
            "sub_metering_1",
            "sub_metering_2",
            "sub_metering_3",
            "hour",
            "day_of_week",
            "month",
            "is_weekend"
        ],
        "engineered_features": [
            "hour_weekend_interaction",
            "voltage_intensity_product",
            "total_sub_metering"
        ]
    }


if __name__ == "__main__":
    """
    Run the API with uvicorn when executed directly
    
    For development only. In production, use:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
    """
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
