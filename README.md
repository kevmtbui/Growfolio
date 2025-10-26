# Growfolio

AI-powered investment advisor Chrome extension that helps you make smarter financial decisions using machine learning and Google's Gemini AI.

## What is Growfolio?

Growfolio is a Chrome extension that provides personalized investment recommendations based on your financial profile, risk tolerance, and investment goals. It combines:

- **Machine Learning Models**: LSTM neural networks trained on historical data to predict short-term trading signals
- **Google Gemini AI**: Natural language explanations and long-term portfolio recommendations
- **Live Market Data**: Real-time prices and analysis from Finnhub API

## Features

### 🎯 Personalized Recommendations
- **Day Trading**: ML-powered buy/sell/hold signals with confidence scores for stocks and cryptocurrencies
- **Retirement Planning**: AI-generated portfolio allocations with ETF recommendations
- **Risk Assessment**: Automatic risk profiling based on your financial situation

### 🤖 AI-Powered Insights
- 3-sentence explanations for each recommendation
- Market sentiment analysis
- Portfolio strategy breakdowns

### 📊 Real-Time Data
- Live stock prices
- Current market trends
- Volatility analysis

## Installation

### Prerequisites
- Google Chrome browser
- A computer running Windows, macOS, or Linux

### Step 1: Download the Extension

1. **Download or Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/Growfolio.git
   cd Growfolio
   ```

2. **Or download as ZIP**:
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract the ZIP file to a folder on your computer

### Step 2: Set Up the Backend (Required)

The extension needs a backend server running to work properly.

#### Quick Setup:
```bash
# Navigate to the project folder
cd Growfolio

# Install Python dependencies
pip install -r backend/requirements.txt

# Create environment file
# On Windows (Command Prompt):
copy backend\.env.example backend\.env

# On Mac/Linux:
cp backend/.env.example backend/.env
```

#### Add Your API Keys:
1. Open `backend/.env` in a text editor
2. Get a free Gemini API key from: https://makersuite.google.com/app/apikey
3. Get a free Finnhub API key from: https://finnhub.io/
4. Add your keys to `.env`:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   FINNHUB_API_KEY=your_finnhub_api_key_here
   ```

#### Start the Backend Server:
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Keep this terminal open - the extension won't work without the backend running.

### Step 3: Install the Chrome Extension

1. **Open Chrome Extensions Page**:
   - Open Google Chrome
   - Type `chrome://extensions/` in the address bar and press Enter
   - Or go to: Menu (☰) → Extensions → Manage Extensions

2. **Enable Developer Mode**:
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the Extension**:
   - Click "Load unpacked"
   - Navigate to the `frontend` folder inside the Growfolio folder
   - Select the `frontend` folder
   - Click "Select Folder" (or "Open" on Mac)

4. **Verify Installation**:
   - You should see "Growfolio" appear in your extensions list
   - Look for the Growfolio icon in Chrome's toolbar

### Step 4: Start Using Growfolio

1. **Open the Extension**:
   - Click the Growfolio icon in your Chrome toolbar
   - Or use the puzzle piece icon to access pinned extensions

2. **Complete the Questionnaire**:
   - Fill out the 3-step financial profile
   - Answer questions about income, expenses, goals, and risk tolerance

3. **View Your Recommendations**:
   - Get instant AI-powered investment recommendations
   - See detailed explanations for each recommendation

4. **Export Your Analysis**:
   - Download your complete analysis as a TXT file
   - Share with a financial advisor if needed

## Troubleshooting

### Extension Not Loading?
- Make sure you selected the `frontend` folder (not the parent folder)
- Check that Developer mode is enabled
- Try reloading the extension (click the refresh icon on the extension card)

### Backend Connection Failed?
- Verify the backend server is running on port 8000
- Check that `http://localhost:8000` is accessible in your browser
- Make sure no firewall is blocking the connection

### No Recommendations Showing?
- Check that your API keys are correctly set in `backend/.env`
- Verify the backend server is running without errors
- Check the browser console (F12) for any error messages

## Project Structure

```
Growfolio/
├── frontend/           # Chrome extension (HTML/CSS/JS)
│   ├── popup.html     # Main extension UI
│   ├── dashboard.html # Results dashboard
│   ├── manifest.json  # Extension configuration
│   └── ...
├── backend/           # Python FastAPI server
│   ├── app.py        # Main API endpoints
│   ├── gemini_service.py  # AI integration
│   ├── ml_loader.py  # ML model loading
│   └── ...
├── ml_model/         # Machine learning models
│   ├── models/       # Trained model files
│   ├── src/          # Training scripts
│   └── README.md     # ML model documentation
└── README.md         # This file
```

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

## API Keys Required

### Free Tier Available

Both API keys have free tiers sufficient for personal use:

1. **Gemini API** (Required)
   - Website: https://makersuite.google.com/app/apikey
   - Free tier: 15 requests per minute
   - Required for AI explanations

2. **Finnhub API** (Optional)
   - Website: https://finnhub.io/
   - Free tier: 60 API calls/minute
   - Required for live stock prices
   - Without this key, the extension uses placeholder data

## Development

### Running the Backend Locally
```bash
cd backend
python -m uvicorn app:app --reload
```

### Testing the Extension
1. Start the backend server
2. Load the extension in Chrome
3. Complete the questionnaire
4. Check browser console (F12) for any errors

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python, FastAPI
- **AI**: Google Gemini API
- **ML**: PyTorch, LSTM Neural Networks
- **Data**: Finnhub API, Yahoo Finance
- **Storage**: Chrome Local Storage

## Important Notes

- Growfolio is for educational purposes
- Always do your own research before making investment decisions
- Past performance doesn't guarantee future results
- Consult with a financial advisor for professional advice
- Trading involves risk of financial loss

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the browser console for errors (F12)
3. Check the backend server logs
4. Open an issue on GitHub with details about the problem

## Acknowledgments

- Google Gemini AI for natural language explanations
- Finnhub for real-time market data
- The open-source community for excellent ML tools
