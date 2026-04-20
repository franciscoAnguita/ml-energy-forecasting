# 🚀 SETUP GUIDE - Energy Consumption Forecasting Project

Complete installation and setup instructions for the ML pipeline and API.

---

## PREREQUISITES

Before you begin, ensure you have:

- **Python 3.8 or higher** (3.10+ recommended)
  - Check: `python3 --version` or `python --version`
- **pip** (Python package manager)
  - Check: `pip --version`
- **Git** (for cloning from GitHub)
  - Check: `git --version`
- **5GB free disk space** (for dependencies and data)

---

## STEP 1: GET THE PROJECT

### **Option A: Clone from GitHub**

```bash
git clone https://github.com/franciscoAnguita/ml-energy-forecasting.git
cd ml-energy-forecasting
```

### **Option B: Download ZIP**

1. Go to GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Navigate into the folder:
   ```bash
   cd ml-energy-forecasting
   ```

---

##  STEP 2: UNDERSTAND THE STRUCTURE

After extracting, you should see:

```
ml-energy-forecasting/
│
├── README.md                   ← Project overview
├── requirements.txt            ← Python dependencies
├── .gitignore                  ← Git ignore rules
├── Dockerfile                  ← Docker configuration
│
├── data/                       ← Datasets (gitignored)
│   ├── raw/                    ← Raw data files
│   │   └── household_power_consumption.txt
│   └── processed/              ← Preprocessed data
│       └── processed_energy_data.csv
│
├── models/                     ← Saved models (gitignored until trained)
│   ├── energy_model.pkl        ← Trained Random Forest model
│   └── scaler.pkl              ← Fitted StandardScaler
│
├── src/                        ← ML pipeline source code
│   ├── __init__.py
│   ├── config.py               ← Configuration constants
│   ├── data_ingestion.py       ← Load raw data
│   ├── data_preprocessing.py   ← Clean & prepare data
│   ├── feature_engineering.py  ← Create features
│   ├── model_training.py       ← Train & evaluate model
│   └── generate_sample_data.py ← Generate synthetic data
│
├── api/                        ← FastAPI application
│   ├── __init__.py
│   ├── main.py                 ← API endpoints & routing
│   ├── schemas.py              ← Pydantic data models
│   └── predict.py              ← Prediction logic
│
├── tests/                      ← Test suite
│   ├── __init__.py
│   └── test_api.py             ← API endpoint tests
│
└── docs/                       ← Documentation
    ├── SETUP_GUIDE.md          ← This file
    ├── QUICKSTART.md           ← Quick reference
    ├── API_GUIDE.md            ← API documentation
    ├── DEPLOYMENT_GUIDE.md     ← Production deployment
    └── DATA_SOURCE.md          ← Data documentation

``` 

**Note:** Some folders (like `data/`, `models/`, `auxiliary/`) won't exist until you create them or run the pipeline.

---

## STEP 3: CREATE VIRTUAL ENVIRONMENT

A virtual environment isolates this project's Python packages from your system Python.

### **Why use a virtual environment?**

- Prevents dependency conflicts between projects
- Easy to reproduce exact package versions
- Clean uninstall (just delete the `venv/` folder)

### **Create and activate:**

#### **Linux/Mac:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should now see (venv) in your prompt
```

#### **Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should now see (venv) in your prompt
```

#### **Windows (Command Prompt):**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### **Verify activation:**

Your terminal prompt should now look like:
```
(venv) user@computer:~/ml-energy-forecasting$
```

The `(venv)` prefix means the virtual environment is active.

---

## STEP 4: INSTALL DEPENDENCIES

With the virtual environment **activated**:

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### **What gets installed:**

**Core ML libraries:**
- `pandas` - Data manipulation
- `numpy` - Numerical computations
- `scikit-learn` - Machine learning
- `joblib` - Model serialization

**API framework:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

**Development tools:**
- `pytest` - Testing framework
- `requests` - HTTP client (for tests)

### **Expected output:**

```
Collecting pandas
  Downloading pandas-2.0.3-cp310-cp310-linux_x86_64.whl (12.4 MB)
...
Successfully installed pandas-2.0.3 scikit-learn-1.3.0 fastapi-0.103.0 ...
```

### **Verify installation:**

```bash
python -c "import pandas, sklearn, fastapi; print('All core packages installed!')"
```

**Expected:** `All core packages installed!`

---

## STEP 5: CREATE REQUIRED DIRECTORIES

Some directories are gitignored (not in the repository). Create them manually:

```bash
# Create data directories
mkdir -p data/raw
mkdir -p data/processed

# Create models directory
mkdir -p models

# Create auxiliary docs (optional - for your learning materials)
mkdir -p auxiliary/docs
```

---

## STEP 6: VERIFY SETUP

Run these verification commands:

### **Check Python version:**
```bash
python --version
```
**Expected:** Python 3.8+ (3.10+ recommended)

### **Check venv is active:**
```bash
which python  # Linux/Mac
where python  # Windows
```
**Expected:** Path should include `venv/` folder

### **Check packages:**
```bash
pip list
```
**Expected:** Should show pandas, scikit-learn, fastapi, etc.

### **Check directory structure:**
```bash
ls -la
```
**Expected:** Should see src/, api/, data/, models/, tests/ folders

---

## STEP 7: GET THE DATASET (Optional)

You have two options for data:

### **Option A: Generate Synthetic Data (Quick)**

```bash
python -m src.generate_sample_data
```

**Pros:** Instant, no download needed
**Cons:** Synthetic (not real data)

### **Option B: Download Real UCI Dataset (Recommended)**

1. **Download from:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/individual+household+electric+power+consumption)

2. **Or use direct link:** 
   ```bash
   wget https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip
   unzip household_power_consumption.zip
   mv household_power_consumption.txt data/raw/
   ```

