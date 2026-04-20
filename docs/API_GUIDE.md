# 🚀 API GUIDE
## Energy Consumption Forecasting API Documentation

---

## 📋 Overview

This API provides machine learning-powered predictions for household energy consumption. It's built with FastAPI and serves a trained Random Forest model.

**Base URL (local):** `http://localhost:8000`

**Tech Stack:**
- FastAPI (Python web framework)
- Pydantic (data validation)
- scikit-learn (ML model)
- uvicorn (ASGI server)

---

## 🎯 Endpoints

### **1. Health Check**

**Endpoint:** `GET /`

**Description:** Check if the API is running

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Energy Consumption Forecasting API",
  "status": "running",
  "version": "1.0.0"
}
```

---

### **2. Get Prediction**

**Endpoint:** `POST /predict`

**Description:** Predict energy consumption based on input features

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
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
}
```

**Field Descriptions:**
- `voltage` (float): Voltage in volts (typically 230-250V)
- `global_intensity` (float): Current intensity in amperes (A)
- `sub_metering_1` (float): Kitchen consumption in watt-hours
- `sub_metering_2` (float): Laundry consumption in watt-hours
- `sub_metering_3` (float): Climate control consumption in watt-hours
- `hour` (int): Hour of day (0-23)
- `day_of_week` (int): Day of week (0=Monday, 6=Sunday)
- `month` (int): Month (1-12)
- `is_weekend` (int): Weekend indicator (0=weekday, 1=weekend)

**Example Request (curl):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "voltage": 240.5,
    "global_intensity": 4.6,
    "sub_metering_1": 1.2,
    "sub_metering_2": 0.8,
    "sub_metering_3": 17.0,
    "hour": 14,
    "day_of_week": 2,
    "month": 4,
    "is_weekend": 0
  }'
```

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/predict"
data = {
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

response = requests.post(url, json=data)
print(response.json())
```

**Success Response (200 OK):**
```json
{
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
```

**Response Fields:**
- `predicted_consumption_kw`: Predicted energy consumption in kilowatts
- `consumption_level`: Classification (Low/Medium/High)
- `confidence`: Model confidence score (0-1)
- `timestamp`: Time of prediction
- `features_used`: Echo of input features (for verification)

**Error Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "loc": ["body", "voltage"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### **3. Model Information**

**Endpoint:** `GET /model-info`

**Description:** Get information about the trained model

**Request:**
```bash
curl http://localhost:8000/model-info
```

**Response:**
```json
{
  "model_type": "RandomForestRegressor",
  "n_estimators": 100,
  "training_date": "2024-04-15",
  "metrics": {
    "test_r2": 0.92,
    "test_mae": 0.15,
    "test_rmse": 0.21
  },
  "features": [
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
}
```

---

### **4. Batch Predictions**

**Endpoint:** `POST /predict-batch`

**Description:** Get predictions for multiple inputs at once

**Request Body:**
```json
{
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
```

**Response:**
```json
{
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
```

---

## 🎯 Interactive Documentation

FastAPI automatically generates interactive API documentation:

**Swagger UI:** `http://localhost:8000/docs`
- Interactive interface to test endpoints
- Automatic request/response examples
- Try out API calls directly in browser

**ReDoc:** `http://localhost:8000/redoc`
- Alternative documentation style
- Clean, readable format
- Good for sharing with stakeholders

---

## 🔧 Usage Examples

### **Example 1: Simple Prediction**

```python
import requests

# Define input
data = {
    "voltage": 240.0,
    "global_intensity": 5.0,
    "sub_metering_1": 2.0,
    "sub_metering_2": 1.0,
    "sub_metering_3": 15.0,
    "hour": 18,           # 6 PM
    "day_of_week": 5,     # Saturday
    "month": 7,           # July
    "is_weekend": 1       # Weekend
}

# Make prediction
response = requests.post("http://localhost:8000/predict", json=data)
result = response.json()

print(f"Predicted consumption: {result['predicted_consumption_kw']} kW")
print(f"Level: {result['consumption_level']}")
```

---

### **Example 2: Time-Series Predictions**

```python
import requests
from datetime import datetime, timedelta

# Predict for next 24 hours
predictions = []
start_time = datetime.now()

for hour_offset in range(24):
    current_time = start_time + timedelta(hours=hour_offset)
    
    data = {
        "voltage": 240.0,
        "global_intensity": 4.5,
        "sub_metering_1": 1.0,
        "sub_metering_2": 0.5,
        "sub_metering_3": 12.0,
        "hour": current_time.hour,
        "day_of_week": current_time.weekday(),
        "month": current_time.month,
        "is_weekend": 1 if current_time.weekday() >= 5 else 0
    }
    
    response = requests.post("http://localhost:8000/predict", json=data)
    predictions.append(response.json()['predicted_consumption_kw'])

# Analyze predictions
avg_consumption = sum(predictions) / len(predictions)
peak_hour = predictions.index(max(predictions))

print(f"Average predicted consumption: {avg_consumption:.2f} kW")
print(f"Peak consumption at hour: {peak_hour}")
```

---

### **Example 3: Error Handling**

```python
import requests

def get_prediction(data):
    """Get prediction with error handling"""
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json=data,
            timeout=5
        )
        response.raise_for_status()  # Raise error for bad status codes
        return response.json()
    
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API. Is it running?")
        return None
    
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e.response.status_code} - {e.response.text}")
        return None

# Use it
data = {"voltage": 240.0, "hour": 14, ...}
result = get_prediction(data)

if result:
    print(f"Prediction: {result['predicted_consumption_kw']} kW")
```

---

## 📊 Response Consumption Levels

The API classifies consumption into three levels:

| Level  | Range (kW) | Typical Scenario |
|--------|------------|------------------|
| Low    | < 1.0      | Night time, minimal appliances |
| Medium | 1.0 - 3.0  | Normal daytime usage |
| High   | > 3.0      | Peak usage, multiple appliances |

---

## 🛡️ Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200  | Success | Prediction successful |
| 422  | Validation Error | Invalid input data |
| 500  | Server Error | Model loading or prediction failed |
| 503  | Service Unavailable | Model not loaded |

---

## 🔒 Security Notes

**Current Implementation (Development):**
- No authentication required
- CORS enabled for all origins
- Suitable for local development/testing

**Production Recommendations:**
- Add API key authentication
- Implement rate limiting
- Enable HTTPS
- Restrict CORS to specific domains
- Add request logging
- Monitor for abuse

---

## 🚀 Starting the API

### **Development Mode:**
```bash
uvicorn api.main:app --reload
```

### **Production Mode:**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📈 Performance

**Expected Response Times:**
- Single prediction: ~50-100ms
- Batch predictions (10 items): ~200-300ms

**Throughput:**
- ~100-200 requests/second (single worker)
- ~400-800 requests/second (4 workers)

---

## 🐛 Troubleshooting

### **API won't start**
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Try a different port
uvicorn api.main:app --port 8001
```

### **Model not found error**
```bash
# Train the model first
python -m src.model_training

# Verify model file exists
ls -la models/energy_model.pkl
```

### **Import errors**
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Verify you're in the project root
pwd  # Should show .../ml-energy-forecasting
```

---

## 📚 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

## 💡 Tips for Developers

1. **Use the interactive docs** (`/docs`) for testing during development
2. **Validate inputs** - Pydantic handles this automatically
3. **Log predictions** for monitoring and debugging
4. **Cache model loading** - Model loads once at startup, not per request
5. **Handle edge cases** - Very high/low values, missing features, etc.

---

**Need help?** Check the main README.md or open an issue on GitHub.
