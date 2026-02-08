# src/model.py
import torch
import torch.nn as nn

class FilePrefetchLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super(FilePrefetchLSTM, self).__init__()
        
        # 1. Embedding Layer: Converts file IDs to vectors [cite: 43]
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # 2. LSTM Layer: Captures the time-series sequence [cite: 23, 24]
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        
        # 3. Dense Output Layer: Predicts probability of next file
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        # x shape: (batch_size, seq_length)
        embeds = self.embedding(x)
        
        # LSTM output
        lstm_out, _ = self.lstm(embeds)
        
        # We only care about the output of the last time step
        last_time_step = lstm_out[:, -1, :]
        
        # Predict logits
        out = self.fc(last_time_step)
        return out
