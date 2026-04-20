# ⚡ Energy Consumption Forecasting - ML Pipeline & API

A complete machine learning pipeline that predicts household energy consumption using Random Forest regression and serves predictions via a FastAPI REST API.

---

## Project Overview

This project demonstrates an end-to-end ML workflow:
- Data ingestion and preprocessing
- Feature engineering with domain knowledge
- Model training and evaluation
- Production-ready API deployment
- Comprehensive testing and documentation

**Use Case:** Predict household electricity consumption (kW) based on voltage, current, sub-metering data, and time features.

---

## Features

- ✅ **Complete ML Pipeline** - From raw data to deployed model
- ✅ **Feature Engineering** - Time-based and interaction features
- ✅ **Model Training** - Random Forest with performance metrics
- ✅ **REST API** - FastAPI with automatic documentation
- ✅ **Data Validation** - Pydantic models with custom validators
- ✅ **Batch Predictions** - Process multiple inputs efficiently
- ✅ **Testing** - Pytest test suite
- ✅ **Docker Support** - Containerized deployment
- ✅ **Comprehensive Docs** - Setup, API, and deployment guides

---

## Tech Stack

**ML & Data:**
- Python 3.10+
- pandas, NumPy - Data manipulation
- scikit-learn - Machine learning
- joblib - Model serialization

**API:**
- FastAPI - Modern Python web framework
- Pydantic - Data validation
- uvicorn - ASGI server

**Development:**
- pytest - Testing
- Docker - Containerization

---

## Project Structure

```
ml-energy-forecasting/
├── src/                        # ML pipeline code
│   ├── config.py               # Configuration
│   ├── data_ingestion.py       # Data loading
│   ├── data_preprocessing.py   # Data cleaning
│   ├── feature_engineering.py  # Feature creation
│   ├── model_training.py       # Model training
│   └── generate_sample_data.py # Sample data generator
│
├── api/                        # FastAPI application
│   ├── main.py                 # API endpoints
│   ├── schemas.py              # Pydantic models
│   └── predict.py              # Prediction logic
│
├── data/                       # Datasets (gitignored)
│   ├── raw/                    # Raw data
│   └── processed/              # Preprocessed data
│
├── models/                     # Trained models
│   ├── energy_model.pkl        # Saved model
│   └── scaler.pkl              # Fitted scaler
│
├── tests/                      # Test files
│   └── test_api.py             # API tests
│
├── docs/                       # Documentation
│   ├── SETUP_GUIDE.md          # Setup instructions
│   ├── API_GUIDE.md            # API documentation
│   ├── DEPLOYMENT_GUIDE.md     # Deployment guide
│   ├── QUICKSTART.md           # Quick reefrence
│   └── DATA_SOURCE.md          # Data documentation
│
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

---

## Installation & Setup

### **Prerequisites**
- Python 3.10 or higher
- pip (Python package manager)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/franciscoAnguita/ml-energy-forecasting.git
cd ml-energy-forecasting
```

### **Step 2: Create Virtual Environment**
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### **Step 3: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 4: Generate Sample Data (if needed)**
```bash
python -m src.generate_sample_data
```

### **Step 5: Run the ML Pipeline**
```bash
# Data preprocessing
python -m src.data_preprocessing

# Feature engineering and model training
python -m src.model_training
```

### **Step 6: Start the API**
```bash
uvicorn api.main:app --reload
```

API will be available at: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

---

## Quick Start

### **Make a Prediction**

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

**Response:**
```json
{
  "predicted_consumption_kw": 2.34,
  "consumption_level": "Medium",
  "confidence": 0.92,
  "timestamp": "2024-04-16T14:30:00",
  "features_used": {...}
}
```

### **Python Example**

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

---

## Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_api.py -v

# With coverage
pytest tests/ --cov=api --cov-report=html
```

---

## Docker Deployment

### **Build Image**
```bash
docker build -t energy-forecasting-api .
```

### **Run Container**
```bash
docker run -d -p 8000:8000 --name energy-api energy-forecasting-api
```

### **Access API**
```bash
curl http://localhost:8000/health
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/predict` | POST | Single prediction |
| `/predict-batch` | POST | Batch predictions |
| `/model-info` | GET | Model metadata |
| `/version` | GET | API version |
| `/features` | GET | Required features list |
| `/docs` | GET | Interactive API docs |

See [API_GUIDE.md](docs/API_GUIDE.md) for detailed documentation.

---

## Model Performance

**Metrics on test set:**
- **R² Score:** ~0.92 (92% variance explained)
- **MAE:** ~0.15 kW (average error)
- **RMSE:** ~0.21 kW
- **MAPE:** ~8% (percentage error)

**Model:** Random Forest Regressor with 100 trees

**Features:**
- 9 base features (voltage, intensity, sub-metering, time)
- 3 engineered features (interactions, totals)

---

## What This Project Demonstrates

### **For Data Science Roles:**
- Complete ML pipeline (data → model → deployment)
- Feature engineering with domain knowledge
- Model evaluation and interpretation
- Production-ready code structure

### **For ML Engineering Roles:**
- API development with FastAPI
- Data validation with Pydantic
- Model serving and deployment
- Containerization with Docker
- Testing and documentation

### **For Software Engineering Roles:**
- Clean code architecture
- Separation of concerns
- Error handling and logging
- REST API design
- Comprehensive testing

---

## Dataset

**Source:** UCI Machine Learning Repository - Household Power Consumption Dataset

**Features:**
- **Voltage** - Electric voltage (V)
- **Global_intensity** - Current intensity (A)
- **Sub_metering_1-3** - Energy sub-metering (Wh)
- **Time features** - Hour, day of week, month, weekend flag

**Target:** `Global_active_power` - Total active power (kW)

**Note:** A synthetic dataset generator is included for testing when the real dataset is unavailable.

---

## Documentation

- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[API_GUIDE.md](docs/API_GUIDE.md)** - Complete API documentation
- **[DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Production deployment guide

---

## Configuration

All configuration is centralized in `src/config.py`:

- Data paths
- Model parameters
- API settings
- Consumption thresholds

Modify this file to customize the pipeline.

---

## Roadmap

**Potential enhancements:**
- [ ] Add authentication (API keys)
- [ ] Implement caching (Redis)
- [ ] Add monitoring (Prometheus/Grafana)
- [ ] Support multiple models
- [ ] Time-series forecasting (next 24 hours)
- [ ] Model retraining pipeline
- [ ] CI/CD with GitHub Actions

---

## Troubleshooting

### **API won't start**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn api.main:app --port 8001
```

### **Model not found**
```bash
# Train the model first
python -m src.model_training
```

### **Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Author

**Your Name**
- GitHub: https://github.com/franciscoAnguita
- LinkedIn: https://linkedin.com/in/francisco-anguita-15a95117
- Email: pacoanguita@hotmail.com

---

## Acknowledgments

- UCI Machine Learning Repository for the dataset
- FastAPI framework for excellent documentation
- The open-source community

---

## Contact

For questions or feedback:
- Open an issue on GitHub
- Email: pacoanguita@hotmail.com
- LinkedIn: https://linkedin.com/in/francisco-anguita-15a95117

---

**⭐ If you find this project useful, please consider giving it a star on GitHub!**
