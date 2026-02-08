# src/evaluator.py
import time
import subprocess
import os
import yaml
import sys

def clear_cache():
    """Forces Linux to drop RAM caches to simulate a 'Cold Start'."""
    print("[!] Clearing System Cache (Requires Sudo)...")
    os.system("sync; echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null")

def measure_launch_time(app_name):
    start_time = time.time()
    
    # Launch app and wait for it to initialize
    # Note: 'timeout' stops the app after 5 seconds so we don't get stuck
    try:
        subprocess.run(["timeout", "5s", app_name], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception:
        pass # Expected since we kill it with timeout
        
    end_time = time.time()
    return end_time - start_time

def evaluate():
    with open("config/config.yaml") as f:
        cfg = yaml.safe_load(f)
    
    app_name = cfg['system']['target_app']
    
    print("--- EVALUATION STARTED ---")
    
    # Test 1: Cold Start (No AI)
    clear_cache()
    print("[*] Measuring Cold Start Time (Baseline)...")
    cold_time = measure_launch_time(app_name)
    print(f" -> Cold Start Time: {cold_time:.4f} seconds")

    # Test 2: AI Prefetched Start
    clear_cache()
    print("[*] Running AI Prefetcher...")
    # Use the same python that is running this script (the venv one)
    os.system(f"{sys.executable} -m src.prefetcher")
    
    print("[*] Measuring Prefetched Start Time...")
    ai_time = measure_launch_time(app_name)
    print(f" -> AI Start Time:   {ai_time:.4f} seconds")

    # Results
    improvement = ((cold_time - ai_time) / cold_time) * 100
    print("-" * 30)
    print(f"RESULT: Speedup of {improvement:.2f}%")

if __name__ == "__main__":
    evaluate()
