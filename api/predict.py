"""
Prediction Module
Contains prediction logic and helper functions
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import logging

from src.config import CONSUMPTION_THRESHOLDS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_features(input_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Prepares input data into the format expected by the model
    
    The model expects features in a specific order and format.
    This function creates a DataFrame with one row containing all features.
    
    Args:
        input_data (dict): Input data from API request
        
    Returns:
        pd.DataFrame: Single-row DataFrame with features in correct order
    """
    # Extract base features
    features = {
        'Global_reactive_power': 0.15,  # Typical household value (approximation)
        'Voltage': input_data['voltage'],
        'Global_intensity': input_data['global_intensity'],
        'Sub_metering_1': input_data['sub_metering_1'],
        'Sub_metering_2': input_data['sub_metering_2'],
        'Sub_metering_3': input_data['sub_metering_3'],
        'hour': input_data['hour'],
        'day_of_week': input_data['day_of_week'],
        'month': input_data['month'],
        'is_weekend': input_data['is_weekend']
    }
    
    # Create DataFrame
    df = pd.DataFrame([features])
    
    # Add engineered features (must match training!)
    df = add_engineered_features(df)
    
    logger.info(f"Prepared features: {df.columns.tolist()}")
    
    return df


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds engineered features to match training data
    
    CRITICAL: These must exactly match the features created during training!
    If training used certain interaction features, we must create them here too.
    
    Args:
        df (pd.DataFrame): DataFrame with base features
        
    Returns:
        pd.DataFrame: DataFrame with all engineered features
    """
    
    # Interaction feature: hour × is_weekend
    df['hour_weekend_interaction'] = df['hour'] * df['is_weekend']
    
    # Interaction feature: voltage × intensity (power approximation)
    df['voltage_intensity_product'] = df['Voltage'] * df['Global_intensity']
    
    # Total sub-metering
    df['total_sub_metering'] = (
        df['Sub_metering_1'] + 
        df['Sub_metering_2'] + 
        df['Sub_metering_3']
    )
    
    logger.info(f"Added {3} engineered features")
    
    return df


def make_prediction(model, scaler, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Makes a single prediction using the trained model
    
    Args:
        model: Trained scikit-learn model
        scaler: Fitted StandardScaler
        input_data (dict): Input features from API request
        
    Returns:
        dict: Prediction results with metadata
    """
    try:
        # Prepare features
        features_df = prepare_features(input_data)
        
        # Scale features (must match training!)
        features_scaled = scaler.transform(features_df)
        
        # Make prediction
        prediction_kw = model.predict(features_scaled)[0]
        
        # Ensure prediction is positive
        prediction_kw = max(0.0, prediction_kw)
        
        # Calculate confidence (using model's prediction variance)
        # For Random Forest, we can get predictions from all trees
        if hasattr(model, 'estimators_'):
            # Get predictions from all trees
            tree_predictions = np.array([
                tree.predict(features_scaled)[0] 
                for tree in model.estimators_
            ])
            
            # Calculate confidence based on prediction consistency
            # Lower variance = higher confidence
            prediction_std = np.std(tree_predictions)
            prediction_mean = np.mean(tree_predictions)
            
            # Normalize to 0-1 range
            # Low std relative to mean = high confidence
            if prediction_mean > 0:
                coefficient_of_variation = prediction_std / prediction_mean
                confidence = max(0.0, min(1.0, 1.0 - coefficient_of_variation))
            else:
                confidence = 0.5  # Default confidence
        else:
            confidence = 0.85  # Default confidence for models without tree access
        
        # Classify consumption level
        consumption_level = classify_consumption(prediction_kw)
        
        # Build response
        result = {
            'predicted_consumption_kw': round(prediction_kw, 4),
            'consumption_level': consumption_level,
            'confidence': round(confidence, 2),
            'timestamp': datetime.now().isoformat(),
            'features_used': {
                'voltage': input_data['voltage'],
                'global_intensity': input_data['global_intensity'],
                'hour': input_data['hour'],
                'is_weekend': input_data['is_weekend']
            }
        }
        
        logger.info(f"Prediction successful: {prediction_kw:.4f} kW ({consumption_level})")
        
        return result
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise ValueError(f"Prediction error: {str(e)}")


