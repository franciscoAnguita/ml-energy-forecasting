
"""
Feature Engineering Module
Creates time-based features and derives new variables from existing data
"""

import pandas as pd
import numpy as np
from src.config import (
    PROCESSED_DATA_FILE,
    TIME_FEATURES,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)
from src.data_preprocessing import load_processed_data


def extract_time_features(df):
   
    """
    Extracts time-based features from datetime column
    
    Time features help the model learn temporal patterns:
    - Hour: Energy usage varies by time of day
    - Day of week: Weekday vs weekend patterns
    - Month: Seasonal patterns
    - Is weekend: Binary indicator for weekend days
    
    Args:
        df (pd.DataFrame): Dataframe with 'datetime' column
        
    Returns:
        pd.DataFrame: Dataframe with additional time feature columns
    """
   
   
    print("\n Extracting time-based features...")
    
    # Ensure datetime is in datetime format
    if not pd.api.types.is_datetime64_any_dtype(df['datetime']):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Extract hour (0-23)
    df['hour'] = df['datetime'].dt.hour
    
    # Extract day of week (0=Monday, 6=Sunday)
    df['day_of_week'] = df['datetime'].dt.dayofweek
    
    # Extract month (1-12)
    df['month'] = df['datetime'].dt.month
    
    # Create binary weekend indicator (1=weekend, 0=weekday)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    print(f"    Created features: {TIME_FEATURES}")
    print(f"\n    Feature value ranges:")
    print(f"      - Hour: {df['hour'].min()}-{df['hour'].max()}")
    print(f"      - Day of week: {df['day_of_week'].min()}-{df['day_of_week'].max()}")
    print(f"      - Month: {df['month'].min()}-{df['month'].max()}")
    print(f"      - Is weekend: {df['is_weekend'].unique()}")
    
    return df


def create_lag_features(df, target_col, lags=[1, 2, 3, 6, 12, 24]):
    
    """
    Creates lag features (previous values) for time series prediction
    
    Lag features capture recent history:
    - lag_1: Value from 1 hour ago
    - lag_24: Value from 24 hours ago (same time yesterday)
    
    Args:
        df (pd.DataFrame): Input dataframe
        target_col (str): Column to create lags for
        lags (list): List of lag periods (in hours)
        
    Returns:
        pd.DataFrame: Dataframe with lag features (NaNs NOT dropped yet)
    """
    
    
    print(f"\n Creating lag features for '{target_col}'...")
    
    for lag in lags:
        col_name = f'{target_col}_lag_{lag}'
        df[col_name] = df[target_col].shift(lag)
        print(f"    Created: {col_name}")
    
    print(f"     Created {len(lags)} lag features (will clean NaN later)")
    
    return df



def create_rolling_features(df, target_col, windows=[3, 6, 12, 24]):
    
    """
    Creates rolling statistics (moving averages, std)
    
    Rolling features capture trends:
    - rolling_mean_3: Average of last 3 hours
    - rolling_std_24: Standard deviation of last 24 hours
    
    Args:
        df (pd.DataFrame): Input dataframe
        target_col (str): Column to calculate rolling stats for
        windows (list): Window sizes (in hours)
        
    Returns:
        pd.DataFrame: Dataframe with rolling features (NaNs NOT dropped yet)
    """
    
    
    print(f"\n Creating rolling statistics for '{target_col}'...")
    
    for window in windows:
        # Rolling mean
        mean_col = f'{target_col}_rolling_mean_{window}'
        df[mean_col] = df[target_col].rolling(window=window).mean()
        print(f"    Created: {mean_col}")
        
        # Rolling standard deviation
        std_col = f'{target_col}_rolling_std_{window}'
        df[std_col] = df[target_col].rolling(window=window).std()
        print(f"    Created: {std_col}")
    
    print(f"   ℹ️  Created {len(windows)*2} rolling features (will clean NaN later)")
    
    return df



