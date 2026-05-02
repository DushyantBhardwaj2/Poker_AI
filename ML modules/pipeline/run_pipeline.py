import os
import sys
import logging
import argparse

# Add the project root to sys.path to support absolute imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.parsers.aggressive_parser import run_ingestion
from src.evaluation.validate_data_quality import run_validation
from src.preprocessing.generate_mismatch_surface import generate_mismatch_surface
from src.features.calculate_player_stats_aggressive import run_profiling
from src.features.engineer_features_v2 import engineer_features_v2
from src.features.engineer_features_v3 import engineer_features_v3
from src.labeling.heuristic_labeler_v2 import generate_labels_v2
from src.labeling.heuristic_labeler_v3 import generate_labels_v3
from src.models.train_model_v2 import train_model_v2
from src.models.train_model_v3 import train_model_v3
from src.utils.config_loader import load_config, get_data_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ML_Pipeline")

def check_dependencies(steps, version='v2'):
    """Verify that required input files exist for each step."""
    config = load_config()
    data_config = config.get('data', {})
    
    feature_key = f'features_{version}'
    label_key = f'labels_{version}'
    
    dependencies = {
        'validate': ['parsed_aggressive'],
        'surface': ['parsed_aggressive'],
        'profile': ['raw_hand_histories'],
        'features': ['parsed_aggressive', 'player_stats_aggressive'],
        'labeling': [feature_key, 'mismatch_surface'],
        'train': [label_key]
    }
    
    missing = []
    for step in steps:
        if step in dependencies:
            for dep_key in dependencies[step]:
                path = get_data_path(dep_key)
                if not path or not os.path.exists(path):
                    # For profile, raw_hand_histories is a directory
                    if dep_key == 'raw_hand_histories' and path and os.path.isdir(path):
                        continue
                    # For mismatch_surface, it might be in the same dir as parsed_aggressive
                    if dep_key == 'mismatch_surface' and not path:
                         parsed_path = get_data_path('parsed_aggressive')
                         if parsed_path:
                             path = os.path.join(os.path.dirname(parsed_path), 'mismatch_surface.csv')
                             if os.path.exists(path):
                                 continue
                    missing.append(f"{step} -> {dep_key} ({path})")
    
    return missing

def run_pipeline(steps=None, limit=1000, dry_run=False, version='v2'):
    """
    Run the ML pipeline steps.
    Steps can be: 'ingest', 'validate', 'surface', 'profile', 'features', 'labeling', 'train', 'all'
    """
    config = load_config()
    logger.info(f"Starting ML Pipeline ({version})...")
    
    if not steps or 'all' in steps:
        steps = ['ingest', 'validate', 'surface', 'profile', 'features', 'labeling', 'train']
    
    # Check dependencies (except for ingest which creates its own)
    missing = check_dependencies([s for s in steps if s != 'ingest'], version=version)
    if missing:
        logger.error("Missing dependencies for pipeline execution:")
        for m in missing:
            logger.error(f"  - {m}")
        if not dry_run:
            logger.error("Abort.")
            return

    if dry_run:
        logger.info("Dry run check passed. All dependencies for requested steps are present.")
        return
        
    if 'ingest' in steps:
        logger.info("--- Step 1: Data Ingestion (Aggressive) ---")
        run_ingestion(limit=limit)

    if 'validate' in steps:
        logger.info("--- Step 1.5: Data Quality Validation ---")
        success = run_validation(get_data_path("parsed_aggressive"))
        if not success:
            logger.error("Data quality validation FAILED. Pipeline aborted.")
            return
        logger.info("Data quality validation PASSED.")

    if 'surface' in steps:
        logger.info("--- Step 1.6: Dynamic Mismatch Surface Generation ---")
        success = generate_mismatch_surface()
        if not success:
            logger.error("Surface generation FAILED. Pipeline aborted.")
            return
        logger.info("Mismatch surface generation PASSED.")

    if 'profile' in steps:
        logger.info("--- Step 2: Player Profiling (Aggressive) ---")
        run_profiling(limit=max(limit, 2000))

    if 'features' in steps:
        logger.info(f"--- Step 3: Feature Engineering ({version}) ---")
        if version == 'v3':
            engineer_features_v3()
        else:
            engineer_features_v2()
        
    if 'labeling' in steps:
        logger.info(f"--- Step 4: Heuristic Labeling ({version}) ---")
        if version == 'v3':
            generate_labels_v3()
        else:
            generate_labels_v2()
        
    if 'train' in steps:
        logger.info(f"--- Step 5: Model Training ({version}) ---")
        if version == 'v3':
            train_model_v3()
        else:
            train_model_v2()
        
    logger.info("ML Pipeline completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PokerSense ML Pipeline")
    parser.add_argument(
        "--steps", 
        nargs="+", 
        choices=["ingest", "validate", "surface", "profile", "features", "labeling", "train", "all"],
        default=["all"],
        help="Pipeline steps to run"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100, # Small default for safety
        help="Limit for files to process in ingestion/profiling"
    )
    parser.add_argument(
        "--version",
        choices=["v2", "v3"],
        default="v2",
        help="Feature and Labeling version"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check dependencies without executing steps"
    )
    
    args = parser.parse_args()
    run_pipeline(args.steps, limit=args.limit, dry_run=args.dry_run, version=args.version)
