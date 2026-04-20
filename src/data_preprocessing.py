"""
Data Preprocessing Module
Handles missing values, outliers, and data type conversions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from src.config import (
    RAW_DATA_FILE,
    PROCESSED_DATA_FILE,
    MISSING_VALUE_STRATEGY,
    TEST_SIZE,
    RANDOM_STATE,
    TARGET_COLUMN,
    SCALER_PATH,
    AGGREGATION_WINDOW
)
from src.data_ingestion import load_raw_data


def handle_missing_values(df, strategy="interpolate"):
    """
    Handles missing values in the dataset
    
    Args:
        df (pd.DataFrame): Input dataframe
        strategy (str): Strategy for handling missing values
                       - 'interpolate': Time-based interpolation (best for time series)
                       - 'drop': Remove rows with missing values
                       - 'fill_median': Fill with column median
    
    Returns:
        pd.DataFrame: Dataframe with missing values handled
    """
    
    print(f"\nHandling missing values using strategy: '{strategy}'")
    
    initial_rows = len(df)
    missing_before = df.isnull().sum().sum()
    
    if strategy == "interpolate":
        # Time-based interpolation (best for time series)
        df = df.set_index('datetime')
        df = df.interpolate(method='time', limit_direction='both')
        df = df.reset_index()
        
    elif strategy == "drop":
        # Drop rows with any missing values
        df = df.dropna()
        
    elif strategy == "fill_median":
        # Fill with median of each column
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df[col].fillna(df[col].median(), inplace=True)
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    missing_after = df.isnull().sum().sum()
    rows_after = len(df)
    
    print(f"   Missing values: {missing_before:,} → {missing_after:,}")
    print(f"   Rows: {initial_rows:,} → {rows_after:,} (lost {initial_rows - rows_after:,})")
    
    return df


def remove_outliers(df, columns=None, n_std=3):
    """
    Removes outliers using the Z-score method
    
    Args:
        df (pd.DataFrame): Input dataframe
        columns (list): Columns to check for outliers (None = all numeric)
        n_std (float): Number of standard deviations for outlier threshold
    
    Returns:
        pd.DataFrame: Dataframe with outliers removed
    """
    print(f"\n Removing outliers (threshold: {n_std} std deviations)")
    
    initial_rows = len(df)
    
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    # Calculate Z-scores
    for col in columns:
        if col in df.columns:
            mean = df[col].mean()
            std = df[col].std()
            z_scores = np.abs((df[col] - mean) / std)
            df = df[z_scores < n_std]
    
    rows_after = len(df)
    print(f"   Rows: {initial_rows:,} → {rows_after:,} (removed {initial_rows - rows_after:,} outliers)")
    
    return df


def resample_to_hourly(df):
    
    """
    Resamples minute-level data to hourly averages
    Reduces data volume while preserving patterns
    
    Args:
        df (pd.DataFrame): Input dataframe with datetime index
        
    Returns:
        pd.DataFrame: Hourly resampled data
    """


    print(f"\n Resampling data to hourly intervals...")
    
    initial_rows = len(df)
    
    # Set datetime as index for resampling
    df = df.set_index('datetime')
    
    # Resample to hourly, taking the mean
    df_hourly = df.resample(AGGREGATION_WINDOW).mean()
    
    # Reset index to make datetime a column again
    df_hourly = df_hourly.reset_index()
    
    # Drop any rows with NaN (from resampling)
    df_hourly = df_hourly.dropna()
    
    rows_after = len(df_hourly)
    print(f"   Rows: {initial_rows:,} → {rows_after:,} (aggregated to hourly)")
    
    return df_hourly


def validate_data_types(df):
    
    """
    Ensures all columns have correct data types
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        pd.DataFrame: Dataframe with validated types
    """


    print("\n Validating data types...")
    
    # Ensure datetime is datetime type
    if 'datetime' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Ensure all other columns are numeric
    numeric_columns = [col for col in df.columns if col != 'datetime']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"   Data types validated")
    print(f"\n{df.dtypes}")
    
    return df


def preprocess_pipeline(df_raw):
   
    """
    Complete preprocessing pipeline
    
    Args:
        df_raw (pd.DataFrame): Raw data from ingestion
        
    Returns:
        pd.DataFrame: Fully preprocessed data
    """


    print("\n" + "="*70)
    print(" STARTING PREPROCESSING PIPELINE")
    print("="*70)
    
    # Step 1: Validate data types
    df = validate_data_types(df_raw.copy())
    
    # Step 2: Handle missing values
    df = handle_missing_values(df, strategy=MISSING_VALUE_STRATEGY)
    
    # Step 3: Resample to hourly (reduces volume, improves training speed)
    df = resample_to_hourly(df)
    
    # Step 4: Remove outliers (optional - comment out if you want to keep all data)
    # df = remove_outliers(df, n_std=4)  # More lenient threshold for energy data
    
    # Step 5: Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)
    
    print("\n" + "="*70)
    print(" PREPROCESSING COMPLETE")
    print("="*70)
    print(f" Final shape: {df.shape}")
    print(f" Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"\n{df.describe()}")
    
    return df


def save_processed_data(df):
   
    """
    Saves preprocessed data to disk
    
    Args:
        df (pd.DataFrame): Preprocessed dataframe
    """
   
   
    print(f"\n Saving processed data to {PROCESSED_DATA_FILE}...")
    
    PROCESSED_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_FILE, index=False)
    
    file_size = PROCESSED_DATA_FILE.stat().st_size / 1024 / 1024
    print(f"    Saved! File size: {file_size:.2f} MB")


def load_processed_data():
    
    """
    Loads preprocessed data from disk
    
    Returns:
        pd.DataFrame: Preprocessed data
    """
    
    
    print(f"\n Loading processed data from {PROCESSED_DATA_FILE}...")
    
    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(
            f"Processed data not found at {PROCESSED_DATA_FILE}. "
            "Run preprocessing first!"
        )
    
    df = pd.read_csv(PROCESSED_DATA_FILE, parse_dates=['datetime'])
    print(f"   Loaded {len(df):,} rows")
    
    return df


if __name__ == "__main__":
   
    """
    Run the complete preprocessing pipeline
    """

    print(" Starting data preprocessing...\n")
    
    # Load raw data (use full dataset or subset with nrows parameter)
    print(" Step 1: Load raw data")
    df_raw = load_raw_data(nrows=None)  # Load all data
    
    # Preprocess
    print("\n Step 2: Preprocess data")
    df_processed = preprocess_pipeline(df_raw)
    
    # Save
    print("\n Step 3: Save processed data")
    save_processed_data(df_processed)
    
    print("\n Preprocessing complete! Ready for feature engineering.")
