# 🧪 Growfolio Testing Guide

This guide covers how to test both the frontend (Chrome extension) and backend (FastAPI) components of your Growfolio application.

## 📋 Prerequisites

### 1. Environment Setup
Create a `.env` file in the `backend/` directory:
```bash
cd backend
cat > .env << EOF
GEMINI_API_KEY=your_actual_gemini_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
EOF
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

## 🚀 Testing Methods

### Method 1: Backend API Testing (Command Line)

#### Start the Backend
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Test Endpoints
```bash
# Test 1: Get question sections
curl -X GET "http://localhost:8000/get_question_sections"

# Test 2: Create a user profile
curl -X POST "http://localhost:8000/create_profile" \
  -H "Content-Type: application/json" \
  -d '{
    "1": 5000,
    "2": {"Housing": 2000, "Groceries": 500, "Utilities": 200, "Transportation": 300, "Miscellaneous": 300},
    "3": 10000,
    "4": "None",
    "5": 0,
    "6": 30,
    "7": "Retirement",
    "8": "15+ years",
    "9": 65,
    "10": 20,
    "11": 3,
    "12": "Do nothing",
    "13": "Intermediate",
    "14": "Weekly",
    "15": "I am okay with short-term losses if I can earn more long-term.",
    "16": "Balanced Growth"
  }'

# Test 3: Get stock recommendation
curl -X POST "http://localhost:8000/recommend_stock" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_name": "AAPL",
    "user_profile": {"risk_tolerance": 3, "investment_goal": "Retirement"},
    "ml_output": {"confidence": 85, "action": "buy"}
  }'
```

### Method 2: Automated Python Testing

#### Run Step-by-Step Tests
```bash
python test_step_by_step.py
```

#### Run Comprehensive Backend Tests
```bash
python test_both_backends.py
```

#### Run Setup & Test Script
```bash
python setup_test.py
```

### Method 3: Frontend (Chrome Extension) Testing

#### 1. Load the Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked" and select the `frontend/` folder
4. The GrowFolio extension should appear in your extensions

#### 2. Test the Extension
1. Click the extension icon to open the popup
2. Complete the 3-step onboarding questionnaire:
   - **Step 1**: Financial Snapshot (income, expenses, savings, etc.)
   - **Step 2**: Investment Goals (trader type, horizon, risk tolerance)
   - **Step 3**: Personal Profile (experience, behavior)
3. Click "Continue to Dashboard" to see your analysis
4. Use the "Refresh" button to get new insights

#### 3. Expected Workflow
- **Day Trader**: Shows ML predictions with buy/sell/hold signals
- **Retirement Investor**: Shows portfolio allocation recommendations
- **Supplemental Income**: Shows income-focused strategies

### Method 4: Full Integration Testing

#### Start Both Backends (if you have a secure proxy)
```bash
chmod +x start_both_backends.sh
./start_both_backends.sh
```

This starts:
- Secure Proxy on port 8000
- Original Backend on port 8001

## 🔧 Troubleshooting

### Common Issues

#### 1. CORS Errors in Chrome Extension
- Make sure backend is running on `http://localhost:8000`
- Check that `manifest.json` has correct host permissions
- Verify CORS settings in `backend/app.py`

#### 2. API Key Errors
- Ensure `.env` file exists in `backend/` directory
- Verify GEMINI_API_KEY is set correctly
- Check that API key has proper permissions

#### 3. Connection Refused
- Verify backend is running: `ps aux | grep uvicorn`
- Check port availability: `lsof -i :8000`
- Try different port if 8000 is occupied

#### 4. Extension Not Loading
- Check `manifest.json` syntax
- Verify all required files exist in `frontend/` directory
- Check Chrome console for errors

### Debug Commands

```bash
# Check if backend is running
curl http://localhost:8000/

# Check backend logs
tail -f backend/logs/app.log

# Test specific endpoint
curl -X GET "http://localhost:8000/health"

# Check Chrome extension console
# Open DevTools in extension popup
```

## 📊 Expected Test Results

### Backend Tests Should Show:
- ✅ GET /get_question_sections - Returns question structure
- ✅ POST /create_profile - Creates user profile
- ✅ POST /recommend_stock - Generates stock recommendations
- ✅ POST /create_advanced_profile - Creates detailed profile
- ✅ POST /analyze_trader_type - Analyzes trader behavior

### Frontend Tests Should Show:
- ✅ Extension loads without errors
- ✅ Questionnaire displays correctly
- ✅ Data submission works
- ✅ Dashboard shows appropriate content
- ✅ No CORS errors in console

## 🎯 Quick Test Checklist

- [ ] Backend starts without errors
- [ ] API endpoints respond correctly
- [ ] Chrome extension loads
- [ ] Questionnaire works end-to-end
- [ ] Dashboard displays results
- [ ] No console errors
- [ ] CORS issues resolved

## 🚀 Next Steps

After successful testing:
1. Deploy backend to production server
2. Update extension manifest with production URL
3. Test with real API keys
4. Add unit tests for individual components
5. Set up CI/CD pipeline for automated testing
