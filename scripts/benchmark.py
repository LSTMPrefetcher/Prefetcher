import subprocess
import os
import time
import re
import sys

# --- FIX START: Add the project root to Python path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
# --- FIX END ---

from src.utils import get_paths

def clear_cache():
    """Forces Linux to clear RAM (Drop Caches). Requires Sudo."""
    print(f"[*] Clearing System RAM (Cold Start Simulation)...")
    os.system("sync; echo 3 > /proc/sys/vm/drop_caches")

def parse_execution_time(log_path):
    """Calculates time difference by finding timestamps anywhere in the line."""
    start_time = None
    end_time = None
    
    # Regex to find time format HH:MM:SS.micros (e.g., 17:45:48.085)
    time_regex = re.compile(r'(\d{2}):(\d{2}):(\d{2})\.(\d+)')

    try:
        with open(log_path, 'r', errors='ignore') as f:
            for line in f:
                # Search the ENTIRE line for a timestamp match
                match = time_regex.search(line)
                if match:
                    # Extract the time components
                    h, m, s, ms = match.groups()
                    
                    # Convert to absolute seconds
                    # We treat microseconds (ms) as a fraction
                    total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + float(f"0.{ms}")
                    
                    if start_time is None:
                        start_time = total_seconds
                    end_time = total_seconds

        if start_time and end_time:
            return end_time - start_time
        
        # If we found no timestamps, return 0
        return 0.0

    except FileNotFoundError:
        print(f"[!] Error: Log file {log_path} not found.")
        return 0.0

def run_test_cycle(label, use_ai=False):
    cfg, paths = get_paths()
    log_file = f"data/raw/{label}_benchmark.txt"
    
    # 1. Clear RAM to ensure the test is fair
    clear_cache()

    # 2. If AI is enabled, run the prefetcher FIRST
    if use_ai:
        print(f"[*] Running AI Prefetcher...")
        # We run the prefetcher script as a subprocess
        subprocess.run([sys.executable, "src/prefetcher.py"], check=False)

    # 3. Run the Application with strace to measure time
    print(f"[*] Launching Application ({label})...")
    
    # We use -tt to get microsecond timestamps
    cmd = f"strace -tt -f -e trace=openat -o {log_file} {paths['app_cmd']}"
    
    # Using os.system because it handles complex commands (timeout/pipes) well
    os.system(cmd)

    # 4. Calculate Time
    duration = parse_execution_time(log_file)
    print(f"[{label}] Startup Time: {duration:.4f} seconds")
    return duration

def main():
    # Check for sudo (needed for drop_caches)
    if os.geteuid() != 0:
        print("[!] This script requires ROOT privileges to clear RAM.")
        print("[!] Please run with: sudo ./venv/bin/python3 scripts/benchmark.py")
        sys.exit(1)

    print("="*50)
    print("   AI PREFETCHER PERFORMANCE BENCHMARK")
    print("="*50)

    # 1. Measure COLD Start (Standard Linux)
    t_cold = run_test_cycle("COLD_START", use_ai=False)

    print("-" * 50)

    # 2. Measure WARM Start (With AI)
    t_warm = run_test_cycle("AI_START", use_ai=True)

    print("=" * 50)
    print("FINAL RESULTS:")
    print(f"Cold Start Time : {t_cold:.4f} sec")
    print(f"AI Start Time   : {t_warm:.4f} sec")
    
    if t_cold > 0:
        improvement = ((t_cold - t_warm) / t_cold) * 100
        print(f"SPEEDUP         : {improvement:.2f}% FASTER")
    else:
        print("Error: Could not measure time (log empty?)")
    print("=" * 50)

if __name__ == "__main__":
    main()
