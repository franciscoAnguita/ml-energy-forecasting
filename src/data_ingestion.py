"""
Data Ingestion Module
Downloads and loads the Household Power Consumption dataset
"""

import pandas as pd
import urllib.request
import zipfile
import os
from pathlib import Path
from src.config import (
    DATASET_URL,
    RAW_DATA_DIR,
    RAW_DATA_FILE
)


def download_dataset():
    """
    Downloads the Household Power Consumption dataset from UCI repository
    
    Returns:
        Path: Path to the downloaded file
    """
    print("Downloading dataset from UCI repository...")
    
    # Create raw data directory if it doesn't exist
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download zip file
    zip_path = RAW_DATA_DIR / "household_power_consumption.zip"
    
    if RAW_DATA_FILE.exists():
        print(f"Dataset already exists at {RAW_DATA_FILE}")
        return RAW_DATA_FILE
    
    try:
        urllib.request.urlretrieve(DATASET_URL, zip_path)
        print(f"Downloaded to {zip_path}")
        
        # Extract zip file
        print("Extracting zip file...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DATA_DIR)
        
        # Remove zip file to save space
        os.remove(zip_path)
        print(f"Extracted to {RAW_DATA_DIR}")
        
        return RAW_DATA_FILE
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        raise


def load_raw_data(nrows=None):
    """
    Loads the raw energy consumption data
    
    Args:
        nrows (int, optional): Number of rows to load. None loads all data.
        
    Returns:
        pd.DataFrame: Raw energy consumption data
    """
    print(f"Loading raw data from {RAW_DATA_FILE}...")
    
    if not RAW_DATA_FILE.exists():
        print("Raw data file not found. Downloading...")
        download_dataset()
    
    try:
        # Load data with semicolon separator
        df = pd.read_csv(
            RAW_DATA_FILE,
            sep=";",
            low_memory=False,
            nrows=nrows
        )
        
        # Combine Date and Time into datetime column
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M:%S')
        df = df.drop(['Date', 'Time'], axis=1)
        
        # Reorder columns to have datetime first
        cols = ['datetime'] + [col for col in df.columns if col != 'datetime']
        df = df[cols]
        
        print(f"Loaded {len(df):,} rows and {len(df.columns)} columns")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nData types:\n{df.dtypes}")
        print(f"\nFirst few rows:\n{df.head()}")
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        raise


def get_data_info(df):
    """
    Prints detailed information about the dataset
    
    Args:
        df (pd.DataFrame): The dataframe to analyze
    """
    print("\n" + "="*70)
    print("DATASET INFORMATION")
    print("="*70)
    
    print(f"\n Shape: {df.shape[0]:,} rows {df.shape[1]} columns")
    print(f" Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\n Date range:")
    if 'datetime' in df.columns:
        print(f"   Start: {df['datetime'].min()}")
        print(f"   End: {df['datetime'].max()}")
        print(f"   Duration: {df['datetime'].max() - df['datetime'].min()}")
    
    print(f"\n Missing values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        missing_pct = (missing / len(df) * 100).round(2)
        missing_df = pd.DataFrame({
            'Missing': missing,
            'Percentage': missing_pct
        })
        print(missing_df[missing_df['Missing'] > 0])
    else:
        print("   No missing values!")
    
    print(f"\n Numeric columns summary:")
    print(df.describe())


if __name__ == "__main__":
    """
    Example usage: Run this script directly to test data ingestion
    """
    print(" Starting data ingestion pipeline...\n")
    
    # Download and load data (load first 100k rows for testing)
    # Remove nrows parameter to load full dataset
    df = load_raw_data(nrows=100000)
    
    # Display dataset information
    get_data_info(df)
    
    print("\n Data ingestion complete!")
