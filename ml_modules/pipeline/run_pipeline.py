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
from src.features.engineer_features_v3 import engineer_features_v3
from src.labeling.heuristic_labeler_v3 import generate_labels_v3
from src.models.train_model_v3 import train_model_v3
from src.models.train_showdown_model import train_showdown_model
from src.utils.config_loader import load_config, get_data_path

# This file used to import engineer_features_v2, heuristic_labeler_v2 and
# train_model_v2, and default --version to v2. Those three modules were deleted
# when v3 replaced them, so importing this module raised ModuleNotFoundError and
# the documented entry point could not be run at all. v3 is the only path now, so
# the version switch is gone with it.
#
# The 'showdown' step is the one that produces the deployed model. 'train' fits
# against the heuristic labels, which is the approach MAKING_OF_ML_MODULE.md
# describes abandoning; it is kept because the comparison is the point of that
# write-up, but it is not what packages/ai/models holds.

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ML_Pipeline")

ALL_STEPS = ['ingest', 'validate', 'surface', 'profile', 'features', 'labeling', 'showdown']

def check_dependencies(steps):
    """Verify that required input files exist for each step."""
    config = load_config()
    data_config = config.get('data', {})

    dependencies = {
        'validate': ['parsed_aggressive'],
        'surface': ['parsed_aggressive'],
        'profile': ['raw_hand_histories'],
        'features': ['parsed_aggressive', 'player_stats_aggressive'],
        'labeling': ['features_v3', 'mismatch_surface'],
        'train': ['labels_v3'],
        'showdown': ['labels_v3']
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

def run_pipeline(steps=None, limit=1000, dry_run=False):
    """
    Run the ML pipeline steps.
    Steps can be: 'ingest', 'validate', 'surface', 'profile', 'features',
    'labeling', 'train', 'showdown', 'all'
    """
    config = load_config()
    logger.info("Starting ML Pipeline...")

    if not steps or 'all' in steps:
        steps = list(ALL_STEPS)

    # Check dependencies (except for ingest which creates its own)
    missing = check_dependencies([s for s in steps if s != 'ingest'])
    if missing:
        logger.error("Missing dependencies for pipeline execution:")
        for m in missing:
            logger.error(f"  - {m}")
        # A dry run reports and stops either way. It used to fall through to the
        # unconditional "all dependencies are present" line below, so it printed
        # the list of what was missing and then declared the check passed.
        if dry_run:
            logger.error(f"Dry run FAILED: {len(missing)} missing input(s).")
        else:
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
        logger.info("--- Step 3: Feature Engineering ---")
        engineer_features_v3()

    if 'labeling' in steps:
        logger.info("--- Step 4: Heuristic Labeling ---")
        generate_labels_v3()

    if 'train' in steps:
        logger.info("--- Step 5a: Training on heuristic labels (superseded) ---")
        train_model_v3()

    if 'showdown' in steps:
        logger.info("--- Step 5b: Training on showdown ground truth ---")
        train_showdown_model()

    logger.info("ML Pipeline completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PokerSense ML Pipeline")
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=ALL_STEPS + ["train", "all"],
        default=["all"],
        help="Pipeline steps to run. 'all' skips 'train', the superseded "
             "heuristic-label fit; ask for it by name to run it."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100, # Small default for safety
        help="Limit for files to process in ingestion/profiling"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check dependencies without executing steps"
    )

    args = parser.parse_args()
    run_pipeline(args.steps, limit=args.limit, dry_run=args.dry_run)
