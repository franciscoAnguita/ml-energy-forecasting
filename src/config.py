"""
Configuration file for the Energy Consumption Forecasting ML Pipeline
Centralized settings for paths, model parameters, and API configuration
"""

import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model paths
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "energy_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

# Dataset URL (UCI Household Power Consumption)
DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip"
RAW_DATA_FILE = RAW_DATA_DIR / "household_power_consumption.txt"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "processed_energy_data.csv"

# Data preprocessing parameters
MISSING_VALUE_STRATEGY = "interpolate"  # Options: 'interpolate', 'drop', 'fill_median'
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Feature engineering
TIME_FEATURES = ["hour", "day_of_week", "month", "is_weekend"]
AGGREGATION_WINDOW = "1h"  # Resample to hourly data (lowercase 'h' for pandas 2.0+)

# Model parameters
MODEL_PARAMS = {
    "n_estimators": 100,
    "max_depth": 20,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": RANDOM_STATE,
    "n_jobs": -1  # Use all CPU cores
}

# Feature columns (will be updated after preprocessing)
FEATURE_COLUMNS = [
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

# Target column
TARGET_COLUMN = "Global_active_power"

# API configuration
API_TITLE = "Energy Consumption Forecasting API"
API_DESCRIPTION = "ML-powered API for predicting household energy consumption"
API_VERSION = "1.0.0"

# Consumption level thresholds (in kW)
CONSUMPTION_THRESHOLDS = {
    "low": 1.0,
    "medium": 3.0,
    "high": float("inf")
}

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
