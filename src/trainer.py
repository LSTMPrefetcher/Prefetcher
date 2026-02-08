# src/trainer.py
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
from src.model import FilePrefetchLSTM
from src.preprocessor import parse_strace_log
from src.utils import get_paths

class FileLogDataset(Dataset):
    def __init__(self, log_path, vocab, seq_length=10):
        self.files = parse_strace_log(log_path)
        self.vocab = vocab
        self.seq_length = seq_length
        self.data_ids = [self.vocab[f] for f in self.files if f in self.vocab]

    def __len__(self):
        return max(0, len(self.data_ids) - self.seq_length)

    def __getitem__(self, idx):
        x = self.data_ids[idx : idx + self.seq_length]
        y = self.data_ids[idx + self.seq_length]
        return torch.tensor(x, dtype=torch.long), torch.tensor(y, dtype=torch.long)

def train_model():
    cfg, paths = get_paths()
    os.makedirs(cfg['data']['models_path'], exist_ok=True)

    print(f"[*] Training Brain for: {cfg['system']['app_name']}")

    # Load Vocab
    with open(paths['vocab'], 'r') as f:
        vocab = json.load(f)

    # Prepare Data
    dataset = FileLogDataset(paths['raw_log'], vocab, seq_length=cfg['model']['seq_length'])
    if len(dataset) == 0:
        print("[!] Not enough data to train. Run collection more times.")
        return

    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Init Model
    model = FilePrefetchLSTM(len(vocab) + 1, cfg['model']['embedding_dim'], cfg['model']['hidden_dim'])
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=cfg['model']['learning_rate'])

    # Train
    model.train()
    for epoch in range(cfg['model']['epochs']):
        total_loss = 0
        for x_batch, y_batch in dataloader:
            optimizer.zero_grad()
            output = model(x_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1} Loss: {total_loss/len(dataloader):.4f}")

    # SAVE UNIQUE MODEL
    torch.save(model.state_dict(), paths['model'])
    print(f"[*] Model saved to {paths['model']}")

if __name__ == "__main__":
    train_model()
