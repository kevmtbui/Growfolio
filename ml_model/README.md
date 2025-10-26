# ML Day Trading Bot

A machine learning-based trading system that predicts short-term Buy/Hold/Sell signals for stocks and cryptocurrencies using PyTorch.

## Features

- **Multiple ML Models**: LSTM, GRU, and Transformer architectures
- **Technical Indicators**: RSI, EMA, MACD, ATR, VWAP, and more
- **Real-time Prediction**: Live trading signal generation
- **Risk Management**: User-configurable risk tolerance and position sizing
- **Timeframes**: 1-minute, 5-minute, and 15-minute analysis
- **Backtesting**: Historical performance evaluation

## ML Model Specifications

### Inputs
- **Technical Features** (16 features):
  - `open`, `high`, `low`, `close`, `volume`
  - `rsi_14`, `ema_9`, `ema_21`, `ema_50`
  - `macd`, `macd_signal`, `macd_histogram`
  - `atr_14`, `vwap`, `price_change_pct`, `volatility`
- **User Features** (3 features):
  - `risk_tolerance` (1-10 scale)
  - `investment_amount` (USD)
  - `desired_profit_pct` (percentage)
- **Sequence Length**: 60 time steps (lookback period)

### Outputs
- **Action**: Buy/Hold/Sell (encoded as 1/0/-1)
- **Confidence**: Confidence score (0-1)
- **Probability**: Probability distribution [Buy, Hold, Sell]

## Project Structure

```
ml_model/
├── data/
│   ├── raw/           # Raw OHLCV data
│   └── processed/    # Processed features and labels
├── models/           # Trained model files
├── results/         # Training results and plots
├── logs/           # Training logs
├── src/
│   ├── indicators.py      # Technical indicators
│   ├── preprocess_data.py # Data preprocessing
│   ├── models.py          # PyTorch model definitions
│   ├── train_model.py     # Model training
│   └── predict_live.py    # Live prediction
├── config.py        # Configuration settings
├── example_usage.py # Usage examples
└── requirements.txt # Dependencies
```

## Quick Start

### 1. Installation

```bash
cd ml_model
pip install -r requirements.txt
```

### 2. Run Examples

```bash
python example_usage.py
```

This will:
- Create sample data
- Train LSTM, GRU, and Transformer models
- Make live predictions
- Compare model performance

### 3. Train Your Own Model

```python
from src.train_model import TradingModelTrainer

# Initialize trainer
trainer = TradingModelTrainer(model_type='lstm')

# Prepare data (you need OHLCV data in parquet format)
data = trainer.prepare_data('AAPL', '5m', 'path/to/data')

# Train model
results = trainer.train_model(data, 'AAPL', '5m')
```

### 4. Make Live Predictions

```python
from src.predict_live import LivePredictor

# Initialize predictor
predictor = LivePredictor(model_type='lstm')

# Load your OHLCV data
df = pd.read_parquet('your_data.parquet')

# Make prediction
result = predictor.predict_signal(df, 'AAPL', '5m', {
    'risk_tolerance': 7,
    'investment_amount': 10000,
    'desired_profit_pct': 0.02
})

print(f"Action: {result['action']}")
print(f"Confidence: {result['confidence']}")
```

## 🧠 Model Architecture

### LSTM Model
- **Input**: 60 timesteps × 16 features
- **LSTM Layers**: 2 layers, 64 units each
- **Attention**: Multi-head attention mechanism
- **Output**: 3-class classification

### GRU Model
- **Input**: 60 timesteps × 16 features
- **GRU Layers**: 2 layers, 64 units each
- **Attention**: Multi-head attention mechanism
- **Output**: 3-class classification

### Transformer Model
- **Input**: 60 timesteps × 16 features
- **Encoder Layers**: 4 transformer layers
- **Attention Heads**: 8 attention heads
- **Output**: 3-class classification

## Technical Indicators

The system computes 16 technical indicators:

1. **Price Data**: open, high, low, close, volume
2. **Momentum**: RSI (14), MACD (12,26,9)
3. **Trend**: EMA (9,21,50)
4. **Volatility**: ATR (14), Bollinger Bands
5. **Volume**: VWAP, Volume SMA
6. **Price Features**: Price change %, High-Low %, etc.

## Configuration

Edit `config.py` to customize:

```python
# Model parameters
MODEL_CONFIG = {
    'sequence_length': 60,
    'lstm_units': 64,
    'dropout_rate': 0.2,
    'learning_rate': 0.001,
    'epochs': 100
}

# User settings
USER_CONFIG = {
    'risk_tolerance': 5,  # 1-10 scale
    'investment_amount': 10000,
    'desired_profit_pct': 0.02
}
```

## Performance Metrics

The system evaluates models using:

- **Accuracy**: Overall prediction accuracy
- **Precision/Recall**: Per-class performance
- **F1-Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Detailed classification results
- **Training History**: Loss and accuracy curves

## 🔄 Training Pipeline

1. **Data Loading**: Load OHLCV data from parquet files
2. **Data Cleaning**: Remove invalid data, handle missing values
3. **Feature Engineering**: Compute technical indicators
4. **Label Generation**: Create Buy/Hold/Sell labels based on future returns
5. **Data Splitting**: Train/Validation/Test (70/15/15)
6. **Model Training**: Train with early stopping
7. **Evaluation**: Test on unseen data
8. **Saving**: Save model and results

## Live Prediction Pipeline

1. **Data Preparation**: Load recent OHLCV data
2. **Feature Computation**: Calculate technical indicators
3. **Scaling**: Apply trained scaler to features
4. **Prediction**: Run through trained model
5. **Risk Adjustment**: Apply user risk preferences
6. **Output**: Return action, confidence, and probabilities

## 📝 Example Output

```json
{
  "symbol": "AAPL",
  "timeframe": "5m",
  "action": "Buy",
  "risk_adjusted_action": "Buy",
  "confidence": 0.85,
  "probabilities": {
    "sell": 0.05,
    "hold": 0.10,
    "buy": 0.85
  }
}
```

## Customization

### Adding New Features
1. Modify `src/indicators.py` to add new technical indicators
2. Update `config.py` to include new features in `MODEL_CONFIG['features']`
3. Retrain models with new features

### Adding New Models
1. Create new model class in `src/models.py`
2. Add to `ModelFactory.create_model()`
3. Update training and prediction scripts

### Risk Management
- Adjust `USER_CONFIG` for different risk profiles
- Modify `_apply_risk_adjustment()` in `predict_live.py`
- Implement position sizing based on confidence scores

## 📚 Dependencies

- **PyTorch**: Deep learning framework
- **pandas/numpy**: Data manipulation
- **scikit-learn**: ML utilities and metrics
- **ta**: Technical analysis indicators
- **matplotlib/plotly**: Visualization
- **joblib**: Model serialization

## Important Notes

- This is for educational/research purposes
- Always test thoroughly before live trading
- Past performance doesn't guarantee future results
- Consider transaction costs and slippage
- Implement proper risk management
- Monitor model performance regularly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Use at your own risk for actual trading.
