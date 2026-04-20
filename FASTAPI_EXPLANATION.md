# 🚀 FASTAPI FILES EXPLAINED
## Complete Guide to the API Implementation

---

## 📁 Overview of the Three Files

The API is split into three files for **separation of concerns**:

1. **`schemas.py`** - Data models (what data looks like)
2. **`predict.py`** - Business logic (how to make predictions)
3. **`main.py`** - API endpoints (routes that handle requests)

**Why split into 3 files?**
- ✅ **Organized** - Each file has a clear purpose
- ✅ **Maintainable** - Easy to find and fix code
- ✅ **Testable** - Can test each part independently
- ✅ **Professional** - Industry-standard pattern

---

## 📄 FILE 1: `schemas.py` - Data Models

### 🎯 **Purpose:**
Defines the "shape" of data using Pydantic models.

**Think of it like:** A contract that says "this is what valid data looks like"

---

### **Key Concepts:**

#### **1. Pydantic BaseModel**
```python
class PredictionInput(BaseModel):
    voltage: float = Field(..., ge=200.0, le=260.0)
```

**What this does:**
- `voltage: float` → Must be a decimal number
- `ge=200.0` → Greater than or Equal to 200 (minimum)
- `le=260.0` → Less than or Equal to 260 (maximum)
- `...` → Required field (not optional)

**Why it's powerful:**
- FastAPI **automatically validates** the input
- If someone sends `voltage="hello"` → Error! (must be float)
- If someone sends `voltage=100` → Error! (must be ≥ 200)

---

#### **2. Field Descriptions**
```python
voltage: float = Field(
    ...,
    description="Voltage in volts (V)",
    example=240.5
)
```

**What this does:**
- `description` → Shows in API docs
- `example` → Sample value for testing

**Result:** Beautiful auto-generated documentation at `/docs`

---

#### **3. Custom Validators**
```python
@validator('is_weekend')
def validate_weekend_consistency(cls, v, values):
    day = values['day_of_week']
    expected_weekend = 1 if day >= 5 else 0
    if v != expected_weekend:
        raise ValueError("is_weekend doesn't match day_of_week!")
    return v
```

**What this does:**
Catches user errors like:
- `day_of_week=2` (Tuesday) but `is_weekend=1` ❌
- Automatically validates consistency

---

### **Models in schemas.py:**

1. **`PredictionInput`** - Single prediction request
2. **`PredictionOutput`** - Single prediction response
3. **`BatchPredictionInput`** - Multiple predictions request
4. **`BatchPredictionOutput`** - Multiple predictions response
5. **`ModelInfo`** - Model metadata
6. **`HealthCheck`** - API health status
7. **`ErrorResponse`** - Error format

---

## 🧮 FILE 2: `predict.py` - Prediction Logic

### 🎯 **Purpose:**
Contains all the logic for making predictions.

**Think of it like:** The "brain" that does the actual work

---

### **Key Functions:**

#### **1. `prepare_features(input_data)`**

**What it does:** Converts API input into model format

**Example:**
```python
# API receives this:
{
    "voltage": 240.5,
    "hour": 14,
    ...
}

# Function creates this:
DataFrame with columns: [Voltage, hour, Global_intensity, ...]
```

**Why needed:** Model expects specific column names and order

---

#### **2. `add_engineered_features(df)`**

**What it does:** Creates the same engineered features as training

**CRITICAL:** Must match training exactly!

```python
# Training created these:
hour_weekend_interaction = hour × is_weekend
voltage_intensity_product = voltage × intensity
total_sub_metering = sub1 + sub2 + sub3

# Prediction MUST create the same ones!
```

**Why critical:** If training used 12 features but prediction uses 9 → ERROR!

---

#### **3. `make_prediction(model, scaler, input_data)`**

**What it does:** The actual prediction pipeline

**Steps:**
1. Prepare features → DataFrame
2. Add engineered features
3. Scale features (using fitted scaler)
4. Make prediction
5. Calculate confidence
6. Classify consumption level
7. Return results

**Confidence calculation:**
```python
# Random Forest has 100 trees
# Each tree makes a prediction
# If all agree: High confidence
# If they disagree: Low confidence

tree_predictions = [2.3, 2.4, 2.3, 2.5, ...]  # From 100 trees
std = 0.1  # Low variance
confidence = 0.95  # High confidence!
```

---

#### **4. `classify_consumption(consumption_kw)`**

**What it does:** Converts number to category

```python
consumption_kw = 2.5
↓
Level = "Medium"

Thresholds:
< 1.0 kW → "Low"
1.0 - 3.0 kW → "Medium"
> 3.0 kW → "High"
```

**Why useful:** Easier for non-technical users to understand

---

#### **5. `validate_input_ranges(input_data)`**

**What it does:** Extra validation beyond Pydantic

**Example:**
```python
voltage = 240V
intensity = 50A
power = 240 × 50 = 12,000W = 12kW

# This exceeds typical household capacity!
# Raise warning/error
```

**Why needed:** Catches physically impossible values

---

## 🌐 FILE 3: `main.py` - FastAPI Application

### 🎯 **Purpose:**
The actual API server with endpoints

**Think of it like:** The "reception desk" that handles requests

---

### **Key Components:**

#### **1. App Initialization**
```python
app = FastAPI(
    title="Energy Consumption Forecasting API",
    description="ML-powered predictions",
    version="1.0.0"
)
```

**What this does:**
- Creates the FastAPI app
- Sets metadata (shows in docs)

---

#### **2. CORS Middleware**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    ...
)
```

**What this does:** Allows frontend apps to call the API

**Example:**
- Frontend at `http://localhost:3000` (React app)
- Can call API at `http://localhost:8000/predict`
- Without CORS → Browser blocks the request
- With CORS → Request allowed

