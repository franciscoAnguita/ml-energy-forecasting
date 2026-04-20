"""
Model Training Module
Trains Random Forest model and evaluates performance
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import (
    MODEL_PATH,
    SCALER_PATH,
    TARGET_COLUMN,
    FEATURE_COLUMNS,
    MODEL_PARAMS,
    TEST_SIZE,
    RANDOM_STATE,
    MODELS_DIR
)
from src.feature_engineering import (
    feature_engineering_pipeline,
    load_processed_data
)


def prepare_features_and_target(df):
    
    """
    Separates features (X) and target (y) from dataframe
    
    Args:
        df (pd.DataFrame): Dataframe with features and target
        
    Returns:
        tuple: (X, y) where X is features dataframe, y is target series
    """
    
    
    print("\n Preparing features and target...")
    
    # Separate target from features
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataframe")
    
    y = df[TARGET_COLUMN]
    
    # Remove target and non-feature columns from X
    exclude_cols = [TARGET_COLUMN, 'datetime']
    X = df.drop(columns=[col for col in exclude_cols if col in df.columns])
    
    print(f"   Features (X): {X.shape[1]} columns, {X.shape[0]} rows")
    print(f"   Target (y): {y.shape[0]} values")
    print(f"\n   Feature columns:\n{list(X.columns)}")
    
    return X, y


def split_train_test(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE):
   
    """
    Splits data into training and testing sets
    
    For time-series, we could use time-based split instead of random split.
    Here we use random split for simplicity, but time-based is more realistic.
    
    Args:
        X (pd.DataFrame): Features
        y (pd.Series): Target
        test_size (float): Proportion of data for testing (0.2 = 20%)
        random_state (int): Random seed for reproducibility
        
    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
   
   
    print(f"\n  Splitting data (test_size={test_size})...") 
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state,
        shuffle=True  # For time-series, consider shuffle=False
    )
    
    print(f"   Training set: {len(X_train)} samples ({len(X_train)/(len(X_train)+len(X_test))*100:.1f}%)")
    print(f"   Test set: {len(X_test)} samples ({len(X_test)/(len(X_train)+len(X_test))*100:.1f}%)")
    
    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    
    """
    Scales features using StandardScaler
    
    Note: Random Forest doesn't require scaling, but we do it anyway to:
    1. Show best practices (essential for other models)
    2. Make features interpretable
    3. Prepare for potential model comparison later
    
    Args:
        X_train (pd.DataFrame): Training features
        X_test (pd.DataFrame): Test features
        
    Returns:
        tuple: (X_train_scaled, X_test_scaled, scaler)
    """
    
    
    print("\n Scaling features...")
    
    scaler = StandardScaler()
    
    # Fit on training data only!
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Transform test data using training statistics
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame to keep column names
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
    
    print(f"    Scaled {X_train_scaled.shape[1]} features")
    print(f"    Training data: mean ≈ 0, std ≈ 1")
    
    return X_train_scaled, X_test_scaled, scaler



def train_model(X_train, y_train, model_params=MODEL_PARAMS):
   
    """
    Trains Random Forest Regressor model
    
    Random Forest is chosen because:
    - Handles non-linear relationships
    - Resistant to overfitting
    - Provides feature importance
    - Works well with mixed feature types
    - No need for extensive hyperparameter tuning
    
    Args:
        X_train (pd.DataFrame): Training features
        y_train (pd.Series): Training target
        model_params (dict): Model hyperparameters
        
    Returns:
        RandomForestRegressor: Trained model
    """
    
    
    print("\n Training Random Forest model...")
    print(f"   Model parameters: {model_params}")
    
    model = RandomForestRegressor(**model_params)
    
    # Train the model
    model.fit(X_train, y_train)
    
    print(f"   Model trained successfully!")
    print(f"   Number of trees: {model.n_estimators}")
    print(f"   Max depth: {model.max_depth}")
    
    return model



