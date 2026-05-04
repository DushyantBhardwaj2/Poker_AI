import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, precision_recall_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os

from src.utils.config_loader import get_data_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_labels():
    logger.info("Loading labeled data...")
    labels_v2_path = get_data_path('labels_v2')
    if not labels_v2_path or not os.path.exists(labels_v2_path):
        logger.error(f"Labeled data not found at {labels_v2_path}")
        return
        
    df = pd.read_parquet(labels_v2_path)
    
    # Filter for showdown hands where we have a true label
    showdown_df = df[df['true_label'].notna()].copy()
    logger.info(f"Validating against {len(showdown_df)} showdown records.")
    
    if showdown_df.empty:
        logger.error("No showdown data for validation.")
        return

    # To calculate metrics, we need to threshold the soft label
    # Let's test different thresholds to find the best one
    thresholds = np.linspace(0.1, 0.9, 9)
    results = []
    
    for t in thresholds:
        y_pred = (showdown_df['soft_label'] > t).astype(int)
        y_true = showdown_df['true_label'].astype(int)
        
        p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
        results.append({'threshold': t, 'precision': p, 'recall': r, 'f1': f1})
        
    results_df = pd.DataFrame(results)
    logger.info("\nThreshold Calibration Results:")
    print(results_df)
    
    # Best threshold by F1
    best_t = results_df.loc[results_df['f1'].idxmax(), 'threshold']
    logger.info(f"\nBest Soft-Label Threshold: {best_t:.2f}")
    
    # 1. PR Curve
    precision, recall, _ = precision_recall_curve(showdown_df['true_label'], showdown_df['soft_label'])
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(10, 6))
    plt.plot(recall, precision, label=f'Heuristic (AUC = {pr_auc:.2f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve (Heuristic vs Showdown Ground Truth)')
    plt.legend()
    plt.grid(True)
    plt.savefig('parsed_output/pr_curve_heuristic.png')
    
    # 2. Confusion Matrix at best threshold
    y_pred_best = (showdown_df['soft_label'] > best_t).astype(int)
    cm = confusion_matrix(showdown_df['true_label'], y_pred_best)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted (Heuristic)')
    plt.ylabel('Actual (Showdown)')
    plt.title(f'Confusion Matrix at Threshold {best_t:.2f}')
    plt.savefig('parsed_output/confusion_matrix_heuristic.png')
    
    # Save Report
    with open('parsed_output/calibration_report.txt', 'w') as f:
        f.write("PHASE 4: CALIBRATION REPORT\n")
        f.write(f"Validation records: {len(showdown_df)}\n")
        f.write(f"Best Threshold: {best_t}\n")
        f.write(f"Precision: {results_df.loc[results_df['threshold'] == best_t, 'precision'].values[0]:.3f}\n")
        f.write(f"Recall: {results_df.loc[results_df['threshold'] == best_t, 'recall'].values[0]:.3f}\n")
        f.write(f"F1-Score: {results_df.loc[results_df['threshold'] == best_t, 'f1'].values[0]:.3f}\n")
        f.write(f"PR-AUC: {pr_auc:.3f}\n")

    logger.info("Calibration complete. Results saved to parsed_output/")

if __name__ == "__main__":
    validate_labels()