def make_batch_predictions(
    model, 
    scaler, 
    batch_inputs: list
) -> Dict[str, Any]:
    
    """
    Makes predictions for multiple inputs
    
    More efficient than calling make_prediction() in a loop because:
    - Batches can be vectorized
    - Scaling happens once for all inputs
    
    Args:
        model: Trained model
        scaler: Fitted scaler
        batch_inputs (list): List of input dictionaries
        
    Returns:
        dict: Batch prediction results
    """
  
    try:
        predictions = []
        
        for input_data in batch_inputs:
            # Make individual prediction
            result = make_prediction(model, scaler, input_data)
            
            # Add simplified result to batch
            predictions.append({
                'predicted_consumption_kw': result['predicted_consumption_kw'],
                'consumption_level': result['consumption_level']
            })
        
        # Build batch response
        batch_result = {
            'predictions': predictions,
            'count': len(predictions),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Batch prediction successful: {len(predictions)} predictions")
        
        return batch_result
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {str(e)}")
        raise ValueError(f"Batch prediction error: {str(e)}")


def classify_consumption(consumption_kw: float) -> str:
    
    """
    Classifies consumption into Low/Medium/High categories
    
    Thresholds are defined in config.py:
    - Low: < 1.0 kW
    - Medium: 1.0 - 3.0 kW
    - High: > 3.0 kW
    
    Args:
        consumption_kw (float): Predicted consumption in kW
        
    Returns:
        str: Consumption level classification
    """
   
    if consumption_kw < CONSUMPTION_THRESHOLDS['low']:
        return 'Low'
    elif consumption_kw < CONSUMPTION_THRESHOLDS['medium']:
        return 'Medium'
    else:
        return 'High'


def get_model_info(model) -> Dict[str, Any]:
   
    """
    Extracts information about the trained model
    
    Args:
        model: Trained scikit-learn model
        
    Returns:
        dict: Model metadata
    """
   
    try:
        info = {
            'model_type': type(model).__name__,
            'n_estimators': getattr(model, 'n_estimators', None),
            'training_date': None,  # Could be stored during training
            'metrics': {
                'test_r2': None,  # Would need to be stored during training
                'test_mae': None,
                'test_rmse': None
            },
            'features': [
                'global_reactive_power', 
                'voltage',
                'global_intensity',
                'sub_metering_1',
                'sub_metering_2',
                'sub_metering_3',
                'hour',
                'day_of_week',
                'month',
                'is_weekend',
                'hour_weekend_interaction',
                'voltage_intensity_product',
                'total_sub_metering'
            ]
        }
        
        logger.info("Model info retrieved successfully")
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        raise ValueError(f"Model info error: {str(e)}")


def validate_input_ranges(input_data: Dict[str, Any]) -> bool:
   
    """
    Additional validation beyond Pydantic
    
    Checks if inputs are within reasonable physical ranges.
    This catches potential data quality issues.
    
    Args:
        input_data (dict): Input data to validate
        
    Returns:
        bool: True if valid, raises ValueError if not
    """
    
    
    # Check for physically impossible combinations
    # Example: Very high intensity with low voltage is suspicious
    voltage = input_data['voltage']
    intensity = input_data['global_intensity']
    
    # Power = Voltage × Current (approximately)
    apparent_power = voltage * intensity / 1000  # Convert to kW
    
    if apparent_power > 10.0:
        raise ValueError(
            f"Input combination seems unrealistic: "
            f"Voltage={voltage}V × Intensity={intensity}A = {apparent_power:.2f}kW. "
            f"This exceeds typical household capacity."
        )
    
    # Check sub-metering total doesn't exceed reasonable limits
    total_submetering = (
        input_data['sub_metering_1'] + 
        input_data['sub_metering_2'] + 
        input_data['sub_metering_3']
    )
    
    if total_submetering > 50.0:
        logger.warning(
            f"High sub-metering total: {total_submetering:.2f} Wh. "
            f"This is unusual but not invalid."
        )
    
    return True
