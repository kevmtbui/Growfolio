# Growfolio

### Chrome Extension · AI-Powered Financial Advisor

Growfolio helps young investors make smarter, stress-free financial decisions using AI insights, machine learning predictions, and the Gemini API — all within a simple Chrome extension.

---

## Overview

**Problem**  
Financial literacy and investing confidence are low among young adults. Most robo-advisors are complex or paywalled.

**Solution**  
Growfolio bridges that gap by providing personalized stock recommendations, explanations, and trend insights powered by AI and ML. It enables users to grow wealth safely and confidently through an accessible Chrome extension.

---

## Goals and Objectives

- Simplify portfolio decision-making for new investors  
- Use the Gemini API to interpret user intent and explain recommendations  
- Integrate ML models to detect short-term stock trends and risk patterns  
- Encourage long-term, sustainable investing habits

---

## Target Users

- Primary: Students and young professionals new to investing  
- Secondary: Budget-conscious individuals seeking AI-assisted financial planning

---

## Core Features (MVP)

| Feature | Description |
|----------|--------------|----------|
| Smart Financial Intake | Collects income, rent, and spending data |
| Risk and Literacy Quiz | Determines user confidence and tolerance | 
| AI Stock Recommender | Suggests stocks matched to user risk and goals |
| Decision Support Summaries | Explains why each stock was chosen |
| Manual Ticker Analysis | Lets users query any stock for AI insights |
| Chrome Extension UI | Dashboard for financial tools |
| Auto-Trading (Stretch) | Wealthsimple API integration |

---

## AI and ML Integration

**Gemini API (LLM Layer)**  
- Understands user intent  
- Summarizes patterns and reasoning  
- Generates natural-language explanations  

**ML Model (Analytical Layer)**  
- Predicts short-term stock trends  
- Uses Random Forest or LSTM on open data (Yahoo Finance or Alpha Vantage)  
- Outputs confidence and volatility metrics  

**Example Output**  
“Given your moderate risk tolerance, AAPL shows stable growth with 78% confidence.  
Gemini explains: Apple’s cash flow resilience aligns with your goal to save safely over time.”

---

## Decision Support Logic

1. Collect user context (income, expenses, goals)  
2. Predict stock performance using the ML model  
3. Generate reasoning with the Gemini API  
4. Rank 3–5 stocks by confidence and risk match  
5. Allow the user to simulate or trade manually  

---

## Tech Stack

| Layer | Tools |
|--------|-------|
| Frontend | Chrome Extension (HTML/CSS/JS, optional React) |
| Backend | Python (FastAPI) or Node.js |
| ML Model | scikit-learn / TensorFlow Lite |
| AI Assistant | Google Gemini API |
| Data | Yahoo Finance / Alpha Vantage |
| Storage | LocalStorage / IndexedDB |
| Integration (Stretch) | Wealthsimple API |

---

## User Flow

1. Install Growfolio Chrome extension  
2. Complete financial intake and quiz  
3. Receive stock recommendations (ML + Gemini)  
4. View explanation summaries  
5. Simulate or trade manually  
6. (Stretch) Enable voice insights  

---

## Success Metrics

- Chrome extension collects financial data and predicts locally  
- Gemini generates reasoning for at least three stock recommendations  
- Explanations improve user confidence  
- Works offline with mock data  
- Stretch: Wealthsimple or voice integration  

--

## Architecture Overview

Growfolio follows a clean separation between frontend and backend:

**Frontend (Chrome Extension)**
- Collects user input through 3-step onboarding questionnaire
- Displays trader-specific dashboards (Day Trader vs Retirement Investor)
- Handles all UI interactions and user experience
- Communicates with backend via HTTPS requests

**Backend (FastAPI Server)**
- Processes user profiles and determines trader type
- Routes requests to appropriate analysis engines
- **Day Traders**: ML model generates short-term predictions (buy/sell/hold signals)
- **Retirement Investors**: Gemini AI creates long-term portfolio allocations
- Provides structured, clean responses to frontend

**Key Benefits**
- No database required - all interactions are stateless
- Secure - API keys and ML models stay on backend
- Scalable - backend can be hosted anywhere
- User-friendly - extension works offline after initial setup

## Run Locally

### Quick Setup (Recommended)
```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt

# 2. Set up environment
# Create backend/.env with your API keys:
echo "GEMINI_API_KEY=your_actual_gemini_api_key_here" > backend/.env
echo "FINNHUB_API_KEY=your_finnhub_api_key_here" >> backend/.env

# 3. Run the setup script
python setup_test.py
```

### Manual Setup
```bash
# Backend
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Frontend (Chrome Extension)
# 1. Open Chrome and go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked" and select the 'frontend' folder
# 4. Click the GrowFolio extension icon to start
```

### Testing the Complete Workflow

1. **Complete Onboarding**: Answer the 3-step questionnaire
2. **Choose Trader Type**: Select "Day Trader" or "Retirement Investor"
3. **View Analysis**: 
   - Day Traders see ML predictions with buy/sell/hold signals
   - Retirement Investors see portfolio allocation recommendations
4. **Refresh Insights**: Use the refresh button to get new analysis
5. **Export Data**: Download your profile and analysis data

## Advanced Portfolio System

Growfolio now includes a sophisticated robo-advisor system with real-time data integration:

**Risk-Based Portfolio Allocation**
- 6 risk bands from "Very Conservative" to "Aggressive"
- Deterministic asset allocation based on risk score (1-10)
- Support for US and Canadian jurisdictions
- Automatic rebalancing recommendations

**Real-Time Data Integration**
- Live stock quotes via Finnhub API
- Recent news and market sentiment
- ETF selection with expense ratio analysis
- Function calling with Gemini AI for intelligent ETF picking

**Advanced Features**
- Gemini AI selects optimal ETFs for each asset class
- Live portfolio tracking with current prices
- Comprehensive explanations for each recommendation
- Fallback to basic analysis if APIs are unavailable

### API Endpoints

- `GET /get_question_sections` - Returns onboarding questionnaire
- `POST /create_profile` - Creates basic user profile via Gemini AI
- `POST /create_advanced_profile` - Creates advanced profile with real-time portfolio
- `POST /analyze_trader_type` - Routes to appropriate analysis engine
- `POST /recommend_stock` - Explains individual stock recommendations

### Required API Keys

**Required:**
- `GEMINI_API_KEY` - Google Gemini AI API key

**Optional (for full functionality):**
- `FINNHUB_API_KEY` - Finnhub API key for real-time market data
  - Without this key, the system uses mock data for development
  - Get your free key at: https://finnhub.io/
