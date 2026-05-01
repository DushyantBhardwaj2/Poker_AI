import json
import os

def load_config():
    """Load the pipeline configuration from the configs directory."""
    # Assuming this script is run from the 'ML modules' root or via the pipeline
    config_path = os.path.join(os.path.dirname(__file__), '../../configs/pipeline_config.json')
    if not os.path.exists(config_path):
        # Fallback for when running from root
        config_path = 'configs/pipeline_config.json'
        
    with open(config_path, 'r') as f:
        return json.load(f)

def get_data_path(key):
    """Get a specific data path from the config."""
    config = load_config()
    return config['data'].get(key)