def evaluate_model(model, X_train, X_test, y_train, y_test):
    
    """
    Evaluates model performance on both training and test sets
    
    Metrics explained:
    - MAE (Mean Absolute Error): Average prediction error in kW
    - RMSE (Root Mean Squared Error): Penalizes large errors more
    - R² Score: Proportion of variance explained (1.0 = perfect, 0.0 = useless)
    - MAPE (Mean Absolute Percentage Error): Error as percentage
    
    Args:
        model: Trained model
        X_train, X_test: Feature sets
        y_train, y_test: Target sets
        
    Returns:
        dict: Dictionary of metrics
    """
    
    
    print("\n Evaluating model performance...")
    
    # Make predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculate metrics for training set
    train_mae = mean_absolute_error(y_train, y_train_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    train_r2 = r2_score(y_train, y_train_pred)
    train_mape = np.mean(np.abs((y_train - y_train_pred) / y_train)) * 100
    
    # Calculate metrics for test set
    test_mae = mean_absolute_error(y_test, y_test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_r2 = r2_score(y_test, y_test_pred)
    test_mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100
    
    # Print results
    print("\n" + "="*70)
    print(" MODEL PERFORMANCE METRICS")
    print("="*70)

    """
    MAE (Mean Absolute Error): Average absolute difference between predictions and actual values (how wrong you are on average).
    RMSE (Root Mean Squared Error): Square-root of average squared errors, giving more weight to large mistakes.
    R² (Coefficient of Determination): Proportion of variance in the target explained by the model (1 = perfect, 0 = no better than mean).
    MAPE (Mean Absolute Percentage Error): Average absolute error expressed as a percentage of actual values.

    For the overfitting check:
    R² difference (train vs test): Gap in performance between training and test sets, used as a proxy for overfitting (larger gap = worse generalization).    
    """
    
    print("\n TRAINING SET:")
    print(f"   MAE:   {train_mae:.4f} kW   (average error)")
    print(f"   RMSE:  {train_rmse:.4f} kW   (penalizes large errors)")
    print(f"   R²:    {train_r2:.4f}       (variance explained, 1.0 = perfect)")
    print(f"   MAPE:  {train_mape:.2f}%      (percentage error)")
    
    print("\n TEST SET:")
    print(f"   MAE:   {test_mae:.4f} kW")
    print(f"   RMSE:  {test_rmse:.4f} kW")
    print(f"   R²:    {test_r2:.4f}")
    print(f"   MAPE:  {test_mape:.2f}%")
    
    # Check for overfitting
    print("\n OVERFITTING CHECK:")
    r2_diff = train_r2 - test_r2
    if r2_diff < 0.05:
        print(f"    Minimal overfitting (R² diff: {r2_diff:.4f})")
    elif r2_diff < 0.15:
        print(f"    Slight overfitting (R² diff: {r2_diff:.4f})")
    else:
        print(f"    Significant overfitting (R² diff: {r2_diff:.4f})")
    
    # Store metrics
    metrics = {
        'train_mae': train_mae,
        'train_rmse': train_rmse,
        'train_r2': train_r2,
        'train_mape': train_mape,
        'test_mae': test_mae,
        'test_rmse': test_rmse,
        'test_r2': test_r2,
        'test_mape': test_mape,
        'y_test': y_test,
        'y_test_pred': y_test_pred
    }
    
    return metrics


def analyze_feature_importance(model, feature_names, top_n=10):
    
    """
    Analyzes and displays feature importance from the trained model
    
    Shows which features contribute most to predictions.
    This is valuable for:
    - Understanding model behavior
    - Feature selection
    - Explaining to stakeholders
    
    Args:
        model: Trained Random Forest model
        feature_names (list): List of feature names
        top_n (int): Number of top features to display
    """
    
    
    print("\n" + "="*70)
    print("🔍 FEATURE IMPORTANCE ANALYSIS")
    print("="*70)
    
    # Get feature importances
    importances = model.feature_importances_
    
    # Create dataframe for easy sorting
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"\n Top {top_n} Most Important Features:")
    print(feature_importance_df.head(top_n).to_string(index=False))
    
    print(f"\n Interpretation:")
    print(f"   - Values sum to 1.0")
    print(f"   - Higher values = more important for predictions")
    print(f"   - Features with importance < 0.01 are less useful")
    
    return feature_importance_df



def save_model_and_scaler(model, scaler):
    
    """
    Saves trained model and scaler to disk
    
    Args:
        model: Trained model
        scaler: Fitted scaler
    """
    
    
    print("\n Saving model and scaler...")
    
    # Ensure models directory exists
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"   Model saved to: {MODEL_PATH}")
    
    # Save scaler
    joblib.dump(scaler, SCALER_PATH)
    print(f"   Scaler saved to: {SCALER_PATH}")
    
    # Print file sizes
    model_size = MODEL_PATH.stat().st_size / (1024 * 1024)
    scaler_size = SCALER_PATH.stat().st_size / 1024
    print(f"\n    Model size: {model_size:.2f} MB")
    print(f"    Scaler size: {scaler_size:.2f} KB")



