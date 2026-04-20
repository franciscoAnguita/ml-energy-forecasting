# ⚡ QUICKSTART GUIDE
## Get Up and Running in 5 Minutes

This guide gets you from "I just downloaded the project" to "API is running and making predictions."

---

## 🎯 CHOOSE YOUR SCENARIO

**👉 SCENARIO A:** First time running (need to train model)
**👉 SCENARIO B:** Model already trained (just run API)

Jump to your scenario below.

---

# 📦 SCENARIO A: FIRST TIME SETUP (Complete Pipeline)

Run this the **first time** you set up the project, or when you want to retrain the model.

---

## ⏱️ **Time Required:** ~10 minutes

---

## **STEP 1: Navigate to Project**

```bash
cd /path/to/ml-energy-forecasting
```

---

## **STEP 2: Activate Virtual Environment**

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```powershell
venv\Scripts\activate
```

**You should see:** `(venv)` appears before your command prompt

**If venv doesn't exist yet:** See [SETUP_GUIDE.md](SETUP_GUIDE.md) first

---

## **STEP 3: Generate Sample Data** *(Optional - skip if using real dataset)*

```bash
python -m src.generate_sample_data
```

**What this does:** Creates synthetic household energy data for testing

**Expected output:**
```
📊 SAMPLE DATA GENERATION
Sample data saved to: data/raw/household_power_consumption.txt
Generated 8,761 hourly records
✅ Done!
```

**Saved to:** `data/raw/household_power_consumption.txt`

**Skip this if:** You have the real UCI dataset (place it in `data/raw/`)

---

## **STEP 4: Run Data Preprocessing**

```bash
python -m src.data_preprocessing
```

**What this does:** Cleans the raw data, handles missing values, resamples to hourly

**Expected output:**
```
📥 STEP 1: Load raw data
   Loaded X rows
📊 STEP 2: Data type conversion
   Converted to numeric
🧹 STEP 3: Handle missing values
   Dropped X rows with missing values
⏰ STEP 4: Resample to hourly
   Resampled to 8,761 hourly records
💾 Saved: data/processed/processed_energy_data.csv
✅ PREPROCESSING COMPLETE
```

**Saved to:** `data/processed/processed_energy_data.csv`

---

## **STEP 5: Train the Model**

```bash
python -m src.model_training
```

**What this does:** 
- Engineers features (time features, interactions)
- Splits data (80% train, 20% test)
- Trains Random Forest model
- Evaluates performance
- Saves model and scaler

**Expected output:**
```
🚀 STARTING COMPLETE TRAINING PIPELINE
📥 STEP 1: Load preprocessed data
   Loaded 8,761 rows
📥 STEP 2: Feature engineering
   Created features: ['hour', 'day_of_week', 'month', 'is_weekend']
   Created: hour_weekend_interaction
   Created: voltage_intensity_product
   Created: total_sub_metering
   Final shape: (8761, 15)
📥 STEP 3: Prepare features and target
   Features shape: (8761, 12)
   Target shape: (8761,)
📊 STEP 4: Split data
   Training set: 7,008 samples
   Test set: 1,753 samples
🔧 STEP 5: Scale features
📚 STEP 6: Train Random Forest
   Training Random Forest with 100 trees...
   Training complete!
📊 STEP 7: Evaluate model
   R² Score: 0.9234
   MAE: 0.1523 kW
   RMSE: 0.2145 kW
💾 STEP 8: Save model
   ✅ Model saved: models/energy_model.pkl
   ✅ Scaler saved: models/scaler.pkl
✅ PIPELINE COMPLETE
```

**Saved to:**
- `models/energy_model.pkl` (trained model)
- `models/scaler.pkl` (fitted scaler)

**Time:** 30-60 seconds

---

## **STEP 6: Start the API**

```bash
uvicorn api.main:app --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/project']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:api.main:Loading model and scaler...
INFO:api.main:✅ Model and scaler loaded successfully
INFO:api.main:   Model type: RandomForestRegressor
INFO:     Application startup complete.
```

**API is now running!** Keep this terminal open.

**Access at:** `http://localhost:8000`

---

## **STEP 7: Test the API**

**Open browser:** `http://localhost:8000/docs`

**You should see:** Interactive Swagger UI documentation

**Make a test prediction:**
1. Click `POST /predict` (green box)
2. Click "Try it out"
3. Click "Execute" (uses pre-filled example data)
4. See prediction result:
   ```json
   {
     "predicted_consumption_kw": 2.34,
     "consumption_level": "Medium",
     "confidence": 0.92,
     "timestamp": "2024-04-20T15:30:00"
   }
   ```

**✅ SUCCESS!** Your ML pipeline is working end-to-end.

---

## **STEP 8: Run Tests** *(Optional)*

**Open a NEW terminal** (keep API running in the first one)

