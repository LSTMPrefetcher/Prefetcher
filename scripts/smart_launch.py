import sys
import os
import subprocess
import time

# --- FIX: Add project root to path so imports work ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
# ---------------------------------------------------

from src.utils import get_paths
from src.prefetcher import run_prefetcher

def smart_launch():
    # 1. Run the AI Prefetcher
    print("\n" + "="*40)
    print("      🚀 AI SMART LAUNCHER      ")
    print("="*40)
    
    print("[1/2] Analyzing context and prefetching files...")
    start_time = time.time()
    
    # This function loads the model and runs 'vmtouch'
    run_prefetcher()
    
    duration = time.time() - start_time
    print(f"      (AI Prep complete in {duration:.4f} sec)")

    # 2. Launch the Application
    cfg, paths = get_paths()
    app_cmd = cfg['system']['target_app']
    
    print(f"[2/2] Launching Application: {cfg['system']['app_name']}...")
    print("-" * 40)
    
    # Execute the actual command
    os.system(app_cmd)

if __name__ == "__main__":
    smart_launch()
