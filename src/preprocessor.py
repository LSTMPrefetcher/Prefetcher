# src/preprocessor.py
import re
import json
import os
from src.utils import get_paths

def parse_strace_log(log_path):
    file_sequence = []
    regex = r'openat\(.*?"(.*?)"'
    
    with open(log_path, 'r', errors='ignore') as f:
        for line in f:
            match = re.search(regex, line)
            if match:
                filepath = match.group(1)
                if filepath.startswith("/") and not filepath.startswith("/dev") and not filepath.startswith("/proc"):
                    file_sequence.append(filepath)
    return file_sequence

def build_vocab(file_sequence, save_path):
    unique_files = sorted(list(set(file_sequence)))
    vocab = {file: idx + 1 for idx, file in enumerate(unique_files)}
    with open(save_path, 'w') as f:
        json.dump(vocab, f)
    return vocab

def preprocess():
    cfg, paths = get_paths()
    os.makedirs(cfg['data']['processed_path'], exist_ok=True)

    print(f"[*] Processing data for: {cfg['system']['app_name']}")
    files = parse_strace_log(paths['raw_log'])
    print(f"[*] Found {len(files)} events.")
    
    vocab = build_vocab(files, paths['vocab'])
    print(f"[*] Vocab saved to: {paths['vocab']}")

if __name__ == "__main__":
    preprocess()
