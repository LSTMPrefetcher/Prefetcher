# src/prefetcher.py
import torch
import json
import os
import subprocess
import sys

# --- FIX START: Add project root to path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
# --- FIX END ---

from src.model import FilePrefetchLSTM
from src.utils import get_paths

def load_vmtouch(filepath):
    if os.path.exists(filepath):
        subprocess.run(["vmtouch", "-t", filepath], check=False, stderr=subprocess.DEVNULL)

def run_prefetcher():
    cfg, paths = get_paths()

    # Load specific vocab and model
    with open(paths['vocab'], 'r') as f:
        vocab = json.load(f)
    idx_to_file = {v: k for k, v in vocab.items()}

    model = FilePrefetchLSTM(len(vocab)+1, cfg['model']['embedding_dim'], cfg['model']['hidden_dim'])
    model.load_state_dict(torch.load(paths['model']))
    model.eval()

    print(f"[*] Prefetcher loaded for: {cfg['system']['app_name']}")
    
    # Fake input for demo (in production, hook to live system)
    dummy_input_ids = [1] * cfg['model']['seq_length']
    input_tensor = torch.tensor([dummy_input_ids])

    with torch.no_grad():
        output = model(input_tensor)
        predicted_id = torch.argmax(output, dim=1).item()
    
    predicted_file = idx_to_file.get(predicted_id, None)
    
    if predicted_file:
        print(f"[*] Prediction: {predicted_file}")
        load_vmtouch(predicted_file)

if __name__ == "__main__":
    run_prefetcher()
