# src/collector.py
import subprocess
import os
import shlex
from src.utils import get_paths

def collect_traces():
    cfg, paths = get_paths()
    
    # Ensure directory exists
    os.makedirs(cfg['data']['raw_path'], exist_ok=True)

    print(f"[*] App: {cfg['system']['app_name']}")
    print(f"[*] Target: {paths['raw_log']}")

    # Use 'shlex' to split safely
    app_cmd = shlex.split(paths['app_cmd'])

    cmd = [
        "strace", 
        "-f", 
        "-A", # Append mode (Keep history for THIS app)
        "-e", "trace=openat", 
        "-o", paths['raw_log'], 
    ] + app_cmd

    try:
        subprocess.run(cmd, check=False) # check=False because timeout returns 124
        print("[*] Trace collection complete.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    collect_traces()
