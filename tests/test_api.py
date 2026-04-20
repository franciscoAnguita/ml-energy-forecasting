"""
Basic API Tests
Tests for the Energy Consumption Forecasting API
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

# Create test client
client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns API information"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "status" in data
    assert data["status"] == "running"
    assert "version" in data


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "model_loaded" in data
    assert "timestamp" in data
    assert "version" in data


def test_version_endpoint():
    """Test the version endpoint"""
    response = client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "version" in data
    assert isinstance(data["version"], str)


def test_features_endpoint():
    """Test the features endpoint"""
    response = client.get("/features")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "required_features" in data
    assert "engineered_features" in data
    assert isinstance(data["required_features"], list)
    assert len(data["required_features"]) == 9  # 9 base features


def test_model_info_endpoint():
    """Test the model info endpoint (may fail if model not loaded)"""
    response = client.get("/model-info")
    
    # Should either return 200 with model info or 503 if model not loaded
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "model_type" in data
        assert "features" in data


def test_predict_endpoint_valid_input():
    """Test prediction endpoint with valid input"""
    valid_input = {
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
    
    response = client.post("/predict", json=valid_input)
    
    # Should either return 200 with prediction or 503 if model not loaded
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "predicted_consumption_kw" in data
        assert "consumption_level" in data
        assert "confidence" in data
        assert "timestamp" in data
        
        # Check data types
        assert isinstance(data["predicted_consumption_kw"], float)
        assert isinstance(data["consumption_level"], str)
        assert data["consumption_level"] in ["Low", "Medium", "High"]
        assert 0.0 <= data["confidence"] <= 1.0


def test_predict_endpoint_missing_field():
    """Test prediction endpoint with missing required field"""
    invalid_input = {
        "voltage": 240.5,
        # Missing global_intensity
        "sub_metering_1": 1.2,
        "sub_metering_2": 0.8,
        "sub_metering_3": 17.0,
        "hour": 14,
        "day_of_week": 2,
        "month": 4,
        "is_weekend": 0
    }
    
    response = client.post("/predict", json=invalid_input)
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_predict_endpoint_invalid_range():
    """Test prediction endpoint with out-of-range value"""
    invalid_input = {
        "voltage": 500.0,  # Too high (max is 260)
        "global_intensity": 4.6,
        "sub_metering_1": 1.2,
        "sub_metering_2": 0.8,
        "sub_metering_3": 17.0,
        "hour": 14,
        "day_of_week": 2,
        "month": 4,
        "is_weekend": 0
    }
    
    response = client.post("/predict", json=invalid_input)
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_predict_endpoint_invalid_type():
    """Test prediction endpoint with wrong data type"""
    invalid_input = {
        "voltage": "not_a_number",  # Should be float
        "global_intensity": 4.6,
        "sub_metering_1": 1.2,
        "sub_metering_2": 0.8,
        "sub_metering_3": 17.0,
        "hour": 14,
        "day_of_week": 2,
        "month": 4,
        "is_weekend": 0
    }
    
    response = client.post("/predict", json=invalid_input)
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_predict_endpoint_weekend_inconsistency():
    """Test prediction endpoint with inconsistent weekend flag"""
    invalid_input = {
        "voltage": 240.5,
        "global_intensity": 4.6,
        "sub_metering_1": 1.2,
        "sub_metering_2": 0.8,
        "sub_metering_3": 17.0,
        "hour": 14,
        "day_of_week": 2,  # Tuesday (weekday)
        "month": 4,
        "is_weekend": 1     # But marked as weekend - inconsistent!
    }
    
    response = client.post("/predict", json=invalid_input)
    
    # Should return 422 (validation error from custom validator)
    assert response.status_code == 422


def test_batch_predict_endpoint():
    """Test batch prediction endpoint"""
    batch_input = {
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
    
    response = client.post("/predict-batch", json=batch_input)
    
    # Should either return 200 or 503 if model not loaded
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "predictions" in data
        assert "count" in data
        assert "timestamp" in data
        assert data["count"] == 2
        assert len(data["predictions"]) == 2


def test_batch_predict_empty_list():
    """Test batch prediction with empty list"""
    batch_input = {
        "predictions": []
    }
    
    response = client.post("/predict-batch", json=batch_input)
    
    # Should return 422 (validation error - min_items=1)
    assert response.status_code == 422


def test_batch_predict_too_large():
    """Test batch prediction with too many items"""
    # Create 101 predictions (max is 100)
    predictions = []
    for i in range(101):
        predictions.append({
            "voltage": 240.5,
            "global_intensity": 4.6,
            "sub_metering_1": 1.2,
            "sub_metering_2": 0.8,
            "sub_metering_3": 17.0,
            "hour": 14,
            "day_of_week": 2,
            "month": 4,
            "is_weekend": 0
        })
    
    batch_input = {"predictions": predictions}
    
    response = client.post("/predict-batch", json=batch_input)
    
    # Should return 422 (too many items)
    assert response.status_code == 422


# Run tests with: pytest tests/test_api.py -v
