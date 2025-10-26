"""
Configuration for ML Trading Bot using PyTorch
"""
import os
from datetime import datetime, timedelta

# Project Structure
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Create directories
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, RESULTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Timeframes for analysis
TIMEFRAMES = ['1m', '5m', '15m']

# ML Model Configuration
MODEL_CONFIG = {
    # Sequence length for LSTM/GRU models
    'sequence_length': 60,
    
    # Features to use for training
    'features': [
        'open', 'high', 'low', 'close', 'volume',
        'rsi_14', 'ema_9', 'ema_21', 'ema_50',
        'macd', 'macd_signal', 'macd_histogram',
        'atr_14', 'vwap', 'price_change_pct', 'volatility'
    ],
    
    # Label generation threshold (0.1% for buy/sell signals - more sensitive)
    'signal_threshold': 0.001,
    
    # Data split ratios
    'train_ratio': 0.7,
    'val_ratio': 0.15,
    'test_ratio': 0.15,
    
    # PyTorch model parameters (optimized for M2 MacBook Air)
    'lstm_units': 16,  # Smaller for faster training
    'gru_units': 16,   # Smaller for faster training
    'transformer_heads': 2,  # Minimal transformer
    'transformer_layers': 1,  # Single layer
    'dropout_rate': 0.1,
    'learning_rate': 0.001,  # Higher for faster convergence
    'batch_size': 32,  # Larger batches for M2 efficiency
    'epochs': 20,  # Reduced for faster training
    'early_stopping_patience': 3,  # Stop early if no improvement
    'weight_decay': 1e-4
}

# Technical Indicators Configuration
INDICATORS_CONFIG = {
    'rsi_period': 14,
    'ema_periods': [9, 21, 50],
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'atr_period': 14,
    'volatility_period': 20
}

# User Configuration
USER_CONFIG = {
    'risk_tolerance': 5,  # 1-10 scale
    'investment_amount': 10000,  # USD
    'desired_profit_pct': 0.02,  # 2% target profit
    'max_position_size': 0.1,  # 10% of portfolio per trade
    'stop_loss_pct': 0.02,  # 2% stop loss
    'take_profit_pct': 0.03  # 3% take profit
}

# ML Model Inputs and Outputs Specification
ML_MODEL_SPECS = {
    'inputs': {
        'technical_features': [
            'open', 'high', 'low', 'close', 'volume',
            'rsi_14', 'ema_9', 'ema_21', 'ema_50',
            'macd', 'macd_signal', 'macd_histogram',
            'atr_14', 'vwap', 'price_change_pct', 'volatility'
        ],
        'user_features': [
            'risk_tolerance', 'investment_amount', 'desired_profit_pct'
        ],
        'sequence_length': 60  # Number of time steps to look back
    },
    'outputs': {
        'action': 'Buy/Hold/Sell (encoded as 1/0/-1)',
        'confidence': 'Confidence score (0-1)',
        'probability': 'Probability distribution [Buy, Hold, Sell]'
    }
}

# Reduced dataset (50 stocks + 25 cryptos for faster training)
FULL_STOCKS = [
    # Tech (15 stocks)
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM',
    'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO',
    
    # Finance (10 stocks)
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SPGI', 'MCO',
    
    # Healthcare (10 stocks)
    'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'DHR', 'ABT', 'BMY', 'LLY',
    
    # Consumer (10 stocks)
    'WMT', 'PG', 'KO', 'PEP', 'COST', 'TGT', 'HD', 'LOW', 'MCD', 'SBUX',
    
    # Energy (5 stocks)
    'XOM', 'CVX', 'COP', 'EOG', 'SLB'
]

# Reduced crypto symbols (25 major cryptocurrencies)
FULL_CRYPTO = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT',
    'SOL/USDT', 'DOGE/USDT', 'DOT/USDT', 'AVAX/USDT', 'SHIB/USDT',
    'MATIC/USDT', 'LTC/USDT', 'UNI/USDT', 'LINK/USDT', 'ATOM/USDT',
    'XLM/USDT', 'BCH/USDT', 'FIL/USDT', 'TRX/USDT', 'ETC/USDT',
    'NEAR/USDT', 'FTM/USDT', 'ALGO/USDT', 'VET/USDT', 'ICP/USDT'
]

# Sample stock tickers for testing (subset)
SAMPLE_STOCKS = FULL_STOCKS[:10]

# Sample crypto symbols for testing (subset)
SAMPLE_CRYPTO = FULL_CRYPTO[:5]

# Device configuration
DEVICE = 'cuda' if os.environ.get('CUDA_VISIBLE_DEVICES') else 'cpu'
