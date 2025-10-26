# GrowFolio

AI-powered investment advisor Chrome extension that helps you make smarter financial decisions using machine learning and Google's Gemini AI.

## What is GrowFolio?

GrowFolio is a Chrome extension that provides personalized investment recommendations based on your financial profile, risk tolerance, and investment goals. It combines:

- **Machine Learning Models**: LSTM neural networks trained on historical data to predict short-term trading signals
- **Google Gemini AI**: Natural language explanations and long-term portfolio recommendations
- **Live Market Data**: Real-time prices and analysis from Finnhub API

## Features

### Personalized Recommendations
- **Day Trading**: ML-powered buy/sell/hold signals with confidence scores for stocks and cryptocurrencies
- **Retirement Planning**: AI-generated portfolio allocations with ETF recommendations
- **Risk Assessment**: Automatic risk profiling based on your financial situation

### AI-Powered Insights
- 3-sentence explanations for each recommendation
- Market sentiment analysis
- Portfolio strategy breakdowns

### Real-Time Data
- Live stock prices
- Current market trends
- Volatility analysis

## Installation

**📋 [View detailed installation instructions →](INSTALLATION.md)**

Quick overview:
1. Download the `frontend` folder from this repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable Developer mode and click "Load unpacked"
4. Select the `frontend` folder
5. Start using GrowFolio!


## How It Works

### 1. User Input
You complete a comprehensive financial questionnaire covering:
- Income and expenses
- Investment goals and timeline
- Risk tolerance
- Investment experience

### 2. AI Analysis
The backend processes your profile:
- **Risk Score**: Calculated based on your financial situation (1-10 scale)
- **Trader Type**: Determined by your goals (Day Trader vs Retirement Investor)

### 3. Recommendations

**For Day Traders**:
- ML models analyze historical price data
- Generate buy/sell/hold signals with confidence scores
- Include entry and exit price targets

**For Retirement Investors**:
- Gemini AI creates long-term portfolio allocations
- Recommends specific ETFs across asset classes
- Provides detailed explanations for each choice

### 4. Display
Results are shown in an easy-to-understand dashboard with:
- Visual stat cards
- Recommendation cards with detailed rationale
- Export functionality

## Backend Configuration

The backend is hosted on Railway and already configured with all necessary API keys. Users don't need to configure anything - just install the extension and start using it!

### ML Models

The machine learning models used for day trading predictions are publicly available on Hugging Face:
- **Repository**: [https://huggingface.co/kevmtbui/growfolio-models/tree/main](https://huggingface.co/kevmtbui/growfolio-models/tree/main)
- **Models**: LSTM neural networks trained on 5-minute and 15-minute intervals
- **Assets**: Covers stocks (AAPL, MSFT, NVDA, TSLA, etc.) and cryptocurrencies (BTC, ETH, ADA, SOL, etc.)
- **Total Size**: ~3.11 MB of trained model files


## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python, FastAPI
- **AI**: Google Gemini API
- **ML**: PyTorch, LSTM Neural Networks
- **Data**: Finnhub API, Yahoo Finance
- **Storage**: Chrome Local Storage

## Important Notes

- GrowFolio is for educational purposes
- Always do your own research before making investment decisions
- Past performance doesn't guarantee future results
- Consult with a financial advisor for professional advice
- Trading involves risk of financial loss


## Acknowledgments

- Google Gemini AI for natural language explanations
- Finnhub for real-time market data