```bash
# Terminal 2
cd /path/to/ml-energy-forecasting
source venv/bin/activate
pytest tests/test_api.py -v
```

**Expected output:**
```
tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_predict_endpoint_valid_input PASSED
...
============ 14 passed in 2.35s ============
```

---

## **STEP 9: Stop the API**

**In Terminal 1** (where uvicorn is running):
```
Press Ctrl+C
```

**Expected output:**
```
INFO:     Shutting down
INFO:     Finished server process [12346]
```

---

# 🚀 SCENARIO B: QUICK START (Model Already Trained)

Use this when you've already run the complete pipeline once and just want to start the API.

---

## ⏱️ **Time Required:** ~30 seconds

---

## **STEP 1: Navigate to Project**

```bash
cd /path/to/ml-energy-forecasting
```

---

## **STEP 2: Activate Virtual Environment**

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```powershell
venv\Scripts\activate
```

**Verify:** You see `(venv)` in your prompt

---

## **STEP 3: Verify Model Files Exist**

```bash
ls models/
```

**Expected output:**
```
energy_model.pkl
scaler.pkl
```

**If missing:** Go to Scenario A (you need to train first)

---

## **STEP 4: Start the API**

```bash
uvicorn api.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:api.main:✅ Model and scaler loaded successfully
INFO:     Application startup complete.
```

**Keep this terminal open!**

---

## **STEP 5: Use the API**

**Browser:** `http://localhost:8000/docs`

**Make predictions:**
1. `POST /predict` → Try it out → Execute
2. See results instantly

**Or use curl:**
```bash
# Open a NEW terminal
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

## **STEP 6: Stop the API**

**Terminal 1:**
```
Press Ctrl+C
```

---

# 📋 DAILY WORKFLOW CHEAT SHEET

## **Every Time You Work on the Project:**

```bash
# 1. Navigate
cd /path/to/ml-energy-forecasting

# 2. Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Start API
uvicorn api.main:app --reload

# 4. Open browser
# Go to: http://localhost:8000/docs

# 5. When done, stop API
# Press Ctrl+C in the terminal
```

---

# 🔧 TROUBLESHOOTING

## **Issue: "Model not found" error**

**Symptom:**
```json
{
  "detail": "Model not loaded"
}
```

**Solution:** Train the model first (Scenario A, Step 5)

---

## **Issue: "Address already in use" error**

**Symptom:**
```
ERROR:    [Errno 48] Address already in use
```

**Solution:** Port 8000 is already in use

**Fix 1: Kill existing process**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

**Fix 2: Use different port**
```bash
uvicorn api.main:app --reload --port 8001
# Then access at http://localhost:8001
```

---

## **Issue: "Module not found" error**

**Symptom:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:** Venv not activated or dependencies not installed

**Fix:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## **Issue: Prediction returns error about missing feature**

**Symptom:**
```json
{
  "detail": "Feature names should match..."
}
```

**Solution:** Mismatch between training and prediction features

**Fix:** Retrain the model
```bash
python -m src.model_training
```

Then restart the API.

---

# ✅ VERIFICATION CHECKLIST

**Before considering setup complete, verify:**

- [ ] Virtual environment activates successfully
- [ ] `ls models/` shows `energy_model.pkl` and `scaler.pkl`
- [ ] `uvicorn api.main:app --reload` starts without errors
- [ ] Browser opens `http://localhost:8000/docs` successfully
- [ ] Test prediction returns valid JSON result
- [ ] All 14 tests pass: `pytest tests/test_api.py -v`

---

# 🎓 KEY CONCEPTS

## **Terminal Setup:**

**Always need 1 terminal minimum:**
- **Terminal 1:** Running API (`uvicorn ...`)

**For development, use 2 terminals:**
- **Terminal 1:** Running API
- **Terminal 2:** Running tests, making changes, using curl

## **Virtual Environment:**

**MUST activate every time** you:
- Open a new terminal
- Restart your computer
- Start working on the project

**How to tell if active:** `(venv)` appears in prompt

## **Training vs Prediction:**

**Training (once):**
- Loads historical data
- Learns patterns
- Saves model to disk
- Takes 30-60 seconds

**Prediction (many times):**
- Loads saved model
- Makes predictions instantly
- Takes <50ms per request
- No data needed (uses model in memory)

---

# 📚 NEXT STEPS

**After quickstart works:**

1. Read [COMPLETE_PIPELINE_NARRATIVE.md](../COMPLETE_PIPELINE_NARRATIVE.md) to understand how it all works
2. Read [API_GUIDE.md](API_GUIDE.md) for detailed API documentation
3. Explore the code in `src/` and `api/` folders
4. Try modifying features or model parameters
5. Deploy to production ([DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))

---

**Questions? Check the main [README.md](../README.md) or the troubleshooting section above.**