---

#### **3. Startup Event**
```python
@app.on_event("startup")
async def load_model():
    global model, scaler
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
```

**What this does:** Loads model **once** when API starts

**Why important:**
- Loading model takes ~2-5 seconds
- Loading on every request = SLOW ❌
- Loading once at startup = FAST ✅

---

### **Endpoints Explained:**

#### **`GET /`** - Root endpoint
```python
@app.get("/")
async def root():
    return {"message": "Energy Forecasting API", "status": "running"}
```

**What it does:** Basic info about the API

**When to use:** Check if API is running

---

#### **`GET /health`** - Health check
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if model else "unhealthy",
        "model_loaded": model is not None
    }
```

**What it does:** Checks if model is loaded

**When to use:** Monitoring systems (UptimeRobot, Pingdom, etc.)

---

#### **`POST /predict`** - Main prediction endpoint
```python
@app.post("/predict")
async def predict(input_data: PredictionInput):
    # 1. Check model loaded
    # 2. Validate input
    # 3. Make prediction
    # 4. Return result
```

**What it does:** Makes a single prediction

**Request:**
```json
{
  "voltage": 240.5,
  "global_intensity": 4.6,
  "hour": 14,
  ...
}
```

**Response:**
```json
{
  "predicted_consumption_kw": 2.34,
  "consumption_level": "Medium",
  "confidence": 0.92
}
```

---

#### **`POST /predict-batch`** - Batch predictions
```python
@app.post("/predict-batch")
async def predict_batch(batch_input: BatchPredictionInput):
    # Process multiple inputs at once
```

**What it does:** Makes multiple predictions efficiently

**When to use:**
- Forecasting next 24 hours
- Analyzing different scenarios
- Bulk processing

---

#### **`GET /model-info`** - Model metadata
```python
@app.get("/model-info")
async def model_information():
    return {
        "model_type": "RandomForestRegressor",
        "n_estimators": 100,
        "features": [...]
    }
```

**What it does:** Returns info about the model

**When to use:** Understanding what the model does

---

### **Error Handling:**

#### **HTTP Status Codes:**
- `200` - Success
- `422` - Validation Error (bad input)
- `500` - Server Error (prediction failed)
- `503` - Service Unavailable (model not loaded)

#### **Global Exception Handler:**
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "error": type(exc).__name__,
        "message": "Internal server error"
    }
```

**What it does:** Catches unexpected errors gracefully

**Why important:** API doesn't crash, returns clean error

---

## 🔄 Complete Request Flow

Let's trace a prediction request through all three files:

```
1. USER SENDS REQUEST
   POST /predict
   {"voltage": 240.5, "hour": 14, ...}
   
2. main.py RECEIVES IT
   @app.post("/predict")
   async def predict(input_data: PredictionInput)
   
3. schemas.py VALIDATES IT
   PredictionInput model checks:
   ✅ voltage is float
   ✅ voltage is 200-260
   ✅ hour is 0-23
   ✅ is_weekend matches day_of_week
   
4. predict.py PROCESSES IT
   prepare_features() → DataFrame
   add_engineered_features() → More columns
   model.predict() → 2.34 kW
   classify_consumption() → "Medium"
   
5. main.py RETURNS RESPONSE
   PredictionOutput model formats:
   {
     "predicted_consumption_kw": 2.34,
     "consumption_level": "Medium",
     "confidence": 0.92,
     "timestamp": "2024-04-16T14:30:00"
   }
   
6. USER RECEIVES RESULT
   Status 200 OK
   JSON response
```

---

## 🎯 What This Shows Recruiters

### **API Design:**
- ✅ RESTful endpoints
- ✅ Proper HTTP methods (GET/POST)
- ✅ Clear naming (`/predict`, `/health`)
- ✅ Batch processing support

### **Data Validation:**
- ✅ Pydantic models
- ✅ Type checking
- ✅ Range validation
- ✅ Custom validators

### **Error Handling:**
- ✅ Proper status codes
- ✅ Descriptive error messages
- ✅ Global exception handling
- ✅ Graceful degradation

### **Performance:**
- ✅ Model loaded once (not per request)
- ✅ Batch processing
- ✅ Efficient data structures

### **Documentation:**
- ✅ Auto-generated docs at `/docs`
- ✅ Clear docstrings
- ✅ Example requests/responses

### **Best Practices:**
- ✅ Separation of concerns (3 files)
- ✅ Logging throughout
- ✅ Type hints everywhere
- ✅ CORS configuration
- ✅ Health check endpoint

---

## 🚀 How to Test

### **1. Start the API:**
```bash
uvicorn api.main:app --reload
```

### **2. Open interactive docs:**
```
http://localhost:8000/docs
```

### **3. Test `/predict` endpoint:**
Click "Try it out" and use the example data

### **4. Make a curl request:**
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

---

## 🐛 Common Issues

### **"Model not found"**
```
Solution: Train the model first
python -m src.model_training
```

### **"Port 8000 already in use"**
```
Solution: Use different port
uvicorn api.main:app --port 8001
```

### **"Module not found"**
```
Solution: Install dependencies
pip install -r requirements.txt
```

---

## 📚 Further Learning

**Pydantic:**
- Validation library
- Type checking
- Auto-documentation

**FastAPI:**
- Modern Python web framework
- Async support
- Auto docs with Swagger

**CORS:**
- Cross-Origin Resource Sharing
- Allows frontend apps to call API

**HTTP Status Codes:**
- 200 = Success
- 422 = Validation Error
- 500 = Server Error
- 503 = Service Unavailable

---

**Questions?** Test the API locally and refer to the API_GUIDE.md for usage examples!