def create_interaction_features(df):
    
    """
    Creates interaction features (combinations of existing features)
    
    Interactions capture combined effects:
    - hour * is_weekend: Weekend nights behave differently
    - voltage * global_intensity: Power calculation relationship
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        pd.DataFrame: Dataframe with interaction features
    """
    
    
    print("\n🔗 Creating interaction features...")
    
    # Hour and weekend interaction
    if 'hour' in df.columns and 'is_weekend' in df.columns:
        df['hour_weekend_interaction'] = df['hour'] * df['is_weekend']
        print("   Created: hour_weekend_interaction")
    
    # Voltage and intensity interaction (approximates power)
    if 'Voltage' in df.columns and 'Global_intensity' in df.columns:
        df['voltage_intensity_product'] = df['Voltage'] * df['Global_intensity']
        print("   Created: voltage_intensity_product")
    
    # Total sub-metering (sum of all sub-meters)
    sub_meter_cols = ['Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
    if all(col in df.columns for col in sub_meter_cols):
        df['total_sub_metering'] = df[sub_meter_cols].sum(axis=1)
        print("   Created: total_sub_metering")
    
    return df


def feature_engineering_pipeline(df, include_advanced=False):
   
    """
    Complete feature engineering pipeline
    
    Args:
        df (pd.DataFrame): Preprocessed data
        include_advanced (bool): Whether to include lag and rolling features
                                 (These are powerful but increase complexity)
        
    Returns:
        pd.DataFrame: Data with all engineered features
    """
    
    
    print("\n" + "="*70)
    print("🔧 STARTING FEATURE ENGINEERING PIPELINE")
    print("="*70)
    
    df = df.copy()
    initial_rows = len(df)
    
    # Step 1: Time-based features (always include)
    df = extract_time_features(df)
    
    # Step 2: Interaction features (always include)
    df = create_interaction_features(df)
    
    # Step 3: Advanced features (optional - can make model more complex)
    if include_advanced:
        print("\n Including advanced time-series features...")
        df = create_lag_features(df, TARGET_COLUMN, lags=[1, 24])
        df = create_rolling_features(df, TARGET_COLUMN, windows=[3, 24])
    else:
        print("\n  Skipping advanced features (lag/rolling) for simpler model")
    
    # Step 4: Drop NaN values intelligently
    print("\n Cleaning NaN values created during feature engineering...")
    rows_before_clean = len(df)
    
    if include_advanced:
        # Only drop rows where lag/rolling features have NaN
        lag_cols = [col for col in df.columns if 'lag' in col or 'rolling' in col]
        print(f"   Checking NaN only in advanced features: {lag_cols}")
        df = df.dropna(subset=lag_cols)
    else:
        # Drop any rows with NaN (basic features rarely have them)
        df = df.dropna()
    
    rows_after_clean = len(df)
    rows_lost = rows_before_clean - rows_after_clean
    
    print(f"   Dropped {rows_lost} rows with NaN ({rows_after_clean}/{initial_rows} remaining)")
    print(f"   Data retention: {rows_after_clean/initial_rows*100:.1f}%")
    
    print("\n" + "="*70)
    print(" FEATURE ENGINEERING COMPLETE")
    print("="*70)
    print(f" Final shape: {df.shape}")
    print(f" Total features: {len(df.columns)}")
    print(f"\n All columns:\n{list(df.columns)}")
    print(f"\n Sample data:\n{df.head()}")
    
    return df


def get_feature_importance_preview(df):
    """
    Shows correlation of features with target (quick preview)
    
    Args:
        df (pd.DataFrame): Dataframe with features and target
    """
    
    print("\n" + "="*70)
    print(" FEATURE CORRELATION WITH TARGET")
    print("="*70)
    
    if TARGET_COLUMN not in df.columns:
        print("⚠️  Target column not found, skipping correlation analysis")
        return
    
    # Calculate correlations
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlations = df[numeric_cols].corrwith(df[TARGET_COLUMN]).abs().sort_values(ascending=False)
    
    print("\nTop 10 features by correlation with target:")
    print(correlations.head(10))
    
    print("\n Interpretation:")
    print("   - Values close to 1.0: Strong relationship")
    print("   - Values close to 0.0: Weak relationship")


def save_engineered_data(df, filename="engineered_data.csv"):
   
    """
    Saves data with engineered features
    
    Args:
        df (pd.DataFrame): Dataframe with features
        filename (str): Output filename
    """
    
    from src.config import PROCESSED_DATA_DIR
    
    output_path = PROCESSED_DATA_DIR / filename
    print(f"\n Saving engineered data to {output_path}...")
    
    df.to_csv(output_path, index=False)
    print(f"   Saved! {len(df)} rows, {len(df.columns)} columns")


if __name__ == "__main__":
    """
    Run feature engineering pipeline
    """
    print("🚀 Starting feature engineering...\n")
    
    # Load preprocessed data
    print(" Step 1: Load preprocessed data")
    df = load_processed_data()
    
    # Run feature engineering
    print("\n Step 2: Engineer features")
    df_features = feature_engineering_pipeline(df, include_advanced=False)
    
    # Preview feature importance
    print("\n Step 3: Analyze feature correlations")
    get_feature_importance_preview(df_features)
    
    # Save
    print("\n Step 4: Save engineered data")
    save_engineered_data(df_features)
    
    print("\n Feature engineering complete! Ready for model training.")