3. **Or manually:**
   - Download the ZIP file
   - Extract `household_power_consumption.txt`
   - Place in `data/raw/` folder

**File size:** ~130MB (20 million rows)

---

## STEP 8: RUN INITIAL TESTS

Verify everything works:

### **Test 1: Import modules**
```bash
python -c "from src import config; print(' src/ imports work')"
python -c "from api import schemas; print(' api/ imports work')"
```

### **Test 2: Configuration**
```bash
python -c "from src.config import MODEL_PATH; print(f'Model will be saved to: {MODEL_PATH}')"
```

**Expected:** Shows path like `models/energy_model.pkl`

---

## 🎓 STEP 9: UNDERSTAND THE WORKFLOW

Now that setup is complete, here's the typical workflow:

### **First Time (Complete Pipeline):**

```bash
# 1. Activate venv (if not already)
source venv/bin/activate

# 2. Generate or download data
python -m src.generate_sample_data

# 3. Preprocess data
python -m src.data_preprocessing

# 4. Train model
python -m src.model_training

# 5. Start API
uvicorn api.main:app --reload

# 6. Test at http://localhost:8000/docs
```

### **Daily Use (API Only):**

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Start API
uvicorn api.main:app --reload

# 3. Use API at http://localhost:8000/docs
```

**See [QUICKSTART.md](QUICKSTART.md) for detailed step-by-step instructions.**

---

## 🔧 TROUBLESHOOTING

### **Issue: "python3: command not found"**

**Try:**
```bash
python --version  # Use 'python' instead of 'python3'
```

**If Python not installed:** Install from [python.org](https://www.python.org/downloads/)

---

### **Issue: "pip: command not found"**

**Linux:**
```bash
sudo apt-get install python3-pip
```

**Mac:**
```bash
python3 -m ensurepip --upgrade
```

**Windows:** Reinstall Python with "Add to PATH" checked

---

### **Issue: "Permission denied" activating venv**

**Linux/Mac:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

### **Issue: Package installation fails**

**Try installing one by one:**
```bash
pip install pandas
pip install scikit-learn
pip install fastapi
pip install uvicorn
pip install pydantic
pip install pytest
```

**Or upgrade pip:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### **Issue: "ModuleNotFoundError" when running code**

**Cause:** Virtual environment not activated

**Solution:**
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Verify:** You see `(venv)` in your prompt

---

### **Issue: "No such file or directory: data/raw/..."**

**Cause:** Data directory doesn't exist or data file missing

**Solution:**
```bash
mkdir -p data/raw
python -m src.generate_sample_data
```

---

## DOCKER SETUP (Alternative)

If you prefer Docker:

```bash
# Build image
docker build -t energy-forecasting-api .

# Run container
docker run -d -p 8000:8000 --name energy-api energy-forecasting-api

# Check logs
docker logs energy-api

# Access API
curl http://localhost:8000/health

# Stop container
docker stop energy-api
docker rm energy-api
```

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment.**

---

## CLEANUP

### **Deactivate virtual environment:**
```bash
deactivate
```

### **Remove virtual environment:**
```bash
rm -rf venv/  # Linux/Mac
rmdir /s venv  # Windows
```

### **Start fresh:**
```bash
rm -rf venv/ data/ models/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## VERIFICATION CHECKLIST

Before proceeding to run the pipeline, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] `(venv)` appears in terminal prompt
- [ ] All packages installed successfully
- [ ] `data/` and `models/` directories exist
- [ ] Can import: `from src import config`
- [ ] Can import: `from api import schemas`

---

## NEXT STEPS

**Setup complete!** Now you're ready to:

1. **Run the pipeline:** See [QUICKSTART.md](QUICKSTART.md)
2. **Use the API:** See [API_GUIDE.md](API_GUIDE.md)
3. **Deploy to production:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## BEST PRACTICES

### **Always:**
- Activate venv before working (`source venv/bin/activate`)
- Keep `requirements.txt` updated (`pip freeze > requirements.txt`)
- Use `.gitignore` (don't commit `venv/`, `data/`, `__pycache__/`)

### **Never:**
- Install packages system-wide (always use venv)
- Commit large data files or models to Git
- Share your venv folder (share `requirements.txt` instead)

### **Development workflow:**
```bash
# Morning routine
cd ml-energy-forecasting
source venv/bin/activate
git pull
pip install -r requirements.txt  # If requirements changed

# Work on code...

# Evening routine
git add .
git commit -m "Description of changes"
git push
deactivate
```

---

## COMMON QUESTIONS

### **Q: Do I need to activate venv every time?**
**A:** YES. Every time you open a new terminal or restart your computer.

### **Q: Can I use conda instead?**
**A:** Yes!
```bash
conda create -n energy-ml python=3.10
conda activate energy-ml
pip install -r requirements.txt
```

### **Q: How much disk space do I need?**
**A:** 
- Virtual environment: ~500MB
- Dependencies: ~1GB
- Data (if using UCI dataset): ~200MB
- Models: ~50MB
- **Total:** ~2GB

### **Q: What if I want to use a different Python version?**
**A:** 
```bash
python3.10 -m venv venv  # Specify version
source venv/bin/activate
pip install -r requirements.txt
```

### **Q: How do I update dependencies?**
**A:**
```bash
pip install --upgrade package_name
pip freeze > requirements.txt  # Update requirements file
```

---

## GETTING HELP

**If you encounter issues:**

1. Check the Troubleshooting section above
2. Check [QUICKSTART.md](QUICKSTART.md) for workflow guidance
3. Search error messages online
4. Check package documentation
5. Open an issue on GitHub

---

**Setup complete! Proceed to [QUICKSTART.md](QUICKSTART.md) to run the pipeline.**
