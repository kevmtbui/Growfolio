# Growfolio ML Models

Machine learning models that power short-term trading recommendations in the Growfolio Chrome extension. This directory contains the training scripts and model files for predicting Buy/Hold/Sell signals using LSTM neural networks.

## Overview

The ML models in this directory are trained to predict short-term price movements for popular stocks and cryptocurrencies. When users select "Short-term trading" as their investment goal, these models provide AI-powered trading signals with confidence scores.

## Architecture

### Model Type
- **Architecture**: LSTM (Long Short-Term Memory) neural networks
- **Framework**: PyTorch
- **Input Features**: Technical indicators (RSI, MACD, EMA, ATR, VWAP, etc.)
- **Output**: Buy/Hold/Sell action with confidence score (0-100%)

### Supported Assets
The models are trained on the following assets:
- **Stocks**: AAPL, MSFT, NVDA, TSLA, GOOGL, AMZN, META, AMD, INTC, LOW, TMO, MA, PEP, NFLX
- **Cryptocurrencies**: BTC, ETH, BNB, ADA, SOL, XRP, DOGE, AVAX, DOT, SHIB

### Timeframes
- 5-minute and 15-minute intervals

## Project Structure

```
ml_model/
├── models/              # Trained .pth model files
│   ├── AAPL_5m_lstm.pth
│   ├── AAPL_15m_lstm.pth
│   ├── BTC_USDT_5m_lstm.pth
│   └── ...
├── src/
│   ├── train_top20.py       # Main training script
│   ├── models.py            # LSTM model definition
│   ├── indicators.py        # Technical indicators
│   ├── preprocess_data.py   # Data preprocessing
│   └── predict_live.py      # Live prediction functions
├── data/
│   ├── raw/                 # Raw OHLCV data
│   └── processed/           # Processed features
├── results/                 # Training results and logs
├── config.py                # Model configuration
└── requirements.txt         # Dependencies
```

## Training Models

### Quick Start

Train models for all supported assets:

```bash
cd ml_model
python train_top20.py
```

This will:
1. Download historical price data for all assets
2. Preprocess and engineer features
3. Train LSTM models for each asset/timeframe combination
4. Save trained models to `models/` directory
5. Generate training reports in `results/`

### Training Configuration

Edit `src/train_top20.py` to customize:
- `SYMBOLS`: List of assets to train
- `TIMEFRAMES`: List of intervals (e.g., ['5m', '15m'])
- `EPOCHS`: Number of training epochs
- `BATCH_SIZE`: Training batch size

### Training Process

For each asset/timeframe combination:
1. **Data Collection**: Download historical OHLCV data
2. **Feature Engineering**: Calculate 16+ technical indicators
3. **Data Splitting**: 70% train, 15% validation, 15% test
4. **Model Training**: Train LSTM with early stopping
5. **Evaluation**: Calculate accuracy and F1 score
6. **Model Saving**: Save `.pth` file to `models/` directory

## Deployment to Hugging Face

### Why Hugging Face?
The trained models are too large (~5-10MB each) for GitHub. They are hosted on Hugging Face Hub and automatically downloaded by the backend on startup.

### Uploading Models

1. **Create Hugging Face Repository**:
   - Go to https://huggingface.co/new
   - Create a repository (e.g., `your-username/growfolio-models`)
   - Set repository type to "Model"

2. **Upload Models**:
   ```bash
   # Install huggingface_hub
   pip install huggingface_hub
   
   # Login to Hugging Face
   huggingface-cli login
   
   # Upload models
   cd ml_model/models
   huggingface-cli upload your-username/growfolio-models . --repo-type model
   ```

3. **Update Backend Configuration**:
   Edit `backend/ml_loader.py`:
   ```python
   REPO_NAME = "your-username/growfolio-models"
   ```

### Model Download

The backend automatically downloads models on startup via `backend/ml_loader.py`:
- Downloads occur only once per deployment
- Models are cached locally for faster subsequent startups
- Missing models fall back to placeholder predictions

## Integration with Growfolio

### Backend Integration

The ML models are used in `backend/app.py`:

```python
# Route: /analyze_trader_type
# When trader_type == "day_trader":
def handle_day_trader_analysis(user_profile):
    # Load ML predictor
    from ml_loader import get_ml_predictor
    predictor = get_ml_predictor()
    
    # Generate predictions
    predictions = predictor.predict_for_assets(assets)
    
    # Enhance with live prices
    predictions = enhance_with_live_data(predictions)
    
    # Return to frontend
    return predictions
```

### Frontend Display

The frontend (`frontend/dashboard.js`) displays predictions as:
- **Stock Ticker**: e.g., AAPL, BTC
- **Action**: BUY, SELL, or HOLD
- **Confidence**: Percentage (0-100%)
- **Current Price**: Live market price
- **Buy Target**: Recommended entry price
- **Sell Target**: Recommended exit price
- **AI Feedback**: 3-sentence explanation from Gemini

## Model Performance

### Expected Metrics
- **Accuracy**: 60-70% on test set
- **F1 Score**: 0.55-0.65
- **Confidence Calibration**: Well-calibrated for confidence scores

### Limitations
- Models are trained on historical data
- Past performance ≠ future results
- Short-term predictions are inherently uncertain
- Always use with proper risk management

## Technical Details

### Input Features (16 total)
1. **Price Data**: open, high, low, close, volume
2. **Momentum**: RSI(14), MACD(12,26,9)
3. **Trend**: EMA(9,21,50)
4. **Volatility**: ATR(14), Bollinger Bands
5. **Volume**: VWAP, Volume MA
6. **Derived**: Price change %, High-Low spread

### Model Architecture
```
Input (60 timesteps × 16 features)
    ↓
LSTM Layer 1 (64 units)
    ↓
Dropout (0.2)
    ↓
LSTM Layer 2 (64 units)
    ↓
Dropout (0.2)
    ↓
Dense Layer (32 units)
    ↓
Output Layer (3 classes: Buy/Hold/Sell)
```

### Prediction Pipeline
1. Load last 60 candlesticks of OHLCV data
2. Calculate technical indicators
3. Normalize features using trained scaler
4. Pass through LSTM model
5. Apply softmax to get probabilities
6. Select action with highest probability
7. Calculate confidence as max probability
8. Enhance with live price from Finnhub API

## Dependencies

```
torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
ta>=0.11.0
huggingface_hub>=0.17.0
```

## Troubleshooting

### Model Not Loading
- Check Hugging Face credentials in `.env`
- Verify repository name in `ml_loader.py`
- Ensure models exist in Hugging Face repository

### Poor Predictions
- Models may need retraining with new data
- Check if market conditions have changed
- Review technical indicator calculations

### Slow Predictions
- Models are loaded once on startup
- Subsequent predictions are fast (<100ms)
- If slow, check Finnhub API rate limits

## Future Improvements

- [ ] Add GRU and Transformer model variants
- [ ] Implement online learning for model updates
- [ ] Add more technical indicators (custom indicators)
- [ ] Ensemble multiple models for better accuracy
- [ ] Add portfolio-level predictions
- [ ] Real-time streaming predictions via WebSocket


