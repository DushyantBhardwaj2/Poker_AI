import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_squared_error, r2_score, precision_recall_fscore_support
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model():
    logger.info("Loading labeled dataset...")
    df = pd.read_parquet('parsed_output/labeled_dataset_v1.parquet')
    
    # Define features and target
    features = [
        'street', 'rel_bet_size', 'bet_spike', 'dryness',
        'vpip', 'pfr', 'prev_action_bet_size', 'is_monotonic', 'range_miss'
    ]
    target = 'soft_label'
    weight = 'confidence_weight'
    
    X = df[features]
    y = df[target]
    w = df[weight]
    groups = df['player_id'] # Use player_id for GroupKFold to prevent leakage
    
    # Clean inf and nan
    logger.info("Cleaning inf and nan values...")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0) # Simple imputation for now
    
    logger.info(f"Training on {len(df)} records with {len(features)} features.")
    
    # Initialize GroupKFold
    gkf = GroupKFold(n_splits=5)
    
    # Tracking metrics
    mse_scores = []
    r2_scores = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        w_train, w_val = w.iloc[train_idx], w.iloc[val_idx]
        
        # Train XGBoost
        model = xgb.XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            n_jobs=-1,
            random_state=42
        )
        
        model.fit(X_train, y_train, sample_weight=w_train, eval_set=[(X_val, y_val)], 
                  sample_weight_eval_set=[w_val], verbose=False)
        
        # Predict
        y_pred = model.predict(X_val)
        
        mse = mean_squared_error(y_val, y_pred, sample_weight=w_val)
        r2 = r2_score(y_val, y_pred, sample_weight=w_val)
        
        mse_scores.append(mse)
        r2_scores.append(r2)
        logger.info(f"Fold {fold}: MSE={mse:.4f}, R2={r2:.4f}")

    logger.info(f"Average MSE: {np.mean(mse_scores):.4f}")
    logger.info(f"Average R2: {np.mean(r2_scores):.4f}")
    
    # Final model training on full data
    final_model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42
    )
    final_model.fit(X, y, sample_weight=w)
    
    # Save model and metadata
    model_path = 'parsed_output/bluff_detector_v1.joblib'
    joblib.dump(final_model, model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Save feature importance
    importance = pd.DataFrame({
        'feature': features,
        'importance': final_model.feature_importances_
    }).sort_values('importance', ascending=False)
    importance.to_csv('parsed_output/feature_importance_v1.csv', index=False)
    logger.info("\nFeature Importance:")
    print(importance)
    
    # 3. Final Validation against Showdown Ground Truth
    showdown_mask = df['true_label'].notna()
    if showdown_mask.any():
        X_test = df.loc[showdown_mask, features]
        y_true = df.loc[showdown_mask, 'true_label'].astype(int)
        
        y_prob = final_model.predict(X_test)
        y_pred = (y_prob > 0.4).astype(int) # Using calibrated threshold
        
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
        logger.info("\nFinal Validation on Showdown Data:")
        logger.info(f"Precision: {p:.3f}, Recall: {r:.3f}, F1: {f1:.3f}")
        
    return final_model

if __name__ == "__main__":
    train_model()
