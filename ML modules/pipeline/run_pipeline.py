import os
import sys
import logging
import argparse

# Add the project root to sys.path to support absolute imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.features.engineer_features_v2 import engineer_features_v2
from src.labeling.heuristic_labeler_v2 import generate_labels_v2
from src.models.train_model_v2 import train_model_v2
from src.utils.config_loader import load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ML_Pipeline")

def run_pipeline(steps=None):
    """
    Run the ML pipeline steps.
    Steps can be: 'features', 'labeling', 'train', 'all'
    """
    config = load_config()
    logger.info("Starting ML Pipeline...")
    
    if not steps or 'all' in steps:
        steps = ['features', 'labeling', 'train']
        
    if 'features' in steps:
        logger.info("--- Step 1: Feature Engineering ---")
        engineer_features_v2()
        
    if 'labeling' in steps:
        logger.info("--- Step 2: Heuristic Labeling ---")
        generate_labels_v2()
        
    if 'train' in steps:
        logger.info("--- Step 3: Model Training ---")
        train_model_v2()
        
    logger.info("ML Pipeline completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PokerSense ML Pipeline")
    parser.add_argument(
        "--steps", 
        nargs="+", 
        choices=["features", "labeling", "train", "all"],
        default=["all"],
        help="Pipeline steps to run"
    )
    
    args = parser.parse_args()
    run_pipeline(args.steps)
