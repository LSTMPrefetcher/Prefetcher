# src/utils.py
import os
import yaml

def get_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_paths():
    cfg = get_config()
    name = cfg['system']['app_name']
    
    # Generate unique filenames based on the App Name
    paths = {
        "raw_log": os.path.join(cfg['data']['raw_path'], f"{name}_log.txt"),
        "vocab": os.path.join(cfg['data']['processed_path'], f"{name}_vocab.json"),
        "model": os.path.join(cfg['data']['models_path'], f"{name}_model.pth"),
        "app_cmd": cfg['system']['target_app']
    }
    return cfg, paths
