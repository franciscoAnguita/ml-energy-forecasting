"""
Sample Dataset Generator
Creates a synthetic energy consumption dataset that mimics the UCI dataset structure
Use this when the real dataset cannot be downloaded
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from src.config import RAW_DATA_DIR, RAW_DATA_FILE


def generate_sample_dataset(n_days=365, samples_per_day=1440):
   
    """
    Generates a synthetic energy consumption dataset
    
    Args:
        n_days (int): Number of days of data to generate
        samples_per_day (int): Measurements per day (default 1440 = 1 per minute)
        
    Returns:
        pd.DataFrame: Synthetic energy consumption data
    """
   
   
    print(f"Generating synthetic dataset: {n_days} days, {samples_per_day} samples/day...")
    
    # Total number of samples
    n_samples = n_days * samples_per_day
    
    # Generate datetime range (1-minute intervals)
    start_date = datetime(2006, 12, 16, 17, 24, 0)
    dates = [start_date + timedelta(minutes=i) for i in range(n_samples)]
    
    # Extract time features for realistic patterns
    hours = np.array([d.hour for d in dates])
    days_of_week = np.array([d.weekday() for d in dates])
    
    # Base consumption patterns
    # Higher during day (7am-11pm), lower at night
    hourly_pattern = np.where(
        (hours >= 7) & (hours <= 23),
        1.0 + 0.5 * np.sin((hours - 7) * np.pi / 16),  # Day pattern
        0.3 + 0.1 * np.sin(hours * np.pi / 12)  # Night pattern
    )
    
    # Weekend vs weekday pattern
    weekend_factor = np.where(days_of_week >= 5, 1.2, 1.0)  # Higher on weekends
    
    # Seasonal pattern (simplified)
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonal_pattern = 1.0 + 0.3 * np.sin((day_of_year - 80) * 2 * np.pi / 365)
    
    # Global Active Power (kW) - main target variable
    base_power = 1.5
    global_active_power = (
        base_power * hourly_pattern * weekend_factor * seasonal_pattern +
        np.random.normal(0, 0.3, n_samples)  # Add noise
    )
    global_active_power = np.maximum(global_active_power, 0.1)  # Ensure positive
    
    # Global Reactive Power (kW)
    global_reactive_power = global_active_power * 0.1 + np.random.normal(0, 0.02, n_samples)
    global_reactive_power = np.maximum(global_reactive_power, 0)
    
    # Voltage (V) - typically around 240V
    voltage = 240 + np.random.normal(0, 3, n_samples)
    
    # Global Intensity (A) - Power / Voltage
    global_intensity = (global_active_power * 1000 / voltage) + np.random.normal(0, 0.2, n_samples)
    global_intensity = np.maximum(global_intensity, 0)
    
    # Sub-metering (three different circuits in the house)
    # Kitchen (higher during meal times)
    meal_times = ((hours >= 7) & (hours <= 9)) | ((hours >= 12) & (hours <= 14)) | ((hours >= 18) & (hours <= 21))
    sub_metering_1 = np.where(meal_times, 
                               global_active_power * 0.3 + np.random.normal(0, 0.5, n_samples),
                               global_active_power * 0.1 + np.random.normal(0, 0.2, n_samples))
    sub_metering_1 = np.maximum(sub_metering_1, 0)
    
    # Laundry (random peaks)
    laundry_events = np.random.random(n_samples) < 0.05  # 5% chance of laundry
    sub_metering_2 = np.where(laundry_events,
                               global_active_power * 0.4 + np.random.normal(0, 0.3, n_samples),
                               global_active_power * 0.05 + np.random.normal(0, 0.1, n_samples))
    sub_metering_2 = np.maximum(sub_metering_2, 0)
    
    # Climate control (AC/heating) - higher in summer/winter
    climate_load = np.where((day_of_year < 80) | (day_of_year > 280), 1.5,  # Winter
                            np.where((day_of_year > 150) & (day_of_year < 240), 1.3, 0.8))  # Summer
    sub_metering_3 = global_active_power * 0.25 * climate_load + np.random.normal(0, 0.3, n_samples)
    sub_metering_3 = np.maximum(sub_metering_3, 0)
    
    # Create DataFrame
    df = pd.DataFrame({
        'datetime': dates,
        'Global_active_power': global_active_power.round(3),
        'Global_reactive_power': global_reactive_power.round(3),
        'Voltage': voltage.round(2),
        'Global_intensity': global_intensity.round(1),
        'Sub_metering_1': sub_metering_1.round(1),
        'Sub_metering_2': sub_metering_2.round(1),
        'Sub_metering_3': sub_metering_3.round(1)
    })
    
    # Add some missing values (like real data)
    missing_mask = np.random.random(n_samples) < 0.01  # 1% missing
    for col in df.columns[1:]:  # Skip datetime
        df.loc[missing_mask, col] = np.nan
    
    print(f"✅ Generated {len(df):,} samples")
    print(f"📊 Columns: {list(df.columns)}")
    print(f"📅 Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    
    return df


def save_sample_dataset(df, file_path=None):
    """
    Saves the sample dataset to disk
    
    Args:
        df (pd.DataFrame): The dataset to save
        file_path (Path, optional): Where to save. Defaults to RAW_DATA_FILE.
    """
    if file_path is None:
        file_path = RAW_DATA_FILE
    
    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV with semicolon separator (to match UCI format)
    # Split datetime back into Date and Time for compatibility
    df_save = df.copy()
    df_save['Date'] = df_save['datetime'].dt.strftime('%d/%m/%Y')
    df_save['Time'] = df_save['datetime'].dt.strftime('%H:%M:%S')
    df_save = df_save.drop('datetime', axis=1)
    
    # Reorder columns to match UCI format
    cols = ['Date', 'Time', 'Global_active_power', 'Global_reactive_power', 
            'Voltage', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']
    df_save = df_save[cols]
    
    # Save with semicolon separator
    df_save.to_csv(file_path, sep=';', index=False)
    
    print(f"💾 Saved dataset to: {file_path}")
    print(f"📦 File size: {file_path.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    """
    Generate and save a sample dataset
    """
    print("🚀 Generating sample energy consumption dataset...\n")
    
    # Generate 1 year of data (can adjust for more/less)
    df = generate_sample_dataset(n_days=365, samples_per_day=1440)
    
    # Save to raw data directory
    save_sample_dataset(df)
    
    print("\n✅ Sample dataset generation complete!")
    print(f"\n📋 Sample data preview:\n{df.head(10)}")
    print(f"\n📊 Summary statistics:\n{df.describe()}")
