import torch
import torch.nn as nn

class DeepLogLSTM(nn.Module):
    def __init__(self, vocab_size: int = 31, embedding_dim: int = 32, hidden_size: int = 64, num_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        last_time_step = lstm_out[:, -1, :]
        return self.fc(last_time_step)

