"""
PyTorch ML Models for Trading Bot
Implements LSTM, GRU, and Transformer models for time series prediction
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Dict, Tuple, Optional
import math

class TradingDataset(Dataset):
    """PyTorch Dataset for trading data"""
    
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class LSTMTradingModel(nn.Module):
    """LSTM model for trading signal prediction"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, 
                 dropout: float = 0.2, num_classes: int = 3):
        super(LSTMTradingModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8, dropout=dropout)
        
        # Classification layers
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_size // 2, num_classes)
        
    def forward(self, x):
        batch_size = x.size(0)
        
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Apply attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use the last output
        out = attn_out[:, -1, :]
        
        # Classification layers
        out = F.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

class GRUTradingModel(nn.Module):
    """GRU model for trading signal prediction"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2,
                 dropout: float = 0.2, num_classes: int = 3):
        super(GRUTradingModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # GRU layers
        self.gru = nn.GRU(input_size, hidden_size, num_layers,
                         batch_first=True, dropout=dropout)
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=8, dropout=dropout)
        
        # Classification layers
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_size // 2, num_classes)
        
    def forward(self, x):
        # GRU forward pass
        gru_out, hidden = self.gru(x)
        
        # Apply attention
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        
        # Use the last output
        out = attn_out[:, -1, :]
        
        # Classification layers
        out = F.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

class TransformerTradingModel(nn.Module):
    """Transformer model for trading signal prediction"""
    
    def __init__(self, input_size: int, d_model: int = 64, nhead: int = 8, 
                 num_layers: int = 4, dropout: float = 0.2, num_classes: int = 3):
        super(TransformerTradingModel, self).__init__()
        
        self.d_model = d_model
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(d_model, dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Classification layers
        self.fc1 = nn.Linear(d_model, d_model // 2)
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(d_model // 2, num_classes)
        
    def forward(self, x):
        # Project input to model dimension
        x = self.input_projection(x)
        
        # Add positional encoding
        x = self.pos_encoding(x)
        
        # Transformer forward pass
        transformer_out = self.transformer(x)
        
        # Use the last output
        out = transformer_out[:, -1, :]
        
        # Classification layers
        out = F.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                           (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
        
    def forward(self, x):
        x = x + self.pe[:x.size(1), :].transpose(0, 1)
        return self.dropout(x)

class ModelFactory:
    """Factory class for creating different model types"""
    
    @staticmethod
    def create_model(model_type: str, input_size: int, config: Dict) -> nn.Module:
        """
        Create a model based on type and configuration
        
        Args:
            model_type: Type of model ('lstm', 'gru', 'transformer')
            input_size: Number of input features
            config: Model configuration dictionary
            
        Returns:
            PyTorch model
        """
        if model_type.lower() == 'lstm':
            return LSTMTradingModel(
                input_size=input_size,
                hidden_size=config.get('lstm_units', 64),
                num_layers=2,
                dropout=config.get('dropout_rate', 0.2),
                num_classes=3
            )
        elif model_type.lower() == 'gru':
            return GRUTradingModel(
                input_size=input_size,
                hidden_size=config.get('gru_units', 64),
                num_layers=2,
                dropout=config.get('dropout_rate', 0.2),
                num_classes=3
            )
        elif model_type.lower() == 'transformer':
            return TransformerTradingModel(
                input_size=input_size,
                d_model=config.get('transformer_heads', 8) * 8,
                nhead=config.get('transformer_heads', 8),
                num_layers=config.get('transformer_layers', 4),
                dropout=config.get('dropout_rate', 0.2),
                num_classes=3
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

class ModelTrainer:
    """Class for training PyTorch models"""
    
    def __init__(self, model: nn.Module, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        
    def train_epoch(self, dataloader: DataLoader, optimizer: torch.optim.Optimizer, 
                   criterion: nn.Module) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        
        for batch_X, batch_y in dataloader:
            batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
            
            # Check for NaN values in input
            if torch.isnan(batch_X).any() or torch.isnan(batch_y).any():
                print("Warning: NaN values detected in batch, skipping...")
                continue
            
            optimizer.zero_grad()
            outputs = self.model(batch_X)
            
            # Check for NaN in outputs
            if torch.isnan(outputs).any():
                print("Warning: NaN values in model outputs, skipping...")
                continue
                
            loss = criterion(outputs, batch_y)
            
            # Check for NaN in loss
            if torch.isnan(loss):
                print("Warning: NaN loss detected, skipping...")
                continue
                
            loss.backward()
            
            # Gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(dataloader) if len(dataloader) > 0 else 0.0
    
    def validate_epoch(self, dataloader: DataLoader, criterion: nn.Module) -> Tuple[float, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_X, batch_y in dataloader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
        
        accuracy = correct / total
        return total_loss / len(dataloader), accuracy
    
    def predict(self, dataloader: DataLoader) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions on a dataset"""
        self.model.eval()
        predictions = []
        probabilities = []
        
        with torch.no_grad():
            for batch_X, _ in dataloader:
                batch_X = batch_X.to(self.device)
                outputs = self.model(batch_X)
                probs = F.softmax(outputs, dim=1)
                
                predictions.extend(torch.argmax(outputs, dim=1).cpu().numpy())
                probabilities.extend(probs.cpu().numpy())
        
        return np.array(predictions), np.array(probabilities)