def load_model_and_scaler():
    """
    Loads trained model and scaler from disk
    
    Returns:
        tuple: (model, scaler)
    """
   
   
    print("\n Loading model and scaler...")
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
    
    if not SCALER_PATH.exists():
        raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
    
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    print(f"   ✅ Model loaded from: {MODEL_PATH}")
    print(f"   ✅ Scaler loaded from: {SCALER_PATH}")
    
    return model, scaler



def plot_predictions_vs_actual(y_test, y_pred, save_path=None):
    """
    Creates scatter plot of predictions vs actual values
    
    Good predictions should fall on the diagonal line (y=x)
    
    Args:
        y_test: Actual values
        y_pred: Predicted values
        save_path: Where to save plot (optional)
    """
    plt.figure(figsize=(10, 6))
    
    # Scatter plot
    plt.scatter(y_test, y_pred, alpha=0.5, s=10)
    
    # Perfect prediction line (y=x)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    
    plt.xlabel('Actual Energy Consumption (kW)', fontsize=12)
    plt.ylabel('Predicted Energy Consumption (kW)', fontsize=12)
    plt.title('Predictions vs Actual Values', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"    Plot saved to: {save_path}")
    
    plt.close()


def complete_training_pipeline(include_advanced_features=False):
    """
    Complete end-to-end training pipeline
    
    Args:
        include_advanced_features (bool): Whether to use lag/rolling features
        
    Returns:
        tuple: (model, scaler, metrics)
    """
    print("\n" + "="*70)
    print(" STARTING COMPLETE TRAINING PIPELINE")
    print("="*70)
    
    # Step 1: Load and engineer features
    print("\n STEP 1: Load preprocessed data")
    df_processed = load_processed_data()
    
    print("\n STEP 2: Feature engineering")
    df_features = feature_engineering_pipeline(df_processed, include_advanced=include_advanced_features)
    
    # Step 2: Prepare X and y
    print("\n STEP 3: Prepare features and target")
    X, y = prepare_features_and_target(df_features)
    
    # Step 3: Split data
    print("\n STEP 4: Split into train/test sets")
    X_train, X_test, y_train, y_test = split_train_test(X, y)
    
    # Step 4: Scale features
    print("\n STEP 5: Scale features")
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    
    # Step 5: Train model
    print("\n STEP 6: Train Random Forest model")
    model = train_model(X_train_scaled, y_train)
    
    # Step 6: Evaluate
    print("\n STEP 7: Evaluate model")
    metrics = evaluate_model(model, X_train_scaled, X_test_scaled, y_train, y_test)
    
    # Step 7: Feature importance
    print("\n STEP 8: Analyze feature importance")
    feature_importance = analyze_feature_importance(model, X_train.columns)
    
    # Step 8: Save
    print("\n STEP 9: Save model and scaler")
    save_model_and_scaler(model, scaler)
    
    # Step 9: Visualize (optional)
    print("\n STEP 10: Generate visualizations")
    plot_path = MODELS_DIR / "predictions_vs_actual.png"
    plot_predictions_vs_actual(metrics['y_test'], metrics['y_test_pred'], save_path=plot_path)
    
    print("\n" + "="*70)
    print(" TRAINING PIPELINE COMPLETE!")
    print("="*70)
    print(f"\n Final Test R² Score: {metrics['test_r2']:.4f}")
    print(f" Final Test MAE: {metrics['test_mae']:.4f} kW")
    print(f"\n Model ready for deployment!")
    
    return model, scaler, metrics




if __name__ == "__main__":
    """
    Run the complete training pipeline
    """
    print(" Starting model training...\n")
    
    # Train model (set include_advanced_features=True for lag/rolling features)
    model, scaler, metrics = complete_training_pipeline(include_advanced_features=False)
    
    print("\n Training complete! Model saved and ready for API deployment.")
